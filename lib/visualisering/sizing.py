"""Shared body-measurements (children).

Numbers are in cm and represent population averages drawn from
publicly-available pattern-grading tables (Craft Yarn Council "Children",
PetiteKnit children's-sizing chart, Drops Design baby/børnestørrelser).
They're a reasonable starting point, **not** a guarantee — always offer
the user the option to override with their own measurements.

Both the strik (knit) and hækl (crochet) skills consume this module so
that auto-fill helpers behave identically across the two domains.
"""

from __future__ import annotations

from typing import TypedDict


class ChildSize(TypedDict):
    """Per-age-band body measurements in cm."""
    head_circumference_cm: float
    chest_cm: float
    foot_length_cm: float
    sleeve_length_cm: float


# Age-band labels are the canonical strings users pass on the CLI.
# Short labels (3-6M, 1-2y, …) are intentionally simple; aliases are
# resolved by :func:`child_size`.
CHILD_SIZES: dict[str, ChildSize] = {
    "0-3M": {
        "head_circumference_cm": 38.0,
        "chest_cm": 41.0,
        "foot_length_cm": 9.0,
        "sleeve_length_cm": 16.0,
    },
    "3-6M": {
        "head_circumference_cm": 41.0,
        "chest_cm": 43.0,
        "foot_length_cm": 10.0,
        "sleeve_length_cm": 18.0,
    },
    "6-12M": {
        "head_circumference_cm": 44.0,
        "chest_cm": 46.0,
        "foot_length_cm": 11.5,
        "sleeve_length_cm": 20.0,
    },
    "1-2y": {
        "head_circumference_cm": 47.0,
        "chest_cm": 49.0,
        "foot_length_cm": 13.0,
        "sleeve_length_cm": 23.0,
    },
    "2-4y": {
        "head_circumference_cm": 49.0,
        "chest_cm": 53.0,
        "foot_length_cm": 15.0,
        "sleeve_length_cm": 27.0,
    },
    "4-6y": {
        "head_circumference_cm": 51.0,
        "chest_cm": 57.0,
        "foot_length_cm": 17.0,
        "sleeve_length_cm": 30.0,
    },
    "6-8y": {
        "head_circumference_cm": 52.0,
        "chest_cm": 62.0,
        "foot_length_cm": 19.0,
        "sleeve_length_cm": 33.0,
    },
    "8-10y": {
        "head_circumference_cm": 53.0,
        "chest_cm": 67.0,
        "foot_length_cm": 21.0,
        "sleeve_length_cm": 36.0,
    },
    "10-12y": {
        "head_circumference_cm": 54.0,
        "chest_cm": 72.0,
        "foot_length_cm": 22.5,
        "sleeve_length_cm": 39.0,
    },
}


# Common alternative spellings users may pass.
_ALIASES: dict[str, str] = {
    "0-3m": "0-3M",
    "3-6m": "3-6M",
    "6-12m": "6-12M",
    "0_3M": "0-3M",
    "3_6M": "3-6M",
    "6_12M": "6-12M",
    "1_2y": "1-2y",
    "2_4y": "2-4y",
    "4_6y": "4-6y",
    "6_8y": "6-8y",
    "8_10y": "8-10y",
    "10_12y": "10-12y",
    "1-2Y": "1-2y",
    "2-4Y": "2-4y",
    "4-6Y": "4-6y",
    "6-8Y": "6-8y",
    "8-10Y": "8-10y",
    "10-12Y": "10-12y",
    "newborn": "0-3M",
    "baby": "6-12M",
    "toddler": "1-2y",
}


def _normalize(age_label: str) -> str:
    """Resolve an age-band label, raising ``ValueError`` if unknown."""
    if age_label in CHILD_SIZES:
        return age_label
    if age_label in _ALIASES:
        return _ALIASES[age_label]
    # Try a case-insensitive match against canonical keys.
    lower = age_label.lower()
    for key in CHILD_SIZES:
        if key.lower() == lower:
            return key
    raise ValueError(
        f"unknown age-band {age_label!r}. "
        f"Known: {', '.join(CHILD_SIZES.keys())}."
    )


def child_size(age_label: str) -> ChildSize:
    """Return the full measurements dict for ``age_label``.

    Raises :class:`ValueError` if the label isn't recognised. Aliases like
    ``"newborn"`` or ``"6-12m"`` are accepted.
    """
    return CHILD_SIZES[_normalize(age_label)]


def head_for_age(age_label: str) -> float:
    """Head circumference in cm for ``age_label``."""
    return child_size(age_label)["head_circumference_cm"]


def chest_for_age(age_label: str) -> float:
    """Chest circumference in cm for ``age_label``."""
    return child_size(age_label)["chest_cm"]


def foot_for_age(age_label: str) -> float:
    """Foot length (heel-to-toe) in cm for ``age_label``."""
    return child_size(age_label)["foot_length_cm"]


def sleeve_for_age(age_label: str) -> float:
    """Sleeve length (underarm to wrist) in cm for ``age_label``."""
    return child_size(age_label)["sleeve_length_cm"]


def known_age_labels() -> list[str]:
    """Canonical (non-alias) age-band labels in chronological order."""
    return list(CHILD_SIZES.keys())


__all__ = [
    "CHILD_SIZES",
    "ChildSize",
    "child_size",
    "head_for_age",
    "chest_for_age",
    "foot_for_age",
    "sleeve_for_age",
    "known_age_labels",
]
