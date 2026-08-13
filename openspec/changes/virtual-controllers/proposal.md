## Why

Today a lesson can only be played with a Web MIDI controller: no hardware means
no way to hit a pad, so the app is unusable to anyone who has not bought and
connected a drum controller — and unusable on a phone or tablet, which have no
Web MIDI at all. The whole scoring pipeline already runs on an abstract note
stream, so the missing piece is not the engine but the input: a computer
keyboard and an on-screen pad grid would let a curious visitor start playing in
the first session, on whatever device they opened the site with.

## What Changes

- Add a **computer-keyboard controller**: a fixed default key→pad layout so any
  laptop can play a lesson immediately, with the hits scored exactly as MIDI
  hits are.
- Add **on-screen touch pads**: a virtual pad grid, sized for phones and tablets,
  that turns a tap into the same scored hit — the only way to play on a
  touchscreen device.
- Both virtual sources feed the **same note stream** the existing engine already
  scores (`Controller.handle()` → `registerHit()`), so the highway, timing
  windows, result report and per-pad breakdown work unchanged.
- Both are **selectable input sources** alongside connected Web MIDI ports, and
  each carries a **stable synthetic device identity** ("Keyboard", "Touch pads")
  so a scored run is attributed to it in practice stats rather than recorded as
  `null` / "no controller".
- Each virtual source has its own **pad→GM-drum mapping**, defaulting to a
  sensible layout and reusing the existing cell→GM-note model; there is no note
  to capture, so mapping is chosen/edited, not learned from the hardware.
- Add **keyboard transport hotkeys** — start/resume and stop/pause from the
  keyboard, so a keyboard-only student can run a lesson end to end without
  reaching for hardware they do not have. The on-screen touch controller needs no
  such addition: it already carries visible start/pause controls.
- Availability with **no MIDI hardware and no Web MIDI support at all** — the
  app must still reach a playable state, since that is now the common case.

Not in scope: hi-hat pedal semantics for virtual sources — they expose the pad's
default voice only.

## Capabilities

### New Capabilities

- `virtual-controllers`: playing lessons through a computer keyboard or on-screen
  touch pads — the default layouts, how a tap/keypress becomes a scored hit on
  the existing note stream, how a virtual source is selected and mapped, and how
  it is identified in practice stats.

### Modified Capabilities

<!-- No existing spec's requirements change. Input source selection, mapping and
     stats attribution are all newly specified behavior owned by the new
     capability above; the scoring/highway engine is unchanged. -->

## Impact

- **Code**: `src/lib/midi-hub.svelte.ts` (register virtual sources in the input
  list beside Web MIDI ports), `src/lib/controller.svelte.ts` (mapping keyed by a
  synthetic device id; no note-capture path), `src/routes/lessons/[id]/+page.svelte`
  (keyboard listener + on-screen pad overlay driving the existing
  `registerHit()`; keyboard transport hotkeys driving the existing
  `handleTransport()`; device recorded for stats), and a new keyboard/touch input
  module.
- **Config**: new default layouts and per-source mappings in `localStorage`
  beside the existing per-device pad grids; `/debug/settings` and onboarding gain
  the virtual sources as selectable inputs.
- **Stats**: `SessionStat.device` / `deviceId` gain the two synthetic identities;
  no schema change, existing records keep working.
- **No dependency, API, or build changes** — keyboard and pointer events only, no
  new packages.
