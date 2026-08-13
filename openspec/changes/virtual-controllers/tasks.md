## 1. Shared dispatch seam

- [ ] 1.1 Extract the tail of `handleMidi()` in `src/routes/lessons/[id]/+page.svelte` into a single `dispatchHit(gm)` that plays the sample, flashes the pad, and runs the guarded `registerHit(gm, currentBeat())`
- [ ] 1.2 Move the `document.hidden` guard and the `playing && !paused` / `hitBeat >= -MATCH_WINDOW_BEATS` window gate into `dispatchHit`, and have the MIDI path call `dispatchHit(ev.note)` after `Controller.handle()` — confirm hardware play is unchanged

## 2. Virtual source model & selection

- [ ] 2.1 Define the two reserved ids/names (`virtual:keyboard` → "Keyboard", `virtual:touch` → "On-screen pads") in a shared module, shaped as `MidiInputInfo`
- [ ] 2.2 Append the virtual entries to the selectable input list where the page reads `MidiHub.inputs`, leaving `MidiHub` itself untouched
- [ ] 2.3 Ensure the active-source `selectedId` machinery drives which virtual capture is live, and that the choice persists across sessions like a Web MIDI selection
- [ ] 2.4 Confirm a scored run records `{ device, deviceId }` from the selected virtual source, distinct from `null`, from each other, and from any Web MIDI device (spec: "Virtual runs are attributed in practice stats")

## 3. Per-source mapping

- [ ] 3.1 Ship a built-in default pad→GM mapping for each virtual source, stored in the existing deviceId-keyed grid store under the reserved id (cell→GM half only)
- [ ] 3.2 Ship a default keyboard `event.code`→pad layout (starting point: home-position cluster e.g. `KeyF`/`KeyG`/`KeyH`/`KeyJ` as core pads)
- [ ] 3.3 Make the per-cell GM dropdown edit a virtual source's mapping and persist it (spec: "Each virtual source has its own editable mapping"); surface the virtual sources as selectable inputs on `/debug/settings`

## 4. Keyboard controller

- [ ] 4.1 Add a `window` `keydown` listener that is active only while the keyboard source is selected, ignoring `event.repeat` so a held key yields exactly one hit
- [ ] 4.2 Resolve `event.code` → pad → GM and call `dispatchHit(gm)`; ignore unmapped keys (no sound, no score)
- [ ] 4.3 Route the reserved transport hotkeys to `handleTransport('start')` / `handleTransport('stop')` for start/resume and pause/stop-on-second-press (spec: "Keyboard transport hotkeys")

## 5. Touch controller

- [ ] 5.1 Build the on-screen pad grid rendering the source's cells, with a minimum touch-target size and full-width fill, using pointer events with `touch-action: none` and `preventDefault` to defeat the click delay, double-tap zoom, and scroll-on-drag
- [ ] 5.2 Fire `dispatchHit(gm)` on `pointerdown` (attack on press) for the tapped pad
- [ ] 5.3 Show the grid on the resting page and as an overlay during a run so the highway stays visible while tapping; confirm the touch source needs no extra transport binding (existing on-screen start/pause suffice)

## 6. Verification

- [ ] 6.1 `pnpm check` and a manual pass: with no Web MIDI, select each virtual source and play a lesson to the result screen (spec: "No hardware and no Web MIDI support", "Playable on a touchscreen with no Web MIDI")
- [ ] 6.2 Verify held-key single-hit, unmapped-key/pad ignored, hidden-tab deafness, and that keyboard/touch runs appear correctly attributed on `/stats`
