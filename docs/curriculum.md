# Curriculum design

How Groove Academy's lessons are ordered, why, and where the ladder goes.

Stages 1 and 2 are built to this design; everything past Stage 3 is still a
plan. `LESSONS.md` is the lesson-by-lesson index and says what is live,
`AGENTS.md` is the record of how the machinery works.

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
runs straight through the stage (`2.1` … `2.9`), so nobody has to say "2.2.1".

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

Four tiers, ten stages, thirty modules, three lessons each. This is the shape;
the lesson-level index — every slug, tier, pattern and status — is
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
│   ├── [✓] The strike            quarters, one hand
│   ├── [→] Two hands             alternation
│   ├── [→] One hand, faster      density
│   └── [→] ◆ Checkpoint 1
│
└── Stage 2 · The Backbeat                 two and three voices; fixed fingers
    ├── [→] Trading               two voices, never together
    ├── [✓] Stacking              voices as one sound
    ├── [✓] The rock beat         the groove
    └── [→] ◆ Checkpoint 2

VOCABULARY ─ do you have hands, and things to say with them?
│
├── Stage 3 · Subdivision & the grid
│   ├── Sixteenths  ├── Triplets  ├── Feel  └── ◆ Checkpoint 3
│
├── Stage 4 · Sticking
│   ├── Strokes  ├── [✓] The paradiddle  ├── Bigger diddles  └── ◆ Checkpoint 4
│
├── Stage 5 · Syncopation & displacement
│   ├── Pushing  ├── Displacement  ├── Feel shifts  └── ◆ Checkpoint 5
│
└── Stage 6 · Dynamics                                    [⊘ velocity scoring]
    ├── Accents  ├── Ghost notes  └── Flams               [⊘ sub-grid scoring]

MUSIC ─ can you play something someone wants to hear?
│
├── Stage 7 · Form & fills                                [⊘ multi-bar phrases]
│   ├── Phrasing  ├── Fills  └── Form
│
└── Stage 8 · Styles                       one module per style, triad each
    ├── Rock  ├── Funk  ├── Hip-hop  ├── House & disco
    └── Breakbeat & DnB  ├── Jazz  ├── Latin  └── Reggae & afrobeat

MASTERY ─ can you make it your own?
│
├── Stage 9 · Independence & polyrhythm
│   ├── Ostinato  ├── Polyrhythm  └── Odd meters          [⊘ time signatures]
│
└── Stage 10 · Performance
    ├── Speed  ├── Repertoire  [⊘ long-form]  └── Your own voice
```

---

## 7. What the app needs, per stage

The roadmap outruns the engine in four specific places. Each is a small, bounded
piece of work that unlocks a whole stage.

| need                | blocks  | what it means                                                      |
| ------------------- | ------- | ------------------------------------------------------------------ |
| stage/module/prereq | all     | manifest fields + catalogue headings + a roadmap view              |
| velocity scoring    | Stage 6 | grade the note-on velocity we already receive and throw away today |
| multi-bar phrasing  | Stage 7 | generators and the chart assume a 4-bar loop of identical bars     |
| time signatures     | Stage 9 | `BEATS_PER_BAR = 4` is a constant in the generator and the page    |
| sub-grid tolerance  | flams   | a fixed ±ms window around a grid position marks a flam as an error |

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
generator split into `scripts/lessons/`, and Stages 1 and 2 written out in full
— nineteen playable lessons and two checkpoints where there were five lessons.

| was | is                  | stage | module         | tier    | now |
| --- | ------------------- | ----- | -------------- | ------- | --- |
| 1.1 | `kick-quarters`     | 1     | The strike     | plain   | 1.1 |
| 1.2 | `kick-hats-unison`  | 2     | Stacking       | plain   | 2.4 |
| 2.1 | `four-on-the-floor` | 2     | The rock beat  | core    | 2.8 |
| 2.2 | `disco-open-hats`   | 2     | The rock beat  | stretch | 2.9 |
| 3.1 | `paradiddle-single` | 4     | The paradiddle | plain   | 4.4 |

Every previously shipped lesson landed as a `plain` or the top of a module —
the diagnosis restated: the old curriculum was all peaks and no approach.

Stage 3 and the rest of Stage 4 are declared as `planned()` slots, so they hold
their numbers and show in the catalogue as the road ahead. Next up is Stage 3,
and then the two engine changes that unlock the most: **velocity scoring** (the
whole of Stage 6) and **mutable lanes**, which turn every existing lesson into
three drills without writing a note.

---

[qfg]: https://questforgroove.com/paths/
[fda]: https://www.fingerdrummingacademy.com/onlinecourse
[melodics]: https://melodics.com/finger-drumming
[drumeo]: https://www.drumeo.com/method
[trinity]: https://www.trinitycollege.com/resource?id=8831
[ci]: https://cognitivesciencesociety.org/cogsci20/papers/0469/0469.pdf
[music-ci]: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4989027/
