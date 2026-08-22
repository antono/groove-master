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
| 1.4 | `alternating-quarters`  | plain   | live   | snare / hat / snare / hat, one per beat | riff       |
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

## Stage 3 · Space

**Goal** — the notes you do not play. A groove you already own with a beat, a
half bar or a whole bar taken out of it, and coming back in exactly on time.

No new pad, no finer grid, no hand travel: every pattern here is Stage 2 with
something removed. Silence is where a beginner's time actually fails — inside a
run of notes the hands cover for the clock, and the moment nothing sounds the
clock is all there is.

### Module: Holes — a beat taken out

| #   | slug                  | tier    | status | pattern                                    | bass       |
| --- | --------------------- | ------- | ------ | ------------------------------------------ | ---------- |
| 3.1 | `groove-hole-3`       | plain   | live   | the rock beat with beat 3 emptied          | quarter    |
| 3.2 | `groove-hole-bar-end` | core    | live   | beat 4 emptied — re-enter on the down-beat | octave     |
| 3.3 | `holes-walking`       | stretch | live   | the hole moves a beat later each bar       | syncopated |

### Module: Stop time — a bar with nothing in it

| #   | slug                   | tier    | status | pattern                                 | bass       |
| --- | ---------------------- | ------- | ------ | --------------------------------------- | ---------- |
| 3.4 | `stop-every-other-bar` | plain   | live   | one bar of groove, one bar of nothing   | quarter    |
| 3.5 | `stop-and-answer`      | core    | live   | one snare on beat 4 of the empty bar    | riff       |
| 3.6 | `stops-alternating`    | stretch | live   | two beats on, two off — the halves swap | syncopated |

### Module: Sparse — almost nothing, exactly on time

| #   | slug              | tier    | status | pattern                                | bass       |
| --- | ----------------- | ------- | ------ | -------------------------------------- | ---------- |
| 3.7 | `whole-notes`     | plain   | live   | kick and hat on beat 1, nothing else   | quarter    |
| 3.8 | `half-notes`      | core    | live   | kick on 1, snare on 3, a hat with each | octave     |
| 3.9 | `sparse-doubling` | stretch | live   | one hit, two, four, eight — same pulse | syncopated |

**◆ Checkpoint 3** `checkpoint-3` — a hole, a whole empty bar, a crawl, a half
bar: four bars, four different silences.

> The backing bass matters more in this stage than anywhere else in the
> curriculum, because during a hole it is the only thing left. That is why these
> lessons fade from `quarter` — a note on every beat you are missing — to
> `syncopated`, which is no help at all.

## Stage 4 · The Cymbals

**Goal** — the three pads beyond the core three: ride, crash and open hat. The
same time on a different cymbal, and the first hand travel with a musical reason
rather than a rhythmic one.

Kick, snare, closed hat, open hat, ride and crash are exactly the six pads the
on-screen controller ships with, so every lesson here is playable with no
hardware at all. Toms are not in that set and so are not in the curriculum.

### Module: The ride — a second timekeeper

| #   | slug             | tier    | status | pattern                                 | bass    |
| --- | ---------------- | ------- | ------ | --------------------------------------- | ------- |
| 4.1 | `ride-quarters`  | plain   | live   | ride on all four, kick on 1 & 3         | quarter |
| 4.2 | `rock-beat-ride` | core    | live   | the rock beat with the ride on the 8ths | octave  |
| 4.3 | `hat-to-ride`    | stretch | live   | two bars hat, two bars ride — travel    | octave  |

### Module: The crash — the note that opens a phrase

| #   | slug              | tier    | status | pattern                                      | bass       |
| --- | ----------------- | ------- | ------ | -------------------------------------------- | ---------- |
| 4.4 | `crash-on-one`    | plain   | live   | crash on every down-beat — a three-pad stack | quarter    |
| 4.5 | `crash-every-two` | core    | live   | crash on bars 1 and 3 — the two-bar phrase   | octave     |
| 4.6 | `crash-into-ride` | stretch | live   | crash on 1, ride from the "and"              | syncopated |

### Module: Open and closed — the hat that hands the bar over

| #   | slug               | tier    | status | pattern                                 | bass       |
| --- | ------------------ | ------- | ------ | --------------------------------------- | ---------- |
| 4.7 | `open-hat-lead-in` | plain   | live   | closed hats with the last 8th opened up | quarter    |
| 4.8 | `crash-after-open` | core    | live   | the open hat landing on a crash         | octave     |
| 4.9 | `every-pad`        | stretch | live   | hats and open hat, then ride and crash  | syncopated |

**◆ Checkpoint 4** `checkpoint-4` — one bar each of 4.2 / 4.4 / 4.7 / 4.6: the
timekeeping hand on a different pad in every bar.

## Stage 5 · Two Bars

**Goal** — a groove with a beginning and an end. Bar 2 answers bar 1, a cymbal
marks the top of the phrase, and the last two beats hand it back.

Nothing here is finer than an 8th note and nothing lands off the beat, because
the new axis is **form** (H) and a stage that moved form and subdivision at once
could not tell the student which one they failed. Music's Stage 10 keeps fills
and 8-bar form; this is the two-bar unit they are built from.

### Module: Question and answer — bar two replies

| #   | slug            | tier    | status | pattern                                 | bass       |
| --- | --------------- | ------- | ------ | --------------------------------------- | ---------- |
| 5.1 | `two-bar-kick`  | plain   | live   | bar 2 adds one kick, on beat 4          | quarter    |
| 5.2 | `two-bar-snare` | core    | live   | bar 2 puts the snare on 2, 3 and 4      | octave     |
| 5.3 | `two-bar-both`  | stretch | live   | a crash on bar 1, both answers in bar 2 | syncopated |

### Module: Four bars — a phrase you can hear the end of

| #   | slug             | tier    | status | pattern                                    | bass       |
| --- | ---------------- | ------- | ------ | ------------------------------------------ | ---------- |
| 5.4 | `four-bar-crash` | plain   | live   | one crash every four bars                  | quarter    |
| 5.5 | `four-bar-build` | core    | live   | quarters, 8ths, more kick, then the answer | riff       |
| 5.6 | `four-bar-drop`  | stretch | live   | bar 4 is its down-beat and nothing else    | syncopated |

### Module: The turnaround — the way back to bar one

| #   | slug                  | tier    | status | pattern                                 | bass       |
| --- | --------------------- | ------- | ------ | --------------------------------------- | ---------- |
| 5.7 | `turnaround-snare`    | plain   | live   | the last two beats given to the snare   | quarter    |
| 5.8 | `turnaround-open-hat` | core    | live   | crash at the top, open hat at the end   | riff       |
| 5.9 | `full-phrase`         | stretch | live   | all six pads across one four-bar phrase | syncopated |

**◆ Checkpoint 5** `checkpoint-5` — one four-bar phrase: the top, the answer,
the ride, the turnaround. This closes Foundations.

> These three stages were added after Stages 1 and 2 and before Vocabulary, so
> every stage number from Subdivision onwards moved up by three. Nothing a
> student owns moved: history and tempo ceilings are keyed by slug, and the
> displayed lesson number has always been rendered from position.

## Stage 6 · Subdivision & the grid

**Goal** — the 16th grid and the triplet grid, and a note placed anywhere on
either. Three pads throughout — kick, snare and closed hat, and no cymbals at all
after a whole stage of them — because everything hard here is meant to be
_where the notes are_.
No open hat, so the whole stage plays on a kit with no working hi-hat pedal.

### Module: Sixteenths — twice as fine

| #   | slug               | tier    | status | pattern                                          | bass       |
| --- | ------------------ | ------- | ------ | ------------------------------------------------ | ---------- |
| 6.1 | `hats-16ths-split` | plain   | live   | 16th hats shared between the hands, nothing else | quarter    |
| 6.2 | `rock-16th-hats`   | core    | live   | the same over kick 1 & 3, snare 2 & 4            | octave     |
| 6.3 | `kick-16th-grid`   | stretch | live   | 8th hats, kick on the "a" of 1 and the "e" of 3  | syncopated |

### Module: Triplets — three where there were two

| #   | slug              | tier    | status | pattern                                                          | bass       |
| --- | ----------------- | ------- | ------ | ---------------------------------------------------------------- | ---------- |
| 6.4 | `triplets-8th`    | plain   | live   | 8th-note triplets, hand to hand — the lead hand swaps every beat | shuffle    |
| 6.5 | `triplet-groove`  | core    | live   | triplet hats over the backbeat — the 12/8 feel                   | quarter    |
| 6.6 | `triplets-broken` | stretch | live   | the middle note dropped, and the sticking becomes doubles        | syncopated |

### Module: Feel — straight and swung

| #   | slug                | tier    | status | pattern                                                 | bass       |
| --- | ------------------- | ------- | ------ | ------------------------------------------------------- | ---------- |
| 6.7 | `shuffle-hats`      | plain   | live   | swung 8ths on the hat, one hand                         | shuffle    |
| 6.8 | `shuffle-groove`    | core    | live   | the full shuffle with kick and backbeat                 | shuffle    |
| 6.9 | `half-time-shuffle` | stretch | live   | the shuffle at half time (ghost notes wait for Stage 9) | syncopated |

**◆ Checkpoint 6** `checkpoint-6` — one bar each of 6.2 / 6.5 / 6.8 / 6.9:
16ths, triplets, shuffle, half-time shuffle, on the same three pads.

> **In triplet feel the bass ladder is re-derived, not reused.** Every line in
> `bass.py` except `shuffle` is written on the straight grid, so under triplets
> they stop sorting by support: `octave`, `answer` and `syncopated` all land on
> the "and", a slot a shuffle does not have. That leaves `quarter`, which marks
> the beat and says nothing about how it is divided, and `shuffle`, which plays
> the new grid alongside the student. Modules 2 and 3 therefore fade from
> `shuffle` to `quarter` to a straight line — the same fade, upside down. The
> checkpoint takes `quarter` because it is the only line that does not lie about
> one of the two grids it interleaves.

## Stage 7 · Sticking

**Goal** — rudiments, then rudiments inside a groove. _Which_ hand plays a note
starts to matter as much as when.

### Module: Strokes

| #   | slug            | tier    | status | pattern                     |
| --- | --------------- | ------- | ------ | --------------------------- |
| 7.1 | `singles-16ths` | plain   | todo   | single stroke roll in 16ths |
| 7.2 | `doubles-8ths`  | core    | todo   | R R L L in 8ths             |
| 7.3 | `doubles-16ths` | stretch | todo   | R R L L in 16ths            |

### Module: The paradiddle

| #   | slug                    | tier    | status | pattern                                              |
| --- | ----------------------- | ------- | ------ | ---------------------------------------------------- |
| 7.4 | `paradiddle-single`     | plain   | live   | R L R R / L R L L in 8ths                            |
| 7.5 | `paradiddle-groove`     | core    | live   | the paradiddle across hat and snare, kick underneath |
| 7.6 | `paradiddle-inversions` | stretch | todo   | the four inversions, one per bar                     |

### Module: Bigger diddles

| #   | slug                | tier    | status | pattern                   |
| --- | ------------------- | ------- | ------ | ------------------------- |
| 7.7 | `paradiddle-double` | plain   | todo   | R L R L R R / L R L R L L |
| 7.8 | `paradiddle-diddle` | core    | todo   | R L R R L L               |
| 7.9 | `six-stroke-roll`   | stretch | todo   | R L L R R L               |

**◆ Checkpoint 7** — singles / doubles / paradiddle / an inversion.

> `paradiddle-single` ships today as lesson 6.1, with nothing before it that
> ever alternates the hands. Stage 1's `alternating-8ths` and this stage's
> `singles` and `doubles` are its missing prerequisites.

## Stage 8 · Syncopation & displacement

**Goal** — playing against the grid without losing it.

### Module: Pushing

| #   | slug          | tier    | status | pattern                        |
| --- | ------------- | ------- | ------ | ------------------------------ |
| 8.1 | `upbeat-hats` | plain   | todo   | hats on the off-beats only     |
| 8.2 | `kick-pushed` | core    | todo   | kick on the "and" of 2 and 4   |
| 8.3 | `all-upbeats` | stretch | todo   | the whole groove on the "and"s |

### Module: Displacement

| #   | slug                   | tier    | status | pattern                              |
| --- | ---------------------- | ------- | ------ | ------------------------------------ |
| 8.4 | `snare-displaced-8th`  | plain   | todo   | backbeat moved to the "and"          |
| 8.5 | `snare-displaced-16th` | core    | todo   | backbeat on the "a" of 2             |
| 8.6 | `groove-displaced`     | stretch | todo   | the whole groove shifted a 16th late |

### Module: Feel shifts

| #   | slug          | tier    | status | pattern                                     |
| --- | ------------- | ------- | ------ | ------------------------------------------- |
| 8.7 | `half-time`   | plain   | todo   | one backbeat per bar                        |
| 8.8 | `double-time` | core    | todo   | the same groove at twice the density        |
| 8.9 | `feel-switch` | stretch | todo   | half and double time, alternating every bar |

**◆ Checkpoint 8** — pushed / displaced / half / double.

## Stage 9 · Dynamics · blocked

We receive note-on velocity and throw it away. Grading it unlocks this whole
stage — and with it the difference between a beginner's groove and a
musician's.

### Module: Accents

| #   | slug                   | tier    | status  | pattern                                |
| --- | ---------------------- | ------- | ------- | -------------------------------------- |
| 9.1 | `hat-accents-quarters` | plain   | blocked | accent the numbers, ghost the rest     |
| 9.2 | `hat-accents-8ths`     | core    | blocked | an accent pattern across 8th hats      |
| 9.3 | `hat-shaping`          | stretch | blocked | a hat line shaped across the whole bar |

### Module: Ghost notes

| #   | slug              | tier    | status  | pattern                                 |
| --- | ----------------- | ------- | ------- | --------------------------------------- |
| 9.4 | `ghost-single`    | plain   | blocked | one ghosted snare between the backbeats |
| 9.5 | `ghost-funk`      | core    | blocked | the ghost-note funk groove              |
| 9.6 | `ghost-16th-funk` | stretch | blocked | ghosts on the full 16th grid            |

### Module: Flams — also needs sub-grid scoring

| #   | slug          | tier    | status  | pattern                  |
| --- | ------------- | ------- | ------- | ------------------------ |
| 9.7 | `flam-snare`  | plain   | blocked | two hands a hair apart   |
| 9.8 | `flam-accent` | core    | blocked | the flam accent rudiment |
| 9.9 | `flam-groove` | stretch | blocked | flams on the backbeat    |

## Stage 10 · Form & Fills

**Goal** — a groove that says something: down-beats moved early, fills that
announce the change, and eight-bar pieces with a beginning, a middle and an
end. The first stage of Music, and the first with **eight-bar lessons** — the
chart and highway always drew whatever they were given, and eight bars is
where a verse and a chorus can both live.

### Module: The push — the down-beat, early

| #    | slug              | tier    | status | pattern                                            | bass       |
| ---- | ----------------- | ------- | ------ | -------------------------------------------------- | ---------- |
| 10.1 | `push-into-one`   | plain   | live   | every other bar's first kick arrives half early    | quarter    |
| 10.2 | `push-with-crash` | core    | live   | the crash lands with the push and rings through 1  | riff       |
| 10.3 | `pushed-stop`     | stretch | live   | push into an empty bar, return with a snare figure | syncopated |

### Module: Fills — two beats that announce the change

| #    | slug             | tier    | status | pattern                                          | bass       |
| ---- | ---------------- | ------- | ------ | ------------------------------------------------ | ---------- |
| 10.4 | `fill-two-beats` | plain   | live   | snare 16ths across beats 3–4, into a crash       | quarter    |
| 10.5 | `fill-with-kick` | core    | live   | R L R K, R L R K — the foot takes every fourth   | riff       |
| 10.6 | `fill-broken`    | stretch | live   | dotted spacing, then two 16ths slamming the door | syncopated |

### Module: Song form — eight bars with a shape

| #    | slug              | tier    | status | pattern                                            | bass       |
| ---- | ----------------- | ------- | ------ | -------------------------------------------------- | ---------- |
| 10.7 | `verse-chorus`    | plain   | live   | 8 bars: hat verse, open-hat hand-over, ride chorus | riff       |
| 10.8 | `eight-bar-build` | core    | live   | 8 bars adding a layer every two, spent on a fill   | pedal      |
| 10.9 | `the-arrangement` | stretch | live   | intro · verse · fill · chorus · push · ending      | syncopated |

**◆ Checkpoint 10** `checkpoint-10` — the pushed top, the empty-one landing,
the ride chorus, and the 16th fill, one bar each.

## Stage 11 · Styles: The Radio

**Goal** — rock, funk and hip-hop: one skeleton (snare on 2 and 4, hats in
8ths), three kick vocabularies, each at its genre's own tempo. The first
lessons whose manifest BPM is chosen by style rather than by the ladder — and
the first where the backing bass plays the genre with you (`pump` for rock,
the 16th `funk` interlock, the riff and the dark pedal for hip-hop).

### Module: Rock — the kick that drives

| #    | slug            | tier    | status | pattern                                           | bass |
| ---- | --------------- | ------- | ------ | ------------------------------------------------- | ---- |
| 11.1 | `rock-drive`    | plain   | live   | kick 1, 3 and the "and" of 3 · 92 BPM             | pump |
| 11.2 | `rock-anthem`   | core    | live   | ride 8ths, crash each 2 bars, kick pulls on 2-and | pump |
| 11.3 | `rock-sixteens` | stretch | live   | five kicks, two off the 8th grid ("a" of 1 and 4) | pump |

### Module: Funk — the one, and everything after it

| #    | slug             | tier    | status | pattern                                          | bass |
| ---- | ---------------- | ------- | ------ | ------------------------------------------------ | ---- |
| 11.4 | `funk-one`       | plain   | live   | kick 1, "a" of 1, "and" of 3 under straight hats | funk |
| 11.5 | `funk-open-hat`  | core    | live   | the hat barks open on the "and" of 2             | funk |
| 11.6 | `funk-displaced` | stretch | live   | a third snare on the "a" of 4 — the pickup       | funk |

### Module: Hip-hop — the lazy pocket

| #    | slug             | tier    | status | pattern                                          | bass  |
| ---- | ---------------- | ------- | ------ | ------------------------------------------------ | ----- |
| 11.7 | `boom-bap`       | plain   | live   | kick tucked on the "a" of 2 behind the snare     | riff  |
| 11.8 | `head-nod`       | core    | live   | kick doubled on 1-and, landing on the "e" of 3   | riff  |
| 11.9 | `trap-half-time` | stretch | live   | 16th hats, snare on 3 alone, kick 1 and "a" of 2 | pedal |

**◆ Checkpoint 11** `checkpoint-11` — driving rock, the funk one, boom bap and
half-time hats, one bar each, over the funk bass.

## Stage 12 · Styles: The Dancefloor

**Goal** — house, breaks and reggae: three skeletons, not one. The hat leaves
the beat, the snare leaves the backbeat, and beat 1 learns to be empty on
purpose. Reggae closes the curriculum's oldest thread — the one drop is a
groove _made of_ the silence Space taught, over a `dub` bass that skips the
down-beat too.

### Module: House — the pump

| #    | slug         | tier    | status | pattern                                            | bass   |
| ---- | ------------ | ------- | ------ | -------------------------------------------------- | ------ |
| 12.1 | `house-pump` | plain   | live   | four-floor kick, open hats off-beat only · 118 BPM | octave |
| 12.2 | `house-skip` | core    | live   | closed hats tucked on the "a" of 2 and 4           | octave |
| 12.3 | `house-drop` | stretch | live   | bar 4 loses the floor; a snare build snaps it back | octave |

### Module: Breaks — the snare starts moving

| #    | slug              | tier    | status | pattern                                                 | bass  |
| ---- | ----------------- | ------- | ------ | ------------------------------------------------------- | ----- |
| 12.4 | `the-breakbeat`   | plain   | live   | a two-bar break; bar 2 shifts the kick, adds pickup     | funk  |
| 12.5 | `break-displaced` | core    | live   | beat 4's snare moves to the "a" of 3                    | funk  |
| 12.6 | `two-step`        | stretch | live   | drum & bass's two-step at 160 — the tempo is the lesson | pedal |

### Module: Reggae — the empty one

| #    | slug       | tier    | status | pattern                                             | bass |
| ---- | ---------- | ------- | ------ | --------------------------------------------------- | ---- |
| 12.7 | `one-drop` | plain   | live   | kick + snare on 3, beat 1 empty every bar           | dub  |
| 12.8 | `skank`    | core    | live   | hats move off-beat: nothing lands on a number but 3 | dub  |
| 12.9 | `steppers` | stretch | live   | the kick returns to all four beats under the skank  | dub  |

**◆ Checkpoint 12** `checkpoint-12` — the pump, the break's answer bar, the
two-step and the one drop, one bar each at one uncomfortable tempo.

> Jazz, Latin and the ghost-note funk and brushes variants from the original
> styles sketch are not dropped — they wait on the same engine work Stage 9
> does (velocity scoring, and swung 16ths on the grid), and belong to a later
> styles stage once those land.

## Stage 13 · Independence & polyrhythm

### Module: Ostinato

| #    | slug               | tier    | status | pattern                               |
| ---- | ------------------ | ------- | ------ | ------------------------------------- |
| 13.1 | `ostinato-vary`    | plain   | todo   | one hand fixed, the other varies      |
| 13.2 | `ostinato-melodic` | core    | todo   | the free hand moves across pads       |
| 13.3 | `linear`           | stretch | todo   | linear drumming — nothing ever stacks |

### Module: Polyrhythm

| #    | slug              | tier    | status | pattern     |
| ---- | ----------------- | ------- | ------ | ----------- |
| 13.4 | `three-over-four` | plain   | todo   | 3 against 4 |
| 13.5 | `four-over-three` | core    | todo   | 4 against 3 |
| 13.6 | `five-over-four`  | stretch | todo   | 5 against 4 |

### Module: Odd meters — needs time-signature support

| #    | slug                | tier    | status  | pattern                 |
| ---- | ------------------- | ------- | ------- | ----------------------- |
| 13.7 | `odd-5-4`           | plain   | blocked | 5/4                     |
| 13.8 | `odd-7-8`           | core    | blocked | 7/8                     |
| 13.9 | `metric-modulation` | stretch | blocked | the pulse reinterpreted |

## Stage 14 · Performance

### Module: Speed

| #    | slug               | tier    | status | pattern                              |
| ---- | ------------------ | ------- | ------ | ------------------------------------ |
| 14.1 | `one-handed-16ths` | plain   | todo   | 16th hats on one hand under a groove |
| 14.2 | `finger-rolls`     | core    | todo   | rolls and buzzes                     |
| 14.3 | `belt-ladder`      | stretch | todo   | every earlier lesson taken to gold   |

### Module: Repertoire

| #    | slug            | tier    | status  | pattern                             |
| ---- | --------------- | ------- | ------- | ----------------------------------- |
| 14.4 | `transcribe`    | plain   | todo    | learn a groove by ear, then play it |
| 14.5 | `full-song`     | core    | blocked | a song top to bottom                |
| 14.6 | `trading-fours` | stretch | blocked | improvise the answering bar         |

### Module: Your own voice

| #    | slug              | tier    | status | pattern                         |
| ---- | ----------------- | ------- | ------ | ------------------------------- |
| 14.7 | `own-beat`        | plain   | todo   | build one groove of your own    |
| 14.8 | `own-fills`       | core    | todo   | a fill vocabulary that is yours |
| 14.9 | `improvise-a-set` | stretch | todo   | eight bars, no chart            |

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

Every lesson written so far is at 60, and the written BPM is the
lesson's floor rather than its ceiling — depth comes from the ladder, never
from piling on more notes. Sixteenths at 60 are already the fastest notes in
the curriculum (as fast as 8ths at 120), which is why the subdivision stage did
not need a faster tempo to be harder than the one before it. `stretch` lessons are hard by _pattern_; belts are hard by _tempo_. Keep
the two apart or neither means anything.

## Bass lines

The backing bass is the lesson's scaffold, and for a long time every line was
some arrangement of one root note hammered on the beat. Three separate things
were wrong, and they are independent.

**Placement.** A bass note struck at the same instant as a drum is not heard as
bass at all — same attack, and the kit wins. Every lesson puts drums on every
beat and most on every 8th, so a line on the beats is masked _by construction_.
This is what `quarter`, `octave` and `syncopated` all are.

**Motion.** A line that repeats one pitch is dull however it is placed.

**Dynamics.** Flat velocity is the loudest tell that a line came out of a text
editor. Velocity now survives the whole path — `parseMidi` keeps it on backing
notes and the sampler applies it as gain — so a ghost note is a ghost.

A corollary worth stating: **a walking bass is the wrong tool for this app.**
Walking means a note on every beat, and there is nowhere on the beat for it to
be heard. It was tried and replaced.

| line    | sits                                  | support | character                     |
| ------- | ------------------------------------- | ------- | ----------------------------- |
| `riff`  | anchor on 1, then off-beats and 16ths | highest | a hook you can play against   |
| `pedal` | one long root, then a scramble        | medium  | stillness against motion      |
| `dub`   | the down-beat left empty              | lowest  | attitude, resists the student |

**1 · Riff** — _implemented, live on 1.4._ Four bars over Am - F - C - G, and a
phrase rather than a bar played four times: the hook states itself in bar 1,
answers in bar 2, opens a hole in bar 3 where nothing plays across beat 3, and
drives home in bar 4 on a 16th-note turnaround. 19 of its 23 notes are the only
thing sounding at that moment; the other four are the roots anchoring beat 1
with the snare. The push before beat 2 is a ghost at velocity 55 against
accents at 100. Each bar ends a semitone from the next root, so the loop closes
rather than stops — G# pulls up to A and bar 4 runs straight back into bar 1.

**2 · Pedal & answer** — a long root under the first half of the bar, then a
burst of 16th-note melody in the second. The contrast does the work: two beats
of stillness make the answer an event. Best under the dense lessons, where a
16th answer is the only line that can find a gap at all.

**3 · Dub drop** — beat 1 is **empty**, and the line enters on the "and" of 1
or on beat 3, sparse and syncopated with long decays. Nothing marks the
down-beat, so the student has to be the one who knows where it is. The natural
end-of-stage line, replacing `syncopated`.

**4 · Shuffle** — _implemented, live across Stage 6._ The one line written on
the triplet grid: root on the beat, then a walking note two thirds of the way
across it, over Am - Am - Dm - E. It is not on the ladder above, because in
triplet feel that ladder does not sort — see the note under Stage 6. Masking is
not the objection it usually is here: the line is carrying a _rhythm_, and a
rhythm survives being blended into the kit in a way a melody does not. Bar 4
ends on a G#, a semitone under the tonic that follows the last drum hit.

`quarter`, `octave` and `syncopated` are still in use on every other lesson and
all three are masked by the drums above them. They should retire as the lines
above land.

> **Rule for a new line: write it against the lesson's drum pattern, not just
> against its position in the stage.** Under 8th-note drums the only free slots
> are 16ths. A line written without looking at what is on top of it will not be
> heard, however good it is.

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
- **A stage is one file.** Writing Stage 3 touches `stage03_space.py` and
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
