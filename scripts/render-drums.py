#!/usr/bin/env python3
"""Pre-render drum one-shots from the SoundFont into static/drums/.

Each kit is a bank-128 (GM percussion) preset in the .sf2. For every mapped
GM drum note we render a short OGG one-shot with fluidsynth, so the browser
can play low-latency samples without shipping the 244 MB SoundFont.

Some GM notes have no key zone in the SoundFont. fluidsynth still exits 0 and
still writes a structurally valid file — it just holds five seconds of digital
silence, which the browser decodes without complaint and plays as nothing. So
every render is audited (see ogg_audio_bytes) and silent ones are replaced from
FALLBACKS; anything still silent at the end fails the run.

Outputs:
  static/drums/kit<N>/<note>.oga   one file per drum, per kit
  static/drums/manifest.json       kits + drum (note -> name) catalogue

Re-run after changing the SoundFont or the drum layout:
  python3 scripts/render-drums.py

Audit the files already in static/drums/ — no SoundFont or fluidsynth needed:
  python3 scripts/render-drums.py --audit

Substitute any silent ones in place — needs ffmpeg, but still no SoundFont:
  python3 scripts/render-drums.py --repair

Bake the LEVELS trims into the samples (idempotent — only the delta against
static/drums/levels.json is applied, so re-running changes nothing):
  python3 scripts/render-drums.py --level

A full render needs `fluidsynth`; substitution needs `ffmpeg`. Both are in
devenv.nix.
"""
import json
import os
import shutil
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

SAMPLE_RATE = 44100
TAIL_SECONDS = 5.004   # what the MIDI below renders to at 480 ppq

# A real 5 s hit carries 13-17 KB of Vorbis audio pages; silence carries ~217 B
# (the file is then almost entirely the 4230-byte codebook header).
SILENT_AUDIO_BYTES = 1000

# Stand-ins for notes the SoundFont leaves unmapped. Which drum covers for a
# missing one is a musical call, so it is spelled out rather than inferred.
# Tried in order; the first candidate that lands audibly wins.
#   ("kit",   None)              same note from the nearest kit that isn't silent
#   ("pitch", note, semitones)   neighbour note, resampled — what an SF2 itself
#                                does to stretch one sample across a key range
FALLBACKS = {
    39: [("kit", None)],          # Hand Clap: silent in kits 7-12, real in 1-6.
                                  # Its neighbours (37 Side Stick, 40 E Snare)
                                  # are other instruments, so borrow a clap.
    # LoMid Tom <- Lo Tom, two semitones up. Its other neighbour, HiMid Tom, is
    # the closer interval but one of the quietest samples in the bank: the .sf2
    # renders toms anywhere from -29 dBFS (48 HiMid) to -10 dBFS (41 Lo Floor),
    # and at -29 next to a -7.5 dB snare a pad reads as broken even when it
    # isn't. Lo Tom is adjacent on the grid too (DEFAULT_SOUND has 45/47/50 in a
    # row), so matching its level keeps that row even.
    47: [("pitch", 45, 2)],
    68: [("pitch", 67, -4)],      # Lo Agogo <- Hi Agogo, a major third down
}

# Level trims baked into the rendered samples, in dB, as kit -> note -> gain.
# The SoundFont's own levels are uneven — a kit spans roughly -33 to -7.5 dBFS —
# so drums that should sit up in the mix come out too quiet to hear next to a
# kick or snare. Values come from auditioning on /debug/levels.
LEVELS = {
    1: {
        42: 9,   # Closed HH, -27.7 dBFS as rendered
        44: 9,   # Pedal HH,  -29.6 dBFS as rendered
        46: 6,   # Open HH,   -27.9 dBFS as rendered
        59: 6,   # Ride 2,    -27.7 dBFS as rendered
    },
}

# What LEVELS has actually been applied to the files on disk. Kept beside the
# samples because the gain is baked in: without it a second run would stack
# another +9 dB on an already-boosted file. Only the difference is ever applied,
# so re-running is a no-op and lowering a value works as well as raising it.
APPLIED = os.path.join(OUT, "levels.json")


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
         "-r", str(SAMPLE_RATE), "-g", "0.9", SF2, f"{TMP}/{note}.mid"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


# --- silence audit ---------------------------------------------------------


def ogg_audio_bytes(path):
    """Total payload of every Ogg page after the two header pages.

    Page 1 is the Vorbis identification header and page 2 the comment/setup
    header (codebooks); everything after that is encoded audio. Summing it is
    enough to tell a real hit from silence, and needs no Vorbis decoder.
    """
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return 0
    total = pages = offset = 0
    while True:
        i = data.find(b"OggS", offset)
        if i < 0:
            return total
        nsegs = data[i + 26]
        body = sum(data[i + 27:i + 27 + nsegs])
        pages += 1
        if pages > 2:
            total += body
        offset = i + 27 + nsegs + body


def is_silent(path):
    return ogg_audio_bytes(path) < SILENT_AUDIO_BYTES


def kit_dir(kit):
    return os.path.join(OUT, f"kit{kit}")


def sample_path(kit, note):
    return os.path.join(kit_dir(kit), f"{note}.oga")


def audit():
    """Every (kit, note) whose rendered file has no audio in it."""
    return [
        (kit, note)
        for kit in range(1, NUM_KITS + 1)
        for note in NOTES
        if is_silent(sample_path(kit, note))
    ]


def report(silent):
    """Group the audit by note — the way the SoundFont's gaps actually fall."""
    by_note = {}
    for kit, note in silent:
        by_note.setdefault(note, []).append(kit)
    for note in sorted(by_note):
        kits = ", ".join(str(k) for k in by_note[note])
        print(f"  note {note:2d} {GM_DRUMS[note]:14s} silent in kit(s): {kits}")


# --- stand-ins for unmapped notes -----------------------------------------


def nearest_audible_kit(kit, note, skip=()):
    """Kit closest to `kit` whose render of `note` has sound in it.

    `skip` holds the (kit, note) pairs found silent by the initial audit, so a
    kit that is only audible because it was *just* repaired is not treated as a
    source. Otherwise the first repair becomes the second one's source and the
    choice depends on iteration order.
    """
    others = sorted(
        (k for k in range(1, NUM_KITS + 1) if k != kit),
        key=lambda k: (abs(k - kit), k),
    )
    for k in others:
        if (k, note) not in skip and not is_silent(sample_path(k, note)):
            return k
    return None


def pitch_shift(src, dest, semitones):
    """Resample `src` to shift its pitch, then encode to Ogg Vorbis.

    asetrate reinterprets the sample rate (tape-speed: pitch and duration move
    together) and aresample brings it back to SAMPLE_RATE. Trimming to
    TAIL_SECONDS keeps every one-shot the same length as a direct render.

    The source is the neighbour's own .oga, not a fresh WAV render, so a repair
    needs nothing but ffmpeg — no SoundFont. That costs one Vorbis generation
    on what is already a decaying tail, which is a fair trade for being able to
    fix the shipped samples without the 244 MB .sf2.
    """
    rate = SAMPLE_RATE * (2 ** (semitones / 12))
    tmp = dest + ".tmp.oga"        # ffmpeg cannot read and write the same file
    subprocess.run(
        ["ffmpeg", "-y", "-i", src,
         "-af", f"asetrate={rate},aresample={SAMPLE_RATE}",
         "-t", str(TAIL_SECONDS), "-c:a", "libvorbis", "-q:a", "5", tmp],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    os.replace(tmp, dest)


def substitute(kit, note, skip=()):
    """Fill a silent (kit, note) from FALLBACKS. Returns what was used, or None."""
    dest = sample_path(kit, note)
    for candidate in FALLBACKS.get(note, []):
        if candidate[0] == "kit":
            src_kit = candidate[1] or nearest_audible_kit(kit, note, skip)
            if src_kit is None:
                continue
            shutil.copyfile(sample_path(src_kit, note), dest)
            if not is_silent(dest):
                return f"{GM_DRUMS[note]} from kit {src_kit}"

        elif candidate[0] == "pitch":
            _, src_note, semitones = candidate
            src = sample_path(kit, src_note)
            if is_silent(src):
                continue
            pitch_shift(src, dest, semitones)
            if not is_silent(dest):
                return f"{GM_DRUMS[src_note]} pitched {semitones:+d} semitone(s)"

    return None


# --- baked level trims ----------------------------------------------------


def load_applied():
    """kit -> note -> dB already baked into the files on disk."""
    try:
        with open(APPLIED) as f:
            raw = json.load(f).get("gainsDb", {})
    except (OSError, ValueError):
        return {}
    return {int(k): {int(n): float(db) for n, db in v.items()} for k, v in raw.items()}


def save_applied(applied):
    def tidy(db):
        return int(db) if float(db).is_integer() else db

    trimmed = {
        str(kit): {str(n): tidy(db) for n, db in sorted(notes.items()) if db}
        for kit, notes in sorted(applied.items())
        if any(notes.values())
    }
    with open(APPLIED, "w") as f:
        json.dump({"gainsDb": trimmed}, f, indent=2)
        f.write("\n")


def apply_gain(path, db):
    """Re-encode `path` with `db` of gain."""
    tmp = path + ".tmp.oga"
    subprocess.run(
        ["ffmpeg", "-y", "-i", path, "-af", f"volume={db}dB",
         "-c:a", "libvorbis", "-q:a", "5", tmp],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    os.replace(tmp, path)


def peak_dbfs(path):
    """Peak level of a file, via ffmpeg's volumedetect."""
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    for line in out.splitlines():
        if "max_volume:" in line:
            return float(line.split("max_volume:")[1].strip().split()[0])
    return None


def level(reset=False):
    """Bake LEVELS into the samples, applying only what isn't applied yet.

    Each change re-encodes the file, so repeatedly tweaking the same drum stacks
    Vorbis generations. That is inaudible for a hit or two, but once a set of
    trims has settled it is worth a full render to bake them in one pass from
    the SoundFont.
    """
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH (see devenv.nix)")
    applied = {} if reset else load_applied()
    changed = 0

    for kit in range(1, NUM_KITS + 1):
        for note in NOTES:
            want = LEVELS.get(kit, {}).get(note, 0)
            have = applied.get(kit, {}).get(note, 0)
            delta = round(want - have, 3)
            if not delta:
                continue

            path = sample_path(kit, note)
            before = peak_dbfs(path)
            if before is not None and before + delta > -0.5:
                print(f"  kit{kit}/{note}.oga would clip at {before + delta:+.1f} dBFS — skipped")
                continue

            apply_gain(path, delta)
            applied.setdefault(kit, {})[note] = want
            after = peak_dbfs(path)
            print(
                f"  kit{kit}/{note}.oga {GM_DRUMS[note]:14s} {delta:+5.1f} dB  "
                f"{before:+.1f} -> {after:+.1f} dBFS"
            )
            changed += 1

    save_applied(applied)
    print(f"{changed} sample(s) re-levelled; state in {APPLIED}")
    return 0


def repair():
    """Substitute every silent sample on disk. Returns a shell exit code."""
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH (see devenv.nix)")
    silent = audit()
    if not silent:
        print("nothing to repair")
        return 0
    print(f"{len(silent)} silent sample(s) — substituting:")
    report(silent)
    skip = set(silent)
    for kit, note in silent:
        used = substitute(kit, note, skip)
        print(f"  kit{kit}/{note}.oga <- {used or 'NOTHING (no fallback worked)'}")
    return run_audit()


# --- entry points ----------------------------------------------------------


def run_audit():
    """Print the silence audit. Returns a shell exit code."""
    silent = audit()
    total = NUM_KITS * len(NOTES)
    if not silent:
        print(f"all {total} drum samples have audio")
        return 0
    print(f"{len(silent)} of {total} drum samples are silent:")
    report(silent)
    return 1


def main():
    if not os.path.exists(SF2):
        sys.exit(f"SoundFont not found: {SF2}")
    for tool in ("fluidsynth", "ffmpeg"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH (see devenv.nix)")
    os.makedirs(TMP, exist_ok=True)

    kits = []
    for k in range(NUM_KITS):
        os.makedirs(kit_dir(k + 1), exist_ok=True)
        for note in NOTES:
            render(k, note, sample_path(k + 1, note))
        kits.append({"id": k + 1, "name": f"Perfect Drums {k + 1}"})
        print(f"rendered kit {k + 1}/{NUM_KITS}")

    # Second pass: notes with no zone in the SoundFont rendered as silence.
    # Substituting needs every kit already on disk (a stand-in may come from
    # another kit), so it can't happen inside the loop above.
    still_silent = repair()

    # Third pass: a fresh render carries no trims, so bake them from scratch.
    print("baking level trims:")
    level(reset=True)

    manifest = {
        "kits": kits,
        "drums": [{"note": n, "name": GM_DRUMS[n]} for n in NOTES],
    }
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {os.path.join(OUT, 'manifest.json')}")

    # Never ship silence again without saying so.
    if still_silent:
        sys.exit("still silent after substitution — extend FALLBACKS")


if __name__ == "__main__":
    flags = sys.argv[1:]
    if "--audit" in flags:
        sys.exit(run_audit())
    elif "--repair" in flags:
        sys.exit(repair())
    elif "--level" in flags:
        sys.exit(level())
    main()
