## 1. Supabase project & schema

- [x] 1.1 Provision the Supabase project and record `PUBLIC_SUPABASE_URL` / `PUBLIC_SUPABASE_ANON_KEY`
- [x] 1.2 Add a migration creating `lesson_progress` (`user_id`, `lesson_id`, `max_bpm`, `tier`, `unlocked`, `updated_at`; PK `user_id, lesson_id`)
- [x] 1.3 Add a migration creating `sessions` (`id` uuid PK, `user_id`, `at`, `day`, `lesson`, `lesson_name`, `bpm`, `device`, `device_id`, `stat` jsonb, `created_at`)
- [x] 1.4 Add indexes `sessions(user_id, at)` and `sessions(user_id, day)`
- [x] 1.5 Enable RLS and add owner-scoped policies (`auth.uid() = user_id`) for select/insert on both tables; update on `lesson_progress` only (`sessions` is append-only)
- [x] 1.6 Verify RLS: policies are owner-scoped `TO authenticated`, `sessions` has no update/delete policy, and anon has no policy (deny-by-default)

## 2. Auth integration (SSR)

- [x] 2.1 Add `@supabase/supabase-js` and `@supabase/ssr`; add the public env vars to `.env`/`.env.example`
- [x] 2.2 Create the browser client and server client factories (`$lib/supabase.ts` browser factory + inline server client in hooks/`+layout.ts` per the @supabase/ssr idiom)
- [x] 2.3 Add `hooks.server.ts` binding the server client to SvelteKit cookies and exposing `event.locals.supabase` + `safeGetSession()` (validate via `getUser()`)
- [x] 2.4 Add root `+layout.server.ts` / `+layout.ts` to pass `{ session, user }` to pages and hydrate without a signed-out flash
- [x] 2.5 Add the magic-link auth callback route (`/auth/confirm`, handles PKCE `code` and `token_hash`); redirect-URL allowlist documented in `supabase/SETUP.md` (dashboard-only, not scriptable via MCP)
- [x] 2.6 Swap `@sveltejs/adapter-auto` for `@sveltejs/adapter-vercel`; env wiring documented in `supabase/SETUP.md`

## 3. Auth UI

- [x] 3.1 Add a session store reflecting `{ session, user }` and auth state changes (`$lib/auth.svelte.ts` + `onAuthStateChange` wiring in `+layout.svelte`)
- [x] 3.2 Add the sign-in form (email input + validation) that requests a magic link and confirms it was sent (`/account`)
- [x] 3.3 Add signed-in display (user email) and a sign-out action that ends client + server session
- [x] 3.4 Verify unauthenticated use is fully unchanged (SSR renders signed-out; `supabaseConfigured=false` path no-ops all sync/auth) — routes 200 in preview

## 4. Local data model prep

- [x] 4.1 Add a stable client-generated UUID (`uuid`) to new sessions at record time in `src/lib/stats.ts`
- [x] 4.2 Implement an idempotent, run-once backfill assigning UUIDs to existing local sessions (IndexedDB v1→v2 `onupgradeneeded` cursor backfill)
- [x] 4.3 Outbox for pending changes — implemented as the derived pending set (`remoteSynced=false` runs + re-merged localStorage progress) rather than a second store to keep consistent; a deliberate simplification, noted in `sync.ts`

## 5. Sync engine (`src/lib/sync.ts`)

- [x] 5.1 Trigger sync after local progress/stat writes (lesson page `queueReconcile()` post-record) without blocking the local write
- [x] 5.2 Implement single-flight `reconcile()` triggered on auth sign-in, `online`, `visibilitychange`, after local writes, and a 60s periodic backstop
- [x] 5.3 Implement progress merge: `max_bpm = max`, `unlocked = OR`, `tier` from higher ceiling; upsert both directions; idempotent by construction
- [x] 5.4 Implement stats merge: union by `uuid`, upload only locally-new runs, insert remotely-new runs, never update existing
- [x] 5.5 Implement first-login adoption: push existing local progress and runs into the account (unsynced runs + full localStorage snapshot pushed on first reconcile)
- [x] 5.6 Ensure sync failures (offline/error/denied) leave pending state intact and never disrupt playback (try/catch → `error` status, local state untouched)

## 6. UI wiring

- [x] 6.1 Point `src/routes/stats/+page.svelte` at the merged set — signed-in mount awaits `reconcile()` (which pulls remote runs into IndexedDB, deduped by uuid) then re-reads `allSessions()`
- [x] 6.2 Lesson unlock/ceiling reads reflect merged progress after sign-in — sync writes the same localStorage keys the ladder reads, so merged progress shows on next lesson load
- [x] 6.3 Add a lightweight sync-status indicator (`$lib/sync-badge.svelte` in the header: synced / pending / syncing / offline / failed)

## 7. Verification

- [x] 7.5 `svelte-check` passes (0 errors/0 warnings), `pnpm build` succeeds with adapter-vercel, and SSR renders the signed-out state cleanly (`/`, `/account`, `/lessons`, `/stats`, `/auth/error` all 200 in preview)

Manual E2E below needs a live magic-link email + a real signed-in session (and, for 7.4, two devices), so they can't be driven headlessly. Code is complete and unit/build-verified; run these once after the dashboard redirect-URL setup in `supabase/SETUP.md`:

- [ ] 7.1 Sign in on a device with existing local data → data is adopted, nothing lost
- [ ] 7.2 Sign in on a fresh device → cloud progress and stats pull down
- [ ] 7.3 Record a run offline, then come online → it uploads exactly once (no duplicate in cloud or stats)
- [ ] 7.4 Cross-device: higher ceiling and union of unlocks win on both devices
