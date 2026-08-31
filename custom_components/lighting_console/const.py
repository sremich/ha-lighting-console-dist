"""Constants for the Lighting Console integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "lighting_console"

# Human-facing name, used by the config flow and the card.
NAME: Final = "Lighting Console"

# Build metadata. Both are rewritten by scripts/sync_version.py at build time
# from the VERSION file and the git SHA; the values committed here are the
# development placeholders. The version lives ONLY in VERSION — never edit
# BUILD_VERSION by hand.
BUILD_VERSION: Final = "0.3.1"
BUILD_GIT_SHA: Final = "962dbdd9e05d"

# Where the card is published so the frontend can always fetch it.
#
# Home Assistant's `frontend` component registers `/local` -> `config/www`
# during its own setup, which happens long before any config entry is set up.
# Our own static path is registered at entry setup, which is the whole
# problem: for several seconds after every restart the dashboard is served
# while our URL still 404s, and Lovelace only ever tries once per page load.
# Publishing a copy of the bundle under `config/www` puts it behind a route
# that is live from the moment the frontend answers at all.
LOCAL_URL_PREFIX: Final = "/local"
#: Fixed id so the notice is replaced, never stacked, across restarts.
RESTART_NOTIFICATION_ID: Final = f"{DOMAIN}_restart_to_finish"
WWW_SUBDIR: Final = DOMAIN
CARD_STEM: Final = "lighting-console-card"

# How many effect frames may be in flight against the bridge at once.
#
# Measured on the rig, because the trade is real and not obvious. One frame at
# a time gives the fastest possible stop - a single bridge round-trip - but
# gives up the request pipelining that keeps a bridge busy, and a strobe
# delivered less than half the changes it used to. More frames keep the bridge
# working, at the cost of a worst-case stop that many round-trips long. Two is
# the compromise: a stop still well under a second, and a strobe that still
# reads as a strobe. See EffectEngine._async_pump.
CONF_MAX_FRAMES_IN_FLIGHT: Final = "max_frames_in_flight"
DEFAULT_MAX_FRAMES_IN_FLIGHT: Final = 2
MIN_FRAMES_IN_FLIGHT: Final = 1
MAX_FRAMES_IN_FLIGHT: Final = 5

# The domain of Home Assistant's own Hue integration. Used to recognise a
# device as Hue-owned when mapping entities to bridge resources — never to
# call into it.
HUE_INTEGRATION_DOMAIN: Final = "hue"

# Persistent storage. Bump STORAGE_VERSION only alongside a migration; the
# rig is small but losing it mid-get-in would be infuriating.
STORAGE_VERSION: Final = 1
STORAGE_KEY_RIG: Final = "rig"

# Shows and their cue lists. Separate from the rig because they have utterly
# different lifetimes: the rig changes hourly during a get-in and is worth
# little once struck, while a cue list is the artefact of a whole production
# and must survive everything.
STORAGE_KEY_SHOWS: Final = "shows"

# Config-entry keys for bridge credentials. These are written to Home
# Assistant's own storage and must never be logged, exported, or sent to the
# card — the card is told whether a bridge is paired, never with what.
CONF_BRIDGE_HOST: Final = "bridge_host"
CONF_BRIDGE_ID: Final = "bridge_id"
CONF_BRIDGE_NAME: Final = "bridge_name"
CONF_APP_KEY: Final = "app_key"
CONF_CLIENT_KEY: Final = "client_key"

# Identifies this application to the bridge in the pairing request, and is
# what appears in the Hue app's list of connected apps.
HUE_APP_NAME: Final = "lighting_console#homeassistant"

# Frontend card asset. The integration serves this from its own directory so
# that a HACS install of the integration also installs the card — the two are
# versioned and shipped as one unit.
CARD_FILENAME: Final = "lighting-console-card.js"
CARD_URL_PATH: Final = f"/{DOMAIN}/{CARD_FILENAME}"
