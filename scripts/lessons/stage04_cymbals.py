"""Stage 4 — The Cymbals.

Three pads the student owns but has never been asked for: the ride, the crash
and — properly this time — the open hat. Same grid, same tempo, same kick and
snare; what changes is which pad the timekeeping hand is on and when it moves.

The pad set is not arbitrary. Kick, snare, closed hat, open hat, ride and crash
are exactly the six the on-screen controller ships with (`DEFAULT_PADS` in
`$lib/virtual-input.ts`), so every lesson in this stage is playable by someone
who has no hardware at all. Toms are not in that set and so are not here.

Musically this is the stage where a groove stops being a loop and starts having
a shape: a crash says *this is the top of the phrase*, and a move from hat to
ride says *this is the chorus*. Neither is a rhythm — both are decisions, and
they are the first ones the curriculum asks the student to make with a hand.
"""

from .bass import OCTAVE, QUARTER, SYNCOPATED
from .grids import (
    BACKBEAT,
    BEATS,
    DOWNBEATS,
    EIGHTHS,
    cycle_bars,
    per_bar,
    voices,
)
from .midi import CLOSED_HH, CRASH, KICK, OPEN_HH, RIDE, SNARE
from .schema import checkpoint, lesson, module, stage

# The last 8th of the bar — where an open hat goes, and the only note in a rock
# beat that habitually gets a different pad.
LAST_EIGHTH = 3.5

# --- Module 1: the ride -------------------------------------------------------


def ride_quarters(bars=4):
    """Ride on all four beats, kick on 1 and 3 — the hat lesson on a new pad."""
    return voices(bars, (RIDE, BEATS), (KICK, DOWNBEATS))


def rock_beat_ride(bars=4):
    """The rock beat with the ride keeping the 8ths instead of the hat."""
    return voices(bars, (RIDE, EIGHTHS), (KICK, DOWNBEATS), (SNARE, BACKBEAT))


def hat_to_ride(bars=4):
    """Two bars on the closed hat, two on the ride — the hand moves on a bar line.

    The kick and snare do not change across the move, which is the point: the
    groove is identical and only its colour is different. Travelling on a bar
    line rather than mid-bar is what makes this the module's stretch rather than
    something harder — there is a whole beat of warning, and it still goes wrong
    the first few times.
    """
    return per_bar(
        bars,
        lambda bar: [
            (RIDE if bar % 4 >= 2 else CLOSED_HH, EIGHTHS),
            (KICK, DOWNBEATS),
            (SNARE, BACKBEAT),
        ],
    )


# --- Module 2: the crash ------------------------------------------------------


def crash_on_one(bars=4):
    """The rock beat with a crash on every down-beat.

    Three pads at once on beat 1 — crash, hat and kick — which is a stack the
    student has done since Stage 2, on pads that are further apart than any
    stack so far.
    """
    return voices(
        bars,
        (CRASH, [0]),
        (CLOSED_HH, EIGHTHS),
        (KICK, DOWNBEATS),
        (SNARE, BACKBEAT),
    )


def crash_every_two(bars=4):
    """A crash on the down-beat of every *other* bar — the two-bar phrase, audible.

    Same groove throughout; the only thing that says where the phrase starts is
    the cymbal. Two bars is the unit almost all popular music is built from, and
    this is the first lesson where the student has to feel it rather than be
    told it.
    """

    def for_bar(bar):
        line = [(CLOSED_HH, EIGHTHS), (KICK, DOWNBEATS), (SNARE, BACKBEAT)]
        return [(CRASH, [0])] + line if bar % 2 == 0 else line

    return per_bar(bars, for_bar)


def crash_into_ride(bars=4):
    """Crash on 1, then the ride carries the bar — the chorus entrance.

    The crash takes the down-beat and the ride picks up from the "and", so the
    hand travels *within* one beat instead of across a bar line. That is the
    real move, and it is why this is the stretch: everything before it gave the
    hand a whole beat of notice.
    """

    def for_bar(bar):
        crashing = bar % 2 == 0
        return [
            (CRASH, [0] if crashing else []),
            # The ride yields the down-beat to the crash, then runs the bar out.
            (RIDE, [p for p in EIGHTHS if not (crashing and p == 0)]),
            (KICK, DOWNBEATS),
            (SNARE, BACKBEAT),
        ]

    return per_bar(bars, for_bar)


# --- Module 3: open and closed ------------------------------------------------


def open_hat_lead_in(bars=4):
    """Closed hats through the bar, open on the last 8th — the lead-in.

    One note of the hat line moves to the other pad, and it is the note that
    hands the bar over to the next one. The most-played hi-hat move in popular
    music, and the whole difficulty is that it happens once a bar, at the point
    where the hand is least ready for it.
    """
    return voices(
        bars,
        (CLOSED_HH, [p for p in EIGHTHS if p != LAST_EIGHTH]),
        (OPEN_HH, [LAST_EIGHTH]),
        (KICK, DOWNBEATS),
        (SNARE, BACKBEAT),
    )


def crash_after_open(bars=4):
    """The open hat lead-in landing on a crash — the two halves of one gesture."""
    return voices(
        bars,
        (CRASH, [0]),
        (CLOSED_HH, [p for p in EIGHTHS if p != LAST_EIGHTH]),
        (OPEN_HH, [LAST_EIGHTH]),
        (KICK, DOWNBEATS),
        (SNARE, BACKBEAT),
    )


def every_pad(bars=4):
    """All six pads in four bars: hat and open hat, then ride and crash.

    Bars 1 and 2 are the lead-in groove, bars 3 and 4 are the ride groove with
    a crash opening bar 3 — a verse and a chorus, joined by an open hat on the
    last 8th of bar 2 that pushes straight into the cymbal. Every pad the app
    guarantees, in one loop, and no new rhythm anywhere in it.
    """

    def for_bar(bar):
        core = [(KICK, DOWNBEATS), (SNARE, BACKBEAT)]
        if bar % 4 < 2:  # verse: closed hats with the open lead-in
            return [
                (CLOSED_HH, [p for p in EIGHTHS if p != LAST_EIGHTH]),
                (OPEN_HH, [LAST_EIGHTH]),
            ] + core
        crashing = bar % 4 == 2  # chorus: crash opens it, ride carries it
        return [
            (CRASH, [0] if crashing else []),
            (RIDE, [p for p in EIGHTHS if not (crashing and p == 0)]),
        ] + core

    return per_bar(bars, for_bar)


# --- Checkpoint ---------------------------------------------------------------


def checkpoint_4(bars=4):
    """One bar each: the ride groove, a crash on 1, the open-hat lead-in, both."""
    core = [(KICK, DOWNBEATS), (SNARE, BACKBEAT)]
    closed_but_last = [p for p in EIGHTHS if p != LAST_EIGHTH]
    return cycle_bars(
        bars,
        [
            [(RIDE, EIGHTHS)] + core,
            [(CRASH, [0]), (CLOSED_HH, EIGHTHS)] + core,
            [(CLOSED_HH, closed_but_last), (OPEN_HH, [LAST_EIGHTH])] + core,
            [(CRASH, [0]), (RIDE, [p for p in EIGHTHS if p != 0])] + core,
        ],
    )


STAGE = stage(
    number=4,
    slug="cymbals",
    title="The Cymbals",
    goal="The three pads beyond the core three: ride, crash and open hat. The "
    "same time on a different cymbal, and the first hand travel that has a "
    "musical reason rather than a rhythmic one.",
    modules=[
        module(
            "the-ride",
            "The ride",
            "a second timekeeper",
            [
                lesson(
                    slug="ride-quarters",
                    name="Ride on Every Beat",
                    tier="plain",
                    drums=ride_quarters,
                    bass=QUARTER,
                    prereq=["kick-hats-unison"],
                    summary="Ride on all four beats with a kick on 1 and 3 — the "
                    "hat lesson, moved to a new pad.",
                    description=(
                        "Note for note this is Kick & Hi-Hat from Stage 2 with the "
                        "hat swapped for the ride, so nothing about the rhythm is "
                        "new and everything about the geography is. The ride is "
                        "the other pad a drummer keeps time on, and it is usually "
                        "the furthest one from where your hand rests. Getting there "
                        "without looking is the lesson."
                    ),
                    hints=[
                        "Ride on your weak hand, kick on your strong one, exactly "
                        "as the hat and kick were.",
                        "Find the ride pad before you press Play and leave the "
                        "finger on it. This lesson never asks the hand to move.",
                        "Beats 1 and 3 are two pads dropping together. Drill that "
                        "pair before running the loop.",
                        "A ride is a long sound where a closed hat is a short one. "
                        "Let it ring rather than damping it with the finger.",
                    ],
                ),
                lesson(
                    slug="rock-beat-ride",
                    name="Rock Beat on the Ride",
                    tier="core",
                    drums=rock_beat_ride,
                    bass=OCTAVE,
                    prereq=["ride-quarters", "rock-beat-8th-hats"],
                    summary="The rock beat with the ride keeping the 8ths instead "
                    "of the hi-hat.",
                    description=(
                        "The groove that ends Stage 2, played on the ride. This is "
                        "what almost every rock band does at the chorus and what "
                        "almost every jazz group does all night: the same time, "
                        "opened up. Kick and snare have not moved, so anything that "
                        "falls apart here is the new pad and nothing else."
                    ),
                    hints=[
                        "Play Rock Beat, 8th Hats first, then this. The only "
                        "difference is which pad the weak hand is on.",
                        "The ride rings into the next note. That is correct — do "
                        "not shorten the strokes to make it sound like a hat.",
                        "Rides tend to get louder than hats because the pad is "
                        "further away and the hand travels further. Keep the "
                        "backbeat above it.",
                        "If the 8ths get uneven, the arm is doing the work. Let the "
                        "finger bounce from a fixed position.",
                    ],
                ),
                lesson(
                    slug="hat-to-ride",
                    name="Hat to Ride",
                    tier="stretch",
                    drums=hat_to_ride,
                    bass=OCTAVE,
                    prereq=["rock-beat-ride"],
                    summary="Two bars on the closed hat, two on the ride — the "
                    "hand moves on the bar line.",
                    description=(
                        "The verse and the chorus in one loop. The groove is "
                        "identical for all four bars; only the pad under the "
                        "timekeeping hand changes, and it changes on the bar line "
                        "where there is a whole beat of warning. That warning is "
                        "why this is the stretch of an easy module rather than a "
                        "hard lesson — and it still takes a few runs before the "
                        "move stops costing a note."
                    ),
                    hints=[
                        "The move happens between bar 2 and bar 3, and again as the "
                        "loop wraps back round to bar 1. Two moves, not one.",
                        'The last 8th before the move — the "and" of 4 — is the '
                        "note people drop. Play it on the pad you are leaving, then "
                        "travel.",
                        "Kick and snare carry straight through the move. If they "
                        "hesitate, the hands are talking to each other when they "
                        "should not be.",
                        "Practise the move alone: two bars of hat, two of ride, no "
                        "kick and no snare, until the hand knows the distance.",
                    ],
                ),
            ],
        ),
        module(
            "the-crash",
            "The crash",
            "the note that opens a phrase",
            [
                lesson(
                    slug="crash-on-one",
                    name="Crash on 1",
                    tier="plain",
                    drums=crash_on_one,
                    bass=QUARTER,
                    prereq=["rock-beat-8th-hats", "stack-every-beat"],
                    summary="The rock beat with a crash on every down-beat — three "
                    "pads at once, further apart than ever.",
                    description=(
                        "A crash is not timekeeping; it is punctuation, and it "
                        "lands on the beat everything else already lands on. That "
                        "makes beat 1 a three-pad stack of crash, hat and kick — a "
                        "shape you have played since Stage 2, but never with the "
                        "pads this far apart. The rest of the bar is unchanged."
                    ),
                    hints=[
                        "Crash on the weak hand alongside the hat, kick and snare "
                        "on the strong one. The weak hand covers two pads and moves "
                        "only on beat 1.",
                        "All three notes on beat 1 are one movement. If it lands as "
                        "a roll, the crash is arriving after the hat.",
                        "Get back to the hat for the \"and\" of 1. That eighth is "
                        "the one that disappears while the hand is still out at the "
                        "crash.",
                        "A crash is loud by nature — do not add to it. Everything "
                        "else in the bar should stay where it was.",
                    ],
                ),
                lesson(
                    slug="crash-every-two",
                    name="Crash Every Two Bars",
                    tier="core",
                    drums=crash_every_two,
                    bass=OCTAVE,
                    prereq=["crash-on-one"],
                    summary="The same groove with a crash only on bars 1 and 3 — "
                    "the two-bar phrase, made audible.",
                    description=(
                        "Popular music is built in twos and fours, and this is the "
                        "first lesson where you have to feel that rather than be "
                        "told it. Nothing in the groove marks the phrase; the "
                        "cymbal does, on the down-beat of every other bar. Miss one "
                        "and the loop is still perfectly playable, which is exactly "
                        "why it is easy to lose."
                    ),
                    hints=[
                        "Count bars as well as beats: one-two-three-four, "
                        "two-two-three-four, and crash on every odd bar's 1.",
                        "The crash bars and the plain bars are otherwise identical. "
                        "Nothing else should change when it lands.",
                        "If you find yourself crashing every bar, you are playing "
                        "the pad rather than the phrase. Drop to two bars of "
                        "counting with no crash at all, then put it back.",
                        "The lesson ends on a crash — the closing hit repeats "
                        "whatever beat 1 had, and beat 1 had all three pads.",
                    ],
                ),
                lesson(
                    slug="crash-into-ride",
                    name="Crash, then Ride",
                    tier="stretch",
                    drums=crash_into_ride,
                    bass=SYNCOPATED,
                    prereq=["crash-every-two", "rock-beat-ride"],
                    summary="Crash on the down-beat, ride from the \"and\" — the "
                    "hand travels inside a single beat.",
                    description=(
                        "The chorus entrance as it is actually played: the crash "
                        "takes beat 1 and the ride picks the bar up half a beat "
                        "later. Every move before this one had a bar line to happen "
                        "on; this one has an eighth note. The kick and snare are "
                        "the same rock beat they have been all stage, so the travel "
                        "is the only new thing — and it is plenty."
                    ),
                    hints=[
                        'Crash on 1, ride on the "and" — one hand, two pads, half a '
                        "beat apart. Drill that pair on its own first.",
                        "The ride does not play beat 1 of a crash bar. If you hear "
                        "both, the hand went to the crash and came back too early.",
                        "Bars 2 and 4 are the plain ride groove. The hand should be "
                        "resting on the ride for those, not hovering.",
                        "The bass is pushing between the beats and will not mark "
                        "the down-beat you are crashing on. Count it yourself.",
                    ],
                ),
            ],
        ),
        module(
            "open-and-closed",
            "Open and closed",
            "the hat that hands the bar over",
            [
                lesson(
                    slug="open-hat-lead-in",
                    name="The Open Hat Lead-In",
                    tier="plain",
                    drums=open_hat_lead_in,
                    bass=QUARTER,
                    prereq=["disco-open-hats"],
                    summary="Closed hats through the bar with the last 8th opened "
                    "up — the most-played hi-hat move there is.",
                    description=(
                        'One note of the hat line moves to the other pad: the "and" '
                        "of 4, the last eighth before the bar turns over. It is "
                        "there to hand one bar to the next, and it is the single "
                        "most common thing a hi-hat does in popular music. Disco "
                        "Open Hats alternated the two pads all bar; this asks for "
                        "one move, once, at the point the hand is least ready."
                    ),
                    hints=[
                        "Index on the closed hat, middle on the open one, both on "
                        "the weak hand. The move is one finger, once a bar.",
                        "The open hat is the last note of the bar. Let it ring "
                        "across the bar line into the down-beat rather than cutting "
                        "it off.",
                        "Come straight back to the closed pad for beat 1. Landing "
                        "the down-beat on the open hat is the usual mistake and it "
                        "is instantly audible.",
                        "Drill the hat hand alone: seven closed, one open, over and "
                        "over, before adding the kick and snare.",
                    ],
                ),
                lesson(
                    slug="crash-after-open",
                    name="Open Hat into the Crash",
                    tier="core",
                    drums=crash_after_open,
                    bass=OCTAVE,
                    prereq=["open-hat-lead-in", "crash-on-one"],
                    summary="The open hat on the last 8th landing on a crash — one "
                    "gesture in two halves.",
                    description=(
                        "The two things you just learned are really one thing. The "
                        "open hat lifts at the end of the bar and the crash lands "
                        "on the down-beat that follows, so the hand travels open "
                        "hat, crash, closed hat across three consecutive eighths. "
                        "Played well it sounds like a single move; played badly it "
                        "sounds like three separate scrambles."
                    ),
                    hints=[
                        'The sequence is "open — crash — closed" on the last 8th, '
                        "beat 1, and the \"and\" of 1. Practise those three notes "
                        "alone, out of time.",
                        "The crash is the loud one, so the open hat before it does "
                        "not need to be. Let it ring rather than hitting it hard.",
                        'The "and" of 1 is where this comes apart — the hand is '
                        "still out at the crash. Get it home early.",
                        "Kick and snare do not move all lesson. If they wobble on "
                        "beat 1, the strong hand is waiting for the weak one.",
                    ],
                ),
                lesson(
                    slug="every-pad",
                    name="All Six Pads",
                    tier="stretch",
                    drums=every_pad,
                    bass=SYNCOPATED,
                    prereq=["crash-into-ride", "crash-after-open"],
                    summary="Two bars of hats with the open lead-in, two of ride "
                    "opened by a crash — every pad the app guarantees.",
                    description=(
                        "A verse and a chorus in four bars. Bars 1 and 2 are the "
                        "lead-in groove on the closed hat, the open hat at the end "
                        "of bar 2 pushes straight into the crash that opens bar 3, "
                        "and the ride carries bars 3 and 4 before handing back. "
                        "Kick and snare never move and no rhythm in it is new — "
                        "every difficulty is which pad, and when."
                    ),
                    hints=[
                        "Learn the map before the notes: hat, hat, ride, ride, with "
                        "one open hat and one crash at the join.",
                        "The join is the lesson. Open hat on the last 8th of bar 2, "
                        "crash on the down-beat of bar 3, ride from its \"and\".",
                        "Bar 4 hands back to bar 1: the ride has to be off the pad "
                        "and onto the closed hat by the next down-beat.",
                        "Play it as two two-bar halves before you play it as four "
                        "bars. Each half is a groove you already know.",
                    ],
                ),
            ],
        ),
    ],
    closing=checkpoint(
        slug="checkpoint-4",
        name="Checkpoint — The Cymbals",
        drums=checkpoint_4,
        bass=OCTAVE,
        summary="One bar each: the ride groove, a crash on 1, the open-hat "
        "lead-in, and a crash into the ride.",
        description=(
            "Four bars, and the timekeeping hand is on a different pad in each of "
            "them. Kick and snare are the same rock beat throughout — deliberately, "
            "so that everything you have to think about is above them. Switching "
            "cymbal every bar is harder than any one of these grooves and it is "
            "what makes them stick."
        ),
        hints=[
            "Ride, hat, hat-and-open, then ride again with a crash. Know the next "
            "bar's pad before the bar line.",
            "Bars 2 and 3 are both on the closed hat — the only pair that does not "
            "move. Use bar 2 to get the hand home.",
            "The crash in bar 4 takes the down-beat and the ride comes in on the "
            "\"and\". That is the one place the hand travels inside a beat.",
            "Kick and snare never change. If they move when the cymbal does, the "
            "hands are leaning on each other.",
        ],
    ),
)
