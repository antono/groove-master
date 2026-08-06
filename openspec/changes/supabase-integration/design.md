## Context

Groove Academy is a fully client-side SvelteKit 5 PWA. There is no backend, no
auth, and no server routes — only static assets. User data is device-local:

- **Progress** in `localStorage`: `groove-master:lessons-unlocked` (JSON array),
  `groove-master:maxbpm:<lesson>` (ceiling), `groove-master:tier:<lesson>`.
  Written from `src/routes/lessons/[id]/+page.svelte`.
- **Stats** in `IndexedDB` (`groove-master` DB, `sessions` store, autoincrement
  `id`, indexes on `at` and `lesson`). One `SessionStat` row per finished run.
  Managed by `src/lib/stats.ts`; the stats page aggregates by local calendar day.

The proposal adds optional email magic-link auth and offline-first sync of both
data sets to Supabase, with local storage remaining the source of truth. This
design covers the auth integration, the Supabase schema + RLS, and the sync
engine and merge rules.

## Goals / Non-Goals

**Goals:**

- Optional auth that never degrades the offline, signed-out experience.
- SSR-correct session handling (no signed-out flash, server validates the user).
- Owner-scoped Supabase schema with RLS enforced at the database.
- Offline-first sync: local writes always succeed; Supabase is a durable mirror.
- Deterministic, non-regressing merge (max ceiling, union of unlocks, append-only
  de-duplicated stats).
- Adopt pre-existing local data on first sign-in with no data loss.

**Non-Goals:**

- Realtime/live sync between simultaneously-open devices (periodic/triggered
  sync is enough).
- Social/OAuth or password auth (magic link only, per the proposal).
- Server-side aggregation or analytics; the stats page keeps aggregating client
  side over the merged set.
- Conflict UI or manual merge — merges are automatic and rule-based.
- Migrating the local storage engines away from `localStorage`/`IndexedDB`.

## Decisions

### 1. Auth via `@supabase/ssr`, validated with `getUser()`

Use `@supabase/ssr` with a `hooks.server.ts` that creates a request-scoped
server client bound to SvelteKit's cookie API, plus a browser client in a root
`+layout.ts`. Expose a `safeGetSession()` helper that calls
`supabase.auth.getUser()` to **validate** the JWT against Supabase (not trust the
unverified `getSession()` cookie), and surface `{ session, user }` via
`event.locals` and `PageData`.

- _Why_: This is the supported SvelteKit pattern. `getSession()` alone reads an
  unvalidated cookie; `getUser()` authenticates it, avoiding spoofable sessions
  and the signed-out hydration flash.
- _Alternative considered_: client-only auth (`localStorage` session, no SSR).
  Simpler, but causes an auth-state flash on load and can't gate SSR data;
  rejected because SSR correctness is a spec requirement.

### 2. Anon key + RLS only; no service role on the client

Ship only `PUBLIC_SUPABASE_URL` and `PUBLIC_SUPABASE_ANON_KEY`. All access is
authenticated user context; every table has RLS policies keyed to
`auth.uid() = user_id`. No service-role key ever reaches the browser or the
SvelteKit server bundle.

- _Why_: The client is untrusted; RLS is the only real boundary. Anon key +
  per-row policies is the Supabase-native model.
- _Alternative considered_: proxy all writes through SvelteKit server endpoints
  with a service key. More moving parts, a new trust boundary, and no benefit
  over RLS for this owner-scoped data; rejected.

### 3. Schema: `lesson_progress` (upsert) + `sessions` (append-only)

```
lesson_progress
  user_id     uuid    references auth.users, not null
  lesson_id   text    not null
  max_bpm     int     not null default 0        -- the ceiling
  tier        int                                -- selected rung
  unlocked    bool    not null default false     -- lesson itself unlocked
  updated_at  timestamptz not null default now()
  primary key (user_id, lesson_id)

sessions
  id          uuid    primary key                -- client-generated (dedup key)
  user_id     uuid    references auth.users, not null
  at          bigint  not null                    -- finish epoch ms
  day         text    not null                    -- local YYYY-MM-DD
  lesson      text    not null
  lesson_name text
  bpm         int
  device      text
  device_id   text
  stat        jsonb   not null                     -- full SessionStat payload
  created_at  timestamptz not null default now()
```

- Progress is modeled per `(user_id, lesson_id)` so merges are a per-row upsert;
  the "unlocked lessons" set is derived from rows where `unlocked = true`.
- Stats keep the hot query/aggregation columns (`at`, `day`, `lesson`, `bpm`) as
  first-class columns for indexing, and carry the full `SessionStat` in `stat`
  jsonb so the schema doesn't have to track every scoring field (`lanes`, timing
  breakdown, grade, etc.).
- _Why jsonb for the payload_: the `SessionStat` shape is broad and app-owned;
  columnizing all ~20 fields couples the DB to UI scoring internals. Index only
  what aggregation needs.
- _Alternative considered_: fully normalized columns + a `lanes` child table.
  Rejected as over-engineering for append-only, user-scoped records read in bulk.

### 4. Client-generated `id` (UUID) as the stats de-dup key

The `sessions.id` is a UUID generated on the client when a run is recorded, and
is the primary key in both IndexedDB-adjacent bookkeeping and Postgres. Existing
local rows use an autoincrement `id` and have no UUID, so a one-time local
migration assigns a stable UUID to each existing session (stored alongside the
row) before its first upload.

- _Why_: Append-only + "count a run exactly once" (spec) needs an
  origin-assigned stable id; a DB-assigned id can't dedup across re-syncs.
- _Alternative considered_: content hash of the run. Fragile (identical drills
  could collide) and heavier; rejected in favor of an explicit UUID.

### 5. Sync engine: an outbox + trigger-based reconcile

Add `src/lib/sync.ts` orchestrating:

- **Outbox**: pending local changes (progress upserts, new sessions) tracked in
  IndexedDB. Local writes in `stats.ts` and the lesson page enqueue an outbox
  entry after their existing local write — the local write path is never blocked
  on the network.
- **Triggers**: reconcile runs on `auth` state change (sign-in), on `online`,
  after a local write, and on a periodic backstop. Reconcile is a single-flight
  operation (no overlapping runs).
- **Reconcile**: pull remote (progress rows + session ids/rows), merge per the
  rules below, push the outbox, then clear applied entries. Failures leave the
  outbox intact for the next trigger.

- _Why_: An outbox makes offline the default and sync a best-effort background
  reconcile, matching the "sync failures do not disrupt use" requirement.
- _Alternative considered_: write-through (every local write also awaits a
  Supabase write). Rejected — it couples playback to the network and breaks
  offline.

### 6. Merge rules

- **Progress** (per lesson): `max_bpm = max(local, remote)`; `unlocked = local OR
remote`; `tier` follows the row with the higher `max_bpm` (ties → most recent
  `updated_at`). Upsert the merged row both ways. Idempotent by construction.
- **Stats**: union by `id`. Pull remote ids, upload only local sessions whose
  `id` is absent remotely; insert remote sessions absent locally. Never update an
  existing session row. The stats page reads the merged local set.

### 7. Deploy adapter

SSR auth requires a running server, so replace `@sveltejs/adapter-auto` with the
concrete adapter for the chosen host (e.g. `adapter-node` or an edge adapter) and
provision the two public env vars there.

## Risks / Trade-offs

- **[No cross-device conflict resolution beyond max/union]** → Acceptable: the
  data is monotonic (ceilings only rise, unlocks only add, runs only append), so
  last-writer conflicts don't meaningfully exist. `tier` is the only mutable
  scalar and is low-stakes (a UI selection).
- **[Existing local sessions lack a UUID]** → One-time local backfill assigns and
  persists a UUID per legacy row before upload; the backfill is idempotent and
  guarded so it runs once.
- **[Magic-link redirect / PKCE in a PWA]** → Configure the auth callback route
  and allowed redirect URLs explicitly; test the offline→online link-open path.
- **[`getSession()` misuse]** → Standardize on `safeGetSession()` + `getUser()`
  everywhere server-side; add a lint/review note so no code trusts the raw cookie.
- **[Duplicate uploads under races]** → Single-flight reconcile plus dedup by
  primary key (`sessions.id`) makes re-runs safe; upserts are idempotent.
- **[Storage/permission denied]** → Same graceful degradation as today; sync just
  stays queued. Signed-out users are entirely unaffected.
- **[Adapter change affects deploy]** → Land the adapter swap and env wiring as
  its own step, verified in preview before enabling auth UI.

## Migration Plan

1. Provision the Supabase project; create `lesson_progress` and `sessions` tables,
   indexes (`sessions(user_id, at)`, `sessions(user_id, day)`), and RLS policies.
   Manage as a migration/declarative schema in the repo.
2. Add `@supabase/supabase-js` + `@supabase/ssr`, the browser/server clients,
   `hooks.server.ts`, `safeGetSession()`, and the auth callback route. No UI yet.
3. Swap the adapter and wire `PUBLIC_SUPABASE_*` env in the deploy target; verify
   SSR renders signed-out cleanly.
4. Add sign-in/out UI and the session store behind the existing app shell.
5. Implement `src/lib/sync.ts` (outbox, reconcile, merge) and the legacy-session
   UUID backfill; hook enqueues into `stats.ts` and the lesson progress writes.
6. Point the stats page at the merged set; add the sync-status indicator.

**Rollback:** the feature is additive and gated on sign-in. Hiding the sign-in UI
(or a feature flag) reverts every user to today's device-local behavior with no
data migration; local storage is never removed or rewritten destructively.

## Open Questions

- Which deploy adapter/host is the target (decides `adapter-node` vs edge)?
- Should `tier` sync at all, or stay a purely local UI preference? (Currently
  synced for full cross-device continuity.)
- Periodic reconcile cadence and whether to also reconcile on tab `visibility`
  regain.
- Do we want a "sign in to back up your progress" nudge, or keep auth fully
  passive/discoverable only?
