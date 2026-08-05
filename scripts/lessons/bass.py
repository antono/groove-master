"""Backing bass lines — the lesson's scaffold, ordered by how much they help.

    quarter     doubles the pulse the student is chasing        most support
    octave      bounces on the 8ths, still rooted on the beat
    syncopated  pushes between the hits and must be ignored     least support

Support that never fades is not support: a module opens on `quarter` and a stage
ends on `syncopated`, where holding your own against the bass is the exercise
rather than an obstacle to the first note anyone plays.
"""

from .midi import BEATS_PER_BAR, PPQ, bass_note

BAR_TICKS = BEATS_PER_BAR * PPQ
PROGRAM_CHANGE = (0, -1, bytes([0xC0, 0]))  # ignored by our sampler, kept for players


def quarter_bass(bars=4):
    """Root on every beat over Am - Am - F - G, one chord per bar.

    A plain quarter-note pulse: it doubles the beat the student is chasing
    instead of syncopating against it, which is what an early lesson needs.
    """
    events = [PROGRAM_CHANGE]
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    for bar in range(bars):
        base = bar * BAR_TICKS
        root = roots[bar % len(roots)]
        for beat in range(BEATS_PER_BAR):
            bass_note(events, base + beat * PPQ, root, dur=360)
    return events, bars * BAR_TICKS


def octave_bass(bars=4):
    """Disco/house octave bounce over Am - F - C - G, one chord per bar.

    Root on the down-beats, octave-up on the off-beats, with a chromatic
    approach note on the last 8th leading into the next bar's root.
    """
    events = [PROGRAM_CHANGE]
    roots = [33, 29, 36, 31]  # A1, F1, C2, G1
    eighth = PPQ // 2
    for bar in range(bars):
        base = bar * BAR_TICKS
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        for i, pos in enumerate(range(0, BAR_TICKS, eighth)):
            if i == 7:
                note = nxt - 1  # chromatic approach into the next root
            elif i % 2 == 0:
                note = root  # down-beat: root
            else:
                note = root + 12  # off-beat: octave up
            bass_note(events, base + pos, note, dur=180)
    return events, bars * BAR_TICKS


def syncopated_bass(bars=4):
    """Off-beat bass over Am - Am - F - G: "1, 2-and, 3, 4-and".

    Beats 1 and 3 stay anchored so the down-beat is never in doubt, while the
    pushes on the "and" of 2 and 4 keep the line from just doubling the drums.
    The last off-beat walks a semitone into the next bar's root.
    """
    events = [PROGRAM_CHANGE]
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    for bar in range(bars):
        base = bar * BAR_TICKS
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        bass_note(events, base + 0 * PPQ, root, dur=300)  # beat 1: root
        bass_note(events, base + 3 * PPQ // 2, root + 12, dur=200)  # 2-and: octave
        bass_note(events, base + 2 * PPQ, root, dur=300)  # beat 3: root
        bass_note(events, base + 7 * PPQ // 2, nxt - 1, dur=200)  # 4-and: approach
    return events, bars * BAR_TICKS


QUARTER = ("lately", quarter_bass)
OCTAVE = ("lately", octave_bass)
SYNCOPATED = ("lately", syncopated_bass)
