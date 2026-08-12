## 1. Schema

- [x] 1.1 Apply the existing `quote_ratings` migration to the remote project (applied via MCP: table + owner RLS)
- [x] 1.2 Verify RLS on `quote_ratings`: RLS on, 3 owner-scoped policies (select/insert/update `TO authenticated`, `auth.uid() = user_id`); advisors show no new issues

## 2. Fault-isolated reconcile

- [x] 2.1 Refactor `reconcile()` in `src/lib/sync.ts` to a registry of named routines run with `Promise.allSettled` (progress, stats, ratings)
- [x] 2.2 Aggregate status: `error` if any routine rejects (logged per routine), else `idle`/`lastSyncedAt`; successful routines are never rolled back
- [x] 2.3 Single-flight, triggers, and `refreshPending` unchanged; `syncProgress`/`syncStats` bodies unchanged

## 3. Quote ratings sync

- [x] 3.1 Add `syncRatings(supabase, userId)` using `quote-store.ts` helpers (`readRatings`, `applyRemoteRatings`, `markRatingsSynced`); LWW by `updated_at`
- [x] 3.2 Register `ratings` in the reconcile registry
- [x] 3.3 First-login adoption: existing local ratings are all "newer" than an empty cloud, so the push half uploads them on the first reconcile
- [x] 3.4 Verified the quote component's `rate()` already calls `queueReconcile()` after recording

## 4. Coverage rule (docs)

- [x] 4.1 Documented the sync-coverage rule in the `sync.ts` header: dataset registry with merge strategy + pull-back per dataset; controller-config named as the next routine (separate branch)

## 5. Verification

- [x] 5.1 `pnpm check` passes (0 errors) and `pnpm build` succeeds

Live E2E below needs a signed-in session on the deployed build (and, for 5.3, a second device); code is complete and build-verified:

- [ ] 5.2 Rate a quote signed in → row appears in `quote_ratings`; re-rate → converges to one current value (LWW)
- [ ] 5.3 Sign in on a second device → ratings pull down
- [ ] 5.4 Fault isolation: with one routine forced to throw, the others still sync and their results persist; status shows failed-pending
