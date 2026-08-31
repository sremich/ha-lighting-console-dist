# Lighting Console

A theatre lighting console that lives inside Home Assistant.

Record a cue, edit it, drop an effect into it, press **GO**. Built for small
productions where the rig is Philips Hue bulbs, a few practicals on smart
plugs, and whatever else is to hand — and where the whole thing has to be
programmable by someone who is not a Home Assistant expert.

> **Status: pre-1.0, under active development.** Milestone 0 is the installable
> shell: the integration loads, the card renders, and the release pipeline
> works end to end. The cue list, rig capture and effects arrive in the
> milestones after it. Every 0.x release is a pre-release.

## Why

Home Assistant can already turn lights on. What it cannot do is run a show:
there is no cue list, no GO button, no crossfade between looks, and no way to
jump to a cue mid-rehearsal. Effects built out of `repeat` loops and
`light.turn_on` calls stagger visibly across bulbs, because the standard Hue
REST API accepts only around ten light updates a second.

This project adds the console layer:

- **A rig** — a configurable set of HA entities the console considers "the
  lights", including non-Hue bulbs, switches, dimmers and plugs.
- **Cues that capture everything.** Set the room by hand, press Record, and
  the cue restores exactly that state — including the plug you added five
  minutes ago.
- **A cue list** with GO, Back, Goto, per-cue fade times, and a current/next
  display.
- **Effects as part of a cue** — chase, strobe, pulse, colour cycle, candle
  flicker — driven over the Hue **Entertainment streaming API** at up to
  25 fps, where every light in the area updates in the same frame instead of
  stuttering one after another.
- **Graceful degradation.** If the stream cannot be established, the console
  falls back to REST, says so on the card, and the show continues.

## How it talks to Hue

Two very different APIs, used deliberately:

| | CLIP v2 REST | Entertainment streaming |
|---|---|---|
| Transport | HTTPS to the bridge | DTLS 1.2 PSK over UDP 2100 |
| Rate | ~10 light updates/sec per bridge | up to 25 fps, all lights in sync |
| Used for | discovery, pairing, entertainment areas, static looks | effects |
| Limits | rate-limited, staggers across bulbs | colour-capable Hue lights only, one area at a time per bridge |

While a stream is active the bridge ignores REST commands for the lights in
that area, so handoff between the two is explicit and driven by cue content —
never by the operator. A global **Release** always ends the stream and hands
every light back to normal Home Assistant control.

Lights that cannot be in an entertainment area — Hue white bulbs, third-party
Zigbee bulbs, switches, plugs — are first-class members of every cue and are
always driven through normal Home Assistant services.

## Installation

Requires Home Assistant **2026.8.0** or newer.

### Via HACS (recommended)

1. In HACS, add `https://github.com/sremich/ha-lighting-console-dist` as a custom
   repository with category **Integration**.
2. Install **Lighting Console**, then restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and add
   **Lighting Console**.
4. Add the **Lighting Console** card to a dashboard.

The card is bundled inside the integration and served by it — there is no
second HACS repository to install and no Lovelace resource to register by
hand. The two always match versions, and the card shows both in its corner so
a half-finished update is visible immediately.

### Manual

Download `lighting-console.zip` from the
[latest release](https://github.com/sremich/ha-lighting-console-dist/releases),
extract it into `config/custom_components/lighting_console/`, and restart.

## About this repository

This is the **distribution repository** for Lighting Console. It exists so that
HACS can install the integration, and it carries only the built integration,
its bundled card, and the licence.

Development happens elsewhere; issues and questions belong here. Every release
is built, stamped and verified by CI and published as `lighting-console.zip` —
nothing is assembled by hand.

## Credits

Protocol groundwork for the DTLS streaming layer was informed by
[`niklasR/ha-hue-entertainment-sequencer`](https://github.com/niklasR/ha-hue-entertainment-sequencer)
(MIT), which demonstrates Hue Entertainment streaming from Home Assistant.
This project implements its own streaming layer; see the credits in the
source where its approach is reused.

## Non-goals

No DMX, Art-Net or sACN output. No standalone web or mobile app outside Home
Assistant. No audio-reactive effects, no timecode sync. This is a show tool
that happens to live in Home Assistant — not a replacement for HA's scene
editor for general home use.
