#!/usr/bin/env python3
"""Generate lesson MIDI files into static/lessons/.

The curriculum lives in the LESSONS table below; each entry writes a multi-track
(format 1) MIDI named lesson-<id>.mid plus an entry in
static/lessons/manifest.json (id, name, file, bpm, bars, summary, description).
Track roles are chosen by the track name:
  - "drums"        -> playable: shown on the highway and scored.
  - "family:id"    -> backing:  auto-played from static/<family>/<id>/<note>.oga
                      (e.g. "bass:lately"), never shown or scored.
  - "count-in"     -> the stick count that leads the student in; audible but
                      never shown or scored (see COUNT-IN RULE below).

COUNT-IN RULE: every lesson must have three stick clicks before it starts, on the
last three beats of the lead-in bar. Nothing clicks on the pattern's first beat —
that one is the student's. build_lesson() adds the track to every lesson
automatically, so a new entry in LESSONS gets it for free — do not hand-roll one
per lesson, and do not remove it.

Re-run after adding or editing a lesson:
  python3 scripts/make-lessons.py
"""
import json
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "lessons")

PPQ = 480
BEATS_PER_BAR = 4

# GM percussion notes used by the drum lessons. The count-in clicks on the side
# stick: a dry rim sound that cuts through a kit without being mistaken for one
# of the pads the student is about to play. (GM 31 "Sticks" would read better
# still, but render-drums.py only renders 35-70.)
KICK, SNARE, CLOSED_HH, OPEN_HH, SIDE_STICK = 36, 38, 42, 46, 37


def varint(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def build_track(name, events, length_ticks, meta=None):
    """events: list of (tick, order, raw_bytes); order sorts ties (offs<ons)."""
    ev = list(meta or [])
    if name:
        nm = name.encode("latin1")
        ev.append((0, -10, bytes([0xFF, 0x03]) + varint(len(nm)) + nm))
    allev = sorted(ev + events, key=lambda e: (e[0], e[1]))
    body = b""
    prev = 0
    for tick, _order, raw in allev:
        body += varint(tick - prev) + raw
        prev = tick
    body += varint(max(0, length_ticks - prev)) + bytes([0xFF, 0x2F, 0x00])
    return b"MTrk" + struct.pack(">I", len(body)) + body


def write_midi(path, tracks):
    hdr = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), PPQ)
    with open(path, "wb") as f:
        f.write(hdr + b"".join(tracks))


def hit(events, tick, note):
    """A percussion strike on channel 10: note-on then a short note-off."""
    events.append((tick, 1, bytes([0x99, note, 100])))
    events.append((tick + 60, 0, bytes([0x89, note, 0])))


def bass_note(events, tick, note, dur=200):
    """A bass note on channel 1."""
    events.append((tick, 1, bytes([0x90, note, 95])))
    events.append((tick + dur, 0, bytes([0x80, note, 0])))


def count_in_sticks():
    """The stick count that leads the student in — three clicks, then silence.

    Written in a lead-in bar of its own: beats 2, 3 and 4 of that bar click, and
    the bar line that follows IS the pattern's first beat. The app plays this
    track one bar early (it already holds an empty bar of lead-in before the
    pattern), so the count runs "click, click, click" and the student's own first
    hit lands on the empty down-beat that follows.
    """
    events = []
    for beat in (1, 2, 3):  # the 4th beat is left silent — the down-beat is theirs
        hit(events, beat * PPQ, SIDE_STICK)
    return events, BEATS_PER_BAR * PPQ


def quarter_kick(bars=4):
    """Kick on every beat — one limb, straight quarter notes."""
    events = []
    bar_ticks = BEATS_PER_BAR * PPQ
    for bar in range(bars):
        for beat in range(BEATS_PER_BAR):
            hit(events, bar * bar_ticks + beat * PPQ, KICK)
    return events, bars * bar_ticks


def kick_and_hats(bars=4):
    """Kick on 1 & 3 under closed hats on all four beats — two limbs together."""
    events = []
    bar_ticks = BEATS_PER_BAR * PPQ
    for bar in range(bars):
        base = bar * bar_ticks
        for beat in range(BEATS_PER_BAR):
            hit(events, base + beat * PPQ, CLOSED_HH)
        for beat in (0, 2):  # beats 1 and 3
            hit(events, base + beat * PPQ, KICK)
    return events, bars * bar_ticks


def four_on_the_floor(bars=4):
    """Kick on every beat, snare backbeat on 2 & 4, closed hats on 8ths."""
    events = []
    bar_ticks = BEATS_PER_BAR * PPQ
    for bar in range(bars):
        base = bar * bar_ticks
        for beat in range(BEATS_PER_BAR):
            hit(events, base + beat * PPQ, KICK)
        for beat in (1, 3):  # beats 2 and 4
            hit(events, base + beat * PPQ, SNARE)
        for eighth in range(BEATS_PER_BAR * 2):
            hit(events, base + eighth * (PPQ // 2), CLOSED_HH)
    return events, bars * bar_ticks


def disco_open_hats(bars=4):
    """2.1's groove with the off-beat hats opened up — four pads.

    Kick on every beat and snare on 2 & 4 are unchanged from four-on-the-floor;
    the 8th-note hat line now splits across two pads, closed on the beats and
    open on the "and"s, so the hat hand has to alternate instead of repeat.
    """
    events = []
    bar_ticks = BEATS_PER_BAR * PPQ
    eighth = PPQ // 2
    for bar in range(bars):
        base = bar * bar_ticks
        for beat in range(BEATS_PER_BAR):
            hit(events, base + beat * PPQ, KICK)
            hit(events, base + beat * PPQ, CLOSED_HH)  # down-beat: closed
            hit(events, base + beat * PPQ + eighth, OPEN_HH)  # "and": open
        for beat in (1, 3):  # beats 2 and 4
            hit(events, base + beat * PPQ, SNARE)
    return events, bars * bar_ticks


def octave_bass(bars=4):
    """Disco/house octave-bounce bass over Am - F - C - G (one chord per bar).

    Root on the down-beats, octave-up on the off-beats, with a chromatic
    approach note on the last 8th leading into the next bar's root.
    """
    events = [(0, -1, bytes([0xC0, 0]))]  # program change (ignored by our sampler)
    roots = [33, 29, 36, 31]  # A1, F1, C2, G1
    bar_ticks = BEATS_PER_BAR * PPQ
    eighth = PPQ // 2
    for bar in range(bars):
        base = bar * bar_ticks
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        for i, pos in enumerate(range(0, bar_ticks, eighth)):  # 8 eighth-notes
            if i == 7:
                note = nxt - 1  # chromatic approach into the next root
            elif i % 2 == 0:
                note = root  # down-beat: root
            else:
                note = root + 12  # off-beat: octave up
            bass_note(events, base + pos, note, dur=180)
    return events, bars * bar_ticks


def quarter_bass(bars=4):
    """Root note on every beat over Am - Am - F - G (one chord per bar).

    A plain quarter-note pulse: it doubles the beat the student is chasing
    instead of syncopating against it, which is what the early lessons need.
    """
    events = [(0, -1, bytes([0xC0, 0]))]  # program change (ignored by our sampler)
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    bar_ticks = BEATS_PER_BAR * PPQ
    for bar in range(bars):
        base = bar * bar_ticks
        root = roots[bar % len(roots)]
        for beat in range(BEATS_PER_BAR):
            bass_note(events, base + beat * PPQ, root, dur=360)
    return events, bars * bar_ticks


def syncopated_bass(bars=4):
    """Off-beat bass over Am - Am - F - G: "1, 2-and, 3, 4-and".

    Beats 1 and 3 stay anchored so the down-beat is never in doubt, while the
    pushes on the "and" of 2 and 4 keep the line from just doubling the drums.
    The last off-beat walks a semitone into the next bar's root.
    """
    events = [(0, -1, bytes([0xC0, 0]))]  # program change (ignored by our sampler)
    roots = [33, 33, 29, 31]  # A1, A1, F1, G1
    bar_ticks = BEATS_PER_BAR * PPQ
    for bar in range(bars):
        base = bar * bar_ticks
        root = roots[bar % len(roots)]
        nxt = roots[(bar + 1) % len(roots)]
        bass_note(events, base + 0 * PPQ, root, dur=300)  # beat 1: root
        bass_note(events, base + 3 * PPQ // 2, root + 12, dur=200)  # 2-and: octave
        bass_note(events, base + 2 * PPQ, root, dur=300)  # beat 3: root
        bass_note(events, base + 7 * PPQ // 2, nxt - 1, dur=200)  # 4-and: approach
    return events, bars * bar_ticks


# The curriculum, in the order the catalogue lists it. `drums` and `bass` are
# pattern builders taking a bar count; `summary` is the one-liner on the
# catalogue card, `description` the longer brief on the lesson page, and `hints`
# the practice tips listed under the chart there.
LESSONS = [
    {
        "id": "1.1",
        "name": "1.1 — Kick on Every Beat",
        "bpm": 60,
        "bars": 4,
        "drums": quarter_kick,
        "bass": ("lately", syncopated_bass),
        "summary": "One pad, straight quarter notes: kick on all four beats.",
        "description": "Your first groove: nothing but the kick, once on every "
        "beat. The bass lands with you on 1 and 3 and pushes off-beat in "
        "between, so you have something to lock against without it playing "
        "your part for you. Aim for even spacing rather than force — one "
        "steady bar is worth four rushed ones.",
        "hints": [
            "Press Listen first. Play only once you can hum the pulse back.",
            "One finger, one pad: keep your strong hand's index on the kick "
            "and don't reposition mid-loop.",
            "Count \"1 2 3 4\" out loud and strike on the number, not after "
            "it — saying it late is playing it late.",
            "Watch the note approach the line instead of reacting to the "
            "sound you just made.",
            "The bass pushes between your hits — that is on purpose. Follow "
            "its notes on 1 and 3 and ignore the ones in between.",
            "Orange notes mean drifting time, not weak hits. Hit Listen "
            "again, re-sync with the pulse, then run it once more.",
        ],
    },
    {
        "id": "1.2",
        "name": "1.2 — Kick & Hi-Hat",
        "bpm": 60,
        "bars": 4,
        "drums": kick_and_hats,
        "bass": ("lately", quarter_bass),
        "summary": "Two pads at once: hats on all four beats, kick on 1 and 3.",
        "description": "Now two limbs. The hi-hat keeps every beat while the "
        "kick plays only 1 and 3, so beats 1 and 3 are struck by both pads "
        "together and beats 2 and 4 by the hat alone. Getting those pairs to "
        "land as one sound is the whole exercise.",
        "hints": [
            "One pad per hand: hi-hat on your weak hand, kick on your strong "
            "hand. Never cross over to cover both.",
            "Beats 1 and 3 are a single motion — both fingers drop together. "
            "Drill just that pair a dozen times before running the loop.",
            "If the pair sounds like two taps rather than one thud, leave the "
            "loop and drill the two fingers together until it's one sound.",
            "Let the hat hand run like a metronome and drop the kick into it; "
            "don't try to steer both hands at once.",
            "Say \"both — hat — both — hat\" through the bar so beats 2 and 4 "
            "never grow an extra kick.",
        ],
    },
    {
        "id": "2.1",
        "name": "2.1 — Four on the Floor",
        "bpm": 60,
        "bars": 4,
        "drums": four_on_the_floor,
        "bass": ("lately", octave_bass),
        "summary": "Four-on-the-floor: kick on all four beats, snare on 2 "
        "and 4, closed hats on every 8th.",
        "description": "The four-on-the-floor groove: kick on every beat, "
        "snare backbeat on 2 and 4, and closed hi-hats on the off-beats. "
        "An octave-bouncing bass line runs underneath — start slow and lock "
        "into it.",
        "hints": [
            "Three voices, three fingers, fixed positions: hats and snare on "
            "one hand, kick on the other.",
            "The hats run in 8ths — twice the speed of the kick. Keep that "
            "hand moving continuously and land the other voices inside it.",
            "Beats 2 and 4 stack kick + snare + hat. Practise those two beats "
            "alone until all three fire as one sound.",
            "Sing it before you play it: \"boom-tick, bap-tick, boom-tick, "
            "bap-tick.\" If you can say it, your hands can find it.",
            "Missing hats usually means the wrist is tensing up. Shake the "
            "hand out and let the fingers bounce instead of pressing.",
        ],
    },
    {
        "id": "2.2",
        "name": "2.2 — Disco Open Hats",
        "bpm": 60,
        "bars": 4,
        "drums": disco_open_hats,
        "bass": ("lately", octave_bass),
        "summary": "Four-on-the-floor with the off-beats opened up: closed hat "
        "on the beats, open hat on every \"and\".",
        "description": "Lesson 2.1's groove, one pad wider. Kick still lands on "
        "every beat and the snare still answers on 2 and 4, but the 8th-note "
        "hat line now splits in two: closed hat on the numbers, open hat on "
        "every \"and\". The same octave-bouncing bass runs underneath, "
        "so only your part got harder — the hat hand has to move between "
        "two pads instead of repeating one.",
        "hints": [
            "Four voices now. Give the two hats neighbouring pads on your weak "
            "hand — index closed, middle open — with snare and kick "
            "on the strong hand.",
            "Drill the hat hand alone first: \"closed-open-closed-open\" "
            "for a full bar, no kick, no snare. Only add the other hand once "
            "that alternation runs without looking.",
            "The open hat is a swing door, not a stab — let it ring into "
            "the next closed hit instead of clipping it short.",
            "Every open hat sits alone between two stacks — it is the only "
            "moment nothing else fires. Use it to breathe and reset the hand.",
            "Say \"boom-tss, bap-tss\" and keep the \"tss\" "
            "louder than in 2.1 — if the open hats disappear, you are "
            "landing on the closed pad twice.",
            "Losing the alternation halfway through a bar means the hat hand is "
            "leading with the wrong finger. Stop, reset on the next bar line, "
            "start the pair from closed.",
        ],
    },
]


def build_lesson(lesson):
    """Write one lesson's MIDI and return its manifest entry."""
    bars = lesson["bars"]
    tempo = int(round(60_000_000 / lesson["bpm"]))
    conductor_meta = [
        (0, -3, bytes([0xFF, 0x58, 0x04, 0x04, 0x02, 0x18, 0x08])),  # 4/4
        (0, -2, bytes([0xFF, 0x51, 0x03]) + tempo.to_bytes(3, "big")),  # tempo
    ]

    drum_events, length = lesson["drums"](bars)
    count_events, count_length = count_in_sticks()
    tracks = [
        build_track("tempo", [], length, meta=conductor_meta),
        build_track("drums", drum_events, length),
        # Every lesson counts in — see COUNT-IN RULE at the top of this file.
        build_track("count-in", count_events, count_length),
    ]
    if lesson.get("bass"):
        bass_id, builder = lesson["bass"]
        bass_events, _ = builder(bars)
        tracks.append(build_track(f"bass:{bass_id}", bass_events, length))

    file = f"lesson-{lesson['id']}.mid"
    write_midi(os.path.join(OUT, file), tracks)
    return {
        "id": lesson["id"],
        "name": lesson["name"],
        "file": file,
        "bpm": lesson["bpm"],
        "bars": bars,
        "summary": lesson["summary"],
        "description": lesson["description"],
        "hints": lesson.get("hints", []),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    lessons = [build_lesson(l) for l in LESSONS]
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        # Trailing newline so the file matches what prettier (pre-commit) expects
        # and regenerating never shows up as a diff.
        json.dump({"lessons": lessons}, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {len(lessons)} lesson(s) to {OUT}")


if __name__ == "__main__":
    main()
