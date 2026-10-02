"""One sensor for a Stream Deck: where the show is.

State is the label of the cue on stage; the attributes carry what the next GO
will fire. It is recomputed from the console on every change signal, never
cached, so it cannot disagree with the card.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .console import Console
from .const import DOMAIN, NAME


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([CueSensor(hass.data[DOMAIN][entry.entry_id], entry)])


class CueSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Cue"
    _attr_should_poll = False

    def __init__(self, console: Console, entry: ConfigEntry) -> None:
        self._console = console
        self._attr_unique_id = f"{entry.entry_id}_cue"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._console.signal, self.async_write_ha_state
            )
        )

    def _playhead(self) -> tuple[Any, Any, Any]:
        """(show, current cue, the cue GO would fire next)."""
        show = self._console.shows.active_show
        cues = show.cues if show else []
        index = self._console.playback.status(show)["current_index"]
        current = cues[index] if index is not None else None
        nxt = 0 if index is None else index + 1
        return show, current, cues[nxt] if nxt < len(cues) else None

    @property
    def native_value(self) -> str | None:
        _, current, _ = self._playhead()
        return current.label if current else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        show, current, nxt = self._playhead()
        effect = self._console.effects.status()["running"]
        return {
            "cue_name": current.name if current else None,
            "next_cue": nxt.label if nxt else None,
            "next_cue_name": nxt.name if nxt else None,
            "show": show.name if show else None,
            "cue_count": len(show.cues) if show else 0,
            "effect_running": effect is not None,
            "effect": effect,
        }
