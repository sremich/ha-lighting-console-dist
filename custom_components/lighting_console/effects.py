"""Effects: the cues that move.

Two things live here. **Definitions** describe each effect — its name, its
parameters, and the sane default for every one of them. The card renders its
editing form straight from that description, so adding an effect never means
touching the frontend. **The engine** runs one, as an asyncio task, by
calling ordinary Home Assistant services.

## Why this is REST-driven, and why that is temporary

Stevie's rig already runs chases today, as an `input_boolean` driving an
automation that loops a script of `light.turn_on` / `delay` / `light.turn_off`
at 200-300 ms a step. That is the ceiling of what per-light REST calls to a
Hue bridge can do, and it is visibly steppy. Milestone 3 replaces the
transport with the Entertainment stream at 25 fps.

So the engine deliberately keeps the *description* of an effect and the
*execution* of it apart. `EffectEngine.async_start` takes a name and a
parameter dict and nothing else; when streaming lands it becomes a second
backend behind the same call, and every cue already stored keeps working
untouched.

## The rule that outranks everything else here

An effect must never outlive the thing that started it. The engine holds at
most one running effect, cancels it on any new start, and is stopped
unconditionally when the config entry unloads. `async_stop` is written so it
cannot itself fail: if the lights cannot be reached, the task still dies.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    DEFAULT_MAX_FRAMES_IN_FLIGHT,
    MAX_FRAMES_IN_FLIGHT,
    MIN_FRAMES_IN_FLIGHT,
)

_LOGGER = logging.getLogger(__name__)

# Nothing may ask the bridge to do more than this. A chase stepping faster
# than roughly 20 Hz over REST does not look faster, it looks broken — the
# calls queue behind each other and the pattern falls apart. Milestone 3
# lifts this by changing transport, not by raising the number.
MIN_STEP_MS = 50


@dataclass(frozen=True)
class EffectParam:
    """One knob on an effect, and everything the card needs to draw it."""

    key: str
    label: str
    type: str
    """`number`, `color`, `entities`, `select`, `boolean` or `steps`."""

    default: Any = None
    minimum: float | None = None
    maximum: float | None = None
    step: float | None = None
    unit: str = ""
    options: list[str] = field(default_factory=list)
    help: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "type": self.type,
            "default": self.default,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "step": self.step,
            "unit": self.unit,
            "options": list(self.options),
            "help": self.help,
        }


@dataclass(frozen=True)
class EffectDefinition:
    """An effect the console knows how to run."""

    name: str
    label: str
    description: str
    params: list[EffectParam]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "params": [p.to_dict() for p in self.params],
        }

    def defaults(self) -> dict[str, Any]:
        return {p.key: p.default for p in self.params}


_TARGETS = EffectParam(
    key="targets",
    label="Lights",
    type="entities",
    default=[],
    help="Which lights this effect drives. Empty means the whole rig.",
)
_BRIGHTNESS = EffectParam(
    key="brightness_pct",
    label="Brightness",
    type="number",
    default=100,
    minimum=1,
    maximum=100,
    step=1,
    unit="%",
)

EFFECTS: dict[str, EffectDefinition] = {
    "chase": EffectDefinition(
        name="chase",
        label="Chase",
        description=(
            "Walks the lights in order, one at a time. Runs until the next cue or Stop."
        ),
        params=[
            _TARGETS,
            EffectParam(
                key="colors",
                label="Colours",
                type="color",
                default=[[255, 147, 41]],
                help="Cycled across the lights. One colour chases in a single tint.",
            ),
            _BRIGHTNESS,
            EffectParam(
                key="step_ms",
                label="Step",
                type="number",
                default=300,
                minimum=MIN_STEP_MS,
                maximum=5000,
                step=10,
                unit="ms",
                help="Time between one light lighting and the next.",
            ),
            EffectParam(
                key="fade_in",
                label="Fade in",
                type="number",
                default=0.1,
                minimum=0,
                maximum=10,
                step=0.1,
                unit="s",
                help="How long each light takes to rise on its step.",
            ),
            EffectParam(
                key="fade_out",
                label="Fade out",
                type="number",
                default=1.0,
                minimum=0,
                maximum=10,
                step=0.1,
                unit="s",
                help="How long each light takes to fall after its step.",
            ),
            EffectParam(
                key="direction",
                label="Direction",
                type="select",
                default="forward",
                options=["forward", "reverse", "bounce"],
            ),
        ],
    ),
    "flash": EffectDefinition(
        name="flash",
        label="Flash",
        description="One hit on every light, then out. Fires once and stops.",
        params=[
            _TARGETS,
            EffectParam(
                key="colors",
                label="Colours",
                type="color",
                default=[[255, 188, 113]],
                help="One per light, cycled. One colour flashes everything in it.",
            ),
            _BRIGHTNESS,
            EffectParam(
                key="hold_ms",
                label="Hold",
                type="number",
                default=200,
                minimum=20,
                maximum=5000,
                step=10,
                unit="ms",
            ),
            EffectParam(
                key="fade_out",
                label="Fade out",
                type="number",
                default=0.5,
                minimum=0,
                maximum=10,
                step=0.1,
                unit="s",
            ),
        ],
    ),
    "strobe": EffectDefinition(
        name="strobe",
        label="Strobe",
        description=(
            "Every light on and off together, repeating. Runs until the next "
            "cue or Stop."
        ),
        params=[
            _TARGETS,
            EffectParam(
                key="colors",
                label="Colours",
                type="color",
                default=[[255, 255, 255]],
                help="One per light, cycled. One colour strobes everything in it.",
            ),
            _BRIGHTNESS,
            EffectParam(
                key="period_ms",
                label="Period",
                type="number",
                default=200,
                minimum=MIN_STEP_MS * 2,
                maximum=4000,
                step=10,
                unit="ms",
                help="A full on-and-off cycle.",
            ),
        ],
    ),
    "sequence": EffectDefinition(
        name="sequence",
        label="Sequence",
        description=(
            "Your own steps, in order: each lights its lamps in one colour, "
            "holds, and the previous step's lamps go out. Police lights, a "
            "custom chase, anything a chase cannot spell."
        ),
        params=[
            _BRIGHTNESS,
            EffectParam(
                key="loop",
                label="Loop",
                type="boolean",
                default=True,
                help="Off: run the steps once and stop.",
            ),
            EffectParam(
                key="steps",
                label="Steps",
                type="steps",
                default=[
                    {
                        "targets": [],
                        "color": [255, 0, 0],
                        "hold_ms": 500,
                        "fade_in": 0.0,
                        "fade_out": 0.0,
                    },
                    {
                        "targets": [],
                        "color": [0, 0, 255],
                        "hold_ms": 500,
                        "fade_in": 0.0,
                        "fade_out": 0.0,
                    },
                ],
                help="Each step: which lights, one colour, how long to hold, "
                "and how fast they rise and fall. Empty lights means the whole rig.",
            ),
        ],
    ),
}

#: One normalised sequence step: (targets, rgb, hold seconds, fade in, fade out).
_Step = tuple[list[str], list[int], float, float, float]


def _steps(params: dict[str, Any], targets: list[str]) -> list[_Step]:
    """Normalise the step list; a step's empty or unknown lights mean all of
    `targets`. Malformed steps are dropped; no usable step means the default."""
    raw = params.get("steps")
    if not isinstance(raw, list):
        raw = EFFECTS["sequence"].defaults()["steps"]
    in_rig = set(targets)
    steps: list[_Step] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        chosen = [
            e for e in item.get("targets") or [] if isinstance(e, str) and e in in_rig
        ]
        steps.append(
            (
                chosen or list(targets),
                _colors({"colors": [item.get("color")]}, [[255, 255, 255]])[0],
                _as_int(item, "hold_ms", 500, MIN_STEP_MS, 60_000) / 1000,
                _as_float(item, "fade_in", 0.0, 0.0, 10.0),
                _as_float(item, "fade_out", 0.0, 0.0, 10.0),
            )
        )
    if not steps:
        return _steps({"steps": None}, targets)
    return steps


def describe_effects() -> list[dict[str, Any]]:
    """Every effect, for the card's picker and its generic parameter form."""
    return [effect.to_dict() for effect in EFFECTS.values()]


def _as_int(params: dict[str, Any], key: str, default: int, low: int, high: int) -> int:
    try:
        return max(low, min(high, int(float(params.get(key, default)))))
    except (TypeError, ValueError):
        return default


def _as_float(
    params: dict[str, Any], key: str, default: float, low: float, high: float
) -> float:
    try:
        return max(low, min(high, float(params.get(key, default))))
    except (TypeError, ValueError):
        return default


def _colors(params: dict[str, Any], fallback: list[list[int]]) -> list[list[int]]:
    """Normalise the colour list, dropping anything that is not an RGB triple."""
    raw = params.get("colors")
    out: list[list[int]] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, (list, tuple)) and len(item) == 3:
                try:
                    out.append([max(0, min(255, int(c))) for c in item])
                except (TypeError, ValueError):
                    continue
    return out or fallback


def _clamp_in_flight(value: object) -> int:
    """Keep the configured limit inside the range the options flow allows.

    A stored option outlives the range that produced it, and an engine that
    spawned zero pumps would light nothing at all - a silent failure in the
    middle of a show, which is the worst kind this project can have.
    """
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return DEFAULT_MAX_FRAMES_IN_FLIGHT
    return max(MIN_FRAMES_IN_FLIGHT, min(MAX_FRAMES_IN_FLIGHT, number))


class EffectEngine:
    """Runs at most one effect at a time.

    "At most one" is a design decision, not a limitation of the loop. Two
    effects layered over the same fixture fight over it, and the result on
    stage depends on which service call happens to land last — which is
    exactly the kind of thing that is fine in rehearsal and wrong on a Friday
    night. Starting an effect stops whatever was running.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        max_in_flight: int = DEFAULT_MAX_FRAMES_IN_FLIGHT,
    ) -> None:
        self._hass = hass
        self._task: asyncio.Task[None] | None = None
        self._running: str | None = None
        self._running_params: dict[str, Any] = {}
        # Frame delivery. See `_async_pump` for why this exists at all.
        self._max_in_flight = _clamp_in_flight(max_in_flight)
        self._pumps: list[asyncio.Task[None]] = []
        self._pending: dict[frozenset[str], tuple[str, dict[str, Any]]] = {}
        self._frame_ready = asyncio.Event()
        self._sent = 0
        self._dropped = 0

    @property
    def frame_counts(self) -> tuple[int, int]:
        """(delivered, superseded) since the running effect started."""
        return self._sent, self._dropped

    @property
    def max_in_flight(self) -> int:
        return self._max_in_flight

    def set_max_in_flight(self, value: object) -> None:
        """Change the limit. Applies to the next effect, not the running one.

        Changing it under a running effect would mean starting or killing
        pumps mid-flight for no benefit: the entry reloads when its options
        change, which stops effects anyway.
        """
        self._max_in_flight = _clamp_in_flight(value)

    @property
    def running(self) -> str | None:
        """The name of the running effect, or None."""
        return self._running

    @property
    def running_params(self) -> dict[str, Any]:
        return dict(self._running_params)

    def status(self) -> dict[str, Any]:
        return {"running": self._running, "params": self.running_params}

    async def async_start(
        self, name: str, params: dict[str, Any], targets: list[str]
    ) -> bool:
        """Start an effect over `targets`. Returns False if it is unknown.

        `targets` is resolved by the caller — the engine is told the entity
        list rather than reaching for the rig itself, so a cue can drive a
        subset without the engine knowing what a rig is.
        """
        if name not in EFFECTS:
            return False
        await self.async_stop()
        if not targets:
            _LOGGER.warning("Effect %s started with no targets; nothing to drive", name)
            return False

        self._running = name
        self._running_params = dict(params)
        self._sent = 0
        self._dropped = 0
        self._pending = {}
        self._frame_ready.clear()
        self._pumps = [
            self._hass.async_create_background_task(
                self._async_pump(),
                f"lighting_console effect frames {name} #{i}",
                eager_start=False,
            )
            for i in range(self._max_in_flight)
        ]
        # A *background* task, deliberately. A chase runs until someone stops
        # it, so tracking it as a normal task would make anything that waits
        # for pending work - Home Assistant's own shutdown included - wait
        # forever on a loop that never intends to finish.
        self._task = self._hass.async_create_background_task(
            self._async_run(name, params, targets),
            f"lighting_console effect {name}",
            eager_start=False,
        )
        return True

    async def async_stop(self) -> None:
        """Stop whatever is running. Must not raise, ever.

        Both halves, and the loop first: killing it before the pump means it
        cannot enqueue another frame while the pump is being shut down.
        Anything still waiting is discarded - Stop means stop, and the cue or
        Release that follows sets the lights itself.
        """
        task, self._task = self._task, None
        pumps, self._pumps = self._pumps, []
        self._running = None
        self._running_params = {}

        doomed: list[tuple[asyncio.Task[None], str]] = []
        if task is not None:
            doomed.append((task, "Effect"))
        doomed.extend((pump, "Effect frame pump") for pump in pumps)

        for victim, what in doomed:
            if victim.done():
                continue
            victim.cancel()
            try:
                await victim
            except asyncio.CancelledError:
                pass
            except Exception:  # a dying effect must not take the console with it
                _LOGGER.exception("%s task raised while being stopped", what)

        self._pending = {}
        self._frame_ready.clear()

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def _async_run(
        self, name: str, params: dict[str, Any], targets: list[str]
    ) -> None:
        try:
            if name == "chase":
                await self._run_chase(params, targets)
            elif name == "flash":
                await self._run_flash(params, targets)
            elif name == "strobe":
                await self._run_strobe(params, targets)
            elif name == "sequence":
                await self._run_sequence(params, targets)
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOGGER.exception("Effect %s failed", name)
        finally:
            # A one-shot that ran to completion must stop reporting itself as
            # running. Checking the task's own `done()` here cannot work -
            # this *is* that task, so it is never done yet. The name guard is
            # what makes this safe: a cancelled effect has already been
            # cleared by `async_stop`, and an effect superseded by a newer one
            # sees a different name here and leaves it alone.
            if self._running == name:
                self._running = None
                self._running_params = {}

    async def _async_pump(self) -> None:
        """Deliver frames to the lights, one at a time, latest wins.

        Effects used to call `async_call(..., blocking=False)` straight from
        the loop. Home Assistant turns each of those into its own task and
        returns immediately, so the loop never learned that the bridge was
        slower than its frame rate and simply kept issuing. Measured on the
        rig: a strobe at the default 200 ms period issues ten frames a second,
        each one a bridge command per lamp, against a bridge that manages
        about ten commands a second in total. The queue grew for as long as
        the effect ran, and because those queued calls belong to Home
        Assistant rather than to us, `async_stop` could not cancel them - it
        returned in 6 ms while the rig kept working through the backlog for
        another twenty-six seconds. Pressing Release again only added more
        commands to the back of the same queue.

        So: at most one frame in flight, and one waiting frame *per set of
        lights*. A frame that arrives while another is waiting for the same
        lights replaces it rather than queueing behind it. Superseding rather
        than skipping means the newest instruction always wins - a flash's
        closing "off" is never discarded in favour of the "on" before it,
        which is what a plain "skip while busy" rule would do.

        Per set of lights, and not one slot for everything, because a chase
        issues `turn_off(lamp A)` and `turn_on(lamp B)` back to back with no
        sleep between them. A single slot lets the `on` supersede the `off`
        and leaves lamp A lit - a chase smeared into a trail instead of a
        moving dot. Frames addressed to different lights do not supersede one
        another, so the backlog is bounded by the size of the rig rather than
        by how long the effect has been running, which is the property that
        was missing before.

        There are `max_in_flight` of these running concurrently, all feeding
        from the same waiting set. One gives the fastest stop and the least
        throughput; the default of two keeps the bridge pipelined. Stopping is
        bounded by that many bridge round-trips - whatever is in flight lands,
        and everything still waiting is dropped.
        """
        while True:
            await self._frame_ready.wait()
            if not self._pending:
                self._frame_ready.clear()
                continue
            key = next(iter(self._pending))
            service, data = self._pending.pop(key)
            if not self._pending:
                self._frame_ready.clear()
            try:
                await self._hass.services.async_call(
                    "light", service, data, blocking=True
                )
                self._sent += 1
            except asyncio.CancelledError:
                raise
            except Exception:
                _LOGGER.exception("Effect frame %s failed", service)

    def _send(self, service: str, data: dict[str, Any]) -> None:
        """Queue one frame, superseding any frame waiting for the same lights.

        Keyed on the lights it addresses, so a frame can only ever displace an
        instruction it actually overrides.
        """
        entity_id = data.get("entity_id") or []
        key = frozenset(entity_id if isinstance(entity_id, list) else [entity_id])
        if key in self._pending:
            self._dropped += 1
        self._pending[key] = (service, data)
        self._frame_ready.set()

    async def _light_on(
        self,
        entity_ids: list[str],
        rgb: list[int],
        brightness_pct: int,
        transition: float,
    ) -> None:
        self._send(
            "turn_on",
            {
                "entity_id": entity_ids,
                "rgb_color": rgb,
                "brightness_pct": brightness_pct,
                "transition": transition,
            },
        )

    @staticmethod
    def _spread(
        targets: list[str], colors: list[list[int]]
    ) -> list[tuple[list[int], list[str]]]:
        """Colour i to target i, cycled: the targets grouped per distinct colour.

        Will enters one colour per lamp, as chase lets him, and expects each
        lamp to take its own. A single colour is still exactly one group. The
        closing off uses the same grouping so each off shares its supersede
        key with its on — an off keyed on all targets at once would share it
        with none of them and could land ahead of a still-pending on.
        """
        by_color: dict[tuple[int, ...], list[str]] = {}
        for index, entity_id in enumerate(targets):
            by_color.setdefault(tuple(colors[index % len(colors)]), []).append(
                entity_id
            )
        return [(list(rgb), entity_ids) for rgb, entity_ids in by_color.items()]

    async def _light_on_spread(
        self,
        groups: list[tuple[list[int], list[str]]],
        brightness_pct: int,
        transition: float,
    ) -> None:
        for rgb, entity_ids in groups:
            await self._light_on(entity_ids, rgb, brightness_pct, transition)

    async def _light_off_spread(
        self, groups: list[tuple[list[int], list[str]]], transition: float
    ) -> None:
        for _, entity_ids in groups:
            await self._light_off(entity_ids, transition)

    async def _light_off(self, entity_ids: list[str], transition: float) -> None:
        self._send("turn_off", {"entity_id": entity_ids, "transition": transition})

    async def _run_chase(self, params: dict[str, Any], targets: list[str]) -> None:
        colors = _colors(params, [[255, 147, 41]])
        brightness = _as_int(params, "brightness_pct", 100, 1, 100)
        step_ms = _as_int(params, "step_ms", 300, MIN_STEP_MS, 5000)
        fade_in = _as_float(params, "fade_in", 0.1, 0.0, 10.0)
        fade_out = _as_float(params, "fade_out", 1.0, 0.0, 10.0)
        direction = params.get("direction", "forward")
        if direction not in ("forward", "reverse", "bounce"):
            direction = "forward"

        order = list(targets)
        if direction == "reverse":
            order.reverse()
        elif direction == "bounce" and len(order) > 2:
            order = order + order[-2:0:-1]

        step = step_ms / 1000
        index = 0
        while True:
            entity = order[index % len(order)]
            color = colors[index % len(colors)]
            await self._light_on([entity], color, brightness, fade_in)
            await asyncio.sleep(step)
            await self._light_off([entity], fade_out)
            index += 1

    async def _run_flash(self, params: dict[str, Any], targets: list[str]) -> None:
        colors = _colors(params, [[255, 188, 113]])
        brightness = _as_int(params, "brightness_pct", 100, 1, 100)
        hold_ms = _as_int(params, "hold_ms", 200, 20, 5000)
        fade_out = _as_float(params, "fade_out", 0.5, 0.0, 10.0)

        groups = self._spread(targets, colors)
        await self._light_on_spread(groups, brightness, 0)
        await asyncio.sleep(hold_ms / 1000)
        await self._light_off_spread(groups, fade_out)
        # A flash is a one-shot; wait out its own fade so that a GO landing
        # immediately after does not fight the tail of it.
        await asyncio.sleep(fade_out)

    async def _run_sequence(self, params: dict[str, Any], targets: list[str]) -> None:
        brightness = _as_int(params, "brightness_pct", 100, 1, 100)
        loop = params.get("loop", True) is not False
        steps = _steps(params, targets)

        previous: _Step | None = None
        while True:
            for step in steps:
                lights, color, hold, fade_in, _ = step
                if previous is not None:
                    # Lamps that carry over into this step are not switched off
                    # in between — that would flicker them.
                    gone = [e for e in previous[0] if e not in lights]
                    if gone:
                        await self._light_off_spread(
                            self._spread(gone, [previous[1]]), previous[4]
                        )
                await self._light_on_spread(
                    self._spread(lights, [color]), brightness, fade_in
                )
                await asyncio.sleep(hold)
                previous = step
            if not loop:
                break
        # A one-shot ends dark, and waits out its own fade like a flash does.
        assert previous is not None
        await self._light_off_spread(
            self._spread(previous[0], [previous[1]]), previous[4]
        )
        await asyncio.sleep(previous[4])

    async def _run_strobe(self, params: dict[str, Any], targets: list[str]) -> None:
        colors = _colors(params, [[255, 255, 255]])
        brightness = _as_int(params, "brightness_pct", 100, 1, 100)
        period_ms = _as_int(params, "period_ms", 200, MIN_STEP_MS * 2, 4000)
        half = period_ms / 2000
        groups = self._spread(targets, colors)

        while True:
            await self._light_on_spread(groups, brightness, 0)
            await asyncio.sleep(half)
            await self._light_off_spread(groups, 0)
            await asyncio.sleep(half)
