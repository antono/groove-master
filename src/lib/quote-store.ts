// Device-local storage for the Quote of the Day: a user's like/dislike per
// quote, which quotes they've seen this cycle, and the "never show" opt-out.
//
// Mirrors progress-store.ts: localStorage under the `groove-master:` prefix,
// best-effort so private mode / no storage yields empty reads and silent writes.
// Ratings are the source of truth locally; sync.ts reconciles them with the
// cloud via the `unsyncedRatings` / `markRatingsSynced` helpers below, the same
// shape stats.ts exposes.

import { STORAGE_PREFIX } from "./config";

const RATINGS_KEY = STORAGE_PREFIX + "quote-ratings";
const SEEN_KEY = STORAGE_PREFIX + "quotes-seen";
const OFF_KEY = STORAGE_PREFIX + "quotes-off";

export type RatingValue = "like" | "dislike";

/** One quote's rating, shaped to map onto a `quote_ratings` cloud row. */
export type Rating = {
  value: RatingValue;
  /** Wall-clock ms of the last change — the clock for last-write-wins merges. */
  at: number;
  /** False until the sync engine has pushed this value to the cloud. */
  synced: boolean;
};

export type RatingMap = Record<string, Rating>;

// --- ratings ---------------------------------------------------------------

export function readRatings(): RatingMap {
  try {
    const raw = localStorage.getItem(RATINGS_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    if (!parsed || typeof parsed !== "object") return {};
    const out: RatingMap = {};
    for (const [id, r] of Object.entries(parsed as Record<string, unknown>)) {
      const rr = r as Partial<Rating>;
      if (rr && (rr.value === "like" || rr.value === "dislike")) {
        out[id] = {
          value: rr.value,
          at: typeof rr.at === "number" ? rr.at : 0,
          synced: Boolean(rr.synced),
        };
      }
    }
    return out;
  } catch {
    return {};
  }
}

function writeRatings(map: RatingMap): void {
  try {
    localStorage.setItem(RATINGS_KEY, JSON.stringify(map));
  } catch {
    // no storage — the rating just won't persist
  }
}

/** Record (or replace) a quote's rating; returns the stored value. */
export function setRating(id: string, value: RatingValue): Rating {
  const map = readRatings();
  const rating: Rating = { value, at: Date.now(), synced: false };
  map[id] = rating;
  writeRatings(map);
  return rating;
}

export function getRating(id: string): Rating | null {
  return readRatings()[id] ?? null;
}

// --- sync helpers (used by sync.ts) ----------------------------------------

/** Ratings not yet pushed to the cloud, keyed by quote id. */
export function unsyncedRatings(): Array<{ id: string } & Rating> {
  return Object.entries(readRatings())
    .filter(([, r]) => !r.synced)
    .map(([id, r]) => ({ id, ...r }));
}

/**
 * Fold cloud/merge results back in: set each id to the winning value and mark
 * it synced. A local value newer than what is passed is left untouched, so a
 * rating made mid-sync is not clobbered.
 */
export function applyRemoteRatings(
  rows: Array<{ id: string; value: RatingValue; at: number }>,
): void {
  const map = readRatings();
  for (const row of rows) {
    const local = map[row.id];
    if (!local || row.at >= local.at) {
      map[row.id] = { value: row.value, at: row.at, synced: true };
    }
  }
  writeRatings(map);
}

/** Mark the given quote ids as synced (their current local value reached the cloud). */
export function markRatingsSynced(ids: Iterable<string>): void {
  const map = readRatings();
  let touched = false;
  for (const id of ids) {
    if (map[id] && !map[id].synced) {
      map[id] = { ...map[id], synced: true };
      touched = true;
    }
  }
  if (touched) writeRatings(map);
}

// --- seen set --------------------------------------------------------------

export function readSeen(): Set<string> {
  try {
    const raw = localStorage.getItem(SEEN_KEY);
    const ids = raw ? JSON.parse(raw) : [];
    return new Set(
      Array.isArray(ids) ? ids.filter((i) => typeof i === "string") : [],
    );
  } catch {
    return new Set();
  }
}

function writeSeen(ids: Set<string>): void {
  try {
    localStorage.setItem(SEEN_KEY, JSON.stringify([...ids]));
  } catch {
    // no storage — seen set just won't persist
  }
}

export function markSeen(id: string): void {
  const seen = readSeen();
  seen.add(id);
  writeSeen(seen);
}

/** Start a fresh cycle — every quote is unseen again. */
export function resetSeen(): void {
  writeSeen(new Set());
}

// --- "never show" preference ----------------------------------------------

export function isQuotesOff(): boolean {
  try {
    return localStorage.getItem(OFF_KEY) === "1";
  } catch {
    return false;
  }
}

export function setQuotesOff(off: boolean): void {
  try {
    if (off) localStorage.setItem(OFF_KEY, "1");
    else localStorage.removeItem(OFF_KEY);
  } catch {
    // no storage — the opt-out just won't persist
  }
}
