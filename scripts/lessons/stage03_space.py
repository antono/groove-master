"""Stage 3 — Space.

The first stage about the notes you *don't* play. Every pattern here is a groove
the student already owns with something taken out of it: a beat, a half bar, a
whole bar, or nearly everything. Nothing new is added — no new pad, no finer
grid, no hand travel — because the difficulty is meant to be the silence and
only the silence.

Silence is where a beginner's time actually fails. Inside a run of notes the
hands cover for the clock; the moment nothing sounds, the clock is all there is,
and a bar that comes back in a 16th early is the single most common thing that
makes a groove sound amateur. The backing bass matters more here than anywhere
else in the curriculum: during a hole it is the only thing left, which is why
these lessons fade from `quarter` (a note on every beat you are missing) to
`syncopated` (a line that is no help at all).
"""

from .bass import OCTAVE, QUARTER, RIFF, SYNCOPATED
from .grids import (
    BACKBEAT,
    BEATS,
    DOWNBEATS,
    EIGHTHS,
    cycle_bars,
    per_bar,
    voices,
)
from .midi import CLOSED_HH, KICK, SNARE
from .schema import checkpoint, lesson, module, stage


def without(positions, holes):
    """`positions` with every note that falls inside one of `holes` removed.

    A hole is a whole beat given by its index — `2` is beat 3 — and it swallows
    everything struck from that beat up to the next one, the 8ths and 16ths
    included. Holes are written as beats rather than as lists of positions so a
    pattern says "beat 3 is empty" rather than "these four notes are missing",
    which is also how the student has to think about it.
    """
    gone = {int(b) for b in holes}
    return [p for p in positions if int(p) not in gone]


# The groove every lesson in this stage cuts holes in: the Stage 2 rock beat,
# note for note. Nothing here is new until it is taken away.
ROCK = [(CLOSED_HH, EIGHTHS), (KICK, DOWNBEATS), (SNARE, BACKBEAT)]


def rock_with_holes(holes):
    """The rock beat with whole beats emptied — every voice, not just one."""
    return [(note, without(positions, holes)) for note, positions in ROCK]


# --- Module 1: holes ----------------------------------------------------------


def groove_hole_3(bars=4):
    """The rock beat with beat 3 empty — one silent beat a bar, mid-bar."""
    return voices(bars, *rock_with_holes([2]))


def groove_hole_bar_end(bars=4):
    """The rock beat with beat 4 empty, so the silence runs into the bar line.

    Harder than a hole in the middle for one reason: the note that ends it is a
    down-beat. A hole on beat 3 is a gap you land after; a hole on beat 4 is a
    gap you have to *start* out of, and starting is where the time goes.
    """
    return voices(bars, *rock_with_holes([3]))


def holes_walking(bars=4):
    """The hole moves one beat later each bar, then bar 4 has two.

    Four bars, four different shapes, and the last one takes out both 2 and 4 —
    the beats the snare was on, so the backbeat disappears from the bar that
    needs it most.
    """
    schedule = [[1], [2], [3], [1, 3]]
    return per_bar(bars, lambda bar: rock_with_holes(schedule[bar % len(schedule)]))


# --- Module 2: stop time ------------------------------------------------------


def stop_every_other_bar(bars=4):
    """Bars 1 and 3 groove; bars 2 and 4 are completely empty.

    Four beats of nothing, then a down-beat that has to be exactly right. There
    is no hat to hang on to — the pattern owns one elsewhere, so nothing is
    borrowed in (see the GUIDE-HAT RULE) and the silence is real silence.
    """
    return per_bar(bars, lambda bar: ROCK if bar % 2 == 0 else [])


def stop_and_answer(bars=4):
    """The same stop, with one snare on beat 4 of the empty bar.

    The answer is the proof. A student who lost count during the stop cannot
    place it, and unlike a missed down-beat it is obvious the instant it lands
    — one note, three beats after the groove stopped, with nothing around it.
    """
    answer = [(SNARE, [3])]
    return per_bar(bars, lambda bar: ROCK if bar % 2 == 0 else answer)


def stops_alternating(bars=4):
    """Two beats on, two beats off — and the halves swap every bar.

    Bar 1 plays its first half, bar 2 plays its second, so every other bar
    *opens* on silence and is entered on beat 3 from a standing start. Four
    beats of rest either side of it, no lead-in, and the count is the only
    thing that can put it in the right place.
    """
    first = [(note, [p for p in positions if p < 2]) for note, positions in ROCK]
    second = [(note, [p for p in positions if p >= 2]) for note, positions in ROCK]
    return per_bar(bars, lambda bar: first if bar % 2 == 0 else second)


# --- Module 3: sparse ---------------------------------------------------------


def whole_notes(bars=4):
    """Kick and hat together on beat 1, and nothing else for three beats.

    The thinnest lesson in the curriculum: four hits, one a bar. It sounds like
    nothing to play and is the hardest thing here to play *in time*, because
    three quarters of every bar is counted rather than felt.
    """
    return voices(bars, (CLOSED_HH, [0]), (KICK, [0]))


def half_notes(bars=4):
    """Kick on 1, snare on 3, a hat on both — two hits a bar, evenly spaced."""
    return voices(bars, (CLOSED_HH, DOWNBEATS), (KICK, [0]), (SNARE, [2]))


def sparse_doubling(bars=4):
    """One hit, then two, then four, then eight — the same pulse, four densities.

    Nothing changes but how much of the bar is filled, so the tempo has nowhere
    to hide: the usual mistake is to speed up as the bar gets busier and drag
    when it empties out again. The kick anchors beat 1 of every bar so the four
    bars are the same length by ear as well as on paper.
    """
    densities = [[0], DOWNBEATS, BEATS, EIGHTHS]
    return per_bar(
        bars,
        lambda bar: [(CLOSED_HH, densities[bar % len(densities)]), (KICK, [0])],
    )


# --- Checkpoint ---------------------------------------------------------------


def checkpoint_3(bars=4):
    """Four bars, four different silences: a hole, a stop, a crawl, a half bar."""
    return cycle_bars(
        bars,
        [
            rock_with_holes([2]),
            [],
            [(CLOSED_HH, DOWNBEATS), (KICK, [0]), (SNARE, [2])],
            [(note, [p for p in positions if p < 2]) for note, positions in ROCK],
        ],
    )


STAGE = stage(
    number=3,
    slug="space",
    title="Space",
    goal="The notes you do not play. A groove you already own with a beat, a "
    "half bar or a whole bar taken out of it — and coming back in exactly "
    "on time.",
    modules=[
        module(
            "holes",
            "Holes",
            "a beat taken out",
            [
                lesson(
                    slug="groove-hole-3",
                    name="The Hole on 3",
                    tier="plain",
                    drums=groove_hole_3,
                    bass=QUARTER,
                    prereq=["rock-beat-8th-hats", "eighths-through-rests"],
                    summary="The rock beat with beat 3 emptied — one silent beat "
                    "in the middle of every bar.",
                    description=(
                        "The groove you finished Stage 2 with, minus one beat. "
                        "Everything goes at once on beat 3 — kick and both hats — "
                        "so for a whole beat you are playing nothing and the bass "
                        "is the only thing left marking time. The notes either "
                        "side of the hole have not moved. If they have moved when "
                        "you play it, the hole is why."
                    ),
                    hints=[
                        "The hole is a beat you play, not a beat you wait through. "
                        "Count 3 out loud with the same weight as the beats you "
                        "are hitting.",
                        "The bass plays a note on every beat, including the one you "
                        "are missing. Use it — that is what it is there for.",
                        "Coming in early on beat 4 is the usual fault: the hand "
                        "starts moving during the silence. Keep it still and let "
                        "the count bring it down.",
                        "Play the whole groove without the hole for a bar first, "
                        "then take beat 3 out without changing anything else.",
                    ],
                ),
                lesson(
                    slug="groove-hole-bar-end",
                    name="The Hole at the Bar Line",
                    tier="core",
                    drums=groove_hole_bar_end,
                    bass=OCTAVE,
                    prereq=["groove-hole-3"],
                    summary="Beat 4 emptied instead, so the silence runs into the "
                    "bar line and you re-enter on the down-beat.",
                    description=(
                        "The same idea moved one beat later, and it is a different "
                        "problem. A hole in the middle of the bar is a gap you land "
                        "after; a hole at the end of it is a gap you have to start "
                        "out of, with the next down-beat as the first thing you "
                        'play. This shape is everywhere in real music — the groove '
                        'stops on the "and" of 3 and everyone comes back in '
                        "together on 1."
                    ),
                    hints=[
                        "The snare on 2 is now the last note of the bar. Everything "
                        "after it is counting.",
                        "Beat 1 of the next bar is the note this lesson is about. "
                        "It should land as firmly as if you had been playing right "
                        "up to it.",
                        "If the down-beat arrives early, you are counting the "
                        "silence faster than you played the notes. The bass bounces "
                        "through the hole in 8ths — stay with it.",
                        "Four bars means four re-entries. Getting one right is "
                        "luck; getting all four right is the lesson.",
                    ],
                ),
                lesson(
                    slug="holes-walking",
                    name="The Moving Hole",
                    tier="stretch",
                    drums=holes_walking,
                    bass=SYNCOPATED,
                    prereq=["groove-hole-bar-end"],
                    summary="The silent beat moves one later each bar — 2, then 3, "
                    "then 4, then both 2 and 4.",
                    description=(
                        "Four bars and no two the same. The hole walks through the "
                        "bar, and the last bar loses both 2 and 4 — the beats the "
                        "snare was on, so the backbeat vanishes from the bar that "
                        "leans on it hardest. Nothing about the groove changed; you "
                        "are simply never allowed to settle into it."
                    ),
                    hints=[
                        "Know which beat is missing before the bar starts. Reading "
                        "the hole as it arrives is already too late.",
                        "Bar 4 has no snare at all. It will feel like the floor "
                        "went — that is the exercise, not a mistake.",
                        "The bass is pushing between the beats now and will not "
                        "mark the missing ones for you. Count them yourself.",
                        "Bars 1 to 3 are one hole each and bar 4 is two. If bar 4 "
                        "collapses, drill it alone and put the other three back "
                        "afterwards.",
                    ],
                ),
            ],
        ),
        module(
            "stop-time",
            "Stop time",
            "a bar with nothing in it",
            [
                lesson(
                    slug="stop-every-other-bar",
                    name="Stop Time",
                    tier="plain",
                    drums=stop_every_other_bar,
                    bass=QUARTER,
                    prereq=["groove-hole-bar-end"],
                    summary="One bar of groove, one bar of nothing, twice over.",
                    description=(
                        "Four beats of silence is a long time. The groove plays for "
                        "a bar, stops dead, and comes back exactly one bar later — "
                        "and there is no hat ticking underneath to hold on to, "
                        "because the pattern owns its hat and takes it away with "
                        "everything else. What is left is the bass on the beat and "
                        "your own counting."
                    ),
                    hints=[
                        'Count the empty bar out loud: "2, 2, 3, 4". Saying it is '
                        "the difference between a rest and a guess.",
                        "Do not stop moving. Keep the hand going through the silent "
                        "bar without letting it touch the pad, so the pulse never "
                        "actually stops.",
                        "The bass plays four notes in the empty bar. Land your "
                        "down-beat with its first note of the next one.",
                        "The lesson ends on a silent bar and one final hit. That "
                        "last note is scored — it is the whole point.",
                    ],
                ),
                lesson(
                    slug="stop-and-answer",
                    name="Stop and Answer",
                    tier="core",
                    drums=stop_and_answer,
                    bass=RIFF,
                    prereq=["stop-every-other-bar"],
                    summary="The same stop, with one snare on beat 4 of the empty "
                    "bar — the note that proves you kept counting.",
                    description=(
                        "One note in the middle of the silence, three beats after "
                        "the groove stopped, with nothing on either side of it. "
                        "Unlike a down-beat, which can be nudged into place by the "
                        "bar starting, this one is naked: if the count drifted, "
                        "everybody hears exactly how far. The bass has become a "
                        "four-bar riff rather than a metronome, so it is company "
                        "rather than a crutch."
                    ),
                    hints=[
                        "The answer is on beat 4, the last beat of the empty bar. "
                        "One snare, nothing with it.",
                        'Count the whole empty bar and put the snare on "4" — do '
                        "not count to three and reach for it.",
                        "A late answer usually means you relaxed on beat 1 of the "
                        "stop. The count has to run at full attention from the "
                        "moment the groove ends.",
                        "The riff underneath has a hole of its own in bar 3. When "
                        "the two silences overlap you are on your own, and that is "
                        "the bar to check.",
                    ],
                ),
                lesson(
                    slug="stops-alternating",
                    name="Half On, Half Off",
                    tier="stretch",
                    drums=stops_alternating,
                    bass=SYNCOPATED,
                    prereq=["stop-and-answer"],
                    summary="Two beats of groove, two of silence — and the halves "
                    "swap every bar, so every other bar opens empty.",
                    description=(
                        "The groove plays the first half of bar 1 and the second "
                        "half of bar 2, which means bar 2 begins with nothing at "
                        "all and is entered on beat 3 from a standing start. Four "
                        "beats of rest sit either side of that entry with no "
                        "lead-in of any kind. It is the hardest entrance in the "
                        "stage and the most useful one: coming in mid-bar, on time, "
                        "with no help."
                    ),
                    hints=[
                        "Every entry is a different beat: 1, then 3, then 1, then 3. "
                        "Know which one is next.",
                        "The mid-bar entry has no down-beat to lean on. Count "
                        '"1, 2" through the silence and play on "3".',
                        "The bass pushes off the beat and will pull you early. Your "
                        "own count is the grid here, not the bass.",
                        "Two beats on is barely enough to settle. Treat each half "
                        "bar as a phrase you have to place, not as a groove you can "
                        "fall into.",
                    ],
                ),
            ],
        ),
        module(
            "sparse",
            "Sparse",
            "almost nothing, exactly on time",
            [
                lesson(
                    slug="whole-notes",
                    name="One Hit a Bar",
                    tier="plain",
                    drums=whole_notes,
                    bass=QUARTER,
                    prereq=["kick-hats-unison"],
                    summary="Kick and hat together on beat 1, and nothing at all "
                    "for the other three.",
                    description=(
                        "Four hits in the whole lesson. It looks like the easiest "
                        "thing in the app and it is the hardest to land, because "
                        "three quarters of every bar has to be counted rather than "
                        "felt — and the only way to know you counted right is "
                        "whether the next hit is early. Two pads at once, which you "
                        "have done since Stage 2, so nothing about the hit itself "
                        "is new."
                    ),
                    hints=[
                        "Count all four beats every bar, out loud. This lesson is "
                        "the count with a hit stapled to it.",
                        "Rushing is the fault, always. If a bar feels long you are "
                        "counting too fast — trust the bass, which plays all four "
                        "beats under you.",
                        "Keep the hand moving through the empty beats without "
                        "touching the pads, as if you were playing quarters and "
                        "only one of them landed.",
                        "Both fingers drop together. Three beats of waiting makes it "
                        "very easy to let the kick arrive first.",
                    ],
                ),
                lesson(
                    slug="half-notes",
                    name="Two Hits a Bar",
                    tier="core",
                    drums=half_notes,
                    bass=OCTAVE,
                    prereq=["whole-notes"],
                    summary="Kick on 1, snare on 3, a hat with each — two hits a "
                    "bar with a beat of silence between them.",
                    description=(
                        "Half the bar filled and the gaps evenly spaced, which "
                        "makes a different demand from the last lesson: the two "
                        "hits have to be the same distance apart every time. This "
                        "is also the placement that half-time grooves are built on "
                        "— the backbeat on 3 rather than on 2 and 4 — so it is "
                        "worth getting the feel of it now, with nothing else "
                        "happening."
                    ),
                    hints=[
                        "Beat 3 is the snare, not beat 2. The pull towards 2 is "
                        "strong and it is wrong here.",
                        "The two hits should divide the bar exactly in half. If the "
                        "snare drifts early, the bar has two long beats and two "
                        "short ones.",
                        "The hat plays with both hits and nowhere else, so each one "
                        "is a two-pad stack.",
                        "Beats 2 and 4 are empty and the octave bass bounces "
                        "through them. Let it fill the gap; do not fill it "
                        "yourself.",
                    ],
                ),
                lesson(
                    slug="sparse-doubling",
                    name="Twice as Many, Every Bar",
                    tier="stretch",
                    drums=sparse_doubling,
                    bass=SYNCOPATED,
                    prereq=["half-notes", "eighths-weak-hand"],
                    summary="One hit, then two, then four, then eight — the same "
                    "pulse at four densities.",
                    description=(
                        "The bar fills up as the lesson goes: a single hit, then "
                        "half notes, then quarters, then 8ths, with a kick anchoring "
                        "beat 1 all the way through. Nothing about the tempo "
                        "changes, which is the point — the standard fault is to "
                        "speed up as the bar gets busier and drag when it thins out "
                        "again, and here you do both inside four bars."
                    ),
                    hints=[
                        "The kick on beat 1 is the same distance apart in all four "
                        "bars. If it is not, the density is driving your tempo.",
                        "Bar 4 is a plain 8th-note hat line — you played it in "
                        "Stage 1. If it feels fast, the first three bars were slow.",
                        "Rushing shows up between bars 3 and 4 and dragging between "
                        "bars 4 and 1 as it wraps round. Check those two joins.",
                        "The bass is no help by design. Keep your own count running "
                        "underneath all four bars.",
                    ],
                ),
            ],
        ),
    ],
    closing=checkpoint(
        slug="checkpoint-3",
        name="Checkpoint — Space",
        drums=checkpoint_3,
        bass=OCTAVE,
        summary="Four bars, four different silences: a hole, a whole empty bar, a "
        "crawl, and a half bar.",
        description=(
            "Every kind of gap in the stage, one after another, with no two bars "
            "the same shape. Bar 1 has a beat missing, bar 2 has nothing in it at "
            "all, bar 3 is down to two hits, and bar 4 plays only its first half. "
            "The groove is never the difficulty; knowing where you are when "
            "nothing is sounding is. Play this clean and silence has stopped "
            "being a problem."
        ),
        hints=[
            "Four bars, four different re-entries. Name each one before it "
            "arrives.",
            "Bar 2 is empty. Count it out loud — it is the only bar where nothing "
            "at all reminds you where the beat is.",
            "Bar 4 stops halfway and the lesson ends on the down-beat after it. "
            "That last hit is scored.",
            "The octave bass runs all the way through. It is your metronome for "
            "the whole lesson — never your cue to play.",
        ],
    ),
)
