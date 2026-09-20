"""Recording the stage, and putting it back: GO.

Three jobs.

**Capture** reads the live state of every rig member and turns it into a
look. This is what the record button does, and it is the feature the whole
console is really about: an operator lights the stage by eye using ordinary
Home Assistant controls, presses one button, and owns that look forever.

**Apply** puts a look back with a fade. Every member is driven, including the
ones that were off — a cue that only restored the lit fixtures would leave
the previous cue bleeding onto stage.

**The playhead** is which cue is on stage, and GO / Back / Goto move it.

## The playhead is deliberately not persisted

GO is the most timing-critical thing this product does, and it happens on
someone's cue in a live show. Writing to disk on every press to survive a
restart that almost never happens would trade the thing that matters for the
thing that does not. If Home Assistant restarts mid-show the operator presses
Goto, which is one tap. The cue *data* is of course persisted; only the
pointer into it is in memory.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_MODE,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    ATTR_XY_COLOR,
    LightEntityFeature,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_SUPPORTED_FEATURES, STATE_ON
from homeassistant.core import HomeAssistant, split_entity_id

from .cues import Cue, CueKind, LightLevel
from .effects import EffectEngine
from .rig import is_group_light

_LOGGER = logging.getLogger(__name__)

# Domains the console can drive. A rig is mostly lights, but a practical on a
# switched socket is a real fixture and belongs in the cue like any other.
DIMMABLE_DOMAIN = "light"
SWITCHABLE_DOMAINS = {"light", "switch", "input_boolean", "fan"}


def capture(hass: HomeAssistant, entity_ids: list[str]) -> list[LightLevel]:
    """Read the live state of the rig into a look.

    A member Home Assistant cannot currently see is recorded as off rather
    than skipped. Skipping it would mean the cue silently stopped controlling
    that fixture — so a bulb switched off at the wall during a get-in would
    quietly drop out of every cue recorded afterwards.
    """
    levels: list[LightLevel] = []
    for entity_id in entity_ids:
        state = hass.states.get(entity_id)
        if state is None or state.state in ("unavailable", "unknown"):
            levels.append(LightLevel(entity_id=entity_id, state="off"))
            continue
        if state.state != STATE_ON:
            levels.append(LightLevel(entity_id=entity_id, state="off"))
            continue

        attrs = state.attributes
        color_mode = attrs.get(ATTR_COLOR_MODE)
        brightness = attrs.get(ATTR_BRIGHTNESS)
        xy = attrs.get(ATTR_XY_COLOR)
        hs = attrs.get(ATTR_HS_COLOR)
        kelvin = attrs.get(ATTR_COLOR_TEMP_KELVIN)

        # Keep only the colour that matches the mode the light reported.
        # Home Assistant derives the others, and storing a derived value
        # invites a round trip that visibly shifts the colour.
        keep_xy = color_mode == "xy" and xy is not None
        keep_hs = color_mode == "hs" and hs is not None
        keep_ct = color_mode == "color_temp" and kelvin is not None
        if not (keep_xy or keep_hs or keep_ct):
            # An unfamiliar or absent mode — fall back to whatever colour is
            # actually present, preferring xy, which is what Hue works in.
            keep_xy = xy is not None
            keep_hs = not keep_xy and hs is not None
            keep_ct = not keep_xy and not keep_hs and kelvin is not None

        levels.append(
            LightLevel(
                entity_id=entity_id,
                state="on",
                brightness=int(brightness) if brightness is not None else None,
                color_mode=color_mode if isinstance(color_mode, str) else None,
                xy_color=(float(xy[0]), float(xy[1])) if keep_xy else None,
                hs_color=(float(hs[0]), float(hs[1])) if keep_hs else None,
                color_temp_kelvin=int(kelvin) if keep_ct else None,
            )
        )
    return levels


def _supports_transition(hass: HomeAssistant, entity_id: str) -> bool:
    """Whether it is safe to pass `transition` to this entity.

    Passing it to a light that does not support it is an error in Home
    Assistant, and an error mid-cue is a cue that does not happen.
    """
    if split_entity_id(entity_id)[0] != DIMMABLE_DOMAIN:
        return False
    state = hass.states.get(entity_id)
    if state is None:
        return False
    features = state.attributes.get(ATTR_SUPPORTED_FEATURES) or 0
    return bool(int(features) & LightEntityFeature.TRANSITION)


def build_calls(
    hass: HomeAssistant, levels: list[LightLevel], fade: float
) -> list[tuple[str, str, dict[str, Any]]]:
    """Turn a look into the service calls that realise it.

    Returned rather than executed so the whole plan is inspectable — the
    tests assert on it directly, which is how a cue can be verified without
    any lights present.

    Everything being turned off with the same fade is collapsed into one
    call. Blackout is the single commonest cue in Stevie's show — 16 of the
    67 in *Company* — and one service call for the whole rig makes it land
    together rather than as a ragged sweep.
    """
    calls: list[tuple[str, str, dict[str, Any]]] = []
    off_with_transition: list[str] = []
    off_plain: list[str] = []

    for level in levels:
        domain = split_entity_id(level.entity_id)[0]
        if domain not in SWITCHABLE_DOMAINS or is_group_light(hass, level.entity_id):
            continue
        can_fade = _supports_transition(hass, level.entity_id)

        if level.state != "on":
            (off_with_transition if can_fade else off_plain).append(level.entity_id)
            continue

        if domain != DIMMABLE_DOMAIN:
            calls.append((domain, "turn_on", {ATTR_ENTITY_ID: [level.entity_id]}))
            continue

        data: dict[str, Any] = {ATTR_ENTITY_ID: [level.entity_id]}
        if level.brightness is not None:
            data[ATTR_BRIGHTNESS] = level.brightness
        if level.xy_color is not None:
            data[ATTR_XY_COLOR] = list(level.xy_color)
        elif level.hs_color is not None:
            data[ATTR_HS_COLOR] = list(level.hs_color)
        elif level.color_temp_kelvin is not None:
            data[ATTR_COLOR_TEMP_KELVIN] = level.color_temp_kelvin
        if can_fade:
            data["transition"] = fade
        calls.append((DIMMABLE_DOMAIN, "turn_on", data))

    if off_with_transition:
        calls.append(
            (
                DIMMABLE_DOMAIN,
                "turn_off",
                {ATTR_ENTITY_ID: off_with_transition, "transition": fade},
            )
        )
    for entity_id in off_plain:
        calls.append(
            (split_entity_id(entity_id)[0], "turn_off", {ATTR_ENTITY_ID: [entity_id]})
        )
    return calls


def resolve_targets(
    effect_params: dict[str, Any], rig_entity_ids: list[str]
) -> list[str]:
    """Which lights an effect should drive, and in what order.

    An empty or absent `targets` means the whole rig — the sensible default,
    and what a cue saved before anyone touched the picker will have.

    **Order is meaningful and is preserved exactly as given.** A chase walks
    its targets in sequence, so the order the operator picked them in *is* the
    path the chase takes across the stage. Sorting them here, or silently
    reordering them into rig order, would quietly change the look.

    Targets that are no longer in the rig are dropped: a cue saved against a
    fixture that has since been struck should still run on what remains,
    rather than failing or driving a light the console no longer owns. If that
    leaves nothing at all, the whole rig is used, because an effect cue that
    does nothing is worse than one that is too broad.
    """
    raw = effect_params.get("targets")
    if not isinstance(raw, list) or not raw:
        return list(rig_entity_ids)

    in_rig = set(rig_entity_ids)
    chosen = [
        entity_id
        for entity_id in raw
        if isinstance(entity_id, str) and entity_id in in_rig
    ]
    if not chosen:
        _LOGGER.warning(
            "Effect targets %r are no longer in the rig; falling back to the whole rig",
            raw,
        )
        return list(rig_entity_ids)
    return chosen


class Playback:
    """The playhead, and everything that moves it."""

    def __init__(self, hass: HomeAssistant, effects: EffectEngine) -> None:
        self._hass = hass
        self._effects = effects
        self._current_cue_id: str | None = None

    @property
    def current_cue_id(self) -> str | None:
        return self._current_cue_id

    def status(self, show: Any | None) -> dict[str, Any]:
        """What the card renders in its transport bar."""
        index = (
            show.index_of(self._current_cue_id)
            if show and self._current_cue_id
            else None
        )
        return {
            "current_cue_id": self._current_cue_id,
            "current_index": index,
            "cue_count": len(show.cues) if show else 0,
            "effect": self._effects.status(),
        }

    def reset(self) -> None:
        """Forget the playhead — on a show change, where it means nothing."""
        self._current_cue_id = None

    # ------------------------------------------------------------------
    # Firing cues
    # ------------------------------------------------------------------

    async def async_apply(
        self, cue: Cue, rig_entity_ids: list[str], fade: float | None = None
    ) -> None:
        """Put one cue on stage.

        Any running effect is stopped first, unconditionally. In Stevie's
        current rig a chase is an `input_boolean` that keeps running until
        someone remembers to switch it off — so the blackout after his LX19b
        chase does not actually stop the chase. Making every cue stop the
        previous effect is the fix, and it is what a real console does.
        """
        await self._effects.async_stop()

        if cue.kind is CueKind.EFFECT:
            await self._effects.async_start(
                cue.effect or "",
                cue.effect_params,
                resolve_targets(cue.effect_params, rig_entity_ids),
            )
            self._current_cue_id = cue.id
            return

        calls = build_calls(self._hass, cue.levels, cue.fade if fade is None else fade)
        # Fired together rather than in sequence: six sequential awaits put a
        # visible ripple across the rig on a snap cue.
        await asyncio.gather(
            *(
                self._hass.services.async_call(domain, service, data, blocking=False)
                for domain, service, data in calls
            )
        )
        self._current_cue_id = cue.id

    async def async_go(self, show: Any, rig_entity_ids: list[str]) -> Cue | None:
        """Fire the next cue. From nowhere, fires the first."""
        if not show or not show.cues:
            return None
        index = show.index_of(self._current_cue_id) if self._current_cue_id else None
        nxt = 0 if index is None else index + 1
        if nxt >= len(show.cues):
            return None
        cue = show.cues[nxt]
        await self.async_apply(cue, rig_entity_ids)
        return cue

    async def async_back(self, show: Any, rig_entity_ids: list[str]) -> Cue | None:
        """Fire the previous cue.

        Uses the cue's own fade rather than snapping back. Going back is
        almost always a correction during tech, and a snap draws the room's
        attention to the mistake.
        """
        if not show or not show.cues:
            return None
        index = show.index_of(self._current_cue_id) if self._current_cue_id else None
        if index is None or index <= 0:
            return None
        cue = show.cues[index - 1]
        await self.async_apply(cue, rig_entity_ids)
        return cue

    async def async_goto(
        self, show: Any, cue_id: str, rig_entity_ids: list[str]
    ) -> Cue | None:
        if not show:
            return None
        cue = show.cue(cue_id)
        if cue is None:
            return None
        await self.async_apply(cue, rig_entity_ids)
        return cue

    async def async_release(self, rig_entity_ids: list[str]) -> None:
        """Stop everything and hand the rig back to normal control.

        This must work when nothing else does. It stops any effect first —
        that is the part that can otherwise keep driving lights forever — and
        only then turns the rig off. The playhead is cleared so the next GO
        starts from the top rather than from a cue nobody can see.
        """
        await self._effects.async_stop()
        self._current_cue_id = None
        if not rig_entity_ids:
            return
        by_domain: dict[str, list[str]] = {}
        for entity_id in rig_entity_ids:
            domain = split_entity_id(entity_id)[0]
            if domain in SWITCHABLE_DOMAINS:
                by_domain.setdefault(domain, []).append(entity_id)
        for domain, entity_ids in by_domain.items():
            try:
                await self._hass.services.async_call(
                    domain, "turn_off", {ATTR_ENTITY_ID: entity_ids}, blocking=False
                )
            except Exception:  # release must never raise
                _LOGGER.exception("Release failed for %s", domain)


__all__ = [
    "Playback",
    "build_calls",
    "capture",
    "resolve_targets",
]
