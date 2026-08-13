## Context

`/lessons/+page.svelte` renders the whole curriculum as one flat scroll. It
fetches `static/lessons/manifest.json` in `onMount`, groups the `stages →
modules → lessons` tree, and prints every lesson card (with a MIDI-derived
chart, earned/tempo badges, and greyed `planned()` slots) in one pass. The
proposal replaces that with drill-down navigation down the same spine
(tier → stage → lesson), with breadcrumbs and per-level orienting text.

Two facts about the current data shape drive most of the decisions below:

- **The journey tier is not in the manifest.** `manifest.json` has `stages`
  (`slug`, `number`, `title`, `goal`, `modules`, `closing`) and lesson slots
  carry a `tier` field — but that field is the _lesson_ tier
  (`plain`/`core`/`stretch`). The four journey tiers (Foundations, Vocabulary,
  Music, Mastery) and their orienting questions exist only in
  `docs/curriculum.md §6`. The word "tier" is overloaded in this codebase; this
  document uses **tier** for the journey level and **lesson tier** for
  plain/core/stretch.
- **The manifest is sparse.** Only stages 1–4 are emitted today; Music and
  Mastery have no stages at all. So a tier's membership and existence cannot be
  derived from "which stages are present" — the tier set has to be declared
  independently, or the landing can never show the road ahead.

## Goals / Non-Goals

**Goals:**

- One level per screen: tier landing → a tier's stages → a stage's lessons.
- Every level below the landing has breadcrumbs and a real, shareable URL.
- The orienting text already authored (tier question, stage `goal`, module
  subtitle) is surfaced at the level it belongs to.
- Per-tier and per-stage progress rollups, reusing existing history.
- A "Continue" shortcut so drill-down never taxes a returning student.
- The lesson card, chart, badges and `planned()` treatment are unchanged, only
  regrouped under the stage view.

**Non-Goals:**

- No change to MIDI generation, lesson patterns, or `/lessons/[id]`.
- **No progress-gated unlocks.** "Locked" here means "not written yet", the same
  meaning `planned()` already has — not a gate that opens on prior mastery. Gated
  unlocks are a separate roadmap item (`curriculum.md §7`) and stay out.
- No change to the stats/progress schema; only new read-time aggregation.

## Decisions

### D1 — Declare tiers in the generator, emit into the manifest

The tier set (name, orienting question, which stages belong) becomes a
declaration in `scripts/lessons/` and is written to `manifest.json` as a new
top-level `tiers` array (e.g. `{ slug, name, question, stages: [1, 2] }`). The
app reads it; it never hard-codes tier names.

- **Why:** This codebase keeps one source of truth per fact on principle —
  charts come from MIDI, lesson order lives in the manifest and nowhere else. A
  client-side tier table would put curriculum knowledge in two places and let the
  landing drift from `curriculum.md`. It also solves the sparse-manifest problem:
  a declared tier can render (locked) even when none of its stages are emitted
  yet, which is exactly the `planned()` philosophy applied one level up.
- **Scope note:** this refines the proposal's "no generator change" — the change
  is _additive metadata only_ (no MIDI, no pattern, no re-render). Regenerating
  is still a no-op diff.
- **Alternative considered:** a client-side constant mapping stage-number ranges
  → tier + question. Rejected: duplicates the curriculum, and the app would own a
  fact the generator should.

### D2 — Routing: reserved static segments under `/lessons`

- Landing stays at `/lessons`.
- Tier view: `/lessons/tier/<tier-slug>`.
- Stage view: `/lessons/stage/<stage-slug>`.
- Lesson stays at `/lessons/<slug>` via the existing `[id]` route.

SvelteKit resolves static segments (`tier/`, `stage/`) before the dynamic
`[id]`, so there is no collision as long as no lesson slug is literally `tier`
or `stage` — cheap to reserve those two words in the generator.

- **Why over query params (`/lessons?tier=…`):** the proposal asks for real
  breadcrumbs, back-button and shareable per-level URLs; distinct routes give all
  three for free and keep each level a `+page`.
- **Alternative considered:** nesting lessons under stage
  (`/lessons/stage/<stage>/<lesson>`). Rejected: it would break the stable
  `/lessons/<slug>` URL that stats, remembered-tempo and shared links depend on,
  and a lesson's URL must not encode its position.
- **Placement:** breadcrumbs sit at the **top** of every level below the landing
  — the first thing on the page, above the level's heading and orienting text —
  so location is read before content on every screen.

### D3 — Load the manifest in a shared `+page.ts`/`load`, not per-page `onMount`

The tier and stage pages read only manifest metadata (names, goals, structure,
progress) — no MIDI. Move that fetch into a universal `load` shared across the
new levels so breadcrumbs and headings render server-side.

- **Why:** it fixes, for the new pages, the SEO gap called out in `CLAUDE.md`
  (the current `onMount` fetch means crawlers see the fallback). The stage view's
  **lesson charts still parse MIDI client-side** exactly as today — that stays in
  `onMount`; only the structural metadata moves to `load`.
- **Alternative considered:** keep everything in `onMount`. Rejected for the new
  pages (worse orientation-on-load and SEO); acceptable only where MIDI parsing
  forces it.

### D4 — Progress rollups are read-time aggregation over existing history

`progressByLesson()` already yields per-lesson cleared/tempo data. A tier or
stage rollup is "written lessons cleared / written lessons total" within that
scope, computed on read. Planned slots are excluded from the denominator so the
bar reflects only playable material.

- **Why:** no schema change, non-throwing by contract like the rest of stats; a
  browser with no IndexedDB shows structure with empty bars and still navigates.

### D5 — "Continue" = first uncleared written lesson in curriculum order

The landing's shortcut targets the first written, non-`planned` lesson that the
history does not mark cleared, in manifest order; if everything written is
cleared, it points at the last written lesson. Best-effort, derived from the same
progress read as the rollups.

- **Why:** simple, needs no new "current lesson" state, and degrades cleanly when
  there is no history (points at the first lesson).

### D6 — Roadmap visualization: a visual journey spine, bars as fallback

"You are here" is carried by breadcrumbs plus a **visual journey spine** — the
vertical tier→stage path from `curriculum.md §6`, with the current position
marked — shown on the landing and tier view. The per-scope progress bars (D4
data) fold into the spine as the fill on each node rather than living as a
separate strip.

- **Why:** the strongest sense of place, which is the whole ask ("student must
  always understand where he is"). We try it first; if it reads as too heavy for
  the intended minimalism it degrades cleanly to the slim progress bars, since
  both render from the same rollup data.
- **Build note:** keep the spine a self-contained component fed by
  `{ tiers, stages, progress, here }` so swapping it for a plain bar list is a
  one-component change, not a rework of the pages.
- **Alternative considered:** slim progress bars only. Kept in reserve as the
  fallback, not the default.

## Risks / Trade-offs

- **[Overloaded "tier" term breeds confusion in code and manifest]** → name the
  new field `tiers` at the top level and keep the lesson field `tier`; document
  the two meanings where they are read (they are never siblings, so they don't
  clash structurally, only in prose).
- **[Drill-down is 3 clicks to a lesson for a returning student]** → the D5
  "Continue" shortcut on the landing is the mitigation and is in scope, not
  optional polish.
- **[Locked tiers read as "gated on my progress" rather than "not built yet"]**
  → use the same visual language as `planned()` cards (dashed/dimmed) and label
  by state ("not written yet"), never with a progress lock; no unlock logic
  exists to imply.
- **[A future lesson slug collides with `tier`/`stage`]** → reserve both words in
  the generator's slug validation (`schema.py`).
- **[Manifest gains a field older cached clients don't expect]** → the app treats
  `tiers` as optional and falls back to grouping stages with no tier as a single
  untitled section, so a stale manifest still renders.

## Migration Plan

1. Add the `tiers` declaration to `scripts/lessons/` and emit `tiers` in
   `make-lessons.py`; regenerate the manifest (additive, no MIDI change).
2. Build the three levels as new routes; keep the current flat page working
   until the stage view reaches parity, then repoint `/lessons` to the landing.
3. No data migration: history, remembered tempo and lesson URLs are untouched.
   Rollback is reverting the routes; the extra `tiers` field is inert if unread.

## Resolved Questions

- **O1 — Roadmap form → visual journey spine first (D6).** Ship the spine; fall
  back to slim progress bars only if it proves too heavy. Both render from the
  same rollup data, so the fallback is a one-component swap.
- **O2 — Tier earns its own screen → yes.** Three navigable levels stand:
  tier landing → tier view → stage view. A tier holds 2–4 stages today and is
  expected to gain more, so folding it into the landing was rejected — the tier
  view is the natural home for a tier's growing stage list and its question.
- **O3 — Old flat `/lessons` deep links → redirect to the new landing.** No
  attempt to preserve scroll-position anchors; `/lessons` simply becomes the tier
  landing.
