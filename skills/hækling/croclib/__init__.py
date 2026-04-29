"""croclib — crochet-specific layer of the hækling skill.

Generic, domain-agnostic primitives (Pattern, Stitch, Row, Gauge, shaping,
SVG, HTML) live in :mod:`lib.visualisering`. This package re-exports what
the constructions need plus the crochet-only stitch dictionary.

The contract: math and validation lives here as pure Python.
LLMs format the structured output into prose patterns.
Never let an LLM compute stitch counts directly — same rule as knit.
"""

from lib.visualisering import (
    Gauge, cm_to_sts, cm_to_rows, round_to_multiple,
    Stitch, Op, RowValidator, ValidationError,
    Pattern, Section, Step,
)

from .crorow import CrochetRow

# Backwards/forwards-compatible alias: callers can use ``Row`` for the
# crochet-aware row, mirroring the strikning convention.
Row = CrochetRow

from .stitches import (
    ALIASES, CroStitch, STITCHES, magic_ring, stitch,
)

__all__ = [
    # generic re-exports
    "Gauge", "cm_to_sts", "cm_to_rows", "round_to_multiple",
    "Stitch", "Op", "RowValidator", "ValidationError",
    "Pattern", "Section", "Step",
    # crochet-only
    "CrochetRow", "Row",
    "ALIASES", "CroStitch", "STITCHES",
    "magic_ring", "stitch",
]
