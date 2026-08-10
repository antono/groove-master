# Depends on `supabase-integration` for cloud persistence. Tasks in groups 1–3

# and 6–7 work with no Supabase configured; group 5 lights up only once that

# change's auth + `reconcile()` are in place.

## 1. Quotes data asset

- [x] 1.1 Add `scripts/make-quotes.py`: read `docs/groove_academy_quotes.csv` (handle quoted fields / trailing blank line) and write `static/quotes/quotes.json`
- [x] 1.2 Give each quote a stable id `<author-slug>-<8-hex citation hash>`; assert ids are unique and independent of row order
- [x] 1.3 Emit each entry as `{ id, citation, author, testimonial }` (testimonial = CSV `reference`)
- [x] 1.4 Generate `static/quotes/quotes.json` and document the regenerate step in CLAUDE.md alongside the other `scripts/make-*.py`

## 2. Local rating & preference store

- [x] 2.1 Add `src/lib/quote-store.ts` mirroring `progress-store.ts`, best-effort over `localStorage` under the `groove-master:` prefix
- [x] 2.2 Ratings: `readRatings()` / `setRating(id, "like"|"dislike")` stamping `{ value, at: Date.now(), synced: false }`; re-rating replaces the previous value
- [x] 2.3 Seen set: `readSeen()` / `markSeen(id)` / `resetSeen()`, persisted across sessions
- [x] 2.4 Preference: `isQuotesOff()` / `setQuotesOff(true)`
- [x] 2.5 Sync hooks: `unsyncedRatings()` and `markRatingsSynced(ids)`, shaped like the helpers `stats.ts` exposes to `sync.ts`

## 3. Quote of the Day component

- [x] 3.1 Add `src/lib/quote-of-the-day.svelte` that lazy-`fetch`es `quotes.json` and exposes an `open()` / hidden-by-default overlay API
- [x] 3.2 Selection: pick a random quote preferring unseen (`readSeen`); when all seen, `resetSeen()` and draw again from the full set; `markSeen` the chosen quote
- [x] 3.3 Layout: full-screen overlay, citation + author centered vertically and horizontally
- [x] 3.4 Reveal the author testimonial on hover **and** click/tap/keyboard (author is a `<button>`), hidden until then
- [x] 3.5 Like / dislike controls that call `setRating`, then `queueReconcile()`, then the `onAdvance` callback
- [x] 3.6 A bottom "never show quotes" checkbox that calls `setQuotesOff(true)` and immediately fires `onAdvance` with no rating

## 4. Result-screen interstitial wiring

- [x] 4.1 In `src/routes/lessons/[id]/+page.svelte`, mount `quote-of-the-day` and turn the result-screen "Next lesson" `<a>` (≈line 1384) into a button that delegates to it
- [x] 4.2 Handler: if `isQuotesOff()` → navigate straight to `nextLesson`; else `open()` the interstitial
- [x] 4.3 On `onAdvance`, `goto` the next lesson href (navigation stays the page's job); ensure Listen/Play and the rest of the result screen are untouched

## 5. Cloud persistence (rides on supabase-integration)

- [x] 5.1 Add a `supabase/migrations/*_create_quote_ratings.sql`: table `quote_ratings(user_id, quote_id, value check in (like,dislike), updated_at, PK(user_id,quote_id))`
- [x] 5.2 Enable RLS with owner-scoped select/insert/update `TO authenticated` (`auth.uid() = user_id`), no delete policy, anon deny-by-default — mirroring the `lesson_progress` policies
- [x] 5.3 Add `syncRatings(supabase, userId)` and call it from `reconcile()` after progress/stats
- [x] 5.4 Merge last-write-wins by `updated_at` vs local `at`; upsert changed rows `onConflict: "user_id,quote_id"`; `markRatingsSynced` the converged ids
- [x] 5.5 First-login adoption: local unsynced ratings push on the first post-sign-in reconcile with no loss (falls out of 5.3–5.4 as with progress/stats)
- [x] 5.6 Confirm no Supabase configured → store + interstitial still work fully offline (`supabaseConfigured === false` no-ops the sync path)

## 6. Verification

- [ ] 6.1 Finish a run → "Next lesson" shows the full-screen quote; like/dislike advances to the next lesson
- [ ] 6.2 "Never show quotes" dismisses instantly, skips to the next lesson, and stays off on later runs
- [ ] 6.3 Seen set advances per run and restarts the cycle once every quote has been shown
- [ ] 6.4 Signed out: ratings persist locally; sign in → local ratings adopt into the account and appear in `quote_ratings`
- [ ] 6.5 Re-rating a quote converges to one current value across device and cloud (LWW)
- [x] 6.6 `pnpm check` passes; SSR renders the lesson page with no signed-out flash and no console errors
