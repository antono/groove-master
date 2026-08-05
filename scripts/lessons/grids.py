"""Pattern helpers, so a lesson is a list of positions rather than a bar loop.

Positions are **beat offsets inside a bar**, as floats: `0` is the down-beat,
`1.5` is the "and" of 2, `2.25` is the "e" of 3. Every drum pattern in the
curriculum is one of two shapes:

    voices(bars, (KICK, [0, 2]), (SNARE, [1, 3]))          every bar the same
    per_bar(bars, lambda i: ...)                           bars that differ

`per_bar` is what hand-swaps, feel switches and checkpoints are built from.
"""

from .midi import BEATS_PER_BAR, PPQ, hit

BAR_TICKS = BEATS_PER_BAR * PPQ

# Common position sets, named so a pattern reads as music rather than arithmetic.
BEATS = [0, 1, 2, 3]  # the numbers
OFFBEATS = [0.5, 1.5, 2.5, 3.5]  # the "and"s
EIGHTHS = [i / 2 for i in range(8)]
SIXTEENTHS = [i / 4 for i in range(16)]
BACKBEAT = [1, 3]  # 2 and 4
DOWNBEATS = [0, 2]  # 1 and 3


def per_bar(bars, voices_for):
    """`voices_for(bar_index)` -> iterable of (note, positions) for that bar."""
    events = []
    for bar in range(bars):
        base = bar * BAR_TICKS
        for note, positions in voices_for(bar):
            for pos in positions:
                hit(events, base + round(pos * PPQ), note)
    return events, bars * BAR_TICKS


def voices(bars, *lines):
    """Every bar identical. `lines` are (note, positions) pairs."""
    return per_bar(bars, lambda _bar: lines)


def alternating(bars, lead, other, positions, swap_each_bar=False):
    """Hand-to-hand singles across `positions`, `lead` first.

    One note per position and never a stack — the sticking *is* the exercise, so
    a second voice would only give the student somewhere else to put a mistake.
    """

    def for_bar(bar):
        a, b = (other, lead) if swap_each_bar and bar % 2 else (lead, other)
        return [
            (a, positions[0::2]),
            (b, positions[1::2]),
        ]

    return per_bar(bars, for_bar)


def sticking(bars, lead, other, positions, hands):
    """One note per position, the hand chosen by `hands` — "RLRR" style.

    `hands` is a string of R/L (or a list of bools, True = lead), one entry per
    position. This is how the rudiments are written.
    """
    if isinstance(hands, str):
        hands = [c.upper() == "R" for c in hands]
    if len(hands) != len(positions):
        raise ValueError(f"{len(hands)} hands for {len(positions)} positions")
    return voices(
        bars,
        (lead, [p for p, is_lead in zip(positions, hands) if is_lead]),
        (other, [p for p, is_lead in zip(positions, hands) if not is_lead]),
    )


def cycle_bars(bars, patterns):
    """One bar of each pattern in turn — how a checkpoint is built.

    `patterns` are lists of (note, positions), one per bar; they repeat if the
    lesson is longer than the list.
    """
    return per_bar(bars, lambda bar: patterns[bar % len(patterns)])
