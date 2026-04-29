"""visualisering — generic, domain-agnostic pattern infrastructure.

Pure-Python primitives for parametric textile patterns:
- Pattern / Section / Step (structured intermediate)
- Stitch / Row / RowValidator (domain-agnostic stitch bookkeeping)
- Gauge conversion + rounding
- Shaping (even spacing / Bresenham)
- SVG schematic helpers
- HTML / Paged.js renderer

Domain-specific stitch dictionaries (knit, crochet, …) live in their
respective skills (`skills/strikning/knitlib/stitches.py`,
`skills/hækling/croclib/stitches.py`).
"""

from .gauge import Gauge, cm_to_sts, cm_to_rows, round_to_multiple
from .bookkeeping import (
    Stitch, Op, Row, RowValidator, ValidationError, validate_repeat,
)
from .shaping import evenly_spaced, distribute_decreases
from .pattern import Pattern, Section, Step

__all__ = [
    "Gauge",
    "cm_to_sts",
    "cm_to_rows",
    "round_to_multiple",
    "Stitch",
    "Op",
    "Row",
    "RowValidator",
    "ValidationError",
    "validate_repeat",
    "evenly_spaced",
    "distribute_decreases",
    "Pattern",
    "Section",
    "Step",
]
