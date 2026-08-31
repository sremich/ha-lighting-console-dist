"""Serving and registration of the console card.

The card is not a separate HACS repository: it is built into this
integration's directory and served from it, so installing the integration
installs a card of exactly the matching version. This avoids the classic
failure mode where a card and its backend drift apart across updates.
"""

from __future__ import annotations

import hashlib
import logging
import shutil
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import (
    BUILD_VERSION,
    CARD_FILENAME,
    CARD_STEM,
    CARD_URL_PATH,
    LOCAL_URL_PREFIX,
    RESTART_NOTIFICATION_ID,
    WWW_SUBDIR,
)

_LOGGER = logging.getLogger(__name__)

# Set once per HA run — registering the same static path twice raises.
_REGISTERED_KEY = "lighting_console_frontend_registered"


def _async_restart_notice(hass: HomeAssistant, *, show: bool) -> None:
    """Ask the operator, in the interface, for the one restart that finishes it.

    A log line cannot do this job. Home Assistant surfaces no INFO from a
    custom integration in either the container log or `home-assistant.log` —
    checked on a running instance, where even this integration's own "starting
    up" line is absent — so anything an operator is expected to act on has to
    reach the interface. This is the one manual step in the install, and it is
    the difference between a card that works and a card that shows
    "Configuration error" after every restart, so it must not be missable.

    A fixed notification id means a restart replaces the notice rather than
    stacking another copy, and clears it once the card is served from /local.
    """
    try:
        from homeassistant.components import persistent_notification
    except ImportError:  # not present in the tier-1 harness
        return

    if not show:
        persistent_notification.async_dismiss(hass, RESTART_NOTIFICATION_ID)
        return

    persistent_notification.async_create(
        hass,
        (
            "The Lighting Console card is installed, but Home Assistant needs "
            "one more restart before it can be served reliably.\n\n"
            "Until you restart, the console may show **Configuration error** "
            "on a dashboard opened in the first few seconds after Home "
            "Assistant starts; reloading the page works around it.\n\n"
            "Go to **Settings → System → Restart**. You only have to do this "
            "once."
        ),
        title="Lighting Console: one more restart",
        notification_id=RESTART_NOTIFICATION_ID,
    )


def _local_is_served(hass: HomeAssistant) -> bool:
    """Whether `/local` is being served right now.

    `frontend` only registers it when `config/www` already exists at its own
    setup — so on the very first install, after we have just created that
    directory, it is not served yet and will not be until the next restart.
    Asking the router is exact; guessing from the directory's existence is
    not, because we may be the ones who just created it.
    """
    try:
        for resource in hass.http.app.router.resources():
            canonical = getattr(resource, "canonical", None)
            if canonical and str(canonical).rstrip("/") == LOCAL_URL_PREFIX:
                return True
    except Exception:  # router internals are not a public API
        _LOGGER.debug("Could not inspect the HTTP router for /local", exc_info=True)
    return False


def _publish_to_www(www_root: Path, bundle: Path, digest: str) -> str | None:
    """Copy the bundle under `config/www`, content-addressed. Returns its name.

    Blocking: call from the executor. Returns None if it could not be written,
    which is not fatal — the integration's own static path still serves the
    card, just with the startup window this exists to close.
    """
    target_dir = www_root / WWW_SUBDIR
    name = f"{CARD_STEM}-{digest}.js"
    target = target_dir / name
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or target.stat().st_size != bundle.stat().st_size:
            # Write beside, then replace, so a dashboard loading at this exact
            # moment can never read a half-copied bundle.
            staging = target.with_suffix(".js.part")
            shutil.copyfile(bundle, staging)
            staging.replace(target)
        # One build's copy is all that is ever wanted. Old ones are dead
        # weight, and a stale one left behind is a card that could be served
        # to somebody by an equally stale Lovelace resource.
        for old in target_dir.glob(f"{CARD_STEM}-*.js"):
            if old.name != name:
                old.unlink(missing_ok=True)
    except OSError:
        _LOGGER.warning(
            "Could not publish the console card into %s; falling back to "
            "serving it from the integration directory, which leaves a short "
            "window after each restart in which a dashboard can fail to load "
            "it. See DECISIONS.md, 2026-08-29.",
            target_dir,
            exc_info=True,
        )
        return None
    return name


def _bundle_digest(path: Path) -> str:
    """Short content hash of the card bundle, used as the cache-buster.

    Content, not version: two builds of the same version are different cards
    during development, and the browser must be told so. Twelve hex characters
    is the same order as the git SHA it replaces in that URL.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


async def async_register_card(hass: HomeAssistant) -> bool:
    """Serve the card bundle and load it into the Lovelace frontend.

    Returns True if the card was registered, False if the bundle is missing
    (a source checkout that has not been built). A missing bundle is not
    fatal: the integration still loads, so that backend work and tests do
    not require a frontend build.
    """
    if hass.data.get(_REGISTERED_KEY):
        return True

    card_path = Path(__file__).parent / "www" / CARD_FILENAME
    if not await hass.async_add_executor_job(card_path.is_file):
        _LOGGER.warning(
            "Console card bundle not found at %s — the integration is loaded but "
            "the card will not be available. Run 'make build-card' (or install a "
            "release build rather than a source checkout).",
            card_path,
        )
        return False

    # Cacheable, because the URL below is content-addressed: one URL can only
    # ever mean one bundle, so a browser that keeps it for a month is right to.
    # This buys more than a saved fetch. Home Assistant serves dashboards for
    # several seconds before config entries finish setting up, and this static
    # path is registered here, at entry setup. Inside that window the card URL
    # 404s — measured on the rig 2026-08-28, t+29s and t+32s after a restart,
    # back at t+34s — and a 404 on a Lovelace resource module is fatal for that
    # page: the import fails, `customElements.whenDefined` never fires, and the
    # dashboard shows a Configuration error until someone reloads it by hand.
    # A browser that already holds the bundle never issues that request, so it
    # cannot lose that race. See DECISIONS.md, 2026-08-28.
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL_PATH, str(card_path), cache_headers=True)]
    )

    # Auto-loading the card into Lovelace needs the frontend component, which
    # is not a hard dependency: declaring it as one makes the integration
    # unloadable on any Home Assistant without the compiled frontend package
    # installed — including the tier-1 test harness. `after_dependencies` in
    # manifest.json orders us after it when it is present, and this guard
    # covers the case where it is not.
    # Cache-bust on the bundle's own content, so the URL changes exactly when
    # the file does. The git SHA cannot do this job: `sync_version.py` stamps
    # it only for release builds, so every development build and every source
    # checkout served the identical `?v=<version>.unknown` however many times
    # the card was rebuilt — which was harmless only for as long as the bundle
    # was uncacheable, and is what makes caching it safe now. The SAME string
    # is used for both registration routes below, so a browser that sees both
    # fetches and evaluates the module exactly once.
    digest = await hass.async_add_executor_job(_bundle_digest, card_path)
    module_url = f"{CARD_URL_PATH}?v={BUILD_VERSION}.{digest}"

    # Prefer `/local`, which is live before config entries are set up.
    #
    # Cache headers narrowed this problem but could not close it: they only
    # help a browser that already holds the bundle, and every genuinely new
    # device, cleared cache or changed version has to fetch it at least once.
    # Measured in HA 2026.8.3's frontend, that one fetch is all there is --
    # `ha-panel-lovelace` calls `loadLovelaceResources` without awaiting it,
    # behind a module-level `resourcesLoaded` flag, so a resource that 404s is
    # never requested again for the life of that page. `customElements.define`
    # is therefore never called, `whenDefined` never resolves, the `ll-rebuild`
    # that would have healed the card never fires, and the error stays put
    # until somebody reloads by hand. On the Android companion app, resuming
    # does not reload, so it survives every foreground for as long as the app
    # lives. Publishing under `config/www` removes the 404 rather than racing
    # it. See DECISIONS.md, 2026-08-29.
    published = await hass.async_add_executor_job(
        _publish_to_www, Path(hass.config.path("www")), card_path, digest
    )
    if published and _local_is_served(hass):
        module_url = f"{LOCAL_URL_PREFIX}/{WWW_SUBDIR}/{published}"
        # Whatever asked for a restart has now happened.
        _async_restart_notice(hass, show=False)
    elif published:
        _async_restart_notice(hass, show=True)
        _LOGGER.warning(
            "Published the console card to config/www/%s/%s, but /local is not "
            "served yet -- Home Assistant only registers it when config/www "
            "exists at startup. Serving from the integration directory for now; "
            "restart Home Assistant to close the startup window for good.",
            WWW_SUBDIR,
            published,
        )

    # Route 1: a Lovelace resource. This is the one that actually matters.
    # Lovelace fetches its resource list when it opens a dashboard, and the
    # list is persisted in `.storage`, so it answers correctly from the moment
    # Lovelace answers at all — unlike the index tag, which is written at
    # setup time. It does not make the card immune to a restart: the URL it
    # hands out still 404s until the static path above is registered, which is
    # why that path is now served with cache headers.
    await _async_register_lovelace_resource(hass, module_url)

    if "frontend" in hass.config.components:
        from homeassistant.components.frontend import add_extra_js_url

        # Route 2: the index tag. Kept because it is the only route that works
        # for a YAML-mode dashboard, where the resource collection is
        # read-only. On its own it is not enough: Home Assistant starts
        # serving the dashboard several seconds before config entries finish
        # setting up, and this URL is baked into the index at setup time — so
        # every restart has a window in which the page loads, looks fine, and
        # renders "Custom element doesn't exist" instead of the console.
        add_extra_js_url(hass, module_url)
        _LOGGER.debug("Registered console card at %s", CARD_URL_PATH)
    else:
        _LOGGER.warning(
            "The frontend component is not loaded, so the console card is "
            "served at %s but not added to Lovelace automatically. Add it as "
            "a dashboard resource manually if you need it.",
            CARD_URL_PATH,
        )

    hass.data[_REGISTERED_KEY] = True
    return True


async def _async_register_lovelace_resource(hass: HomeAssistant, url: str) -> bool:
    """Add the card to Lovelace's resource list, idempotently.

    Why this exists is worth stating plainly, because the failure it fixes is
    intermittent and looks like a broken card rather than a race.

    `add_extra_js_url` writes a `<script>import(...)</script>` into the
    frontend index at the moment our config entry sets up. Home Assistant's
    HTTP server, however, starts answering several seconds earlier. Measured
    on a real instance: for the first ~8 seconds after a restart the dashboard
    (measured before the Lovelace-resource route existed; ~3-5 s after it,
    see the note in `async_register_card`)
    returns HTTP 200 with no reference to the card at all, and any page loaded
    in that window shows a Configuration error until it is reloaded by hand.

    A Lovelace resource is not subject to *that*, because the list is
    persisted and so answers correctly from the moment Lovelace answers at
    all. It does not make the card immune to a restart, and an earlier version
    of this docstring claimed it did. The URL it hands out points at a static
    path registered in the same setup call, so for ~5 s after a restart the
    resource is listed and the bundle behind it 404s. Cache headers on that
    path are what cover the remainder: a browser holding the bundle makes no
    request. See DECISIONS.md, 2026-08-28, both entries.

    Returns False when the resource collection is unavailable or read-only —
    a YAML-mode dashboard, or a Home Assistant without Lovelace — which is not
    an error: `add_extra_js_url` still covers those.
    """
    lovelace = hass.data.get("lovelace")
    resources = getattr(lovelace, "resources", None)
    if resources is None:
        _LOGGER.debug("Lovelace resources unavailable; relying on the index tag")
        return False

    # A YAML-mode collection has no create method. Nothing to do, and nothing
    # wrong: resources are declared in configuration.yaml in that mode.
    if not hasattr(resources, "async_create_item"):
        _LOGGER.debug("Lovelace resources are YAML-managed; not adding ours")
        return False

    try:
        if hasattr(resources, "async_load") and not resources.loaded:
            await resources.async_load()

        for item in resources.async_items():
            if str(item.get("url", "")).split("?")[0] == CARD_URL_PATH:
                if item.get("url") == url:
                    return True
                # Same card, stale cache-buster: point it at this build rather
                # than accumulating a resource per version ever installed.
                await resources.async_update_item(item["id"], {"url": url})
                _LOGGER.debug("Updated the console card Lovelace resource")
                return True

        await resources.async_create_item({"res_type": "module", "url": url})
        _LOGGER.debug("Added the console card as a Lovelace resource")
        return True
    except Exception:  # a card that fails to register must not break setup
        _LOGGER.exception(
            "Could not register the console card as a Lovelace resource; "
            "falling back to the frontend index tag"
        )
        return False
