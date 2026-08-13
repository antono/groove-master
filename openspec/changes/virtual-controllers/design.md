## Context

See `proposal.md` — Why. The scoring engine already runs on an abstract hit:
`handleMidi()` in `src/routes/lessons/[id]/+page.svelte` turns a Web MIDI message
into a resolved GM drum note, then does exactly three things with it — play the
sample, flash the pad, and `registerHit(gm, beat)`. Everything before that tail
(`Controller.handle()`) is hardware plumbing: note→cell mapping, hi-hat pedal
state, transport-button matching, all keyed off a raw controller note.

Two facts shape the design:

- The selectable input is a `MidiInputInfo { id, name, manufacturer }`; the page
  remembers a `selectedId` and records `{ device, deviceId }` into stats from it.
  `MidiHub.inputs` is a thin, Web-MIDI-only enumeration.
- Pad→GM mappings live in `localStorage` keyed by the Web MIDI `deviceId`. A
  virtual source has no controller note to capture, so only the cell→GM half of
  that model is meaningful to it.

## Goals / Non-Goals

**Goals:**

- Reach `registerHit()` from keyboard and touch without duplicating the score/
  play/flash tail, and without inventing fake MIDI bytes.
- Reuse the existing `selectedId` selection + `{ device, deviceId }` stats
  attribution unchanged, by giving virtual sources real (reserved) ids.
- Keep `MidiHub` a pure Web MIDI wrapper — synthetic sources do not enter it.

**Non-Goals:**

- Hi-hat pedal voicing for virtual sources (proposal scopes it out).
- A capture/learn UI for the keyboard (mapping is edit-only; there is no note to
  learn). Gamepad and other input devices.

## Decisions

### 1. Virtual hits bypass `Controller.handle()` and call the score tail directly

Factor the tail of `handleMidi()` — `player.play(kit, gm)` + `flash(gm)` +
guarded `registerHit(gm, currentBeat())` — into one `dispatchHit(gm)`. The MIDI
path keeps calling `Controller.handle()` and then `dispatchHit(ev.note)`; the
keyboard and touch sources resolve a key/pad to a GM note themselves and call
`dispatchHit(gm)` straight away.

- **Why not synthesize `[0x90, note, vel]` and run it through `Controller`?**
  That path exists to undo a hardware indirection virtual sources don't have: we
  would have to mint fake controller notes, maintain a note→cell map for them,
  and pass through hi-hat resolution that never applies. Resolving pad→GM in the
  virtual source and entering at the already-resolved seam is strictly less
  machinery.
- The `document.hidden` guard and the `playing && !paused` / `hitBeat >=
-MATCH_WINDOW_BEATS` gate move into `dispatchHit`, so every source inherits the
  same "deaf when backgrounded / only score inside the window" behavior for free.

### 2. Synthetic sources are reserved ids concatenated onto the input list

Add two reserved ids — `virtual:keyboard` and `virtual:touch` — as
`MidiInputInfo`-shaped entries the selection layer appends to `MidiHub.inputs`.
`MidiHub` itself is untouched; the concatenation lives where the page already
reads `inputs`/`selectedId`. Because they are ordinary ids, selection,
persistence of the choice, and the `{ device, deviceId }` stats record all work
with no special-casing — the id is the `deviceId`, and the display name
("Keyboard", "On-screen pads") is the `device`.

- **Why not register them inside `MidiHub`?** It documents itself as a thin Web
  MIDI wrapper; a virtual source has no `MIDIInput`, no `onmidimessage`, no
  `listen()`. Keeping them out preserves that boundary and avoids null-guards
  throughout the hub.

### 3. Mapping reuses the deviceId-keyed store, cell→GM half only

Virtual sources store their pad→GM mapping in the same `localStorage` grid store,
keyed by their reserved id. The controller-note→cell half is simply absent. Ship
a built-in default mapping for each so first use needs no setup, and let the
existing per-cell GM dropdown edit it. The keyboard adds one layer on top —
`event.code`→pad — so the physical key positions are fixed while which drum each
pad triggers stays editable like any other source.

- Keyboard uses `event.code` (physical position), not `event.key`, so the default
  layout is the same shape on QWERTY/AZERTY/Dvorak and doesn't depend on the OS
  keyboard language.
- Touch pads _are_ the grid cells: the on-screen grid renders the source's cells
  and each cell taps to its mapped GM note, so the pad layout and the mapping are
  the same object.

### 4. Input capture per source

- **Keyboard**: a `window` `keydown` listener, active only while the keyboard
  source is selected. Ignore `event.repeat` (kills auto-repeat → one hit per
  press per requirement); the reserved transport hotkeys route to the existing
  `handleTransport('start'|'stop')`, everything else resolves through the code→
  pad→GM map or is ignored.
- **Touch**: an on-screen pad grid using pointer events with `touch-action:
none` and `preventDefault`, to defeat the synthetic-click delay, double-tap
  zoom, and scroll-on-drag. Shown on the resting page and as an overlay during a
  run so the student can watch the highway and tap. `pointerdown` fires the hit
  (attack on press, not release).

## Risks / Trade-offs

- **Keyboard `code` default doesn't match a student's mental key labels** (a
  Dvorak typist sees the letters move) → the mapping is by physical position on
  purpose (stable home-row shape); the per-pad GM dropdown lets anyone re-pick,
  and a future key-remap UI is additive.
- **Small touch targets cause mis-hits on phones** → enforce a minimum pad size
  and let the grid fill the width; scoring already tolerates timing spread, and a
  wrong pad is an `extra`, not a crash.
- **Held key or long press double-firing** → keyboard ignores `event.repeat`;
  touch fires once on `pointerdown` and ignores the rest of the gesture.
- **A backgrounded tab still receiving key events** → `dispatchHit` keeps the
  `document.hidden` guard, so virtual sources are as deaf as the MIDI path when
  the tab is hidden.

## Migration Plan

Purely additive — no data migration. Existing per-device pad grids and stats
records are untouched; the two reserved ids are new keys that cannot collide with
a Web MIDI `deviceId`. Rollback is removing the virtual entries from the input
list; hardware play is unaffected at every step.

## Open Questions

- The exact default `event.code` layout and the touch grid's column count are
  design-level details that don't change the specs, the seam, or the task
  breakdown; they can be settled during implementation. Proposed starting point:
  a two-row home-position cluster for the keyboard (e.g. `KeyF`/`KeyG`/`KeyH`/
  `KeyJ` as the core pads) and a grid whose cells mirror the lesson-chart layout
  for touch.
