"""Stage 12 — Styles: The Dancefloor.

Three traditions built for dancing rather than listening: house, the breakbeat
family, and reggae. Where The Radio varied the kick under one skeleton, this
stage varies the skeleton itself — house removes the closed hat from the beat
entirely, breakbeat moves the *snare*, and reggae empties beat 1 and drops
everything on 3.

Reggae is the quiet capstone of the whole curriculum's oldest thread. Space
taught silence, the push taught an empty down-beat, and the one drop is a
groove where **nothing at all happens on beat 1, every bar, on purpose** — over
a dub bass that skips the down-beat too. If the student truly owns their clock,
this is where it shows.

Tempos are the genres' own, and the stretch of the breaks module is honest
about drum & bass: 160 BPM, the same notes as its plain sibling, and the tempo
*is* the lesson.
"""

from .bass import DUB, FUNK, OCTAVE, PEDAL
from .grids import BACKBEAT, BEATS, EIGHTHS, OFFBEATS, cycle_bars, per_bar, voices
from .midi import CLOSED_HH, KICK, OPEN_HH, SNARE
from .schema import checkpoint, lesson, module, stage

# --- Module 1: house --------------------------------------------------------------


def house_pump(bars=4):
    """The house engine: kick on every beat, open hat on every "and", clap on
    2 and 4 — and no closed hat anywhere."""
    return voices(
        bars, (KICK, BEATS), (OPEN_HH, OFFBEATS), (SNARE, BACKBEAT)
    )


def house_skip(bars=4):
    """The pump with a garage skip: closed hats on the "a" of 2 and the "a"
    of 4, tucked between the open hats and the kicks."""
    return voices(
        bars,
        (KICK, BEATS),
        (OPEN_HH, OFFBEATS),
        (CLOSED_HH, [1.75, 3.75]),
        (SNARE, BACKBEAT),
    )


def house_drop(bars=4):
    """Three bars of pump, then the kick and clap vanish for the drop.

    Bar 4 is open hats alone until beat 4 hands it back with four snare 16ths
    — the DJ pulling the floor out and the build snapping it back in. The
    off-beat hats keep running through the drop, which means the bar's only
    timekeeper never plays a beat: holding the grid from its off-beats alone
    is the stretch.
    """
    pump = [(KICK, BEATS), (OPEN_HH, OFFBEATS), (SNARE, BACKBEAT)]
    drop = [(OPEN_HH, OFFBEATS), (SNARE, [3, 3.25, 3.5, 3.75])]
    return per_bar(bars, lambda bar: drop if bar % 4 == 3 else pump)


# --- Module 2: breaks ---------------------------------------------------------------


def the_breakbeat(bars=4):
    """A two-bar break: the second bar answers with a shifted kick and a
    snare pickup.

    Bar 1 is the b-boy skeleton — kick on 1, snare 2 and 4, kick driving on
    the "and" of 3. Bar 2 keeps the snares and moves the kick to the "e" of 3,
    then adds a snare pickup on the "a" of 4. Two bars, looped: the shape
    every breakbeat record is chopped from.
    """
    bar_a = [(CLOSED_HH, EIGHTHS), (KICK, [0, 2.5]), (SNARE, BACKBEAT)]
    bar_b = [(CLOSED_HH, EIGHTHS), (KICK, [0, 2.25]), (SNARE, [1, 3, 3.75])]
    return per_bar(bars, lambda bar: bar_a if bar % 2 == 0 else bar_b)


def break_displaced(bars=4):
    """The snare leaves the backbeat: 2 stays, 4 moves to the "a" of 3.

    Displacement proper — the note everyone can feel coming arrives a 16th
    and a half early, and the empty beat 4 it leaves behind is the funkiest
    thing in the bar. The kick tucks on the "a" of 2 to answer it.
    """
    bar_a = [(CLOSED_HH, EIGHTHS), (KICK, [0, 1.75]), (SNARE, [1, 2.75])]
    bar_b = [(CLOSED_HH, EIGHTHS), (KICK, [0, 2.25]), (SNARE, [1, 2.75, 3.5])]
    return per_bar(bars, lambda bar: bar_a if bar % 2 == 0 else bar_b)


def two_step(bars=4):
    """Drum & bass's two-step: kick on 1 and the "and" of 3, snares on 2 and
    4 — at 160."""
    return voices(bars, (CLOSED_HH, EIGHTHS), (KICK, [0, 2.5]), (SNARE, BACKBEAT))


# --- Module 3: reggae ----------------------------------------------------------------


def one_drop(bars=4):
    """The one drop: kick and snare together on 3, and beat 1 completely empty."""
    return voices(bars, (CLOSED_HH, EIGHTHS), (KICK, [2]), (SNARE, [2]))


def skank(bars=4):
    """The one drop with the hat moved to the off-beats — the skank.

    Now *nothing* in the bar lands on a number except the drop itself: the
    hats play only the "and"s, the kick and snare only beat 3. Beat 1 is
    marked by nobody — not the drums, not the dub bass — and keeping the bar
    the right way round is entirely the player's own clock.
    """
    return voices(bars, (CLOSED_HH, OFFBEATS), (KICK, [2]), (SNARE, [2]))


def steppers(bars=4):
    """Steppers: the kick returns to all four beats under the skank.

    Reggae's other engine — four-on-the-floor under off-beat hats, the drop
    still marked by the snare on 3. After two lessons of empty down-beats the
    floor coming back feels like a gift; keeping the hats off the beat while
    the foot plays every one of them is what earns it.
    """
    return voices(bars, (CLOSED_HH, OFFBEATS), (KICK, BEATS), (SNARE, [2]))


# --- Checkpoint ------------------------------------------------------------------------


def checkpoint_12(bars=4):
    """One bar each: the pump, the break, the two-step shape, the one drop."""
    return cycle_bars(
        bars,
        [
            [(KICK, BEATS), (OPEN_HH, OFFBEATS), (SNARE, BACKBEAT)],
            [(CLOSED_HH, EIGHTHS), (KICK, [0, 2.25]), (SNARE, [1, 3, 3.75])],
            [(CLOSED_HH, EIGHTHS), (KICK, [0, 2.5]), (SNARE, BACKBEAT)],
            [(CLOSED_HH, EIGHTHS), (KICK, [2]), (SNARE, [2])],
        ],
    )


STAGE = stage(
    number=12,
    slug="dancefloor",
    title="Styles: The Dancefloor",
    goal="House, breaks and reggae — three skeletons, not one. The hat leaves "
    "the beat, the snare leaves the backbeat, and beat 1 learns to be "
    "empty on purpose.",
    modules=[
        module(
            "house",
            "House",
            "the pump",
            [
                lesson(
                    slug="house-pump",
                    name="The House Pump",
                    tier="plain",
                    drums=house_pump,
                    bass=OCTAVE,
                    prereq=["disco-open-hats", "four-on-the-floor"],
                    bpm=118,
                    summary="Kick on every beat, open hat on every \"and\", "
                    "clap on 2 and 4 — and no closed hat at all.",
                    description=(
                        "Disco Open Hats with the closed pad taken away: the "
                        "hat hand plays *only* the off-beats now, one pad, "
                        "landing exactly between the kicks. Four to the floor "
                        "under it, the snare clapping 2 and 4, the octave bass "
                        "bouncing along — the engine of every house record "
                        "since 1985, at the tempo it actually runs. Placing a "
                        "hand that never plays a beat is harder than "
                        "alternating two pads; that is the whole lesson."
                    ),
                    hints=[
                        "The hat hand never lands on a number. If a hat and a "
                        "kick ever sound together, the hand has drifted onto "
                        "the beat.",
                        "Let the foot be the metronome and place the hats "
                        "exactly halfway between its notes — the see-saw is "
                        "the pump.",
                        "The open hats want to ring into the next kick. Even, "
                        "unhurried, every one the same length.",
                        "The bass octaves land with your hats, note for note. "
                        "When you are truly between the kicks, you and the "
                        "bass are one instrument.",
                    ],
                ),
                lesson(
                    slug="house-skip",
                    name="The Skip",
                    tier="core",
                    drums=house_skip,
                    bass=OCTAVE,
                    prereq=["house-pump", "kick-16th-grid"],
                    bpm=116,
                    summary='Closed hats tucked on the "a" of 2 and the "a" of '
                    "4 — the garage skip inside the pump.",
                    description=(
                        "Two closed hats slip into the pump, on the \"a\" of 2 "
                        "and the \"a\" of 4 — a 16th after the open hat, a "
                        "16th before the kick. The skip is what turns straight "
                        "house into something that swings its hips, and it "
                        "asks the hat hand to do the open-closed travel from "
                        "Disco at double speed, twice a bar, off the grid the "
                        "openers sit on."
                    ),
                    hints=[
                        'The skip notes are the "a" slots — later than the '
                        "open hat, earlier than the kick, touching neither.",
                        "Open on the \"and\", closed on the \"a\": the pair is "
                        "one gesture, out and back, twice a bar.",
                        "If the skip lands with the kick it has become a 16th "
                        "too late; the kick should always sound alone.",
                        "Keep the skips light. They are the shaker in the "
                        "mix, not a second backbeat.",
                    ],
                ),
                lesson(
                    slug="house-drop",
                    name="The Drop",
                    tier="stretch",
                    drums=house_drop,
                    bass=OCTAVE,
                    prereq=["house-pump", "stop-every-other-bar"],
                    bpm=120,
                    summary="Three bars of pump, then the floor vanishes — open "
                    "hats alone until a snare build snaps it back.",
                    description=(
                        "The DJ's move, played by hand: every fourth bar the "
                        "kick and the clap vanish, the off-beat hats keep "
                        "running alone, and beat 4 fills with four snare 16ths "
                        "that slam the floor back in. The only thing keeping "
                        "time through the drop never plays a beat — you are "
                        "holding the bar from its off-beats, which is Space's "
                        "final exam at 120."
                    ),
                    hints=[
                        "The hats do not stop, speed up, or move to the beat "
                        "during the drop. Same hand, same slots, no floor "
                        "under them.",
                        "The snare build starts ON beat 4, not before it. "
                        "Three empty beats of hats first — count them.",
                        "The kick's return on the next down-beat is the whole "
                        "payoff. Land it with the bass's root and the room "
                        "moves.",
                        "If you cannot tell whether your hats drifted onto the "
                        "beat during the drop, the returning kick will tell "
                        "you: hat-with-kick means they did.",
                    ],
                ),
            ],
        ),
        module(
            "breaks",
            "Breaks",
            "the snare starts moving",
            [
                lesson(
                    slug="the-breakbeat",
                    name="The Breakbeat",
                    tier="plain",
                    drums=the_breakbeat,
                    bass=FUNK,
                    prereq=["kick-16th-grid", "two-bar-kick"],
                    bpm=96,
                    summary="A two-bar break: bar 2 shifts the kick to the "
                    '"e" of 3 and adds a snare pickup.',
                    description=(
                        "The shape every breakbeat record is chopped from. Bar "
                        "1 is the b-boy skeleton — kick on 1, snares on 2 and "
                        "4, a kick driving on the \"and\" of 3. Bar 2 answers: "
                        "the driving kick lands a 16th earlier, on the \"e\", "
                        "and the bar ends with a snare pickup on the \"a\" of "
                        "4. Two bars that rhyme without repeating, over a funk "
                        "bass that knows the break as well as you do."
                    ),
                    hints=[
                        "Learn the two bars as call and answer, not as eight "
                        "beats. Bar 1 drives, bar 2 stumbles and picks up.",
                        'Bar 2\'s kick is on the "e" of 3 — just after the '
                        "beat, alone between hats. It is the head-nod slot "
                        "from The Radio.",
                        "The pickup snare ends bar 2 and leans into bar 1. "
                        "Place it; the loop turns on it.",
                        "If the two bars come out identical, you are playing "
                        "the one you know twice. Count bars out loud until "
                        "the answer bar is a habit.",
                    ],
                ),
                lesson(
                    slug="break-displaced",
                    name="Snare off the Grid",
                    tier="core",
                    drums=break_displaced,
                    bass=FUNK,
                    prereq=["the-breakbeat", "funk-displaced"],
                    bpm=94,
                    summary="Beat 4's snare moves to the \"a\" of 3, and the "
                    "empty 4 it leaves is the funkiest thing in the bar.",
                    description=(
                        "Displacement proper: the backbeat's second half "
                        "arrives a 16th and a half early — on the \"a\" of 3 — "
                        "and beat 4, where every ear expects a snare, holds "
                        "nothing but a hat. The kick tucks in on the \"a\" of "
                        "2 to answer it, and bar 2 adds one more snare on the "
                        "\"and\" of 4 to fold the phrase back over. The note "
                        "you do not play on 4 is the lesson."
                    ),
                    hints=[
                        'The displaced snare is on the "a" of 3: after beat '
                        "3's hat, before 4's. It sounds alone, always.",
                        "Beat 4 is empty and will scream for a snare. Refusing "
                        "it is the exercise — the hat there must sound naked.",
                        "Snare on 2 has not moved. One anchor, one wanderer: "
                        "if both drift the bar has no spine.",
                        "The funk bass leaves the same slots open it always "
                        "did. When your displaced snare and its notes take "
                        "turns cleanly, the displacement is seated.",
                    ],
                ),
                lesson(
                    slug="two-step",
                    name="The Two-Step",
                    tier="stretch",
                    drums=two_step,
                    bass=PEDAL,
                    prereq=["the-breakbeat", "eighths-weak-hand"],
                    bpm=160,
                    summary="Drum & bass's two-step: five voices' worth of "
                    "energy from three, at 160.",
                    description=(
                        "The notes are nothing you have not played for months: "
                        "kick on 1 and the \"and\" of 3, snares on 2 and 4, "
                        "hats in 8ths. The tempo is the lesson — 160 beats a "
                        "minute, the floor of real drum & bass, where the hat "
                        "hand's 8ths run at a speed Pulse never asked of it "
                        "and every spare motion costs a note. The bass holds "
                        "long subs and leaves the speed entirely to you."
                    ),
                    hints=[
                        "Strip every stroke to its minimum: fingers bounce, "
                        "nothing lifts higher than it must. At this speed "
                        "technique is the groove.",
                        "The hat hand carries the tempo; the kick and snare "
                        "just visit. If the 8ths survive, everything "
                        "survives.",
                        "Do not tense as the bar ends. The loop is the same "
                        "four notes forever — the moment your wrist locks, "
                        "the next bar pays for it.",
                        "The snare on 2 and 4 should feel *slow* against the "
                        "hats. Half your speed lives in letting it.",
                    ],
                ),
            ],
        ),
        module(
            "reggae",
            "Reggae",
            "the empty one",
            [
                lesson(
                    slug="one-drop",
                    name="The One Drop",
                    tier="plain",
                    drums=one_drop,
                    bass=DUB,
                    prereq=["half-notes", "stop-every-other-bar"],
                    bpm=76,
                    summary="Kick and snare together on 3, hats in 8ths — and "
                    "beat 1 empty, every bar, on purpose.",
                    description=(
                        "The only major drum tradition where beat 1 is "
                        "deliberately silent. Everything lands on 3 — kick and "
                        "snare together, one sound, the drop — and the bar "
                        "line passes with nothing but a hat. The dub bass "
                        "skips the down-beat too, so nobody in the band plays "
                        "the one: it exists only in your count. Every stage "
                        "since Space has been preparing you to hold a beat "
                        "nobody marks; this is the groove that is *made of* "
                        "that."
                    ),
                    hints=[
                        "The drop on 3 is kick and snare as one sound — the "
                        "stack you have played since Stage 2, now the whole "
                        "groove.",
                        "Beat 1 gets a hat and nothing else. Putting a kick "
                        "there flips the bar into rock and it stops being "
                        "reggae instantly.",
                        "In a real reggae band that snare is a cross-stick — "
                        "play it as a placed knock, not a backbeat crack.",
                        "The bass lands half a beat after the silent one. If "
                        "you wait for it to find bar 1, you are a half beat "
                        "late everywhere — your count owns the one.",
                    ],
                ),
                lesson(
                    slug="skank",
                    name="The Skank",
                    tier="core",
                    drums=skank,
                    bass=DUB,
                    prereq=["one-drop"],
                    bpm=76,
                    summary="The one drop with the hats moved to the "
                    "off-beats: nothing in the bar lands on a number except "
                    "the drop.",
                    description=(
                        "The hat hand moves to the \"and\"s — the skank, the "
                        "upstroke of a reggae guitar written for a hat — and "
                        "now literally nothing lands on a number except the "
                        "drop on 3. No drum, no hat, no bass note marks beat "
                        "1, 2 or 4. The whole bar hangs off your internal "
                        "clock and one stack in its middle, which is why a "
                        "band that can play this can play anything slowly."
                    ),
                    hints=[
                        "Hats on the \"and\"s only. The house pump taught this "
                        "hand position — here it is half the tempo and twice "
                        "as exposed.",
                        "With nothing on the beats, rushing the skank is "
                        "undetectable until the drop lands early. Check "
                        "yourself against beat 3, every bar.",
                        "The drop is the only down-stroke in the bar. Let it "
                        "be heavy; everything else is lift.",
                        "If the bar turns inside out — skank notes becoming "
                        "the beats — stop and count two bars out loud before "
                        "re-entering. It happens to everyone once.",
                    ],
                ),
                lesson(
                    slug="steppers",
                    name="Steppers",
                    tier="stretch",
                    drums=steppers,
                    bass=DUB,
                    prereq=["skank", "four-on-the-floor"],
                    bpm=78,
                    summary="The kick returns to all four beats under the "
                    "skank — reggae's other engine.",
                    description=(
                        "After two lessons of empty down-beats the floor comes "
                        "back: kick on every beat, the drop's snare still on "
                        "3, the hats still skanking the \"and\"s. Foot on "
                        "every number, hand never on one — full four-limb "
                        "independence in miniature, and the exact opposite "
                        "job in each limb. The dub bass still avoids beat 1, "
                        "so your kick is now the only voice in the whole band "
                        "that plays it."
                    ),
                    hints=[
                        "Foot on the numbers, hand on the \"and\"s, and never "
                        "the twain: no note in this groove has two voices "
                        "except the drop on 3.",
                        "The kick is a heartbeat, not four accents. Keep it "
                        "under the skank the way the house pump kept the "
                        "floor under the hats.",
                        "Beat 3 stacks kick and snare — the drop survives "
                        "inside the pulse. It should still be the loudest "
                        "moment in the bar.",
                        "Your kick on 1 is the only note anyone plays there. "
                        "The whole band is leaning on you — place it like it "
                        "matters, because it does.",
                    ],
                ),
            ],
        ),
    ],
    closing=checkpoint(
        slug="checkpoint-12",
        name="Checkpoint — The Dancefloor",
        drums=checkpoint_12,
        bass=OCTAVE,
        bpm=104,
        summary="One bar each: the house pump, the break's answer bar, the "
        "two-step, and the one drop.",
        description=(
            "Four dancefloors in four bars. The hat hand changes job at every "
            "bar line — off-beats, 8ths, 8ths, 8ths — the kick goes from every "
            "beat to almost none, and the last bar empties beat 1 entirely. "
            "One tempo holds all four, faster than reggae likes and slower "
            "than the two-step wants, which is exactly the discomfort a "
            "working drummer gets paid for."
        ),
        hints=[
            "Bar 1's hats are off the beat and bar 2's are on the 8ths. That "
            "first join is the hardest hand move in the loop.",
            "Bar 2 is the break's *answer* bar — kick on the \"e\" of 3, "
            "pickup snare at the end. Do not play the plain bar there.",
            "Bar 4 has nothing on beat 1. After three bars of floor, leaving "
            "it empty is the checkpoint inside the checkpoint.",
            "The octave bass pumps through all four bars without taking "
            "sides. Lock the changing drums to its unchanging grid.",
        ],
    ),
)
