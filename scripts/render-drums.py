#!/usr/bin/env python3
"""Pre-render drum one-shots from the SoundFont into static/drums/.

Each kit is a bank-128 (GM percussion) preset in the .sf2. For every mapped
GM drum note we render a short OGG one-shot with fluidsynth, so the browser
can play low-latency samples without shipping the 244 MB SoundFont.

Outputs:
  static/drums/kit<N>/<note>.oga   one file per drum, per kit
  static/drums/manifest.json       kits + drum (note -> name) catalogue

Re-run after changing the SoundFont or the drum layout:
  python3 scripts/render-drums.py
"""
import json
import os
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SF2 = os.path.join(ROOT, "soundfonts", "Perfect_Drums.sf2")
OUT = os.path.join(ROOT, "static", "drums")
TMP = "/tmp/pad_mid"

# General MIDI percussion map (notes present in every kit: 35-70).
GM_DRUMS = {
    35: "Ac Bass Drum", 36: "Kick", 37: "Side Stick", 38: "Snare",
    39: "Hand Clap", 40: "E Snare", 41: "Lo Floor Tom", 42: "Closed HH",
    43: "Hi Floor Tom", 44: "Pedal HH", 45: "Lo Tom", 46: "Open HH",
    47: "LoMid Tom", 48: "HiMid Tom", 49: "Crash", 50: "Hi Tom",
    51: "Ride", 52: "China", 53: "Ride Bell", 54: "Tambourine",
    55: "Splash", 56: "Cowbell", 57: "Crash 2", 58: "Vibraslap",
    59: "Ride 2", 60: "Hi Bongo", 61: "Lo Bongo", 62: "Mute Conga",
    63: "Open Conga", 64: "Lo Conga", 65: "Hi Timbale", 66: "Lo Timbale",
    67: "Hi Agogo", 68: "Lo Agogo", 69: "Cabasa", 70: "Maracas",
}

NUM_KITS = 12          # presets 0..11 in Perfect_Drums.sf2
NOTES = list(range(35, 71))


def varint(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def write_midi(preset, note, path):
    """Minimal SMF: select drum kit on ch10, hit one note, 3s tail for decay."""
    ev = varint(0) + bytes([0xC9, preset])          # program change -> kit
    ev += varint(0) + bytes([0x99, note, 110])       # note on
    ev += varint(960) + bytes([0x89, note, 0])       # note off @1s
    ev += varint(1920) + bytes([0xFF, 0x2F, 0x00])   # end of track @3s
    trk = b"MTrk" + struct.pack(">I", len(ev)) + ev
    hdr = b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480)
    with open(path, "wb") as f:
        f.write(hdr + trk)


def render(preset, note, dest):
    write_midi(preset, note, f"{TMP}/{note}.mid")
    subprocess.run(
        ["fluidsynth", "-ni", "-F", dest, "-T", "oga", "-O", "s16",
         "-r", "44100", "-g", "0.9", SF2, f"{TMP}/{note}.mid"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def main():
    if not os.path.exists(SF2):
        sys.exit(f"SoundFont not found: {SF2}")
    os.makedirs(TMP, exist_ok=True)

    kits = []
    for k in range(NUM_KITS):
        kit_dir = os.path.join(OUT, f"kit{k + 1}")
        os.makedirs(kit_dir, exist_ok=True)
        for note in NOTES:
            render(k, note, os.path.join(kit_dir, f"{note}.oga"))
        kits.append({"id": k + 1, "name": f"Perfect Drums {k + 1}"})
        print(f"rendered kit {k + 1}/{NUM_KITS}")

    manifest = {
        "kits": kits,
        "drums": [{"note": n, "name": GM_DRUMS[n]} for n in NOTES],
    }
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {os.path.join(OUT, 'manifest.json')}")


if __name__ == "__main__":
    main()
