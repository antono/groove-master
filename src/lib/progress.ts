// What a student has earned on a lesson, reconstructed from the practice log.
//
// The tempo ladder itself lives in /lessons/[id]: a lesson starts at its own base
// BPM and every rung above is BPM_STEP faster, each one earned by clearing the
// rung below without skipping a note. The player keeps its ceiling in
// localStorage because it builds the ladder during render and cannot wait on
// IndexedDB; the catalogue is under no such pressure and derives the same numbers
// from the run log, which is the record of what actually happened.

import type { SessionStat } from "./stats";

/** Rungs of the tempo ladder are this far apart. */
export const BPM_STEP = 10;

/** Finished without skipping a note — the run that opens the next rung. */
export function isCleanRun(run: { total: number; miss: number }): boolean {
  return run.total > 0 && run.miss === 0;
}

export type LessonProgress = {
  /** Runs finished without a skipped note. */
  cleared: number;
  /** Fastest rung the ladder allows, as far as the log can show. */
  maxBpm: number;
};

/**
 * Tally the run log per lesson.
 *
 * A rung can only be played once it is open, and clearing one opens the next — so
 * the ceiling is the higher of "fastest rung played" and "fastest rung cleared,
 * plus one". It can still read low against the player's own stored ceiling if the
 * history was cleared, which is the honest answer: this is what the log knows.
 *
 * Ids need no mapping here — allSessions canonicalises legacy ones on read.
 */
export function progressByLesson(
  runs: SessionStat[],
): Map<string, LessonProgress> {
  const out = new Map<string, LessonProgress>();
  for (const run of runs) {
    const seen = out.get(run.lesson) ?? { cleared: 0, maxBpm: 0 };
    const clean = isCleanRun(run);
    if (clean) seen.cleared++;
    seen.maxBpm = Math.max(seen.maxBpm, clean ? run.bpm + BPM_STEP : run.bpm);
    out.set(run.lesson, seen);
  }
  return out;
}
