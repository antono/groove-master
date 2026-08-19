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
- [x] 7.7 **Narrow-screen pad layout** — the resting pad grid goes two-up and square (`aspect-ratio:1`) below 560px, so a thumb gets big honest targets instead of a cramped row of slivers. (8 pads → 2×4; the run overlay stays 4-up and compact at the bottom, ~16% of the viewport, so the highway remains visible during play.)
- [x] 7.8 **Only-taps on the pads** — `touch-action:none`, `user-select:none`, `-webkit-touch-callout:none`, `-webkit-tap-highlight-color:transparent`, `-webkit-user-drag:none`, and a `contextmenu` preventDefault, so a press never selects text, flashes a tap highlight, drags, or raises a right-click / long-press menu — it only ever plays the pad.
- [x] 7.9 **Six essential pads** — the default set is now kick / snare / closed hat / open hat / crash / ride (toms dropped): the curriculum is overwhelmingly the first four, and six keeps the grid to 2×3 / 3×2 so it fits a phone. Keyboard is R T Y / F G H, core on the home row.
- [x] 7.10 **Pads live in the Listen block** — the virtual pads render beside the chart where a drum controller's schematic sits (compact, `2.6rem`/`1.9rem` squares), not in a block at the page bottom. The old bottom block is gone; a keyboard hint points up at them.
- [x] 7.11 **Pads are the exact note colour** — coloured by `laneColor` keyed to the note's _lane index_ (not the pad's), and rendered as the solid note colour (not a tint), so a pad and its note read as one colour.
- [x] 7.12 **Press feedback, no stuck selection** — a tap blinks the pad (own brief `struck` state, ~20ms in/out via CSS transition) then returns; the button is blurred and its focus ring removed so nothing sits there looking selected.
- [x] 7.13 **Tall-screen run** — on portrait the strip is pushed into the upper third and the drum-name lane column is hidden (notes get the width), freeing the lower half for the pad overlay, which grows and goes 2×3 vertical to match the preview.
- [x] 7.14 **Onboarding key feedback** — in the setup wizard's Sounds step a keyboard key lights its pad and plays its assigned drum, so the mapping being edited is seen and heard.
- [x] 7.15 **Sticky-pad bug** — a global `button:hover` rule (→ grey) was overriding the pad colour, and on a touchscreen `:hover` sticks until you tap elsewhere, so a tapped pad looked stuck-selected. A scoped `.pad:hover/:active` override (winning specificity) keeps the pad its note colour; the only press feedback is the brief struck/lit pulse.
- [x] 7.16 **Get-ready cue** — during a run each pad whose note is within a beat of the hit line lights a bright ring + glow (`cue`), driven by a rAF loop off the audio clock, so the student sees which pad to play next before the strike (verified: the Hat pad rings as Closed HH notes approach).
- [x] 7.17 **Slower, wider perspective** — `PX_PER_BEAT` lowered globally 280 → 190 (and 150 at ≤640px); display only, scoring is beat-based. Notes travel slower and arrive from further off — a bar of look-ahead on desktop, easier on the eyes, and much more prep time on a phone. The get-ready cue's per-frame loop now runs only on a touch run (the sole consumer), so keyboard/MIDI runs do no extra per-frame work.
