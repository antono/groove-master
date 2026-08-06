# Lessons

The curriculum, lesson by lesson. This file is the **index**: what each lesson
is, what is new in it, and whether it exists yet. The reasoning behind the
ordering — the complexity axes, the numbering scheme, the learning research —
lives in [`docs/curriculum.md`](docs/curriculum.md).

## Shape

```
Stage    a phase of the journey, with a stated goal        "Stage 2 — The Backbeat"
 Module  one technique, always exactly three lessons       "Stacking"
  plain    the technique alone, nothing else sounding
  core     the technique in its normal musical form
  stretch  the technique pushed to its hardest useful variation
```

**Three lessons per module, always.** `plain` strips the technique to nothing
else, so a failure can only mean one thing. `core` is the form a musician
actually plays. `stretch` is where the module is genuinely hard, and it is the
rung that carries a student into the next module rather than leaving them at
"well, I can do it slowly."

Numbering stays two levels — `2.4` — and runs straight through the stage.
Modules are headings, not numbers; nobody should have to say "2.2.1". The
displayed number is rendered from position; the **id is the slug**, and never
changes (see [Ids](docs/curriculum.md#ids-must-stop-being-numbers)).

**Status** — `live` ships today · `next` is the batch to write now · `todo` is
planned · `blocked` needs an engine change first ([§7](docs/curriculum.md#7-what-the-app-needs-per-stage)).

**Axis** — the one thing a lesson adds. Within a module the axis is the
module's own; across modules it is the next one along:

|                |                   |                    |                |                 |
| -------------- | ----------------- | ------------------ | -------------- | --------------- |
| **A** voices   | **B** subdivision | **C** coordination | **D** sticking | **E** placement |
| **F** dynamics | **G** hand travel | **H** form         | **I** feel     | **J** tempo     |

---

## Stage 0 · Setup & Orientation

Not scored lessons — the wizard and the docs. Mapping the controller, the 4×4
layout, _hit don't press_ (a wrist drop, not a button push), reading the
highway, the count-in, and what the four grades mean.

## Stage 1 · Pulse

**Goal** — a steady internal clock and a strike that lands where you meant it.
One voice sounding at a time; nothing ever stacks. This stage sets the hand
convention the rest of the curriculum assumes: **strong hand plays kick and
snare, weak hand plays the hi-hats.**

### Module: The strike — one hand, quarter notes

| #   | slug                 | tier    | status | pattern                            | bass    |
| --- | -------------------- | ------- | ------ | ---------------------------------- | ------- |
| 1.1 | `kick-quarters`      | plain   | live   | kick on all four beats             | quarter |
| 1.2 | `hats-quarters`      | core    | live   | the same four beats, weak hand     | quarter |
| 1.3 | `quarters-hand-swap` | stretch | live   | quarters, hands swapping every bar | quarter |

### Module: Two hands — alternation

| #   | slug                    | tier    | status | pattern                                 | bass       |
| --- | ----------------------- | ------- | ------ | --------------------------------------- | ---------- |
| 1.4 | `alternating-quarters`  | plain   | live   | snare / hat / snare / hat, one per beat | walking    |
| 1.5 | `alternating-8ths`      | core    | live   | the single stroke roll in 8ths          | quarter    |
| 1.6 | `alternating-8ths-swap` | stretch | live   | the same, lead hand flips every bar     | syncopated |

### Module: One hand, faster — density

| #   | slug                    | tier    | status | pattern                                                | bass       |
| --- | ----------------------- | ------- | ------ | ------------------------------------------------------ | ---------- |
| 1.7 | `eighths-strong-hand`   | plain   | live   | eight 8ths a bar on the snare, one hand                | quarter    |
| 1.8 | `eighths-weak-hand`     | core    | live   | the same, weak hand on the hi-hat                      | quarter    |
| 1.9 | `eighths-through-rests` | stretch | live   | 8ths with beat 3 silent — hold the grid through a hole | syncopated |

**◆ Checkpoint 1** `checkpoint-1` — one bar each of 1.1 / 1.5 / 1.8 / 1.9.

> Two hands sharing 8ths (1.5) is easier than one hand playing them (1.7), so
> alternation comes before density. `kick-quarters` used to ship with the
> syncopated bass; it now opens on `quarter` — the first lesson anyone plays is
> the wrong place to spend attention on ignoring the backing, and the syncopated
> line does more good at the top of the stage where holding your own against it
> is the exercise.

## Stage 2 · The Backbeat

**Goal** — two and three voices, including the first pads that must fire as one
sound. Fixed finger positions throughout; no hand travels until 2.9.

### Module: Trading — two voices, never together

| #   | slug                   | tier    | status | pattern                                                   | bass    |
| --- | ---------------------- | ------- | ------ | --------------------------------------------------------- | ------- |
| 2.1 | `backbeat-plain`       | plain   | live   | kick 1 & 3, snare 2 & 4                                   | quarter |
| 2.2 | `kick-snare-8ths`      | core    | live   | kick on the numbers, snare on the "and"s                  | quarter |
| 2.3 | `trading-three-voices` | stretch | live   | kick / snare / hat rotating through 8ths — nothing stacks | quarter |

### Module: Stacking — voices as one sound

| #   | slug                     | tier    | status | pattern                                                             | bass    |
| --- | ------------------------ | ------- | ------ | ------------------------------------------------------------------- | ------- |
| 2.4 | `kick-hats-unison`       | plain   | live   | hat on all four, kick on 1 & 3 — the first stack                    | quarter |
| 2.5 | `rock-beat-quarter-hats` | core    | live   | + snare on 2 & 4 — something stacks on every beat                   | quarter |
| 2.6 | `stack-every-beat`       | stretch | live   | kick + hat on all four, snare on 2 & 4 — a triple stack twice a bar | octave  |

### Module: The rock beat — the groove

| #   | slug                 | tier    | status | pattern                                        | bass   |
| --- | -------------------- | ------- | ------ | ---------------------------------------------- | ------ |
| 2.7 | `rock-beat-8th-hats` | plain   | live   | kick 1 & 3, snare 2 & 4, hats in 8ths          | octave |
| 2.8 | `four-on-the-floor`  | core    | live   | kick on all four under 8th hats                | octave |
| 2.9 | `disco-open-hats`    | stretch | live   | open hats on the "and"s — the hat hand travels | octave |

**◆ Checkpoint 2** `checkpoint-2` — one bar each of 2.1 / 2.5 / 2.8 / 2.9.

> This stage is where the cliff was. The old curriculum jumped from
> `kick-hats-unison` straight to `four-on-the-floor`, adding a third voice,
> doubling the subdivision and introducing the first triple stack in one step.
> 2.5, 2.6 and 2.7 are the rungs that were missing.

## Stage 3 · Subdivision & the grid

**Goal** — the 16th grid and the triplet grid, and a note placed anywhere on
either.

### Module: Sixteenths

| #   | slug               | tier    | status | pattern                                          |
| --- | ------------------ | ------- | ------ | ------------------------------------------------ |
| 3.1 | `hats-16ths-split` | plain   | todo   | 16th hats shared between the hands, nothing else |
| 3.2 | `rock-16th-hats`   | core    | todo   | the same over a backbeat                         |
| 3.3 | `kick-16th-grid`   | stretch | todo   | kick on the "e" and the "a"                      |

### Module: Triplets

| #   | slug              | tier    | status | pattern                                        |
| --- | ----------------- | ------- | ------ | ---------------------------------------------- |
| 3.4 | `triplets-8th`    | plain   | todo   | 8th-note triplets, hand to hand                |
| 3.5 | `triplet-groove`  | core    | todo   | triplet hats over a backbeat                   |
| 3.6 | `triplets-broken` | stretch | todo   | the middle note dropped — the shuffle skeleton |

### Module: Feel

| #   | slug                | tier    | status | pattern                                                 |
| --- | ------------------- | ------- | ------ | ------------------------------------------------------- |
| 3.7 | `shuffle-hats`      | plain   | todo   | swung 8ths on the hat                                   |
| 3.8 | `shuffle-groove`    | core    | todo   | the full shuffle with kick and backbeat                 |
| 3.9 | `half-time-shuffle` | stretch | todo   | the shuffle at half time (ghost notes wait for Stage 6) |

**◆ Checkpoint 3** — straight 16ths / triplets / shuffle / half-time shuffle.

## Stage 4 · Sticking

**Goal** — rudiments, then rudiments inside a groove. _Which_ hand plays a note
starts to matter as much as when.

### Module: Strokes

| #   | slug            | tier    | status | pattern                     |
| --- | --------------- | ------- | ------ | --------------------------- |
| 4.1 | `singles-16ths` | plain   | todo   | single stroke roll in 16ths |
| 4.2 | `doubles-8ths`  | core    | todo   | R R L L in 8ths             |
| 4.3 | `doubles-16ths` | stretch | todo   | R R L L in 16ths            |

### Module: The paradiddle

| #   | slug                    | tier    | status | pattern                                              |
| --- | ----------------------- | ------- | ------ | ---------------------------------------------------- |
| 4.4 | `paradiddle-single`     | plain   | live   | R L R R / L R L L in 8ths                            |
| 4.5 | `paradiddle-groove`     | core    | todo   | the paradiddle across hat and snare, kick underneath |
| 4.6 | `paradiddle-inversions` | stretch | todo   | the four inversions, one per bar                     |

### Module: Bigger diddles

| #   | slug                | tier    | status | pattern                   |
| --- | ------------------- | ------- | ------ | ------------------------- |
| 4.7 | `paradiddle-double` | plain   | todo   | R L R L R R / L R L R L L |
| 4.8 | `paradiddle-diddle` | core    | todo   | R L R R L L               |
| 4.9 | `six-stroke-roll`   | stretch | todo   | R L L R R L               |

**◆ Checkpoint 4** — singles / doubles / paradiddle / an inversion.

> `paradiddle-single` ships today as lesson 3.1, with nothing before it that
> ever alternates the hands. Stage 1's `alternating-8ths` and this stage's
> `singles` and `doubles` are its missing prerequisites.

## Stage 5 · Syncopation & displacement

**Goal** — playing against the grid without losing it.

### Module: Pushing

| #   | slug          | tier    | status | pattern                        |
| --- | ------------- | ------- | ------ | ------------------------------ |
| 5.1 | `upbeat-hats` | plain   | todo   | hats on the off-beats only     |
| 5.2 | `kick-pushed` | core    | todo   | kick on the "and" of 2 and 4   |
| 5.3 | `all-upbeats` | stretch | todo   | the whole groove on the "and"s |

### Module: Displacement

| #   | slug                   | tier    | status | pattern                              |
| --- | ---------------------- | ------- | ------ | ------------------------------------ |
| 5.4 | `snare-displaced-8th`  | plain   | todo   | backbeat moved to the "and"          |
| 5.5 | `snare-displaced-16th` | core    | todo   | backbeat on the "a" of 2             |
| 5.6 | `groove-displaced`     | stretch | todo   | the whole groove shifted a 16th late |

### Module: Feel shifts

| #   | slug          | tier    | status | pattern                                     |
| --- | ------------- | ------- | ------ | ------------------------------------------- |
| 5.7 | `half-time`   | plain   | todo   | one backbeat per bar                        |
| 5.8 | `double-time` | core    | todo   | the same groove at twice the density        |
| 5.9 | `feel-switch` | stretch | todo   | half and double time, alternating every bar |

**◆ Checkpoint 5** — pushed / displaced / half / double.

## Stage 6 · Dynamics · blocked

We receive note-on velocity and throw it away. Grading it unlocks this whole
stage — and with it the difference between a beginner's groove and a
musician's.

### Module: Accents

| #   | slug                   | tier    | status  | pattern                                |
| --- | ---------------------- | ------- | ------- | -------------------------------------- |
| 6.1 | `hat-accents-quarters` | plain   | blocked | accent the numbers, ghost the rest     |
| 6.2 | `hat-accents-8ths`     | core    | blocked | an accent pattern across 8th hats      |
| 6.3 | `hat-shaping`          | stretch | blocked | a hat line shaped across the whole bar |

### Module: Ghost notes

| #   | slug              | tier    | status  | pattern                                 |
| --- | ----------------- | ------- | ------- | --------------------------------------- |
| 6.4 | `ghost-single`    | plain   | blocked | one ghosted snare between the backbeats |
| 6.5 | `ghost-funk`      | core    | blocked | the ghost-note funk groove              |
| 6.6 | `ghost-16th-funk` | stretch | blocked | ghosts on the full 16th grid            |

### Module: Flams — also needs sub-grid scoring

| #   | slug          | tier    | status  | pattern                  |
| --- | ------------- | ------- | ------- | ------------------------ |
| 6.7 | `flam-snare`  | plain   | blocked | two hands a hair apart   |
| 6.8 | `flam-accent` | core    | blocked | the flam accent rudiment |
| 6.9 | `flam-groove` | stretch | blocked | flams on the backbeat    |

## Stage 7 · Form & fills · blocked

Generators and the chart assume a loop of identical bars. Phrases need bars
that differ.

### Module: Phrasing

| #   | slug              | tier    | status  | pattern                    |
| --- | ----------------- | ------- | ------- | -------------------------- |
| 7.1 | `two-bar-phrase`  | plain   | blocked | bar 2 answers bar 1        |
| 7.2 | `crash-on-one`    | core    | blocked | the downbeat of the phrase |
| 7.3 | `four-bar-phrase` | stretch | blocked | a four-bar shape           |

### Module: Fills

| #   | slug             | tier    | status  | pattern               |
| --- | ---------------- | ------- | ------- | --------------------- |
| 7.4 | `fill-one-beat`  | plain   | blocked | a fill on beat 4      |
| 7.5 | `fill-two-beats` | core    | blocked | half a bar of fill    |
| 7.6 | `fill-one-bar`   | stretch | blocked | a full bar every four |

### Module: Form

| #   | slug                 | tier    | status  | pattern                                |
| --- | -------------------- | ------- | ------- | -------------------------------------- |
| 7.7 | `groove-fill-groove` | plain   | blocked | back into the groove without a stumble |
| 7.8 | `fill-from-rudiment` | core    | blocked | fill vocabulary built from Stage 4     |
| 7.9 | `eight-bar-form`     | stretch | blocked | a whole section                        |

## Stage 8 · Styles

**Goal** — the same skills, spoken in different accents. One module per style,
each with its own plain / core / stretch. All `todo`.

| module            | plain             | core                | stretch        |
| ----------------- | ----------------- | ------------------- | -------------- |
| Rock              | straight 8ths     | 16th hats           | punk           |
| Funk              | 16th kick         | "the one"           | ghost funk     |
| Hip-hop           | boom bap          | laid-back placement | trap hats      |
| House & disco     | four on the floor | open hats           | shuffled house |
| Breakbeat & DnB   | the amen          | chopped amen        | two-step       |
| Jazz              | the ride pattern  | ride + comping      | brushes        |
| Latin             | bossa nova        | samba               | songo          |
| Reggae & afrobeat | one-drop          | steppers            | afrobeat       |

## Stage 9 · Independence & polyrhythm

### Module: Ostinato

| #   | slug               | tier    | status | pattern                               |
| --- | ------------------ | ------- | ------ | ------------------------------------- |
| 9.1 | `ostinato-vary`    | plain   | todo   | one hand fixed, the other varies      |
| 9.2 | `ostinato-melodic` | core    | todo   | the free hand moves across pads       |
| 9.3 | `linear`           | stretch | todo   | linear drumming — nothing ever stacks |

### Module: Polyrhythm

| #   | slug              | tier    | status | pattern     |
| --- | ----------------- | ------- | ------ | ----------- |
| 9.4 | `three-over-four` | plain   | todo   | 3 against 4 |
| 9.5 | `four-over-three` | core    | todo   | 4 against 3 |
| 9.6 | `five-over-four`  | stretch | todo   | 5 against 4 |

### Module: Odd meters — needs time-signature support

| #   | slug                | tier    | status  | pattern                 |
| --- | ------------------- | ------- | ------- | ----------------------- |
| 9.7 | `odd-5-4`           | plain   | blocked | 5/4                     |
| 9.8 | `odd-7-8`           | core    | blocked | 7/8                     |
| 9.9 | `metric-modulation` | stretch | blocked | the pulse reinterpreted |

## Stage 10 · Performance

### Module: Speed

| #    | slug               | tier    | status | pattern                              |
| ---- | ------------------ | ------- | ------ | ------------------------------------ |
| 10.1 | `one-handed-16ths` | plain   | todo   | 16th hats on one hand under a groove |
| 10.2 | `finger-rolls`     | core    | todo   | rolls and buzzes                     |
| 10.3 | `belt-ladder`      | stretch | todo   | every earlier lesson taken to gold   |

### Module: Repertoire

| #    | slug            | tier    | status  | pattern                             |
| ---- | --------------- | ------- | ------- | ----------------------------------- |
| 10.4 | `transcribe`    | plain   | todo    | learn a groove by ear, then play it |
| 10.5 | `full-song`     | core    | blocked | a song top to bottom                |
| 10.6 | `trading-fours` | stretch | blocked | improvise the answering bar         |

### Module: Your own voice

| #    | slug              | tier    | status | pattern                         |
| ---- | ----------------- | ------- | ------ | ------------------------------- |
| 10.7 | `own-beat`        | plain   | todo   | build one groove of your own    |
| 10.8 | `own-fills`       | core    | todo   | a fill vocabulary that is yours |
| 10.9 | `improvise-a-set` | stretch | todo   | eight bars, no chart            |

---

## Tempo belts

A lesson is not finished, it is finished _at a tempo_. Every scored run already
banks its BPM and accuracy, so each lesson carries the same ladder:

| belt   | tempo                | accuracy                        |
| ------ | -------------------- | ------------------------------- |
| bronze | the lesson's own BPM | ≥ 80% good-or-better, no misses |
| silver | +25%                 | ≥ 85%                           |
| gold   | +50%                 | ≥ 90%                           |
| black  | +100%                | ≥ 95%                           |

Stage 1 and 2 are written at 60. From Stage 3 the written BPM is the lesson's
floor, not its ceiling — depth comes from the ladder, never from piling on more
notes. `stretch` lessons are hard by _pattern_; belts are hard by _tempo_. Keep
the two apart or neither means anything.

## Bass lines

The backing bass is the lesson's scaffold, and for a long time every line was
some arrangement of one root note hammered on the beat. Two separate things
were wrong with that.

**A bass note struck at the same instant as a drum is not a bass note.** Same
attack, and the kit wins — the line is inaudible as a voice of its own no
matter how good the notes are. Every live lesson puts drums on all four beats
and most of them on all eight 8ths, so a bass on the beats is masked _by
construction_, everywhere. This is the bigger of the two problems and it still
applies to `quarter`, `octave` and `syncopated`.

**Support and interest are different axes.** A line can mark the pulse as
reliably as a metronome and still move; what made the early lessons dull was
the repeated pitch, not the placement.

So a line is judged on both: where it sits relative to the drums, and whether
it goes anywhere.

| line      | sits                                 | support | character                        |
| --------- | ------------------------------------ | ------- | -------------------------------- |
| `walking` | anchor on 1, then all four off-beats | highest | jazz/blues motion, pulls forward |
| `riff`    | a motif with rests in it             | medium  | memorable, has an identity       |
| `pedal`   | one long root, then a scramble       | medium  | stillness against motion         |
| `dub`     | the down-beat left empty             | lowest  | attitude, resists the student    |

**1 · Walking** — _implemented, live on 1.4._ Over Am - F - C - G. The root
anchors beat 1 with the snare and everything else lands on the off-beats, so a
bass note sounds in **every hole the drums leave** — 16 of its 20 notes are the
only thing playing at that moment. Pitches never repeat inside a bar, and the
last off-beat is a chromatic leading note resolving a semitone into the next
bar's root, so the four bars turn over as a phrase rather than stopping: G#
pulls up to A and the loop closes without a seam.

**2 · Riff** — a two-bar motif with holes in it, repeated. Root on 1, a jump to
the 5th on the "and" of 2, silence across 3, a walk-up on 4. The rests are the
point: a repeated shape is something you can remember and play _against_ rather
than merely follow. Medium support — 1 and 4 are marked, 3 is not.

**3 · Pedal & answer** — a long root under the first half of the bar, then a
burst of 16th-note melody in the second half. The contrast does the work: two
beats of stillness make the answer an event. Best under the dense lessons,
where the 16th answer is the only line that can find a gap at all.

**4 · Dub drop** — beat 1 is **empty**, and the line enters on the "and" of 1
or on beat 3, sparse and syncopated with long decays. Nothing marks the
down-beat, so the student has to be the one who knows where it is. The natural
end-of-stage line, replacing `syncopated`.

`quarter`, `octave` and `syncopated` are still in use and all three are masked
by the drums above them. They should retire as the four above land — `walking`
and `dub` already do their pedagogical jobs, audibly.

> **Rule for a new line: check it against the lesson's drum pattern, not just
> its position in the stage.** Under 8th-note drums the only free slots are
> 16ths. A line written without looking at what is on top of it will not be
> heard.

## Checkpoints

Every stage ends with a `◆` checkpoint: four bars, each a different pattern
from that stage, usually the plain and stretch ends of each module. Practising
one pattern until it is smooth feels productive and retains poorly;
interleaving competing patterns feels worse and retains far better. The
checkpoint is where a stage is actually passed.

---

## Organising the lesson files

Both of these are in place — this is how the tree works now, not a proposal.

### Generated MIDI — a directory per stage, filenames by slug

```
static/lessons/
  manifest.json
  stage-01-pulse/
    kick-quarters.mid
    hats-quarters.mid
    …
  stage-02-backbeat/
    backbeat-plain.mid
    …
```

Filenames carry the **slug only** — no numbers. Order lives in the manifest and
nowhere else, so inserting a lesson is a one-line change instead of a rename
cascade, and a lesson that moves stages is a `git mv` with its id, its stats
history and its remembered tempo intact. The stage directory is for humans
browsing the folder; nothing reads it. `make-lessons.py` rebuilds the tree on
every run, so a renamed lesson cannot leave a stale MIDI behind still being
served.

### The generator — a module per stage

`make-lessons.py` is now only a driver. The curriculum lives in
`scripts/lessons/`, split by what changes together:

```
scripts/
  make-lessons.py          driver: walk the curriculum, write MIDI + manifest
  lessons/
    __init__.py            CURRICULUM = [stage01.STAGE, stage02.STAGE, …]
    schema.py              stage() / module() / lesson() / planned() / checkpoint()
    midi.py                varint, build_track, write_midi, hit, bass_note, PPQ
    grids.py               voices(), per_bar(), alternating(), sticking(), cycle_bars()
    bass.py                QUARTER, OCTAVE, SYNCOPATED
    stage01_pulse.py       patterns + prose for Stage 1
    stage02_backbeat.py    …
```

Each stage file exports one structure, patterns and prose side by side:

```python
STAGE = stage(
    number=1, slug="pulse", title="Pulse", goal="…",
    modules=[
        module("the-strike", "The strike", "one hand, quarter notes", [
            lesson(slug="kick-quarters", tier="plain", drums=kick_quarters, …),
            …
        ]),
    ],
    closing=checkpoint(slug="checkpoint-1", …),
)
```

Three things this buys:

- **Prose next to its pattern.** The builders used to sit at the top of one file
  and their descriptions three hundred lines below, joined only by a function
  reference. Checking "does this hint describe this pattern" meant scrolling.
- **Patterns as positions.** `voices(bars, (KICK, BEATS), (SNARE, BACKBEAT))`
  says once what five hand-rolled bar loops used to, and no lesson re-derives
  `bar * bar_ticks`.
- **A stage is one file.** Writing Stage 3 touches `stage03_subdivision.py` and
  nothing else; a bad triad can be reverted without reading the rest.

`module()` refuses anything that is not exactly plain / core / stretch, and the
driver refuses duplicate slugs or a `prereq` naming a lesson that does not
exist — the two mistakes that are easy to make and hard to see.

### Manifest

Two keys. `lessons` is the playable set: `id` (slug), `number`, `file`, `stage`,
`module`, `tier`, `prereq`, plus `name`, `bpm`, `bars`, `summary`,
`description`, `hints`. `stages` is the outline the catalogue renders its
headings from — stage titles and goals, module titles and subtitles, and every
slot including the `planned` ones.

Practice history recorded under the old numeric ids reattaches through
`LEGACY_IDS` in `$lib/stats.ts`, applied on read. A remembered tempo under an
old key is not migrated: it is one slider drag to set again.

## Conventions for a new lesson

- **One new thing.** Name the axis before writing the pattern. If you cannot
  name exactly one, it is two lessons.
- **Three per module, no exceptions.** If a technique only has two useful
  forms, it is not a module — fold it into a neighbour. If it has five, it is
  two modules.
- **plain must be boring.** If the plain lesson has anything in it besides the
  technique, a student who fails it learns nothing from failing.
- **The scaffold fades.** Early in a stage the bass marks every beat; late in a
  stage it stops. Support that never fades is not support — but see
  [Bass lines](#bass-lines): fading the support is not a reason to make the
  line dull, and a line that marks the pulse can still move.
- **Hints never mention tempo.** The written BPM is the lesson's; the slider is
  the student's.
- **Every lesson counts in** — three side-stick clicks, added automatically by
  `build_lesson`.
