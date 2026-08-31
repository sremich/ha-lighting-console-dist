"""A small Hue bridge client: pairing and the CLIP v2 reads the console needs.

Deliberately not `aiohue`. The core Home Assistant Hue integration pins
`aiohue==4.9.0` exactly; a second exact pin in this integration would either
conflict with it or couple our releases to core's. The surface we actually
need is small — pair, read lights, read entertainment configurations — so we
own it and keep `"requirements": []`.

Two API generations are unavoidable here:

* **Pairing** is the legacy `POST /api` endpoint. There is no CLIP v2
  equivalent; it is also the only way to obtain the *client key*, which is
  the pre-shared key the Entertainment stream authenticates with.
* **Everything else** is CLIP v2 under `/clip/v2/resource/...`, authenticated
  with the `hue-application-key` header.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .errors import (
    AuthenticationFailed,
    BridgeUnreachable,
    HueApiError,
    LinkButtonNotPressed,
    NotABridge,
)
from .models import (
    BridgeInfo,
    EntertainmentConfiguration,
    HueGroup,
    HueLight,
    HueScene,
)

_LOGGER = logging.getLogger(__name__)

# The bridge presents a self-signed certificate issued to its bridge id, so
# ordinary verification cannot succeed. Callers pass a session created with
# verify_ssl=False; see DECISIONS.md for why that is acceptable here and what
# it does not excuse.
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10)

# Hue error codes we can act on. 101 is the one operators will actually meet.
ERR_LINK_BUTTON_NOT_PRESSED = 101
ERR_UNAUTHORISED = 1


class HueBridgeClient:
    """Talks to one bridge. Stateless apart from the credentials it holds."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        app_key: str | None = None,
        scheme: str = "https",
    ) -> None:
        self._session = session
        self._host = host
        self._app_key = app_key
        # A real bridge is always https. `scheme` exists so tier-1 tests can
        # point the client at a plain-HTTP fake bridge and exercise the actual
        # request and error handling, rather than a mocked-out session.
        self._scheme = scheme

    @property
    def host(self) -> str:
        return self._host

    @property
    def app_key(self) -> str | None:
        return self._app_key

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self._scheme}://{self._host}{path}"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> Any:
        headers: dict[str, str] = {}
        if authenticated:
            if not self._app_key:
                raise AuthenticationFailed(
                    "No application key: pair with the bridge first."
                )
            headers["hue-application-key"] = self._app_key

        try:
            async with self._session.request(
                method,
                self._url(path),
                json=json_body,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
                ssl=False,
            ) as response:
                if response.status == 403:
                    raise AuthenticationFailed(
                        "The bridge rejected the application key. Pair again."
                    )
                if response.status >= 500:
                    raise HueApiError(
                        f"The bridge returned HTTP {response.status} for {path}"
                    )
                try:
                    return await response.json(content_type=None)
                except ValueError as exc:
                    raise NotABridge(
                        f"{self._host} answered {path} with something that is "
                        "not JSON — is that address really a Hue bridge?"
                    ) from exc
        except TimeoutError as exc:
            raise BridgeUnreachable(
                f"The bridge at {self._host} did not answer within "
                f"{DEFAULT_TIMEOUT.total:.0f}s."
            ) from exc
        except aiohttp.ClientError as exc:
            raise BridgeUnreachable(
                f"Could not reach the bridge at {self._host}: {exc}"
            ) from exc

    @staticmethod
    def _unwrap_v2(payload: Any, resource: str) -> list[dict[str, Any]]:
        """Return the `data` array from a CLIP v2 response, or raise."""
        if not isinstance(payload, dict):
            raise HueApiError(f"Unexpected response reading {resource}: {payload!r}")
        if errors := payload.get("errors"):
            raise HueApiError(f"Bridge reported errors reading {resource}: {errors}")
        data = payload.get("data")
        if data is None:
            raise HueApiError(f"No data in the bridge response for {resource}")
        return list(data)

    # ------------------------------------------------------------------
    # Identity and pairing
    # ------------------------------------------------------------------

    async def async_get_bridge_info(self) -> BridgeInfo:
        """Read the bridge's identity. Needs no credentials."""
        payload = await self._request("GET", "/api/config", authenticated=False)
        if not isinstance(payload, dict) or "bridgeid" not in payload:
            raise NotABridge(
                f"{self._host} answered, but did not identify itself as a Hue bridge."
            )
        return BridgeInfo.from_config(payload)

    async def async_pair(self, app_name: str) -> tuple[str, str]:
        """Perform push-link pairing. Returns (application key, client key).

        The bridge's link button must have been pressed within the last ~30
        seconds. The client key is requested explicitly — without
        `generateclientkey` the bridge returns only the application key, and
        the Entertainment stream cannot be authenticated at all.
        """
        payload = await self._request(
            "POST",
            "/api",
            json_body={"devicetype": app_name, "generateclientkey": True},
            authenticated=False,
        )

        if not isinstance(payload, list) or not payload:
            raise HueApiError(f"Unexpected pairing response: {payload!r}")

        entry = payload[0]
        if error := entry.get("error"):
            if error.get("type") == ERR_LINK_BUTTON_NOT_PRESSED:
                raise LinkButtonNotPressed(
                    "Press the round button on top of the bridge, then try again "
                    "within 30 seconds."
                )
            raise HueApiError(f"The bridge refused to pair: {error}")

        success = entry.get("success") or {}
        app_key = success.get("username")
        client_key = success.get("clientkey")

        if not app_key:
            raise HueApiError(f"Pairing succeeded but returned no key: {entry!r}")
        if not client_key:
            # Worth failing loudly: everything looks fine until the first
            # attempt to stream, weeks later, in a rehearsal.
            raise HueApiError(
                "The bridge issued an application key but no client key, so "
                "effects could never stream. The bridge firmware may be too "
                "old for the Entertainment API."
            )

        self._app_key = app_key
        return app_key, client_key

    # ------------------------------------------------------------------
    # CLIP v2 reads
    # ------------------------------------------------------------------

    async def async_get_lights(self) -> list[HueLight]:
        payload = await self._request("GET", "/clip/v2/resource/light")
        return [
            HueLight.from_resource(item) for item in self._unwrap_v2(payload, "lights")
        ]

    async def async_get_entertainment_configurations(
        self,
    ) -> list[EntertainmentConfiguration]:
        """Read the entertainment areas, resolving channels down to lights.

        The bridge models this as a chain: an area has channels, each channel
        has members pointing at `entertainment` services, and each of those is
        owned by a device that also owns a light. Callers want lights, so the
        chain is walked here rather than in every caller.
        """
        configs_payload, entertainment_payload, lights = await asyncio.gather(
            self._request("GET", "/clip/v2/resource/entertainment_configuration"),
            self._request("GET", "/clip/v2/resource/entertainment"),
            self.async_get_lights(),
        )

        # entertainment service id -> owning device id
        service_owner: dict[str, str] = {}
        for item in self._unwrap_v2(entertainment_payload, "entertainment services"):
            owner = item.get("owner") or {}
            if owner.get("rid"):
                service_owner[item["id"]] = owner["rid"]

        # device id -> light ids it owns
        device_lights: dict[str, list[str]] = {}
        for light in lights:
            if light.owner_id:
                device_lights.setdefault(light.owner_id, []).append(light.id)

        configurations: list[EntertainmentConfiguration] = []
        for item in self._unwrap_v2(configs_payload, "entertainment configurations"):
            channel_light_ids: dict[int, list[str]] = {}
            for channel in item.get("channels") or []:
                channel_id = channel.get("channel_id")
                if channel_id is None:
                    continue
                resolved: list[str] = []
                for member in channel.get("members") or []:
                    service = member.get("service") or {}
                    if service.get("rtype") != "entertainment":
                        continue
                    device_id = service_owner.get(service.get("rid", ""))
                    if device_id:
                        resolved.extend(device_lights.get(device_id, []))
                channel_light_ids[int(channel_id)] = resolved

            metadata = item.get("metadata") or {}
            configurations.append(
                EntertainmentConfiguration(
                    id=item["id"],
                    name=metadata.get("name", "") or item["id"],
                    status=item.get("status", "inactive"),
                    channel_light_ids=channel_light_ids,
                    raw=item,
                )
            )

        return configurations

    async def async_get_groups(self) -> list[HueGroup]:
        """Every room and zone, with the lights each contains.

        Rooms and zones are separate resources on the bridge but the same
        thing to an operator picking a show to import, so they are returned
        as one list. The two differ in what `children` points at — a zone
        lists lights directly, a room lists the *devices* that own them — so
        the room case is resolved through the light list.
        """
        rooms_payload, zones_payload, lights = await asyncio.gather(
            self._request("GET", "/clip/v2/resource/room"),
            self._request("GET", "/clip/v2/resource/zone"),
            self.async_get_lights(),
        )

        device_lights: dict[str, list[str]] = {}
        for light in lights:
            if light.owner_id:
                device_lights.setdefault(light.owner_id, []).append(light.id)
        known_lights = {light.id for light in lights}

        groups: list[HueGroup] = []
        for payload, group_type in ((rooms_payload, "room"), (zones_payload, "zone")):
            for item in self._unwrap_v2(payload, f"{group_type}s"):
                light_ids: list[str] = []
                for child in item.get("children") or []:
                    rid = child.get("rid")
                    if not rid:
                        continue
                    if child.get("rtype") == "light" and rid in known_lights:
                        light_ids.append(rid)
                    elif child.get("rtype") == "device":
                        light_ids.extend(device_lights.get(rid, []))
                metadata = item.get("metadata") or {}
                groups.append(
                    HueGroup(
                        id=item["id"],
                        name=metadata.get("name", "") or item["id"],
                        type=group_type,
                        light_ids=light_ids,
                        raw=item,
                    )
                )
        return groups

    async def async_get_scenes(self) -> list[HueScene]:
        """Every scene on the bridge, with its per-light actions."""
        payload = await self._request("GET", "/clip/v2/resource/scene")
        return [
            HueScene.from_resource(item) for item in self._unwrap_v2(payload, "scenes")
        ]
