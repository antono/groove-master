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
- **Some GM notes have no key zone in the .sf2**, and fluidsynth renders those as
  five seconds of silence while still exiting 0 — a pad that decodes fine and
  plays nothing. So the script audits every render and fills silent ones from its
  `FALLBACKS` table (a stand-in from another kit, or a neighbour note resampled
  with ffmpeg); it exits non-zero if any file is still silent. Currently notes 39
  (kits 7-12), 47 and 68 are covered this way.
  - `audit-samples` (`--audit`) lists silent samples — no SoundFont needed.
  - `repair-samples` (`--repair`) substitutes them in place; needs ffmpeg, but
    still no SoundFont, so the shipped assets can be fixed without the 244 MB .sf2.
- Sample levels in this SoundFont are uneven (-33 to -7.5 dBFS across a kit), so
  when choosing a stand-in, match the level of its neighbours on the grid, not
  just the nearest pitch.
- The grid uses two mappings: **controller note → cell** (Capture) and
  **cell → GM drum note** (per-cell dropdown). Both are saved per device in
  `localStorage`.

## Sample caching

- `src/service-worker.ts` caches `**/*.oga` cache-first, so samples are kept on
  the user's machine and a kit switch is instant after the first visit. The audio
  is _not_ precached (~10 MB); `serviceWorker.files` in `vite.config.ts` keeps it
  out of the `$service-worker` manifest.
- `warmKit()` in `$lib/drums.ts` pulls the saved kit (~700 KB) into that cache
  from `+layout.svelte` on idle, skipping anything already stored. It waits for
  the worker to control the page first — on a first visit the document loads
  before the worker exists, and fetches made before `clients.claim()` bypass it
  and are downloaded for nothing.
- Samples live at stable URLs, so a re-render only reaches people when the
  version-keyed cache is replaced on activate. Verify with
  `pnpm build && pnpm preview`; in dev `build` is empty so only the runtime
  audio caching is exercised.

## Lessons

- `python3 scripts/make-lessons.py` writes the lesson MIDIs (`lesson-<id>.mid`)
  and `static/lessons/manifest.json`. The curriculum is the `LESSONS` table in
  that script; each entry needs `id`, `name`, `bpm`, `bars`, drum/bass pattern
  builders, a one-line `summary` (catalogue card), a longer `description`, and
  `hints` — the practice tips listed under the schematic.
- Hints must not tell the student to change tempo: BPM is fixed per lesson and
  only overridable via `?bpm=`.
- **Every lesson counts in**: three side-stick clicks on the last three beats of
  the lead-in bar, with the pattern's first beat left silent for the student. It
  ships as a `count-in` track in each MIDI, written in the lead-in bar the
  highway already had; `parseMidi` shifts it to beats -3, -2, -1 and keeps it out
  of the lanes, the chart and the scoring. `build_lesson` adds it to every
  lesson, so new entries get it for free. Play counts in; Listen skips it.

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
