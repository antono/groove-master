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
    """Root on every beat over Am - Am - F - G, walking home through bar 4.

    A plain quarter-note pulse: it doubles the beat the student is chasing
    instead of syncopating against it, which is what an early lesson needs.
    Two things keep it from being a metronome with a pitch. The down-beat of
    each bar is leant on and the other three notes sit under it, the way a
    player marks the bar without being asked; and bar 4 walks G - B - D - E up
    the chord — still one note per beat, still nothing off the grid, but the
    last bar audibly heads home instead of stamping the same pitch four times.
    The E falls a fifth onto the A that opens bar 1, the oldest cadence there
    is.
    """
    events = [PROGRAM_CHANGE]
    ROOT_VEL, STEP_VEL = 96, 78
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    walk = [31, 35, 38, 40]  # G1, B1, D2, E2 — chord tones, up and over
    for bar in range(bars):
        base = bar * BAR_TICKS
        if bar % 4 == 3:
            for beat, note in enumerate(walk):
                vel = ROOT_VEL if beat == 0 else 84
                bass_note(events, base + beat * PPQ, note, dur=360, vel=vel)
        else:
            root = roots[bar % len(roots)]
            for beat in range(BEATS_PER_BAR):
                vel = ROOT_VEL if beat == 0 else STEP_VEL
                bass_note(events, base + beat * PPQ, root, dur=360, vel=vel)
    return resolved(events, bars)


def octave_bass(bars=4):
    """Disco/house octave bounce over Am - F - C - G, one chord per bar.

    Root on the down-beats, octave-up on the off-beats, with a chromatic
    approach note on the last 8th leading into the next bar's root. The floor
    notes are leant on and the bounces sit lighter and shorter above them —
    the pump comes from that see-saw, not from the notes alone; played flat it
    is an octave exercise, not disco. The very last off-beat of the loop drops
    the bounce for a fifth, so the run into bar 1 is a little run and not just
    a step.
    """
    events = [PROGRAM_CHANGE]
    FLOOR_VEL, BOUNCE_VEL, PUSH_VEL = 94, 70, 84
    roots = [33, 29, 36, 31]  # A1, F1, C2, G1
    eighth = PPQ // 2
    for bar in range(bars):
        base = bar * BAR_TICKS
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        for i, pos in enumerate(range(0, BAR_TICKS, eighth)):
            if i == 7:
                note, dur, vel = nxt - 1, 160, PUSH_VEL  # chromatic approach
            elif i == 6 and bar % len(roots) == len(roots) - 1:
                note, dur, vel = root + 7, 160, PUSH_VEL  # fifth: the run home
            elif i % 2 == 0:
                note, dur, vel = root, 210, FLOOR_VEL  # down-beat: the floor
            else:
                note, dur, vel = root + 12, 150, BOUNCE_VEL  # off-beat: bounce
            bass_note(events, base + pos, note, dur=dur, vel=vel)
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
    The anchors are leant on and the pushes sit lighter — a push that is as
    loud as the beat it is pushing against stops being a push and starts being
    an argument. The last off-beat of each bar walks a semitone into the next
    root, except at the very end of the loop, where the single push splits
    into a two-note enclosure — B above, G# below — closing on the A like a
    door.
    """
    events = [PROGRAM_CHANGE]
    ANCHOR_VEL, PUSH_VEL = 92, 72
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    sixteenth = PPQ // 4
    for bar in range(bars):
        base = bar * BAR_TICKS
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        bass_note(events, base, root, dur=300, vel=ANCHOR_VEL)  # beat 1
        bass_note(events, base + 3 * PPQ // 2, root + 12, dur=180, vel=PUSH_VEL)
        bass_note(events, base + 2 * PPQ, root, dur=300, vel=ANCHOR_VEL)  # beat 3
        if bar % len(roots) == len(roots) - 1:
            # the enclosure: over, under, home — the loop's own full stop
            bass_note(events, base + 14 * sixteenth, nxt + 2, dur=100, vel=PUSH_VEL)
            bass_note(events, base + 15 * sixteenth, nxt - 1, dur=110, vel=86)
        else:
            bass_note(events, base + 7 * PPQ // 2, nxt - 1, dur=180, vel=80)
    return resolved(events, bars)


def pedal_bass(bars=4):
    """One long root across the first half of the bar, then a scramble home.

    The pedal is the line for a lesson that needs harmonic ground without a
    rhythmic crutch: the root sounds once, on the down-beat, and *holds* —
    beats 2 is never marked at all — then the second half of the bar wakes up
    with the fifth on 3, a ghosted octave pickup, and an approach note into
    the next bar. Half the bar is a drone and half is motion, which is what
    puts it below `octave` on the support ladder: the long note confirms where
    beat 1 was, and after that the student is on their own until beat 3.
    """
    events = [PROGRAM_CHANGE]
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    for bar in range(bars):
        base = bar * BAR_TICKS
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        bass_note(events, base, root, dur=900, vel=95)  # the pedal itself
        bass_note(events, base + 2 * PPQ, root + 7, dur=300, vel=80)  # fifth on 3
        bass_note(events, base + 11 * PPQ // 4, root + 12, dur=110, vel=58)  # ghost
        bass_note(events, base + 7 * PPQ // 2, nxt - 1, dur=200, vel=76)  # approach
    return resolved(events, bars)


def dub_bass(bars=4):
    """A dub line over Am - Am - F - G that never plays the down-beat.

    The least supportive line on the straight grid, and the one that teaches
    the most about owning beat 1: every bar opens with silence where the root
    should be, and the root lands half a beat late — the classic dub drop.
    From there the bar is sparse and behind the beat by temperament: the fifth
    on 3 (the one beat it does mark, reggae's own anchor), a ghosted octave,
    and a soft approach into the next bar's late root. A student who leans on
    this line falls over, which is the point of the lessons it is written for
    — by the time it appears, the down-beat has to be theirs.
    """
    events = [PROGRAM_CHANGE]
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    for bar in range(bars):
        base = bar * BAR_TICKS
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        bass_note(events, base + PPQ // 2, root, dur=450, vel=90)  # the late root
        bass_note(events, base + 2 * PPQ, root + 7, dur=300, vel=80)  # fifth on 3
        bass_note(events, base + 11 * PPQ // 4, root + 12, dur=120, vel=60)  # ghost
        bass_note(events, base + 7 * PPQ // 2, nxt - 1, dur=200, vel=72)  # approach
    return resolved(events, bars)


def pump_bass(bars=4):
    """Straight-8th root drive over Am - Am - F - G — the rock engine.

    A style line, off the support ladder the way `shuffle` is: under a rock
    lesson the 8th-note drive *is* the genre, and the fact that every note
    lands with a hat is not masking but blend — the rhythm is carried through
    the kit, and rhythm survives blending in a way a melody does not. Beats
    leant on, off-beats tucked under them and cut shorter, which is the
    difference between a band and a sequencer. The last two 8ths of the loop
    step B - G# up into the A, so bar 4 audibly turns the corner.
    """
    events = [PROGRAM_CHANGE]
    BEAT_VEL, OFF_VEL = 94, 72
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    eighth = PPQ // 2
    for bar in range(bars):
        base = bar * BAR_TICKS
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        last = bar % len(roots) == len(roots) - 1
        for i in range(8):
            if last and i == 6:
                note = root + 4  # the third: B under a G bar, aimed at the A
            elif i == 7:
                note = nxt - 1  # chromatic approach into the next root
            else:
                note = root
            on_beat = i % 2 == 0
            bass_note(
                events,
                base + i * eighth,
                note,
                dur=210 if on_beat else 150,
                vel=BEAT_VEL if on_beat else OFF_VEL,
            )
    return resolved(events, bars)


def funk_bass(bars=4):
    """A one-chord 16th line on Am7 — the interlock, not the ladder.

    Funk does not change chord; it changes *where you are inside the beat*, so
    this line sits on A minor 7 for its whole length and does all its talking
    rhythmically. Written as a two-bar phrase — statement, then an answer that
    opens a hole across beat 3 and drops to the low E — with a busier fourth
    bar that closes on G#, a semitone under home. Ghosts are well under the
    accents: on a line this syncopated, flat velocity would read as random
    instead of funky. Nothing lands exactly on 2 or 4, so the student's own
    backbeat is always heard alone.
    """
    events = [PROGRAM_CHANGE]
    # Am7 tones: A1 33, C2 36, E2 40, G2 43, A2 45, G1 31, E1 28.
    figures = [
        [  # bar 1 — the statement.
            (0.00, 33, 240, 100),
            (0.75, 33, 100, 58),  # ghost, pushing at beat 2
            (1.25, 36, 140, 80),
            (1.75, 38, 100, 66),  # D2, a passing note into the E
            (2.00, 40, 200, 88),
            (2.75, 43, 110, 70),
            (3.25, 40, 130, 76),
            (3.75, 31, 110, 84),  # G1 pickup into the next A
        ],
        [  # bar 2 — the answer: fewer notes, a hole, and the low drop.
            (0.00, 33, 220, 96),
            (0.50, 45, 100, 64),  # octave pop
            (1.50, 43, 160, 84),
            (1.75, 40, 100, 60),  # ghost
            (2.50, 36, 160, 80),
            (3.50, 28, 200, 86),  # E1: the floor falls out, into bar 3
        ],
        None,  # bar 3 repeats bar 1
        [  # bar 4 — the turnaround, busiest of the four.
            (0.00, 33, 220, 96),
            (0.75, 33, 100, 58),
            (1.50, 36, 140, 80),
            (2.25, 38, 110, 74),
            (2.50, 40, 130, 84),
            (3.25, 43, 110, 80),
            (3.75, 32, 110, 86),  # G#1, a semitone under home
        ],
    ]
    figures[2] = figures[0]
    for bar in range(bars):
        base = bar * BAR_TICKS
        for pos, note, dur, vel in figures[bar % len(figures)]:
            bass_note(events, base + round(pos * PPQ), note, dur=dur, vel=vel)
    return resolved(events, bars)


# Each line is bound to its own instrument, so the curriculum does not sound
# like one bass practising forever. The pairing follows the line's character —
# the conversational lines sit on the real electric basses, the machine lines
# on the synths — and it respects each SoundFont's rendered range: the two
# electric basses are real recordings and stop at A2/A#2 (see
# static/bass/manifest.json), which `make-lessons.py` checks per lesson. A
# stage that wants a different colour can pair any builder with any rendered
# id: `bass=("synth1", riff_bass)` is a legal lesson field.
ANSWER = ("finger", answer_bass)  # call-and-response wants a hand, not an envelope
RIFF = ("finger", riff_bass)  # ghosts and accents read best on the real thing
QUARTER = ("picked", quarter_bass)  # the pick's front edge marks the beat
OCTAVE = ("synth1", octave_bass)  # disco bounce, disco machine
PEDAL = ("synth2", pedal_bass)  # the DX7 holds a drone without decaying away
SYNCOPATED = ("synth2", syncopated_bass)  # the pushes want punch, not warmth
DUB = ("finger", dub_bass)  # deep, round, and behind the beat
SHUFFLE = ("picked", shuffle_bass)  # a boogie is guitar-band music
PUMP = ("picked", pump_bass)  # rock 8ths want the pick's front edge
FUNK = ("synth1", funk_bass)  # the interlock wants punch and a fast attack
