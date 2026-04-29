"""Crochet scarf (tørklæde) — flat rectangle in a chosen base stitch.

The simplest possible crochet construction. Choose a base stitch (sc / hdc /
dc / tr) and a target width and length in cm; the generator computes a
foundation chain and a row count, validates per-row stitch balance, and
returns a Pattern.

Stitch heights (very rough, used for row-gauge → cm conversion):

* sc  ~ 1.0 cm at typical worsted gauge
* hdc ~ 1.5 cm
* dc  ~ 2.0 cm
* tr  ~ 2.5 cm

Callers can override ``row_gauge_per_cm`` if they have a real swatch.
"""

from __future__ import annotations

from dataclasses import dataclass

from lib.visualisering import Pattern, RowValidator
from ..crorow import CrochetRow
from ..stitches import stitch as _stitch


# Default *row* gauge (stitches deep per cm) for each base stitch type. These
# are rules of thumb — anyone making a real scarf should swatch first.
_DEFAULT_ROW_GAUGE_PER_CM: dict[str, float] = {
    "sc":  1.0,
    "hdc": 0.7,
    "dc":  0.5,
    "tr":  0.4,
}

# Turning chain heights — number of chains worked at the start of each row
# in US convention (Agent B §1, "turning chain").
_TURNING_CHAINS: dict[str, int] = {
    "sc": 1,
    "hdc": 2,
    "dc": 3,
    "tr": 4,
}


@dataclass
class CrochetTørklædeSpec:
    width_cm: float
    length_cm: float
    gauge_sts_per_cm: float       # stitches per cm in the chosen base stitch
    stitch_type: str = "dc"       # "sc" | "hdc" | "dc" | "tr"
    row_gauge_per_cm: float | None = None  # overrides _DEFAULT_ROW_GAUGE_PER_CM
    name: str = "Hæklet tørklæde"


def _l(da: str, en: str, lang: str) -> str:
    return en if lang == "en" else da


def generate_tørklæde(spec: CrochetTørklædeSpec, lang: str = "da") -> Pattern:
    if spec.width_cm <= 0 or spec.length_cm <= 0:
        raise ValueError("width_cm and length_cm must both be > 0")
    if spec.gauge_sts_per_cm <= 0:
        raise ValueError("gauge_sts_per_cm must be > 0")
    if spec.stitch_type not in _DEFAULT_ROW_GAUGE_PER_CM:
        raise ValueError(
            f"unsupported stitch_type {spec.stitch_type!r}. "
            f"Allowed: {sorted(_DEFAULT_ROW_GAUGE_PER_CM)}."
        )

    # Look up the base stitch — raises if unknown
    _stitch(spec.stitch_type)

    row_gauge = spec.row_gauge_per_cm or _DEFAULT_ROW_GAUGE_PER_CM[spec.stitch_type]
    width_sts = max(1, round(spec.width_cm * spec.gauge_sts_per_cm))
    rows = max(1, round(spec.length_cm * row_gauge))
    turning_ch = _TURNING_CHAINS[spec.stitch_type]

    p = Pattern(
        name=spec.name,
        construction="haekle_tørklæde",
        difficulty="beginner",
        inputs={
            "_domain": "crochet",
            "width_cm": spec.width_cm,
            "length_cm": spec.length_cm,
            "stitch_type": spec.stitch_type,
            "gauge_sts_per_cm": spec.gauge_sts_per_cm,
            "row_gauge_per_cm": row_gauge,
            "width_sts": width_sts,
            "rows": rows,
            "turning_chain": turning_ch,
            # Gauge in "x sts/10 cm × y rows/10 cm" form for the cover-builder
            "gauge": {
                "sts_per_10cm": int(round(spec.gauge_sts_per_cm * 10)),
                "rows_per_10cm": int(round(row_gauge * 10)),
            },
        },
    )

    validator = RowValidator()

    # ----- Foundation chain ----------------------------------------------
    foundation_ch = width_sts + turning_ch
    sec1 = p.add_section(_l("Bundkæde", "Foundation chain", lang),
                         sts_before=0)
    sec1.add(
        _l(f"Hækl {foundation_ch} lm.",
           f"Crochet {foundation_ch} ch.",
           lang),
        sts_after=foundation_ch,
        note=_l(f"{width_sts} bundmasker + {turning_ch} luftmasker som vendekæde",
                f"{width_sts} base sts + {turning_ch} ch as turning chain",
                lang),
    )
    r0 = CrochetRow(sts_before=0, label="bundkæde")
    r0.ch(foundation_ch)
    validator.add(r0)

    # ----- Row 1: turn into the foundation -------------------------------
    sec2 = p.add_section(_l("Række 1", "Row 1", lang),
                         sts_before=foundation_ch)
    r1 = CrochetRow(sts_before=foundation_ch, label="Række 1")
    r1.sl_st(turning_ch)
    r1.op(spec.stitch_type, width_sts)
    validator.add(r1)
    sec2.add(
        _l(f"Hækl 1 {_stitch_name(spec.stitch_type, 'da')} i den "
           f"{turning_ch + 1}. lm fra hægten, "
           f"og 1 {_stitch_name(spec.stitch_type, 'da')} i hver lm til enden.",
           f"Crochet 1 {_stitch_name(spec.stitch_type, 'en')} into the "
           f"{turning_ch + 1}{_ord(turning_ch + 1)} ch from the hook, "
           f"and 1 {_stitch_name(spec.stitch_type, 'en')} into each ch to the end.",
           lang),
        sts_after=width_sts,
        note=_l(f"{width_sts} {_stitch_name(spec.stitch_type, 'da')} i alt",
                f"{width_sts} {_stitch_name(spec.stitch_type, 'en')} total",
                lang),
    )

    # ----- Subsequent rows ------------------------------------------------
    sec3 = p.add_section(_l("Krop", "Body", lang), sts_before=width_sts)
    for i in range(2, rows + 1):
        r = CrochetRow(sts_before=width_sts, label=f"R {i}")
        r.op(spec.stitch_type, width_sts)
        validator.add(r)
    sec3.add(
        _l(f"Vend arbejdet, hækl {turning_ch} lm (vendekæde), spring den "
           f"første lm over og hækl 1 {_stitch_name(spec.stitch_type, 'da')} i hver "
           f"maske til enden.",
           f"Turn the work, crochet {turning_ch} ch (turning chain), skip "
           f"the first ch and crochet 1 {_stitch_name(spec.stitch_type, 'en')} into each "
           f"st to the end.",
           lang),
        sts_after=width_sts,
        note=_l(f"gentag i alt {rows - 1} rækker",
                f"repeat for a total of {rows - 1} rows", lang),
    )

    # ----- Finishing -----------------------------------------------------
    sec4 = p.add_section(_l("Afslutning", "Finishing", lang),
                         sts_before=width_sts)
    sec4.add(
        _l("Klip garnet, træk gennem løkken og hæft alle ender. Damp eller "
           "blok let efter behov.",
           "Cut the yarn, pull through the loop and weave in all ends. Steam "
           "or block lightly as needed.",
           lang),
        sts_after=width_sts,
    )

    # Notes
    actual_w = width_sts / spec.gauge_sts_per_cm
    actual_l = rows / row_gauge
    p.notes.append(
        _l(f"Bredde efter rounding: {width_sts} m × 1/{spec.gauge_sts_per_cm:.2f} "
           f"= {actual_w:.1f} cm.",
           f"Width after rounding: {width_sts} sts × 1/{spec.gauge_sts_per_cm:.2f} "
           f"= {actual_w:.1f} cm.",
           lang)
    )
    p.notes.append(
        _l(f"Længde efter rounding: {rows} rækker × 1/{row_gauge:.2f} = "
           f"{actual_l:.1f} cm.",
           f"Length after rounding: {rows} rows × 1/{row_gauge:.2f} = "
           f"{actual_l:.1f} cm.",
           lang)
    )

    p.validate_continuity()
    return p


def _stitch_name(short: str, lang: str = "da") -> str:
    if lang == "en":
        return {"sc": "sc", "hdc": "hdc", "dc": "dc", "tr": "tr"}[short]
    return {
        "sc":  "fm",
        "hdc": "hstm",
        "dc":  "stm",
        "tr":  "dst",
    }[short]


def _ord(n: int) -> str:
    """English ordinal suffix for a positive integer."""
    if 11 <= (n % 100) <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
