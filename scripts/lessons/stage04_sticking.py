"""Stage 4 — Sticking.

Rudiments, then rudiments inside a groove: *which* hand plays a note starts to
matter as much as when.

Only the single paradiddle is written. Its module's other two slots and the
modules either side are `planned()`, so the paradiddle keeps its number while
the rest of the stage is filled in — and so the catalogue is honest about the
fact that it currently sits there without the strokes that lead into it.
"""

from .bass import QUARTER, RIFF
from .grids import DOWNBEATS, EIGHTHS, sticking, voices
from .midi import CLOSED_HH, KICK, SNARE
from .schema import lesson, module, planned, stage


# One full paradiddle per bar, in 8th notes. Shared by both lessons in this
# module so the groove is provably the same sticking as the plain version — the
# kick is the only thing that changes between them.
PARADIDDLE = "RLRRLRLL"


def paradiddle_single(bars=4):
    """R L R R / L R L L in 8th notes — one full paradiddle per bar.

    The lead hand plays the snare and the other the closed hat, so the two
    doubles (RR and LL) are audible as a repeated pad rather than felt only in
    the fingers. Nothing stacks: every 8th note is exactly one hit from one
    hand, which is the point — the sticking is the whole exercise and a third
    voice would only give the student somewhere else to put the mistake.
    """
    return sticking(bars, SNARE, CLOSED_HH, EIGHTHS, PARADIDDLE)


def paradiddle_groove(bars=4):
    """The same paradiddle, with a kick on 1 and 3 underneath it.

    The hands do not change. Snare on the lead, closed hat on the other, the
    identical R L R R / L R L L — so the one new thing in this lesson is the
    foot, and a paradiddle that falls apart here fell apart because of the
    kick and nothing else. That is the whole step from `plain` to `core`: the
    rudiment stops being an exercise and starts being a groove.

    The kick lands on beats 1 and 3, which is where a groove puts it and also
    the two places it teaches the most. Beat 1 is a lead-hand snare, so the
    strong hand plays both pads at once; beat 3 is an other-hand hat, so the
    kick arrives against the opposite hand. One kick per bar would be a
    decoration — these two are the two different problems.
    """
    lead = [p for p, hand in zip(EIGHTHS, PARADIDDLE) if hand == "R"]
    other = [p for p, hand in zip(EIGHTHS, PARADIDDLE) if hand == "L"]
    return voices(bars, (SNARE, lead), (CLOSED_HH, other), (KICK, DOWNBEATS))


STAGE = stage(
    number=4,
    slug="sticking",
    title="Sticking",
    goal="Rudiments, then rudiments inside a groove. Which hand plays a note "
    "starts to matter as much as when.",
    modules=[
        module(
            "strokes",
            "Strokes",
            "singles and doubles",
            [
                planned("singles-16ths", "Single Strokes in 16ths", "plain"),
                planned("doubles-8ths", "Double Strokes", "core"),
                planned("doubles-16ths", "Double Strokes in 16ths", "stretch"),
            ],
        ),
        module(
            "the-paradiddle",
            "The paradiddle",
            "alternate, then double",
            [
                lesson(
                    slug="paradiddle-single",
                    name="Single Paradiddle",
                    tier="plain",
                    drums=paradiddle_single,
                    bass=QUARTER,
                    prereq=["alternating-8ths-swap"],
                    summary="The first sticking pattern: R L R R, L R L L in 8th "
                    "notes, snare on the lead hand and closed hat on the other.",
                    description=(
                        "Until now each hand owned its own pads and its own beats. "
                        "The paradiddle breaks that: the hands alternate — R L — "
                        "then one of them plays twice in a row — R R — and the "
                        "whole thing flips on the second half of the bar. Snare is "
                        "the lead hand, closed hat the other, so you can hear the "
                        "two doubles as well as feel them. Nothing ever stacks — "
                        "one hit, one hand, every 8th note — and the bass walks in "
                        "plain quarter notes, so the sticking is the only hard "
                        "thing here."
                    ),
                    hints=[
                        'Say it before you play it: "pa-ra-did-dle, pa-ra-did-dle" '
                        "— four syllables per half bar, one 8th note each.",
                        "Two fingers, two pads, and the hands never swap roles: "
                        "snare on your strong hand, closed hat on the weak one. No "
                        "two pads ever fire together, so if you hear a stack you "
                        "played an extra note.",
                        'The doubles are the lesson. Beat 2 and "2-and" are two '
                        'snares in a row; beat 4 and "4-and" are two hats. '
                        "Everything else alternates.",
                        'Drill the two halves separately: a bar of nothing but "R L '
                        'R R", then a bar of nothing but "L R L L". Join them only '
                        "once neither one needs counting.",
                        "The second double lands on the last two 8ths of the bar, "
                        "so every bar starts on the opposite hand to the one that "
                        "just played twice: two hats, then straight back to the "
                        "snare on 1.",
                        "A double that arrives as one flam means the second finger "
                        "is chasing the first. Lift it early and drop it on time "
                        "rather than pushing it faster.",
                        "Extra notes usually mean a triple crept in. Stop at the "
                        "bar line and restart the count instead of playing through "
                        "it.",
                    ],
                ),
                lesson(
                    slug="paradiddle-groove",
                    name="Paradiddle Groove",
                    tier="core",
                    drums=paradiddle_groove,
                    bass=RIFF,
                    prereq=["paradiddle-single"],
                    summary="The same paradiddle, with a kick on 1 and 3 "
                    "underneath — the rudiment becomes a groove.",
                    description=(
                        "Everything your hands do here you already did in 4.4: "
                        "the identical R L R R, L R L L, snare on the strong hand "
                        "and closed hat on the weak one. What is new is the kick, "
                        "on beats 1 and 3, and that is enough to turn a rudiment "
                        "into something you could play behind a song. The two "
                        "kicks are deliberately different problems. On beat 1 the "
                        "strong hand is already playing the snare, so both pads "
                        "fire together off one hand. On beat 3 the strong hand is "
                        "free and the weak one is on the hat, so the kick lands "
                        "against the opposite hand instead. If the sticking "
                        "survives both, it will survive a real groove."
                    ),
                    hints=[
                        "Play 4.4 once first. The hands are identical, so anything "
                        "that falls apart here is the kick — you know exactly what "
                        "changed.",
                        "Beat 1 is a stack: kick and snare together, one hand. Drop "
                        "both fingers as a single movement rather than rolling one "
                        "into the other, or it lands as a flam.",
                        "Beat 3 is the easier of the two and the one people rush — "
                        "the strong hand is free, so it tends to arrive early. Let "
                        "the hat on that beat set the timing and put the kick with "
                        "it.",
                        'Keep saying "pa-ra-did-dle" through it. The kick is not '
                        "part of the word, and the moment you start counting the "
                        "kicks instead, the doubles go.",
                        "The doubles are still the lesson: two snares across beat 2 "
                        'and its "and", two hats across beat 4 and its "and". '
                        "Neither of them has a kick on it, so they should be the "
                        "steadiest thing in the bar.",
                        "If a double turns into a single, you are almost certainly "
                        "putting the missing energy into the kick. Play a bar with "
                        "no kick at all, then add it back one beat at a time.",
                    ],
                ),
                planned("paradiddle-inversions", "The Four Inversions", "stretch"),
            ],
        ),
        module(
            "bigger-diddles",
            "Bigger diddles",
            "longer patterns, same idea",
            [
                planned("paradiddle-double", "Double Paradiddle", "plain"),
                planned("paradiddle-diddle", "Paradiddle-diddle", "core"),
                planned("six-stroke-roll", "Six Stroke Roll", "stretch"),
            ],
        ),
    ],
)
