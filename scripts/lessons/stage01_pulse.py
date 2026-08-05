"""Stage 1 — Pulse.

One voice sounding at a time; nothing ever stacks. The whole stage is about a
strike that lands where you meant it, and a clock that keeps running when the
pattern stops helping you.

Hand convention, set here and kept for the rest of the curriculum:
**strong hand plays kick and snare, weak hand plays the hi-hats.**
"""

from .bass import OCTAVE, QUARTER, SYNCOPATED
from .grids import BEATS, EIGHTHS, cycle_bars, per_bar, voices
from .midi import CLOSED_HH, KICK, SNARE
from .schema import checkpoint, lesson, module, stage

# --- Module 1: the strike -----------------------------------------------------


def kick_quarters(bars=4):
    """Kick on every beat — one finger, straight quarter notes."""
    return voices(bars, (KICK, BEATS))


def hats_quarters(bars=4):
    """The same rhythm on the weak hand's hi-hat."""
    return voices(bars, (CLOSED_HH, BEATS))


def quarters_hand_swap(bars=4):
    """Quarters, but the hand changes at every bar line: kick, hat, kick, hat."""
    return per_bar(bars, lambda bar: [(CLOSED_HH if bar % 2 else KICK, BEATS)])


# --- Module 2: two hands ------------------------------------------------------


def alternating_quarters(bars=4):
    """Snare, hat, snare, hat — one hand per beat, hands trading."""
    return voices(bars, (SNARE, [0, 2]), (CLOSED_HH, [1, 3]))


def alternating_8ths(bars=4):
    """The single stroke roll: snare on the numbers, hat on the "and"s."""
    return voices(bars, (SNARE, EIGHTHS[0::2]), (CLOSED_HH, EIGHTHS[1::2]))


def alternating_8ths_swap(bars=4):
    """The same 8ths, with the lead hand flipping at every bar line.

    Odd bars start on the snare, even bars on the hat. The notes never change —
    only which hand owns the down-beat — so the exercise is entirely in knowing
    where you are.
    """

    def for_bar(bar):
        lead, other = (CLOSED_HH, SNARE) if bar % 2 else (SNARE, CLOSED_HH)
        return [(lead, EIGHTHS[0::2]), (other, EIGHTHS[1::2])]

    return per_bar(bars, for_bar)


# --- Module 3: one hand, faster -----------------------------------------------


def eighths_strong_hand(bars=4):
    """Eight 8ths a bar on the snare — one hand, no help from the other."""
    return voices(bars, (SNARE, EIGHTHS))


def eighths_weak_hand(bars=4):
    """The same, on the weak hand's hi-hat."""
    return voices(bars, (CLOSED_HH, EIGHTHS))


def eighths_through_rests(bars=4):
    """8ths with beat 3 removed — the grid has to survive a hole in it."""
    return voices(bars, (CLOSED_HH, [p for p in EIGHTHS if p not in (2, 2.5)]))


# --- Checkpoint ---------------------------------------------------------------


def checkpoint_1(bars=4):
    """One bar each of the stage: quarters, alternating 8ths, 8ths, 8ths with a hole."""
    return cycle_bars(
        bars,
        [
            [(KICK, BEATS)],
            [(SNARE, EIGHTHS[0::2]), (CLOSED_HH, EIGHTHS[1::2])],
            [(CLOSED_HH, EIGHTHS)],
            [(CLOSED_HH, [p for p in EIGHTHS if p not in (2, 2.5)])],
        ],
    )


STAGE = stage(
    number=1,
    slug="pulse",
    title="Pulse",
    goal="A steady internal clock and a strike that lands where you meant it. "
    "One voice at a time — nothing ever stacks, so a note that is late can only "
    "be your timing.",
    modules=[
        module(
            "the-strike",
            "The strike",
            "one hand, quarter notes",
            [
                lesson(
                    slug="kick-quarters",
                    name="Kick on Every Beat",
                    tier="plain",
                    drums=kick_quarters,
                    bass=QUARTER,
                    summary="One pad, straight quarter notes: kick on all four beats.",
                    description=(
                        "Your first groove: nothing but the kick, once on every "
                        "beat. The bass plays the same four beats underneath, so "
                        "the pulse is never in doubt — all you have to do is land "
                        "on it. Aim for even spacing rather than force; one steady "
                        "bar is worth four rushed ones."
                    ),
                    hints=[
                        "Press Listen first. Play only once you can hum the pulse back.",
                        "One finger, one pad: keep your strong hand's index on the "
                        "kick and don't reposition mid-loop.",
                        'Count "1 2 3 4" out loud and strike on the number, not '
                        "after it — saying it late is playing it late.",
                        "Hit, don't press. The finger drops onto the pad and comes "
                        "off; it does not push it down like a button.",
                        "Watch the note approach the line instead of reacting to "
                        "the sound you just made.",
                        "Orange notes mean drifting time, not weak hits. Hit Listen "
                        "again, re-sync with the pulse, then run it once more.",
                    ],
                ),
                lesson(
                    slug="hats-quarters",
                    name="Hi-Hat on Every Beat",
                    tier="core",
                    drums=hats_quarters,
                    bass=QUARTER,
                    prereq=["kick-quarters"],
                    summary="The same four beats, played by the weak hand on the hi-hat.",
                    description=(
                        "Identical rhythm, other hand. From here on the weak hand "
                        "owns the hi-hats and the strong hand owns the kick and "
                        "snare, and every later lesson assumes it — so this is "
                        "where the weak hand learns to keep time on its own, "
                        "before it has anything else to think about."
                    ),
                    hints=[
                        "Weak hand only. If the strong hand twitches along, sit "
                        "on it.",
                        "The weak hand will feel late for the first few bars. It "
                        "is not weaker at timing, only less rehearsed.",
                        "Same wrist drop as the kick — the hat is quieter because "
                        "of the sample, not because you hit it more softly.",
                        "Run 1.1 and this back to back and listen for the "
                        "difference in evenness. That gap is the thing you are "
                        "closing.",
                    ],
                ),
                lesson(
                    slug="quarters-hand-swap",
                    name="Quarters, Hands Swapping",
                    tier="stretch",
                    drums=quarters_hand_swap,
                    bass=QUARTER,
                    prereq=["hats-quarters"],
                    summary="Quarter notes that change hands at every bar line — "
                    "kick, hat, kick, hat.",
                    description=(
                        "The rhythm never changes; the hand does. A bar of kick, a "
                        "bar of hi-hat, and around again. Nothing is faster than "
                        "1.1 — the difficulty is entirely in the hand-over, which "
                        "is where most people drop a beat or double one."
                    ),
                    hints=[
                        "The hand-over happens on the bar line, and the new hand "
                        "plays beat 1. Get that one note right and the rest of the "
                        "bar follows.",
                        "Lift the finishing hand early rather than pulling it away "
                        "at the last moment — a rushed exit drags the entry with it.",
                        "The incoming hand should already be resting over its pad a "
                        "beat before it plays. Do not travel and strike in the same "
                        "motion.",
                        "An extra note on beat 1 means both hands played it. Count "
                        'the bars out loud — "kick two three four, hat two three '
                        'four" — until the swap is automatic.',
                    ],
                ),
            ],
        ),
        module(
            "two-hands",
            "Two hands",
            "alternation",
            [
                lesson(
                    slug="alternating-quarters",
                    name="Alternating Quarters",
                    tier="plain",
                    drums=alternating_quarters,
                    bass=QUARTER,
                    prereq=["quarters-hand-swap"],
                    summary="Snare, hat, snare, hat — the hands trade, one beat each.",
                    description=(
                        "Both hands in the same bar for the first time, but never "
                        "at the same moment: strong hand on 1 and 3, weak hand on 2 "
                        "and 4. Nothing stacks, so if you hear two pads together "
                        "you played an extra note."
                    ),
                    hints=[
                        "Strong hand takes the snare, weak hand the hi-hat, and "
                        "they never swap. Fixed pads, fixed fingers.",
                        "Let the hands take turns rather than steering each one. "
                        "Think of a single motion passing back and forth.",
                        "The weak hand's beats are the ones that drift. If 2 and 4 "
                        "sound late, they are.",
                        "Say the pads out loud as you play — \"snare, hat, snare, "
                        'hat" — so a swapped hand is audible before it is visible.',
                    ],
                ),
                lesson(
                    slug="alternating-8ths",
                    name="Alternating 8ths",
                    tier="core",
                    drums=alternating_8ths,
                    bass=QUARTER,
                    prereq=["alternating-quarters"],
                    summary="The single stroke roll: snare on the numbers, hat on "
                    'the "and"s.',
                    description=(
                        "The same trade, twice as often. This is the single stroke "
                        "roll — the first rudiment, and the one everything in Stage "
                        "4 is built on. The bass still plays quarter notes, so the "
                        "numbers are always underneath you and only the \"and\"s "
                        "are yours alone."
                    ),
                    hints=[
                        "Two hands sharing 8ths is easier than one hand playing "
                        "them. Let the alternation do the work rather than hurrying.",
                        'Your strong hand always lands on a number, your weak hand '
                        'always on an "and". If that ever inverts, stop at the bar '
                        "line and restart.",
                        "Count \"1 and 2 and 3 and 4 and\" out loud and put the "
                        "snare on the numbers.",
                        "Evenness beats speed: the gap between snare and hat should "
                        "be the same as the gap between hat and snare.",
                        "If the hat notes bunch up against the snare, the weak hand "
                        "is chasing. Lift it earlier, don't push it faster.",
                    ],
                ),
                lesson(
                    slug="alternating-8ths-swap",
                    name="Alternating 8ths, Lead Swapping",
                    tier="stretch",
                    drums=alternating_8ths_swap,
                    bass=SYNCOPATED,
                    prereq=["alternating-8ths"],
                    summary="The same 8ths, but the lead hand flips at every bar "
                    "line.",
                    description=(
                        "Odd bars start on the snare, even bars on the hat. Not one "
                        "note changes — only which hand owns the down-beat — so the "
                        "whole exercise is knowing where you are. The bass stops "
                        "helping here too: it pushes off-beat, and holding your own "
                        "against it is the point."
                    ),
                    hints=[
                        "The swap is on the bar line, so two of the same pad land "
                        "in a row across it. That doubled sound is correct — it is "
                        "how you know the flip happened.",
                        "Keep the alternation running through the swap. Do not stop "
                        "and restart the hands.",
                        "Feel the bar, not the beat. Count bars out loud — \"one "
                        "two three four, two two three four\" — and the flip stops "
                        "needing a decision.",
                        "The bass pushes between your notes on purpose. Follow its "
                        "beats 1 and 3 and ignore the rest.",
                        "Losing the lead halfway through means you flipped mid-bar. "
                        "Reset on the next bar line rather than playing through it.",
                    ],
                ),
            ],
        ),
        module(
            "one-hand-faster",
            "One hand, faster",
            "density",
            [
                lesson(
                    slug="eighths-strong-hand",
                    name="8ths, Strong Hand",
                    tier="plain",
                    drums=eighths_strong_hand,
                    bass=QUARTER,
                    prereq=["alternating-8ths"],
                    summary="Eight 8th notes a bar on the snare, one hand, no help.",
                    description=(
                        "The same eight notes as the alternating lesson, but one "
                        "hand plays all of them. Two hands sharing 8ths is easy; "
                        "one hand keeping them even is not, and this is where the "
                        "hi-hat lines in every groove from Stage 2 onward come from."
                    ),
                    hints=[
                        "Bounce, don't push. The finger falls and rebounds; it does "
                        "not press eight separate times.",
                        "Missing notes usually means the wrist has tensed up. Shake "
                        "the hand out and start again rather than gripping harder.",
                        "The second half of the bar is where evenness goes. Listen "
                        "to beats 3 and 4, not 1 and 2.",
                        "The bass plays the four numbers. Every second note of "
                        "yours should land exactly on one of them.",
                    ],
                ),
                lesson(
                    slug="eighths-weak-hand",
                    name="8ths, Weak Hand",
                    tier="core",
                    drums=eighths_weak_hand,
                    bass=QUARTER,
                    prereq=["eighths-strong-hand"],
                    summary="The same eight notes on the weak hand's hi-hat.",
                    description=(
                        "This is the hi-hat line of a rock groove with everything "
                        "else stripped away, and it lives on the weak hand for the "
                        "rest of the curriculum. Getting it even now means Stage 2 "
                        "is only about the other hand."
                    ),
                    hints=[
                        "Weak hand alone. The strong hand stays off the pads "
                        "entirely.",
                        "Let the hand run like a metronome — it should feel like "
                        "one continuous motion, not eight decisions.",
                        "If it wobbles, it will wobble under a groove too. Fix it "
                        "here, where nothing else is in the way.",
                        "Play it once with your eyes on the highway and once with "
                        "your eyes closed. The second one tells you whether you are "
                        "keeping time or reading it.",
                    ],
                ),
                lesson(
                    slug="eighths-through-rests",
                    name="8ths Through a Rest",
                    tier="stretch",
                    drums=eighths_through_rests,
                    bass=SYNCOPATED,
                    prereq=["eighths-weak-hand"],
                    summary="8th-note hi-hats with beat 3 removed — the grid has to "
                    "survive a hole in it.",
                    description=(
                        "Six notes where there were eight: beat 3 and its \"and\" "
                        "are silent. Nothing is faster and nothing is new, but the "
                        "pattern stops carrying you through the middle of the bar "
                        "and your own clock has to. With the bass pushing off-beat "
                        "as well, there is nothing left to lean on — which is the "
                        "exercise."
                    ),
                    hints=[
                        "Keep the hand moving through the rest. Play the silence in "
                        "the air above the pad rather than stopping.",
                        "Count out loud the whole way through, especially where "
                        'nothing sounds: "3 and" is still two beats of time.',
                        "The note after the hole — the \"and\" of 4 — is the one "
                        "that tells you whether you kept the grid. Listen for it.",
                        "Coming back early means you shortened the rest. Coming "
                        "back late means you waited for a cue that never arrives.",
                        "If it falls apart, run 1.8 once to reset the feel, then "
                        "come straight back.",
                    ],
                ),
            ],
        ),
    ],
    closing=checkpoint(
        slug="checkpoint-1",
        name="Checkpoint — Pulse",
        drums=checkpoint_1,
        bass=OCTAVE,
        summary="One bar each of the stage: quarters, alternating 8ths, one-hand "
        "8ths, and 8ths through a rest.",
        description=(
            "Four bars, four different patterns, no repeats. Practising one "
            "pattern until it is smooth feels productive and holds up badly; "
            "switching between patterns feels worse and holds up far better. This "
            "is where the stage is actually passed — if you can play it clean, "
            "Stage 2 is yours."
        ),
        hints=[
            "Read one bar ahead. The pattern changes at every bar line, so the "
            "note you are playing is never the one you should be looking at.",
            "The hands change job three times: strong, both, weak, weak. Know "
            "which hand starts each bar before you press Play.",
            "Do not slow down for the hard bar. An even loop with one shaky bar "
            "beats four bars of different tempos.",
            "Losing a bar is normal the first few runs. Come back in at the next "
            "bar line rather than chasing what you missed.",
        ],
    ),
)
