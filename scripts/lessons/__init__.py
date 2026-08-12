"""The curriculum: one module per stage, in the order the catalogue lists them.

Adding a stage means adding a file here and one line below. Nothing else in the
tree knows how many stages there are.

See LESSONS.md for the lesson-by-lesson index and docs/curriculum.md for why the
order is what it is.
"""

from . import stage01_pulse, stage02_backbeat, stage03_subdivision, stage04_sticking

CURRICULUM = [
    stage01_pulse.STAGE,
    stage02_backbeat.STAGE,
    stage03_subdivision.STAGE,
    stage04_sticking.STAGE,
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
        "stages": [0, 1, 2],
    },
    {
        "slug": "vocabulary",
        "name": "Vocabulary",
        "question": "Do you have hands, and things to say with them?",
        "stages": [3, 4, 5, 6],
    },
    {
        "slug": "music",
        "name": "Music",
        "question": "Can you play something someone wants to hear?",
        "stages": [7, 8],
    },
    {
        "slug": "mastery",
        "name": "Mastery",
        "question": "Can you make it your own?",
        "stages": [9, 10],
    },
]
