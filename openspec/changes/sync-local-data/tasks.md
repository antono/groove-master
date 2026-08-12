## 1. Schema

- [ ] 1.1 Apply the existing `quote_ratings` migration to the remote project (`supabase/migrations/…_create_quote_ratings.sql`)
- [ ] 1.2 Verify RLS on `quote_ratings`: owner-scoped select/insert/update `TO authenticated` (`auth.uid() = user_id`), anon denied; run `get_advisors(security)`

## 2. Fault-isolated reconcile

- [ ] 2.1 Refactor `reconcile()` in `src/lib/sync.ts` to a registry of named routines run with `Promise.allSettled` (progress, stats)
- [ ] 2.2 Aggregate status: `error` if any routine rejects (logged per routine), else `idle`/`lastSyncedAt`; never roll back a routine that succeeded
- [ ] 2.3 Confirm single-flight, triggers, and `refreshPending` still behave; `syncProgress`/`syncStats` bodies unchanged

## 3. Quote ratings sync

- [ ] 3.1 Add `syncRatings(supabase, userId)` using `quote-store.ts` helpers (`unsyncedRatings`, `applyRemoteRatings`, `markRatingsSynced`); LWW by `updated_at`
- [ ] 3.2 Register `ratings` in the reconcile registry
- [ ] 3.3 First-login adoption: existing local (unsynced) ratings upload on the first reconcile with no data loss
- [ ] 3.4 Verify the quote component's `queueReconcile()` after a rating triggers the routine

## 4. Coverage rule (docs)

- [ ] 4.1 Document the sync-coverage rule: the registry of datasets, each with its merge strategy and pull-back decision (progress = max/union, stats = append-only, ratings = LWW); note controller-config as the next dataset (separate branch)

## 5. Verification

- [ ] 5.1 `pnpm check` passes and `pnpm build` succeeds
- [ ] 5.2 Rate a quote signed in → row appears in `quote_ratings`; re-rate → converges to one current value (LWW)
- [ ] 5.3 Sign in on a second device → ratings pull down
- [ ] 5.4 Fault isolation: with one routine forced to throw, the others still sync and their results persist; status shows failed-pending
