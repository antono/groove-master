#!/usr/bin/env python3
"""Generate lesson MIDI files into static/lessons/.

A lesson is a multi-track (format 1) MIDI plus an entry in
static/lessons/manifest.json. Track roles are chosen by the track name:
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


def main():
    os.makedirs(OUT, exist_ok=True)
    lessons = []

    bpm = 60
    bars = 4
    tempo = int(round(60_000_000 / bpm))
    conductor_meta = [
        (0, -3, bytes([0xFF, 0x58, 0x04, 0x04, 0x02, 0x18, 0x08])),  # 4/4
        (0, -2, bytes([0xFF, 0x51, 0x03]) + tempo.to_bytes(3, "big")),  # tempo
    ]

    drum_events, length = four_on_the_floor(bars)
    bass_events, _ = octave_bass(bars)

    tracks = [
        build_track("tempo", [], length, meta=conductor_meta),
        build_track("drums", drum_events, length),
        build_track("bass:lately", bass_events, length),
    ]
    write_midi(os.path.join(OUT, "lesson2.mid"), tracks)
    lessons.append(
        {
            "id": "lesson2",
            "name": "Lesson 2",
            "file": "lesson2.mid",
            "bpm": bpm,
            "bars": bars,
            "description": "The four-on-the-floor groove: kick on every beat, "
            "snare backbeat on 2 and 4, and closed hi-hats on the off-beats. "
            "A simple bass line plays along in the background. Start slow and "
            "lock in with the click.",
        }
    )

    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump({"lessons": lessons}, f, indent=2)
    print(f"wrote {len(lessons)} lesson(s) to {OUT}")


if __name__ == "__main__":
    main()
