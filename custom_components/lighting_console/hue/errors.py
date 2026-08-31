"""Errors raised by the Hue bridge client.

These are deliberately specific: the config flow and the card both need to
tell the operator *which* thing went wrong, and "the bridge did not answer"
and "you did not press the button" need very different messages during a
get-in.
"""

from __future__ import annotations


class HueError(Exception):
    """Base class for every Hue bridge failure."""


class BridgeUnreachable(HueError):
    """The bridge did not answer at all — wrong address, or off the network."""


class NotABridge(HueError):
    """Something answered, but it is not a Hue bridge."""


class LinkButtonNotPressed(HueError):
    """Pairing was attempted before the physical link button was pressed."""


class AuthenticationFailed(HueError):
    """The stored application key is no longer accepted by the bridge."""


class UnsupportedBridge(HueError):
    """The bridge is too old to speak CLIP v2 or to stream."""


class HueApiError(HueError):
    """The bridge returned an error we did not specifically anticipate."""
