// Practice history, kept in IndexedDB.
//
//   groove-master / sessions   one record per scored lesson run, keyed by autoIncrement
//                        id, indexed on `at` (finish time) and `lesson`.
//
// The pad configuration lives in localStorage (see config.ts), but a practice log
// grows without bound and carries per-lane detail, so it wants a real store with
// an index to scan in time order rather than a JSON blob that has to be parsed
// whole on every write.
//
// Everything here is best-effort. A browser with no IndexedDB — private mode,
// storage blocked by the user — must still play lessons, it just records nothing,
// so no call rejects: writes resolve silently and reads resolve empty.

export const DB_NAME = "groove-master";
const DB_VERSION = 1;
const STORE = "sessions";

/** Per-pad accuracy for one run, as shown in the lesson's result table. */
export type LaneStat = {
  note: number;
  name: string;
  total: number;
  hits: number;
  avgMs: number;
};

/** One completed lesson run. Mirrors the lesson page's result report. */
export type SessionStat = {
  id?: number; // assigned by the store on write
  at: number; // epoch ms, when the run finished
  /**
   * Local calendar day, `YYYY-MM-DD`. Stored rather than derived on read: the
   * heatmap buckets by the day the student experienced, and a run finished at
   * 00:30 local is the previous day in UTC.
   */
  day: string;
  lesson: string; // lesson id, e.g. "1.2"
  lessonName: string;
  bpm: number; // the tempo actually played, slider/?bpm= included

  /**
   * The controller the run was played on: the live Web MIDI port name, falling
   * back to the name saved with the device mapping. `null` when no input was
   * connected — the run still scores, it just has no hits to score.
   */
  device: string | null;
  /**
   * Web MIDI port id for that controller. Stored alongside the name because it
   * is what config.ts keys the pad mapping on, and because port *names* are not
   * stable across operating systems — grouping by id survives what grouping by
   * name would split.
   */
  deviceId: string | null;

  // note stats
  total: number;
  hits: number;
  perfect: number;
  good: number;
  off: number;
  miss: number;
  extra: number;
  accuracy: number; // hits / total, 0..1

  // ms stats
  avgAbsMs: number; // mean |timing error| over the notes that were hit
  early: number;
  late: number;

  /**
   * Milliseconds played — the transport time of the run, count-in included.
   *
   * Derived from the run's length in beats at its BPM rather than measured off
   * the wall clock, so a pause mid-lesson does not get banked as practice time.
   * A run that is abandoned never reaches the result screen and is never
   * recorded, so every stored duration is a lesson played end to end.
   */
  durationMs: number;

  grade: string;
  lanes: LaneStat[];
};

/** Local calendar day of a timestamp, as `YYYY-MM-DD`. */
export function dayKey(when: number | Date): string {
  const d = typeof when === "number" ? new Date(when) : when;
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}

// One connection per page, opened lazily on first use. Cached as the promise, not
// the database, so concurrent callers share a single open request.
let dbPromise: Promise<IDBDatabase | null> | null = null;

function openDb(): Promise<IDBDatabase | null> {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve) => {
    if (typeof indexedDB === "undefined") return resolve(null);
    let req: IDBOpenDBRequest;
    try {
      req = indexedDB.open(DB_NAME, DB_VERSION);
    } catch {
      // Firefox throws here instead of erroring the request when storage is off.
      return resolve(null);
    }
    req.onupgradeneeded = () => {
      const db = req.result;
      if (db.objectStoreNames.contains(STORE)) return;
      const store = db.createObjectStore(STORE, {
        keyPath: "id",
        autoIncrement: true,
      });
      store.createIndex("at", "at");
      store.createIndex("lesson", "lesson");
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => resolve(null);
    // No `onblocked`: it can only fire on a version change, and at version 1
    // there is no older connection to be blocked by. Bumping DB_VERSION means
    // adding one here, or a second tab wedges this promise forever.
  });
  return dbPromise;
}

/**
 * Append a finished run to the history. Never throws — the caller is on the path
 * that shows the result screen, and a storage failure must not interrupt it.
 */
export async function recordSession(stat: SessionStat): Promise<void> {
  const db = await openDb();
  if (!db) return;
  await new Promise<void>((resolve) => {
    let tx: IDBTransaction;
    try {
      tx = db.transaction(STORE, "readwrite");
    } catch {
      return resolve();
    }
    tx.objectStore(STORE).add(stat);
    tx.oncomplete = () => resolve();
    tx.onerror = () => resolve();
    tx.onabort = () => resolve();
  });
}

// A lesson's id used to be its number ("1.2"), so it changed whenever the
// curriculum was reordered. Ids are slugs now and never change, but runs
// recorded before that carry the old number — mapped here on read so a
// student's history stays attached to the lesson they actually played.
//
// Reading only: nothing new is ever written under a legacy id, and the stored
// `lessonName` already renders correctly, so this only matters for grouping.
const LEGACY_IDS: Record<string, string> = {
  "1.1": "kick-quarters",
  "1.2": "kick-hats-unison",
  "2.1": "four-on-the-floor",
  "2.2": "disco-open-hats",
  "3.1": "paradiddle-single",
};

/** The current slug for a lesson id, which for anything recent is itself. */
export function canonicalLesson(id: string): string {
  return LEGACY_IDS[id] ?? id;
}

/** Every recorded run, oldest first (the `at` index supplies the ordering). */
export async function allSessions(): Promise<SessionStat[]> {
  const db = await openDb();
  if (!db) return [];
  return new Promise((resolve) => {
    let tx: IDBTransaction;
    try {
      tx = db.transaction(STORE, "readonly");
    } catch {
      return resolve([]);
    }
    const req = tx.objectStore(STORE).index("at").getAll();
    req.onsuccess = () => {
      const rows = (req.result as SessionStat[]) ?? [];
      resolve(rows.map((r) => ({ ...r, lesson: canonicalLesson(r.lesson) })));
    };
    req.onerror = () => resolve([]);
    tx.onabort = () => resolve([]);
  });
}

/** Wipe the practice history. Used by the "Clear history" action on /stats. */
export async function clearSessions(): Promise<void> {
  const db = await openDb();
  if (!db) return;
  await new Promise<void>((resolve) => {
    let tx: IDBTransaction;
    try {
      tx = db.transaction(STORE, "readwrite");
    } catch {
      return resolve();
    }
    tx.objectStore(STORE).clear();
    tx.oncomplete = () => resolve();
    tx.onerror = () => resolve();
    tx.onabort = () => resolve();
  });
}
