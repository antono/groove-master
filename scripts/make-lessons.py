#!/usr/bin/env python3
"""Generate lesson MIDI files into static/lessons/.

The curriculum lives in the LESSONS table below; each entry writes a multi-track
(format 1) MIDI named lesson-<id>.mid plus an entry in
static/lessons/manifest.json (id, name, file, bpm, bars, summary, description).
Track roles are chosen by the track name:
  - "drums"        -> playable: shown on the highway and scored.
  - "family:id"    -> backing:  auto-played from static/<family>/<id>/<note>.oga
                      (e.g. "bass:lately"), never shown or scored.

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

# GM percussion notes used by the drum lessons.
KICK, SNARE, CLOSED_HH = 36, 38, 42


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
    tracks = [
        build_track("tempo", [], length, meta=conductor_meta),
        build_track("drums", drum_events, length),
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
