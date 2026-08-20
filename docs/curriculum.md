# Curriculum design

How Groove Academy's lessons are ordered, why, and where the ladder goes.

Stages 1 to 7 are built to this design (Stage 7 only in part); everything past
them is still a plan.
`LESSONS.md` is the lesson-by-lesson index and says what is live, `AGENTS.md` is
the record of how the machinery works.

---

## 1. Where we were

Five lessons, one flat grid, all 4 bars at 60 BPM, numbered `block.lesson` with
the blocks never named anywhere:

| id  | pads | subdivision | what is new                                     |
| --- | ---- | ----------- | ----------------------------------------------- |
| 1.1 | 1    | quarters    | the strike, the grid, the count-in              |
| 1.2 | 2    | quarters    | a second hand; two pads firing as one sound     |
| 2.1 | 3    | 8ths        | third voice **+** 8th hats **+** a triple stack |
| 2.2 | 4    | 8ths        | the hat hand travels between two pads           |
| 3.1 | 2    | 8ths        | sticking: hands alternate, then one doubles     |

Four problems fall out of that table.

**The 2.1 cliff.** Every other step adds one thing; 2.1 adds three — a third
voice, twice the subdivision, and the first three-note stack. It is where a
beginner stalls, and when they do there is nothing to drop back to.

**3.1 has no prerequisite.** The paradiddle asks the hands to alternate in 8ths
and then double. Nothing before it ever alternates hands — 1.2, 2.1 and 2.2 all
give each hand a fixed job on fixed beats. The skill it builds on was never
taught. It also stands alone: one rudiment, no variations, then the curriculum
stops.

**Tempo is not curriculum.** Every lesson is written at 60 and the slider is
left to the student. But tempo is the one axis that can deepen a lesson without
adding a note, and stats already record the BPM actually played — the ladder is
sitting there unused.

**The scaffold runs backwards.** The backing bass is support, and support should
fade. Today lesson 1.1 — the first thing anyone plays — gets `syncopated_bass`,
the line that deliberately pushes _against_ the student, while 3.1 gets the
plain quarter-note pulse. The lesson text argues for it, but a first lesson is
the wrong place to spend a beginner's attention on ignoring the bass.

Underneath all four: **the order lives in a Python list**. There is no declared
stage, no module, no prerequisite, so the app cannot show a path, recommend a next
step, or tell a student what they are ready for.

---

## 2. How people actually learn this

Every established finger-drumming and drum-set curriculum runs the same spine —
setup and pad layout, then strike technique, then beats, then a beat-building
system, then songs, then styles, then timing work, then "next level" hand
technique ([Quest for Groove][qfg], [Finger Drumming Academy][fda],
[Melodics][melodics]). Drum-set syllabi agree: rudiments and grooves first,
then independence, ghost notes, odd meters, improvisation ([Drumeo
Method][drumeo], [Trinity Grades][trinity]).

Six principles worth designing around, and what each one buys us:

**One new thing per lesson.** Working memory is the bottleneck long before the
fingers are. A lesson that changes two axes at once cannot tell the student
which one they failed. → the axis model in §3.

**Isolate, pair, then whole.** Established practice is to drill the hat hand
alone, then the pair, then the groove. Our hints already say this; the app
cannot do it. → mutable lanes, §7.

**Blocked practice, then interleaved.** Repeating one pattern feels productive
and produces the weakest retention. Interleaving competing patterns feels worse
during practice and retains far better — the classic result is a baseball study
where interleaved batters improved roughly twice as much as blocked ones on
identical pitch counts ([Shea & Morgan effect][ci]; replicated for music
performance, [Carter & Grahn 2016][music-ci]). → **checkpoint lessons**: at the
end of every stage, a 4-bar lesson whose bars are different patterns from that
stage. Cheap to generate, and it is the piece nobody ships.

**Spaced retrieval beats massed repetition.** We already log every scored run
with a day key. → surface "due for review" from stats rather than always
pointing at the next unplayed lesson.

**Deliberate practice sits at the edge of ability.** Not "play it again" —
"play it at 76 with 90% good". → **tempo belts**, §5.

**Scaffolding must fade.** The backing bass is a scaffold. Early in a module it
should double the pulse; late in a module it should syncopate against it; at the
top of a stage it should be optional or gone.

---

## 3. What makes a lesson hard

Ten independent axes. A new lesson moves **one**. This is the whole ordering
rule — everything in §6 is derived from it.

| #   | axis         | easy → hard                                                      |
| --- | ------------ | ---------------------------------------------------------------- |
| A   | voices       | 1 pad → 2 → 3 → 4 → 5+                                           |
| B   | subdivision  | quarters → 8ths → 16ths → triplets → mixed                       |
| C   | coordination | unison stack → trading → alternation → independence → polyrhythm |
| D   | sticking     | one hand → singles → doubles → paradiddle → inversions           |
| E   | placement    | on the beat → off-beat → 16th grid → displaced → across the bar  |
| F   | dynamics     | flat → accents → ghost notes → shaped lines                      |
| G   | hand travel  | fixed fingers → one hand moves → both move → crossing            |
| H   | form         | 1-bar loop → 2-bar phrase → fill → 8-bar form → song             |
| I   | feel         | straight → swung → half-time → double-time → laid-back           |
| J   | tempo        | the belt ladder (§5) — orthogonal to all of the above            |

Read the current curriculum through this and 2.1 moves A, B and C in one step,
which is exactly why it is the cliff.

---

## 4. Structure and numbering

Three levels, two of them numbered:

```
Stage    a phase of the journey, named, with a stated goal      "Stage 2 — The Backbeat"
 Module  one technique — always exactly three lessons           "Stacking"
  plain    the technique alone, nothing else sounding
  core     the technique in its normal musical form
  stretch  the technique pushed to its hardest useful variation
```

The **module** is what "simple technique first, then more and more complex
variations" asks for, and the fixed triad is what keeps it honest. `plain`
strips the technique to nothing else, so a failure can only mean one thing.
`core` is the form a musician actually plays. `stretch` is where the module is
genuinely hard, and it is the rung that carries a student into the next module
instead of leaving them at "well, I can do it slowly."

Modules are a catalogue heading, not a number: numbering stays two levels and
runs straight through the stage (`1.1` … `1.9`), so nobody has to say "1.2.1".
Stages themselves are numbered **within their tier** — every tier restarts at
Stage 1 — because in the drill-down catalogue a student is always inside a tier,
and a global "Stage 6 · Subdivision" reads oddly where "Vocabulary · Stage 1"
does not. The stage part of a lesson number is therefore tier-local too.

The lesson-by-lesson index is [`LESSONS.md`](../LESSONS.md).

### Ids must stop being numbers

`1.2` is currently three things at once: identity (`lesson-1.2.mid`, the stats
key `lesson: "1.2"`, `localStorage["groove-master:bpm:1.2"]`), sort order, and display
label. A curriculum built on "insert variations between existing lessons" will
renumber constantly, and every renumber orphans a student's practice history and
their remembered tempo.

Split them:

- **id** — a stable slug: `kick-quarters`, `rock-beat-8ths`, `paradiddle-single`.
  Never changes, never encodes position. Files become
  `stage-NN-<stage>/<slug>.mid` — see
  [file organisation](../LESSONS.md#organising-the-lesson-files).
- **stage / module / tier / order** — declared fields in the manifest. The displayed
  `2.4` is rendered from position, so inserting a lesson is a one-line change.
- **prereq** — a list of slugs. Turns the list into a graph, which is what makes
  a roadmap view, "recommended next", and gated unlocks possible at all.

Migration: keep a `LEGACY_IDS` map (`"1.2" → "kick-hats-unison"`) in the stats
read path so existing history reattaches. Do this before writing many more
lessons — the cost of the change grows with the lesson count.

---

## 5. Tempo belts

A lesson is not "done", it is done _at a tempo_. Since every scored run already
banks its BPM and accuracy, a lesson can carry a belt ladder for free:

```
bronze   the lesson's own BPM         ≥ 80% good-or-better, no misses
silver   +25%                         ≥ 85%
gold     +50%                         ≥ 90%
black    +100%                        ≥ 95%
```

This is the depth axis. It means five lessons can hold a student for months, it
gives the stats page something to be _for_, and it removes the temptation to
manufacture difficulty by piling on notes.

---

## 6. The roadmap

Four tiers, thirteen stages, three modules each, three lessons per module. This
is the shape; the lesson-level index — every slug, tier, pattern and status — is
[`LESSONS.md`](../LESSONS.md).

`[✓]` has lessons shipping today, `[→]` is the next batch to write, `[⊘]` is
blocked on an engineering prerequisite (§7).

```
FOUNDATIONS ─ can you keep time and stack two hands?
│
├── Stage 0 · Setup & Orientation
│   └── gear & 4×4 layout · hit-don't-press · reading the highway · how to practise
│
├── Stage 1 · Pulse                        one voice at a time; nothing stacks
│   ├── [✓] The strike  ├── [✓] Two hands  ├── [✓] One hand, faster  └── [✓] ◆ 1
│
├── Stage 2 · The Backbeat                 two and three voices; fixed fingers
│   ├── [✓] Trading  ├── [✓] Stacking  ├── [✓] The rock beat  └── [✓] ◆ 2
│
├── Stage 3 · Space                        the notes you do not play
│   ├── [✓] Holes  ├── [✓] Stop time  ├── [✓] Sparse  └── [✓] ◆ 3
│
├── Stage 4 · The Cymbals                  ride, crash, open hat; travel with a reason
│   ├── [✓] The ride  ├── [✓] The crash  ├── [✓] Open and closed  └── [✓] ◆ 4
│
└── Stage 5 · Two Bars                     form: a groove with an end
    ├── [✓] Question and answer  ├── [✓] Four bars  ├── [✓] The turnaround  └── [✓] ◆ 5

VOCABULARY ─ do you have hands, and things to say with them?
│
├── Stage 6 · Subdivision & the grid       two grids, three pads, no open hat
│   ├── [✓] Sixteenths  ├── [✓] Triplets  ├── [✓] Feel  └── [✓] ◆ 6
│
├── Stage 7 · Sticking
│   ├── Strokes  ├── [✓] The paradiddle  ├── Bigger diddles  └── ◆ 7
│
├── Stage 8 · Syncopation & displacement
│   ├── Pushing  ├── Displacement  ├── Feel shifts  └── ◆ 8
│
└── Stage 9 · Dynamics                                     [⊘ velocity scoring]
    ├── Accents  ├── Ghost notes  └── Flams                [⊘ sub-grid scoring]

MUSIC ─ can you play something someone wants to hear?
│
├── Stage 10 · Form & fills                                [⊘ 8-bar forms]
│   ├── Phrasing  ├── Fills  └── Form
│
└── Stage 11 · Styles                      one module per style, triad each
    ├── Rock  ├── Funk  ├── Hip-hop  ├── House & disco
    └── Breakbeat & DnB  ├── Jazz  ├── Latin  └── Reggae & afrobeat

MASTERY ─ can you make it your own?
│
├── Stage 12 · Independence & polyrhythm
│   ├── Ostinato  ├── Polyrhythm  └── Odd meters           [⊘ time signatures]
│
└── Stage 13 · Performance
    ├── Speed  ├── Repertoire  [⊘ long-form]  └── Your own voice
```

---

## 7. What the app needs, per stage

The roadmap outruns the engine in four specific places. Each is a small, bounded
piece of work that unlocks a whole stage.

| need                  | blocks   | what it means                                                           |
| --------------------- | -------- | ----------------------------------------------------------------------- |
| stage/module/prereq   | all      | manifest fields + catalogue headings + a roadmap view                   |
| velocity scoring      | Stage 9  | grade the note-on velocity we already receive and throw away today      |
| forms over 4 bars     | Stage 10 | a lesson is 4 bars; an 8-bar form needs the chart and highway to say so |
| time signatures       | Stage 12 | `BEATS_PER_BAR = 4` is a constant in the generator and the page         |
| sub-grid tolerance    | flams    | a fixed ±ms window around a grid position marks a flam as an error      |
| per-note match window | 16ths    | `MATCH_WINDOW_BEATS` is 0.4 beats, wider than a 16th at 0.25            |

**"Multi-bar phrasing" is no longer on this list.** It was, on the belief that
the generators and the chart assumed a 4-bar loop of identical bars; they do
not. `per_bar()` has always been able to differ bar by bar, the chart draws
whatever it is given, and Stage 5 · Two Bars is built entirely out of that. What
is genuinely missing for Music is length: a lesson is four bars, and an 8-bar
form has nowhere to go.

Two smaller ones worth doing early because they make existing lessons better
rather than adding new ones:

- **Mutable lanes on the resting page.** Every lesson's hints say "drill the hat
  hand alone first" and the app offers no way to do it. One toggle per lane on
  the schematic turns every existing lesson into three drills.
- **Checkpoint generation.** A builder that takes N patterns and emits one bar
  of each is a dozen lines, and it is what turns a stage from a list into
  something that retains.

---

## 8. What was done

The restructure landed: slug ids, stage/module/tier/prereq in the manifest, the
generator split into `scripts/lessons/`, and six stages written out in full —
fifty-six playable lessons and six checkpoints where there were five lessons.

| was | is                  | stage | module         | tier    | now |
| --- | ------------------- | ----- | -------------- | ------- | --- |
| 1.1 | `kick-quarters`     | 1     | The strike     | plain   | 1.1 |
| 1.2 | `kick-hats-unison`  | 2     | Stacking       | plain   | 2.4 |
| 2.1 | `four-on-the-floor` | 2     | The rock beat  | core    | 2.8 |
| 2.2 | `disco-open-hats`   | 2     | The rock beat  | stretch | 2.9 |
| 3.1 | `paradiddle-single` | 4     | The paradiddle | plain   | 4.4 |

Every previously shipped lesson landed as a `plain` or the top of a module —
the diagnosis restated: the old curriculum was all peaks and no approach.

Subdivision then landed whole. It moves exactly one axis — **B, subdivision** — and
holds every other one still: three pads for all ten lessons, no hand travel, no
open hat, kick and snare parked on the numbers wherever the point is the hat.
The two new grids arrive in the order they can be built from each other: 16ths
(two halved again), triplets (a division that shares nothing with them but the
beat), then the shuffle, which is a triplet with its middle note removed — a
relationship the code makes literal, since `triplets_broken` is derived from the
full triplet rather than written out beside it.

It also cost one new backing line. Every bass in `bass.py` was written on the
straight grid, and under triplets they stop sorting by support and start simply
landing on a slot the feel does not have, so the Feel and Triplets modules fade
`shuffle` → `quarter` → straight instead.

The rest of Sticking is still `planned()` slots, holding their numbers. Next are
the two engine changes that unlock the most: **velocity scoring** (the whole of
Stage 9, and the ghost notes the half-time shuffle is currently missing) and
**mutable lanes**, which turn every existing lesson into three drills without
writing a note.

---

[qfg]: https://questforgroove.com/paths/
[fda]: https://www.fingerdrummingacademy.com/onlinecourse
[melodics]: https://melodics.com/finger-drumming
[drumeo]: https://www.drumeo.com/method
[trinity]: https://www.trinitycollege.com/resource?id=8831
[ci]: https://cognitivesciencesociety.org/cogsci20/papers/0469/0469.pdf
[music-ci]: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4989027/

---

## 9. Foundations grew by three

Foundations shipped as two stages and a question — "can you keep time and stack
two hands?" — that they only half answered. Two more things belong under it
before a student is ready for Vocabulary, and one of them is not a rhythm at all.

**Stage 3 · Space** is the notes you do not play. Every pattern in it is Stage 2
with a beat, a half bar or a whole bar removed. It moves no axis at all in the
table above, which is the point: a hole is the _absence_ of complexity, and it is
where a beginner's time actually fails, because inside a run of notes the hands
cover for the clock.

**Stage 4 · The Cymbals** is the rest of the instrument. Ride, crash and open hat
— the three pads the on-screen controller ships with that the curriculum had
never asked for — so it moves **A** (voices) and **G** (hand travel) on rhythms
the student already owns. A crash is not a rhythm, it is a decision, and it is
the first one a student makes with a hand rather than a finger.

**Stage 5 · Two Bars** is **H** (form), one bar early. Nothing in it is finer
than an 8th or off the beat; what is new is that four bars are one thing rather
than four attempts at the same thing, and that it is possible to play every note
correctly and still play it wrongly by losing your place.

Inserting them moved every stage number from Subdivision onwards up by three.
Nothing a student owns moved with it: practice history and tempo ceilings are
keyed by slug, and the displayed number has always been rendered from position.
