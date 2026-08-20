"""Backing bass lines — the lesson's scaffold, ordered by how much they help.

    answer      replies on every off-beat, diatonic, one rest    most support
    riff        a hook in the gaps, with rests and a turnaround
    quarter     the root on every beat
    octave      bounces on the 8ths, still rooted on the beat
    pedal       one long root, then a scramble in the second half
    syncopated  pushes between the hits and must be ignored
    dub         leaves the down-beat empty entirely               least support

    shuffle     swings with the student — off this ladder entirely

**In triplet feel the ladder is re-derived, not reused.** Every line above is
written on the straight grid, so under triplets they no longer sort by support:
`octave`, `answer` and `syncopated` all land on the "and", a slot a shuffle does
not have, and they fight the student instead of scaffolding them. That leaves
`quarter` as the only neutral line — it marks the beat and says nothing about
how it is divided — and `shuffle`, which plays the new grid alongside the
student and is therefore the *most* supportive line there is for a feel lesson.
Stage 3 fades from `shuffle` to `quarter` to a straight line, which is the same
fade in the opposite direction.

Support that never fades is not support: a module opens on a line that marks
every beat and a stage ends on one that does not, where holding your own
against the bass is the exercise rather than an obstacle to the first note
anyone plays.

Two things sink a backing line, and they are independent. **Placement:** a bass
note struck at the same instant as a drum is not heard as bass at all, and
every lesson has drums on every beat — so a line on the beats is masked by
construction, which is what `quarter`, `octave` and `syncopated` all are.
**Motion:** a line that repeats one pitch is dull however it is placed.

A walking bass — a note on every beat — is therefore the wrong tool for this
app, however good it sounds elsewhere: there is nowhere for it to be heard.
`riff` is what replaced it.

**Every line ends on the tonic, after the drums have stopped.** Each one leads
bar 4 toward the A without ever landing on it, so a run used to end on a
question. `resolved()` supplies the answer on the down-beat the pattern would
have turned over on — the one moment the bass is heard alone. Route new
builders through it rather than returning their events directly.
"""

from .midi import BEATS_PER_BAR, PPQ, bass_note

BAR_TICKS = BEATS_PER_BAR * PPQ
PROGRAM_CHANGE = (0, -1, bytes([0xC0, 0]))  # ignored by our sampler, kept for players

# Every line in this file is in A minor, so this is the note they all go home to.
TONIC = 33  # A1
RESOLVE_DUR, RESOLVE_VEL = 900, 90


def resolved(events, bars):
    """Land the tonic on the down-beat after the last bar, and end there.

    THE RULE: a bassline always finishes on the root of the key, and it does so
    *after* the drums have stopped — on the down-beat the pattern would have
    turned over on.

    Every line here already ends bar 4 on a leading tone pointing at the A: the
    riff walks up a semitone from G#, the answer falls a fifth from E. Without
    this note that pull is simply left hanging, and a run ends on a question.
    The tonic underneath the silence is what makes it an ending — and because
    the drums have already finished, it is the one moment in the lesson the
    bass is heard completely alone.

    It costs no length. `lengthBeats` rounds up to a whole bar, so a note
    exactly on the bar line lands inside the pattern's existing final bar; the
    scheduler queues it on the same tick that ends the run, and the note is
    already on the audio clock by the time the transport stops.
    """
    bass_note(events, bars * BAR_TICKS, TONIC, dur=RESOLVE_DUR, vel=RESOLVE_VEL)
    return events, bars * BAR_TICKS


def riff_bass(bars=4):
    """A four-bar riff over Am - F - C - G: a hook, a hole, and a turnaround.

    Three things a backing line needs that none of the older ones had.

    **It has to be somewhere the drums are not.** A bass note struck at the
    same instant as a drum is not a bass note — same attack, and the kit wins.
    Every lesson puts drums on the beats, so apart from the root anchoring beat
    1 this line lives entirely on the off-beats and 16ths between them.

    **It has to be a phrase, not a bar played four times.** The hook states
    itself in bar 1, answers in bar 2, opens a hole in bar 3 where nothing at
    all plays across beat 3, and drives home on bar 4 with a 16th-note
    turnaround. Space is what makes the busy parts sound busy.

    **It has to be played, not typed.** The push before beat 2 is a ghost —
    barely there, felt more than heard — and the accents sit on the roots. Flat
    velocity is the single loudest tell that a line came out of a text editor.

    Each bar still ends on a chromatic leading note a semitone from the next
    root, so the loop closes rather than stops: G# pulls up to A and bar 4 runs
    straight back into bar 1.
    """
    events = [PROGRAM_CHANGE]
    ANCHOR, GHOST, MAIN, SOFT, PICKUP = 100, 55, 90, 84, 76
    # (beat offset, note, duration in ticks, velocity)
    figures = [
        [  # bar 1 — Am. States the hook.
            (0.00, 33, 300, ANCHOR),  # A1
            (0.75, 33, 100, GHOST),  # A1  ghost, pushes into beat 2
            (1.50, 40, 220, MAIN),  # E2
            (2.50, 45, 220, MAIN),  # A2
            (3.50, 43, 110, SOFT),  # G2
            (3.75, 42, 110, PICKUP),  # F#2 -> down a semitone into F
        ],
        [  # bar 2 — F. Answers it.
            (0.00, 41, 300, ANCHOR),  # F2
            (0.75, 41, 100, GHOST),  # F2
            (1.50, 36, 220, MAIN),  # C2
            (2.50, 33, 300, MAIN),  # A1
            (3.50, 35, 200, SOFT),  # B1  -> up a semitone into C
        ],
        [  # bar 3 — C. Opens a hole: nothing sounds across beat 3.
            (0.00, 36, 300, ANCHOR),  # C2
            (0.75, 36, 100, GHOST),  # C2
            (1.50, 31, 420, MAIN),  # G1  rings on into the gap
            (3.50, 40, 110, SOFT),  # E2
            (3.75, 42, 110, PICKUP),  # F#2 -> up a semitone into G
        ],
        [  # bar 4 — G. Turnaround, the busiest bar in the loop.
            (0.00, 43, 300, ANCHOR),  # G2
            (0.75, 43, 100, GHOST),  # G2
            (1.50, 38, 220, MAIN),  # D2
            (2.50, 35, 180, MAIN),  # B1
            (3.25, 36, 100, SOFT),  # C2  16th run home
            (3.50, 35, 100, SOFT),  # B1
            (3.75, 32, 110, MAIN),  # G#1 -> up a semitone into A, and round
        ],
    ]
    for bar in range(bars):
        base = bar * BAR_TICKS
        for pos, note, dur, vel in figures[bar % len(figures)]:
            bass_note(events, base + round(pos * PPQ), note, dur=dur, vel=vel)
    return resolved(events, bars)


def answer_bass(bars=4):
    """A call-and-response line for a lesson whose drums own every beat.

    Written for the opening lessons, where the student plays on all four beats
    and there is no room on any of them. **Every note lands on an off-beat** —
    exactly halfway between two of their hits — so the bar reads as a
    conversation: they play, it answers, they play, it answers. That is also
    what makes it audible at all; a note struck with the kick is not heard as
    bass (see the module docstring).

    Strictly diatonic over Am - Am - F - G, and only chord tones. `riff_bass`
    leans on chromatic approach notes to pull one bar into the next, which
    works underneath a full groove and sounds wrong over a bare kick — there is
    nothing else sounding to explain the dissonance, so it just reads as a
    wrong note. Here the pull between bars comes from the melody instead: bar 4
    climbs G - B - D - E and the E drops a fifth onto the A that opens bar 1.

    Bar 2 stops after two notes. A phrase that never rests is a texture rather
    than a line, and the hole is what makes the answer in bars 3 and 4 arrive
    as an answer.
    """
    events = [PROGRAM_CHANGE]
    ROOT, MID, SOFT = 88, 76, 68
    # (off-beat position, note, duration in ticks, velocity)
    figures = [
        [  # bar 1 — Am. States the phrase, arching up.
            (0.5, 33, 400, ROOT),  # A1
            (1.5, 36, 260, MID),  # C2
            (2.5, 40, 400, MID),  # E2
            (3.5, 38, 260, SOFT),  # D2  steps back down into C
        ],
        [  # bar 2 — Am. Answers in two notes, then leaves the bar open.
            (0.5, 36, 300, MID),  # C2
            (1.5, 33, 700, ROOT),  # A1  rings on across beats 3 and 4
        ],
        [  # bar 3 — F. Lifts the phrase onto the new chord.
            (0.5, 29, 400, ROOT),  # F1
            (1.5, 33, 260, MID),  # A1
            (2.5, 36, 400, MID),  # C2
            (3.5, 33, 260, SOFT),  # A1
        ],
        [  # bar 4 — G. Walks up and hands back to the A.
            (0.5, 31, 400, ROOT),  # G1
            (1.5, 35, 260, MID),  # B1
            (2.5, 38, 300, MID),  # D2
            (3.5, 40, 300, SOFT),  # E2  falls a fifth onto bar 1's A
        ],
    ]
    for bar in range(bars):
        base = bar * BAR_TICKS
        for pos, note, dur, vel in figures[bar % len(figures)]:
            bass_note(events, base + round(pos * PPQ), note, dur=dur, vel=vel)
    return resolved(events, bars)


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
    return resolved(events, bars)


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
    return resolved(events, bars)


def shuffle_bass(bars=4):
    """A boogie shuffle over Am - Am - F - E: root on the beat, a moving note late.

    The only line in this file written on the triplet grid. Two notes a beat —
    the root on the beat, then the *last* note of the triplet, two thirds of the
    way across it — which is exactly the rhythm the Feel module is teaching. A
    student learning to swing needs to hear something else swinging: the late
    note in the bass and the late note on their hat land together, and when
    theirs straightens the two come apart audibly.

    Masking is not the concern it is elsewhere. Under a shuffle both of these
    slots have a hat on them and the line is heard through the kit rather than
    around it — but the *rhythm* is what it is here to carry, and a rhythm
    survives being blended in a way a melody does not.

    Harmony is i - i - VI - V rather than the Am - F - C - G the straight lines
    use: a shuffle is a blues before it is anything else, and E resolving onto A
    is the cadence the whole feel leans on. The last swung note of bar 4 is a
    G#, a semitone under the tonic `resolved()` lands on.

    Every note sits inside the rendered bass range (28-60, see
    `static/bass/manifest.json`). A root below it decodes as a 404 and the line
    simply loses notes, silently — which is why `make-lessons.py` now checks.
    """
    events = [PROGRAM_CHANGE]
    ROOT_VEL, LATE_VEL = 95, 70
    ROOT_DUR, LATE_DUR = 280, 140  # both stop short: a shuffle bass is detached
    # (root, the four notes played late in the bar) — the late notes walk.
    figures = [
        (33, [40, 43, 40, 36]),  # Am: A1, then E2 G2 E2 C2
        (33, [40, 43, 40, 36]),  # Am again
        (29, [33, 36, 33, 40]),  # F:  F1, then A1 C2 A1 E2 -> the next root's pitch
        (28, [35, 38, 35, 32]),  # E:  E1, then B1 D2 B1 G#1 -> a semitone under A
    ]
    third = PPQ // 3
    for bar in range(bars):
        base = bar * BAR_TICKS
        root, late = figures[bar % len(figures)]
        for beat in range(BEATS_PER_BAR):
            at = base + beat * PPQ
            bass_note(events, at, root, dur=ROOT_DUR, vel=ROOT_VEL)
            bass_note(events, at + 2 * third, late[beat], dur=LATE_DUR, vel=LATE_VEL)
    return resolved(events, bars)


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
    return resolved(events, bars)


ANSWER = ("lately", answer_bass)
RIFF = ("lately", riff_bass)
QUARTER = ("lately", quarter_bass)
OCTAVE = ("lately", octave_bass)
SYNCOPATED = ("lately", syncopated_bass)
SHUFFLE = ("lately", shuffle_bass)
