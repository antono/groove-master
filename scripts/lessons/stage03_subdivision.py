"""Stage 3 — Subdivision & the grid.

Designed, not written. Every slot is a `planned()` entry: it holds its number
and shows in the catalogue as the road ahead, so the numbering of Stage 4 does
not shift when these are filled in.
"""

from .schema import module, planned, stage

STAGE = stage(
    number=3,
    slug="subdivision",
    title="Subdivision & the Grid",
    goal="The 16th grid and the triplet grid, and a note placed anywhere on "
    "either.",
    modules=[
        module(
            "sixteenths",
            "Sixteenths",
            "twice as fine",
            [
                planned("hats-16ths-split", "16ths, Split Hands", "plain"),
                planned("rock-16th-hats", "Rock Beat, 16th Hats", "core"),
                planned("kick-16th-grid", 'Kick on the "e" and the "a"', "stretch"),
            ],
        ),
        module(
            "triplets",
            "Triplets",
            "three where there were two",
            [
                planned("triplets-8th", "8th-Note Triplets", "plain"),
                planned("triplet-groove", "Triplet Groove", "core"),
                planned("triplets-broken", "Broken Triplets", "stretch"),
            ],
        ),
        module(
            "feel",
            "Feel",
            "straight and swung",
            [
                planned("shuffle-hats", "Shuffle Hats", "plain"),
                planned("shuffle-groove", "The Shuffle", "core"),
                planned("half-time-shuffle", "Half-Time Shuffle", "stretch"),
            ],
        ),
    ],
)
