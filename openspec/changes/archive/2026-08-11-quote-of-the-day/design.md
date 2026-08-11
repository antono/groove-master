## Context

The repo ships `docs/groove_academy_quotes.csv` — ~58 primary-sourced drummer and
producer quotes (columns: `citation`, `author`, `reference`). Nothing surfaces
them yet. This change shows one at the natural pause between lessons and lets the
student react to it.

The app already has an offline-first Supabase layer from `supabase-integration`
(further along in code than its `tasks.md` checkboxes suggest):

- `src/lib/supabase.ts` — `supabaseConfigured`, `createBrowserSupabase(fetch)`.
- `src/lib/auth.svelte.ts` — `authState` (`user`, `session`, `ready`) runes.
- `src/lib/sync.ts` — single-flight `reconcile()`, triggered from
  `+layout.svelte` via `startSync()` on `online`/visibility/periodic. Local
  stores are the source of truth; the "pending" set is _derived_, not an outbox.
- `src/lib/progress-store.ts` — the localStorage read/merge/write model this
  change mirrors for ratings.
- Migrations under `supabase/migrations/`; owner-scoped RLS keyed to `auth.uid()`.

The result screen lives in `src/routes/lessons/[id]/+page.svelte`; the "Next
lesson" control is the `<a class="lesson-nav next">` at ~line 1384, shown only
when `nextLesson && nextUnlocked`.

## Goals / Non-Goals

**Goals:**

- Ship the quotes as a versioned static JSON with a stable unique id per quote.
- A reusable `quote-of-the-day.svelte` presenting one random quote full-screen,
  author testimonial on hover/click.
- Interstitial on the result screen's "Next lesson"; like/dislike advances,
  "never show" opts out, seen set cycles.
- Ratings offline-first: local immediately, synced per user to an owner-scoped
  `quote_ratings` table, adopted on first sign-in — reusing the existing sync
  engine and triggers, not a parallel one.

**Non-Goals:**

- No new auth, session, or sync-trigger machinery — this rides on
  `supabase-integration`.
- No admin/editing UI for quotes; the CSV stays the editorial source.
- No aggregate/global "most liked" analytics in this change.
- No showing quotes anywhere other than the result-screen "Next lesson" (the
  interstitial is a self-contained component and could be reused later).

## Decisions

### Decision 1: CSV → static JSON at build/author time, not at runtime

A small converter script (`scripts/make-quotes.py`, mirroring the existing
`scripts/make-lessons.py` convention) reads `docs/groove_academy_quotes.csv` and
writes `static/quotes/quotes.json`. The component `fetch`es that JSON on mount.

_Why:_ the CSV is editorial and messy (embedded commas, quoted fields, a trailing
blank line); parsing it in the browser would ship a CSV parser and the raw file.
A generated JSON is small, cache-friendly (`static/`), and keeps the ids stable
in one place. _Alternative rejected:_ import the CSV via a Vite plugin — adds a
build dependency for a once-per-edit transform.

### Decision 2: Stable id = `<author-slug>-<8-hex of citation hash>`

The id is derived from the author (kebab-cased) plus the first 8 hex chars of a
hash of the citation text. It is independent of position, so adding or reordering
quotes never renumbers the others; it only changes if the quote's own text
changes (which is effectively a different quote). This satisfies the spec's
"stable across add/reorder" requirement and gives readable ids.

_Alternatives rejected:_ sequential `q-001` (breaks on reorder/insert); random
UUID baked into JSON (stable, but opaque and needs a side ledger to stay fixed
across regenerations).

### Decision 3: Ratings local store mirrors `progress-store.ts`

A new `src/lib/quote-store.ts` owns three localStorage keys under the existing
`groove-master:` prefix, best-effort like the progress store:

- `groove-master:quote-ratings` — `{ [quoteId]: { value: "like"|"dislike", at: number, synced: boolean } }`
- `groove-master:quotes-seen` — `string[]` of seen quote ids (current cycle)
- `groove-master:quotes-off` — `"1"` when "never show" is set

It exposes `readRatings/setRating`, `readSeen/markSeen/resetSeen`,
`isQuotesOff/setQuotesOff`, and `unsyncedRatings()/markRatingsSynced()` for the
sync engine — the same shape `stats.ts` exposes to `sync.ts`.

### Decision 4: `quote_ratings` table, last-write-wins by `updated_at`

New migration adds:

```
quote_ratings (
  user_id    uuid  references auth.users on delete cascade,
  quote_id   text  not null,
  value      text  not null check (value in ('like','dislike')),
  updated_at timestamptz not null default now(),
  primary key (user_id, quote_id)
)
```

RLS enabled; owner-scoped `select`/`insert`/`update` policies `TO authenticated`
with `auth.uid() = user_id`; no delete policy; anon denied by default — matching
the `lesson_progress` policy set exactly.

Unlike progress (monotonic max/union) and stats (append-only), **a rating can
change**, so the merge is **last-write-wins by `updated_at`**. Each `setRating`
stamps `at = Date.now()` and marks the row unsynced; sync compares local `at`
against remote `updated_at` and keeps the newer, writing the winner back to both
sides. This is deterministic and idempotent once converged.

_Alternative rejected:_ append-only rating events with "latest wins on read" —
more rows, more client logic, no benefit for a single current value per quote.

### Decision 5: Fold `syncRatings()` into the existing `reconcile()`

`reconcile()` in `sync.ts` gains a third step after `syncProgress`/`syncStats`.
It pulls the user's `quote_ratings`, merges LWW against local, upserts changed
rows (`onConflict: "user_id,quote_id"`), and marks synced — reusing the existing
single-flight guard, triggers (`online`/visibility/periodic/sign-in), and
`syncState`. First-login adoption is automatic: local unsynced ratings are pushed
on the first post-sign-in reconcile, exactly as progress/stats already are.

_Why not a separate engine:_ the triggers, coalescing, and error handling are
already correct and centralized; a parallel path would duplicate all of it.

### Decision 6: Interstitial is an overlay owned by the component; the page delegates

`quote-of-the-day.svelte` renders nothing until asked to `open()`. On the result
screen, the "Next lesson" `<a>` becomes a `<button>` whose handler: if quotes are
off → navigate immediately; else `open()` the interstitial. The component picks a
quote (prefer unseen; reset the seen set when empty), marks it seen, and on
like/dislike (or "never show") records via `quote-store`, fires a
`queueReconcile()`, and calls back to navigate with `goto(nextHref)`. Navigation
stays the page's job (it owns the href); the component owns presentation and the
rating write.

_Why:_ keeps the component reusable and free of routing knowledge, and keeps the
page's existing progressive-enhancement anchor semantics as a button fallback.

## Risks / Trade-offs

- **LWW needs a client clock** → both `at` (local) and `updated_at` (remote) are
  wall-clock; a badly skewed device could lose a rating race. Acceptable: a
  quote rating is low-stakes and self-correcting on the next explicit rating.
- **Testimonial reveal on hover is mouse-only** → also bind click/tap and treat
  the author as a `<button>`, so touch and keyboard users get the same reveal.
- **Seen set is device-local, not synced** → a user sees fresh quotes per device.
  Deliberate: syncing "seen" adds a table for no real benefit; ratings (the data
  worth keeping) do sync.
- **JSON diverging from CSV** → the converter is the only writer of
  `quotes.json`; re-run it after editing the CSV (documented in the task list and
  CLAUDE.md, alongside the other `scripts/make-*.py`).
- **Depends on unfinished `supabase-integration`** → the local-only path (store +
  interstitial + seen/never-show) works with no Supabase configured
  (`supabaseConfigured === false`); only cloud persistence waits on that change
  landing. Ratings therefore degrade gracefully to device-local, matching the
  app's optional-auth contract.

## Migration Plan

1. Add the `quote_ratings` migration (table + RLS) under `supabase/migrations/`;
   apply to the project.
2. Generate `static/quotes/quotes.json` from the CSV.
3. Ship `quote-store.ts`, the `syncRatings` step, and the component behind the
   result-screen button.

Rollback: the feature is additive. Reverting the component/store leaves the
`quote_ratings` table harmless (no reads); dropping the table is a separate
down-migration if desired. No existing data is touched.

## Open Questions

- Should the converter live in Python (`scripts/make-quotes.py`, matching
  `make-lessons.py`) or Node? Leaning Python for consistency with existing
  data-generation scripts; either is fine since it runs at author time only.
