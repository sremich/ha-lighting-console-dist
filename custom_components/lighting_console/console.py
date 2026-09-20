"""The console's runtime state: the rig, and what we know about the bridge.

One instance per config entry, held in `hass.data`. Everything the card asks
for is answered from here, so there is a single place where "what does the
console currently believe about the rig" is decided.

A deliberate property: **the console works with no bridge paired.** A rig of
smart plugs and third-party bulbs is a perfectly valid rig; it simply cannot
run effects. Bridge failures degrade this object, they never break it.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util.uuid import random_uuid_hex

from .const import (
    CONF_APP_KEY,
    CONF_BRIDGE_HOST,
    CONF_BRIDGE_ID,
    CONF_BRIDGE_NAME,
    CONF_CLIENT_KEY,
    CONF_MAX_FRAMES_IN_FLIGHT,
    DEFAULT_MAX_FRAMES_IN_FLIGHT,
)
from .cues import Cue, CueKind, LightLevel, ShowStore
from .effects import EffectEngine
from .hue import (
    EntertainmentConfiguration,
    HueBridgeClient,
    HueError,
    HueGroup,
    HueLight,
    HueScene,
)
from .importer import ImportResult, build_light_map, cues_from_scenes
from .playback import Playback, capture
from .rig import (
    Capability,
    RigMember,
    RigStore,
    classify,
    hue_light_id_for_entity,
    is_group_light,
)
from .scenes import SCENE_PREFIX, look_key, scene_actions

_LOGGER = logging.getLogger(__name__)

#: The one zone the console owns on the bridge. It holds exactly the rig's
#: Hue lights, and every compiled look is a scene in it.
ZONE_NAME = "Lighting Console"


class Console:
    """Runtime state for one Lighting Console config entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._hass = hass
        self._entry = entry
        self.rig = RigStore(hass)
        self.shows = ShowStore(hass)
        self.effects = EffectEngine(
            hass,
            entry.options.get(CONF_MAX_FRAMES_IN_FLIGHT, DEFAULT_MAX_FRAMES_IN_FLIGHT),
        )
        self.playback = Playback(hass, self.effects)
        self.playback.scene_recall = self.async_recall_scene

        self._client: HueBridgeClient | None = None
        self._hue_lights: dict[str, HueLight] = {}
        self._entertainment: list[EntertainmentConfiguration] = []
        self._bridge_error: str | None = None
        self._bridge_loaded = False
        self._zone_id: str | None = None
        self._scene_error: str | None = None
        self._scene_count = 0
        self._compile_lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def async_setup(self) -> None:
        await self.rig.async_load()
        await self.shows.async_load()

        if self.is_bridge_configured:
            session = async_get_clientsession(self._hass, verify_ssl=False)
            self._client = HueBridgeClient(
                session,
                self._entry.data[CONF_BRIDGE_HOST],
                self._entry.data[CONF_APP_KEY],
            )
            # Not fatal if this fails — the console must still come up.
            await self.async_refresh_bridge()

    @property
    def is_bridge_configured(self) -> bool:
        return bool(
            self._entry.data.get(CONF_BRIDGE_HOST)
            and self._entry.data.get(CONF_APP_KEY)
        )

    @property
    def has_client_key(self) -> bool:
        """Whether we hold the pre-shared key the Entertainment stream needs.

        An application key without a client key is the failure mode that stays
        invisible until the first attempt to run an effect, so it is surfaced
        separately rather than folded into "paired".
        """
        return bool(self._entry.data.get(CONF_CLIENT_KEY))

    # ------------------------------------------------------------------
    # Bridge
    # ------------------------------------------------------------------

    async def async_refresh_bridge(self) -> bool:
        """Re-read lights and entertainment areas. Never raises."""
        if self._client is None:
            return False

        try:
            lights = await self._client.async_get_lights()
            entertainment = await self._client.async_get_entertainment_configurations()
        except HueError as err:
            self._bridge_error = str(err)
            _LOGGER.warning("Could not read from the Hue bridge: %s", err)
            return False
        except Exception:
            self._bridge_error = "Unexpected error talking to the bridge; see the log."
            _LOGGER.exception("Unexpected error reading from the Hue bridge")
            return False

        self._hue_lights = {light.id: light for light in lights}
        self._entertainment = entertainment
        self._bridge_error = None
        self._bridge_loaded = True
        _LOGGER.debug(
            "Read %d lights and %d entertainment areas from the bridge",
            len(lights),
            len(entertainment),
        )
        await self.async_sync_zone()
        self.schedule_compile()
        return True

    def hue_light_ids(self) -> dict[str, str]:
        """Rig entity id -> Hue light id, for the members that are Hue lights."""
        out: dict[str, str] = {}
        for entity_id in self.rig.entity_ids:
            light_id = hue_light_id_for_entity(self._hass, entity_id, self._hue_lights)
            if light_id is not None:
                out[entity_id] = light_id
        return out

    async def async_sync_zone(self) -> None:
        """Make the console's zone hold exactly the rig's Hue lights. Never raises.

        Created on first contact, membership rewritten whenever it differs.
        A zone with no lights is legal — it is how a bridge with nothing
        paired still gets the scene machinery tested.
        """
        if self._client is None or not self._bridge_loaded:
            return
        wanted = list(self.hue_light_ids().values())
        try:
            zone = next(
                (
                    group
                    for group in await self._client.async_get_groups()
                    if group.type == "zone" and group.name == ZONE_NAME
                ),
                None,
            )
            if zone is None:
                self._zone_id = await self._client.async_create_zone(ZONE_NAME, wanted)
            else:
                self._zone_id = zone.id
                if sorted(zone.light_ids) != sorted(wanted):
                    await self._client.async_set_zone_lights(zone.id, wanted)
        except Exception as err:  # bridge trouble degrades, never breaks
            self._scene_error = f"Could not update the console's zone: {err}"
            _LOGGER.warning(self._scene_error)
            return
        self._scene_error = None

    def bridge_status(self) -> dict[str, Any]:
        """What the card shows about the bridge. Never includes a credential."""
        return {
            "configured": self.is_bridge_configured,
            "bridge_id": self._entry.data.get(CONF_BRIDGE_ID),
            "name": self._entry.data.get(CONF_BRIDGE_NAME),
            # Deliberately not the keys themselves — only whether we hold one.
            "has_client_key": self.has_client_key,
            "reachable": self._bridge_loaded and self._bridge_error is None,
            "error": self._bridge_error,
            "light_count": len(self._hue_lights),
            # The compiled looks: how many scenes the console holds on the
            # bridge, and why the last compile or zone update failed, if it
            # did. The card paints the error in its status corner.
            "scene_count": self._scene_count,
            "scene_error": self._scene_error,
            "entertainment_areas": [
                {
                    "id": configuration.id,
                    "name": configuration.name,
                    "streaming": configuration.is_streaming,
                    "light_count": len(configuration.light_ids),
                    "channel_count": len(configuration.channel_light_ids),
                }
                for configuration in self._entertainment
            ],
        }

    # ------------------------------------------------------------------
    # Looks as bridge scenes
    # ------------------------------------------------------------------

    def schedule_compile(self) -> None:
        """Compile in the background: a whole show is one create per look,
        and nobody should wait on that to see a cue list."""
        if self._client is not None:
            self._hass.async_create_task(self.async_compile_active_show())

    async def async_compile_active_show(self) -> None:
        """Every look of the active show becomes a scene in the zone.

        Identical looks share one scene: the look's key is kept in the
        scene's `appdata`, so the scene list *is* the index and a restart
        cannot lose it. A look that has no Hue lights compiles to nothing
        and keeps going through Home Assistant. Never raises; the first
        error stops the pass and is shown in the bridge status.

        ponytail: one scene create per look, ~100 ms each, so a fresh
        106-cue show takes ~10 s to compile. Fine in the background; batch
        creates if the bridge ever grows a bulk endpoint.
        """
        if self._client is None or self._zone_id is None:
            return
        async with self._compile_lock:
            show = self.shows.active_show
            light_ids = self.hue_light_ids()
            changed = False
            try:
                scenes = await self._client.async_get_scenes()
                mine = {
                    scene.appdata: scene.id
                    for scene in scenes
                    if scene.group_id == self._zone_id
                    and scene.name.startswith(SCENE_PREFIX)
                }
                for cue in show.cues if show else []:
                    actions = (
                        scene_actions(cue.levels, light_ids)
                        if cue.kind is CueKind.LOOK
                        else []
                    )
                    scene_id = None
                    if actions:
                        key = look_key(actions)
                        scene_id = mine.get(key)
                        if scene_id is None:
                            assert show is not None
                            scene_id = await self._client.async_create_scene(
                                f"{SCENE_PREFIX}{show.name} {cue.label}",
                                self._zone_id,
                                actions,
                                key,
                            )
                            mine[key] = scene_id
                    if cue.bridge_scene_id != scene_id:
                        cue.bridge_scene_id = scene_id
                        changed = True
                # Whatever nothing in the active show references any more —
                # a deleted cue, a re-recorded look, the previous show — goes.
                wanted = {cue.bridge_scene_id for cue in show.cues} if show else set()
                for key, scene_id in list(mine.items()):
                    if scene_id not in wanted:
                        await self._client.async_delete_scene(scene_id)
                        del mine[key]
                self._scene_count = len(mine)
                self._scene_error = None
            except Exception as err:  # bridge trouble degrades, never breaks
                self._scene_error = f"Could not compile looks to the bridge: {err}"
                _LOGGER.warning(self._scene_error)
            if changed:
                await self.shows.async_save()

    async def async_purge_scenes(self) -> int:
        """Delete every scene the console ever made, anywhere on the bridge.

        The recovery tool for a bridge full of stale `LC` scenes. Cues forget
        their scene ids and the active show is compiled afresh.
        """
        if self._client is None:
            return 0
        async with self._compile_lock:
            removed = 0
            for scene in await self._client.async_get_scenes():
                if scene.name.startswith(SCENE_PREFIX):
                    await self._client.async_delete_scene(scene.id)
                    removed += 1
            for show in self.shows.shows:
                for cue in show.cues:
                    cue.bridge_scene_id = None
            await self.shows.async_save()
            self._scene_count = 0
        self.schedule_compile()
        return removed

    async def async_recall_scene(self, cue: Cue, fade: float) -> list[LightLevel]:
        """Recall the cue's scene; return the levels it did not cover."""
        if self._client is None or not cue.bridge_scene_id:
            raise RuntimeError("no bridge")
        await self._client.async_recall_scene(cue.bridge_scene_id, int(fade * 1000))
        covered = self.hue_light_ids()
        return [level for level in cue.levels if level.entity_id not in covered]

    # ------------------------------------------------------------------
    # Rig
    # ------------------------------------------------------------------

    def rig_members(self) -> list[RigMember]:
        """Classify every rig entity as the card should show it."""
        return [
            classify(self._hass, entity_id, self._hue_lights, self._entertainment)
            for entity_id in self.rig.entity_ids
        ]

    def rig_summary(self) -> dict[str, Any]:
        members = self.rig_members()
        counts: dict[str, int] = {capability: 0 for capability in Capability}
        for member in members:
            counts[member.capability] += 1
        return {
            "members": [member.to_dict() for member in members],
            "counts": counts,
            "total": len(members),
        }

    def candidate_entities(self) -> list[dict[str, Any]]:
        """Entities that could be added to the rig, excluding current members.

        Restricted to the domains a lighting rig is actually built from. A
        console that offers every entity in the house makes adding a practical
        mid-rehearsal slower, not faster.
        """
        current = set(self.rig.entity_ids)
        candidates = []
        for state in self._hass.states.async_all(["light", "switch"]):
            if state.entity_id in current or is_group_light(
                self._hass, state.entity_id
            ):
                continue
            candidates.append(
                {
                    "entity_id": state.entity_id,
                    "name": state.attributes.get("friendly_name") or state.entity_id,
                    "domain": state.domain,
                }
            )
        return sorted(candidates, key=lambda item: item["name"].lower())

    # ------------------------------------------------------------------
    # Shows and playback
    # ------------------------------------------------------------------

    async def async_unload(self) -> None:
        """Tear down cleanly.

        The one thing that genuinely must happen here is stopping any running
        effect. An effect is a loop calling light services; if the config
        entry goes away while it runs, nothing is left to stop it and the rig
        keeps chasing after the console has gone.
        """
        await self.effects.async_stop()

    def show_summary(self) -> dict[str, Any]:
        """Every show, plus the active one's cues and where the playhead is.

        Sent whole rather than paginated. The largest real cue list on
        Stevie's instance is 127 cues of six fixtures each, which is a few
        tens of kilobytes — far cheaper than making the card manage paging
        during a show.
        """
        active = self.shows.active_show
        return {
            "shows": [
                {
                    "id": show.id,
                    "name": show.name,
                    "cue_prefix": show.cue_prefix,
                    "cue_count": len(show.cues),
                    "created": show.created,
                    "modified": show.modified,
                }
                for show in self.shows.shows
            ],
            "active_show_id": self.shows.active_show_id,
            "active_show": active.to_dict() if active else None,
            "playback": self.playback.status(active),
        }

    async def async_record_cue(
        self, name: str = "", at: int | None = None, fade: float = 0.0
    ) -> Cue | None:
        """Capture the live rig into a new cue on the active show."""
        show = self.shows.active_show
        if show is None:
            return None
        cue = Cue(
            id=random_uuid_hex(),
            label="",
            name=name,
            fade=fade,
            levels=capture(self._hass, self.rig.entity_ids),
        )
        return await self.shows.async_add_cue(show.id, cue, at=at)

    async def async_rerecord_cue(self, cue_id: str) -> Cue | None:
        """Replace one cue's look with what the lights are doing now.

        The cue keeps its id, label, name, notes and fade — only the levels
        change. That is what "update this cue" means to an operator who has
        just nudged a fixture during tech.
        """
        show = self.shows.active_show
        if show is None:
            return None
        levels = capture(self._hass, self.rig.entity_ids)
        return await self.shows.async_update_cue(
            show.id, cue_id, {"levels": [level.to_dict() for level in levels]}
        )

    # ------------------------------------------------------------------
    # Import from the bridge
    # ------------------------------------------------------------------

    async def async_get_importable_groups(self) -> list[dict[str, Any]]:
        """Rooms and zones on the bridge, with how many scenes each holds."""
        if self._client is None:
            return []
        try:
            groups, scenes = await self._fetch_groups_and_scenes()
        except HueError as err:
            _LOGGER.warning("Could not read scenes from the bridge: %s", err)
            return []

        counts: dict[str, int] = {}
        usable: dict[str, int] = {}
        for scene in scenes:
            counts[scene.group_id] = counts.get(scene.group_id, 0) + 1
            if scene.actions:
                usable[scene.group_id] = usable.get(scene.group_id, 0) + 1

        listing = []
        for group in groups:
            total = counts.get(group.id, 0)
            if not total:
                continue
            live = usable.get(group.id, 0)
            # A group whose scenes hold no actions produces cues that control
            # nothing. It is offered, but flagged and refused, rather than
            # hidden — "where has HADESTOWN gone?" is a worse question for an
            # operator than a plain explanation of why it cannot be used.
            if live == 0:
                reason = (
                    "These scenes are empty on the bridge, so there is nothing "
                    "to import. Hue clears a room's scenes when its lights are "
                    "moved to another room."
                )
            elif live < total:
                reason = (
                    f"{total - live} of these scenes are empty and will be skipped."
                )
            else:
                reason = ""
            listing.append(
                {
                    "id": group.id,
                    "name": group.name,
                    "type": group.type,
                    "light_count": len(group.light_ids),
                    "scene_count": total,
                    "usable_scene_count": live,
                    "importable": live > 0,
                    "reason": reason,
                }
            )
        return listing

    async def _fetch_groups_and_scenes(
        self,
    ) -> tuple[list[HueGroup], list[HueScene]]:
        assert self._client is not None
        groups = await self._client.async_get_groups()
        scenes = await self._client.async_get_scenes()
        return groups, scenes

    async def async_import_show(
        self, group_id: str, name: str, default_fade: float = 0.0
    ) -> tuple[str | None, ImportResult | None]:
        """Create a new show from one Hue room or zone's scenes.

        Returns `(show_id, result)`. `(None, None)` means the group is gone or
        the bridge could not be read; `(None, result)` means the group exists
        but held nothing importable. The new show is made active, so the
        operator lands straight on the imported cue list.
        """
        if self._client is None:
            return None, None
        try:
            groups, scenes = await self._fetch_groups_and_scenes()
        except HueError as err:
            _LOGGER.warning("Could not read scenes from the bridge: %s", err)
            return None, None

        group = next((g for g in groups if g.id == group_id), None)
        if group is None:
            return None, None

        light_map = build_light_map(self._hass, self._hue_lights)
        result = cues_from_scenes(group, scenes, light_map, default_fade=default_fade)

        # Nothing usable came across. Report it instead of leaving an empty
        # show behind for someone to find later and wonder about.
        if not result.cues:
            return None, result

        show = await self.shows.async_create_show(name or group.name)
        await self.shows.async_add_cues(show.id, result.cues)
        return show.id, result
