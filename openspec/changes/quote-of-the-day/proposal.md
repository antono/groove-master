## Why

Practice is easier to keep up when it feels like joining a lineage rather than
grinding drills. The repo already ships a curated, primary-sourced collection of
drummer and producer quotes (`docs/groove_academy_quotes.csv`), but nothing in
the app surfaces them. Showing a voice from the tradition at the natural pause
between lessons — the moment a student decides whether to keep going — turns a
transition into a small reward and a reason to come back.

## What Changes

- Ship the quote collection as a static JSON asset with a **stable unique id per
  quote**, converted from `docs/groove_academy_quotes.csv` (citation, author,
  reference/testimonial). The CSV stays the editorial source; the JSON is the
  shipped, versioned artifact.
- Add a **Quote of the Day** Svelte component that shows a single random quote
  **full-screen, centered** vertically and horizontally, with the author's name;
  the author's testimonial (the CSV `reference` text) is revealed on **hover or
  click**.
- Wire the component as an **interstitial on the result screen**: after a scored
  run, pressing **Next lesson** shows the quote first; a **like** or **dislike**
  then advances to the next lesson.
- Add a **"never show quotes"** checkbox at the bottom of the interstitial that
  instantly dismisses the quote, skips straight to the next lesson, and
  suppresses the interstitial from then on (a device-local preference).
- **Prefer unseen quotes** and remember which the user has seen; once every quote
  has been shown at least once, the cycle **starts again from the beginning** (the
  seen set resets), so the collection keeps coming round without repeating a quote
  before the others have had their turn.
- Persist each **like/dislike** offline-first: recorded locally immediately, and
  for a signed-in user synced to a new **owner-scoped Supabase table** keyed to
  `auth.uid()`. Signed-out ratings are kept locally and adopted into the account
  on first sign-in — matching the offline-first pattern established by
  `supabase-integration`.

No breaking changes: users who never sign in keep rating quotes locally, and any
user can turn the interstitial off.

## Capabilities

### New Capabilities

- `quote-interstitial`: Presentation and interaction of the quote — the static
  JSON collection with stable ids, random selection, full-screen centered
  layout, author testimonial on hover/click, the like/dislike-to-advance flow on
  the result screen's "Next lesson", and the device-local "never show quotes"
  preference.
- `quote-ratings`: Offline-first persistence of a user's like/dislike per quote —
  written to device-local storage immediately, synced to an owner-scoped Supabase
  table (RLS keyed to `auth.uid()`) for signed-in users, and adopted from local
  data on first sign-in. De-duplicated so a quote carries one current rating per
  user.

### Modified Capabilities

<!-- None. openspec/specs/ is empty; the auth/sync capabilities this change
     relies on (user-auth, cloud-sync) are defined by the in-flight
     supabase-integration change and are not yet archived specs, so nothing
     here changes an existing archived requirement. -->

## Impact

- **Depends on** the `supabase-integration` change: reuses its Supabase client,
  auth session, SSR session handling, and background sync layer. This change adds
  a rating table + RLS and a rating sync path; it does not re-implement auth.
- **New data asset**: `static/quotes/quotes.json` (from
  `docs/groove_academy_quotes.csv`) plus a small converter script.
- **New code**: `src/lib/quote-of-the-day.svelte` (the component), a ratings
  module in `src/lib` (local store + Supabase sync), and a `quote_ratings` table
  with RLS keyed to `auth.uid()`.
- **Affected code**: the result screen on `src/routes/lessons/[id]/+page.svelte`
  gains the interstitial between "Next lesson" and navigation.
- **Configuration**: no new env vars beyond those introduced by
  `supabase-integration`.
- **Privacy**: for signed-in users, quote ratings become associated with their
  account; signed-out users' ratings stay device-local only.
