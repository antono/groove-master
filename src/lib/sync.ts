// Offline-first sync between the device and Supabase.
//
// The local stores stay the source of truth; this reconciles them with the cloud
// in the background. Reconcile is single-flight and best-effort.
//
// Sync-coverage rule: every dataset the app persists locally has a routine in the
// registry below, each with a merge strategy and a pull-back decision. Adding a
// locally-persisted dataset means adding its routine here.
//
//   dataset   local store        merge                    pull-back?
//   --------  -----------------  -----------------------  ----------
//   progress  localStorage       max ceiling, union       yes
//   stats     IndexedDB          append-only, dedup uuid  yes
//   ratings   localStorage       last-write-wins @updated yes
//   (controller config — a separate branch adds the next routine)
//
// All three merges are idempotent, so re-running changes nothing once converged.
// The routines run fault-isolated (Promise.allSettled): one failing — e.g. a
// table not yet provisioned — never aborts or hides the others.

import type { SupabaseClient } from "@supabase/supabase-js";
import { authState, syncState } from "./auth.svelte";
import {
  mergeProgress,
  readLocalProgress,
  writeLocalProgress,
  type ProgressRow,
} from "./progress-store";
import {
  insertRemoteSessions,
  localUuids,
  markSynced,
  unsyncedSessions,
  type SessionStat,
} from "./stats";
import {
  applyRemoteRatings,
  markRatingsSynced,
  readRatings,
  type RatingValue,
} from "./quote-store";

const PERIODIC_MS = 60_000;

let client: SupabaseClient | null = null;
let started = false;
let running = false;
let queued = false;

/** Wire up triggers once, from the browser layout. Safe to call repeatedly. */
export function startSync(supabase: SupabaseClient | null): void {
  client = supabase;
  if (!supabase || started || typeof window === "undefined") return;
  started = true;

  window.addEventListener("online", queueReconcile);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") queueReconcile();
  });
  // Periodic backstop, so a long-open tab still converges.
  setInterval(() => {
    if (navigator.onLine) queueReconcile();
  }, PERIODIC_MS);

  queueReconcile();
}

/** Ask for a reconcile. Coalesces while one is already in flight. */
export function queueReconcile(): void {
  void reconcile();
}

export async function reconcile(): Promise<void> {
  const supabase = client;
  const user = authState.user;

  if (!supabase || !user) {
    syncState.status = "disabled";
    return;
  }
  if (typeof navigator !== "undefined" && !navigator.onLine) {
    syncState.status = "offline";
    return;
  }
  if (running) {
    queued = true; // fold this request into the in-flight run
    return;
  }

  running = true;
  syncState.status = "syncing";
  try {
    // Each dataset syncs independently: one failing (e.g. a table not yet
    // provisioned, a transient error, a permission denial) must neither abort nor
    // hide the others, and the ones that succeed keep their results. Concurrent
    // is safe — disjoint tables/stores, one shared client that multiplexes.
    const routines: Array<[string, Promise<void>]> = [
      ["progress", syncProgress(supabase, user.id)],
      ["stats", syncStats(supabase, user.id)],
      ["ratings", syncRatings(supabase, user.id)],
    ];
    const results = await Promise.allSettled(routines.map(([, p]) => p));
    const failed = results
      .map((r, i) =>
        r.status === "rejected" ? [routines[i][0], r.reason] : null,
      )
      .filter((x): x is [string, unknown] => x !== null);

    if (failed.length > 0) {
      for (const [name, reason] of failed)
        console.warn(`[sync] ${name} failed`, reason);
      syncState.status = "error";
    } else {
      syncState.status = "idle";
    }
    syncState.lastSyncedAt = Date.now();
  } finally {
    running = false;
    await refreshPending();
    if (queued) {
      queued = false;
      void reconcile();
    }
  }
}

async function syncProgress(
  supabase: SupabaseClient,
  userId: string,
): Promise<void> {
  const local = readLocalProgress();
  const { data, error } = await supabase
    .from("lesson_progress")
    .select("lesson_id, max_bpm, tier, unlocked");
  if (error) throw error;

  const remote: ProgressRow[] = (data ?? []).map((r) => ({
    lesson_id: r.lesson_id as string,
    max_bpm: (r.max_bpm as number) ?? 0,
    tier: (r.tier as number | null) ?? null,
    unlocked: Boolean(r.unlocked),
  }));

  const byId = new Map<string, ProgressRow>();
  for (const row of [...local, ...remote]) {
    const prev = byId.get(row.lesson_id);
    byId.set(row.lesson_id, prev ? mergeProgress(prev, row) : row);
  }
  const merged = [...byId.values()];

  // Fold the merge back into localStorage (rises only; unions unlocks).
  writeLocalProgress(merged);

  // Push only rows that differ from what the cloud already holds.
  const remoteById = new Map(remote.map((r) => [r.lesson_id, r]));
  const changed = merged.filter((m) => {
    const r = remoteById.get(m.lesson_id);
    return (
      !r ||
      r.max_bpm !== m.max_bpm ||
      (r.tier ?? null) !== (m.tier ?? null) ||
      r.unlocked !== m.unlocked
    );
  });
  if (changed.length > 0) {
    const rows = changed.map((m) => ({
      user_id: userId,
      lesson_id: m.lesson_id,
      max_bpm: m.max_bpm,
      tier: m.tier,
      unlocked: m.unlocked,
      updated_at: new Date().toISOString(),
    }));
    const { error: upErr } = await supabase
      .from("lesson_progress")
      .upsert(rows, { onConflict: "user_id,lesson_id" });
    if (upErr) throw upErr;
  }
}

async function syncStats(
  supabase: SupabaseClient,
  userId: string,
): Promise<void> {
  const { data, error } = await supabase
    .from("sessions")
    .select("id, stat")
    .order("at", { ascending: true });
  if (error) throw error;

  const have = await localUuids();
  const remoteIds = new Set<string>();
  const incoming: SessionStat[] = [];
  for (const r of data ?? []) {
    const id = r.id as string;
    remoteIds.add(id);
    if (!have.has(id)) {
      const stat = r.stat as SessionStat;
      incoming.push({ ...stat, uuid: id, remoteSynced: true });
    }
  }
  // Pull: insert runs this device has never seen.
  await insertRemoteSessions(incoming);

  // Push: local runs whose uuid the cloud does not yet have.
  const unsynced = await unsyncedSessions();
  const toPush = unsynced.filter((s) => s.uuid && !remoteIds.has(s.uuid));
  if (toPush.length > 0) {
    const rows = toPush.map((s) => {
      // Strip local-only bookkeeping from the stored payload.
      const { id: _id, remoteSynced: _sy, ...clean } = s;
      void _id;
      void _sy;
      return {
        id: s.uuid!,
        user_id: userId,
        at: s.at,
        day: s.day,
        lesson: s.lesson,
        lesson_name: s.lessonName,
        bpm: s.bpm,
        device: s.device,
        device_id: s.deviceId,
        stat: clean,
      };
    });
    const { error: insErr } = await supabase.from("sessions").insert(rows);
    if (insErr) throw insErr;
  }

  // Everything now in the cloud (just-pushed or already there) is synced locally.
  const syncedNow = new Set<string>();
  for (const s of unsynced) {
    if (s.uuid && remoteIds.has(s.uuid)) syncedNow.add(s.uuid);
  }
  for (const p of toPush) if (p.uuid) syncedNow.add(p.uuid);
  await markSynced(syncedNow);
}

async function syncRatings(
  supabase: SupabaseClient,
  userId: string,
): Promise<void> {
  const { data, error } = await supabase
    .from("quote_ratings")
    .select("quote_id, value, updated_at");
  if (error) throw error;

  // Remote ratings keyed by quote id, with updated_at as the LWW clock.
  const remote = new Map<string, { value: RatingValue; at: number }>();
  for (const r of data ?? []) {
    remote.set(r.quote_id as string, {
      value: r.value as RatingValue,
      at: Date.parse(r.updated_at as string),
    });
  }

  // Pull: any remote value at least as new as the local one wins locally.
  applyRemoteRatings([...remote.entries()].map(([id, r]) => ({ id, ...r })));

  // Push: local ratings the cloud is missing or that are strictly newer.
  // First sign-in adoption is the same path — local ratings are all "newer"
  // than a cloud that has none. Preserve each local `at` as updated_at so the
  // LWW clock survives the round-trip and the merge stays idempotent.
  const local = readRatings();
  const toPush = Object.entries(local).filter(([id, r]) => {
    const rem = remote.get(id);
    return !rem || r.at > rem.at;
  });
  if (toPush.length > 0) {
    const rows = toPush.map(([id, r]) => ({
      user_id: userId,
      quote_id: id,
      value: r.value,
      updated_at: new Date(r.at).toISOString(),
    }));
    const { error: upErr } = await supabase
      .from("quote_ratings")
      .upsert(rows, { onConflict: "user_id,quote_id" });
    if (upErr) throw upErr;
    markRatingsSynced(toPush.map(([id]) => id));
  }
}

async function refreshPending(): Promise<void> {
  try {
    const unsynced = await unsyncedSessions();
    syncState.pending = unsynced.length;
  } catch {
    // ignore — pending count is advisory
  }
}
