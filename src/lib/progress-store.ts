// Read/write access to the earned-progress that /lessons/[id] keeps in
// localStorage, in one place so the sync engine and the lesson page agree on the
// exact keys:
//
//   groove-master:maxbpm:<lessonId>   number  — the BPM ceiling
//   groove-master:tier:<lessonId>     number  — last-selected rung
//   groove-master:lessons-unlocked    string[] — ids of lessons opened so far
//
// Every function is best-effort: no storage (private mode) yields empty reads
// and silent writes, mirroring the lesson page's own contract.

import { STORAGE_PREFIX } from "./config";

const maxBpmKey = (id: string) => STORAGE_PREFIX + "maxbpm:" + id;
const tierKey = (id: string) => STORAGE_PREFIX + "tier:" + id;
const LESSONS_KEY = STORAGE_PREFIX + "lessons-unlocked";

/** One lesson's earned progress, shaped like the `lesson_progress` cloud row. */
export type ProgressRow = {
  lesson_id: string;
  max_bpm: number;
  tier: number | null;
  unlocked: boolean;
};

function num(raw: string | null): number | null {
  if (raw == null) return null;
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? n : null;
}

export function readUnlockedSet(): Set<string> {
  try {
    const raw = localStorage.getItem(LESSONS_KEY);
    const ids = raw ? JSON.parse(raw) : [];
    return new Set(
      Array.isArray(ids) ? ids.filter((i) => typeof i === "string") : [],
    );
  } catch {
    return new Set();
  }
}

function writeUnlockedSet(ids: Set<string>): void {
  try {
    localStorage.setItem(LESSONS_KEY, JSON.stringify([...ids]));
  } catch {
    // no storage — the unlock set just won't persist
  }
}

/**
 * Every lesson the device knows any progress for: a maxbpm, a tier, or a place
 * in the unlocked set. Union of all three so nothing is dropped from a push.
 */
export function readLocalProgress(): ProgressRow[] {
  const unlocked = readUnlockedSet();
  const ids = new Set<string>(unlocked);
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key) continue;
      if (key.startsWith(STORAGE_PREFIX + "maxbpm:"))
        ids.add(key.slice((STORAGE_PREFIX + "maxbpm:").length));
      else if (key.startsWith(STORAGE_PREFIX + "tier:"))
        ids.add(key.slice((STORAGE_PREFIX + "tier:").length));
    }
  } catch {
    // no storage — fall back to whatever the unlocked set held
  }

  const rows: ProgressRow[] = [];
  for (const id of ids) {
    let max_bpm = 0;
    let tier: number | null = null;
    try {
      max_bpm = num(localStorage.getItem(maxBpmKey(id))) ?? 0;
      tier = num(localStorage.getItem(tierKey(id)));
    } catch {
      // ignore per-key read failure
    }
    rows.push({ lesson_id: id, max_bpm, tier, unlocked: unlocked.has(id) });
  }
  return rows;
}

/**
 * Fold merged rows back into localStorage: a ceiling only ever written when it
 * would rise, the unlocked set unioned, tier taken as given. Returns the ids
 * whose stored ceiling actually changed, so the caller can tell if anything moved.
 */
export function writeLocalProgress(rows: ProgressRow[]): void {
  const unlocked = readUnlockedSet();
  for (const row of rows) {
    try {
      const current = num(localStorage.getItem(maxBpmKey(row.lesson_id))) ?? 0;
      if (row.max_bpm > current)
        localStorage.setItem(maxBpmKey(row.lesson_id), String(row.max_bpm));
      if (row.tier != null && row.tier > 0)
        localStorage.setItem(tierKey(row.lesson_id), String(row.tier));
    } catch {
      // no storage — skip this row
    }
    if (row.unlocked) unlocked.add(row.lesson_id);
  }
  writeUnlockedSet(unlocked);
}

/** Merge two progress rows for the same lesson: max ceiling, union unlock. */
export function mergeProgress(a: ProgressRow, b: ProgressRow): ProgressRow {
  // tier follows the higher ceiling; ties keep whichever is non-null.
  const tier = a.max_bpm >= b.max_bpm ? (a.tier ?? b.tier) : (b.tier ?? a.tier);
  return {
    lesson_id: a.lesson_id,
    max_bpm: Math.max(a.max_bpm, b.max_bpm),
    tier,
    unlocked: a.unlocked || b.unlocked,
  };
}
