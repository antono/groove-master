## Why

Today all user data lives only on the device: lesson progress in `localStorage`
(`groove-master:lessons-unlocked`, `maxbpm:<lesson>` ceilings, `tier:<lesson>`)
and run history in `IndexedDB` (the `sessions` store). Clearing site data, using
a different browser, or switching devices loses everything — there is no account
and no backup. Storing stats and progress in Supabase gives each learner a
durable, cross-device record of what they've unlocked and how they've played,
while keeping the app usable offline.

## What Changes

- Add **email magic-link authentication** via Supabase Auth. Signing in is
  optional — the app stays fully usable offline and unauthenticated.
- Add a **Supabase-backed cloud store** for the two existing data sets:
  - lesson progress: unlocked lessons, per-lesson BPM ceiling (`maxbpm`), and
    selected tier;
  - run stats: one row per finished run, mirroring the `SessionStat` shape.
- Keep `localStorage`/`IndexedDB` as the **local source of truth**; add a
  **background sync layer** that pushes local data up and pulls remote data
  down, merging both directions:
  - progress merges by taking the highest BPM ceiling and the union of unlocked
    lessons;
  - stats are append-only and de-duplicated so a run is never counted twice.
- On first sign-in, **adopt existing device-local data** into the account
  instead of discarding it.
- Add sign-in / sign-out UI and a lightweight sync-status indicator.

No breaking changes for existing users: anyone who never signs in keeps the
current local-only behavior unchanged.

## Capabilities

### New Capabilities

- `user-auth`: Passwordless email magic-link sign-in/out via Supabase Auth,
  with session persistence and SvelteKit SSR-aware session handling. Auth is
  optional; the unauthenticated experience is preserved.
- `cloud-sync`: Offline-first synchronization of lesson progress and run stats
  between the device (`localStorage`/`IndexedDB`) and Supabase — background
  push/pull, first-login adoption of local data, and deterministic merge rules
  (max/union for progress, append-only de-duplication for stats). Includes the
  Supabase schema and row-level security that scope every row to its owner.

### Modified Capabilities

<!-- None. openspec/specs/ is currently empty; there are no existing specs whose
     requirements change. -->

## Impact

- **New dependencies**: `@supabase/supabase-js` and `@supabase/ssr`.
- **New configuration**: `PUBLIC_SUPABASE_URL` and `PUBLIC_SUPABASE_ANON_KEY`
  environment variables; a Supabase project with tables (e.g. `lesson_progress`,
  `sessions`) and RLS policies keyed to `auth.uid()`.
- **Affected code**:
  - `src/lib/stats.ts` — add a sync path alongside the existing IndexedDB writes.
  - `src/routes/lessons/[id]/+page.svelte` — progress persistence hooks into sync.
  - `src/routes/stats/+page.svelte` — read merged (local + remote) history.
  - New auth UI + session store, a new sync module, and a `hooks.server.ts` for
    SSR session handling.
- **Build/deploy**: SSR auth may require replacing `@sveltejs/adapter-auto`
  with a concrete adapter, and configuring Supabase env vars in the deploy
  target.
- **Privacy**: run stats and progress become associated with an email-based
  account for signed-in users; unauthenticated users remain device-local only.
