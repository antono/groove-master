## Context

`src/lib/sync.ts` reconciles progress and stats for a signed-in user. Today
`reconcile()` awaits the sub-syncs in sequence inside a single `try/catch`, so a
throw in any one aborts the rest and flips the whole status to `error`. That is
exactly what happened when quote-rating sync was briefly wired in: it queried a
`quote_ratings` table that had never been applied, 404'd, and made the entire
sync read as failed even though progress and stats had uploaded fine. The quote
code was reverted, leaving `quote-store.ts`'s sync helpers unused and the
`quote_ratings` migration file committed but never applied to the remote.

This change hardens reconcile into a set of independent per-dataset routines and
uses that structure to finally land quote-rating sync, establishing the pattern
the coverage rule mandates.

## Goals / Non-Goals

**Goals:**

- Reconcile runs each dataset independently; one failure can't abort or hide the
  others, and the successes still persist.
- Quote ratings sync end to end: migration applied, `syncRatings` wired, LWW by
  `updated_at`, local ratings adopted on first sign-in.
- A documented registry of datasets so adding one is a defined step.

**Non-Goals:**

- Controller/device configuration sync (deferred to a separate branch).
- Changing the merge semantics of progress (max/union) or stats (append-only).
- Any change to signed-out or offline behavior.

## Decisions

### 1. Reconcile as a registry of independent routines

Model reconcile as a list of named sync routines and run them with
`Promise.allSettled`, collecting per-routine outcomes:

```
const routines = [
  { name: 'progress', run: () => syncProgress(supabase, userId) },
  { name: 'stats',    run: () => syncStats(supabase, userId) },
  { name: 'ratings',  run: () => syncRatings(supabase, userId) },
];
const results = await Promise.allSettled(routines.map(r => r.run()));
```

Status is `error` if any rejected (logged per routine), else `idle`; successful
routines have already written their local/remote state regardless. Concurrency is
safe — the routines touch disjoint tables and local stores and share one
supabase-js client, which multiplexes requests.

- _Why_: Directly satisfies the fault-isolation requirement and removes the
  single-`catch` coupling. Adding a dataset is appending one entry.
- _Alternative considered_: keep sequential awaits but wrap each in its own
  try/catch. Works, but the registry makes the coverage rule concrete and keeps
  status aggregation in one place.

### 2. Quote ratings routine (last-write-wins)

`syncRatings` reuses the existing `quote-store.ts` helpers (`unsyncedRatings`,
`applyRemoteRatings`, `markRatingsSynced`): pull remote rows, apply any whose
`updated_at` is at least as new as the local copy, then upsert local ratings that
are new or strictly newer than remote. A rating can change, so the merge is
last-write-wins by `updated_at` — unlike progress (monotonic) or stats
(append-only). Pull-back is yes (ratings follow the user across devices).

### 3. Apply the `quote_ratings` migration to remote

The migration file already exists
(`supabase/migrations/…_create_quote_ratings.sql`, owner-scoped RLS). Apply it to
the project so the routine has a table to hit; verify RLS as with the other
tables.

### 4. First-login adoption

On first sign-in, existing device-local ratings are unsynced by definition, so
the push half of `syncRatings` adopts them into the account with no extra code —
same shape as progress/stats adoption.

## Risks / Trade-offs

- **[A failing routine still shows a red status]** → Correct and intended: the
  user should know something didn't sync. The isolation guarantee is that the
  _other_ datasets succeed and aren't rolled back, not that failures are hidden.
- **[Concurrent routines increase peak requests]** → Small fixed fan-out (3);
  supabase-js handles concurrency. No pagination concerns at this scale.
- **[LWW clock skew across devices]** → Ratings use `updated_at` stamped at write
  time; skew could pick the "wrong" like/dislike, but the stakes are trivial and
  it converges. Matches the already-specified `quote-ratings` behavior.

## Migration Plan

1. Apply the `quote_ratings` migration to the remote project; verify RLS
   (owner-scoped select/insert/update, anon denied).
2. Refactor `reconcile()` to the routine registry with `Promise.allSettled` and
   aggregate status; keep `syncProgress`/`syncStats` unchanged.
3. Add `syncRatings` and register it; enqueue a reconcile after a rating is set
   (the quote component already calls `queueReconcile`).
4. Document the coverage rule (which datasets sync, their merge + pull-back).

**Rollback:** the registry change is behavior-preserving for progress/stats; if
ratings sync misbehaves, unregister the `ratings` routine and the rest is
unaffected — which is the whole point of the isolation.

## Open Questions

- None blocking. (Controller-config sync is explicitly deferred, not open.)
