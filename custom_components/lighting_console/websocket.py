"""WebSocket API: the card to backend channel.

Every command is namespaced `lighting_console/...`. The card is the only
client, but these are a real API surface: a physical button or an automation
could drive them later, so they validate input and return errors the card can
render rather than raising.

**Nothing here ever returns a bridge credential.** The card is told whether a
bridge is paired and whether a client key is held, never their values.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.uuid import random_uuid_hex

from .console import Console
from .const import BUILD_GIT_SHA, BUILD_VERSION, DOMAIN
from .cues import Cue, CueKind
from .effects import EFFECTS, describe_effects
from .playback import resolve_targets

WS_TYPE_INFO = f"{DOMAIN}/info"
WS_TYPE_RIG_LIST = f"{DOMAIN}/rig/list"
WS_TYPE_RIG_ADD = f"{DOMAIN}/rig/add"
WS_TYPE_RIG_REMOVE = f"{DOMAIN}/rig/remove"
WS_TYPE_RIG_REORDER = f"{DOMAIN}/rig/reorder"
WS_TYPE_RIG_CANDIDATES = f"{DOMAIN}/rig/candidates"
WS_TYPE_BRIDGE_STATUS = f"{DOMAIN}/bridge/status"
WS_TYPE_BRIDGE_REFRESH = f"{DOMAIN}/bridge/refresh"

WS_TYPE_SHOW_LIST = f"{DOMAIN}/shows/list"
WS_TYPE_SHOW_CREATE = f"{DOMAIN}/shows/create"
WS_TYPE_SHOW_RENAME = f"{DOMAIN}/shows/rename"
WS_TYPE_SHOW_DELETE = f"{DOMAIN}/shows/delete"
WS_TYPE_SHOW_ACTIVATE = f"{DOMAIN}/shows/activate"
WS_TYPE_SHOW_DUPLICATE = f"{DOMAIN}/shows/duplicate"

WS_TYPE_CUE_RECORD = f"{DOMAIN}/cues/record"
WS_TYPE_CUE_RERECORD = f"{DOMAIN}/cues/rerecord"
WS_TYPE_CUE_ADD_EFFECT = f"{DOMAIN}/cues/add_effect"
WS_TYPE_CUE_UPDATE = f"{DOMAIN}/cues/update"
WS_TYPE_CUE_DUPLICATE = f"{DOMAIN}/cues/duplicate"
WS_TYPE_CUE_DELETE = f"{DOMAIN}/cues/delete"
WS_TYPE_CUE_REORDER = f"{DOMAIN}/cues/reorder"

WS_TYPE_PLAYBACK_GO = f"{DOMAIN}/playback/go"
WS_TYPE_PLAYBACK_BACK = f"{DOMAIN}/playback/back"
WS_TYPE_PLAYBACK_GOTO = f"{DOMAIN}/playback/goto"
WS_TYPE_PLAYBACK_RELEASE = f"{DOMAIN}/playback/release"

WS_TYPE_EFFECTS_LIST = f"{DOMAIN}/effects/list"
WS_TYPE_EFFECTS_PREVIEW = f"{DOMAIN}/effects/preview"
WS_TYPE_EFFECTS_STOP = f"{DOMAIN}/effects/stop"

WS_TYPE_IMPORT_GROUPS = f"{DOMAIN}/import/groups"
WS_TYPE_IMPORT_RUN = f"{DOMAIN}/import/run"

ERR_NO_CONSOLE = "no_console"
ERR_INVALID_REORDER = "invalid_reorder"
ERR_NO_SHOW = "no_show"
ERR_NOT_FOUND = "not_found"
ERR_UNKNOWN_EFFECT = "unknown_effect"
ERR_NO_BRIDGE = "no_bridge"
ERR_NOTHING_TO_IMPORT = "nothing_to_import"


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    """Register every WebSocket command this integration exposes."""
    for command in (
        websocket_info,
        websocket_rig_list,
        websocket_rig_add,
        websocket_rig_remove,
        websocket_rig_reorder,
        websocket_rig_candidates,
        websocket_bridge_status,
        websocket_bridge_refresh,
        websocket_show_list,
        websocket_show_create,
        websocket_show_rename,
        websocket_show_delete,
        websocket_show_activate,
        websocket_show_duplicate,
        websocket_cue_record,
        websocket_cue_rerecord,
        websocket_cue_add_effect,
        websocket_cue_update,
        websocket_cue_duplicate,
        websocket_cue_delete,
        websocket_cue_reorder,
        websocket_playback_go,
        websocket_playback_back,
        websocket_playback_goto,
        websocket_playback_release,
        websocket_effects_list,
        websocket_effects_preview,
        websocket_effects_stop,
        websocket_import_groups,
        websocket_import_run,
    ):
        websocket_api.async_register_command(hass, command)


def _console(hass: HomeAssistant) -> Console | None:
    """The single console instance, or None if the entry is not loaded."""
    entries = list((hass.data.get(DOMAIN) or {}).values())
    return entries[0] if entries else None


def _require_console(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> Console | None:
    console = _console(hass)
    if console is None:
        connection.send_error(
            msg["id"],
            ERR_NO_CONSOLE,
            "The Lighting Console integration is not set up.",
        )
    return console


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_INFO})
@callback
def websocket_info(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Build metadata plus a one-glance summary for the card's status corner."""
    console = _console(hass)
    connection.send_result(
        msg["id"],
        {
            "version": BUILD_VERSION,
            "git_sha": BUILD_GIT_SHA,
            "rig_entity_count": len(console.rig.entity_ids) if console else 0,
            "bridge_configured": console.is_bridge_configured if console else False,
            # No streaming exists until milestone 3. Reported as a fixed value
            # rather than omitted so the card's shape stays stable.
            "streaming": False,
            "streaming_unavailable_reason": "Streaming arrives in a later version.",
        },
    )


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_RIG_LIST})
@callback
def websocket_rig_list(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """The rig, with each member classified."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    connection.send_result(msg["id"], console.rig_summary())


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_RIG_ADD,
        vol.Required("entity_ids"): [str],
    }
)
@websocket_api.async_response
async def websocket_rig_add(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    added = await console.rig.async_add(msg["entity_ids"])
    connection.send_result(msg["id"], {"added": added} | console.rig_summary())


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_RIG_REMOVE,
        vol.Required("entity_ids"): [str],
    }
)
@websocket_api.async_response
async def websocket_rig_remove(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    removed = await console.rig.async_remove(msg["entity_ids"])
    connection.send_result(msg["id"], {"removed": removed} | console.rig_summary())


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_RIG_REORDER,
        vol.Required("entity_ids"): [str],
    }
)
@websocket_api.async_response
async def websocket_rig_reorder(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    try:
        await console.rig.async_reorder(msg["entity_ids"])
    except ValueError as err:
        # A reorder that changes membership is a bug in the caller, not a
        # user action to apply silently.
        connection.send_error(msg["id"], ERR_INVALID_REORDER, str(err))
        return
    connection.send_result(msg["id"], console.rig_summary())


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_RIG_CANDIDATES})
@callback
def websocket_rig_candidates(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Lights and switches not already in the rig."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    connection.send_result(msg["id"], {"candidates": console.candidate_entities()})


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_BRIDGE_STATUS})
@callback
def websocket_bridge_status(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    connection.send_result(msg["id"], console.bridge_status())


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_BRIDGE_REFRESH})
@websocket_api.async_response
async def websocket_bridge_refresh(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Re-read the bridge — used after editing entertainment areas in the Hue app."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    await console.async_refresh_bridge()
    connection.send_result(
        msg["id"], console.bridge_status() | {"rig": console.rig_summary()}
    )


# ----------------------------------------------------------------------
# Shows
#
# Every mutating command answers with the whole show summary rather than a
# diff. The card then has exactly one way to learn the truth, which removes
# the entire class of bug where an optimistic local edit and the backend
# disagree about a cue list during a show.
# ----------------------------------------------------------------------


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_SHOW_LIST})
@callback
def websocket_show_list(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Every show, the active one's cues, and the playhead."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    connection.send_result(msg["id"], console.show_summary())


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_SHOW_CREATE,
        vol.Required("name"): str,
        vol.Optional("cue_prefix"): str,
    }
)
@websocket_api.async_response
async def websocket_show_create(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Create an empty show and make it active."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    await console.shows.async_create_show(msg["name"], msg.get("cue_prefix") or "LX")
    console.playback.reset()
    connection.send_result(msg["id"], console.show_summary())


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_SHOW_RENAME,
        vol.Required("show_id"): str,
        vol.Optional("name"): str,
        vol.Optional("cue_prefix"): str,
        vol.Optional("colors"): [[int]],
    }
)
@websocket_api.async_response
async def websocket_show_rename(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    show = await console.shows.async_rename_show(
        msg["show_id"], msg.get("name"), msg.get("cue_prefix"), msg.get("colors")
    )
    if show is None:
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such show.")
        return
    connection.send_result(msg["id"], console.show_summary())


@websocket_api.websocket_command(
    {vol.Required("type"): WS_TYPE_SHOW_DELETE, vol.Required("show_id"): str}
)
@websocket_api.async_response
async def websocket_show_delete(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete a show and its whole cue list.

    Stops any running effect first. Deleting the show that is currently on
    stage while a chase is running would otherwise leave the chase going with
    nothing left that knows how to stop it.
    """
    if (console := _require_console(hass, connection, msg)) is None:
        return
    if not await console.shows.async_delete_show(msg["show_id"]):
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such show.")
        return
    await console.effects.async_stop()
    console.playback.reset()
    connection.send_result(msg["id"], console.show_summary())


@websocket_api.websocket_command(
    {vol.Required("type"): WS_TYPE_SHOW_ACTIVATE, vol.Required("show_id"): str}
)
@websocket_api.async_response
async def websocket_show_activate(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    if not await console.shows.async_set_active_show(msg["show_id"]):
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such show.")
        return
    # The playhead pointed into a different cue list and means nothing here.
    console.playback.reset()
    connection.send_result(msg["id"], console.show_summary())


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_SHOW_DUPLICATE,
        vol.Required("show_id"): str,
        vol.Required("name"): str,
    }
)
@websocket_api.async_response
async def websocket_show_duplicate(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    if await console.shows.async_duplicate_show(msg["show_id"], msg["name"]) is None:
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such show.")
        return
    connection.send_result(msg["id"], console.show_summary())


# ----------------------------------------------------------------------
# Cues
# ----------------------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_CUE_RECORD,
        vol.Optional("name"): str,
        vol.Optional("at"): int,
        vol.Optional("fade"): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def websocket_cue_record(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Capture the live rig as a new cue. The whole point of the product."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    if console.shows.active_show is None:
        connection.send_error(
            msg["id"], ERR_NO_SHOW, "Create a show before recording a cue."
        )
        return
    cue = await console.async_record_cue(
        name=msg.get("name", ""), at=msg.get("at"), fade=float(msg.get("fade", 0.0))
    )
    connection.send_result(
        msg["id"],
        {"cue": cue.to_dict() if cue else None, **console.show_summary()},
    )


@websocket_api.websocket_command(
    {vol.Required("type"): WS_TYPE_CUE_RERECORD, vol.Required("cue_id"): str}
)
@websocket_api.async_response
async def websocket_cue_rerecord(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Replace one cue's look with what the lights are doing now."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    cue = await console.async_rerecord_cue(msg["cue_id"])
    if cue is None:
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such cue.")
        return
    connection.send_result(msg["id"], {"cue": cue.to_dict(), **console.show_summary()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_CUE_ADD_EFFECT,
        vol.Required("effect"): str,
        vol.Optional("params"): dict,
        vol.Optional("name"): str,
        vol.Optional("at"): int,
    }
)
@websocket_api.async_response
async def websocket_cue_add_effect(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Save an effect into the cue list.

    Paired with `effects/preview`: the operator runs the effect live, adjusts
    it until it looks right, and then saves exactly those parameters as a cue.
    """
    if (console := _require_console(hass, connection, msg)) is None:
        return
    show = console.shows.active_show
    if show is None:
        connection.send_error(
            msg["id"], ERR_NO_SHOW, "Create a show before adding a cue."
        )
        return
    name = msg["effect"]
    if name not in EFFECTS:
        connection.send_error(msg["id"], ERR_UNKNOWN_EFFECT, f"No effect {name!r}.")
        return

    params = EFFECTS[name].defaults() | dict(msg.get("params") or {})
    cue = Cue(
        id=random_uuid_hex(),
        label="",
        kind=CueKind.EFFECT,
        name=msg.get("name") or EFFECTS[name].label,
        effect=name,
        effect_params=params,
    )
    await console.shows.async_add_cue(show.id, cue, at=msg.get("at"))
    connection.send_result(msg["id"], {"cue": cue.to_dict(), **console.show_summary()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_CUE_UPDATE,
        vol.Required("cue_id"): str,
        vol.Required("changes"): dict,
    }
)
@websocket_api.async_response
async def websocket_cue_update(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Edit a cue: its label, name, fade, notes, effect parameters or levels."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    show = console.shows.active_show
    if show is None:
        connection.send_error(msg["id"], ERR_NO_SHOW, "No active show.")
        return
    cue = await console.shows.async_update_cue(show.id, msg["cue_id"], msg["changes"])
    if cue is None:
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such cue.")
        return
    connection.send_result(msg["id"], {"cue": cue.to_dict(), **console.show_summary()})


@websocket_api.websocket_command(
    {vol.Required("type"): WS_TYPE_CUE_DUPLICATE, vol.Required("cue_id"): str}
)
@websocket_api.async_response
async def websocket_cue_duplicate(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    show = console.shows.active_show
    if show is None:
        connection.send_error(msg["id"], ERR_NO_SHOW, "No active show.")
        return
    cue = await console.shows.async_duplicate_cue(show.id, msg["cue_id"])
    if cue is None:
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such cue.")
        return
    connection.send_result(msg["id"], {"cue": cue.to_dict(), **console.show_summary()})


@websocket_api.websocket_command(
    {vol.Required("type"): WS_TYPE_CUE_DELETE, vol.Required("cue_id"): str}
)
@websocket_api.async_response
async def websocket_cue_delete(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    show = console.shows.active_show
    if show is None:
        connection.send_error(msg["id"], ERR_NO_SHOW, "No active show.")
        return
    if not await console.shows.async_delete_cue(show.id, msg["cue_id"]):
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such cue.")
        return
    connection.send_result(msg["id"], console.show_summary())


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_CUE_REORDER,
        vol.Required("cue_ids"): [str],
    }
)
@websocket_api.async_response
async def websocket_cue_reorder(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Reorder the cue list. Rejects anything that is not a permutation."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    show = console.shows.active_show
    if show is None:
        connection.send_error(msg["id"], ERR_NO_SHOW, "No active show.")
        return
    if not await console.shows.async_reorder_cues(show.id, msg["cue_ids"]):
        connection.send_error(
            msg["id"],
            ERR_INVALID_REORDER,
            "The new order must contain exactly the cues already in the show.",
        )
        return
    connection.send_result(msg["id"], console.show_summary())


# ----------------------------------------------------------------------
# Playback
# ----------------------------------------------------------------------


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_PLAYBACK_GO})
@websocket_api.async_response
async def websocket_playback_go(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """GO. Fires the next cue, or the first if nothing is on stage yet."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    cue = await console.playback.async_go(
        console.shows.active_show, console.rig.entity_ids
    )
    connection.send_result(
        msg["id"], {"fired": cue.to_dict() if cue else None, **console.show_summary()}
    )


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_PLAYBACK_BACK})
@websocket_api.async_response
async def websocket_playback_back(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    cue = await console.playback.async_back(
        console.shows.active_show, console.rig.entity_ids
    )
    connection.send_result(
        msg["id"], {"fired": cue.to_dict() if cue else None, **console.show_summary()}
    )


@websocket_api.websocket_command(
    {vol.Required("type"): WS_TYPE_PLAYBACK_GOTO, vol.Required("cue_id"): str}
)
@websocket_api.async_response
async def websocket_playback_goto(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    cue = await console.playback.async_goto(
        console.shows.active_show, msg["cue_id"], console.rig.entity_ids
    )
    if cue is None:
        connection.send_error(msg["id"], ERR_NOT_FOUND, "No such cue.")
        return
    connection.send_result(
        msg["id"], {"fired": cue.to_dict(), **console.show_summary()}
    )


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_PLAYBACK_RELEASE})
@websocket_api.async_response
async def websocket_playback_release(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Stop everything and hand the rig back. Must work when nothing else does."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    await console.playback.async_release(console.rig.entity_ids)
    connection.send_result(msg["id"], console.show_summary())


# ----------------------------------------------------------------------
# Effects
# ----------------------------------------------------------------------


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_EFFECTS_LIST})
@callback
def websocket_effects_list(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Every effect and its parameters, so the card can draw the form itself."""
    connection.send_result(msg["id"], {"effects": describe_effects()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_EFFECTS_PREVIEW,
        vol.Required("effect"): str,
        vol.Optional("params"): dict,
    }
)
@websocket_api.async_response
async def websocket_effects_preview(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Run an effect live without saving it.

    This is how an effect gets designed: run it, watch the stage, change a
    number, run it again. Only when it looks right does it become a cue.
    """
    if (console := _require_console(hass, connection, msg)) is None:
        return
    name = msg["effect"]
    if name not in EFFECTS:
        connection.send_error(msg["id"], ERR_UNKNOWN_EFFECT, f"No effect {name!r}.")
        return
    params = EFFECTS[name].defaults() | dict(msg.get("params") or {})
    started = await console.effects.async_start(
        name, params, resolve_targets(params, console.rig.entity_ids)
    )
    connection.send_result(
        msg["id"], {"started": started, "effect": console.effects.status()}
    )


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_EFFECTS_STOP})
@websocket_api.async_response
async def websocket_effects_stop(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    if (console := _require_console(hass, connection, msg)) is None:
        return
    await console.effects.async_stop()
    connection.send_result(msg["id"], {"effect": console.effects.status()})


# ----------------------------------------------------------------------
# Import from the bridge
# ----------------------------------------------------------------------


@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_IMPORT_GROUPS})
@websocket_api.async_response
async def websocket_import_groups(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Hue rooms and zones that hold scenes, as candidates for import."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    if not console.is_bridge_configured:
        connection.send_error(msg["id"], ERR_NO_BRIDGE, "No Hue bridge is paired yet.")
        return
    connection.send_result(
        msg["id"], {"groups": await console.async_get_importable_groups()}
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_IMPORT_RUN,
        vol.Required("group_id"): str,
        vol.Optional("name"): str,
        vol.Optional("default_fade"): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def websocket_import_run(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Create a new show from a Hue room or zone's scenes."""
    if (console := _require_console(hass, connection, msg)) is None:
        return
    if not console.is_bridge_configured:
        connection.send_error(msg["id"], ERR_NO_BRIDGE, "No Hue bridge is paired yet.")
        return
    show_id, result = await console.async_import_show(
        msg["group_id"],
        msg.get("name", ""),
        default_fade=float(msg.get("default_fade", 0.0)),
    )
    if result is not None and show_id is None:
        connection.send_error(
            msg["id"],
            ERR_NOTHING_TO_IMPORT,
            "Every scene in that room or zone is empty on the bridge, so "
            "there is nothing to import. Hue clears a room's scenes when its "
            "lights are moved to another room.",
        )
        return
    if show_id is None or result is None:
        connection.send_error(
            msg["id"],
            ERR_NOT_FOUND,
            "That room or zone could not be read from the bridge.",
        )
        return
    console.playback.reset()
    connection.send_result(
        msg["id"], {"imported": result.to_dict(), **console.show_summary()}
    )
