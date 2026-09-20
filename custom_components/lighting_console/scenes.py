"""Compiling a look into a Hue scene.

A snap cue fired as six `light.turn_on` calls ripples lamp by lamp, because
the bridge serialises single-light commands at about ten a second. A scene
recall is one request and every lamp in it moves together — which is why the
old *Company* dashboard felt simultaneous: every LX was a bridge scene.

Only the pure parts live here: the actions a look becomes, and the key that
says two looks are the same look. The console owns the bridge round trips.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from homeassistant.util.color import color_hs_to_xy

from .cues import LightLevel

#: Every scene the console makes is named with this, so purge can find its
#: own and only its own among the Hue app's scenes.
SCENE_PREFIX = "LC "


def scene_actions(
    levels: list[LightLevel], light_ids: dict[str, str]
) -> list[dict[str, Any]]:
    """CLIP v2 scene actions for the rig's Hue lights in a look.

    `light_ids` maps rig entity id -> Hue light id; anything not in it (a
    switch, a non-Hue bulb) is not the scene's business and goes through
    Home Assistant as before. Sorted by light so the same look always
    serialises the same way, which is what `look_key` relies on.
    """
    actions: list[dict[str, Any]] = []
    for level in levels:
        rid = light_ids.get(level.entity_id)
        if rid is None:
            continue
        action: dict[str, Any] = {"on": {"on": level.state == "on"}}
        if level.state == "on":
            if level.brightness is not None:
                action["dimming"] = {
                    "brightness": round(max(1, min(255, level.brightness)) / 2.55, 1)
                }
            if level.xy_color is not None:
                x, y = level.xy_color
                action["color"] = {"xy": {"x": round(x, 4), "y": round(y, 4)}}
            elif level.hs_color is not None:
                x, y = color_hs_to_xy(*level.hs_color)
                action["color"] = {"xy": {"x": round(x, 4), "y": round(y, 4)}}
            elif level.color_temp_kelvin:
                mirek = round(1_000_000 / level.color_temp_kelvin)
                action["color_temperature"] = {"mirek": max(153, min(500, mirek))}
        actions.append({"target": {"rid": rid, "rtype": "light"}, "action": action})
    actions.sort(key=lambda item: item["target"]["rid"])
    return actions


def look_key(actions: list[dict[str, Any]]) -> str:
    """Sixteen characters that identify a look — the bridge's `appdata` slot.

    Two cues with identical levels get the same key and share one scene.
    """
    digest = hashlib.sha1(json.dumps(actions, sort_keys=True).encode())
    return digest.hexdigest()[:16]
