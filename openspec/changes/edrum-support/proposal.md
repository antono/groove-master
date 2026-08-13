## Why

Groove Academy assumes one shape of controller: a rectangular grid of pads.
`presets.ts` describes a device as `cols × rows`, the wizard walks that grid
left-to-right capturing one note per cell, and `controller-map.svelte` draws it
back as a rectangle. That is exactly right for an MPD218 and exactly wrong for
an electronic drum kit.

An e-drum kit is not a grid. Its pads sit where the drums they stand for sit —
snare in front of you, toms across the top, cymbals out at the edges — and
their arrangement carries meaning a 4×4 box destroys. Asked to map a Millenium
MD-90 today, the wizard offers a rectangle with seven of its sixteen cells
filled, in an order the student has to invent. Worse, the kit's foot pedals do
not fit the model at all: a hi-hat is one drum with two voices chosen by a
pedal, and nothing in the app can express that.

So the second half of setup — everything after the device is chosen — needs a
second path. Not a wider grid: a different flow, one that shows the kit as a
kit, learns which pad is which drum, learns what the pedals do, and lets the
student prove it works by hitting things and watching them light up.

And a second kind of instrument is the moment to admit there was never a first
one. Today there is no such thing as "the student's controller": there is a
JSON blob in `localStorage` that three pages parse for themselves, a note map
rebuilt on every device change, a transport binding checked separately, and two
components that draw pads without knowing what they are drawing. Adding drum
kits to that means adding a second special case in each of those places.

So this change introduces a **Controller** — one object standing for the
instrument, and a facade over everything the instrument means. It answers
what the device is, what an incoming MIDI message means, which drums it can
produce, and how it is drawn. Grid or kit becomes a property of the controller
rather than a fork in every consumer.

## What Changes

- **Introduce the Controller abstraction.** A single object owning the device's
  identity and metadata, its pads, its pedals, its transport bindings and its
  chosen drum kit — loaded and saved through itself, so no page parses stored
  configuration again.
- **Make it a facade over input.** One call turns a raw MIDI message into what
  it means: a hit with a resolved GM note, a pedal movement, a transport press,
  or nothing. Note mapping, hi-hat pedal state, bounce handling and transport
  matching all move behind it, replacing the map lookup, transport check and
  pedal handling that would otherwise be spread across the lesson page.
- **Give it one preview, reused everywhere.** `$lib/controller-preview.svelte`
  draws any controller from the controller itself — a grid as a grid, a profiled
  kit as its schematic — in three modes over the same geometry: **capture**
  during setup, **map** beside the chart on a resting lesson, and **play** at
  full size during a run when there is room for it. Hits flare, the pad awaiting
  capture pulses, a stateful hi-hat opens and closes with its pedal, and all of
  it stops under reduced motion. This absorbs `controller-map.svelte` and
  `pad-grid.svelte`, which draw pads today without knowing whose they are.
- **Keep a registry of configured controllers**, so a device chooser can say
  "Millenium MD-90 · 7 drums · last used yesterday" instead of repeating a raw
  MIDI port name.
- **Branch the wizard after the device step.** `matchPreset()` gains e-drum
  profiles alongside the existing grid presets. A matched kit routes straight
  into the drum flow with its schematic already on screen; the student can
  always say "not my kit" and pick another profile or the generic path. An
  unmatched device keeps today's grid flow, which stays untouched.
- **Ship predefined kit profiles**, each carrying a name, a **schematic SVG**
  whose drums are addressable by id, and a suggested drum role per pad.
  A profile never asserts MIDI notes: pad notes on these kits are reassignable
  from the module's own panel, so notes are always captured, exactly as
  `presets.ts` already argues for grid controllers.
- **Map drums on the schematic, not in a queue.** The wizard lights one drum at
  a time on the picture and records whatever note the student hits; the
  schematic fills in as they go. Any drum can be skipped and any one re-recorded
  without restarting.
- **Add a pedals step** that discovers how the kit's hi-hat actually behaves —
  two notes (open pad / closed pad), one note plus a stateful pedal, or no pedal
  at all — by asking for three specific gestures rather than assuming a wiring.
  The kick footswitch is captured as a drum like any other. The step is
  skippable and the whole flow works without it.
- **Add a test step**: free play against the schematic, every hit lighting its
  drum and naming it, so a swapped tom or an unmapped pad is visible before the
  first lesson rather than during it.
- **Add a generic flow** for kits with no profile: the student names the kit,
  says how many pads it has, and labels each one as it is captured. It produces
  the same saved layout a profile does — a custom kit is a first-class kit, not
  a degraded one.
- **Offer to share a custom layout.** After a generic setup the student may
  press one button to send the anonymised layout — model name, pad roles, notes,
  pedal behaviour — to a new insert-only Supabase table, so it can become a
  shipped profile. Explicitly opt-in, never automatic, and the setup is complete
  and saved whether or not they press it.
- **Resolve the hi-hat at hit time.** One hi-hat pad can score as closed (42) or
  open (46) depending on pedal position, resolved inside the controller before
  the hit is reported — so scoring, sample playback and highlighting all see one
  unambiguous note. Pedal traffic that is control rather than performance never
  becomes an extra hit.
- **Say when a kit cannot play a lesson.** A controller knows which drums it can
  produce, so a kit with no hi-hat pedal is told it cannot hit the open-hat
  notes before the run, rather than after.

Backwards compatible by construction: a controller of either kind still writes
the `notes` / `soundNotes` pair every existing reader uses, and adds its
structure alongside. Grid users get the same flow they have now, drawn by a new
component.

## Capabilities

### New Capabilities

- `controller`: the abstraction itself — identity and metadata, the facade that
  turns a MIDI message into a hit, a pedal movement or a transport press,
  pedal-aware hi-hat resolution, the capability query behind "your kit can't
  play this", and the single saved shape (with its mirror of the legacy
  `notes` / `soundNotes` pair) plus the registry of configured controllers.
- `controller-preview`: the one renderer — geometry taken from the controller,
  three modes (capture, map, play) over that same geometry, animated hit,
  capture and pedal feedback that stops under reduced motion, and its placement
  beside the chart and at full size during a run when there is room.
- `kit-profiles`: the catalogue of predefined electronic-kit profiles, the
  schematic SVG contract that makes a drum highlightable by id, the drum-role
  vocabulary, and the rule that a profile describes a model while a controller
  describes a student's instrument.
- `edrum-setup`: the wizard's second path — profile detection with an override,
  drum-by-drum capture on the schematic, the pedal-discovery step, the test
  step, and the generic flow for an unrecognised kit.
- `layout-sharing`: opt-in submission of a custom layout to an insert-only,
  unreadable-by-clients Supabase table, so unrecognised kits can become shipped
  profiles.

### Modified Capabilities

<!-- None. The four archived specs (user-auth, cloud-sync, quote-interstitial,
     quote-ratings) are untouched: layout sharing is a one-shot insert that does
     not join reconcile(), and works signed out. -->

## Impact

- **Affected code**
  - `src/routes/lessons/[id]/+page.svelte` — the biggest beneficiary.
    `loadDeviceMapping()` becomes a controller load; `handleMidi()` becomes one
    `controller.handle()` and a switch on what came back, retiring the separate
    `ctrlMap` lookup, `routeTransport()` call and `padCols` / `padRows` /
    `padDrums` triple.
  - `src/routes/onboarding/+page.svelte` — the `Step` union and rail become
    branch-dependent; the wizard builds and saves a controller rather than
    assembling a config literal.
  - `src/lib/presets.ts` — gains e-drum profiles beside the grid presets.
  - `src/lib/controller-map.svelte`, `src/lib/pad-grid.svelte` — both are
    absorbed into the one preview component.
  - `src/lib/transport-control.ts` — keeps parsing and labelling controls; the
    matching moves inside the controller.
  - `src/routes/debug/settings/+page.svelte` — hard-codes a 16-cell grid and
    would silently flatten an e-drum layout on save; it must refuse to.
- **New code**: `$lib/controller.svelte.ts` (the facade, its metadata and its
  registry), `$lib/controller-preview.svelte`, a kit-profile module, and a
  layout-submission call.
- **New assets**: one schematic SVG per profile under `static/kits/`, first-party
  only — they are inlined to be highlightable, so a submitted layout never
  becomes one.
- **New data**: a `device_layouts` table, insert-only, with no client-readable
  policy.
- **Docs**: `CLAUDE.md` and `AGENTS.md` both open with "Only finger drumming is
  supported". That stops being true here and both need rewording, along with the
  `/onboarding` and pad-config sections.
- **Privacy**: sharing is opt-in, one shot, and carries no practice history and
  no account requirement. Signed-in submissions record `auth.uid()`; signed-out
  ones record nothing identifying.
- **Curriculum**: unchanged. Every lesson is still written for finger drumming;
  this change lets a kit play them, it does not add e-drum lessons.
