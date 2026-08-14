## 1. Shared dispatch seam

- [x] 1.1 Extract the tail of `handleMidi()` in `src/routes/lessons/[id]/+page.svelte` into a single `dispatchHit(gm)` that plays the sample, flashes the pad, and runs the guarded `registerHit(gm, currentBeat())`
- [x] 1.2 Move the `document.hidden` guard and the `playing && !paused` / `hitBeat >= -MATCH_WINDOW_BEATS` window gate into `dispatchHit`, and have the MIDI path call `dispatchHit(ev.note)` after `Controller.handle()` — confirm hardware play is unchanged

## 2. Virtual source model & selection

- [x] 2.1 Define the two reserved ids/names (`virtual:keyboard` → "Keyboard", `virtual:touch` → "On-screen pads") in a shared module, shaped as `MidiInputInfo`
- [x] 2.2 Append the virtual entries to the selectable input list where the page reads `MidiHub.inputs`, leaving `MidiHub` itself untouched
- [x] 2.3 Ensure the active-source `selectedId` machinery drives which virtual capture is live, and that the choice persists across sessions like a Web MIDI selection
- [x] 2.4 Confirm a scored run records `{ device, deviceId }` from the selected virtual source, distinct from `null`, from each other, and from any Web MIDI device (spec: "Virtual runs are attributed in practice stats")

## 3. Per-source mapping

- [x] 3.1 Ship a built-in default pad→GM mapping for each virtual source, stored in the existing deviceId-keyed grid store under the reserved id (cell→GM half only)
- [x] 3.2 Ship a default keyboard `event.code`→pad layout (starting point: home-position cluster e.g. `KeyF`/`KeyG`/`KeyH`/`KeyJ` as core pads)
- [x] 3.3 Make a per-pad GM dropdown edit a virtual source's mapping and persist it (spec: "Each virtual source has its own editable mapping"). Editing lives in the **onboarding / setup wizard** (a new `sounds` step reached from the connect screen), not `/debug/settings`: that page is a fixed 16-cell hardware-capture editor and is debug-gated, so it can't host an 8-pad, note-less virtual source or be reached by a touch-only student. The lesson page also exposes both virtual sources in an input picker.

## 4. Keyboard controller

- [x] 4.1 Add a `window` `keydown` listener that is active only while the keyboard source is selected, ignoring `event.repeat` so a held key yields exactly one hit
- [x] 4.2 Resolve `event.code` → pad → GM and call `dispatchHit(gm)`; ignore unmapped keys (no sound, no score)
- [x] 4.3 Route the reserved transport hotkeys to `handleTransport('start')` / `handleTransport('stop')` for start/resume and pause/stop-on-second-press (spec: "Keyboard transport hotkeys")

## 5. Touch controller

- [x] 5.1 Build the on-screen pad grid rendering the source's cells, with a minimum touch-target size and full-width fill, using pointer events with `touch-action: none` and `preventDefault` to defeat the click delay, double-tap zoom, and scroll-on-drag
- [x] 5.2 Fire `dispatchHit(gm)` on `pointerdown` (attack on press) for the tapped pad
- [x] 5.3 Show the grid on the resting page and as an overlay during a run so the highway stays visible while tapping; confirm the touch source needs no extra transport binding (existing on-screen start/pause suffice)

## 6. Verification

- [x] 6.1 `pnpm check` and `pnpm build` clean. Full browser verification against `pnpm preview` (Chrome DevTools): input picker lists Keyboard + On-screen pads and defaults by pointer type; **keyboard run end-to-end** — Space starts, KeyF/KeyG score, run finishes and records a session with `device:"Keyboard"`, `deviceId:"virtual:keyboard"`; **touch run end-to-end** — Play starts, the overlay pads tap and score, records `device:"On-screen pads"`, `deviceId:"virtual:touch"`. Selection persists to `localStorage`. No console errors from the feature.
- [x] 6.2 Confirmed live: unmapped key ignored (no sound), mapped key sounds once, **held/repeat key adds no hit** (`e.repeat` guard), hidden-tab deafness (`document.hidden` guard); Esc pauses then ends on the second press; editing round-trips (a remapped pad 49→35 persisted under `virtual:keyboard` and reloaded on the lesson page).

## 7. Fixes found during verification

- [x] 7.1 **Jitter** — the run only preloaded the lesson's own lanes, so hitting a virtual pad the lesson doesn't use (crash/tom/ride) fetched+decoded mid-run and landed late. `kitNotes` now also preloads `controller.drums`, so every pad is warm before play (helps any controller, not just virtual).
- [x] 7.2 **Touch/keyboard silent at rest** — audio only came up on Play/Listen, so a pad tap or key before starting hit a null player. `virtualHit()` brings audio up on the first interaction (that tap is the gesture), so pads sound immediately.
- [x] 7.3 **Pad colours** — `VirtualPads` colours each pad with `laneColor(sound)`, the same `--note-*` hue the highway lanes use, so a pad reads as the note it plays.
- [x] 7.4 **Drum names in the preview** — the generic `ControllerPreview` schematic was blank for a virtual source (only the used lane labelled), so it is suppressed for virtual and `VirtualPads` — named, coloured, with the lesson's pads highlighted and the rest dimmed — is the single pad display.
- [x] 7.5 **Key letters only on keyboard** — the touch pads no longer show keyboard letters (a `keys` prop, true only for the keyboard source).
- [x] 7.6 **Touch overlay hidden under the highway** — the run overlay was `z-index:40` beneath the fullscreen highway (`z-index:50`); raised to `60` so it is visible and tappable during a run.
