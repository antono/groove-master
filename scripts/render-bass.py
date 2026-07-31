#!/usr/bin/env python3
"""Pre-render bass one-shots from the CC0 FreePats bass SoundFonts.

These provide a backing-track bass to play under the drum lessons. Each bass
is a bank-0 / program-0 melodic preset; we render a chromatic range of notes
to short OGG files so the browser can sequence a bassline without shipping the
SoundFonts. Sources are all CC0 1.0 (public domain) — see THANKS.md.

Outputs:
  static/bass/<id>/<note>.oga   one file per note, per bass
  static/bass/manifest.json     basses + note range

Re-run after changing the SoundFonts or range:
  python3 scripts/render-bass.py
"""
import json
import os
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFDIR = os.path.join(ROOT, "soundfonts")
OUT = os.path.join(ROOT, "static", "bass")
TMP = "/tmp/pad_bass_mid"

# Practical bass range for backing lines: E1 (28) .. C4 (60).
LO, HI = 28, 60

BASSES = [
    {"id": "lately", "name": "Lately Bass", "sf2": "LatelyBass.sf2"},
    {"id": "synth1", "name": "Synth Bass 1", "sf2": "SynthBass1.sf2"},
    {"id": "synth2", "name": "Synth Bass 2", "sf2": "SynthBass2.sf2"},
]


def varint(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def write_midi(note, path):
    """Melodic channel 1, program 0, hold ~1.6s then let the release ring."""
    ev = varint(0) + bytes([0xC0, 0])            # program change -> preset 0
    ev += varint(0) + bytes([0x90, note, 100])    # note on
    ev += varint(1536) + bytes([0x80, note, 0])   # note off @1.6s
    ev += varint(960) + bytes([0xFF, 0x2F, 0x00]) # end of track @2.6s
    trk = b"MTrk" + struct.pack(">I", len(ev)) + ev
    hdr = b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480)
    with open(path, "wb") as f:
        f.write(hdr + trk)


def render(sf2, note, dest):
    write_midi(note, f"{TMP}/{note}.mid")
    subprocess.run(
        ["fluidsynth", "-ni", "-F", dest, "-T", "oga", "-O", "s16",
         "-r", "44100", "-g", "0.6", sf2, f"{TMP}/{note}.mid"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def main():
    os.makedirs(TMP, exist_ok=True)
    notes = list(range(LO, HI + 1))
    catalogue = []
    for bass in BASSES:
        sf2 = os.path.join(SFDIR, bass["sf2"])
        if not os.path.exists(sf2):
            sys.exit(f"SoundFont not found: {sf2}")
        dest_dir = os.path.join(OUT, bass["id"])
        os.makedirs(dest_dir, exist_ok=True)
        for note in notes:
            render(sf2, note, os.path.join(dest_dir, f"{note}.oga"))
        catalogue.append({"id": bass["id"], "name": bass["name"]})
        print(f"rendered {bass['name']} ({len(notes)} notes)")

    manifest = {"basses": catalogue, "lo": LO, "hi": HI}
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {os.path.join(OUT, 'manifest.json')}")


if __name__ == "__main__":
    main()
