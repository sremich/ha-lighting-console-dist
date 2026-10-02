"""Home Assistant services: the same moves the card makes, for a Stream Deck.

Each one is a thin wrapper over the playback call the matching WebSocket
command already makes. They are registered once, in `async_setup`, so they
exist whether or not the config entry is loaded — and say so plainly when it
is not, rather than vanishing from the service list mid-show.
"""

from __future__ import annotations

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from .console import Console
from .const import DOMAIN
from .cues import Cue, Show
from .websocket import _console

SERVICE_GO = "go"
SERVICE_BACK = "back"
SERVICE_GOTO = "goto"
SERVICE_RELEASE = "release"
SERVICE_STOP_EFFECT = "stop_effect"

ATTR_CUE_ID = "cue_id"


def _loaded(hass: HomeAssistant) -> Console:
    console = _console(hass)
    if console is None:
        raise HomeAssistantError("The Lighting Console integration is not loaded.")
    return console


def _active_show(console: Console) -> Show:
    show = console.shows.active_show
    if show is None:
        raise ServiceValidationError("There is no active show to play.")
    return show


def _find_cue(show: Show, ref: str) -> Cue:
    """A cue by id, or by label ("LX5", case-insensitive) as operators say it.

    Ids are unique; labels are free text and could repeat, so an ambiguous
    label is an error rather than a guess — Goto fires lights on a live stage.
    """
    if (cue := show.cue(ref)) is not None:
        return cue
    wanted = ref.strip().casefold()
    matches = [cue for cue in show.cues if cue.label.strip().casefold() == wanted]
    if not matches:
        raise ServiceValidationError(f"No cue {ref!r} in show {show.name!r}.")
    if len(matches) > 1:
        raise ServiceValidationError(
            f"{len(matches)} cues in show {show.name!r} are labelled {ref!r}; "
            "use the cue id instead."
        )
    return matches[0]


async def _async_go(call: ServiceCall) -> None:
    console = _loaded(call.hass)
    await console.playback.async_go(_active_show(console), console.rig.entity_ids)


async def _async_back(call: ServiceCall) -> None:
    console = _loaded(call.hass)
    await console.playback.async_back(_active_show(console), console.rig.entity_ids)


async def _async_goto(call: ServiceCall) -> None:
    console = _loaded(call.hass)
    show = _active_show(console)
    cue = _find_cue(show, call.data[ATTR_CUE_ID])
    await console.playback.async_goto(show, cue.id, console.rig.entity_ids)


async def _async_release(call: ServiceCall) -> None:
    # Needs nothing but the console: no show, no cue, no bridge.
    console = _loaded(call.hass)
    await console.playback.async_release(console.rig.entity_ids)


async def _async_stop_effect(call: ServiceCall) -> None:
    await _loaded(call.hass).effects.async_stop()


def async_register_services(hass: HomeAssistant) -> None:
    """Register the services. Called from `async_setup`, once per process."""
    empty = vol.Schema({})
    hass.services.async_register(DOMAIN, SERVICE_GO, _async_go, empty)
    hass.services.async_register(DOMAIN, SERVICE_BACK, _async_back, empty)
    hass.services.async_register(DOMAIN, SERVICE_RELEASE, _async_release, empty)
    hass.services.async_register(DOMAIN, SERVICE_STOP_EFFECT, _async_stop_effect, empty)
    hass.services.async_register(
        DOMAIN,
        SERVICE_GOTO,
        _async_goto,
        vol.Schema({vol.Required(ATTR_CUE_ID): vol.All(str, vol.Length(min=1))}),
    )
