"""Stage 5 — Two Bars.

Everything the student has played so far is one bar, repeated. This stage is
where a groove stops looping and starts having a beginning and an end: bar 2
answers bar 1, a crash says where the phrase starts, and the last two beats hand
the whole thing back to the top.

The rhythms are deliberately old. Nothing here is finer than an 8th note and
nothing lands off the beat except the hats, which have been on the 8ths since
Stage 2 — because the new axis is **form**, and a stage that moved form and
subdivision at once could not tell the student which one they failed. What is
new is that four bars are no longer four attempts at the same bar; they are one
thing, four bars long, and it is possible to play every note correctly and still
play it wrongly by losing your place inside it.

This closes Foundations. The tier asked "can you keep time and stack two hands?"
— by the end of this stage the answer has to include *for four bars at a time*.
"""

from .bass import OCTAVE, QUARTER, RIFF, SYNCOPATED
from .grids import (
    BACKBEAT,
    BEATS,
    DOWNBEATS,
    EIGHTHS,
    cycle_bars,
    per_bar,
)
from .midi import CLOSED_HH, CRASH, KICK, OPEN_HH, RIDE, SNARE
from .schema import checkpoint, lesson, module, stage

LAST_EIGHTH = 3.5  # the "and" of 4 — where a bar hands over to the next one

# The groove underneath the whole stage: the Stage 2 rock beat. Every lesson
# here varies what happens *around* it rather than what it is.
CORE = [(KICK, DOWNBEATS), (SNARE, BACKBEAT)]
ROCK = [(CLOSED_HH, EIGHTHS)] + CORE

# The last two beats of a bar given over to the snare, in 8ths. The simplest
# turnaround there is, and every note of it sits on a grid the student has
# played since Stage 1.
TURNAROUND_HALF = [2, 2.5, 3, 3.5]


# --- Module 1: question and answer --------------------------------------------


def two_bar_kick(bars=4):
    """Bar 2 adds one kick, on beat 4 — the smallest possible answer.

    The extra kick lands with the snare that was already there, so bar 2 is bar
    1 with one thing thicker and nothing moved. That is the whole idea of a
    two-bar phrase reduced to a single note.
    """
    answer = [(CLOSED_HH, EIGHTHS), (KICK, [0, 2, 3]), (SNARE, BACKBEAT)]
    return per_bar(bars, lambda bar: ROCK if bar % 2 == 0 else answer)


def two_bar_snare(bars=4):
    """Bar 2 answers with the snare on 2, 3 and 4 instead of 2 and 4."""
    answer = [(CLOSED_HH, EIGHTHS), (KICK, DOWNBEATS), (SNARE, [1, 2, 3])]
    return per_bar(bars, lambda bar: ROCK if bar % 2 == 0 else answer)


def two_bar_both(bars=4):
    """A crash opens bar 1; bar 2 answers with both the extra kick and the snares.

    The two halves of the phrase are now unmistakably different: one is marked
    at the front by a cymbal, the other is thicker all the way through its
    second half. Everything is still on the beat.
    """
    call = [(CRASH, [0])] + ROCK
    answer = [(CLOSED_HH, EIGHTHS), (KICK, [0, 2, 3]), (SNARE, [1, 2, 3])]
    return per_bar(bars, lambda bar: call if bar % 2 == 0 else answer)


# --- Module 2: four bars ------------------------------------------------------


def four_bar_crash(bars=4):
    """One crash, on the down-beat of bar 1, and four identical bars under it.

    The groove says nothing about where the phrase begins; the cymbal says all
    of it, once every four bars. Losing count costs nothing audible until the
    crash lands in the wrong place — which is exactly why it is worth drilling.
    """
    return per_bar(bars, lambda bar: ([(CRASH, [0])] + ROCK) if bar % 4 == 0 else ROCK)


def four_bar_build(bars=4):
    """Four bars that get busier: quarters, 8ths, more kick, then the answer.

    A phrase with a shape. The hat opens on quarter notes and doubles in bar 2,
    the kick fills in every beat in bar 3, and bar 4 answers with the snare
    before handing back to the top. Four different bars, no new rhythm in any
    of them.
    """
    shapes = [
        [(CLOSED_HH, BEATS)] + CORE,
        ROCK,
        [(CLOSED_HH, EIGHTHS), (KICK, BEATS), (SNARE, BACKBEAT)],
        [(CLOSED_HH, EIGHTHS), (KICK, DOWNBEATS), (SNARE, [1, 2, 3])],
    ]
    return per_bar(bars, lambda bar: shapes[bar % len(shapes)])


def four_bar_drop(bars=4):
    """Three bars of groove, then a bar with only its down-beat in it.

    The drop: everything stops after beat 1 of bar 4 and the phrase is carried
    by nothing but the count until the loop turns over. Stage 3 taught holding
    an empty bar; this is the same skill with three bars of momentum behind it,
    which makes it considerably harder to resist filling.
    """
    drop = [(CRASH, [0]), (CLOSED_HH, [0]), (KICK, [0])]
    return per_bar(bars, lambda bar: drop if bar % 4 == 3 else ROCK)


# --- Module 3: the turnaround -------------------------------------------------


def turnaround_snare(bars=4):
    """Bars 1-3 groove; bar 4 gives its last two beats to the snare in 8ths.

    Four snare notes where the groove was, on beats 3 and 4 of the fourth bar.
    Nothing off the grid, nothing fast — the difficulty is that the hands swap
    jobs for half a bar and have to be back for the down-beat.
    """
    turn = [
        (CLOSED_HH, [p for p in EIGHTHS if p < 2]),
        (KICK, [0]),
        (SNARE, [1] + TURNAROUND_HALF),
    ]
    return per_bar(bars, lambda bar: turn if bar % 4 == 3 else ROCK)


def turnaround_open_hat(bars=4):
    """The same turnaround, opened by a crash and closed by an open hat.

    The phrase now has both ends marked: a crash on the down-beat of bar 1 says
    where it starts, and an open hat on the very last eighth says it is about to
    start again. Between them the snare turnaround is unchanged.
    """
    turn = [
        (CLOSED_HH, [p for p in EIGHTHS if p < 2]),
        (KICK, [0]),
        (SNARE, [1] + TURNAROUND_HALF[:-1]),
        (OPEN_HH, [LAST_EIGHTH]),
    ]
    return per_bar(
        bars,
        lambda bar: turn
        if bar % 4 == 3
        else (([(CRASH, [0])] + ROCK) if bar % 4 == 0 else ROCK),
    )


def full_phrase(bars=4):
    """Everything the tier has: crash, hats, ride, a turnaround and an open hat.

    Bar 1 opens on a crash, bars 1 and 2 sit on the closed hat, bars 3 and 4
    move to the ride, and bar 4 hands the phrase back with the snare turnaround
    and an open hat on the last eighth. Six pads, four bars, one shape — and
    still not a single note off the beat that was not there in Stage 2.
    """

    def for_bar(bar):
        pos = bar % 4
        if pos == 0:
            return [(CRASH, [0]), (CLOSED_HH, [p for p in EIGHTHS if p != 0])] + CORE
        if pos == 1:
            return ROCK
        if pos == 2:
            return [(RIDE, EIGHTHS)] + CORE
        return [
            (RIDE, [p for p in EIGHTHS if p < 2]),
            (KICK, [0]),
            (SNARE, [1] + TURNAROUND_HALF[:-1]),
            (OPEN_HH, [LAST_EIGHTH]),
        ]

    return per_bar(bars, for_bar)


# --- Checkpoint ---------------------------------------------------------------


def checkpoint_5(bars=4):
    """The stage as one four-bar phrase: top, answer, ride, turnaround."""
    return cycle_bars(
        bars,
        [
            [(CRASH, [0])] + ROCK,
            [(CLOSED_HH, EIGHTHS), (KICK, [0, 2, 3]), (SNARE, [1, 2, 3])],
            [(RIDE, EIGHTHS)] + CORE,
            [
                (RIDE, [p for p in EIGHTHS if p < 2]),
                (KICK, [0]),
                (SNARE, [1] + TURNAROUND_HALF[:-1]),
                (OPEN_HH, [LAST_EIGHTH]),
            ],
        ],
    )


STAGE = stage(
    number=5,
    slug="two-bars",
    title="Two Bars",
    goal="A groove with a beginning and an end. Bar 2 answers bar 1, a cymbal "
    "marks the top of the phrase, and the last two beats hand it back — all "
    "of it on the same grid Stage 2 finished on.",
    modules=[
        module(
            "question-and-answer",
            "Question and answer",
            "bar two replies",
            [
                lesson(
                    slug="two-bar-kick",
                    name="The Second Bar Answers",
                    tier="plain",
                    drums=two_bar_kick,
                    bass=QUARTER,
                    prereq=["rock-beat-8th-hats"],
                    summary="Two bars of rock beat, and the second one adds a "
                    "single kick on beat 4.",
                    description=(
                        "The smallest two-bar phrase there is. Bar 1 is the groove "
                        "you know; bar 2 is the same groove with one extra kick, on "
                        "beat 4, landing with the snare that was already there. "
                        "Nothing moves and nothing is taken away — but the loop is "
                        "now two bars long rather than one, and playing it as one "
                        "bar twice is the mistake this lesson exists to catch."
                    ),
                    hints=[
                        "Count bars out loud as well as beats: "
                        '"one-two-three-four, two-two-three-four."',
                        "The extra kick is on beat 4 of the even bars only, "
                        "stacked with the snare. One movement, two pads.",
                        "Adding it to every bar is the usual fault, and it sounds "
                        "fine — which is why you have to count rather than listen.",
                        "Play four bars of the plain groove first, then put the "
                        "extra kick in on bars 2 and 4 without changing anything "
                        "else.",
                    ],
                ),
                lesson(
                    slug="two-bar-snare",
                    name="The Snare Answers",
                    tier="core",
                    drums=two_bar_snare,
                    bass=OCTAVE,
                    prereq=["two-bar-kick"],
                    summary="Bar 2 puts the snare on 2, 3 and 4 instead of 2 and 4.",
                    description=(
                        "A bigger answer, and one you can hear from across the "
                        "room: the second half of bar 2 fills in with the snare, so "
                        "the phrase leans forward into the bar that follows. The "
                        "kick and the hat are untouched, which means the strong "
                        "hand is doing something different in alternate bars while "
                        "the weak hand does exactly the same thing throughout."
                    ),
                    hints=[
                        "Bar 2's snare is on 2, 3 and 4 — three beats in a row. Bar "
                        "1's is on 2 and 4 as usual.",
                        "The hat does not change at all. If it stumbles in bar 2, "
                        "the weak hand is watching the strong one.",
                        "Beat 3 of bar 2 is the new note: it lands where the kick "
                        "is, so it is a stack rather than an extra beat.",
                        "Say the answer out loud before playing it: "
                        '"bap — bap bap bap."',
                    ],
                ),
                lesson(
                    slug="two-bar-both",
                    name="Call and Answer",
                    tier="stretch",
                    drums=two_bar_both,
                    bass=SYNCOPATED,
                    prereq=["two-bar-snare", "crash-on-one"],
                    summary="A crash opens bar 1; bar 2 answers with the extra kick "
                    "and the extra snares together.",
                    description=(
                        "Both halves of the phrase are now marked. Bar 1 is topped "
                        "by a cymbal, bar 2 thickens through its second half with "
                        "the kick on 4 and the snare on 2, 3 and 4. Two bars that "
                        "sound nothing like each other, built entirely from notes "
                        "that are on the beat, and the bass has stopped marking "
                        "those beats for you."
                    ),
                    hints=[
                        "Bar 1 starts with a three-pad stack: crash, hat and kick. "
                        "Bar 2 has no crash at all.",
                        "The answer is four notes thicker than the call. Do not let "
                        "it get faster as well as busier.",
                        "The bass pushes off the beat now. Every note you play is "
                        "on one — hold that difference.",
                        "If the two bars start sounding the same, drop the crash "
                        "for a run and put it back once bar 2 is reliably different.",
                    ],
                ),
            ],
        ),
        module(
            "four-bars",
            "Four bars",
            "a phrase you can hear the end of",
            [
                lesson(
                    slug="four-bar-crash",
                    name="One Crash in Four Bars",
                    tier="plain",
                    drums=four_bar_crash,
                    bass=QUARTER,
                    prereq=["crash-every-two"],
                    summary="Four identical bars of groove with a single crash on "
                    "the down-beat of the first.",
                    description=(
                        "Nothing in the groove tells you where the phrase begins. "
                        "One cymbal does, once every four bars, and between them "
                        "you have to hold your place with nothing but counting. "
                        "This is the four-bar unit that almost all popular music is "
                        "built from, and the only way to fail it is to lose track "
                        "of which bar you are in."
                    ),
                    hints=[
                        "Count bars, not beats: one, two, three, four — crash on "
                        "the next one.",
                        "Three bars of identical groove between crashes is a long "
                        "time to keep counting. That is the exercise.",
                        "Crashing early is far more common than crashing late. If "
                        "in doubt you are probably a bar ahead.",
                        "The groove itself is Stage 2 and should be automatic. If "
                        "it is taking attention, go back to it before counting bars "
                        "on top.",
                    ],
                ),
                lesson(
                    slug="four-bar-build",
                    name="The Build",
                    tier="core",
                    drums=four_bar_build,
                    bass=RIFF,
                    prereq=["four-bar-crash", "rock-beat-quarter-hats"],
                    summary="Four bars that get busier: quarter hats, 8th hats, "
                    "kick on every beat, then the snare answer.",
                    description=(
                        "A phrase with a shape rather than a marker. The hat starts "
                        "on quarter notes and doubles in bar 2, the kick fills in "
                        "every beat in bar 3, and bar 4 answers with the snare "
                        "before the loop turns over. Every one of those bars is a "
                        "lesson you have already played — the new thing is that "
                        "they are four parts of one sentence."
                    ),
                    hints=[
                        "Four different bars in a row. Name them before you play: "
                        "quarters, eighths, four-on-the-floor, answer.",
                        "The tempo must not build with the density. The kick on "
                        "beat 1 should be exactly as far apart in bar 4 as in bar 1.",
                        "Bar 1 sounds empty after bar 4. Resist filling it — that "
                        "contrast is what makes the build work.",
                        "The bass is a four-bar riff with a hole in bar 3. Let its "
                        "shape and yours line up rather than fighting.",
                    ],
                ),
                lesson(
                    slug="four-bar-drop",
                    name="The Drop",
                    tier="stretch",
                    drums=four_bar_drop,
                    bass=SYNCOPATED,
                    prereq=["four-bar-build", "stop-every-other-bar"],
                    summary="Three bars of groove, then a bar with nothing in it "
                    "but its down-beat.",
                    description=(
                        "Everything stops after beat 1 of bar 4 — one crash, one "
                        "kick, one hat, and then three beats of nothing before the "
                        "loop starts again. You held an empty bar back in Space, "
                        "but not with three bars of momentum pushing you into it, "
                        "and momentum is exactly what makes a drop hard to leave "
                        "empty."
                    ),
                    hints=[
                        "Beats 2, 3 and 4 of bar 4 are silent. Count them out loud "
                        "— they are the lesson.",
                        "The hands want to keep going. Lift them off the pads for "
                        "the drop rather than hovering over them.",
                        "The down-beat that follows is the one to land. It is the "
                        "return, and everything before it was setting it up.",
                        "The bass keeps pushing through the empty bar and does not "
                        "mark the beat. That is not help, it is company.",
                    ],
                ),
            ],
        ),
        module(
            "the-turnaround",
            "The turnaround",
            "the way back to bar one",
            [
                lesson(
                    slug="turnaround-snare",
                    name="The Turnaround",
                    tier="plain",
                    drums=turnaround_snare,
                    bass=QUARTER,
                    prereq=["two-bar-snare", "eighths-strong-hand"],
                    summary="Three bars of groove, then the last two beats of bar 4 "
                    "given to the snare in 8ths.",
                    description=(
                        "The simplest way to end a phrase: hand the last half bar "
                        "to the snare. Four 8th notes on beats 3 and 4 of bar 4, "
                        "with the hat standing down for those two beats — so the "
                        "hands swap jobs briefly and have to be back in place for "
                        "the down-beat. Nothing here is faster than the 8ths you "
                        "played in Stage 1."
                    ),
                    hints=[
                        "The turnaround is four snare 8ths on beats 3 and 4 of the "
                        "last bar. Count them as \"3 and 4 and\".",
                        "The hat stops for those two beats. Do not try to keep it "
                        "going underneath — the hand is needed elsewhere.",
                        "Come back to the groove cleanly on the next down-beat. A "
                        "turnaround that overruns by a note is worse than none.",
                        "Four 8ths on one pad is Stage 1's density. If it feels "
                        "fast, it is the switch that is costing you, not the notes.",
                    ],
                ),
                lesson(
                    slug="turnaround-open-hat",
                    name="Turnaround with an Open Hat",
                    tier="core",
                    drums=turnaround_open_hat,
                    bass=RIFF,
                    prereq=["turnaround-snare", "open-hat-lead-in"],
                    summary="Both ends marked: a crash opens the phrase and an open "
                    "hat on the last 8th hands it back.",
                    description=(
                        "The phrase gets punctuation at both ends. A crash on the "
                        "down-beat of bar 1 says where it starts; the snare "
                        "turnaround runs through beats 3 and 4 of bar 4 and gives "
                        "its very last eighth to the open hat, which rings across "
                        "the bar line into the crash. Between those two moments the "
                        "groove has not changed at all."
                    ),
                    hints=[
                        "The last note of the loop is an open hat, not a snare. It "
                        "replaces the fourth snare of the turnaround.",
                        "Let the open hat ring into the crash rather than stopping "
                        "it. The two are one gesture across the bar line.",
                        "That means the weak hand comes back from resting to play "
                        "the very last eighth. Have it over the pad by beat 4.",
                        "Play bars 3 and 4 alone until the hand-off is reliable, "
                        "then run the whole phrase.",
                    ],
                ),
                lesson(
                    slug="full-phrase",
                    name="The Whole Phrase",
                    tier="stretch",
                    drums=full_phrase,
                    bass=SYNCOPATED,
                    prereq=["turnaround-open-hat", "every-pad"],
                    summary="Four bars with everything Foundations has: crash, "
                    "hats, ride, a turnaround and an open hat.",
                    description=(
                        "The tier in one loop. A crash opens bar 1, the closed hat "
                        "carries bars 1 and 2, the ride takes over for bars 3 and "
                        "4, and bar 4 hands the phrase back with the snare "
                        "turnaround and an open hat on the last eighth. Six pads "
                        "and four different bars — and still not one note that is "
                        "off the beat or finer than an eighth. Everything hard "
                        "about it is knowing where you are."
                    ),
                    hints=[
                        "Learn the map first: crash and hat, hat, ride, ride into "
                        "the turnaround. The rhythm is Stage 2 throughout.",
                        "Two hand moves a loop: hat to ride between bars 2 and 3, "
                        "ride back to the open hat at the very end.",
                        "The ride stands down for beats 3 and 4 of bar 4 while the "
                        "snare turns the phrase around. Only the last eighth is a "
                        "cymbal again.",
                        "Play it as two halves — bars 1 to 2, then bars 3 to 4 — "
                        "before joining them. Each half is a lesson you have "
                        "already passed.",
                    ],
                ),
            ],
        ),
    ],
    closing=checkpoint(
        slug="checkpoint-5",
        name="Checkpoint — Two Bars",
        drums=checkpoint_5,
        bass=RIFF,
        summary="The stage as one four-bar phrase: the crash on top, the answer, "
        "the ride, and the turnaround back to the start.",
        description=(
            "Four bars, four jobs. Bar 1 is the top of the phrase, bar 2 answers "
            "it, bar 3 moves to the ride, and bar 4 turns the whole thing around "
            "and hands it back. This is not four grooves interleaved — it is one "
            "phrase, which is exactly what the stage was for, and it closes "
            "Foundations. Play it clean and you can keep time, stack your hands, "
            "and hold your place in a piece of music."
        ),
        hints=[
            "One phrase, not four bars. If you can hear it as a sentence you will "
            "not lose your place in it.",
            "The pad under the timekeeping hand changes at bar 3 and again at the "
            "very last eighth.",
            "Bar 2 is the only bar with the thick answer — kick on 4, snare on 2, "
            "3 and 4.",
            "The last eighth is an open hat that rings into the closing crash. "
            "That closing hit is scored.",
        ],
    ),
)
