"""The Lighting Console integration.

A theatre lighting console that lives inside Home Assistant: a cue list with
GO, cues that capture the whole rig, and effects driven over the Hue
Entertainment streaming API with a REST fallback.

At this milestone the console knows what the rig is, holds a cue list per
show, records cues from the live rig, fires them with a fade, and runs
effects over normal Home Assistant services. Streaming comes later.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .console import Console
from .const import BUILD_GIT_SHA, BUILD_VERSION, DOMAIN
from .frontend import async_register_card
from .websocket import async_register_commands

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Lighting Console from a config entry."""
    _LOGGER.info("Lighting Console %s (%s) starting up", BUILD_VERSION, BUILD_GIT_SHA)

    # First, before anything that can block. Until this runs, the card URL
    # 404s while Home Assistant is already serving dashboards, and a dashboard
    # opened in that window renders a permanent Configuration error. Console
    # setup reads storage and then makes an HTTP call to the Hue bridge, so
    # leaving the card behind it put a network round-trip — and, with an
    # unreachable bridge, a timeout — inside that window for no reason.
    # Registering the card needs nothing the console provides.
    await async_register_card(hass)

    console = Console(hass, entry)
    await console.async_setup()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = console

    async_register_commands(hass)

    # Re-read the bridge when the entry is reconfigured — pairing happens in
    # the config flow, and without this the console would keep reporting "no
    # bridge" until the next restart.
    entry.async_on_unload(entry.add_update_listener(_async_entry_updated))

    if PLATFORMS:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_entry_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after the entry's data changes, e.g. after pairing a bridge."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    The static path and the extra JS URL are registered for the lifetime of
    the Home Assistant process and are intentionally not torn down here:
    re-registering the same static path on reload raises, and a stale card
    asset is harmless compared with a failed reload mid-show.
    """
    # Before anything else, and whether or not the rest of the unload works:
    # a running effect is a loop calling light services, and once this entry
    # is gone nothing is left that knows how to stop it. This is the local
    # half of "a stream must never outlive the show".
    console: Console | None = (hass.data.get(DOMAIN) or {}).get(entry.entry_id)
    if console is not None:
        await console.async_unload()

    unload_ok = True
    if PLATFORMS:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
