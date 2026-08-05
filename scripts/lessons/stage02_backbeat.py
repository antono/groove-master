"""Stage 2 — The Backbeat.

Two and three voices, including the first pads that must fire as one sound.
Fixed finger positions all the way through: no hand travels until the last
lesson, so every difficulty here is coordination rather than geography.
"""

from .bass import OCTAVE, QUARTER
from .grids import (
    BACKBEAT,
    BEATS,
    DOWNBEATS,
    EIGHTHS,
    OFFBEATS,
    cycle_bars,
    per_bar,
    voices,
)
from .midi import CLOSED_HH, KICK, OPEN_HH, SNARE
from .schema import checkpoint, lesson, module, stage

# --- Module 1: trading --------------------------------------------------------


def backbeat_plain(bars=4):
    """Kick on 1 and 3, snare on 2 and 4 — two voices, never together."""
    return voices(bars, (KICK, DOWNBEATS), (SNARE, BACKBEAT))


def kick_snare_8ths(bars=4):
    """Kick on the numbers, snare on the "and"s — the trade at 8th speed."""
    return voices(bars, (KICK, EIGHTHS[0::2]), (SNARE, EIGHTHS[1::2]))


def trading_three_voices(bars=4):
    """Kick, snare, hat rotating through the 8ths. Nothing ever stacks.

    Three voices in a bar with no two of them ever sounding together — a first
    taste of the linear drumming in Stage 9, and the clearest possible proof
    that "three voices" and "three at once" are different problems.
    """
    rotation = [KICK, SNARE, CLOSED_HH]

    def for_bar(bar):
        # The rotation runs on across the bar line: eight 8ths against three
        # voices leaves a remainder of two, so each bar opens on a new voice and
        # the pattern only comes round after three of them.
        start = bar * len(EIGHTHS)
        return [
            (
                note,
                [
                    p
                    for i, p in enumerate(EIGHTHS)
                    if rotation[(start + i) % 3] == note
                ],
            )
            for note in rotation
        ]

    return per_bar(bars, for_bar)


# --- Module 2: stacking -------------------------------------------------------


def kick_hats_unison(bars=4):
    """Hat on all four beats, kick on 1 and 3 — the first stack."""
    return voices(bars, (CLOSED_HH, BEATS), (KICK, DOWNBEATS))


def rock_beat_quarter_hats(bars=4):
    """Hat on all four, kick on 1 and 3, snare on 2 and 4 — a stack every beat."""
    return voices(bars, (CLOSED_HH, BEATS), (KICK, DOWNBEATS), (SNARE, BACKBEAT))


def stack_every_beat(bars=4):
    """Kick and hat on all four beats, snare on 2 and 4 — a triple stack twice a bar."""
    return voices(bars, (CLOSED_HH, BEATS), (KICK, BEATS), (SNARE, BACKBEAT))


# --- Module 3: the rock beat --------------------------------------------------


def rock_beat_8th_hats(bars=4):
    """The basic rock beat: 8th hats, kick on 1 and 3, snare on 2 and 4."""
    return voices(bars, (CLOSED_HH, EIGHTHS), (KICK, DOWNBEATS), (SNARE, BACKBEAT))


def four_on_the_floor(bars=4):
    """Kick on every beat, snare backbeat on 2 and 4, closed hats on 8ths."""
    return voices(bars, (CLOSED_HH, EIGHTHS), (KICK, BEATS), (SNARE, BACKBEAT))


def disco_open_hats(bars=4):
    """Four on the floor with the off-beat hats opened up — four pads.

    The 8th-note hat line splits across two pads, closed on the beats and open
    on the "and"s, so the hat hand has to alternate instead of repeat.
    """
    return voices(
        bars,
        (CLOSED_HH, BEATS),
        (OPEN_HH, OFFBEATS),
        (KICK, BEATS),
        (SNARE, BACKBEAT),
    )


# --- Checkpoint ---------------------------------------------------------------


def checkpoint_2(bars=4):
    """One bar each: the trade, the quarter-hat groove, four on the floor, disco."""
    return cycle_bars(
        bars,
        [
            [(KICK, DOWNBEATS), (SNARE, BACKBEAT)],
            [(CLOSED_HH, BEATS), (KICK, DOWNBEATS), (SNARE, BACKBEAT)],
            [(CLOSED_HH, EIGHTHS), (KICK, BEATS), (SNARE, BACKBEAT)],
            [
                (CLOSED_HH, BEATS),
                (OPEN_HH, OFFBEATS),
                (KICK, BEATS),
                (SNARE, BACKBEAT),
            ],
        ],
    )


STAGE = stage(
    number=2,
    slug="backbeat",
    title="The Backbeat",
    goal="Two and three voices, including the first pads that have to fire as "
    "one sound. Fingers stay where they are — every difficulty here is "
    "coordination, not travel.",
    modules=[
        module(
            "trading",
            "Trading",
            "two voices, never together",
            [
                lesson(
                    slug="backbeat-plain",
                    name="The Backbeat",
                    tier="plain",
                    drums=backbeat_plain,
                    bass=QUARTER,
                    prereq=["alternating-quarters"],
                    summary="Kick on 1 and 3, snare on 2 and 4 — the shape under "
                    "most songs you know.",
                    description=(
                        "Two voices and no hi-hat: the skeleton of nearly every "
                        "rock and pop groove ever recorded. Nothing sounds at the "
                        "same time as anything else, so this is Stage 1's "
                        "alternation with the pads renamed — but 2 and 4 are now "
                        "the loud ones, and that is what makes it a groove instead "
                        "of an exercise."
                    ),
                    hints=[
                        "Both pads on the strong hand: kick under the index, snare "
                        "under the middle. The weak hand rests this lesson.",
                        "Lean on 2 and 4. The backbeat should be the loudest thing "
                        "in the bar — that is where the song is.",
                        "Nothing stacks. If you hear kick and snare together, you "
                        "played an extra note.",
                        'Say "boom bap boom bap" through the bar. If you can say '
                        "it, your hand can find it.",
                    ],
                ),
                lesson(
                    slug="kick-snare-8ths",
                    name="Kick & Snare in 8ths",
                    tier="core",
                    drums=kick_snare_8ths,
                    bass=QUARTER,
                    prereq=["backbeat-plain", "alternating-8ths"],
                    summary="The same trade at 8th speed: kick on the numbers, "
                    'snare on the "and"s.',
                    description=(
                        "Both pads on one hand now, twice as often, with the snare "
                        "landing entirely between the beats. The bass keeps the "
                        "four numbers going, so every kick has something under it "
                        "and every snare has nothing — which is the whole "
                        "difficulty."
                    ),
                    hints=[
                        "Kick and snare are both on the strong hand. Two fingers, "
                        "fixed, alternating.",
                        'The snares are off-beat. Count "1 and 2 and" out loud and '
                        'put the snare on every "and".',
                        "A snare that drifts toward the next kick means you are "
                        "hearing it as a lead-in rather than a note of its own.",
                        "Play the kicks alone for a bar first, then drop the snares "
                        "into the gaps.",
                    ],
                ),
                lesson(
                    slug="trading-three-voices",
                    name="Three Voices, One at a Time",
                    tier="stretch",
                    drums=trading_three_voices,
                    bass=QUARTER,
                    prereq=["kick-snare-8ths"],
                    summary="Kick, snare and hat rotating through the 8ths — three "
                    "voices, never two at once.",
                    description=(
                        "Three pads in a bar and nothing ever stacks: the voices "
                        "take turns, one 8th note each, and the cycle of three "
                        "against eight 8ths means each bar starts on a different "
                        "voice. This is the difference between \"three voices\" and "
                        '"three at once" — and the second one is the next module.'
                    ),
                    hints=[
                        "Three pads, two hands: kick and snare on the strong hand, "
                        "hat on the weak one. The hands are not taking even turns "
                        "and they are not supposed to.",
                        "Three voices across eight 8ths does not divide evenly, so "
                        "the bar never repeats itself. Read ahead rather than "
                        "predicting.",
                        "Each bar begins on a different voice. Do not assume the "
                        "kick starts it.",
                        "One note at a time, always. Any stack is an extra note.",
                        "If it collapses, play the rotation out loud first — "
                        '"kick snare hat, kick snare hat" — with no pads at all.',
                    ],
                ),
            ],
        ),
        module(
            "stacking",
            "Stacking",
            "voices as one sound",
            [
                lesson(
                    slug="kick-hats-unison",
                    name="Kick & Hi-Hat",
                    tier="plain",
                    drums=kick_hats_unison,
                    bass=QUARTER,
                    prereq=["hats-quarters", "kick-quarters"],
                    summary="Two pads at once: hats on all four beats, kick on 1 "
                    "and 3.",
                    description=(
                        "The first time two pads have to sound together. The "
                        "hi-hat keeps every beat while the kick plays only 1 and "
                        "3, so beats 1 and 3 are struck by both hands at once and "
                        "beats 2 and 4 by the hat alone. Getting those pairs to "
                        "land as one sound is the whole exercise."
                    ),
                    hints=[
                        "One pad per hand: hi-hat on your weak hand, kick on your "
                        "strong hand. Never cross over to cover both.",
                        "Beats 1 and 3 are a single motion — both fingers drop "
                        "together. Drill just that pair a dozen times before "
                        "running the loop.",
                        "If the pair sounds like two taps rather than one thud, "
                        "leave the loop and drill the two fingers together until "
                        "it's one sound.",
                        "Let the hat hand run like a metronome and drop the kick "
                        "into it; don't try to steer both hands at once.",
                        'Say "both — hat — both — hat" through the bar so beats 2 '
                        "and 4 never grow an extra kick.",
                    ],
                ),
                lesson(
                    slug="rock-beat-quarter-hats",
                    name="Rock Beat, Quarter Hats",
                    tier="core",
                    drums=rock_beat_quarter_hats,
                    bass=QUARTER,
                    prereq=["kick-hats-unison", "backbeat-plain"],
                    summary="Hat on all four, kick on 1 and 3, snare on 2 and 4 — "
                    "something stacks on every beat.",
                    description=(
                        "The backbeat and the hat line at once, and now there is no "
                        "beat where only one thing sounds: hat plus kick on 1 and "
                        "3, hat plus snare on 2 and 4. Everything is still on the "
                        "numbers — nothing here is fast — so all the work is in "
                        "making two pads land as one, four times a bar."
                    ),
                    hints=[
                        "Three pads: hat on the weak hand, kick and snare on the "
                        "strong hand. Nothing moves for the whole lesson.",
                        "The pattern is two pairs alternating. Drill "
                        "\"hat+kick\" until it's one sound, then \"hat+snare\", "
                        "then join them.",
                        "The hat is the constant. Start it first and let the other "
                        "hand fall in, rather than leading with the kick.",
                        "A flammed pair — two taps where there should be one — is "
                        "the strong hand arriving late. Drop both fingers from the "
                        "same height at the same time.",
                    ],
                ),
                lesson(
                    slug="stack-every-beat",
                    name="Triple Stack",
                    tier="stretch",
                    drums=stack_every_beat,
                    bass=OCTAVE,
                    prereq=["rock-beat-quarter-hats"],
                    summary="Kick and hat on all four beats, snare on 2 and 4 — "
                    "three pads together, twice a bar.",
                    description=(
                        "The kick fills in 2 and 4, so beats 2 and 4 now stack "
                        "three pads: hat, kick and snare, all in one motion. Still "
                        "nothing but quarter notes — the density is vertical, not "
                        "horizontal, and that is a different kind of hard."
                    ),
                    hints=[
                        "Beats 2 and 4 are three fingers dropping together. "
                        "Practise those two beats alone, out of time, until all "
                        "three fire as one.",
                        "Two fingers of the strong hand move together on 2 and 4. "
                        "Keep them at the same height between hits so they arrive "
                        "at the same time.",
                        "1 and 3 are the easy pair from the last lesson. Do not let "
                        "them get quieter to make room for the hard ones.",
                        "If a triple sounds like a roll, you are dropping the "
                        "fingers in sequence. Slow the whole loop until they land "
                        "flat together.",
                    ],
                ),
            ],
        ),
        module(
            "the-rock-beat",
            "The rock beat",
            "the groove",
            [
                lesson(
                    slug="rock-beat-8th-hats",
                    name="Rock Beat, 8th Hats",
                    tier="plain",
                    drums=rock_beat_8th_hats,
                    bass=OCTAVE,
                    prereq=["rock-beat-quarter-hats", "eighths-weak-hand"],
                    summary="The basic rock beat: 8th hats, kick on 1 and 3, snare "
                    "on 2 and 4.",
                    description=(
                        "The groove behind more records than any other. Only one "
                        "thing changed from the quarter-hat version: the hat hand "
                        "now runs in 8ths, twice the speed of everything else. You "
                        "already played that hat line on its own in Stage 1 — this "
                        "is where it gets a groove underneath it."
                    ),
                    hints=[
                        "Three voices, three fingers, fixed positions: hat on the "
                        "weak hand, kick and snare on the strong.",
                        "Keep the hat hand running continuously and land the other "
                        "voices inside it. Do not start it and stop it.",
                        "Every second hat note stacks with a kick or a snare. The "
                        '"and"s are the only notes the hat plays alone.',
                        'Sing it before you play it: "boom-tick, bap-tick, '
                        'boom-tick, bap-tick."',
                        "Missing hats usually means the wrist is tensing up. Shake "
                        "the hand out and let the fingers bounce instead of "
                        "pressing.",
                    ],
                ),
                lesson(
                    slug="four-on-the-floor",
                    name="Four on the Floor",
                    tier="core",
                    drums=four_on_the_floor,
                    bass=OCTAVE,
                    prereq=["rock-beat-8th-hats", "stack-every-beat"],
                    summary="Four-on-the-floor: kick on all four beats, snare on 2 "
                    "and 4, closed hats on every 8th.",
                    description=(
                        "The house and disco engine: kick on every beat, snare "
                        "backbeat on 2 and 4, closed hi-hats through the 8ths. Two "
                        "lessons met here — the triple stack from the last module "
                        "and the 8th-note hat line from this one — and an "
                        "octave-bouncing bass runs underneath."
                    ),
                    hints=[
                        "Three voices, three fingers, fixed positions: hat on one "
                        "hand, kick and snare on the other.",
                        "The hats run in 8ths — twice the speed of the kick. Keep "
                        "that hand moving continuously and land the other voices "
                        "inside it.",
                        "Beats 2 and 4 stack kick + snare + hat. Practise those two "
                        "beats alone until all three fire as one sound.",
                        'Sing it before you play it: "boom-tick, bap-tick, '
                        'boom-tick, bap-tick." If you can say it, your hands can '
                        "find it.",
                        "Missing hats usually means the wrist is tensing up. Shake "
                        "the hand out and let the fingers bounce instead of "
                        "pressing.",
                    ],
                ),
                lesson(
                    slug="disco-open-hats",
                    name="Disco Open Hats",
                    tier="stretch",
                    drums=disco_open_hats,
                    bass=OCTAVE,
                    prereq=["four-on-the-floor"],
                    summary="Four-on-the-floor with the off-beats opened up: closed "
                    'hat on the beats, open hat on every "and".',
                    description=(
                        "The same groove, one pad wider. Kick still lands on every "
                        "beat and the snare still answers on 2 and 4, but the "
                        "8th-note hat line now splits in two: closed hat on the "
                        'numbers, open hat on every "and". The first lesson where a '
                        "hand has to travel — only your part got harder, the "
                        "backing is unchanged."
                    ),
                    hints=[
                        "Four voices now. Give the two hats neighbouring pads on "
                        "your weak hand — index closed, middle open — with snare "
                        "and kick on the strong hand.",
                        'Drill the hat hand alone first: "closed-open-closed-open" '
                        "for a full bar, no kick, no snare. Only add the other hand "
                        "once that alternation runs without looking.",
                        "The open hat is a swing door, not a stab — let it ring "
                        "into the next closed hit instead of clipping it short.",
                        "Every open hat sits alone between two stacks — it is the "
                        "only moment nothing else fires. Use it to breathe and "
                        "reset the hand.",
                        'Say "boom-tss, bap-tss" and keep the "tss" louder than in '
                        "Four on the Floor — if the open hats disappear, you are "
                        "landing on the closed pad twice.",
                        "Losing the alternation halfway through a bar means the hat "
                        "hand is leading with the wrong finger. Stop, reset on the "
                        "next bar line, start the pair from closed.",
                    ],
                ),
            ],
        ),
    ],
    closing=checkpoint(
        slug="checkpoint-2",
        name="Checkpoint — The Backbeat",
        drums=checkpoint_2,
        bass=OCTAVE,
        summary="One bar each: the bare backbeat, the quarter-hat groove, four on "
        "the floor, and disco open hats.",
        description=(
            "Four bars, four grooves, no repeats — from two voices to four, and "
            "from a bar where nothing stacks to a bar where the hat hand travels. "
            "Switching between grooves is harder than any one of them and it is "
            "what makes them stick. Play this clean and the whole stage is yours."
        ),
        hints=[
            "The voice count climbs every bar: two, three, three, four. Know what "
            "is coming before it arrives.",
            "The hat hand has the most to do: silent, quarters, 8ths, then two "
            "pads. Let it lead each change.",
            "Bar 4 is the only one where a hand moves. Have the fingers over both "
            "hat pads by the end of bar 3.",
            "Do not slow down for the last bar. An even loop with one shaky bar "
            "beats four bars of different tempos.",
        ],
    ),
)
