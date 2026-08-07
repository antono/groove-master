"""Pattern helpers, so a lesson is a list of positions rather than a bar loop.

Positions are **beat offsets inside a bar**, as floats: `0` is the down-beat,
`1.5` is the "and" of 2, `2.25` is the "e" of 3. Every drum pattern in the
curriculum is one of two shapes:

    voices(bars, (KICK, [0, 2]), (SNARE, [1, 3]))          every bar the same
    per_bar(bars, lambda i: ...)                           bars that differ

`per_bar` is what hand-swaps, feel switches and checkpoints are built from.
"""

from .midi import BEATS_PER_BAR, CLOSED_HH, PPQ, hit

BAR_TICKS = BEATS_PER_BAR * PPQ

# How loud the borrowed hat sits under the student's own playing. Well below the
# 100 a scored note is written at: a reference to lean on, not a voice competing
# with the pads.
GUIDE_VEL = 58

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


def close_on_downbeat(events, bars):
    """Repeat the pattern's own down-beat on the bar line after the last bar.

    A loop that stops after its last note *stops*; it does not *end*. The ear
    is already leaning on the bar line that would have opened bar five, and a
    pattern that withholds it leaves the phrase hanging open — the same reason
    the bass resolves onto that beat (see `bass.resolved`). The two land
    together: the closing hit and the tonic underneath it.

    Whatever sounds on beat 0 sounds again here, stack and all. It is the
    pattern's own down-beat voice, so the closing hit is never a new thing to
    learn — it is the note the student has been playing all the way through,
    once more, to finish on.

    This note **is** scored: landing it is part of finishing the lesson. The
    transport keeps running a beat past it so it can actually be hit — see
    TAIL_BEATS in $lib/midi.ts.
    """
    end = bars * BAR_TICKS
    ons = [(tick, raw[1]) for tick, _order, raw in events if raw[0] == 0x99]
    if not ons:
        return events, end
    # Everything on beat 0 — a stacked down-beat closes as the same stack.
    opening = min(tick for tick, _note in ons)
    closing = sorted({note for tick, note in ons if tick == opening})
    out = list(events)
    for note in closing:
        hit(out, end, note)
    return out, end + PPQ  # a beat of room for the closing hit to ring


def guide_hats(bars):
    """Closed hats on the 8ths — the timekeeper a hatless lesson has to borrow.

    On a real kit the hat is the voice that never stops, and everything else is
    read against it. A lesson whose pattern has no hat of its own leaves the
    student counting in silence between their own hits, which is exactly where
    a beginner's timing drifts. This track supplies that voice: audible, never
    shown, never scored (see GUIDE-HAT RULE in make-lessons.py).

    Eighths rather than quarters because the quarters are the part already
    taken — every hatless lesson in the curriculum plays on the beat, so a
    quarter-note guide would strike at the same instant as the student's own
    note and not be heard at all. The 8ths fill the gaps *and* mark the beat.

    It sits well under the kit: loud enough to lean on, quiet enough that
    nobody mistakes it for a hit of their own that scored.
    """
    events = []
    for bar in range(bars):
        base = bar * BAR_TICKS
        for pos in EIGHTHS:
            hit(events, base + round(pos * PPQ), CLOSED_HH, vel=GUIDE_VEL)
    # Carry the hat through the closing hit — a timekeeper that stops a beat
    # before the pattern ends is not keeping time (see close_on_downbeat).
    hit(events, bars * BAR_TICKS, CLOSED_HH, vel=GUIDE_VEL)
    return events, bars * BAR_TICKS + PPQ


def cycle_bars(bars, patterns):
    """One bar of each pattern in turn — how a checkpoint is built.

    `patterns` are lists of (note, positions), one per bar; they repeat if the
    lesson is longer than the list.
    """
    return per_bar(bars, lambda bar: patterns[bar % len(patterns)])
