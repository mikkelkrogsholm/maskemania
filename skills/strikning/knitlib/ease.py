"""Ease guidance per garment type.

Ease = (finished circumference) − (body circumference). Negative ease means
snug fit; positive ease means loose. These values reflect mainstream Western
hand-knit conventions; designers vary, and Japanese and Scandinavian fashion
trends differ. Always treat as starting points, never absolutes.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class EaseRange:
    min_cm: float
    max_cm: float
    note: str = ""

    @property
    def midpoint(self) -> float:
        return (self.min_cm + self.max_cm) / 2


# Bust/chest ease for sweaters and cardigans, by fit style.
SWEATER_EASE = {
    "very_close":  EaseRange(-10, -5, "stretchy yarn / ribbed fabric required"),
    "close":       EaseRange(-5,   0, "fitted"),
    "standard":    EaseRange(0,    5, "classic relaxed sweater"),
    "loose":       EaseRange(5,   10, "casual oversized"),
    "oversized":   EaseRange(10,  20, "drop-shoulder, very loose"),
    "very_oversized": EaseRange(20, 35, "blanket-cardigan territory"),
}

# Hat ease — almost always negative so it stays on.
HAT_EASE = EaseRange(-5, -2, "snug; ribbed brim grips the head")

# Sock ease (for completeness, not yet supported in constructions).
SOCK_EASE = EaseRange(-2, -1, "negative around foot for fit")

EASE_GUIDE: dict[str, EaseRange | dict[str, EaseRange]] = {
    "sweater": SWEATER_EASE,
    "cardigan": SWEATER_EASE,
    "hat": HAT_EASE,
    "sock": SOCK_EASE,
}


def recommended_ease(garment: str, fit: str = "standard") -> EaseRange:
    """Look up an ease range. `fit` is ignored for hats/socks."""
    g = garment.lower()
    if g not in EASE_GUIDE:
        raise KeyError(f"unknown garment type: {garment}")
    entry = EASE_GUIDE[g]
    if isinstance(entry, EaseRange):
        return entry
    if fit not in entry:
        raise KeyError(
            f"unknown fit '{fit}' for {garment}. Options: {list(entry)}"
        )
    return entry[fit]
