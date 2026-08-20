# TODO

- Groove Extraction with: https://github.com/DamRsn/NeuralNote

(App-level task list also lives in [`docs/TODO.md`](docs/TODO.md) — worth merging
the two at some point.)

## From the audit of 20 August 2026

Found while writing Foundations stages 3–5. Ranked; each one has been reproduced.

### 1 · The match window is wider than the notes it scores

`MATCH_WINDOW_BEATS = 0.4` in `src/routes/lessons/[id]/+page.svelte:65`, but a
16th is 0.25 beats apart and an 8th-note triplet 0.33 — both inside it. A hit
binds to the nearest _unmatched_ target of the same pad, so one doubled hat in a
16th run claims the next note instead of counting as an extra, and the rest of
that lane's bar cascades one note forward. It degrades gracefully (everything
reads "off" rather than crashing) but it makes a sloppy 16th run score worse
than it played, across the whole of Vocabulary Stage 1.

Fix: clamp the window per target to half the distance to the nearest other note
on the same lane, rather than using one constant for every subdivision.

### 2 · /stats opens on a day that usually has no runs

`range = $state<Range>('day')` in `src/routes/stats/+page.svelte:396`, with
`selectedDay` set to today in `onMount`. Anyone who practised yesterday opens
the page to six zero tiles and four "No runs in this range yet" charts, directly
above a heatmap with a green square in it. The comment says "the page opens on
the session you just played" — true the one time it is right.

Fix: after `allSessions()` resolves, keep day mode only if today has runs;
otherwise fall back to `30d` (or to the most recent practised day).

### 3 · Two progression models disagree

The catalogue never gates a lesson — every card links. "Next lesson" on the
lesson page does: `nextUnlocked` needs a finished run at `NEXT_LESSON_BPM` (80),
which needs two clean runs first to climb the ladder from 60. So a student's
very first lesson ends on a disabled button whose tooltip asks for a tempo they
cannot select yet, and the only way forward is back through the stage list.

Decide which model is real and apply it in both places.

### 4 · Duplicated logic that can drift

- `readUnlockedSet()` (`src/lib/progress-store.ts:32`) is never imported; the
  lesson page reimplements it as `readUnlockedLessons()` at
  `src/routes/lessons/[id]/+page.svelte:916`. Same key, two readers.
- `tierLocked()` (`src/lib/catalogue.ts:120`) is never imported; `/lessons`
  inlines `roll.total === 0` at `src/routes/lessons/+page.svelte:64`.

### 5 · The service worker precache is all-or-nothing

`cache.addAll(PRECACHE)` in `src/service-worker.ts` covers everything Vite built
plus all of `static/` — which is now 62 lesson MIDIs and growing. `addAll`
rejects if a single request fails, the install fails with it, and the worker
never activates, so offline support disappears silently. Chunk the precache, or
add per-file tolerance and log what was skipped.

### 6 · The pad requirement widened a lot

18 of 62 lessons now need a pad beyond kick / snare / closed hat (12 crash, 9
open hat, 8 ride), up from 2 before Stage 4. The on-screen controller ships all
six, and `canPlay()` / `missing()` warns before a run, so nothing is broken —
but a sparsely-mapped kit now meets that warning far more often. Worth a look at
whether the wizard should nudge harder toward mapping a crash and a ride.

### 7 · Dead exports

`MOBILE_QUERY` and `MOBILE_BREAKPOINT_PX` (`src/lib/breakpoints.ts`) are unused
— nothing calls `matchMedia`; only CSS uses the 48rem literal, with a comment
pointing back at that file. Plus the two unused helpers in item 4.

### 8 · Cosmetic: 16ths read as a picket fence

`lesson-chart.svelte` sizes notes to the tightest subdivision and clamps at 4px,
so a 16th hat line on a catalogue card is a solid row of blocks. Legible on the
lesson page, mush on the card.
