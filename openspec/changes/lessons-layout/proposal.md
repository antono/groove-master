## Why

The `/lessons` catalogue renders the entire curriculum as one flat scroll — every
stage, module and lesson card at once — and nowhere tells a student where they
are or what a tier or stage is _for_. That is tolerable at 19 lessons; against
the designed roadmap (4 tiers, 11 stages, 30 modules) it becomes a wall the
moment the curriculum grows. The topology already exists in the data
(tier → stage → module → lesson); the page just doesn't use it to orient anyone.

## What Changes

- Replace the single flat scroll with **drill-down navigation** down the
  curriculum's own spine: a tier landing → a tier's stages → a stage's lessons.
  Each screen shows exactly one level, so the page stays minimal.
- The landing shows **only the four tiers**, each carrying its orienting question
  ("can you keep time and stack two hands?") and a progress indication.
- Each level surfaces the goal text that is already authored but currently lost
  in the scroll: the tier's question, the stage's `goal`, the module's subtitle.
- **Breadcrumbs** on every level below the landing
  (`Lessons › Foundations › Stage 2 · Backbeat`), so location is always visible
  and every level is a real, shareable URL with a working back-button.
- A **"Continue" shortcut** on the landing that jumps a returning student
  straight to their next lesson, so drill-down navigation never taxes someone who
  just wants to practise.
- The lesson **cards, charts, `planned()` slots and earned/tempo badges** are
  kept as they are today — only regrouped under the stage view; nothing about an
  individual lesson card changes.
- Some form of **roadmap visualization** for "you are here" beyond breadcrumbs is
  in scope, but its exact form (slim progress bars vs. a visual journey spine) is
  deliberately left to `design.md`.

## Capabilities

### New Capabilities

- `lessons-catalogue`: How the lesson catalogue is navigated and laid out — the
  tier → stage → lesson drill-down, the orienting text at each level,
  breadcrumbs, progress indication, the "continue" shortcut, and how
  planned/locked material is shown. Covers presentation and navigation only; the
  curriculum data model (slugs, stage/module/tier fields, the manifest) is
  unchanged and out of scope.

### Modified Capabilities

<!-- None. No existing spec covers the catalogue; the lesson data model is unchanged. -->

## Impact

- **`src/routes/lessons/+page.svelte`** — today's flat scroll becomes the tier
  landing; its stage/module grouping logic and the `card` snippet move to the
  stage view.
- **New routes** under `src/routes/lessons/` for the tier and stage levels. Must
  not collide with the existing `[id]` slug route (a lesson is `/lessons/<slug>`);
  the tier/stage segments need a scheme that keeps `[id]` unambiguous.
- **`static/lessons/manifest.json`** is read as-is; no generator or MIDI change.
  The manifest already carries `stages`, `modules`, `tier` and `goal`.
- **Progress/tempo badges** (`$lib/progress.ts`, `$lib/stats.ts`) are reused for
  the per-tier and per-stage progress rollups; aggregation is new, the data is not.
- No change to `/lessons/[id]`, the highway, scoring, or the lesson pipeline.
