# padrill

A browser-based finger drumming trainer. Play along with interactive lessons to
build finger drumming skills, all in HTML — no native app required. Only finger
drumming is supported.

## Stack

- SvelteKit (Svelte 5) + TypeScript
- Vite

## Routes

- `/lessons` — catalogue: one card per lesson (summary + pattern schematic). The
  schematic is `$lib/lesson-chart.svelte`, rendered from the lesson's own MIDI so
  it can't drift from what the highway plays.
- `/lessons/[id]` — one lesson. At rest the page is always brief → schematic +
  **Listen** → practice hints → **Play**; the scrolling highway only exists during
  a run, so finishing a lesson returns to the same page it started from.
  - **Listen** previews the lesson in place: drums and backing play off the audio
    clock with a playhead sweeping the schematic, nothing scored, no highway.
  - **Play** is the scored run — fullscreen highway, only the student's own hits
    make drum sounds, result report at the end.
  - Sound and Web MIDI come up on the first Play/Listen click (browsers need a
    gesture). MIDI access is never awaited: the permission prompt can stay pending
    indefinitely and must not hold up playback.
  - `?bpm=<40..240>` overrides the manifest tempo, e.g. `/lessons/1.2?bpm=90`.
    There is no in-page tempo control; the effective BPM is shown next to Play and
    in the transport HUD.
- `/settings` — pad grid, device mapping, kit choice. `/onboarding` — setup wizard.

## Drum samples

- `soundfonts/Perfect_Drums.sf2` holds 12 GM-percussion kits (244 MB, not shipped
  to the browser).
- `python3 scripts/render-drums.py` pre-renders each kit's drums to
  `static/drums/kit<N>/<note>.oga` plus `static/drums/manifest.json`
  (kits + drum catalogue). Re-run after changing the SoundFont or layout.
- The grid uses two mappings: **controller note → cell** (Capture) and
  **cell → GM drum note** (per-cell dropdown). Both are saved per device in
  `localStorage`.

## Lessons

- `python3 scripts/make-lessons.py` writes the lesson MIDIs (`lesson-<id>.mid`)
  and `static/lessons/manifest.json`. The curriculum is the `LESSONS` table in
  that script; each entry needs `id`, `name`, `bpm`, `bars`, drum/bass pattern
  builders, a one-line `summary` (catalogue card), a longer `description`, and
  `hints` — the practice tips listed under the schematic.
- Hints must not tell the student to change tempo: BPM is fixed per lesson and
  only overridable via `?bpm=`.

## Bass samples (backing track)

- Three CC0 (public-domain) FreePats basses live in `soundfonts/`
  (`LatelyBass.sf2`, `SynthBass1.sf2`, `SynthBass2.sf2`).
- `python3 scripts/render-bass.py` renders notes E1–C4 (MIDI 28–60) to
  `static/bass/<id>/<note>.oga` plus `static/bass/manifest.json`.
- **Any SoundFont whose samples are shipped must be credited in `THANKS.md`**
  (name, samples taken, license, authors).

## Commands

- `pnpm dev` — start dev server
- `pnpm build` — production build
- `pnpm preview` — preview the production build
- `pnpm check` — type-check with svelte-check
