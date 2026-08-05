"""The shape of the curriculum: stages hold modules, modules hold three lessons.

    Stage    a phase of the journey, with a stated goal
     Module  one technique — always exactly three lessons
      plain    the technique alone, nothing else sounding
      core     the technique in its normal musical form
      stretch  the technique pushed to its hardest useful variation

A lesson's **id is its slug** and never changes. The displayed "2.4" is rendered
from position, so inserting a lesson never renumbers a file, orphans a student's
practice history, or resets a remembered tempo.

A module slot that has not been written yet is a `planned()` entry: it occupies
its number and shows up in the catalogue as the road ahead, but produces no MIDI
and no playable lesson. That is what keeps `plain / core / stretch` honest while
a stage is still being filled in.
"""

TIERS = ("plain", "core", "stretch")


def lesson(
    slug,
    name,
    tier,
    drums,
    bass,
    summary,
    description,
    hints,
    bpm=60,
    bars=4,
    prereq=(),
):
    """One playable lesson. `drums` and `bass` are builders taking a bar count."""
    if tier not in TIERS:
        raise ValueError(f"{slug}: unknown tier {tier!r}")
    return {
        "slug": slug,
        "name": name,
        "tier": tier,
        "drums": drums,
        "bass": bass,
        "summary": summary,
        "description": description,
        "hints": list(hints),
        "bpm": bpm,
        "bars": bars,
        "prereq": list(prereq),
        "planned": False,
    }


def checkpoint(slug, name, drums, bass, summary, description, hints, bpm=60, bars=4):
    """A stage's closing lesson: one bar of each pattern from that stage.

    Practising one pattern until it is smooth feels productive and retains
    poorly; interleaving competing patterns feels worse and retains far better.
    A checkpoint belongs to its stage, not to a module — it is where the stage
    is actually passed.
    """
    entry = lesson(
        slug, name, "stretch", drums, bass, summary, description, hints, bpm, bars
    )
    entry["tier"] = "checkpoint"
    return entry


def planned(slug, name, tier):
    """A slot that is designed but not written. Holds its number, plays nothing."""
    if tier not in TIERS:
        raise ValueError(f"{slug}: unknown tier {tier!r}")
    return {"slug": slug, "name": name, "tier": tier, "planned": True}


def module(slug, title, subtitle, lessons):
    tiers = [entry["tier"] for entry in lessons]
    if tiers != list(TIERS):
        raise ValueError(f"{slug}: modules are plain/core/stretch, got {tiers}")
    return {"slug": slug, "title": title, "subtitle": subtitle, "lessons": lessons}


def stage(number, slug, title, goal, modules, closing=None):
    return {
        "number": number,
        "slug": slug,
        "title": title,
        "goal": goal,
        "modules": modules,
        "closing": closing,  # the checkpoint, or None while a stage is unwritten
    }
