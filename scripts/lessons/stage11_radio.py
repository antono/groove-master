"""Stage 11 — Styles: The Radio.

The backbeat family: rock, funk and hip-hop — three genres that share one
skeleton (snare on 2 and 4, hat keeping 8ths) and differ almost entirely in
**where the kick goes and how fast the air moves**. That is why they make one
stage: every lesson here is the Stage 2 rock beat with its kick rewritten, so
what the student is actually learning is kick placement as vocabulary, one
genre at a time.

Each style brings its own bass. Rock gets the 8th-note pump on the picked
electric, funk gets the 16th interlock on the synth, hip-hop gets the riff and
the long dark pedal — the backing is doing half the teaching, because a style
is a rhythm section, not a drum part.

Tempos are the styles' own. These are the first lessons whose manifest BPM is
chosen by genre rather than by the ladder — a funk groove at 60 is not slower
funk, it is not funk.
"""

from .bass import FUNK, PEDAL, PUMP, RIFF
from .grids import BACKBEAT, EIGHTHS, SIXTEENTHS, cycle_bars, per_bar, voices
from .midi import CLOSED_HH, CRASH, KICK, OPEN_HH, RIDE, SNARE
from .schema import checkpoint, lesson, module, stage

# --- Module 1: rock -------------------------------------------------------------


def rock_drive(bars=4):
    """The driving rock beat: kick on 1, 3 and the "and" of 3."""
    return voices(
        bars, (CLOSED_HH, EIGHTHS), (KICK, [0, 2, 2.5]), (SNARE, BACKBEAT)
    )


def rock_anthem(bars=4):
    """The arena groove: ride 8ths, kick on 1, the "and" of 2, and 3, a crash
    every two bars.

    The kick's second note comes *before* the snare on 3 instead of after it —
    the other classic rock placement, pulling into the back half of the bar
    where `rock_drive` pushes out of it.
    """

    def for_bar(bar):
        line = [(RIDE, EIGHTHS), (KICK, [0, 1.5, 2]), (SNARE, BACKBEAT)]
        return [(CRASH, [0])] + line if bar % 2 == 0 else line

    return per_bar(bars, for_bar)


def rock_sixteens(bars=4):
    """Sixteenth kicks under 8th hats: 1, the "a" of 1, 3, its "and", and the
    "a" of 4 picking up the next bar."""
    return voices(
        bars,
        (CLOSED_HH, EIGHTHS),
        (KICK, [0, 0.75, 2, 2.5, 3.75]),
        (SNARE, BACKBEAT),
    )


# --- Module 2: funk -------------------------------------------------------------

# The stage's funk kick: on the one, the "a" of 1 answering it, and the "and"
# of 3 driving at the last snare. Shared by all three funk lessons — the module
# varies the hat and the snare around it, never the foot.
FUNK_KICK = [0, 0.75, 2.5]


def funk_one(bars=4):
    """On the One: the funk kick under straight 8th hats and a backbeat."""
    return voices(bars, (CLOSED_HH, EIGHTHS), (KICK, FUNK_KICK), (SNARE, BACKBEAT))


def funk_open_hat(bars=4):
    """The same groove with the hat barking open on the "and" of 2.

    Mid-bar this time, not at the bar line: the open hat answers the kick's
    "a" of 1 and closes again on beat 3. One 8th of open sound in the middle
    of a closed line — the single most recognisable hi-hat move in funk.
    """
    return voices(
        bars,
        (CLOSED_HH, [p for p in EIGHTHS if p != 1.5]),
        (OPEN_HH, [1.5]),
        (KICK, FUNK_KICK),
        (SNARE, BACKBEAT),
    )


def funk_displaced(bars=4):
    """The backbeat grows a third snare on the "a" of 4 — the pickup that
    drags the bar around.

    Not a fill: a placed note, every bar, one 16th before the bar line. It is
    what makes a funk bar lean forward, and it is the first snare in the
    curriculum that does not land on a number.
    """
    return voices(
        bars,
        (CLOSED_HH, EIGHTHS),
        (KICK, FUNK_KICK),
        (SNARE, [1, 3, 3.75]),
    )


# --- Module 3: hip-hop ------------------------------------------------------------


def boom_bap(bars=4):
    """Boom bap: kick on 1, tucked on the "a" of 2, driving on the "and" of 3."""
    return voices(
        bars, (CLOSED_HH, EIGHTHS), (KICK, [0, 1.75, 2.5]), (SNARE, BACKBEAT)
    )


def head_nod(bars=4):
    """The stumble: kick doubled on the "and" of 1, then the "e" of 3.

    Two kicks in a row at the top of the bar, then a landing just *after*
    beat 3's snare has everyone leaning — the lazy, behind-the-beat shape that
    a head nods to.
    """
    return voices(
        bars, (CLOSED_HH, EIGHTHS), (KICK, [0, 0.5, 2.25]), (SNARE, BACKBEAT)
    )


def trap_half_time(bars=4):
    """Half-time with 16th hats: snare on 3 only, kick on 1 and the "a" of 2.

    The modern shape: the hat grid is twice as fine as anything else in the
    stage while the snare halves, so the bar feels enormous and busy at once.
    The hats are split between the hands exactly as Subdivision taught them.
    """
    return voices(
        bars, (CLOSED_HH, SIXTEENTHS), (KICK, [0, 1.75]), (SNARE, [2])
    )


# --- Checkpoint --------------------------------------------------------------------


def checkpoint_11(bars=4):
    """One bar each: the rock drive, the funk one, boom bap, and half-time."""
    return cycle_bars(
        bars,
        [
            [(CLOSED_HH, EIGHTHS), (KICK, [0, 2, 2.5]), (SNARE, BACKBEAT)],
            [(CLOSED_HH, EIGHTHS), (KICK, FUNK_KICK), (SNARE, BACKBEAT)],
            [(CLOSED_HH, EIGHTHS), (KICK, [0, 1.75, 2.5]), (SNARE, BACKBEAT)],
            [(CLOSED_HH, SIXTEENTHS), (KICK, [0, 1.75]), (SNARE, [2])],
        ],
    )


STAGE = stage(
    number=11,
    slug="radio",
    title="Styles: The Radio",
    goal="Rock, funk and hip-hop — one skeleton, three vocabularies. The snare "
    "stays on 2 and 4 while the kick learns to speak each genre, at each "
    "genre's own tempo.",
    modules=[
        module(
            "rock",
            "Rock",
            "the kick that drives",
            [
                lesson(
                    slug="rock-drive",
                    name="Driving Rock",
                    tier="plain",
                    drums=rock_drive,
                    bass=PUMP,
                    prereq=["rock-beat-8th-hats", "kick-snare-8ths"],
                    bpm=92,
                    summary='The rock beat with one kick added on the "and" of '
                    "3 — the engine under fifty years of guitar music.",
                    description=(
                        "One note turns the schoolroom rock beat into a song: a "
                        "kick on the \"and\" of 3, driving out of the second "
                        "snare toward the bar line. The bass pumps straight "
                        "8ths under you — the first time the backing plays a "
                        "genre rather than a scaffold — and the two of you are "
                        "the rhythm section, which is what this whole stage is "
                        "about."
                    ),
                    hints=[
                        'The new kick is on the "and" of 3, right after the '
                        "snare. Boom — bap — boom-boom — bap.",
                        "It lands with a hat, like every other kick here. If it "
                        "sounds alone, it slid to a 16th slot.",
                        "Lock your kick to the bass's 8ths: every kick you play "
                        "has a bass note under it. When they flam, you moved.",
                        "Keep the backbeat the loudest thing in the bar. The "
                        "extra kick is drive, not an accent.",
                    ],
                ),
                lesson(
                    slug="rock-anthem",
                    name="The Anthem",
                    tier="core",
                    drums=rock_anthem,
                    bass=PUMP,
                    prereq=["rock-drive", "rock-beat-ride"],
                    bpm=88,
                    summary="Ride 8ths, a crash every two bars, and the kick "
                    'pulling on the "and" of 2.',
                    description=(
                        "The chorus sound: time on the ride, a crash marking "
                        "every second bar, and the kick's second note moved to "
                        "the \"and\" of 2 — before the mid-bar snare instead of "
                        "after it, so the groove pulls into the back half of "
                        "the bar where Driving Rock pushed out of it. Same "
                        "three voices, opposite lean. Hearing that difference "
                        "is the lesson."
                    ),
                    hints=[
                        'The kick pattern is 1, "and of 2", 3. Say "boom — '
                        'and-boom-boom" against the backbeat before you play it.',
                        "The crash replaces nothing — it stacks on the odd "
                        "bars' down-beat over the ride line's first note.",
                        "Ride rings are part of the sound. Do not shorten the "
                        "strokes to tidy it.",
                        "Play Driving Rock, then this, back to back. Push, then "
                        "pull. If they feel the same, the kick is drifting to "
                        "its old slot.",
                    ],
                ),
                lesson(
                    slug="rock-sixteens",
                    name="Sixteenth Drive",
                    tier="stretch",
                    drums=rock_sixteens,
                    bass=PUMP,
                    prereq=["rock-anthem", "kick-16th-grid"],
                    bpm=84,
                    summary='Five kicks a bar, two of them off the 8th grid: the '
                    '"a" of 1 and the "a" of 4.',
                    description=(
                        "The kick learns 16ths while everything above it stays "
                        "in 8ths. The \"a\" of 1 doubles the opening — boom-ba "
                        "— and the \"a\" of 4 is a pickup that belongs to the "
                        "*next* bar, thrown across the line the way Subdivision "
                        "taught. Five kicks, none of them with a snare, both "
                        "off-grid notes sounding completely alone between "
                        "hats."
                    ),
                    hints=[
                        'Count 16ths all bar: the kicks are "1, a, 3, and, a-'
                        'of-4". The hats never leave the 8ths.',
                        'The "a" of 1 is tight behind beat 1 — a double, not '
                        "an echo. If there is daylight between them, it is late.",
                        'The "a" of 4 belongs to the next bar. Lean it forward '
                        "into the down-beat; landing it lazily makes it an "
                        "extra note instead of a pickup.",
                        "Nothing in the hands changed from the plain rock beat. "
                        "If the hats stumble, they are watching the foot.",
                    ],
                ),
            ],
        ),
        module(
            "funk",
            "Funk",
            "the one, and everything after it",
            [
                lesson(
                    slug="funk-one",
                    name="On the One",
                    tier="plain",
                    drums=funk_one,
                    bass=FUNK,
                    prereq=["kick-16th-grid", "rock-beat-8th-hats"],
                    bpm=92,
                    summary='The funk kick: on the one, answered on the "a" of '
                    '1, driving on the "and" of 3.',
                    description=(
                        "Funk puts everything on the one and then spends the "
                        "rest of the bar answering it. The kick states beat 1, "
                        "doubles itself a 16th and a half later, and drives at "
                        "the second snare — while the bass plays a proper 16th "
                        "funk line that interlocks with you instead of "
                        "following you. Your hits and its notes take turns "
                        "almost everywhere; when the pocket is right you can "
                        "hear the two parts breathe."
                    ),
                    hints=[
                        'The kick answer is on the "a" of 1 — a 16th slot, '
                        "later than the \"and\". If it lands with a hat, it "
                        "straightened.",
                        "Beat 1 is sacred in funk. Whatever else wobbles, the "
                        "one lands — that is the genre in a sentence.",
                        "The bass is busier than you are. Do not chase it; hold "
                        "the backbeat still and let it move around you.",
                        "Play the kick pattern alone against the bass line "
                        "before adding hats and snare. The interlock is the "
                        "lesson.",
                    ],
                ),
                lesson(
                    slug="funk-open-hat",
                    name="The Bark",
                    tier="core",
                    drums=funk_open_hat,
                    bass=FUNK,
                    prereq=["funk-one", "open-hat-lead-in"],
                    bpm=92,
                    summary='The hat opens for one 8th on the "and" of 2 — '
                    "funk's most recognisable move.",
                    description=(
                        "One note of the hat line opens, mid-bar: the \"and\" "
                        "of 2, barking between the first snare and beat 3, "
                        "closed again by the next note. The open-hat moves you "
                        "know live at the bar line and hand phrases over; this "
                        "one lives in the middle of the bar and *is* the "
                        "phrase. One finger swaps pads for one 8th and comes "
                        "straight home."
                    ),
                    hints=[
                        'Index on closed, middle on open, and the move is "and '
                        'of 2" only. Everything else in the hat line is home.',
                        "Let the bark ring into beat 3 and let beat 3's closed "
                        "hat cut it — that choke is the sound, not something to "
                        "avoid.",
                        "The kick under the bark does not change. If the foot "
                        "hiccups when the hat opens, the two hands are wired "
                        "together somewhere they should not be.",
                        "Too many barks means the finger is defaulting to the "
                        "open pad. Seven closed, one open, every bar.",
                    ],
                ),
                lesson(
                    slug="funk-displaced",
                    name="The Pickup Snare",
                    tier="stretch",
                    drums=funk_displaced,
                    bass=FUNK,
                    prereq=["funk-open-hat"],
                    bpm=88,
                    summary='A third snare on the "a" of 4 — the pickup that '
                    "leans every bar into the next.",
                    description=(
                        "The backbeat grows a tail: one snare on the \"a\" of "
                        "4, a 16th before the bar line, every bar. It is not a "
                        "fill — it is a placed note that makes the bar lean "
                        "forward, and it is the first snare in the curriculum "
                        "that does not land on a number. Between it and the "
                        "bass's own pickup, the end of every bar is now a "
                        "conversation you are part of rather than a line you "
                        "wait through."
                    ),
                    hints=[
                        'The pickup is on the "a" of 4 — after the last hat, '
                        "before the down-beat, alone. Nothing sounds with it.",
                        "It is quieter in spirit than the backbeat: a lean, not "
                        "a hit. Placed right it pulls the next bar in.",
                        'If it lands on the "and" of 4 it collides with the '
                        "hat and turns into a march. Later than the \"and\", "
                        "earlier than the one.",
                        "The down-beat after it still belongs to the kick. "
                        "Snare-then-kick across the bar line, two sounds, in "
                        "order, every time.",
                    ],
                ),
            ],
        ),
        module(
            "hip-hop",
            "Hip-hop",
            "the lazy pocket",
            [
                lesson(
                    slug="boom-bap",
                    name="Boom Bap",
                    tier="plain",
                    drums=boom_bap,
                    bass=RIFF,
                    prereq=["kick-16th-grid"],
                    bpm=90,
                    summary='Kick on 1, tucked behind the snare on the "a" of '
                    '2, driving on the "and" of 3.',
                    description=(
                        "The sound of a sampled break under a rapper: boom on "
                        "the one, bap on the backbeat, and the kick's middle "
                        "note *tucked* — on the \"a\" of 2, right behind the "
                        "first snare, where it thickens the bap instead of "
                        "answering it. The riff bass loops underneath like the "
                        "sample it is standing in for. Head down, tempo "
                        "modest, nothing showy: the pocket is the whole "
                        "genre."
                    ),
                    hints=[
                        'The tucked kick is a 16th after the first snare — '
                        '"bap-boom", almost one sound. Daylight between them '
                        "is too much.",
                        "Do not rush the tuck into the snare. It follows the "
                        "bap; it never warns of it.",
                        "The groove sits behind its own hats by feel. Keep the "
                        "hat line dead straight and let the kick and snare be "
                        "heavy on it.",
                        "The bass is a four-bar loop with a hole in bar 3 — "
                        "know it the way you would know the sample.",
                    ],
                ),
                lesson(
                    slug="head-nod",
                    name="The Head Nod",
                    tier="core",
                    drums=head_nod,
                    bass=RIFF,
                    prereq=["boom-bap"],
                    bpm=86,
                    summary='Kick doubled on the "and" of 1, landing again just '
                    'after beat 3 — the stumble that nods.',
                    description=(
                        "Two kicks at the top — boom-boom — then nothing from "
                        "the foot until just *after* the second snare's beat: "
                        "the \"e\" of 3, a 16th late, the stumble that makes a "
                        "head nod. The \"e\" is the same slot you learned in "
                        "Subdivision's kick grid, and it is doing here exactly "
                        "what it did there: arriving after the beat instead of "
                        "before it, and sounding alone."
                    ),
                    hints=[
                        'The opening is a pair: 1 and its "and", both kick. '
                        "Even, deliberate, no flam.",
                        'The "e" of 3 lands a 16th after beat 3\'s hat. It is '
                        "a landing, not a push — let the beat happen, then "
                        "place it.",
                        "Beat 4 has nothing but the hat. The foot wants to fill "
                        "it; the genre says no.",
                        "If the groove feels stiff, the \"e\" has crept onto "
                        "beat 3 itself. Play a bar of hats and count "
                        '"3-e" out loud to re-seat it.',
                    ],
                ),
                lesson(
                    slug="trap-half-time",
                    name="Half-Time Hats",
                    tier="stretch",
                    drums=trap_half_time,
                    bass=PEDAL,
                    prereq=["head-nod", "rock-16th-hats", "half-notes"],
                    bpm=72,
                    summary="Sixteenth hats over a snare on 3 alone — the modern "
                    "half-time shape.",
                    description=(
                        "The hat grid doubles while the snare halves: sixteen "
                        "hats a bar, split between the hands, over one snare on "
                        "beat 3 and a kick on 1 and the \"a\" of 2. The bar "
                        "feels enormous and busy at the same time — that "
                        "contradiction is the modern half-time sound, and "
                        "holding both halves of it at once is the stretch. The "
                        "bass holds long dark roots and leaves all the motion "
                        "to you."
                    ),
                    hints=[
                        "Both hands on the hat, strictly alternating, exactly "
                        "as 16ths, Split Hands taught. The snare on 3 is the "
                        "lead hand borrowing one note.",
                        "One snare a bar. The empty beat 4 will beg for a "
                        "second one — half-time lives or dies on refusing it.",
                        'The kick\'s second note is the "a" of 2, tucked '
                        "between hats. If it lands with one, it straightened "
                        'to the "and".',
                        "Keep the hats even and quiet-minded; the groove is "
                        "heavy *under* them, not in them.",
                    ],
                ),
            ],
        ),
    ],
    closing=checkpoint(
        slug="checkpoint-11",
        name="Checkpoint — The Radio",
        drums=checkpoint_11,
        bass=FUNK,
        bpm=88,
        summary="One bar each: driving rock, the funk one, boom bap, and "
        "half-time hats.",
        description=(
            "Four genres in four bars, sharing a snare and almost nothing "
            "else. The kick pattern changes at every bar line and the hat grid "
            "doubles for the last bar — switching vocabularies mid-phrase is "
            "harder than speaking any one of them, and it is what proves the "
            "kick placements are yours rather than one habit wearing four "
            "names."
        ),
        hints=[
            "Name the bars before you play: drive, funk, boom bap, half-time.",
            "The snare is on 2 and 4 for three bars and on 3 alone for the "
            "last. That switch is where the loop usually dies.",
            "Bar 4 doubles the hat grid. Both hands in, exactly as 16ths were "
            "drilled — do not try to take it one-handed at this tempo.",
            "The funk bass runs underneath all four bars. In bar 1 you drive "
            "against it, in bar 2 you interlock with it — hear the "
            "difference.",
        ],
    ),
)
