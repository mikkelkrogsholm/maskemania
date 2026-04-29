"""Standard body measurements.

Numbers are in cm. Source: Craft Yarn Council Women's Standard Body
Measurements / Sizing (the most widely cited reference for hand-knit
patterns). For children/babies the same source is used. Always offer the
user the option to override with their own measurements — these are
population averages, not guarantees.
"""

from __future__ import annotations

# Women's bust circumference in cm. CYC standard.
BUST_CIRCUMFERENCE_CM: dict[str, float] = {
    "XS":  78,
    "S":   86,
    "M":   94,
    "L":  104,
    "XL": 114,
    "2XL":124,
    "3XL":134,
    "4XL":144,
    "5XL":154,
}

# Men's chest circumference in cm. CYC standard (slightly different intervals).
MENS_CHEST_CIRCUMFERENCE_CM: dict[str, float] = {
    "S":   91,
    "M":  102,
    "L":  112,
    "XL": 122,
    "2XL":132,
    "3XL":142,
}

# Head circumference. CYC standard.
HEAD_CIRCUMFERENCE_CM: dict[str, float] = {
    "preemie":   28,
    "newborn":   33,
    "baby_3_6m": 38,
    "baby_6_12m":43,
    "toddler":   46,
    "child":     50,
    "teen":      53,
    "adult_S":   55,
    "adult_M":   56,
    "adult_L":   58,
    "adult_XL":  60,
}

# Typical sleeve-cuff circumference (wrist allowance) in cm by adult size.
WRIST_CIRCUMFERENCE_CM: dict[str, float] = {
    "XS": 14, "S": 15, "M": 16, "L": 17, "XL": 18, "2XL": 19,
}

# Typical upper-arm circumference (bicep) in cm by adult size — used to
# decide when to stop sleeve-decreases on a top-down raglan, and how many
# stitches to bind off at the underarm.
UPPER_ARM_CIRCUMFERENCE_CM: dict[str, float] = {
    "XS": 26, "S": 28, "M": 31, "L": 34, "XL": 37, "2XL": 41,
}

# Approximate body length (from underarm to hem, classic-fit sweater).
BODY_LENGTH_CM: dict[str, float] = {
    "XS": 35, "S": 36, "M": 37, "L": 38, "XL": 39, "2XL": 40,
}

# Yoke depth (raglan depth from neck to underarm) for top-down raglan.
# Rule of thumb: about 1/4 of bust circumference, but capped to a comfortable
# range. Numbers below are typical for adult women.
YOKE_DEPTH_CM: dict[str, float] = {
    "XS": 19, "S": 20, "M": 21, "L": 22, "XL": 23, "2XL": 24,
}


# ---------------------------------------------------------------------------
# Children's sizing (re-exported from lib.visualisering.sizing so both the
# strik and the hækl skill share a single source of truth).
# ---------------------------------------------------------------------------
from lib.visualisering.sizing import (  # noqa: E402  (deliberate late import)
    CHILD_SIZES,
    ChildSize,
    child_size,
    head_for_age,
    chest_for_age,
    foot_for_age,
    sleeve_for_age,
    known_age_labels,
)

__all__ = [
    "BUST_CIRCUMFERENCE_CM",
    "MENS_CHEST_CIRCUMFERENCE_CM",
    "HEAD_CIRCUMFERENCE_CM",
    "WRIST_CIRCUMFERENCE_CM",
    "UPPER_ARM_CIRCUMFERENCE_CM",
    "BODY_LENGTH_CM",
    "YOKE_DEPTH_CM",
    "CHILD_SIZES",
    "ChildSize",
    "child_size",
    "head_for_age",
    "chest_for_age",
    "foot_for_age",
    "sleeve_for_age",
    "known_age_labels",
]
