# Changelog

Notable changes, newest first. **User-facing** is anything you would notice
while practising; **internal** is everything else — tooling, docs, and work that
only shows up in how the project is built.

Announcements for each release live in [`/news`](src/lib/news/); this file is
the complete list, that one is the readable half.

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
