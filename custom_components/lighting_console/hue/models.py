"""Typed views over the CLIP v2 resources this project cares about.

Only the fields the console actually uses are modelled. The bridge returns a
great deal more, and mirroring all of it would be a maintenance cost with no
benefit — but `raw` is kept on each model so a debugging session never has to
change the parser to see what the bridge really said.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BridgeInfo:
    """Identity of a bridge, readable without authenticating."""

    bridge_id: str
    name: str
    swversion: str
    apiversion: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_config(cls, data: dict[str, Any]) -> BridgeInfo:
        return cls(
            bridge_id=str(data.get("bridgeid", "")).lower(),
            name=data.get("name", "Hue Bridge"),
            swversion=str(data.get("swversion", "")),
            apiversion=str(data.get("apiversion", "")),
            raw=data,
        )


@dataclass(frozen=True)
class HueLight:
    """A `light` resource on the bridge."""

    id: str
    """The v2 resource id (a UUID)."""

    owner_id: str
    """The `device` resource that owns this light."""

    name: str
    supports_color: bool
    """True when the light has a `color` service — the gate on entertainment
    area membership. Hue white bulbs and white-ambiance bulbs do not."""

    supports_color_temperature: bool
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_resource(cls, data: dict[str, Any]) -> HueLight:
        metadata = data.get("metadata") or {}
        owner = data.get("owner") or {}
        return cls(
            id=data["id"],
            owner_id=owner.get("rid", ""),
            name=metadata.get("name", "") or data.get("id", ""),
            supports_color="color" in data,
            supports_color_temperature="color_temperature" in data,
            raw=data,
        )


@dataclass(frozen=True)
class EntertainmentConfiguration:
    """An entertainment area, and the lights it can address.

    `channel_light_ids` is what matters for streaming: the stream addresses
    *channels*, and each channel maps to one or more entertainment services,
    each owned by a device that also owns a light. Resolving that chain is the
    client's job so callers can think in terms of lights.
    """

    id: str
    name: str
    status: str
    """`active` while something is streaming to it, otherwise `inactive`."""

    channel_light_ids: dict[int, list[str]] = field(default_factory=dict)
    """Channel index -> the `light` resource ids that channel drives."""

    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def is_streaming(self) -> bool:
        return self.status == "active"

    @property
    def light_ids(self) -> set[str]:
        """Every light reachable through this area."""
        return {
            light_id
            for lights in self.channel_light_ids.values()
            for light_id in lights
        }


@dataclass(frozen=True)
class HueSceneAction:
    """What one scene does to one light.

    Brightness is the bridge's 0-100 percentage, not Home Assistant's 0-255,
    and is left that way here. Converting at the edge of the parser would put
    a rounding step somewhere nobody looking at an import bug would think to
    check; the importer converts, visibly, once.
    """

    light_id: str
    on: bool
    brightness_pct: float | None = None
    xy: tuple[float, float] | None = None
    mirek: int | None = None

    @classmethod
    def from_action(cls, data: dict[str, Any]) -> HueSceneAction | None:
        target = data.get("target") or {}
        if target.get("rtype") != "light" or not target.get("rid"):
            return None
        action = data.get("action") or {}
        dimming = action.get("dimming") or {}
        color = (action.get("color") or {}).get("xy") or {}
        temperature = action.get("color_temperature") or {}

        xy = None
        if "x" in color and "y" in color:
            try:
                xy = (float(color["x"]), float(color["y"]))
            except (TypeError, ValueError):
                xy = None

        mirek = temperature.get("mirek")
        brightness = dimming.get("brightness")
        return cls(
            light_id=target["rid"],
            on=bool((action.get("on") or {}).get("on", True)),
            brightness_pct=float(brightness)
            if isinstance(brightness, (int, float))
            else None,
            xy=xy,
            mirek=int(mirek) if isinstance(mirek, (int, float)) else None,
        )


@dataclass(frozen=True)
class HueScene:
    """A `scene` resource: one stored look, owned by a room or a zone.

    This is the unit Stevie's existing shows are actually built from — 141 of
    the 144 scenes on his instance live on the bridge rather than in Home
    Assistant, one per cue. Importing them is how a decade of previous
    productions gets into the console.
    """

    id: str
    name: str
    group_id: str
    group_type: str
    actions: list[HueSceneAction] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_resource(cls, data: dict[str, Any]) -> HueScene:
        metadata = data.get("metadata") or {}
        group = data.get("group") or {}
        actions = []
        for raw in data.get("actions") or []:
            if isinstance(raw, dict) and (action := HueSceneAction.from_action(raw)):
                actions.append(action)
        return cls(
            id=data["id"],
            name=metadata.get("name", "") or data.get("id", ""),
            group_id=group.get("rid", ""),
            group_type=group.get("rtype", ""),
            actions=actions,
            raw=data,
        )


@dataclass(frozen=True)
class HueGroup:
    """A room or a zone — what a scene belongs to, and what the card offers
    as "which show do you want to import?"."""

    id: str
    name: str
    type: str
    """`room` or `zone`."""

    light_ids: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)
