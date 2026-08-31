"""The rig: which Home Assistant entities the console considers "the lights".

Two things live here.

**Membership** is a plain ordered list of entity ids, persisted in Home
Assistant's storage so it survives a restart. Deliberately not a config-entry
option: the rig changes during a get-in, sometimes several times an hour, and
it belongs in the console's own UI rather than behind Settings.

**Classification** answers the question every later milestone depends on: can
this entity ever be driven by the Entertainment stream, or must it always go
through normal Home Assistant services? Only genuine Hue colour lights that
sit in an entertainment area can stream. Everything else — Hue white bulbs,
third-party Zigbee, switches, plugs, dimmers — is a first-class member of
every cue but is always REST-driven.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from homeassistant.core import HomeAssistant, split_entity_id
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store

from .const import DOMAIN, HUE_INTEGRATION_DOMAIN, STORAGE_KEY_RIG, STORAGE_VERSION
from .hue import EntertainmentConfiguration, HueLight

_LOGGER = logging.getLogger(__name__)

# Colour modes that mean "this light can be told an actual colour". A light
# with only brightness or colour temperature cannot join an entertainment
# area, however Hue it is.
COLOR_MODES = {"hs", "xy", "rgb", "rgbw", "rgbww"}


class Capability(StrEnum):
    """How the console is able to drive one rig entity."""

    STREAMABLE = "streamable"
    """A Hue colour light in an entertainment area. Effects can drive it."""

    HUE_COLOR_NO_AREA = "hue_color_no_area"
    """A Hue colour light that is not in any entertainment area. It could
    stream if it were added to one — this is the actionable case, and the card
    says so rather than silently treating it as REST-only."""

    REST_ONLY = "rest_only"
    """Driven through normal Home Assistant services, always. Correct and
    expected for white bulbs, plugs, switches and non-Hue lights."""

    UNAVAILABLE = "unavailable"
    """In the rig, but Home Assistant does not currently have this entity.
    Kept in the list rather than dropped: a bulb that is switched off at the
    wall during a get-in must not silently vanish from the rig."""


@dataclass(frozen=True)
class RigMember:
    """One entity in the rig, with everything the card needs to render it."""

    entity_id: str
    name: str
    domain: str
    capability: Capability
    reason: str
    """Why it has that capability, in words an operator can act on."""

    hue_light_id: str | None = None
    entertainment_area: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"capability": str(self.capability)}


class RigStore:
    """Persists rig membership across restarts."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{STORAGE_KEY_RIG}"
        )
        self._entity_ids: list[str] = []
        self._loaded = False

    @property
    def entity_ids(self) -> list[str]:
        """Rig membership, in the order it was added."""
        return list(self._entity_ids)

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if data:
            # Tolerate a hand-edited or partially written store rather than
            # failing setup: an unusable rig is recoverable, a console that
            # will not start mid-show is not.
            raw = data.get("entities")
            if isinstance(raw, list):
                self._entity_ids = [e for e in raw if isinstance(e, str)]
            else:
                _LOGGER.warning(
                    "Rig storage was malformed (%r); starting with an empty rig",
                    data,
                )
        self._loaded = True

    async def _async_save(self) -> None:
        await self._store.async_save({"entities": self._entity_ids})

    async def async_add(self, entity_ids: list[str]) -> list[str]:
        """Add entities to the rig. Returns the ones actually added."""
        added = []
        for entity_id in entity_ids:
            if entity_id not in self._entity_ids:
                self._entity_ids.append(entity_id)
                added.append(entity_id)
        if added:
            await self._async_save()
        return added

    async def async_remove(self, entity_ids: list[str]) -> list[str]:
        """Remove entities from the rig. Returns the ones actually removed."""
        removed = [e for e in entity_ids if e in self._entity_ids]
        if removed:
            self._entity_ids = [e for e in self._entity_ids if e not in removed]
            await self._async_save()
        return removed

    async def async_reorder(self, entity_ids: list[str]) -> None:
        """Replace the rig with exactly this list, in this order.

        Rejects a reorder that would add or drop members — that would silently
        turn a drag-and-drop into a destructive edit.
        """
        if set(entity_ids) != set(self._entity_ids):
            raise ValueError(
                "A reorder must contain exactly the current rig members. "
                "Use add/remove to change membership."
            )
        self._entity_ids = list(entity_ids)
        await self._async_save()


def hue_light_id_for_entity(
    hass: HomeAssistant, entity_id: str, hue_lights_by_id: dict[str, HueLight]
) -> str | None:
    """Map a Home Assistant entity to a Hue `light` resource id, if it is one.

    Tried in order of directness:
      1. The entity registry unique id. Home Assistant's Hue integration uses
         the v2 resource id there, so this is usually an exact hit.
      2. The device registry identifiers, matching the owning Hue device
         against the device that owns each light.

    Both are checked because neither is a documented contract, and a wrong
    answer here shows up much later as "why will this light not stream".
    """
    registry = er.async_get(hass)
    entry = registry.async_get(entity_id)
    if entry is None:
        return None

    if entry.unique_id and entry.unique_id in hue_lights_by_id:
        return entry.unique_id

    if entry.device_id:
        devices = dr.async_get(hass)
        device = devices.async_get(entry.device_id)
        if device:
            hue_device_ids = {
                identifier
                for domain, identifier in device.identifiers
                if domain == HUE_INTEGRATION_DOMAIN
            }
            for light in hue_lights_by_id.values():
                if light.owner_id and light.owner_id in hue_device_ids:
                    return light.id

    return None


def classify(
    hass: HomeAssistant,
    entity_id: str,
    hue_lights_by_id: dict[str, HueLight] | None = None,
    entertainment_configurations: list[EntertainmentConfiguration] | None = None,
) -> RigMember:
    """Work out how the console can drive one entity.

    `hue_lights_by_id` and `entertainment_configurations` are optional: with no
    bridge paired the console still works, everything is simply REST-only.
    """
    hue_lights_by_id = hue_lights_by_id or {}
    entertainment_configurations = entertainment_configurations or []

    domain = split_entity_id(entity_id)[0]
    state = hass.states.get(entity_id)

    if state is None:
        return RigMember(
            entity_id=entity_id,
            name=entity_id,
            domain=domain,
            capability=Capability.UNAVAILABLE,
            reason=(
                "Home Assistant does not currently have this entity. It stays "
                "in the rig; cues that reference it will skip it until it "
                "comes back."
            ),
        )

    name = state.attributes.get("friendly_name") or entity_id

    if domain != "light":
        return RigMember(
            entity_id=entity_id,
            name=name,
            domain=domain,
            capability=Capability.REST_ONLY,
            reason=(
                f"A {domain} entity is driven through Home Assistant services. "
                "Only Hue colour lights can stream."
            ),
        )

    hue_light_id = hue_light_id_for_entity(hass, entity_id, hue_lights_by_id)
    supported_modes = set(state.attributes.get("supported_color_modes") or [])
    is_colour = bool(supported_modes & COLOR_MODES)

    if hue_light_id is None:
        reason = (
            "Not a Hue light on the paired bridge, so it is driven through "
            "Home Assistant services."
            if hue_lights_by_id
            else "No Hue bridge is paired yet, so every light is REST-driven."
        )
        return RigMember(
            entity_id=entity_id,
            name=name,
            domain=domain,
            capability=Capability.REST_ONLY,
            reason=reason,
        )

    hue_light = hue_lights_by_id[hue_light_id]
    if not (hue_light.supports_color and is_colour):
        return RigMember(
            entity_id=entity_id,
            name=name,
            domain=domain,
            capability=Capability.REST_ONLY,
            reason=(
                "This is a Hue light, but it has no colour control, so it "
                "cannot be part of an entertainment area."
            ),
            hue_light_id=hue_light_id,
        )

    for configuration in entertainment_configurations:
        if hue_light_id in configuration.light_ids:
            return RigMember(
                entity_id=entity_id,
                name=name,
                domain=domain,
                capability=Capability.STREAMABLE,
                reason=f"In entertainment area {configuration.name!r}.",
                hue_light_id=hue_light_id,
                entertainment_area=configuration.name,
            )

    return RigMember(
        entity_id=entity_id,
        name=name,
        domain=domain,
        capability=Capability.HUE_COLOR_NO_AREA,
        reason=(
            "A Hue colour light that is not in any entertainment area. Add it "
            "to one and effects will be able to drive it."
        ),
        hue_light_id=hue_light_id,
    )
