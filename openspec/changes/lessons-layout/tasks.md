## 1. Manifest tier metadata (generator)

- [x] 1.1 Declare the four tiers in `scripts/lessons/__init__.py` next to `CURRICULUM` — a `TIERS` list, each `{ slug, name, question, stages: [numbers] }`, sourced from `docs/curriculum.md §6` (Foundations 0–2, Vocabulary 3–6, Music 7–8, Mastery 9–10).
- [x] 1.2 In `scripts/make-lessons.py`, emit a top-level `tiers` array into `manifest.json` alongside `stages`/`lessons`, without touching MIDI output or lesson order.
- [x] 1.3 Reserve `tier` and `stage` as forbidden lesson slugs in the generator's `check()` (fail loudly, naming the reserved slug).
- [x] 1.4 Regenerate: `python3 scripts/make-lessons.py`, confirm `tiers` is present and the git diff shows no MIDI/lesson-order change.

## 2. Data loading and progress rollups (shared)

- [x] 2.1 Add per-scope rollup helpers in `src/lib/catalogue.ts`: given the manifest structure + `progressByLesson` map, compute cleared-of-written counts per stage and per tier, excluding `planned` slots.
- [x] 2.2 Add a shared `+layout.ts`/`load` under `src/routes/lessons/` that fetches manifest metadata universally, so tier/stage headings and breadcrumbs render without waiting on `onMount`. MIDI chart parsing stays client-side.
- [x] 2.3 Add a `continueTarget()` helper: first written, non-`planned` lesson in curriculum order not marked cleared; else the last written lesson; else the first written lesson when there is no history.

## 3. Shared components

- [x] 3.1 Create a breadcrumbs component that renders `Lessons › <Tier> › <Stage>` with ancestor crumbs as links; used at the top of every level below the landing.
- [x] 3.2 Create a self-contained journey-spine component fed by `{ tiers, stages, progress, here }` — the vertical tier→stage path with the current position marked and each node filled by its rollup; shows upcoming (unwritten) nodes as the road ahead.

## 4. Tier landing (`/lessons`)

- [x] 4.1 Replace the flat scroll in `src/routes/lessons/+page.svelte` with the tier landing: one entry per tier (name + question from `tiers`), no stages/modules/cards.
- [x] 4.2 Render a tier with no written stages in the `planned`/locked style, labelled "not yet available", and non-navigable.
- [x] 4.3 Render the journey-spine on the landing and a "Continue" shortcut linking to `continueTarget()`.
- [x] 4.4 Handle a stale manifest with no `tiers` field: fall back to a single untitled grouping rather than failing.

## 5. Tier view (`/lessons/tier/[tierSlug]`)

- [x] 5.1 Create the route; list the tier's stages with each stage's title, number and progress; breadcrumbs at top; tier question near the top.
- [x] 5.2 Show the journey-spine with this tier marked current; each stage links to its stage view.

## 6. Stage view (`/lessons/stage/[stageSlug]`)

- [x] 6.1 Create the route; move the lesson `card` snippet and the module grouping out of the old flat page into here, unchanged (schematic, summary, earned/tempo badges, greyed `planned`).
- [x] 6.2 Show breadcrumbs `Lessons › <Tier> › <Stage>` at top, the stage goal near the top, and each module subtitle above its cards; include the checkpoint block.

## 7. Wiring and fallback

- [x] 7.1 Confirm the static `tier/` and `stage/` route segments resolve ahead of `[id]`, and a lesson still opens at `/lessons/<slug>`.
- [x] 7.2 Ensure the old flat `/lessons` URL lands on the new tier landing (it now _is_ the landing — verify no leftover scroll-anchor behaviour).

## 8. Tier-local stage numbering

- [x] 8.1 In the generator, derive each stage's tier-local number (position among its tier's stages, from 1) and emit `tierNumber`; make the lesson number's stage part tier-local. Keep the global `number` for tier-matching and MIDI directory names.
- [x] 8.2 Display `tierNumber` everywhere the catalogue shows a stage number (landing spine, tier view, stage view, breadcrumbs).
- [x] 8.3 Update the numbering docs (`AGENTS.md`/`CLAUDE.md`, `docs/LESSONS.md`, `docs/curriculum.md`).

## 9. Verify

- [x] 9.1 `pnpm check` clean.
- [x] 9.2 `pnpm build && pnpm preview`: walk landing → tier → stage → lesson, back-button, direct URLs, Continue shortcut, and a browser with no history (empty rollups still navigate).
