"""Turning a room's worth of Hue scenes into a cue list.

Stevie's existing shows are not in Home Assistant. Of the 144 scene entities
on his instance, 141 live on the bridge — one Hue scene per lighting cue,
grouped into a Hue room or zone per production (*Company*, *HADESTOWN*,
*LRP STAGE*). That is years of work, and it is the obvious source of a
starting cue list for the next show as well as the only way the old ones
become editable here.

Import **materialises** each scene rather than referencing it. The cue ends
up holding the actual light states, so it can be edited, re-recorded and
fired with no bridge round trip, and it survives someone tidying up the Hue
app later. The alternative — storing a scene id and recalling it — would make
every cue an alias for something we do not control.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util.uuid import random_uuid_hex

from .cues import Cue, CueKind, LightLevel
from .hue import HueGroup, HueLight, HueScene
from .rig import hue_light_id_for_entity

_LOGGER = logging.getLogger(__name__)

_NATURAL = re.compile(r"(\d+)")


def _natural_key(name: str) -> list[Any]:
    """Sort "LX2" before "LX10".

    Cue lists are full of numbers, and plain lexicographic order puts LX10
    immediately after LX1 — which turns an imported show into nonsense that
    the operator then has to drag back into shape by hand.
    """
    return [
        int(part) if part.isdigit() else part.lower()
        for part in _NATURAL.split(name.strip())
        if part != ""
    ]


@dataclass
class ImportResult:
    """What an import did, in terms the card can show the operator."""

    cues: list[Cue]
    unmapped_light_ids: list[str]
    """Lights in the scenes that no Home Assistant entity corresponds to."""

    uncovered_per_cue: int
    """How many (cue, light) pairs were filled in as off because the scene
    said nothing about that light. Usually zero — Hue writes an action for
    every group member — but worth surfacing when it is not."""

    empty_cues: int = 0
    """Cues that came out controlling nothing at all.

    Not hypothetical. A Hue light belongs to exactly one room, so moving the
    rig into a new room empties the old room's scenes: the scene resources
    survive on the bridge with zero actions. Stevie's HADESTOWN room is
    exactly this — 16 scenes, every one a husk. Importing it silently
    produced 16 cues that do nothing, which is worse than refusing.
    """

    def to_dict(self) -> dict[str, Any]:
        return {
            "cue_count": len(self.cues),
            "unmapped_light_ids": list(self.unmapped_light_ids),
            "uncovered_per_cue": self.uncovered_per_cue,
            "empty_cues": self.empty_cues,
        }


def build_light_map(
    hass: HomeAssistant, hue_lights_by_id: dict[str, HueLight]
) -> dict[str, str]:
    """Hue `light` resource id -> Home Assistant entity id.

    Built by walking every light entity Home Assistant has and asking the same
    resolver the rig uses, so import and classification can never disagree
    about which entity is which bulb.
    """
    mapping: dict[str, str] = {}
    for state in hass.states.async_all("light"):
        light_id = hue_light_id_for_entity(hass, state.entity_id, hue_lights_by_id)
        if light_id is not None:
            mapping.setdefault(light_id, state.entity_id)
    return mapping


def _level_from_action(entity_id: str, action: Any) -> LightLevel:
    """One scene action -> one recorded level."""
    if not action.on:
        return LightLevel(entity_id=entity_id, state="off")

    brightness = None
    if action.brightness_pct is not None:
        # Hue works in 0-100, Home Assistant in 0-255. A light the scene turns
        # on is never recorded at zero brightness — that reads as off and
        # would silently drop the fixture out of the look.
        brightness = max(1, min(255, round(action.brightness_pct / 100 * 255)))

    if action.xy is not None:
        return LightLevel(
            entity_id=entity_id,
            state="on",
            brightness=brightness,
            color_mode="xy",
            xy_color=action.xy,
        )
    if action.mirek:
        return LightLevel(
            entity_id=entity_id,
            state="on",
            brightness=brightness,
            color_mode="color_temp",
            color_temp_kelvin=round(1_000_000 / action.mirek),
        )
    return LightLevel(entity_id=entity_id, state="on", brightness=brightness)


def cues_from_scenes(
    group: HueGroup,
    scenes: list[HueScene],
    light_map: dict[str, str],
    default_fade: float = 0.0,
) -> ImportResult:
    """Build a cue list from every scene belonging to one room or zone.

    Cues come out in natural order of scene name, which for every one of
    Stevie's shows is already the running order.

    Each cue defines the *whole group*, not only the lights the scene
    mentions. A cue that left some fixtures undefined would let the previous
    cue bleed through it, which is the one thing a cue must never do.
    """
    in_group = [light_id for light_id in group.light_ids if light_id in light_map]
    unmapped = sorted({light_id for light_id in group.light_ids} - set(light_map))

    # Scenes with no actions at all are dropped rather than turned into cues
    # that control nothing. `empty_cues` on the result still reports anything
    # that slipped through with an empty level list.
    mine = [scene for scene in scenes if scene.group_id == group.id and scene.actions]
    mine.sort(key=lambda scene: _natural_key(scene.name))

    cues: list[Cue] = []
    uncovered = 0
    for scene in mine:
        by_light = {action.light_id: action for action in scene.actions}
        levels: list[LightLevel] = []
        for light_id in in_group:
            entity_id = light_map[light_id]
            action = by_light.get(light_id)
            if action is None:
                uncovered += 1
                levels.append(LightLevel(entity_id=entity_id, state="off"))
            else:
                levels.append(_level_from_action(entity_id, action))

        # Lights the scene touches that are not in the group at all. Rare, but
        # Hue permits it, and dropping them would quietly change the look.
        for light_id, action in by_light.items():
            if light_id in in_group or light_id not in light_map:
                continue
            levels.append(_level_from_action(light_map[light_id], action))

        cues.append(
            Cue(
                id=random_uuid_hex(),
                label=scene.name.strip() or scene.id[:6],
                kind=CueKind.LOOK,
                name="",
                fade=default_fade,
                levels=levels,
                notes=f"Imported from Hue scene {scene.name!r}.",
            )
        )

    empty = sum(1 for cue in cues if not cue.levels)
    if empty:
        _LOGGER.warning(
            "%d of %d scenes in %s %r control no lights at all; on the bridge "
            "they hold no actions. This is what Hue does to a room's scenes "
            "when the lights are moved to a different room.",
            empty,
            len(cues),
            group.type,
            group.name,
        )
    _LOGGER.debug(
        "Imported %d cues from %s %r (%d unmapped lights, %d empty)",
        len(cues),
        group.type,
        group.name,
        len(unmapped),
        empty,
    )
    return ImportResult(
        cues=cues,
        unmapped_light_ids=unmapped,
        uncovered_per_cue=uncovered,
        empty_cues=empty,
    )
