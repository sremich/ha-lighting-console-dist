"""Hue bridge access: pairing and the CLIP v2 reads the console needs."""

from .client import HueBridgeClient
from .errors import (
    AuthenticationFailed,
    BridgeUnreachable,
    HueApiError,
    HueError,
    LinkButtonNotPressed,
    NotABridge,
    UnsupportedBridge,
)
from .models import (
    BridgeInfo,
    EntertainmentConfiguration,
    HueGroup,
    HueLight,
    HueScene,
    HueSceneAction,
)

__all__ = [
    "AuthenticationFailed",
    "BridgeInfo",
    "BridgeUnreachable",
    "EntertainmentConfiguration",
    "HueApiError",
    "HueBridgeClient",
    "HueError",
    "HueGroup",
    "HueLight",
    "HueScene",
    "HueSceneAction",
    "LinkButtonNotPressed",
    "NotABridge",
    "UnsupportedBridge",
]
