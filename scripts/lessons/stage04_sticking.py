"""Stage 4 — Sticking.

Rudiments, then rudiments inside a groove: *which* hand plays a note starts to
matter as much as when.

Only the single paradiddle is written. Its module's other two slots and the
modules either side are `planned()`, so the paradiddle keeps its number while
the rest of the stage is filled in — and so the catalogue is honest about the
fact that it currently sits there without the strokes that lead into it.
"""

from .bass import QUARTER
from .grids import EIGHTHS, sticking
from .midi import CLOSED_HH, SNARE
from .schema import lesson, module, planned, stage


def paradiddle_single(bars=4):
    """R L R R / L R L L in 8th notes — one full paradiddle per bar.

    The lead hand plays the snare and the other the closed hat, so the two
    doubles (RR and LL) are audible as a repeated pad rather than felt only in
    the fingers. Nothing stacks: every 8th note is exactly one hit from one
    hand, which is the point — the sticking is the whole exercise and a third
    voice would only give the student somewhere else to put the mistake.
    """
    return sticking(bars, SNARE, CLOSED_HH, EIGHTHS, "RLRRLRLL")


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
                planned("paradiddle-groove", "Paradiddle Groove", "core"),
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
