"""Stage 10 — Form & Fills.

The first stage of Music, and the first one where the question is not "can you
play it" but "does it say anything". Three ideas, each of them a thing a
drummer does *to* a groove rather than a groove itself: the push, which moves
a down-beat early and leaves a hole where it was; the fill, which announces
that something is about to change; and form, where a lesson stops being a loop
and becomes a piece with a beginning, a middle and an end.

The form module is the first to use **eight-bar lessons** — the chart and the
highway have always drawn whatever they are given, and eight bars is where a
verse and a chorus can both live. Nothing in this stage is finer than a 16th
or newer than the pads Foundations ends on; every difficulty is *when*, not
*what*.
"""

from .bass import PEDAL, QUARTER, RIFF, SYNCOPATED
from .grids import BACKBEAT, BEATS, DOWNBEATS, EIGHTHS, cycle_bars, per_bar
from .midi import CLOSED_HH, CRASH, KICK, OPEN_HH, RIDE, SNARE
from .schema import checkpoint, lesson, module, stage

PUSH = 3.5  # the "and" of 4 — the note that arrives before the bar does

# The groove underneath the stage, same as Two Bars: the Stage 2 rock beat.
CORE = [(KICK, DOWNBEATS), (SNARE, BACKBEAT)]
ROCK = [(CLOSED_HH, EIGHTHS)] + CORE

# Two beats of snare 16ths — the working drummer's first fill.
FILL_16 = [2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]


# --- Module 1: the push ---------------------------------------------------------


def push_into_one(bars=4):
    """Every other bar the kick arrives early, and the next down-beat is empty.

    The push: the kick that belonged to beat 1 of the even bars plays on the
    "and" of 4 *before* them instead. Nothing is added — a note moved half a
    beat left — but the bar line stops being where the accent is, which is the
    single most common thing pop and funk do to a groove.
    """
    pushed = [(CLOSED_HH, EIGHTHS), (KICK, [0, 2, PUSH]), (SNARE, BACKBEAT)]
    landed = [(CLOSED_HH, EIGHTHS), (KICK, [2]), (SNARE, BACKBEAT)]
    return per_bar(bars, lambda bar: pushed if bar % 2 == 0 else landed)


def push_with_crash(bars=4):
    """The pushed note gets the crash, and the down-beat it displaced stays bare.

    This is how a push is actually played on a kit: the cymbal lands *with*
    the early kick and rings across the bar line, so the down-beat that no
    longer has a note on it still has sound over it. The hat stands down for
    that one beat — the crash is the timekeeper's note, moved early.
    """
    pushed = [
        (CLOSED_HH, EIGHTHS),
        (KICK, [0, 2, PUSH]),
        (CRASH, [PUSH]),
        (SNARE, BACKBEAT),
    ]
    landed = [
        (CLOSED_HH, [p for p in EIGHTHS if p != 0]),  # the crash rings through 1
        (KICK, [2]),
        (SNARE, BACKBEAT),
    ]
    return per_bar(bars, lambda bar: pushed if bar % 2 == 0 else landed)


def pushed_stop(bars=4):
    """Push into a whole bar of silence, then come back with the answer.

    The hit-and-hold: bar 2 pushes its last 8th with kick and crash together,
    bar 3 is completely empty while the cymbal rings, and bar 4 re-enters on
    the down-beat and runs a snare fill home. Space taught holding an empty
    bar; this is the same hole with a *musical* edge on each side — thrown
    into by an accent, exited into a fill.
    """

    def for_bar(bar):
        pos = bar % 4
        if pos == 0:
            return ROCK
        if pos == 1:
            return [
                (CLOSED_HH, EIGHTHS),
                (KICK, [0, 2, PUSH]),
                (CRASH, [PUSH]),
                (SNARE, BACKBEAT),
            ]
        if pos == 2:
            return []  # the hold — nothing sounds, the crash is still ringing
        return [
            (CLOSED_HH, [p for p in EIGHTHS if p < 3]),
            (KICK, [0, 2]),
            (SNARE, [1, 3, 3.25, 3.5, 3.75]),  # beat 4 becomes the run home
        ]

    return per_bar(bars, for_bar)


# --- Module 2: fills ------------------------------------------------------------


def fill_two_beats(bars=4):
    """Three bars of groove, then two beats of snare 16ths into a crash.

    The first real fill: beats 3 and 4 of the last bar hand the bar to the
    snare in 16ths — twice the density of the turnaround in Two Bars — and the
    crash that opens the loop is what the fill lands on. A fill is not
    decoration; it is an announcement, and the crash is what it announces.
    """

    def for_bar(bar):
        pos = bar % 4
        if pos == 0:
            return [(CRASH, [0])] + ROCK
        if pos < 3:
            return ROCK
        return [
            (CLOSED_HH, [p for p in EIGHTHS if p < 2]),
            (KICK, [0]),
            (SNARE, [1] + FILL_16),
        ]

    return per_bar(bars, for_bar)


def fill_with_kick(bars=4):
    """The same fill with the kick taking the last 16th of each beat.

    Three snares and a kick, twice: R L R K, R L R K. The foot lands where a
    tom would on a kit — the fill gets a floor under it — and the hands get a
    16th of travel time they did not have before. The kick notes are the two
    everybody rushes, because the foot wants to play *with* a hand rather
    than after one.
    """
    fill_snare = [p for p in FILL_16 if p not in (2.75, 3.75)]
    fill_kick = [2.75, 3.75]

    def for_bar(bar):
        pos = bar % 4
        if pos == 0:
            return [(CRASH, [0])] + ROCK
        if pos < 3:
            return ROCK
        return [
            (CLOSED_HH, [p for p in EIGHTHS if p < 2]),
            (KICK, [0] + fill_kick),
            (SNARE, [1] + fill_snare),
        ]

    return per_bar(bars, for_bar)


def fill_broken(bars=4):
    """A fill with holes in it: dotted spacing, then the door slammed shut.

    Four notes where there were eight — on the beat, off the grid-of-8ths, and
    two 16ths at the end — so the fill's shape is syncopation rather than a
    run. Broken fills are harder than busy ones for the same reason Space was
    harder than the Backbeat: the notes you leave out still have to be exactly
    the right length.
    """
    broken = [2, 2.75, 3.5, 3.75]  # dotted, dotted, then the two-16th slam

    def for_bar(bar):
        pos = bar % 4
        if pos == 0:
            return [(CRASH, [0])] + ROCK
        if pos < 3:
            return ROCK
        return [
            (CLOSED_HH, [p for p in EIGHTHS if p < 2]),
            (KICK, [0]),
            (SNARE, [1] + broken),
        ]

    return per_bar(bars, for_bar)


# --- Module 3: song form (eight bars) --------------------------------------------


def verse_chorus(bars=8):
    """Four bars of verse on the hat, four of chorus on the ride — a real form.

    The first eight-bar lesson. The verse is the rock beat with an open hat on
    its last 8th to hand the section over; the chorus opens on a crash and
    lives on the ride; the eighth bar turns the whole thing around with the
    snare. Every piece is a lesson already passed — the new thing is that they
    happen once each, in order, and you have to know where you are.
    """

    def for_bar(bar):
        pos = bar % 8
        if pos < 3:  # verse
            return ROCK
        if pos == 3:  # the hand-over into the chorus
            return [
                (CLOSED_HH, [p for p in EIGHTHS if p != PUSH]),
                (OPEN_HH, [PUSH]),
            ] + CORE
        if pos == 4:  # chorus top
            return [(CRASH, [0]), (RIDE, [p for p in EIGHTHS if p != 0])] + CORE
        if pos < 7:  # chorus
            return [(RIDE, EIGHTHS)] + CORE
        return [  # bar 8: the turnaround home
            (RIDE, [p for p in EIGHTHS if p < 2]),
            (KICK, [0]),
            (SNARE, [1, 2, 2.5, 3, 3.5]),
        ]

    return per_bar(bars, for_bar)


def eight_bar_build(bars=8):
    """Eight bars that add one layer at a time, then spend it all on a fill.

    An arrangement in miniature: two bars of kick and quarter hats, two with
    the backbeat in, two of the full rock beat, one of four-on-the-floor, and
    a fill. Nothing new is *played* anywhere in it — what is new is that the
    music gets bigger on a schedule, and the schedule is yours to keep. The
    standard fault is the same one Sparse hunted: density pulling tempo.
    """

    def for_bar(bar):
        pos = bar % 8
        if pos < 2:
            return [(CLOSED_HH, BEATS), (KICK, DOWNBEATS)]
        if pos < 4:
            return [(CLOSED_HH, BEATS)] + CORE
        if pos < 6:
            return ROCK
        if pos == 6:
            return [(CLOSED_HH, EIGHTHS), (KICK, BEATS), (SNARE, BACKBEAT)]
        return [
            (CLOSED_HH, [p for p in EIGHTHS if p < 2]),
            (KICK, [0]),
            (SNARE, [1] + FILL_16),
        ]

    return per_bar(bars, for_bar)


def the_arrangement(bars=8):
    """Intro, verse, fill, chorus, push, ending — a whole song in eight bars.

    The stage in one piece. A crash and bare hats to open, two bars of verse,
    a fill into the chorus, a chorus that runs on the ride over four-on-the-
    floor, a push at the end of its last bar, and an ending that stops the
    band and leaves one snare in the silence before the final hit. Every
    module of this stage appears exactly once, which is what makes it an
    arrangement rather than a medley.
    """

    def for_bar(bar):
        pos = bar % 8
        if pos == 0:  # intro: the count the band hears
            return [(CRASH, [0]), (CLOSED_HH, [p for p in EIGHTHS if p != 0])]
        if pos < 3:  # verse
            return ROCK
        if pos == 3:  # fill into the chorus
            return [
                (CLOSED_HH, [p for p in EIGHTHS if p < 2]),
                (KICK, [0]),
                (SNARE, [1] + FILL_16),
            ]
        if pos == 4:  # chorus top: crash, ride, and the floor
            return [
                (CRASH, [0]),
                (RIDE, [p for p in EIGHTHS if p != 0]),
                (KICK, BEATS),
                (SNARE, BACKBEAT),
            ]
        if pos == 5:
            return [(RIDE, EIGHTHS), (KICK, BEATS), (SNARE, BACKBEAT)]
        if pos == 6:  # last chorus bar pushes its ending
            return [
                (RIDE, EIGHTHS),
                (KICK, [0, 2, PUSH]),
                (CRASH, [PUSH]),
                (SNARE, BACKBEAT),
            ]
        return [(SNARE, [3])]  # the ending: silence, one pickup, then the hit

    return per_bar(bars, for_bar)


# --- Checkpoint -------------------------------------------------------------------


def checkpoint_10(bars=4):
    """One bar each: the push, the landing, the ride chorus, the fill."""
    return cycle_bars(
        bars,
        [
            [
                (CRASH, [0]),
                (CLOSED_HH, [p for p in EIGHTHS if p != 0]),
                (KICK, [0, 2, PUSH]),
                (SNARE, BACKBEAT),
            ],
            [(CLOSED_HH, EIGHTHS), (KICK, [2]), (SNARE, BACKBEAT)],
            [(RIDE, EIGHTHS), (KICK, BEATS), (SNARE, BACKBEAT)],
            [
                (CLOSED_HH, [p for p in EIGHTHS if p < 2]),
                (KICK, [0]),
                (SNARE, [1] + FILL_16),
            ],
        ],
    )


STAGE = stage(
    number=10,
    slug="form",
    title="Form & Fills",
    goal="A groove that says something: down-beats moved early, fills that "
    "announce the change, and eight-bar pieces with a beginning, a middle "
    "and an end.",
    modules=[
        module(
            "the-push",
            "The push",
            "the down-beat, early",
            [
                lesson(
                    slug="push-into-one",
                    name="The Push",
                    tier="plain",
                    drums=push_into_one,
                    bass=QUARTER,
                    prereq=["two-bar-kick", "kick-snare-8ths"],
                    bpm=84,
                    summary="Every other bar's first kick arrives half a beat "
                    "early, and the down-beat it left is empty.",
                    description=(
                        "One note moves and everything changes. The kick that "
                        "belonged to beat 1 of the even bars plays on the "
                        "\"and\" of 4 before them instead, so the accent lands "
                        "ahead of the bar line and the bar line itself is "
                        "silent in the drums. This is the push — the single "
                        "most common thing pop, rock and funk do to a groove — "
                        "and the whole trick is that the hat keeps playing "
                        "beat 1 as if nothing happened."
                    ),
                    hints=[
                        "The pushed kick is the last 8th of the odd bars. Count "
                        '"4 and" and play the kick on the "and".',
                        "Beat 1 of the even bars has a hat and nothing else. "
                        "Putting a kick back there is the mistake this lesson "
                        "exists to catch.",
                        "The hat does not move all lesson. If it hiccups at the "
                        "bar line, the pushed kick is dragging it.",
                        "The bass still marks every beat, including the one your "
                        "kick abandoned. Lean on it through the empty down-beat.",
                    ],
                ),
                lesson(
                    slug="push-with-crash",
                    name="Crash the Push",
                    tier="core",
                    drums=push_with_crash,
                    bass=RIFF,
                    prereq=["push-into-one", "crash-every-two"],
                    bpm=84,
                    summary="The crash lands with the pushed kick and rings "
                    "across the bar line.",
                    description=(
                        "How a push is actually played: the cymbal comes with "
                        "the early kick, not after it, and rings over the bar "
                        "line so the empty down-beat still has sound above it. "
                        "The hat stands down for that one beat — its note is "
                        "the crash, moved early. Two pads a hand and half a "
                        "beat of warning: this is the crash-into-ride travel "
                        "from The Cymbals, aimed at a bar line."
                    ),
                    hints=[
                        'Kick and crash on the "and" of 4 are one motion, two '
                        "hands. Drill that single stack before running the loop.",
                        "The bar after the push opens with no hat — the crash is "
                        'still ringing. First hat back is the "and" of 1.',
                        "Do not crash beat 1 as well. The whole point is that "
                        "the accent already happened.",
                        "If the crash keeps landing on 4 instead of its \"and\", "
                        "you are hearing it as the end of the bar rather than "
                        "the start of the next one. It belongs to bar 2.",
                    ],
                ),
                lesson(
                    slug="pushed-stop",
                    name="Push, Then Silence",
                    tier="stretch",
                    drums=pushed_stop,
                    bass=SYNCOPATED,
                    prereq=["push-with-crash", "stop-every-other-bar"],
                    bpm=84,
                    summary="Push into a whole empty bar, hold it, and come back "
                    "with a fill.",
                    description=(
                        "The hit-and-hold, straight off a thousand records: bar "
                        "2 throws its last 8th forward with kick and crash "
                        "together, bar 3 is nothing at all while the cymbal "
                        "rings, and bar 4 re-enters on the down-beat and runs a "
                        "snare figure home. You held an empty bar in Space — "
                        "but not one you were thrown into by an accent, and "
                        "not one you had to leave *into a fill*. Both edges of "
                        "the silence are musical now, and both are yours."
                    ),
                    hints=[
                        "The empty bar starts half a beat after the push. Count "
                        "it in full — the crash ringing is not the count.",
                        "Re-entry is a plain down-beat with three beats of "
                        "silence behind it. It wants to be early; do not let it.",
                        "Beat 4 of the last bar is a four-note snare run. It "
                        "ends the phrase — do not let it become the next one's "
                        "count-in.",
                        "The bass pushes through the silent bar and will not "
                        "mark it for you. Your own count is the only clock in "
                        "bar 3.",
                    ],
                ),
            ],
        ),
        module(
            "fills",
            "Fills",
            "two beats that announce the change",
            [
                lesson(
                    slug="fill-two-beats",
                    name="The 16th Fill",
                    tier="plain",
                    drums=fill_two_beats,
                    bass=QUARTER,
                    prereq=["turnaround-snare", "hats-16ths-split"],
                    bpm=84,
                    summary="Three bars of groove, then beats 3 and 4 go to the "
                    "snare in 16ths, landing on a crash.",
                    description=(
                        "The working drummer's first fill: eight snare 16ths "
                        "across the last two beats of the phrase, into the "
                        "crash that opens the next one. It is the turnaround "
                        "from Two Bars at twice the density, and it has a job "
                        "now — a fill is an announcement that the phrase is "
                        "ending, and the crash is what it announces. Split the "
                        "16ths between your hands, exactly as you learned them."
                    ),
                    hints=[
                        "The fill is two beats, not three. Groove through beat "
                        "2 — starting the fill early is the classic giveaway.",
                        "Two hands share the 16ths, strictly alternating, lead "
                        "hand first. One hand playing eight is a different and "
                        "harder lesson.",
                        "The crash is the fill's last note in spirit: land it "
                        "as the down-beat, with the kick, and get straight back "
                        "to the hat.",
                        "If the fill rushes, the crash arrives early and the "
                        "whole next bar is dragged in with it. The fill must sit "
                        "inside the same tempo as the groove.",
                    ],
                ),
                lesson(
                    slug="fill-with-kick",
                    name="Kick in the Fill",
                    tier="core",
                    drums=fill_with_kick,
                    bass=RIFF,
                    prereq=["fill-two-beats", "kick-16th-grid"],
                    bpm=84,
                    summary="The same fill with the kick taking the last 16th of "
                    "each beat: R L R K, R L R K.",
                    description=(
                        "Three snares and a kick, twice over. On a kit the foot "
                        "takes the note a tom would — the fill gets a floor "
                        "under it — and your hands get one 16th of rest they "
                        "did not have before. The kick notes are the ones "
                        "everybody rushes: the foot wants to land with a hand, "
                        "and here it must land after one, alone, twice."
                    ),
                    hints=[
                        'Say the sticking before you play it: "R L R foot, '
                        'R L R foot."',
                        "The kick is the fourth 16th of each fill beat, alone. "
                        "If you hear kick and snare together, the foot came "
                        "early.",
                        "The hands do not change from the last lesson — they "
                        "just skip every fourth note. Play the full snare fill "
                        "once, then give those notes away.",
                        "Land the crash with the kick on the next down-beat, "
                        "same as before. The fill changed; the landing did not.",
                    ],
                ),
                lesson(
                    slug="fill-broken",
                    name="The Broken Fill",
                    tier="stretch",
                    drums=fill_broken,
                    bass=SYNCOPATED,
                    prereq=["fill-with-kick"],
                    bpm=84,
                    summary="A fill with holes in it: two dotted notes, then two "
                    "16ths slamming the door.",
                    description=(
                        "Four notes where there were eight — on beat 3, off the "
                        "8th grid, and a pair of 16ths at the very end. A "
                        "broken fill is harder than a busy one for the same "
                        "reason Space was harder than the Backbeat: the notes "
                        "you leave out still have to be exactly the right "
                        "length, and there is no run of 16ths to carry your "
                        "hand from one to the next. This is the fill as "
                        "syncopation, and it is the one that sounds like a "
                        "drummer rather than an exercise."
                    ),
                    hints=[
                        'Count the full 16 grid — "3 e and a 4 e and a" — and '
                        'play only "3", "a", "and", "a".',
                        "The second note is the hard one: off the 8th grid, "
                        "alone, a dotted 8th after the first. If it lands on "
                        'the "and" the fill has straightened.',
                        "The last two notes are a pair, tight, into the crash. "
                        "They are the door slamming — do not let them splay.",
                        "Keep the hand moving through the holes the way you "
                        "did in Space: the silences are played, just not "
                        "sounded.",
                    ],
                ),
            ],
        ),
        module(
            "song-form",
            "Song form",
            "eight bars with a shape",
            [
                lesson(
                    slug="verse-chorus",
                    name="Verse / Chorus",
                    tier="plain",
                    drums=verse_chorus,
                    bass=RIFF,
                    prereq=["full-phrase", "checkpoint-5"],
                    bpm=84,
                    bars=8,
                    summary="Eight bars, one shape: four of verse on the hat, "
                    "four of chorus on the ride.",
                    description=(
                        "The first eight-bar lesson in the app. Four bars of "
                        "verse on the closed hat, an open hat to hand the "
                        "section over, a crash into four bars of chorus on the "
                        "ride, and a snare turnaround to bring it home. Every "
                        "bar is a lesson you have already passed — what is new "
                        "is that each one happens once, in order, and the only "
                        "way to play it right is to know which bar you are in "
                        "for all eight of them."
                    ),
                    hints=[
                        "Learn the map before the notes: verse, verse, verse, "
                        "hand-over, chorus top, chorus, chorus, turnaround.",
                        "Count bars all the way to eight. Four-bar habits will "
                        "try to crash in the middle of the verse.",
                        "The open hat at the end of bar 4 and the crash on bar "
                        "5 are one gesture across the bar line — the same join "
                        "you built in The Cymbals.",
                        "The turnaround bar is the only one where the ride "
                        "stops. Its snare run hands the form back to bar 1.",
                    ],
                ),
                lesson(
                    slug="eight-bar-build",
                    name="The Build",
                    tier="core",
                    drums=eight_bar_build,
                    bass=PEDAL,
                    prereq=["verse-chorus", "four-bar-build"],
                    bpm=84,
                    bars=8,
                    summary="Eight bars that add one layer every two: from bare "
                    "kick and quarter hats to a fill that spends it all.",
                    description=(
                        "An arrangement in miniature. Two bars of kick under "
                        "quarter hats, two with the backbeat in, two of the "
                        "full rock beat, one of four-on-the-floor, and a 16th "
                        "fill to cash it in. You built across four bars in Two "
                        "Bars; doubled, the build gets slow enough to feel like "
                        "a real song getting louder — and slow enough that "
                        "keeping the tempo flat while the music grows becomes "
                        "the entire exercise. The bass holds one long note per "
                        "bar and will not push you anywhere."
                    ),
                    hints=[
                        "The kick on beat 1 is identical in all eight bars. It "
                        "is your tempo meter — if bar 7's kick is closer to bar "
                        "8's than bar 1's was to bar 2's, the build rushed.",
                        "Each new layer enters on an odd bar. Know what you are "
                        "adding before the bar line, not at it.",
                        "Bars 1 and 2 sound almost empty and are the hardest to "
                        "keep honest. Do not fill them early.",
                        "The fill is the release of everything the build "
                        "wound up. Spend it, land the crash-less down-beat, "
                        "and the loop starts thin again — that contrast is the "
                        "piece.",
                    ],
                ),
                lesson(
                    slug="the-arrangement",
                    name="The Arrangement",
                    tier="stretch",
                    drums=the_arrangement,
                    bass=SYNCOPATED,
                    prereq=["eight-bar-build", "pushed-stop", "fill-broken"],
                    bpm=84,
                    bars=8,
                    summary="Intro, verse, fill, chorus, push, ending — a whole "
                    "song in eight bars.",
                    description=(
                        "The stage in one piece. A crash over bare hats to "
                        "open, two bars of verse, a 16th fill into a chorus "
                        "that rides over four-on-the-floor, a push at the end "
                        "of the chorus's last bar, and an ending: silence, one "
                        "snare pickup on beat 4, and the final hit. Every "
                        "module of this stage appears exactly once — which is "
                        "what makes it an arrangement rather than a medley, "
                        "and what makes losing your place cost more than "
                        "missing a note."
                    ),
                    hints=[
                        "Eight different jobs in eight bars. Name them out loud "
                        "before the first run: intro, verse, verse, fill, "
                        "chorus, chorus, push, ending.",
                        "Bar 1 is hats and one crash — an intro, not a groove. "
                        "Resist starting the kick early.",
                        "The push at the end of bar 7 throws you into the "
                        "quietest bar of the piece. Land the crash, then play "
                        "almost nothing.",
                        "The last bar is one snare, on 4, alone. It sets up the "
                        "closing hit the way a singer takes a breath — place "
                        "it, don't sneak it.",
                    ],
                ),
            ],
        ),
    ],
    closing=checkpoint(
        slug="checkpoint-10",
        name="Checkpoint — Form & Fills",
        drums=checkpoint_10,
        bass=RIFF,
        bpm=84,
        summary="One bar each: the pushed top, the empty-one landing, the ride "
        "chorus, and the 16th fill.",
        description=(
            "Four bars, four jobs from the stage: a bar that pushes its ending, "
            "a bar that opens with no kick at all, a chorus bar on the ride "
            "over the floor, and the 16th fill to bring it round. Every join "
            "between them is one of the joins the stage taught, and the loop "
            "only sounds like music if all four land as one phrase."
        ),
        hints=[
            "Bar 1 ends early — the push — and bar 2 opens without a kick. "
            "That pair is the stage in two bars.",
            "The hand moves to the ride for bar 3 and back off it for the "
            "fill. Two travels, both on bar lines.",
            "The fill lands on the closing crash of the loop. Keep it inside "
            "the tempo the groove set.",
            "If you lose the form, do not chase it mid-bar. Wait for the "
            "crash and come in at the top.",
        ],
    ),
)
