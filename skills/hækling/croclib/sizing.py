"""Body-measurements helpers for the crochet skill.

Children's tables are shared with the knitting skill via
:mod:`lib.visualisering.sizing` — see that module for the source data.

We re-export the children's helpers here so crochet patterns can pull
auto-fill defaults (head, chest, foot, sleeve) from a single place. For
amigurumi-figurer the relevant scale isn't a body measurement at all
(target finished height); but children-sized hats, scarves, slippers and
cardigans benefit from the same age-band defaults as their knitted
counterparts.
"""

from __future__ import annotations

from lib.visualisering.sizing import (
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
    "CHILD_SIZES",
    "ChildSize",
    "child_size",
    "head_for_age",
    "chest_for_age",
    "foot_for_age",
    "sleeve_for_age",
    "known_age_labels",
]
