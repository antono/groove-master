"""The curriculum: one module per stage, in the order the catalogue lists them.

Adding a stage means adding a file here and one line below. Nothing else in the
tree knows how many stages there are.

See LESSONS.md for the lesson-by-lesson index and docs/curriculum.md for why the
order is what it is.
"""

from . import (
    stage01_pulse,
    stage02_backbeat,
    stage03_space,
    stage04_cymbals,
    stage05_two_bars,
    stage06_subdivision,
    stage07_sticking,
    stage10_form,
    stage11_radio,
    stage12_dancefloor,
)

# Stages 8 and 9 (Syncopation, Dynamics) are designed but unwritten — see
# docs/curriculum.md §6 — so the list jumps from 7 to 10. Stage numbers are
# stable, not positional: writing 8 later inserts it without renaming anything.
CURRICULUM = [
    stage01_pulse.STAGE,
    stage02_backbeat.STAGE,
    stage03_space.STAGE,
    stage04_cymbals.STAGE,
    stage05_two_bars.STAGE,
    stage06_subdivision.STAGE,
    stage07_sticking.STAGE,
    stage10_form.STAGE,
    stage11_radio.STAGE,
    stage12_dancefloor.STAGE,
]

# The journey's top level. Stages group into four tiers, each answering one
# question a student can feel — the orienting text the catalogue shows above a
# tier. Membership is declared here rather than inferred from which stages
# exist, so a tier whose stages are not written yet still renders as the road
# ahead. See docs/curriculum.md §6. ("tier" here is the journey level; a lesson's
# own `tier` field — plain/core/stretch — is a different, narrower thing.)
TIERS = [
    {
        "slug": "foundations",
        "name": "Foundations",
        "question": "Can you keep time and stack two hands?",
        "stages": [0, 1, 2, 3, 4, 5],
    },
    {
        "slug": "vocabulary",
        "name": "Vocabulary",
        "question": "Do you have hands, and things to say with them?",
        "stages": [6, 7, 8, 9],
    },
    {
        "slug": "music",
        "name": "Music",
        "question": "Can you play something someone wants to hear?",
        "stages": [10, 11, 12],
    },
    {
        "slug": "mastery",
        "name": "Mastery",
        "question": "Can you make it your own?",
        "stages": [13, 14],
    },
]
