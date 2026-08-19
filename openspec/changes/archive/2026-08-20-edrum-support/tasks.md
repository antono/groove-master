## 1. The Controller

- [x] 1.1 Write `src/lib/controller.svelte.ts`: the `Controller` class with its
      identity and metadata, the `Pad` and `Geometry` types, and the
      `ControllerEvent` union. Runes-bearing, like `MidiHub`, so the preview can
      read pedal and hit state reactively.
- [x] 1.2 Implement `load()` / `save()` / `list()` as the only readers and
      writers of the stored configuration, non-throwing on blocked storage, and
      move the shape documentation out of `src/lib/config.ts` into the class.
- [x] 1.3 Build a grid controller from a legacy config — synthesised pads,
      positional labels, grid geometry — so a config saved before this change
      loads with no migration and behaves identically.
- [x] 1.4 Implement `handle()`: transport matching (moved in from the lesson
      page's `routeTransport`), note-on mapping, bounce handling, and the
      `none` result for anything unrecognised.
- [x] 1.5 Implement pedal handling inside `handle()` — pedal messages leave as
      `pedal` and never as `hit`, and a stateful hi-hat resolves to the closed or
      open note from the tracked position before the hit is reported.
- [x] 1.6 Implement `drums` and `canPlay()` over the pads and hi-hat mode.

## 2. The preview

- [x] 2.1 Write `src/lib/controller-preview.svelte`: geometry from
      `controller.geometry`, the three modes, and a text description that does
      not depend on animation.
- [x] 2.2 Port `controller-map.svelte` in as the `map` mode — family hues, named
      lesson drums, blank unused pads, the lit flare — then delete it and repoint
      `/lessons/[id]`.
- [x] 2.3 Port `pad-grid.svelte` in as the `capture` mode verbatim — pending /
      current / done states, note labels, the neumorphic pad surface, the pulse,
      click-to-audition — then delete it and repoint `/onboarding`.
- [x] 2.4 Render a schematic geometry: fetch and inline the profile's SVG, mark
      drums by id, and fall back to the neutral arrangement when there is none.
      First-party assets only.
- [x] 2.5 Add the hi-hat open/closed animation driven by `controller.hihat`, and
      confirm every animation in all three modes stops under
      `prefers-reduced-motion` while the state stays readable.
- [x] 2.6 Add the `play` mode and its placement: highway sized first, preview
      takes what remains at the largest size that fits, omitted when nothing
      remains, and no layout reads or writes during a run.

## 3. Kit profiles and schematics

- [x] 3.1 Add the drum-role vocabulary and the `KitProfile` / `KitPad` types
      beside the existing grid presets in `src/lib/presets.ts`, and widen the
      device lookup so one call answers "grid preset, kit profile, or neither".
- [x] 3.2 Draw `static/kits/millenium-md-90.svg` from the product photos — seven
      pads in their real positions, each drum a `<g>` whose id matches its pad —
      flat, unstyled and theme-neutral so the preview owns colour.
- [x] 3.3 Write the `millenium-md-90` profile: label, name pattern, schematic
      path, and the seven pads (snare, three toms, hi-hat, crash, ride) with
      suggested GM sounds and no notes, plus the kick and hi-hat pedal entries.
- [x] 3.4 Add a build-time check that every pad id in every profile exists in
      that profile's SVG, and fail the build when it does not.

## 4. The drum setup path

- [x] 4.1 Rework `/onboarding` to build and save a `Controller` rather than
      assembling a config literal, with the grid path's behaviour unchanged.
- [x] 4.2 Split the wizard's `Step` union into two ordered paths sharing
      `connect` and `device`, and render the rail from the active path.
- [x] 4.3 Build the kit step: detected profile with its preview and name, a
      "not my kit" escape into the profile list, and the generic entry.
- [x] 4.4 Build drum capture in `capture` mode on the schematic — highlight one
      drum, record the next distinct note, and support skip, re-record and
      restart without leaving the step.
- [x] 4.5 Build the pedals step: the three gestures, the two-note / stateful /
      none classification with two-note preferred, kick capture, and a skip that
      still leaves a working setup.
- [x] 4.6 Build the test step: free play lighting drums by name, unmapped hits
      reported rather than swallowed, and direct returns to capture and pedals.
- [x] 4.7 Build the generic path: kit name, pad count, per-pad label and role,
      the neutral arrangement, and the same pedals and test steps.
- [x] 4.8 Extend the `onboardingStep` analytics events to cover the new steps so
      the drop-off on the drum path is measurable.

## 5. Playing through the Controller

- [x] 5.1 Replace `loadDeviceMapping()` in `src/routes/lessons/[id]/+page.svelte`
      with a controller load, retiring `ctrlMap`, `padCols`, `padRows`,
      `padDrums` and `savedDeviceName`.
- [x] 5.2 Reduce `handleMidi()` to `controller.handle()` plus a switch, leaving
      `registerHit`, `flash` and sample playback untouched below it.
- [x] 5.3 Show the preview in `map` mode on the resting page and `play` mode
      during a run.
- [x] 5.4 Add the playability check: compare the lesson's notes against
      `controller.drums` and state any gap on the resting page, leaving Play
      available and scoring unchanged.
- [x] 5.5 Use `Controller.list()` in the device chooser so a configured
      controller is named and described rather than shown as a raw port name.
- [x] 5.6 Make `/debug/settings` refuse to save over an e-drum controller — it
      hard-codes sixteen cells and would flatten one. Show what the controller is
      and point at `/onboarding` instead.

## 6. Layout sharing

- [x] 6.1 Write the `device_layouts` migration: insert-only for `anon` and
      `authenticated`, no select policy for either, nullable `user_id`, and size
      bounds on `device_name` and `layout`.
- [x] 6.2 Add the submission call and wire the opt-in offer into the end of the
      generic path — stating what is sent, offered once, failing quietly.

## 7. Verification and docs

- [ ] 7.1 Walk the whole drum path on the real MD-90: capture, all three pedal
      outcomes (pedal connected, pedal absent, pedal mid-gesture), the test step,
      then a scored lesson with open and closed hi-hats.
- [x] 7.2 Walk the grid path end to end on a grid controller and play a lesson —
      the ported capture mode is the risk here, so verify it directly rather than
      inferring it from the kit path.
- [x] 7.3 Confirm a config saved before this change loads, plays and scores
      untouched, and that nothing rewrites it on read.
- [x] 7.4 Check the preview during a run: appears when there is room, is omitted
      when there is not, never resizes the highway, and does not cost frames.
- [x] 7.5 `pnpm check` and `pnpm build` clean.
- [x] 7.6 Rewrite the "Only finger drumming is supported" opening in `CLAUDE.md`
      and `AGENTS.md`, and replace the `/onboarding` and pad-config sections with
      the Controller.
- [ ] 7.7 Add the release's changelog entry and news post, with a screenshot of
      the kit preview mid-capture and one of the preview beside a lesson chart.
