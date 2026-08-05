"""MIDI mechanics: bytes in, file out. No curriculum knowledge lives here.

A lesson MIDI is format 1, one track per role, and the track *name* is what
tells the app what to do with it:

  "drums"     playable: shown on the highway and scored.
  "family:id" backing:  auto-played from static/<family>/<id>/<note>.oga,
              never shown, never scored (e.g. "bass:lately").
  "count-in"  the stick count that leads the student in; audible, never scored.
"""

import struct

PPQ = 480
BEATS_PER_BAR = 4

# GM percussion notes the curriculum uses. The count-in clicks on the side stick:
# a dry rim sound that cuts through a kit without being mistaken for a pad the
# student is about to play. (GM 31 "Sticks" would read better still, but
# render-drums.py only renders 35-70.)
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
