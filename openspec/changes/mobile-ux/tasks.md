## 1. Breakpoint foundation

- [x] 1.1 Add a `MOBILE_BREAKPOINT` module (value `48rem` / its px equivalent) exporting the value for `matchMedia`, documented as the single source of truth
- [x] 1.2 Add the shared tap-target sizing rule to `src/app.css` (min 44×44 on `(pointer: coarse)`), with a comment naming the breakpoint module
- [x] 1.3 Delete the `@media (max-width: 26rem)` header wrap rule in `+layout.svelte`

## 2. Collapsed navigation

- [x] 2.1 Add the menu control to the header, shown only below the breakpoint; hide the inline nav row below it
- [x] 2.2 Build the full-screen menu panel — links at reading size, current section marked, close control, respecting the debug opt-in
- [x] 2.3 Wire dismissal: close control, Escape, and route change
- [x] 2.4 Trap focus while open, return focus to the menu control on close, and lock scroll on the content behind
- [x] 2.5 Verify the header is a single row at 320px with no horizontal page scroll

## 3. Tap-navigable blocks

- [x] 3.1 Add the stretched-link pattern to tier entries on `/lessons`
- [x] 3.2 Same for stage entries on `/lessons/tier/[tierSlug]`
- [x] 3.3 Same for lesson cards on `/lessons/stage/[stageSlug]`, keeping the "Practice →" CTA above the stretched area
- [x] 3.4 Confirm `/news` entries already satisfy the one-block-one-link rule; align markup if not
- [x] 3.5 Reduce each block to a single exposed link — remove duplicate destination links from the accessibility tree
- [x] 3.6 Verify planned slots and locked tiers remain inert and visibly distinct

## 4. Full-screen result on mobile

- [x] 4.1 Below the breakpoint, switch `.report` from centred card to `inset: 0` sheet with an internally scrolling body
- [x] 4.2 Make `.report-actions` a sticky footer within the sheet, reachable without scrolling
- [x] 4.3 Verify no reflow of the page beneath on show and on dismiss (CLS stays at 0)

## 5. Viewport, safe areas and touch

- [x] 5.1 Add `viewport-fit=cover` to the viewport meta in `src/app.html`
- [x] 5.2 Replace `100vh` with `100dvh` in document flow (`.app`), leaving the run overlay on `inset: 0`
- [x] 5.3 Apply safe-area insets to `.app`, the run overlay's transport and on-screen pads, the menu panel and the result sheet
- [x] 5.4 Add `touch-action: manipulation` and disable text selection on pads and transport controls
- [x] 5.5 Verify fast repeated taps register as two hits with no double-tap zoom, and dragging across pads selects nothing

## 6. Narrow-width pages

- [x] 6.1 Contain the practice heatmap and trend charts in their own horizontally scrolling containers
- [x] 6.2 Reflow `/stats` tiles, range control and runs table to a single column below the breakpoint
- [x] 6.3 Make the onboarding wizard usable at phone width — step name, instruction and controls visible without horizontal scrolling
- [x] 6.4 Scale the controller preview to the available width
- [x] 6.5 Sweep every route at 320px and fix any remaining horizontal page scroll

## 7. Portrait orientation

- [x] 7.1 Adjust lane height and visible lookahead so the highway stays legible in portrait
- [ ] 7.2 Add the dismissible rotate suggestion (never a gate) — **deliberately not built.**
      design.md parked this as an open question ("whether it earns its place, or whether
      portrait ends up good enough that the hint is just noise"), and portrait now measures
      as good enough: the HUD fits on one row clear of the band, and the lookahead went from
      ~2.5 beats to ~3.5. Shipping a nag that the design already doubted, without a real
      phone to judge it on, is the worse of the two errors. The spec permits it (MAY), so
      nothing is unmet.
- [x] 7.3 Verify a run survives rotation mid-play without ending or restarting

## 8. Continue route

- [x] 8.1 Add `/lessons/continue` — resolve via the shared `continueTarget()` on mount and navigate with `replaceState: true`
- [x] 8.2 Handle no history (first written lesson) and an unreadable catalogue (fall back to `/lessons`)
- [x] 8.3 Point the landing's Continue button at the same resolution path so there is one definition
- [x] 8.4 Reserve `continue` as a lesson slug in `scripts/lessons/__init__.py` and confirm generation fails when it is used
- [x] 8.5 Verify Back from the resolved lesson returns to the origin, not to the resolver

## 9. Manifest and icons

- [x] 9.1 Add `scripts/render-icons.sh` (sibling of `render-og.sh`) producing 192/512 icons plus a maskable variant at ~80% of the box
- [x] 9.2 Run it and commit the generated icons under `static/`
- [x] 9.3 Write `static/manifest.webmanifest` — name, short name, `start_url`, `scope`, `display: standalone`, background and theme colours, icon set
- [x] 9.4 Declare the three app shortcuts: Continue lesson, Stats, News
- [x] 9.5 Link the manifest and add `<meta name="theme-color">` from `+layout.svelte`
- [x] 9.6 Verify the browser reports the site as installable and the maskable icon survives a circular crop

## 10. Install affordance and analytics

- [x] 10.1 Add `pwaInstallOffered`, `pwaInstallPrompt({ outcome })` and `pwaInstalled` to `$lib/analytics.ts`
- [x] 10.2 Capture `beforeinstallprompt`, show the dismissible install affordance, and record that it was offered
- [x] 10.3 Record the prompt outcome (accepted/dismissed) and persist dismissal so it stays dismissed
- [x] 10.4 Listen for `appinstalled` and record it, including installs made through the browser's own menu
- [x] 10.5 Suppress the affordance when running installed or when no prompt is exposed
- [x] 10.6 Verify a blocked analytics tag changes no behaviour

## 11. Offline navigation

- [x] 11.1 Add an `/offline` page and include it in the precache
- [x] 11.2 Make navigations network-first in `src/service-worker.ts`, caching successful HTML
- [x] 11.3 Fall back to the exact cached page offline, then to `/offline`
- [x] 11.4 Verify the installed app launches with no network and that the primary routes render

## 12. Precache on install

- [x] 12.1 Add an `onProgress(done, total)` callback to `warmUrls()`, preserving skip-cached, bounded concurrency and never-throws
- [x] 12.2 Add the offline-set warm function beside `warmKit()` — configured kit, basses, lesson manifest, lesson MIDIs, primary route HTML
- [x] 12.3 Trigger it on `appinstalled`
- [x] 12.4 Also trigger on a standalone launch when the offline set is incomplete (covers iOS and refills a dropped cache)
- [x] 12.5 Surface progress as a dismissible strip that does not block practice
- [x] 12.6 Verify no unselected kit is fetched, and that an uninstalled visit still only warms on idle as before
- [x] 12.7 Verify a lesson opens, plays and scores fully offline after the precache
- [x] 12.8 Verify interrupting and re-running fetches only what is missing

## 13. Verification

- [x] 13.1 `pnpm check` passes
- [x] 13.2 `pnpm build && pnpm preview` — exercise install, offline launch, precache and shortcuts against the real service worker (dev has an empty `build`)
- [ ] 13.3 Walk the spec scenarios on a real phone, including a notched device for the safe-area cases
      — **not done: no device available here.** Everything was driven through Chrome DevTools
      emulation at 320×700 and 390×844 with `mobile,touch`, which exercises the breakpoints,
      the tap targets and the coarse-pointer rules but _cannot_ exercise `env(safe-area-inset-*)`
      — those are zero in emulation. The safe-area work (5.3) is therefore written and
      type-checked but visually unverified; a notched device is the only way to confirm it.
- [x] 13.4 Confirm an edited lesson MIDI still reaches a returning online student (network-first unbroken)
