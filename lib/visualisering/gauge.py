"""Gauge conversion and rounding.

Gauge is *the* foundational input. Every dimension in cm becomes a stitch or
row count via these conversions. Always round stitch counts to the multiple
required by the stitch pattern (e.g. multiple of 4 for 2x2 rib).
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Gauge:
    """Knitting gauge measured over 10 cm of stockinette (or specified pattern).

    Attributes:
        sts_per_10cm: stitches per 10 cm width
        rows_per_10cm: rows per 10 cm height
        pattern: optional name of the stitch pattern this gauge was measured in
    """
    sts_per_10cm: float
    rows_per_10cm: float
    pattern: str = "glatstrik"

    def __post_init__(self) -> None:
        if self.sts_per_10cm <= 0 or self.rows_per_10cm <= 0:
            raise ValueError("Gauge values must be positive")


def round_to_multiple(value: float, multiple: int, *, mode: str = "nearest") -> int:
    """Round value to a multiple.

    mode = "nearest" | "up" | "down". Defaults to nearest. Use "up" for cast-on
    where you'd rather have a touch more ease than a too-tight result.
    """
    if multiple < 1:
        raise ValueError("multiple must be >= 1")
    q = value / multiple
    if mode == "nearest":
        return int(round(q)) * multiple
    if mode == "up":
        from math import ceil
        return int(ceil(q)) * multiple
    if mode == "down":
        from math import floor
        return int(floor(q)) * multiple
    raise ValueError(f"unknown rounding mode: {mode}")


def cm_to_sts(cm: float, gauge: Gauge, multiple: int = 1, mode: str = "nearest") -> int:
    """Convert a width in cm to a stitch count, rounded to a pattern multiple."""
    raw = cm * gauge.sts_per_10cm / 10.0
    return round_to_multiple(raw, multiple, mode=mode)


def cm_to_rows(cm: float, gauge: Gauge, multiple: int = 1, mode: str = "nearest") -> int:
    """Convert a height in cm to a row count, rounded if needed.

    For most uses (knit until X cm), multiple=1 is fine — the knitter just
    measures. For things that must align with a stitch repeat (stripe heights,
    crown setup) use a multiple.
    """
    raw = cm * gauge.rows_per_10cm / 10.0
    return round_to_multiple(raw, multiple, mode=mode)


def sts_to_cm(sts: int, gauge: Gauge) -> float:
    return sts * 10.0 / gauge.sts_per_10cm


def rows_to_cm(rows: int, gauge: Gauge) -> float:
    return rows * 10.0 / gauge.rows_per_10cm
