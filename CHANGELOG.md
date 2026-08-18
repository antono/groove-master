# Changelog

Notable changes, newest first. **User-facing** is anything you would notice
while practising; **internal** is everything else — tooling, docs, and work that
only shows up in how the project is built.

Announcements for each release live in [`/news`](src/lib/news/); this file is
the complete list, that one is the readable half.

## v0.1.0 — 17 August 2026

The app stopped needing hardware. Twelve commits.

### User-facing

**Play with no controller at all.** A computer keyboard and a grid of on-screen
pads are now input sources in their own right, offered on setup's first step
under "No controller?". Six pads — kick, snare, closed and open hi-hat, crash,
ride — which is every drum the curriculum leans on. On a keyboard they sit under
`F G H` with `R T Y` above, bound by **physical key position** rather than the
printed letter, so the shape holds on AZERTY and Dvorak; `Space` starts and
resumes, `Escape` pauses and stops on a second press. They are ordinary sources
rather than a fallback mode: chosen
from the same device list, edited with the same per-pad dropdown, and recorded in
your stats under their own name, so keyboard practice stays tellable apart from
kit practice.

**A touchscreen can play a lesson.** No mobile browser implements Web MIDI, so a
phone or tablet previously had no way in at all. The on-screen pads lay out 2×3
to fit a phone and 3×2 wider, sit beside the pattern chart exactly where a kit's
schematic does, and take the room below the lanes during a run.

**A get-ready cue.** On a touch run, the pad whose note is approaching the hit
line rings about a beat ahead — you are looking at your fingers, not the highway,
so the cue goes where your eyes already are. Only touch runs pay for the
per-frame work.

**A calmer highway.** Notes travel 110 pixels per beat instead of 280, so at any
tempo they arrive from further off and much more of the pattern is readable
before it reaches you. Scoring is unaffected: it reads the audio clock and never
pixels.

**Kit pads that sound like the drums they are.** A drum module that names its
pads in GM knows more about them than a profile written from a photograph, so on
a kit a captured note we hold a sample for now becomes that pad's sound,
overriding the profile's suggestion. The MD-90's toms are corrected against real
hardware (47/45 → 45/43). Pad grids are untouched — an MPD218's notes are
addresses, not drums.

**Fixed: revealing a quote's testimonial shoved the buttons away.** It rendered
in the flow, pushing Like/Dislike down as it appeared. It floats now, and neither
the quote nor its buttons move.

### Internal

- `/debug/controller`: the stored mapping as a record rather than an
  interpretation — every pad with the note it listens for and the drum it fires,
  the hi-hat wiring, the transport bindings, plus a live monitor of what
  `Controller.handle()` makes of each incoming message. Exports and imports that
  record as JSON, and **import always re-targets**: a mapping is keyed by MIDI
  port id and browsers scope that per origin, so the id inside a file cannot be
  honoured.
- The production build no longer runs `scripts/check-kits.py`. `.vercelignore`
  excludes `scripts/`, so the v0.0.4 deploy died on the host with a missing-file
  error five seconds in; the check stays in `pnpm check`, where authoring checks
  belong.
- The WTFPL licence file is removed. No project licence ships with the source for
  now; the licence mentions left in `THANKS.md` are third-party sample credits.
- Release process: version numbers stay out of announcements — they live in the
  annotated tag and this file, and nowhere a reader looks.
- openspec: a `virtual-controllers` change (proposal, design, six requirements,
  tasks) written before the work and updated through it; `lessons-layout`
  archived and a baseline `lessons-catalogue` spec captured from its delta.
- devenv: agent skills are discovered from the tool-neutral `.agents/skills` and
  mirrored into `.claude/skills` on shell entry, so one copy serves every
  assistant; devenv and nixpkgs inputs bumped.

## v0.0.4 — 13 August 2026

The app stopped assuming what you play it on. Nine commits.

### User-facing

**Electronic drum kits.** Until now a controller had to be a rectangle of pads;
an e-drum kit could only be set up as a grid with most of its cells empty, in an
order you had to invent. There is now a second setup path that shows a kit as a
kit — its drums where they actually sit on the unit — and walks them one at a
time. A **Millenium MD-90** profile ships with it, matched by its maker: the
module announces itself as `e-drum` by `Medeli`, which is what it is, so the
wizard offers the layout rather than asserting the model.

**Your feet, discovered rather than assumed.** A pedals step captures the bass
pedal, then works out how your hi-hat is actually wired from three gestures —
some kits send one note and let the pedal decide, some send two different notes,
some have no pedal at all. Every pedal is skippable on its own, and what you
skipped is stated, so a kick that will never sound is something you learn before
a lesson rather than during one.

**Lessons know what your kit can't play.** If a lesson needs a drum your setup
cannot produce, the page says so before the run instead of letting those notes
surface as misses nobody can explain.

**A controller you have already set up is checked, not re-mapped.** Reconnecting
a known device goes straight to a screen where you hit pads and it names both the
pad and the drum it plays, and sounds it. Pressing all sixteen again to arrive
back where you started was never setup.

**Your instrument sits beside the lesson.** The pattern chart already said
_when_; the picture of your own controller now says _where_ — the drums a lesson
uses named in the same colours the chart gives them, and lighting as you hit
them. During a run it appears under the highway when there is room for it.

**The catalogue is a drill-down.** `/lessons` opens on four tiers, each with the
question it answers; open a tier for its stages and a stage for its lessons.
Stages are numbered **within their tier**, so you read "Vocabulary · Stage 1"
rather than a running total, and a **Continue** button goes straight to where you
left off.

**Quote ratings follow you between devices**, and a failure in one part of sync
can no longer take the rest down with it — progress, runs and ratings now
reconcile independently, so one dataset erroring cannot abort or hide the others.

**A "How it works" section on the landing page**, with larger section headings
and even spacing.

**Lesson text names stages instead of numbering them** — "the alternation from
Pulse" rather than "Stage 1's alternation" — because tier-local numbering makes
a bare "Stage N" ambiguous.

**Fixes**

- A hi-hat pedal at rest reads as _open_, which is right for a drummer and
  useless here: the lessons are overwhelmingly closed hats, so every hat you hit
  scored nothing unless you held the footswitch down for the whole lesson. Worse,
  it failed silently — the controller picture lit either way, so the hits looked
  like they landed. A lesson that uses one hi-hat voice now pins the hat to it;
  only the two lessons using both leave the pedal in charge.

### Internal

- **A `Controller` abstraction** (`$lib/controller.svelte.ts`): one object for
  the student's instrument and a facade over what its inputs mean. `handle()`
  turns a MIDI message into a hit with the GM note already resolved, a pedal, a
  transport press, an unmapped note, or nothing — replacing a note map, a
  transport check and a geometry triple that each page assembled for itself.
  Grid and kit share one internal shape, so `kind` is consulted when building a
  controller and essentially nowhere afterwards.
- `$lib/controller-preview.svelte` becomes the only thing that draws pads, in
  three modes over geometry taken from the controller, absorbing and retiring
  `pad-grid.svelte` and `controller-map.svelte`.
- Kit profiles describe a model, never a MIDI note: a module's pads are
  reassignable from its own panel, so notes are always captured. Profile
  schematics are geometry-only SVGs under `static/kits/`, inlined so drums can
  be marked by id — first-party assets exclusively.
- `scripts/check-kits.py` fails `pnpm check` when a profile and its schematic
  drift apart in either direction. Not wired into `pnpm build`: `.vercelignore`
  excludes `scripts/`, so a build gated on it cannot run on the deploy host.
- Device identity folds in the manufacturer and strips zero-width and bidi
  control characters — the MD-90 appends U+202D to its maker string.
- A `device_layouts` table for opt-in sharing of a layout we have no profile
  for: insert-only, with no select policy for anyone, so it is a write-only
  mailbox rather than a catalogue the app reads back.
- `/debug/settings` refuses a drum kit rather than flattening it into the 4×4
  grid it hard-codes.
- Saved controller configs from before this release load unchanged and are never
  rewritten on read; the `notes`/`soundNotes` pair is still written for
  consumers that predate the class, so nothing needed migrating.
- OpenSpec: `edrum-support` change added; `lessons-layout` drafted and completed;
  `sync-local-data` planned and partly delivered.

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
