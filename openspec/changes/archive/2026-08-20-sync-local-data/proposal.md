## Why

Cloud sync covers lesson progress and run stats, but other local data goes
unsynced. The immediate gap is quote like/dislike ratings: `quote-store.ts` has
sync helpers, but nothing in `sync.ts` calls them and the `quote_ratings` table
was never applied — so a signed-in student's ratings are lost on a new device or
a storage clear. More generally, each new feature that persists locally risks
repeating this omission.

This change makes cloud sync **self-extending**: every locally persisted dataset
has a Supabase sync routine, and adding one is a defined step rather than an
afterthought. Quote ratings is the worked example here; controller/pad
configuration is the next dataset but is deferred to a separate branch already in
flight for that area.

## What Changes

- Establish a **sync-coverage rule**: any feature that persists data in
  `localStorage`/`IndexedDB` MUST also register a sync routine — a push to
  Supabase, a documented merge strategy, and a pull-back decision (does remote
  data flow to a fresh device?). Progress/stats/ratings/controller config are the
  worked examples.
- Make the reconcile **per-dataset isolated**: each dataset syncs independently
  (`Promise.allSettled`), so one failing — e.g. a table not yet provisioned —
  can't fail the others. (This is the bug that made the whole sync read "failed"
  when quote ratings 404'd.)
- **Quote ratings sync** (finish the existing capability): apply the
  `quote_ratings` migration, fold `syncRatings` into the isolated reconcile, and
  adopt existing local ratings on first sign-in. Merge is last-write-wins by
  `updated_at`.
- Keep everything **offline-first and optional**: unchanged for signed-out users;
  a missing table or offline device just leaves that dataset queued.

Controller/device configuration sync is **out of scope here** (deferred to the
in-flight branch for that area); the coverage rule names it as the next dataset.

## Capabilities

### New Capabilities

<!-- None. The controller-sync capability is deferred to a separate branch. -->

### Modified Capabilities

- `cloud-sync`: Add the **sync-coverage** requirement (every local dataset has a
  registered sync routine with a documented merge + pull-back decision) and make
  reconcile **fault-isolated** per dataset so one domain's failure can't abort or
  hide the others.

<!-- quote-ratings is already specified (openspec/specs/quote-ratings); this
     change implements it and wires it into the shared reconcile, which does not
     change its requirements, so it is not listed as a modified capability. -->

## Impact

- **New dependencies**: none.
- **New configuration**: the existing `quote_ratings` migration
  (`supabase/migrations/…_create_quote_ratings.sql`) finally applied to remote.
- **Affected code**:
  - `src/lib/sync.ts` — `reconcile()` becomes `Promise.allSettled` over a list of
    per-dataset sync routines; add `syncRatings` (from `quote-store.ts`); aggregate
    status without letting one failure poison the rest.
  - `src/lib/quote-store.ts` — already has the rating sync helpers; no change
    beyond wiring.
- **Docs**: note the sync-coverage rule so future local-storage features (the
  controller-config branch first) include a sync routine by default.
