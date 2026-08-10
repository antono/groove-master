// Offline-first sync between the device and Supabase.
//
// The local stores (localStorage progress + IndexedDB runs) stay the source of
// truth; this reconciles them with the cloud in the background. There is no
// separate outbox to keep consistent — the "pending" set is derived: progress is
// re-merged from localStorage each run, and a run is pending iff its
// `remoteSynced` flag is false. Reconcile is single-flight and best-effort: any
// failure leaves local state untouched and the pending set intact for next time.
//
// Merge rules (design.md Decision 6):
//   progress — max ceiling, union of unlocks, tier follows the higher ceiling
//   stats    — union by uuid, append-only, never updated
// Both are idempotent, so re-running changes nothing once converged.

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
    await syncProgress(supabase, user.id);
    await syncStats(supabase, user.id);
    syncState.status = "idle";
    syncState.lastSyncedAt = Date.now();
  } catch (err) {
    // Offline, transient error, or permission denied — keep local state and retry later.
    console.warn("[sync] reconcile failed", err);
    syncState.status = "error";
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

async function refreshPending(): Promise<void> {
  try {
    const unsynced = await unsyncedSessions();
    syncState.pending = unsynced.length;
  } catch {
    // ignore — pending count is advisory
  }
}
