// Supabase client configuration for optional cloud sync.
//
// Auth is optional: the app is fully usable signed-out and offline. So the URL
// and key come from *dynamic* public env — if they are unset the app still
// builds and runs, `supabaseConfigured` is false, and every sync/auth path
// no-ops. Only when both are present does any of it light up.
//
// The value in PUBLIC_SUPABASE_ANON_KEY is a publishable key (sb_publishable_…),
// which is browser-safe by design; the real boundary is row-level security.

import { env } from "$env/dynamic/public";
import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

export const SUPABASE_URL = env.PUBLIC_SUPABASE_URL ?? "";
export const SUPABASE_KEY = env.PUBLIC_SUPABASE_ANON_KEY ?? "";

/** True only when both env vars are present; gates every auth/sync entry point. */
export const supabaseConfigured = Boolean(SUPABASE_URL && SUPABASE_KEY);

/** The browser client, cookie-bound via @supabase/ssr. */
export function createBrowserSupabase(
  fetch: typeof globalThis.fetch,
): SupabaseClient {
  return createBrowserClient(SUPABASE_URL, SUPABASE_KEY, {
    global: { fetch },
  });
}
