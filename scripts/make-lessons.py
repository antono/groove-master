#!/usr/bin/env python3
"""Generate the lesson MIDIs and static/lessons/manifest.json.

The curriculum lives in `scripts/lessons/` — one Python module per stage, each
exporting a `STAGE` built from `lessons/schema.py`. This file is only the
driver: it walks that structure, numbers it, writes a format-1 MIDI per playable
lesson, and emits the manifest the app reads.

Layout on disk:

    static/lessons/
      manifest.json
      stage-01-pulse/kick-quarters.mid
      stage-02-backbeat/backbeat-plain.mid

Filenames carry the **slug only** — never a number. Order lives in the manifest
and nowhere else, so inserting a lesson is a one-line change instead of a rename
cascade, and a lesson that moves stages keeps its id, its practice history and
its remembered tempo.

Track roles are chosen by the track name:
  - "drums"        -> playable: shown on the highway and scored.
  - "family:id"    -> backing:  auto-played from static/<family>/<id>/<note>.oga
                      (e.g. "bass:lately"), never shown or scored.
  - "count-in"     -> the stick count that leads the student in; audible but
                      never shown or scored (see COUNT-IN RULE below).

COUNT-IN RULE: every lesson must have three stick clicks before it starts, on
the last three beats of the lead-in bar. Nothing clicks on the pattern's first
beat — that one is the student's. build_lesson() adds the track to every lesson
automatically, so a new entry gets it for free — do not hand-roll one per
lesson, and do not remove it.

Re-run after adding or editing a lesson:
  python3 scripts/make-lessons.py
"""

import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lessons import CURRICULUM  # noqa: E402
from lessons.midi import (  # noqa: E402
    build_track,
    count_in_sticks,
    write_midi,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "lessons")


PRINT_WIDTH = 80  # prettier's default


def render(value, indent=0):
    """JSON the way prettier writes it, so regenerating is never a diff.

    `json.dump(indent=2)` explodes every array onto its own lines; prettier
    keeps one on a single line when it fits inside the print width, so the two
    disagree on `"prereq": ["kick-quarters"]` and the pre-commit hook rewrites
    the file every run. Objects always expand — prettier does not join them
    back up — so only arrays need the width test.
    """
    pad = " " * indent
    inner = " " * (indent + 2)
    if isinstance(value, dict):
        if not value:
            return "{}"
        items = [
            f"{inner}{json.dumps(k, ensure_ascii=False)}: {render(v, indent + 2)}"
            for k, v in value.items()
        ]
        return "{\n" + ",\n".join(items) + f"\n{pad}}}"
    if isinstance(value, list):
        if not value:
            return "[]"
        flat = "[" + ", ".join(render(v) for v in value) + "]"
        if "\n" not in flat and indent + len(flat) <= PRINT_WIDTH:
            return flat
        items = [f"{inner}{render(v, indent + 2)}" for v in value]
        return "[\n" + ",\n".join(items) + f"\n{pad}]"
    return json.dumps(value, ensure_ascii=False)


def stage_dir(stage):
    return f"stage-{stage['number']:02d}-{stage['slug']}"


def build_lesson(lesson, out_dir, rel_dir):
    """Write one lesson's MIDI and return the fields derived from it."""
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

    write_midi(os.path.join(out_dir, f"{lesson['slug']}.mid"), tracks)
    return f"{rel_dir}/{lesson['slug']}.mid"


def walk():
    """Yield every declared slot in curriculum order, numbered.

    A stage's lessons are numbered straight through it — modules are headings,
    not numbers — so a student says "2.4", never "2.2.1".
    """
    for stage in CURRICULUM:
        position = 0
        for mod in stage["modules"]:
            for entry in mod["lessons"]:
                position += 1
                yield stage, mod, entry, f"{stage['number']}.{position}"
        if stage.get("closing"):
            yield stage, None, stage["closing"], f"{stage['number']}.◆"


def check(entries):
    """Fail loudly on the two mistakes that are easy to make and hard to see."""
    slugs = [e["slug"] for _s, _m, e, _n in entries]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        raise SystemExit(f"duplicate lesson slugs: {sorted(dupes)}")
    known = set(slugs)
    for _stage, _mod, entry, number in entries:
        missing = [p for p in entry.get("prereq", []) if p not in known]
        if missing:
            raise SystemExit(f"{number} {entry['slug']}: unknown prereq {missing}")


def main():
    entries = list(walk())
    check(entries)

    # A stale MIDI from a renamed lesson would keep being served, so the tree is
    # rebuilt rather than written over.
    for name in os.listdir(OUT) if os.path.isdir(OUT) else []:
        path = os.path.join(OUT, name)
        if os.path.isdir(path) and name.startswith("stage-"):
            shutil.rmtree(path)
        elif name.endswith(".mid"):
            os.remove(path)

    lessons = []
    for stage, mod, entry, number in entries:
        if entry.get("planned"):
            continue
        rel_dir = stage_dir(stage)
        out_dir = os.path.join(OUT, rel_dir)
        os.makedirs(out_dir, exist_ok=True)
        lessons.append(
            {
                "id": entry["slug"],
                "number": number,
                "name": entry["name"],
                "file": build_lesson(entry, out_dir, rel_dir),
                "stage": stage["slug"],
                "module": mod["slug"] if mod else None,
                "tier": entry["tier"],
                "bpm": entry["bpm"],
                "bars": entry["bars"],
                "prereq": entry["prereq"],
                "summary": entry["summary"],
                "description": entry["description"],
                "hints": entry["hints"],
            }
        )

    # The outline the catalogue renders its headings from, planned slots
    # included: a student should be able to see the road ahead, greyed out.
    numbers = {e["slug"]: n for _s, _m, e, n in entries}
    stages = [
        {
            "slug": stage["slug"],
            "number": stage["number"],
            "title": stage["title"],
            "goal": stage["goal"],
            "modules": [
                {
                    "slug": mod["slug"],
                    "title": mod["title"],
                    "subtitle": mod["subtitle"],
                    "lessons": [
                        {
                            "id": e["slug"],
                            "number": numbers[e["slug"]],
                            "name": e["name"],
                            "tier": e["tier"],
                            "planned": bool(e.get("planned")),
                        }
                        for e in mod["lessons"]
                    ],
                }
                for mod in stage["modules"]
            ],
            "closing": (
                {
                    "id": stage["closing"]["slug"],
                    "number": numbers[stage["closing"]["slug"]],
                    "name": stage["closing"]["name"],
                    "tier": "checkpoint",
                    "planned": False,
                }
                if stage.get("closing")
                else None
            ),
        }
        for stage in CURRICULUM
    ]

    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        f.write(render({"stages": stages, "lessons": lessons}) + "\n")

    planned = sum(1 for _s, _m, e, _n in entries if e.get("planned"))
    print(f"wrote {len(lessons)} lesson(s) ({planned} planned) to {OUT}")


if __name__ == "__main__":
    main()
