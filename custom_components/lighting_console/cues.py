"""Shows and cues: the data the console exists to hold.

A **show** is one production — *Carrie*, *Company*, *Hadestown*. It owns an
ordered list of cues and nothing else. Shows are the top-level container
because that is how the work actually arrives: a rig goes up in a living
room, one production runs on it for a few weeks, and then the next production
starts from nothing. Making the operator create a new *dashboard* per show
was the old way; here they type a name and get an empty cue list.

A **cue** is one press of GO. Two kinds exist:

- A **look** is a static state of the whole rig, captured from whatever the
  lights are doing right now. This is `record`: fiddle the lights until the
  stage is right, press the button, and the look is yours. Recording captures
  *every* rig member, including the ones that are off — "these six are off"
  is as much a part of a look as "this one is deep blue", and a cue that only
  captured the lit fixtures would leak the previous cue's state onto stage.

- An **effect** is something that moves: a chase, a flash. The cue stores
  *what the effect is* — kind, targets, timing, colours — never a recording
  of it. That indirection is the point: milestone 2 runs effects over normal
  Home Assistant services at roughly the rate a script can manage, and
  milestone 3 swaps in the 25 fps Entertainment stream underneath without
  touching a single stored cue.

Everything here is plain data with no Home Assistant imports beyond storage,
so the shape can be reasoned about — and tested — on its own.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util
from homeassistant.util.uuid import random_uuid_hex

from .const import DOMAIN, STORAGE_KEY_SHOWS, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)

# Default prefix for auto-generated cue labels. "LX" is the standard theatre
# abbreviation for a lighting cue and is what every one of Stevie's existing
# shows uses. Per-show, so a production that numbers cues differently can.
DEFAULT_CUE_PREFIX = "LX"

# Splits "LX19a" into ("LX", "19", "a") so auto-numbering can find the highest
# cue so far and so an inserted cue can take a decimal between its neighbours.
_LABEL_RE = re.compile(r"^\s*([A-Za-z ]*?)\s*(\d+(?:\.\d+)?)\s*([A-Za-z]*)\s*$")


class CueKind(StrEnum):
    """What happens when this cue is fired."""

    LOOK = "look"
    """A static state of the whole rig, captured from the live lights."""

    EFFECT = "effect"
    """Something that moves, described by parameters and run by the engine."""


@dataclass(frozen=True)
class LightLevel:
    """One rig member's state within a look.

    Deliberately stores the colour in the mode the light reported, rather than
    normalising everything to RGB. A Hue lamp works in xy; round-tripping its
    colour through RGB and back visibly shifts it, and a designer who spent an
    hour on a wash will notice.
    """

    entity_id: str
    state: str
    """`on` or `off`. Anything else is treated as off when applied."""

    brightness: int | None = None
    """0-255, Home Assistant's scale, or None for a member with no dimming."""

    color_mode: str | None = None
    xy_color: tuple[float, float] | None = None
    hs_color: tuple[float, float] | None = None
    color_temp_kelvin: int | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"entity_id": self.entity_id, "state": self.state}
        if self.brightness is not None:
            out["brightness"] = self.brightness
        if self.color_mode is not None:
            out["color_mode"] = self.color_mode
        if self.xy_color is not None:
            out["xy_color"] = list(self.xy_color)
        if self.hs_color is not None:
            out["hs_color"] = list(self.hs_color)
        if self.color_temp_kelvin is not None:
            out["color_temp_kelvin"] = self.color_temp_kelvin
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LightLevel | None:
        """Rebuild from storage, or None if the record is unusable.

        Returns None rather than raising: one corrupt level must cost its
        fixture, not the whole cue list.
        """
        entity_id = data.get("entity_id")
        if not isinstance(entity_id, str) or "." not in entity_id:
            return None

        def _pair(key: str) -> tuple[float, float] | None:
            raw = data.get(key)
            if isinstance(raw, (list, tuple)) and len(raw) == 2:
                try:
                    return (float(raw[0]), float(raw[1]))
                except (TypeError, ValueError):
                    return None
            return None

        brightness = data.get("brightness")
        kelvin = data.get("color_temp_kelvin")
        return cls(
            entity_id=entity_id,
            state="on" if data.get("state") == "on" else "off",
            brightness=int(brightness)
            if isinstance(brightness, (int, float))
            else None,
            color_mode=data.get("color_mode")
            if isinstance(data.get("color_mode"), str)
            else None,
            xy_color=_pair("xy_color"),
            hs_color=_pair("hs_color"),
            color_temp_kelvin=int(kelvin) if isinstance(kelvin, (int, float)) else None,
        )


@dataclass
class Cue:
    """One press of GO."""

    id: str
    label: str
    """What the operator calls it — "LX1", "LX19a". Free text by design: real
    cue lists grow letters and decimals, and fighting that helps nobody."""

    kind: CueKind = CueKind.LOOK
    name: str = ""
    """Optional description — "house to half", "Carrie's entrance"."""

    fade: float = 0.0
    """Seconds. 0 is a snap, and a snap is the commonest cue there is: 43 of
    the 63 timed cues in *Company* were 0.05 s or 0.1 s."""

    levels: list[LightLevel] = field(default_factory=list)
    """LOOK only. The whole rig, off members included."""

    effect: str | None = None
    """EFFECT only. The engine's name for it — see `effects.py`."""

    effect_params: dict[str, Any] = field(default_factory=dict)
    """EFFECT only. Validated by the effect itself, not here."""

    notes: str = ""
    created: str = ""
    modified: str = ""

    bridge_scene_id: str | None = None
    """LOOK only. The bridge scene this look was compiled to, if any. A cache
    of bridge state, never the truth: the levels are. Written only when set
    so older shows round-trip unchanged."""

    def to_dict(self) -> dict[str, Any]:
        out = {
            "id": self.id,
            "label": self.label,
            "kind": str(self.kind),
            "name": self.name,
            "fade": self.fade,
            "levels": [level.to_dict() for level in self.levels],
            "effect": self.effect,
            "effect_params": dict(self.effect_params),
            "notes": self.notes,
            "created": self.created,
            "modified": self.modified,
        }
        if self.bridge_scene_id:
            out["bridge_scene_id"] = self.bridge_scene_id
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Cue | None:
        """Rebuild from storage, or None if the record is unusable."""
        cue_id = data.get("id")
        if not isinstance(cue_id, str) or not cue_id:
            return None

        kind = CueKind.EFFECT if data.get("kind") == "effect" else CueKind.LOOK
        raw_levels = data.get("levels")
        levels = []
        if isinstance(raw_levels, list):
            for raw in raw_levels:
                if isinstance(raw, dict) and (level := LightLevel.from_dict(raw)):
                    levels.append(level)

        fade = data.get("fade")
        params = data.get("effect_params")
        return cls(
            id=cue_id,
            label=str(data.get("label") or cue_id[:6]),
            kind=kind,
            name=str(data.get("name") or ""),
            fade=max(0.0, float(fade)) if isinstance(fade, (int, float)) else 0.0,
            levels=levels,
            effect=data.get("effect") if isinstance(data.get("effect"), str) else None,
            effect_params=dict(params) if isinstance(params, dict) else {},
            notes=str(data.get("notes") or ""),
            created=str(data.get("created") or ""),
            modified=str(data.get("modified") or ""),
            bridge_scene_id=data.get("bridge_scene_id")
            if isinstance(data.get("bridge_scene_id"), str)
            else None,
        )


def _rgb_list(raw: Any) -> list[list[int]]:
    """Keep only well-formed [r, g, b] triples, clamped to 0-255."""
    if not isinstance(raw, list):
        return []
    return [
        [max(0, min(255, int(c))) for c in rgb]
        for rgb in raw
        if isinstance(rgb, list)
        and len(rgb) == 3
        and all(isinstance(c, (int, float)) for c in rgb)
    ]


@dataclass
class Show:
    """One production, and its cue list."""

    id: str
    name: str
    cue_prefix: str = DEFAULT_CUE_PREFIX
    cues: list[Cue] = field(default_factory=list)
    created: str = ""
    modified: str = ""
    colors: list[list[int]] = field(default_factory=list)
    """Saved swatches, RGB. Written only when non-empty so a show recorded
    before this key existed round-trips byte-for-byte."""
    imported_from: str | None = None
    """The Hue room or zone this show was imported from. It is what lets the
    console delete that group's scenes from the bridge: the import is the
    backup. Written only when set."""

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "cue_prefix": self.cue_prefix,
            "cues": [cue.to_dict() for cue in self.cues],
            "created": self.created,
            "modified": self.modified,
        }
        if self.colors:
            out["colors"] = [list(rgb) for rgb in self.colors]
        if self.imported_from:
            out["imported_from"] = self.imported_from
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Show | None:
        show_id = data.get("id")
        if not isinstance(show_id, str) or not show_id:
            return None
        raw_cues = data.get("cues")
        cues = []
        if isinstance(raw_cues, list):
            for raw in raw_cues:
                if isinstance(raw, dict) and (cue := Cue.from_dict(raw)):
                    cues.append(cue)
        return cls(
            id=show_id,
            name=str(data.get("name") or "Untitled show"),
            cue_prefix=str(data.get("cue_prefix") or DEFAULT_CUE_PREFIX),
            cues=cues,
            created=str(data.get("created") or ""),
            modified=str(data.get("modified") or ""),
            colors=_rgb_list(data.get("colors")),
            imported_from=str(data.get("imported_from") or "") or None,
        )

    # ------------------------------------------------------------------
    # Cue lookup and labelling
    # ------------------------------------------------------------------

    def index_of(self, cue_id: str) -> int | None:
        for i, cue in enumerate(self.cues):
            if cue.id == cue_id:
                return i
        return None

    def cue(self, cue_id: str) -> Cue | None:
        i = self.index_of(cue_id)
        return self.cues[i] if i is not None else None

    def next_label(self) -> str:
        """The label a newly recorded cue should get.

        One past the highest number already used, so recording after a break
        continues the list rather than colliding with it.
        """
        highest = 0.0
        for cue in self.cues:
            if (m := _LABEL_RE.match(cue.label)) is not None:
                highest = max(highest, float(m.group(2)))
        nxt = int(highest) + 1
        return f"{self.cue_prefix}{nxt}"

    def label_between(self, before: int) -> str:
        """A label for a cue inserted at list position `before`.

        Takes the midpoint of its neighbours' numbers, which is what every
        real console does — inserting between LX3 and LX4 gives LX3.5, and
        nothing downstream has to be renumbered mid-tech.
        """

        def number_at(i: int) -> float | None:
            if 0 <= i < len(self.cues):
                if (m := _LABEL_RE.match(self.cues[i].label)) is not None:
                    return float(m.group(2))
            return None

        prev_n = number_at(before - 1)
        next_n = number_at(before)

        if prev_n is None and next_n is None:
            return f"{self.cue_prefix}1"
        if prev_n is None:
            # Inserting at the top: halve the first cue's number, or step back.
            return self._format_number(next_n / 2 if next_n > 1 else next_n - 0.5)
        if next_n is None:
            return f"{self.cue_prefix}{int(prev_n) + 1}"

        mid = (prev_n + next_n) / 2
        # Neighbours too close to split cleanly — fall back to appending a
        # letter, which is the other idiom already in Stevie's cue lists.
        if mid <= prev_n or mid >= next_n:
            return f"{self.cue_prefix}{self._format_number(prev_n)}a"
        return self._format_number(mid)

    def _format_number(self, n: float) -> str:
        text = f"{n:.3f}".rstrip("0").rstrip(".")
        return f"{self.cue_prefix}{text}"


class ShowStore:
    """Persists every show, and which one is on stage.

    Deliberately one store for all shows rather than one per show: the whole
    lot is a few hundred kilobytes at worst, and a single atomic write means
    a cue recorded during a tech rehearsal can never leave the list in a
    half-saved state.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{STORAGE_KEY_SHOWS}"
        )
        self._shows: list[Show] = []
        self._active_show_id: str | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if not data:
            return
        raw_shows = data.get("shows")
        if isinstance(raw_shows, list):
            for raw in raw_shows:
                if isinstance(raw, dict) and (show := Show.from_dict(raw)):
                    self._shows.append(show)
        else:
            _LOGGER.warning(
                "Show storage was malformed (%r); starting with no shows", data
            )
        active = data.get("active_show_id")
        if isinstance(active, str) and any(s.id == active for s in self._shows):
            self._active_show_id = active
        elif self._shows:
            self._active_show_id = self._shows[0].id

    async def async_save(self) -> None:
        await self._store.async_save(
            {
                "shows": [show.to_dict() for show in self._shows],
                "active_show_id": self._active_show_id,
            }
        )

    # ------------------------------------------------------------------
    # Shows
    # ------------------------------------------------------------------

    @property
    def shows(self) -> list[Show]:
        return list(self._shows)

    @property
    def active_show_id(self) -> str | None:
        return self._active_show_id

    @property
    def active_show(self) -> Show | None:
        if self._active_show_id is None:
            return None
        return self.show(self._active_show_id)

    def show(self, show_id: str) -> Show | None:
        for show in self._shows:
            if show.id == show_id:
                return show
        return None

    async def async_create_show(
        self, name: str, cue_prefix: str = DEFAULT_CUE_PREFIX
    ) -> Show:
        """Create an empty show and make it active.

        Making it active immediately is the whole point of the button: an
        operator who has just typed "Carrie" wants to start recording, not to
        then hunt for a second control that selects it.
        """
        now = dt_util.utcnow().isoformat()
        show = Show(
            id=random_uuid_hex(),
            name=name.strip() or "Untitled show",
            cue_prefix=cue_prefix.strip() or DEFAULT_CUE_PREFIX,
            created=now,
            modified=now,
        )
        self._shows.append(show)
        self._active_show_id = show.id
        await self.async_save()
        return show

    async def async_rename_show(
        self,
        show_id: str,
        name: str | None,
        cue_prefix: str | None = None,
        colors: list[list[int]] | None = None,
    ) -> Show | None:
        show = self.show(show_id)
        if show is None:
            return None
        if name is not None and name.strip():
            show.name = name.strip()
        if cue_prefix is not None and cue_prefix.strip():
            show.cue_prefix = cue_prefix.strip()
        if colors is not None:
            show.colors = _rgb_list(colors)
        show.modified = dt_util.utcnow().isoformat()
        await self.async_save()
        return show

    async def async_delete_show(self, show_id: str) -> bool:
        show = self.show(show_id)
        if show is None:
            return False
        self._shows.remove(show)
        if self._active_show_id == show_id:
            self._active_show_id = self._shows[0].id if self._shows else None
        await self.async_save()
        return True

    async def async_set_active_show(self, show_id: str) -> bool:
        if self.show(show_id) is None:
            return False
        self._active_show_id = show_id
        await self.async_save()
        return True

    async def async_duplicate_show(self, show_id: str, name: str) -> Show | None:
        """Copy a show, cues and all.

        Wanted for the case a revival genuinely happens — and as the safe way
        to experiment with a cue list without risking the one that is running.
        """
        source = self.show(show_id)
        if source is None:
            return None
        now = dt_util.utcnow().isoformat()
        copy = Show.from_dict(source.to_dict())
        assert copy is not None  # round-trip of a valid show always succeeds
        copy.id = random_uuid_hex()
        copy.name = name.strip() or f"{source.name} (copy)"
        copy.created = now
        copy.modified = now
        for cue in copy.cues:
            cue.id = random_uuid_hex()
        self._shows.append(copy)
        await self.async_save()
        return copy

    # ------------------------------------------------------------------
    # Cues
    # ------------------------------------------------------------------

    async def async_add_cue(
        self, show_id: str, cue: Cue, at: int | None = None
    ) -> Cue | None:
        """Insert a cue, appending by default.

        `at` is a list position, not a cue number. When inserting rather than
        appending the label is recomputed from the neighbours, so the caller
        never has to think about numbering.
        """
        show = self.show(show_id)
        if show is None:
            return None
        now = dt_util.utcnow().isoformat()
        cue.created = cue.created or now
        cue.modified = now

        if at is None or at >= len(show.cues):
            if not cue.label:
                cue.label = show.next_label()
            show.cues.append(cue)
        else:
            position = max(0, at)
            if not cue.label:
                cue.label = show.label_between(position)
            show.cues.insert(position, cue)

        show.modified = now
        await self.async_save()
        return cue

    async def async_add_cues(self, show_id: str, cues: list[Cue]) -> int:
        """Append many cues in one write.

        Import is the reason this exists. Adding 127 cues one at a time would
        rewrite the whole store 127 times; a bulk append makes an import one
        atomic write, so a crash halfway through cannot leave half a show.
        """
        show = self.show(show_id)
        if show is None:
            return 0
        now = dt_util.utcnow().isoformat()
        for cue in cues:
            cue.created = cue.created or now
            cue.modified = now
            if not cue.label:
                cue.label = show.next_label()
            show.cues.append(cue)
        show.modified = now
        await self.async_save()
        return len(cues)

    async def async_update_cue(
        self, show_id: str, cue_id: str, changes: dict[str, Any]
    ) -> Cue | None:
        """Apply a partial update to one cue.

        Only the keys present are touched, so the card can send just the field
        the operator edited. `levels` and `effect_params` are replaced whole
        rather than merged — a half-merged look is not a thing anyone wants.
        """
        show = self.show(show_id)
        if show is None:
            return None
        cue = show.cue(cue_id)
        if cue is None:
            return None

        if "label" in changes and str(changes["label"]).strip():
            cue.label = str(changes["label"]).strip()
        if "name" in changes:
            cue.name = str(changes["name"] or "")
        if "notes" in changes:
            cue.notes = str(changes["notes"] or "")
        if "fade" in changes:
            try:
                cue.fade = max(0.0, float(changes["fade"]))
            except (TypeError, ValueError):
                pass
        if "kind" in changes and changes["kind"] in ("look", "effect"):
            cue.kind = CueKind(changes["kind"])
        if "effect" in changes:
            cue.effect = (
                str(changes["effect"]) if isinstance(changes["effect"], str) else None
            )
        if "effect_params" in changes and isinstance(changes["effect_params"], dict):
            cue.effect_params = dict(changes["effect_params"])
        if "levels" in changes and isinstance(changes["levels"], list):
            levels = []
            for raw in changes["levels"]:
                if isinstance(raw, dict) and (level := LightLevel.from_dict(raw)):
                    levels.append(level)
            cue.levels = levels

        now = dt_util.utcnow().isoformat()
        cue.modified = now
        show.modified = now
        await self.async_save()
        return cue

    async def async_duplicate_cue(self, show_id: str, cue_id: str) -> Cue | None:
        """Copy a cue in place: same levels and parameters, new id, next in the list."""
        show = self.show(show_id)
        if show is None or (index := show.index_of(cue_id)) is None:
            return None
        source = show.cues[index]
        copy = Cue.from_dict(source.to_dict())
        assert copy is not None  # round-trip of a valid cue always succeeds
        copy.id = random_uuid_hex()
        copy.label = f"{source.label} copy"
        copy.created = ""
        return await self.async_add_cue(show_id, copy, at=index + 1)

    async def async_delete_cue(self, show_id: str, cue_id: str) -> bool:
        show = self.show(show_id)
        if show is None:
            return False
        index = show.index_of(cue_id)
        if index is None:
            return False
        show.cues.pop(index)
        show.modified = dt_util.utcnow().isoformat()
        await self.async_save()
        return True

    async def async_reorder_cues(self, show_id: str, cue_ids: list[str]) -> bool:
        """Reorder the cue list.

        Rejects anything that is not a permutation of the current list. A
        reorder that silently dropped a cue would be discovered on stage.
        """
        show = self.show(show_id)
        if show is None:
            return False
        if sorted(cue_ids) != sorted(cue.id for cue in show.cues):
            return False
        by_id = {cue.id: cue for cue in show.cues}
        show.cues = [by_id[cue_id] for cue_id in cue_ids]
        show.modified = dt_util.utcnow().isoformat()
        await self.async_save()
        return True
