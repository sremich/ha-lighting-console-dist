# Stream Deck control with Bitfocus Companion

A ready-made Companion page that runs the Lighting Console from a Stream Deck
(or Companion's on-screen emulator, or any surface Companion supports). It
talks to Home Assistant through Companion's stock Home Assistant module and the
console's services; nothing else is installed.

Tested with Companion 5.0.7 and the `homeassistant-server` module 2.0.3.

## Set up

1. Install [Bitfocus Companion](https://bitfocus.io/companion) 5.0 on any
   machine that can reach Home Assistant, and open its web UI.
2. Import `lighting-console.companionconfig` from Companion's **Import /
   Export** tab, as a full import. This replaces Companion's pages and
   connections, so do it on a fresh install or one you do not mind resetting.
3. In **Connections**, open `ha` and set:
   - **URL** to your Home Assistant, e.g. `http://homeassistant.local:8123`
   - **Access token** to a long-lived token: in Home Assistant, Profile →
     Security → Long-lived access tokens → Create token. Copy it when it is
     shown; it is shown once.
4. Save. The STATUS key (top left) turns from red OFFLINE to blue OK within a
   few seconds.

The first time the `ha` connection is used, Companion downloads its Home
Assistant module from the Bitfocus store, so the machine needs internet once.

## The keys (page 1)

```
STATUS   BACK    CURRENT   GO ▸ next   .
.        .       STOP FX   .           RELEASE (hold)
```

| Key | What it does |
|-----|--------------|
| **GO** | The only green key. Fires the next cue; shows that next cue's label and name. At the end of the list it does nothing. |
| **BACK** | Goes back one cue. At the top it does nothing. |
| **CURRENT** | Display only: the cue on stage, its name and the show. Turns amber while an effect is running. |
| **STOP FX** | Stops the running effect. |
| **RELEASE** | **Blackout.** Hold for 1 second: stops any effect, turns the whole rig off and puts the show back to the top. A quick tap does nothing, on purpose. |
| **STATUS** | Blue **OK** when Companion is connected to Home Assistant and the console is loaded. Red **OFFLINE** when the connection is down or the console's sensor is unavailable. |

CURRENT shows `unknown` until the first GO, and again after RELEASE.

## If something is wrong

- **STATUS stays red:** the URL or token on the `ha` connection is wrong, Home
  Assistant is not reachable from the Companion machine, or the Lighting
  Console's entry is unloaded (its sensor reads `unavailable`).
- **Keys do nothing but STATUS is OK:** a failed service call is not shown on
  the key. Try the same action from Home Assistant (Developer tools →
  Actions → `lighting_console.go`) to see the error.
- Keep the token private. A Companion export contains it in clear text, so
  never commit or share one.
