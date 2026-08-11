# Changelog

Notable changes, newest first. **User-facing** is anything you would notice
while practising; **internal** is everything else — tooling, docs, and work that
only shows up in how the project is built.

Announcements for each release live in [`/news`](src/lib/news/); this file is
the complete list, that one is the readable half.

## v0.0.3 — 11 August 2026

Practice stopped being tied to one browser. Ten commits.

### User-facing

**An optional account, and cloud backup behind it.** Email magic-link sign-in —
no password. Signed in, earned tempo ceilings, unlocked lessons and every scored
run back up in the background and return on any device. Signed out the app is
unchanged: fully usable, fully offline, nothing withheld. First sign-in adopts
whatever that device had already practised instead of discarding it, and signing
out keeps the device's own copy.

**Two devices cannot undo each other.** Progress merges by taking the best of
both (higher ceiling, union of unlocked lessons); runs are append-only and
de-duplicated by id. A week on one machine and a week on another add up rather
than the later sync winning.

**Quote of the Day between lessons.** _Next lesson_ on a result screen shows one
line from a drummer or producer before the next lesson loads. The author's name
reveals who they are and where the line is from; like/dislike advances, and
_never show quotes_ ends them for good. 58 quotes, unseen ones preferred until
the set is exhausted. Ratings are stored on the device.

**The practice heatmap fits its window.** It drew 53 weeks whatever the space —
now it draws the weeks that fit, measured from the card rather than a breakpoint,
so it tracks a resized window: a year on a laptop, around 18 at 360px, never
fewer than 12. The header says how many weeks are shown.

**Fixes**

- `/lessons` and `/stats` could both render blank. The sync work moved the
  practice-history store to version 2, and an older connection in another tab or
  in bfcache blocks that upgrade — with no `onblocked` handler the open request
  never settled and both pages waited on it forever. It now gives up and retries
  later, yields when another tab needs the upgrade, and `/lessons` draws its
  cards without awaiting history at all.
- The Quote of the Day never appeared: the component shipped in its feature
  commit but was never imported by the result screen.
- The quote's author testimonial covered the quote it belonged to. Floating it
  above the author put it exactly where the citation's last line is, so a long
  bio hid the words being credited. It sits in the flow under the author now, and
  the overlay is top-anchored rather than centred — which is what makes that
  safe: a centred column shifted up by half of whatever the reveal added, moving
  the author out from under the pointer and flickering the bio on and off. The
  quote and author no longer move at all.
- The heatmap's day tooltip was clipped by the scroller it lived in — 55px off
  the right on the last column, 35px off the top on the first row. It is
  fixed-positioned and clamped to the screen now, flipping below the mark when
  there is no room above and dismissing on scroll. The card header also wraps as
  a unit instead of breaking its title mid-phrase.

### Internal

- Supabase integration: `@supabase/ssr` magic-link auth with SSR-validated
  sessions (`hooks.server.ts` `safeGetSession` → `getUser`), owner-scoped
  `lesson_progress` and `sessions` tables with RLS, and a background
  `reconcile()` sync engine (`$lib/sync.ts`). `adapter-auto` → `adapter-vercel`,
  since cookie auth needs SSR.
- A `quote_ratings` table and migration exist with RLS and last-write-wins
  merge, but **rating sync is not wired**: there is no `syncRatings` in
  `$lib/sync.ts`, so ratings are device-local. Noted as a follow-up when the
  openspec change was archived.
- `scripts/make-quotes.py` builds `static/quotes/quotes.json` from
  `docs/groove_academy_quotes.csv`; ids are `<author>-<8-hex citation hash>`.
- Analytics: `signinLinkSent` / `signinLinkFailed` on `/account`. No email
  address or error text is sent as a parameter.
- `supabase/config.toml` from `supabase init`, with `[auth]` aligned to the live
  project so `config push` stays surgical; `supabase/SETUP.md` documents the
  Vercel env and auth-config steps. `supabase-cli` and a `vercel` script added to
  `devenv.nix`, which also generates the shared MCP configs into the Nix store.
- `.vercelignore` keeps `soundfonts/` (244 MB, over Vercel's 100 MB per-file
  limit) and the dev-only directories out of CLI deploys.
- News posts can carry screenshots: `$lib/news-article.svelte` styles
  `figure`/`img`/`figcaption`, and images live at `static/news/<slug>/`.
- `AGENTS.md` gained a **Releases** section — the version/changelog/news/tag/
  announce flow, and how to shoot the screenshots.
- openspec: `supabase-integration` and `quote-of-the-day` archived, capabilities
  synced into `openspec/specs/`.

## v0.0.2 — 8 August 2026

Lessons went from stopping to ending. Fourteen commits since launch.

### User-facing

**Lessons now finish instead of running out.** Every pattern lands on the bar
line that follows it: whatever sounds on beat one sounds once more at the end,
and the bass resolves onto the root note underneath it, after the drums have
stopped. The closing hit is scored, and the transport runs a beat past it so it
can actually be played rather than counting as a miss by construction.

**A borrowed hi-hat for lessons that had none.** Four early lessons left you
counting in silence between your own hits. They now have closed hats ticking on
the 8ths underneath — audible on the lesson's own kit, never shown on the
highway and never scored.

**A new bassline for lesson 1.1.** The old one played the root on all four beats
— the same beats as your kick, so it was masked by your own playing, and it
repeated one pitch a bar. The new line answers on the off-beats, in the gaps.

**New lesson: 4.5 Paradiddle Groove.** The core slot of the paradiddle module —
the same sticking as 4.4 with a kick on beats one and three underneath.

**Three highway sizes.** A button in the transport bar cycles compact (a thin
band with only the notes moving), medium (the same band at double height) and
full (the original, lanes filling the viewport). Safe to change mid-run,
remembered across lessons.

**Note colours no longer collide with scoring colours.** Drum-family colours and
timing-result colours overlapped: an unplayed kick was the exact hue of a
well-timed one. Identity now owns the cool half of the colour wheel and results
own warm-to-green, with no hue shared between them. The result chips and the
grade ramp were rebuilt onto the same rule.

**Link previews and an icon.** Shared links show a 1200×630 preview card; the
site has its own favicon, apple-touch icon and header mark, and a footer linking
the Mastodon profile.

**Fixes**

- The backing bass was silent on the first play on a device with nothing cached
  — its samples had not finished decoding and the notes were dropped. Lessons
  now wait for their own backing before starting, and warm it in the background
  on visit.
- The result screen showed a disabled _Next lesson_ button beside _Done_. The
  two are now alternatives: whichever applies, never a dead control.

### Internal

- `docs/LESSONS.md` — a how-to for managing lessons: adding a lesson or a stage,
  the pattern helpers, choosing a backing line, and what `make-lessons.py`
  enforces. The root `LESSONS.md` stays the index and `docs/curriculum.md` the
  rationale. `CLAUDE.md` symlinked to `AGENTS.md`.
- Google Analytics events for `lesson_started` / `lesson_finished` (lesson id)
  and `onboarding_started` / `onboarding_step` / `onboarding_finished` (step
  name). No practice data leaves the browser; these are counts of which lessons
  are opened and where setup is abandoned.
- `$lib/page-meta.svelte` and `$lib/site.ts` centralise per-page and site-wide
  link-preview tags, so no route can emit two `og:title`s.
- `warmKit` generalised to `warmUrls` with a `sampleUrl` builder, so backing
  samples warm the same fetch-only way drums already did.
- The `toot` CLI added to `devenv.nix` for Mastodon announcements.
- `scripts/render-og.sh` renders the preview card from `docs/og-card.svg`.
- Docs: a TODO scratchpad and a quotes collection.

## v0.0.1 — 7 August 2026

The launch. A free browser-based finger drumming trainer: lessons scroll down a
highway in time with a backing track, hits from MIDI pads are scored on timing,
and practice history is kept in the browser. No account, nothing to install.

See [the announcement](src/lib/news/2026-08-07-groove-academy-on-air.svelte) for
what shipped and what was still rough.
