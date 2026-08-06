"""Backing bass lines — the lesson's scaffold, ordered by how much they help.

    walking     a note on every beat, and every note different    most support
    quarter     the root on every beat
    octave      bounces on the 8ths, still rooted on the beat
    riff        a motif with rests in it — space, and something to remember
    pedal       one long root, then a scramble in the second half
    syncopated  pushes between the hits and must be ignored
    dub         leaves the down-beat empty entirely               least support

Support that never fades is not support: a module opens on a line that marks
every beat and a stage ends on one that does not, where holding your own
against the bass is the exercise rather than an obstacle to the first note
anyone plays.

**Support and interest are different axes.** What made the early lines dull was
not that they landed on the beat — it was that they played the same note over
and over. `walking` marks all four beats as reliably as `quarter` does and
never repeats a pitch, so a lesson can have maximum scaffolding and still be
worth hearing four times through.
"""

from .midi import BEATS_PER_BAR, PPQ, bass_note

BAR_TICKS = BEATS_PER_BAR * PPQ
PROGRAM_CHANGE = (0, -1, bytes([0xC0, 0]))  # ignored by our sampler, kept for players


def walking_bass(bars=4):
    """A walking line over Am - F - C - G: four quarter notes, none repeated.

    The same scaffolding as `quarter_bass` — a note on every beat, the root on
    every down-beat — but the line moves instead of hammering one pitch. Each
    bar takes the root, two chord tones, and then a **chromatic leading note on
    beat 4** that resolves a semitone into the next bar's root, so the bar line
    is the strongest moment in the loop rather than the place the ear gives up.

    That last note is what makes the four bars a phrase: G# pulls to A and the
    loop comes round without a seam.
    """
    events = [PROGRAM_CHANGE]
    # (root, then the rest of the bar) — beat 4 leads by a semitone into the
    # next bar's root, which is why the last bar climbs to G# for the loop back.
    figures = [
        [33, 40, 45, 42],  # Am : A1  E2  A2  F#2 -> down a semitone into F
        [41, 36, 33, 35],  # F  : F2  C2  A1  B1  -> up   a semitone into C
        [36, 43, 40, 42],  # C  : C2  G2  E2  F#2 -> up   a semitone into G
        [43, 38, 35, 32],  # G  : G2  D2  B1  G#1 -> up   a semitone into A
    ]
    for bar in range(bars):
        base = bar * BAR_TICKS
        for beat, note in enumerate(figures[bar % len(figures)]):
            # A shade under a full beat: walking lines breathe between notes
            # rather than smearing into each other.
            bass_note(events, base + beat * PPQ, note, dur=400)
    return events, bars * BAR_TICKS


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


WALKING = ("lately", walking_bass)
QUARTER = ("lately", quarter_bass)
OCTAVE = ("lately", octave_bass)
SYNCOPATED = ("lately", syncopated_bass)
