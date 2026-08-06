## 1. Supabase project & schema

- [ ] 1.1 Provision the Supabase project and record `PUBLIC_SUPABASE_URL` / `PUBLIC_SUPABASE_ANON_KEY`
- [ ] 1.2 Add a migration creating `lesson_progress` (`user_id`, `lesson_id`, `max_bpm`, `tier`, `unlocked`, `updated_at`; PK `user_id, lesson_id`)
- [ ] 1.3 Add a migration creating `sessions` (`id` uuid PK, `user_id`, `at`, `day`, `lesson`, `lesson_name`, `bpm`, `device`, `device_id`, `stat` jsonb, `created_at`)
- [ ] 1.4 Add indexes `sessions(user_id, at)` and `sessions(user_id, day)`
- [ ] 1.5 Enable RLS and add owner-scoped policies (`auth.uid() = user_id`) for select/insert/update on both tables
- [ ] 1.6 Verify RLS: a user cannot read or write another user's rows, and unauthenticated access is denied

## 2. Auth integration (SSR)

- [ ] 2.1 Add `@supabase/supabase-js` and `@supabase/ssr`; add the public env vars to `.env`/`.env.example`
- [ ] 2.2 Create the browser client and server client factories
- [ ] 2.3 Add `hooks.server.ts` binding the server client to SvelteKit cookies and exposing `event.locals.supabase` + `safeGetSession()` (validate via `getUser()`)
- [ ] 2.4 Add root `+layout.server.ts` / `+layout.ts` to pass `{ session, user }` to pages and hydrate without a signed-out flash
- [ ] 2.5 Add the magic-link auth callback route and configure allowed redirect URLs in Supabase
- [ ] 2.6 Swap `@sveltejs/adapter-auto` for the concrete deploy adapter and wire env vars in the target

## 3. Auth UI

- [ ] 3.1 Add a session store reflecting `{ session, user }` and auth state changes
- [ ] 3.2 Add the sign-in form (email input + validation) that requests a magic link and confirms it was sent
- [ ] 3.3 Add signed-in display (user email) and a sign-out action that ends client + server session
- [ ] 3.4 Verify unauthenticated use is fully unchanged (lessons, playback, local progress/stats)

## 4. Local data model prep

- [ ] 4.1 Add a stable client-generated UUID `id` to new sessions at record time in `src/lib/stats.ts`
- [ ] 4.2 Implement an idempotent, run-once backfill assigning UUIDs to existing local sessions
- [ ] 4.3 Add an IndexedDB outbox store for pending progress upserts and new sessions

## 5. Sync engine (`src/lib/sync.ts`)

- [ ] 5.1 Enqueue outbox entries after local progress writes (lesson page) and stat writes (`stats.ts`) without blocking the local write
- [ ] 5.2 Implement single-flight `reconcile()` triggered on auth sign-in, `online`, after local writes, and a periodic backstop
- [ ] 5.3 Implement progress merge: `max_bpm = max`, `unlocked = OR`, `tier` from higher ceiling; upsert both directions; verify idempotence
- [ ] 5.4 Implement stats merge: union by `id`, upload only locally-new runs, insert remotely-new runs, never update existing
- [ ] 5.5 Implement first-login adoption: push existing local progress and runs into the account with no data loss
- [ ] 5.6 Ensure sync failures (offline/error/denied) leave the outbox intact and never disrupt playback

## 6. UI wiring

- [ ] 6.1 Point `src/routes/stats/+page.svelte` at the merged (local + remote) session set with no duplicates
- [ ] 6.2 Verify lesson unlock/ceiling reads reflect merged progress after sign-in
- [ ] 6.3 Add a lightweight sync-status indicator (pending / syncing / failed)

## 7. Verification

- [ ] 7.1 Sign in on a device with existing local data → data is adopted, nothing lost
- [ ] 7.2 Sign in on a fresh device → cloud progress and stats pull down
- [ ] 7.3 Record a run offline, then come online → it uploads exactly once (no duplicate in cloud or stats)
- [ ] 7.4 Cross-device: higher ceiling and union of unlocks win on both devices
- [ ] 7.5 `svelte-check` passes and SSR renders signed-out state cleanly
