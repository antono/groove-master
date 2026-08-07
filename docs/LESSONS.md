# Managing lessons

How to add, edit and rebuild lessons. Three documents cover the curriculum and
they do not overlap:

| file                             | answers                                       |
| -------------------------------- | --------------------------------------------- |
| [`../LESSONS.md`](../LESSONS.md) | **what** — the lesson-by-lesson index         |
| [`curriculum.md`](curriculum.md) | **why** — ordering, complexity axes, research |
| this file                        | **how** — the mechanics of changing them      |

Nothing here is authored by hand in `static/`. Lessons are Python, and the MIDI
and the manifest the app reads are generated from it.

## The one command

```sh
python3 scripts/make-lessons.py
```

Re-run it after any change under `scripts/lessons/`. It rewrites every MIDI and
`static/lessons/manifest.json`, then prints how many lessons it wrote.

There is nothing to run for the samples — `render-drums.py` and `render-bass.py`
are separate, slow, and only needed when the SoundFonts or the drum layout
change, not when a lesson does.

## Where things live

```
scripts/
  make-lessons.py          the driver — walks the curriculum, numbers it, writes files
  lessons/
    __init__.py            CURRICULUM: the ordered list of stages
    schema.py              stage() module() lesson() checkpoint() planned()
    grids.py               patterns as beat offsets
    midi.py                bytes, GM note constants, the count-in
    bass.py                the backing lines
    stage01_pulse.py       one file per stage: patterns and prose side by side
    stage02_backbeat.py
    …
static/lessons/            GENERATED — never edit by hand
  manifest.json
  stage-01-pulse/kick-quarters.mid
```

The driver knows nothing about the curriculum. Everything a lesson _is_ lives in
its stage file.

## The model

```
Stage    a phase of the journey, with a stated goal
 Module  one technique — always exactly three lessons
  plain    the technique alone, nothing else sounding
  core     the technique in its normal musical form
  stretch  the technique pushed to its hardest useful variation
 Checkpoint  the stage's closing lesson (optional, one per stage)
```

`module()` **rejects** anything that is not exactly `plain, core, stretch` in
that order. That is deliberate: a module missing a tier is a module that has not
been thought through. Fill the gap with `planned()` rather than dropping it.

Currently: 4 stages, 21 playable lessons, 17 planned slots.

## Ids are permanent

A lesson's **id is its slug** (`kick-quarters`). The displayed `2.4` is derived
from position at build time and lives only in the manifest.

This is the one rule with consequences outside the build. A student's practice
history and their earned tempo ceiling are both keyed by slug in browser
storage. **Renaming a slug orphans them silently** — no error, the history just
stops existing. Insert, reorder and move lessons between stages freely; renaming
is the thing to avoid.

Old numeric ids from before the slug scheme are mapped in `LEGACY_IDS`
(`src/lib/stats.ts`), applied on read.

## Adding a lesson

1. **Write the pattern** as a builder taking a bar count and returning
   `(events, length_ticks)` — the `grids.py` helpers all do this:

   ```python
   from .grids import BACKBEAT, DOWNBEATS, voices
   from .midi import KICK, SNARE

   def backbeat_plain(bars=4):
       return voices(bars, (KICK, DOWNBEATS), (SNARE, BACKBEAT))
   ```

2. **Add the entry** to its module's `lessons` list in the stage file, replacing
   the `planned()` slot that held its place:

   ```python
   lesson(
       slug="backbeat-plain",       # permanent — see above
       name="The Backbeat",
       tier="core",                 # must match the slot it replaces
       drums=backbeat_plain,
       bass=QUARTER,
       prereq=["kick-quarters"],    # slugs; the driver checks they exist
       bpm=60,                      # default 60
       bars=4,                      # default 4
       summary="…",                 # one line, the catalogue card
       description="…",             # a paragraph, the lesson page
       hints=["…", "…"],            # practice tips under the schematic
   )
   ```

3. **Rebuild**: `python3 scripts/make-lessons.py`.

4. **Check it**: `pnpm dev`, open `/lessons`, play it.

### Three things the driver adds for you

Do not hand-roll any of these — `build_lesson()` puts them on every lesson, and
writing your own produces a double.

- **The count-in.** Three side-stick clicks on the last three beats of the
  lead-in bar; the pattern's own first beat stays silent, because it is the
  student's.
- **The closing hit.** Whatever sounds on beat 0 sounds once more on the bar
  line after the last bar, so the phrase lands rather than running out. It is
  scored, and the transport runs a beat past it so it can be played — see
  `TAIL_BEATS` in `$lib/midi.ts`. A stacked down-beat closes as the same stack.
- **The guide hat.** Only when the pattern has no hi-hat of its own: closed
  hats on the 8ths, well under the kit, audible but never shown or scored.

The bass lands its own resolution on that same closing beat (below), so the hit
and the tonic finish together.

## Adding a stage

Create `scripts/lessons/stageNN_<slug>.py` exporting a `STAGE = stage(...)`, then
add it to `CURRICULUM` in `scripts/lessons/__init__.py`. Those two edits are the
whole job — nothing else in the tree knows how many stages there are.

Give every stage a `closing=checkpoint(...)`: one bar of each pattern from that
stage, built with `cycle_bars()`. Practising one pattern until it is smooth
feels productive and retains poorly; interleaving competing patterns feels worse
and retains far better, so the checkpoint is where a stage is actually passed.

Stages 1 and 2 have theirs. Stages 3 and 4 do not yet — they are still being
filled in, and a checkpoint over patterns that are mostly `planned()` would have
nothing to interleave.

## Writing patterns

Positions are **beat offsets inside a bar**, as floats. `0` is the down-beat,
`1.5` is the "and" of 2, `2.25` is the "e" of 3.

| helper                                           | for                                         |
| ------------------------------------------------ | ------------------------------------------- |
| `voices(bars, (NOTE, positions), …)`             | every bar identical                         |
| `per_bar(bars, lambda i: …)`                     | bars that differ — hand swaps, feel changes |
| `alternating(bars, lead, other, positions)`      | hand-to-hand singles                        |
| `sticking(bars, lead, other, positions, "RLRR")` | rudiments                                   |
| `cycle_bars(bars, patterns)`                     | one bar of each — checkpoints               |

Named position sets: `BEATS`, `OFFBEATS`, `EIGHTHS`, `SIXTEENTHS`, `BACKBEAT`
(2 and 4), `DOWNBEATS` (1 and 3). Drum notes: `KICK`, `SNARE`, `CLOSED_HH`,
`OPEN_HH`, `SIDE_STICK` — the count-in owns the side stick.

## Choosing a backing bass

`bass.py` exports five lines, ordered by how much they help the student:

| line         | does                                            | most → least support |
| ------------ | ----------------------------------------------- | -------------------- |
| `ANSWER`     | replies on every off-beat, strictly diatonic    | most                 |
| `RIFF`       | a hook in the gaps, with rests and a turnaround |                      |
| `QUARTER`    | the root on every beat                          |                      |
| `OCTAVE`     | bounces on the 8ths, still rooted on the beat   |                      |
| `SYNCOPATED` | pushes between the hits and must be ignored     | least                |

**Support that never fades is not support.** A module opens on a line that marks
every beat and a stage ends on one that does not, where holding your own against
the bass is the exercise rather than an obstacle to the first note anyone plays.

Two things sink a line, and they are independent — both are worth checking
against the lesson's drum pattern before picking:

- **Placement.** A bass note struck at the same instant as a drum is not heard
  as bass at all; the kit wins. A lesson that plays on all four beats has no
  room on any of them, which is what `ANSWER` is for.
- **Motion.** A line that repeats one pitch is dull however it is placed.
  `QUARTER` is one pitch per bar, so it only works where the drums leave gaps.

Chromatic approach notes are a third trap: they pull one bar into the next
underneath a full groove, but over a bare pattern there is nothing sounding to
explain the dissonance and they just read as wrong notes. `ANSWER` is all chord
tones for that reason; `RIFF` is not, and belongs under busier lessons.

**Every line ends on the tonic, after the drums have stopped.** Each one leads
bar 4 toward the A without landing on it, so a run would otherwise end on a
question. `resolved()` supplies the answer on the closing beat — the one moment
in a lesson the bass is heard completely alone. New builders return through it
rather than returning their events directly:

```python
def my_bass(bars=4):
    events = [PROGRAM_CHANGE]
    ...
    return resolved(events, bars)   # not: return events, bars * BAR_TICKS
```

Everything in `bass.py` is in A minor, so `TONIC` is a module-level constant. A
line in another key would need its own root passed through.

Backing is never shown and never scored. `bass=None` is supported by the driver
— for a lesson where a second voice would only give the student somewhere else
to put a mistake — though no lesson uses it yet.

## Writing the prose

- `summary` — one line, on the catalogue card. What the lesson _is_.
- `description` — a paragraph, on the lesson page. What is new, and what is
  deliberately kept easy so the new thing is the only hard thing.
- `hints` — practice tips under the schematic. Specific and diagnostic: what a
  particular mistake sounds like and what to do about it beats general advice.

**Hints must never tell the student to change tempo.** The manifest BPM is the
tempo the lesson is written for; the tempo ladder is the student's own call and
is earned by clean runs, not something the lesson text should direct.

## What the driver guarantees

- **Duplicate slugs fail the run.** Two lessons with one id would share practice
  history.
- **Unknown `prereq` slugs fail the run.**
- **The tree is rebuilt, not written over.** Every `stage-*/` directory is
  removed first, so a renamed or deleted lesson cannot leave a stale MIDI being
  served.
- **`planned()` entries produce no MIDI.** They appear only in the manifest's
  `stages` outline, which is what renders them greyed out in the catalogue — so
  the road ahead is visible and filling a slot in later shifts nothing.
- **The manifest is written the way prettier writes JSON**, so regenerating is
  never a diff and the pre-commit hook does not rewrite it.

## After a change

```sh
python3 scripts/make-lessons.py   # regenerate
pnpm check                        # types
pnpm dev                          # play the lesson
```

Commit the generated `static/lessons/` output alongside the Python that produced
it — the app fetches the manifest at runtime and there is no build step that
regenerates it.
