// Shared reactive auth + sync state, set from the root layout and read by the UI
// (account page, sync indicator) and the sync engine. Kept tiny on purpose: the
// source of truth for the session is the Supabase client; this just mirrors it
// into runes so components re-render on sign-in/out.

import type { Session, User } from "@supabase/supabase-js";

export const authState = $state<{
  user: User | null;
  session: Session | null;
  /** True once the layout has resolved the initial auth state. */
  ready: boolean;
}>({
  user: null,
  session: null,
  ready: false,
});

export type SyncStatus = "disabled" | "idle" | "syncing" | "error" | "offline";

export const syncState = $state<{
  status: SyncStatus;
  lastSyncedAt: number | null;
  /** Local changes waiting to reach the cloud (unsynced runs + progress). */
  pending: number;
}>({
  status: "disabled",
  lastSyncedAt: null,
  pending: 0,
});
