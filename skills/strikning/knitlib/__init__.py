"""knitlib — knit-specific layer of the strikning skill.

Generic, domain-agnostic primitives (Pattern, Stitch, Row, Gauge, shaping,
SVG, HTML) live in `lib.visualisering`. This package re-exports what the
constructions need plus the knit-only stitch dictionary, ease tables and
sizing tables.

The contract: math and validation lives here as pure Python.
LLMs format the structured output into prose patterns.
Never let an LLM compute stitch counts directly.
"""

from lib.visualisering import (
    Gauge, cm_to_sts, cm_to_rows, round_to_multiple,
    Stitch, Op, RowValidator, ValidationError,
    evenly_spaced, distribute_decreases,
    Pattern, Section, Step,
)

from .knitrow import KnitRow
# Backwards-compatible alias: `Row` from this package is the knit-aware Row
# so existing code (and tests) calling `Row(...).k(...)` keep working.
Row = KnitRow

from .stitches import STITCHES, stitch
from .ease import EASE_GUIDE, recommended_ease
from .sizing import BUST_CIRCUMFERENCE_CM, HEAD_CIRCUMFERENCE_CM


# Mark patterns generated through this package as the knit domain so the
# shared HTML renderer can pick the right defaults (see
# lib/visualisering/html.py::register_domain_renderer).
def _mark_knit(pattern: Pattern) -> Pattern:
    pattern.inputs.setdefault("_domain", "knit")
    return pattern

__all__ = [
    "Gauge",
    "cm_to_sts",
    "cm_to_rows",
    "round_to_multiple",
    "Stitch",
    "Op",
    "Row",
    "KnitRow",
    "RowValidator",
    "ValidationError",
    "evenly_spaced",
    "distribute_decreases",
    "Pattern",
    "Section",
    "Step",
    "STITCHES",
    "stitch",
    "EASE_GUIDE",
    "recommended_ease",
    "BUST_CIRCUMFERENCE_CM",
    "HEAD_CIRCUMFERENCE_CM",
]
