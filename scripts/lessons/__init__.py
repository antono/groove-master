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
