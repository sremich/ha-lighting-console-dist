"""Config flow for the Lighting Console.

The initial step is deliberately empty: the console is configured from its own
card — the rig, the shows, the cues — not from a wall of config-flow forms.

Bridge pairing is the exception, and lives here rather than in the card for a
specific reason: it is the one operation that produces long-lived secrets (the
application key and the client key), and Home Assistant's config entries are
the right place for those. The card is never told their values.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_APP_KEY,
    CONF_BRIDGE_HOST,
    CONF_BRIDGE_ID,
    CONF_BRIDGE_NAME,
    CONF_CLIENT_KEY,
    CONF_MAX_FRAMES_IN_FLIGHT,
    DEFAULT_MAX_FRAMES_IN_FLIGHT,
    DOMAIN,
    HUE_APP_NAME,
    HUE_INTEGRATION_DOMAIN,
    MAX_FRAMES_IN_FLIGHT,
    MIN_FRAMES_IN_FLIGHT,
    NAME,
)
from .hue import (
    BridgeUnreachable,
    HueBridgeClient,
    HueError,
    LinkButtonNotPressed,
    NotABridge,
)

_LOGGER = logging.getLogger(__name__)


class LightingConsoleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the (single-instance) config flow, and bridge pairing."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> LightingConsoleOptionsFlow:
        return LightingConsoleOptionsFlow()

    def __init__(self) -> None:
        self._host: str | None = None
        self._bridge_id: str | None = None
        self._bridge_name: str | None = None

    # ------------------------------------------------------------------
    # Initial setup
    # ------------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the single console entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(title=NAME, data={})

    # ------------------------------------------------------------------
    # Bridge pairing (reconfigure)
    # ------------------------------------------------------------------

    def _suggested_host(self) -> str:
        """Pre-fill from Home Assistant's own Hue integration if it is set up.

        Most people running this already have the core Hue integration
        configured, and retyping a bridge address during a get-in is exactly
        the sort of friction worth removing. Falls back to empty.
        """
        for entry in self.hass.config_entries.async_entries(HUE_INTEGRATION_DOMAIN):
            if host := entry.data.get(CONF_HOST):
                return str(host)
        return ""

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the bridge address, then verify something is there."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            session = async_get_clientsession(self.hass, verify_ssl=False)
            client = HueBridgeClient(session, host)
            try:
                info = await client.async_get_bridge_info()
            except BridgeUnreachable:
                errors["base"] = "cannot_connect"
            except NotABridge:
                errors["base"] = "not_a_bridge"
            except HueError:
                _LOGGER.exception("Unexpected error reaching the bridge")
                errors["base"] = "unknown"
            else:
                self._host = host
                self._bridge_id = info.bridge_id
                self._bridge_name = info.name
                return await self.async_step_link()

        entry = self._get_reconfigure_entry()
        current_host = entry.data.get(CONF_BRIDGE_HOST) or self._suggested_host()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=current_host): str}
            ),
            errors=errors,
        )

    async def async_step_link(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Push-link pairing: the operator presses the button, we ask for keys."""
        errors: dict[str, str] = {}

        if user_input is not None:
            assert self._host is not None
            session = async_get_clientsession(self.hass, verify_ssl=False)
            client = HueBridgeClient(session, self._host)
            try:
                app_key, client_key = await client.async_pair(HUE_APP_NAME)
            except LinkButtonNotPressed:
                errors["base"] = "link_button_not_pressed"
            except BridgeUnreachable:
                errors["base"] = "cannot_connect"
            except HueError as err:
                _LOGGER.error("Pairing failed: %s", err)
                errors["base"] = "pairing_failed"
            else:
                entry = self._get_reconfigure_entry()
                return self.async_update_reload_and_abort(
                    entry,
                    data={
                        **entry.data,
                        CONF_BRIDGE_HOST: self._host,
                        CONF_BRIDGE_ID: self._bridge_id,
                        CONF_BRIDGE_NAME: self._bridge_name,
                        CONF_APP_KEY: app_key,
                        CONF_CLIENT_KEY: client_key,
                    },
                    reason="reconfigure_successful",
                )

        return self.async_show_form(
            step_id="link",
            errors=errors,
            description_placeholders={"bridge": self._bridge_name or self._host or ""},
        )


class LightingConsoleOptionsFlow(OptionsFlow):
    """Runtime tuning, as opposed to pairing.

    Only one setting so far, and it is here rather than on the card because it
    describes how the console talks to the bridge rather than what the show
    looks like - the same reason bridge pairing lives in the config flow.
    """

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_MAX_FRAMES_IN_FLIGHT, DEFAULT_MAX_FRAMES_IN_FLIGHT
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MAX_FRAMES_IN_FLIGHT, default=current): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_FRAMES_IN_FLIGHT, max=MAX_FRAMES_IN_FLIGHT),
                    )
                }
            ),
        )
