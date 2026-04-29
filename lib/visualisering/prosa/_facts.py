"""Fact extraction for prose templates.

``_facts(pattern, lang)`` walks the pattern's metadata and produces a flat
dict of strings that the per-construction sentence templates fill via
``str.format(**facts)``. Missing values render as ``"—"`` so unfilled
template slots don't crash the formatter; the caller prunes such
paragraphs out before joining.
"""

from __future__ import annotations

from typing import Any

from ..pattern import Pattern
from ..lang import t


def _fmt_cm(v: Any) -> str:
    """Format a length-in-cm into a short human-readable string."""
    if v is None:
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if f == int(f):
        return f"{int(f)}"
    return f"{f:.0f}"


def _facts(p: Pattern, lang: str) -> dict[str, Any]:
    """Compute the fill-fields used by templates. Always returns strings."""
    inputs = p.inputs or {}
    g = inputs.get("gauge", {}) or {}
    sts10 = int(g.get("sts_per_10cm", 0))
    rows10 = int(g.get("rows_per_10cm", 0))
    construction_label = t(f"construction.{p.construction}", lang) or p.construction

    # total stitch count
    sts_total = 0
    if p.sections:
        sts_total = max((s.sts_after for s in p.sections), default=0)
        if not sts_total:
            sts_total = max((s.sts_before for s in p.sections), default=0)

    if lang == "en":
        gauge_summary = f"{sts10} sts × {rows10} rows / 10 cm"
    else:
        gauge_summary = f"{sts10} m × {rows10} p / 10 cm"

    # Rough meters estimation: per stitch, an extra-conservative 0.07 m
    # for crochet (denser) and 0.04 m for knit. We don't know the section
    # row count exactly here, so we treat sts_total as a proxy multiplied
    # by the row gauge ratio. Skills that compute precise yardage can
    # provide ``inputs["estimated_meters"]`` to override.
    if "estimated_meters" in inputs:
        meters = int(inputs["estimated_meters"])
    else:
        domain = inputs.get("_domain", "knit")
        per_st = 0.07 if domain == "crochet" else 0.04
        # estimate total stitches across all sections
        all_sts = sum(s.sts_after * max(1, len(s.steps)) for s in p.sections)
        if not all_sts:
            all_sts = sts_total * 100  # very rough
        meters = max(50, int(all_sts * per_st))
    balls = max(1, round(meters / 175))

    ease_cm = inputs.get("ease_cm")
    if ease_cm is None:
        ease_note = "moderat ease" if lang == "da" else "moderate ease"
    elif ease_cm == 0:
        ease_note = "0 cm ease"
    elif ease_cm > 0:
        ease_note = (f"+{ease_cm:.0f} cm positiv ease" if lang == "da"
                     else f"+{ease_cm:.0f} cm positive ease")
    else:
        ease_note = (f"{ease_cm:.0f} cm negativ ease" if lang == "da"
                     else f"{ease_cm:.0f} cm negative ease")

    diff = (p.difficulty or "").strip()
    if diff:
        difficulty_label = t(f"difficulty.{diff}", lang)
    else:
        difficulty_label = "ukendt" if lang == "da" else "unknown"

    return {
        "construction_label": construction_label,
        "stitch_count_total": sts_total,
        "sts_total": sts_total,
        "gauge_summary": gauge_summary,
        "meters": meters,
        "balls": balls,
        "ease_note": ease_note,
        "difficulty_label": difficulty_label,
        "head_cm": _fmt_cm(inputs.get("head_circumference_cm")),
        "finished_circ": _fmt_cm(inputs.get("finished_circumference_cm")),
        "height": _fmt_cm(inputs.get("total_height_cm")
                         or inputs.get("height_cm")),
        "rib_height": _fmt_cm(inputs.get("rib_height_cm")),
        "sectors": inputs.get("sectors", "—"),
        "width": _fmt_cm(inputs.get("width_cm")),
        "length": _fmt_cm(inputs.get("length_cm")),
        "pattern": inputs.get("pattern", "glatstrik" if lang == "da" else "stockinette"),
        "bust": _fmt_cm(inputs.get("finished_bust_cm")),
        "body_length": _fmt_cm(inputs.get("body_length_cm")),
        "sleeve_length": _fmt_cm(inputs.get("sleeve_length_cm")),
        "upper_arm": _fmt_cm(inputs.get("upper_arm_cm")),
        "foot_length": _fmt_cm(inputs.get("foot_length_cm")),
        "foot_circ": _fmt_cm(inputs.get("foot_circ_cm")),
        "yoke_depth": _fmt_cm(inputs.get("yoke_depth_cm")
                              or inputs.get("yoke_depth")),
        "doublings": inputs.get("n_doublings", "—"),
        "increase_rows": inputs.get("increase_rows", "—"),
        "actual_diameter": _fmt_cm(inputs.get("actual_diameter_cm")
                                   or inputs.get("diameter_cm")),
        "rounds": inputs.get("rounds")
                  or (inputs.get("n_max", 0) * 2 - 1 if inputs.get("n_max") else "—"),
        "tube_rounds": inputs.get("tube_rounds", "—"),
        "scale": _fmt_cm(inputs.get("scale_cm")),
        "actual_side": _fmt_cm(inputs.get("actual_side_cm")
                               or inputs.get("side_cm")),
        "stitch_type": inputs.get("stitch_type", "dc"),
        "width_cells": inputs.get("width_cells", "—"),
        "height_cells": inputs.get("height_cells", "—"),
        "width_blocks": inputs.get("blocks_wide", "—"),
        "height_blocks": inputs.get("blocks_high", "—"),
        "repeat_width": inputs.get("repeat_width", inputs.get("repeat", "—")),
    }
