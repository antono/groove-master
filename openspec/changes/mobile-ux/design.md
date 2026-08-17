## Context

See `proposal.md` — Why. The constraints that shape the approach:

- **`+layout.svelte` has one breakpoint today** (`@media (max-width: 26rem)`) and
  it wraps the header rather than collapsing it. There is no shared breakpoint
  token; each page invented its own.
- **The run is already a fixed overlay.** `position: fixed; inset: 0` with the
  lanes banded across the middle and the report floating over the frozen
  highway. That no-reflow property is load-bearing (it took a 0.52 CLS to zero)
  and nothing here may trade it away.
- **`warmUrls()` in `$lib/drums.ts` already does most of the precache.** It waits
  for the worker to control the page, skips anything `caches.match` finds, runs
  a bounded pool, and swallows failures. It is missing only progress reporting
  and a bass/lesson counterpart.
- **The service worker leaves navigations entirely to the browser.** Audio is
  cache-first, manifests and MIDIs network-first, precached build assets
  cache-first; page navigations fall through to the network, so offline is a
  browser error page.
- **Progress is device-local.** Clear/unclear comes from IndexedDB and
  `localStorage`, so no server can resolve "my next lesson".
- **One colour scheme.** `app.css` declares dark tokens with no
  `prefers-color-scheme` alternative, so the theme colour is a constant.
- **The site is SSR'd on Vercel** (`adapter-vercel`), so there is no prerendered
  SPA fallback document to serve for an arbitrary offline route.
- **`.vercelignore` excludes `scripts/`**, so anything an authoring script
  generates must be committed, never generated during the deploy build.

## Goals / Non-Goals

**Goals:**

- One breakpoint, defined once, used by both CSS and the code that needs to know
  about it.
- Mobile changes are additive over the existing desktop layout — no parallel
  mobile components, no second result screen.
- The precache reuses the warming path rather than growing a second one.
- Every offline behaviour degrades: no service worker, no `caches`, no install
  prompt, blocked analytics — each is a no-op, not a failure.

**Non-Goals:**

- A vertical, note-falls-toward-you highway for portrait. That is a different
  instrument, not a layout change.
- A separate installed-app layout or navigation.
- Server-side resolution of the continue target.
- Reworking the colour system; only a theme colour is declared.

## Decisions

### One breakpoint, declared twice on purpose

A single mobile breakpoint at **48rem**. Below it the nav collapses, the result
goes full-screen, and statistics reflow to one column.

Custom properties cannot be used in a media query, and the nav panel needs
JavaScript anyway (focus trap, Escape, close-on-navigate), so the value is
exported from a small module for `matchMedia` and written literally in CSS
beside a comment naming that module as its source. Two declarations of one
number is worse than one, but the alternatives are worse still: a build-time CSS
variable injection is machinery for a single constant, and driving layout from a
JS-measured width reintroduces the reflow the fixed overlay exists to avoid.

48rem rather than the current 26rem: seven monospace nav links plus the brand
need roughly 40rem before they crowd, and 26rem is why the header wraps today
instead of collapsing. The existing `max-width: 26rem` rule is deleted, not
layered under the new one.

### Whole-card tap targets via a stretched link, not a wrapping anchor

Each navigable block keeps its existing heading link and gains a
`::after { position: absolute; inset: 0 }` on that link, with the block as the
positioning context. Nested controls sit above it with a higher stacking order.

Alternatives: wrapping the whole `<article>` in an `<a>` gives the link an
accessible name made of the card's entire text (a screen reader reads the
summary, the schematic's label and the progress rollup as the link name), and
makes any nested link or button invalid HTML — lesson cards have a "Practice →"
call to action and stage cards have rollups. A click handler on the card is
worse again: no middle-click, no open-in-new-tab, no href to hover.

The trailing "Enter →" / "Practice →" links stay as visible affordances but
become decorative duplicates of the same destination, so they are marked
`aria-hidden` (or removed from the tab order) to satisfy the spec's "one block,
one link".

### The result sheet is the same element under a media query

`.report` keeps `position: fixed` and its overlay role in both layouts; below the
breakpoint its `top/left/transform/width` centring is replaced by `inset: 0`
with safe-area padding, its body scrolls, and `.report-actions` becomes a
sticky footer inside it. No second component, no conditional rendering — which
also means the "showing the result does not reflow the page" scenario holds by
construction rather than by discipline.

### `dvh` for flow, `inset: 0` for the run

`.app`'s `min-height: 100vh` becomes `100dvh`. The run overlay is deliberately
**not** converted: a fixed `inset: 0` box already tracks the visual viewport, and
`100dvh` would resize the highway every time mobile browser chrome retracts —
mid-run, while the compositor is animating a segment. So `dvh` is for the
document flow; the run keeps `inset: 0` and gains only safe-area padding.

### `viewport-fit=cover` plus explicit insets

`viewport-fit=cover` in the viewport meta is what makes `env(safe-area-inset-*)`
non-zero, but it also lets ordinary content slide under a cutout. So it is added
together with insets at the three places that go edge to edge: `.app`'s
horizontal padding, the run overlay (transport and on-screen pads especially —
the bottom inset is exactly where a home indicator sits under the pads), and the
full-screen nav panel and result sheet.

### Portrait keeps the horizontal highway

In portrait the lanes stay horizontal and scrolling; what changes is lane height
and the visible lookahead, so notes stay legible at a narrower width. A rotate
suggestion is a dismissible hint, never a gate — a student holding a phone in a
stand cannot always rotate it, and blocking play on orientation would make the
lesson unreachable.

Alternative considered and rejected: a vertical highway for portrait. It reads
better, and it is a second scoring surface, a second compositor path and a second
set of hit-window geometry to keep in step with the first.

### A static manifest file, and icons rendered by a script

`static/manifest.webmanifest` rather than a `+server.ts` endpoint: it is a
constant (one colour scheme), and living in `static/` means it rides the existing
`files` precache with no service-worker change.

Icons are rendered from `src/lib/assets/favicon.svg` by a sibling of
`scripts/render-og.sh`, with the maskable variant drawn at ~80% of the box so the
mark survives a circular crop. The outputs are **committed**, and the script is
not wired into `pnpm build` — same reason `check-kits.py` is not: `.vercelignore`
excludes `scripts/`, so a build that depended on it would die on the deploy host.

### Install detection: the event where it exists, the display mode everywhere

The precache and the analytics both need to know "this is installed". Chromium
fires `appinstalled`; iOS fires nothing at all and has no `beforeinstallprompt`.
So the trigger is **either** `appinstalled` **or** a launch detected as
standalone (`matchMedia('(display-mode: standalone)')`, plus the iOS-specific
`navigator.standalone`) where the offline set is not already complete.

That second path is not a fallback bolted on for iOS — it is what makes the
precache **re-triggerable** as the spec requires. The sample cache is
version-keyed and dropped on activate, so a re-render empties it; checking
completeness on a standalone launch refills it without the student reinstalling
anything. A once-ever flag in `localStorage` would have made "refilling an
emptied cache" impossible.

### The precache extends `warmUrls`, and includes page HTML

One new function beside `warmKit()`, warming: the configured kit's samples, the
bass sample set, the lesson manifest and every lesson MIDI, and the HTML of the
primary routes. It gains an `onProgress(done, total)` callback; `warmUrls` grows
the callback and keeps its existing behaviour (skip cached, bounded pool, never
throw), which gives resumability for free — an interrupted run finds most URLs
cached on the next attempt.

Precaching the page HTML is what makes offline navigation work without a shell
document (below). The set is small and enumerable: the six navigation routes
plus the lesson pages.

Progress is surfaced as an unobtrusive, dismissible strip, not a modal — the
whole point is that practice continues while it runs.

### Offline navigation: network-first, with an in-app offline page as the floor

Navigations become network-first, caching successful HTML responses. Offline,
the exact cached page is served; if there is none, a precached `/offline` page.

The tidier-sounding alternative — serve one app shell for any route and let the
client render it — does not work here. There is no prerendered fallback document
under `adapter-vercel`, and serving `/lessons`' SSR'd HTML for `/stats` would
hydrate a mismatched route. Precaching the actual routes sidesteps that entirely,
at the cost of an enumerated list; `/offline` covers whatever is not on it.

The manifest/MIDI network-first rule is unchanged, which is what keeps a
precached lesson from pinning a student to a stale pattern.

### `/lessons/continue` resolves on the client and replaces itself

A manifest shortcut is a static URL; the target is derived from IndexedDB and
`localStorage`. So the route is a page that resolves the target on mount and
navigates with `replaceState: true`, so pressing Back returns where the student
came from rather than bouncing through the resolver again. It shows a brief
resolving state, and falls back to `/lessons` when the catalogue cannot be read.

`continueTarget()` is already the shared definition; the landing's button and
this route both call it, so "continue" cannot come to mean two things.

`continue` joins `tier` and `stage` as a reserved slug in
`scripts/lessons/__init__.py`, so a lesson can never shadow the route.

### Analytics: three events through the existing wrapper

`pwaInstallOffered`, `pwaInstallPrompt({ outcome })` and `pwaInstalled` join the
existing exports in `$lib/analytics.ts`, inheriting its contract — no-op without
the tag, never throws, nothing branches on the result. Three rather than one
because `appinstalled` alone cannot distinguish "never offered" from "always
declined", and `appinstalled` is the count of record because it fires for an
install done through the browser's own menu.

## Risks / Trade-offs

- **`viewport-fit=cover` exposes every edge at once.** → Added in the same change
  as the inset padding at all four edge-to-edge surfaces, and checked on a
  notched device rather than only in a simulator.
- **A stretched link swallows nested controls.** A card whose body becomes one
  big link can eat a button placed inside it. → Nested controls get an explicit
  stacking order above the pseudo-element; the lesson card (which has a CTA) and
  the stage card (which has a rollup) are the two to verify.
- **Two declarations of the breakpoint can drift.** → Both carry a comment naming
  the other, and the module is the stated source of truth.
- **The precache spends a student's data.** ~1 MB on install. → Only on an
  explicit install, only the configured kit, skipping anything already cached —
  after any practice at all, most of it is. Not all twelve kits, which would be
  ~10 MB.
- **Precached page HTML goes stale.** A cached `/lessons` from install time could
  be served after the catalogue changes. → Network-first means it is only ever
  the offline fallback, and a service-worker version bump drops the cache.
- **Enumerated routes rot.** The offline route list is written by hand and a new
  top-level route will be missed. → `/offline` is the floor, so the failure mode
  is a mild one, and the list sits next to the nav links it mirrors.
- **iOS gets no install affordance.** No `beforeinstallprompt` means the spec's
  "not shown when the browser exposes no prompt" leaves iOS with nothing. →
  Accepted; iOS installs through the Share menu, and the standalone-launch
  detection means an iOS install still gets the precache and still records as
  installed.
- **`dvh` reflows as browser chrome retracts.** → Confined to document flow; the
  run overlay stays `inset: 0` and never resizes mid-run.
- **The count of `appinstalled` will not match store-style install numbers.**
  Uninstalls are invisible and re-installs count again. → It is a trend signal,
  not a population count; the standalone-launch signal is the better answer to
  "is anyone using this installed", if that is later wanted.

## Migration Plan

No data migration. Everything here is additive:

1. Ship the responsive work first — it is independent of the service worker and
   reversible by CSS alone.
2. Ship the manifest, icons and `/lessons/continue`. Installability appears; the
   route works whether or not anything is installed.
3. Ship the service-worker changes last. A new worker version drops the previous
   cache on activate, so the first load after deploy re-fetches the app shell and
   the samples warm again by the existing idle path.

Rollback is per step. Reverting the worker leaves installed apps on the previous
version until it activates; nothing is written that an older worker cannot read,
since the cache is keyed by version and simply rebuilt.

Old configurations, stored controllers, progress and practice history are
untouched throughout.

## Open Questions

- Whether the rotate suggestion earns its place, or whether portrait ends up good
  enough that the hint is just noise. Answerable after playing a lesson on a real
  phone; it changes no spec and no other task.
