## Why

Groove Academy is already playable on a phone — virtual controllers gave a
touchscreen its own pads — but the site around them is still a desktop site that
merely survives a narrow viewport. The header wraps into two rows of small text
links, tier and stage cards are only tappable on their heading and a 12px
"Enter →", the result screen is a 500px modal floating in the middle of a phone
screen, and `/stats` renders 53 weeks of heatmap into 375px. There is no web app
manifest at all, so the one place this belongs — the home screen of the device
you actually drum on — cannot install it.

Practising happens with the phone propped up and hands busy. Every interaction
should survive being hit with a thumb, and the app should open from the home
screen straight into the lesson you were on.

## What Changes

**Navigation**

- Below a mobile breakpoint the header nav collapses to a hamburger button that
  opens a **full-screen** menu panel — the links at reading size, not a dropdown
  of 0.9rem monospace. The current section is marked, Escape and a close button
  dismiss it, focus is trapped while open and returned on close, and route
  changes close it.
- The existing `@media (max-width: 26rem)` wrap-and-tighten rule in
  `+layout.svelte` is replaced by this, not layered on top of it.

**Tap targets**

- Every navigational block becomes tappable across its whole surface, not just
  its title: tier entries on `/lessons`, stage entries on `/lessons/tier/…`,
  lesson cards on `/lessons/stage/…`, and news entries. (`/news` already does
  this and is the model.) A card that is not navigable — a `planned()` slot, a
  locked tier — stays visibly inert.
- Interactive controls meet a minimum touch target of 44×44 CSS px, including
  the tempo slider thumb, transport buttons and the `/stats` range chips.

**The result screen**

- On mobile the run report is a full-screen sheet rather than a centred modal:
  it fills the viewport, its actions sit within thumb reach at the bottom, and
  its content scrolls inside the sheet. Desktop keeps the floating card.
- It stays a fixed overlay over the frozen highway either way — the no-reflow
  property that keeps CLS at zero is not traded away for this.

**Responsiveness elsewhere**

- **Viewport units**: `100vh` is replaced by `100dvh` where a full-height box is
  meant, so mobile browser chrome does not push the footer or the highway out of
  view.
- **Safe areas**: the fullscreen highway, its transport HUD and the overlay
  virtual pads respect `env(safe-area-inset-*)`, so nothing lands under a notch
  or a home indicator.
- **`/stats`**: the heatmap and trend charts scroll horizontally inside their own
  containers instead of forcing the page sideways; the range control and tiles
  reflow to a single column.
- **`/onboarding`**: the wizard's step rail, controller preview and capture
  prompts are usable at phone width — the step you are on is always legible.
- **Touch behaviour during a run**: pads and transport get
  `touch-action: manipulation` and no text selection, so a fast double-tap plays
  two hits instead of zooming the page.
- **Orientation**: the highway is written for a wide viewport; portrait phones
  get a layout that works rather than a squeezed one, and landscape is
  suggested, never required.
- No page scrolls horizontally at 320px.

**PWA**

- A web app manifest (`static/manifest.webmanifest`) with name, short name,
  `start_url`, `scope`, `display: standalone`, theme and background colours, and
  a maskable icon set (192/512 at minimum) rendered from the existing mark.
- `<link rel="manifest">` and `<meta name="theme-color">` from the layout head,
  theme-aware.
- **App shortcuts** (the long-press / right-click menu on the installed icon):
  **Continue lesson**, **Stats**, **News**.
- **NEW ROUTE `/lessons/continue`** — a manifest shortcut must be a static URL,
  but "the next uncleared lesson" is computed on the client from local progress.
  This route resolves that target and redirects to it, falling back to `/lessons`
  when there is no history. The `/lessons` Continue button points at the same
  place, so there is one definition of "continue" rather than two.
- **Offline launch**: the service worker gains a navigation fallback, so an
  installed app opened with no network shows the app rather than the browser's
  error page. Today navigations are left entirely to the network.
- An **install affordance** in the app for browsers that expose
  `beforeinstallprompt`, dismissible and never shown once installed.
- **Install is tracked as a GA event** through `$lib/analytics.ts`, the whole
  short funnel rather than the last step alone: the affordance being offered,
  the outcome of the prompt (accepted or dismissed), and the `appinstalled`
  event itself. `appinstalled` is the one signal that fires however the app was
  installed — including the browser's own menu, which never goes through our
  prompt — so it is the count of record; the other two are what tell "nobody was
  offered" apart from "everybody declined". Like every other event here it is
  best-effort and never blocks or breaks the install.

**Precaching on install**

- **Installing the app precaches the audio it needs to work offline.** Offline
  launch without this is a shell that opens and makes no sound — a lesson with
  no samples is not a lesson. Install is the moment to spend the bandwidth
  because it is the first unambiguous signal that this is somebody's instrument
  and not a page they landed on.
- The trigger is the **app being installed**, not the service worker's `install`
  event. Those are different moments: the worker installs on every first visit,
  including for someone who will read one news post and leave, and downloading
  megabytes there is exactly what the current warm-on-idle design avoids. That
  behaviour is unchanged for uninstalled visitors.
- **Scope of the fetch**: the student's configured kit plus the basses (~1 MB
  together), the lesson manifest, and the lesson MIDIs — not all twelve kits.
  A kit the student has not chosen is not something they are about to hear, and
  ~10 MB is a real cost on a phone. Switching kits later warms the new one the
  way it already does.
- It runs in the background, reports progress rather than blocking, survives
  being interrupted, and **skips whatever is already cached** — after a normal
  session of practice most of it will be. It is re-triggerable, not once-ever:
  the sample cache is version-keyed and dropped on activate, so a re-render or a
  re-level empties it and the installed app must be able to fill it again.
- The lesson manifest and MIDIs stay **network-first** when online, so a
  precached copy is the offline fallback and never pins a lesson to a stale
  pattern.

Not in scope: push notifications, background sync, a separate installed-app
layout, or precaching kits the student has not selected.

## Capabilities

### New Capabilities

- `responsive-layout`: How the site behaves below desktop width — the collapsing
  navigation, whole-block tap targets, the full-screen result sheet, touch
  target sizing, dynamic viewport height, safe-area insets, and the no-horizontal-
  scroll floor.
- `pwa-install`: Installability and installed behaviour — the web app manifest
  and icons, app shortcuts, offline launch, precaching the audio an installed
  app needs to be usable offline, the in-app install affordance, and the
  analytics that record whether any of it is being used.

### Modified Capabilities

- `lessons-catalogue`: the **Continue shortcut** requirement gains a stable URL.
  Continue is currently only a button on `/lessons` whose target is computed in
  the page; it becomes a resolvable route (`/lessons/continue`) that both the
  button and the PWA shortcut point at, with defined behaviour when there is no
  practice history.

## Impact

- `src/routes/+layout.svelte` — hamburger nav, manifest and theme-color links,
  install affordance and its analytics.
- `src/lib/analytics.ts` — new install-funnel events, alongside the existing
  lesson and onboarding ones.
- `src/app.html` — viewport meta (`viewport-fit=cover` for safe areas).
- `src/routes/lessons/[id]/+page.svelte` — result sheet, safe areas, touch-action
  on the run overlay.
- `src/routes/lessons/+page.svelte`, `lessons/tier/[tierSlug]`,
  `lessons/stage/[stageSlug]`, `src/routes/news/+page.svelte` — card tap targets.
- `src/routes/stats/+page.svelte`, `src/lib/trend-chart.svelte` — horizontal
  containment.
- `src/routes/onboarding/+page.svelte`, `src/lib/controller-preview.svelte` —
  narrow-width layout.
- `src/app.css` — breakpoint tokens and shared tap-target sizing.
- **New**: `src/routes/lessons/continue/+page.*`, `static/manifest.webmanifest`,
  `static/icons/*`, and an icon render step alongside `scripts/render-og.sh`.
- `src/service-worker.ts` — navigation fallback; the manifest and icons ride the
  existing `files` precache.
- `src/lib/drums.ts` — `warmKit()` grows a sibling that warms for offline (kit +
  basses + lessons) with progress, reusing its skip-what-is-cached behaviour.
- `continue` becomes a reserved lesson slug, like `tier` and `stage`
  (`scripts/lessons/__init__.py`), so no lesson can shadow the route.
- No change to scoring, MIDI, samples, or the curriculum.
