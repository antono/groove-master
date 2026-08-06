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
    """A walking line over Am - F - C - G that walks **in the drums' gaps**.

    A bass note struck at the same instant as a drum is not a bass note, it is
    part of the drum: same attack, and the kit wins. Every lesson's drums land
    on the beats, so a line that also lands on the beats is inaudible as a
    separate voice no matter how good it is — which is what was wrong with the
    quarter-note version of this, and with `quarter_bass` before it.

    So the root anchors beat 1, with the snare, and everything else lives on
    the off-beats: a note sounds in each of the four holes the drums leave.
    Beat 1 keeps the pulse nailed down; the rest is the only voice in the room.

    Pitches still never repeat inside a bar, and the last off-beat is a
    **chromatic leading note** resolving a semitone into the next bar's root,
    so the four bars turn over as a phrase — G# pulls up to A and the loop
    closes without a seam.
    """
    events = [PROGRAM_CHANGE]
    # Beat 1 anchors; 0.5, 1.5, 2.5 and 3.5 sit in the gaps between drum hits.
    positions = [0, 0.5, 1.5, 2.5, 3.5]
    figures = [
        [33, 36, 40, 45, 42],  # Am : A1 C2 E2 A2 F#2 -> down a semitone into F
        [41, 36, 33, 38, 35],  # F  : F2 C2 A1 D2 B1  -> up   a semitone into C
        [36, 40, 43, 48, 42],  # C  : C2 E2 G2 C3 F#2 -> up   a semitone into G
        [43, 38, 35, 31, 32],  # G  : G2 D2 B1 G1 G#1 -> up   a semitone into A
    ]
    for bar in range(bars):
        base = bar * BAR_TICKS
        for pos, note in zip(positions, figures[bar % len(figures)]):
            # The anchor rings under the first half of the bar; the off-beats are
            # short enough to speak between two drum hits and get out of the way.
            dur = 380 if pos == 0 else 210
            bass_note(events, base + round(pos * PPQ), note, dur=dur)
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
