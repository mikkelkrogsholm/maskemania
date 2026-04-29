"""Scarf (tørklæde) generator — flat, no shaping.

The simplest possible construction. Validates only that:
  - cast-on is a multiple of the stitch-pattern repeat
  - row count is a multiple of the row repeat (if specified)

Optional stitch patterns are passed as (repeat_width, repeat_height,
description). The validator confirms the math but doesn't render the
stitch pattern itself — that's the formatter's job.
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import Gauge, cm_to_sts, cm_to_rows, Pattern


@dataclass
class TørklædeSpec:
    width_cm: float
    length_cm: float
    gauge: Gauge
    name: str = "Klassisk tørklæde"
    pattern_repeat_sts: int = 1     # 1 = no constraint (e.g. glatstrik)
    pattern_repeat_rows: int = 1
    pattern_description: str = "ret over alle masker (perlestrik / glatstrik)"
    edge_sts: int = 4               # selvedge on each side (often garter)
    edge_rows: int = 6              # garter border top and bottom


def _l(da: str, en: str, lang: str) -> str:
    return en if lang == "en" else da


# English translations for common stitch patterns used by the scarf module.
_PATTERN_EN = {
    "glatstrik": "stockinette",
    "perlestrik": "seed stitch",
    "ret over alle masker (perlestrik / glatstrik)": "knit every stitch (seed / stockinette)",
    "ret": "knit",
}


def _xlate_pattern(desc: str, lang: str) -> str:
    if lang != "en":
        return desc
    return _PATTERN_EN.get(desc, desc)


def generate_tørklæde(spec: TørklædeSpec, lang: str = "da") -> Pattern:
    g = spec.gauge

    # Cast-on must satisfy: pattern_repeat_sts | (cast_on - 2*edge_sts)
    # We compute the patterned-sts count first, round it, then add edges.
    inner_sts_target = spec.width_cm * g.sts_per_10cm / 10.0 - 2 * spec.edge_sts
    if inner_sts_target < spec.pattern_repeat_sts:
        raise ValueError(
            f"width {spec.width_cm} cm is too narrow for the chosen edge ({spec.edge_sts} sts) "
            f"and pattern repeat ({spec.pattern_repeat_sts} sts)."
        )
    inner_sts = max(
        spec.pattern_repeat_sts,
        round(inner_sts_target / spec.pattern_repeat_sts) * spec.pattern_repeat_sts,
    )
    cast_on = inner_sts + 2 * spec.edge_sts

    total_rows = cm_to_rows(spec.length_cm, g)
    if spec.pattern_repeat_rows > 1:
        # round body rows to repeat
        body_rows = total_rows - 2 * spec.edge_rows
        body_rows = max(spec.pattern_repeat_rows,
                        round(body_rows / spec.pattern_repeat_rows) * spec.pattern_repeat_rows)
        total_rows = body_rows + 2 * spec.edge_rows
    body_rows = total_rows - 2 * spec.edge_rows

    p = Pattern(
        name=spec.name,
        construction="tørklæde",
        difficulty="beginner",
        inputs={
            "_domain": "knit",
            "width_cm": spec.width_cm,
            "length_cm": spec.length_cm,
            "gauge": {"sts_per_10cm": g.sts_per_10cm,
                      "rows_per_10cm": g.rows_per_10cm},
            "pattern": spec.pattern_description,
            "pattern_repeat_sts": spec.pattern_repeat_sts,
            "pattern_repeat_rows": spec.pattern_repeat_rows,
            "edge_sts": spec.edge_sts,
            "edge_rows": spec.edge_rows,
        },
    )

    pat_en = _xlate_pattern(spec.pattern_description, lang)

    sec1 = p.add_section(_l("Opslag", "Cast on", lang), sts_before=cast_on)
    sec1.add(
        _l(f"Slå {cast_on} m op på lige pind eller rundpind (strikkes flat).",
           f"Cast on {cast_on} sts on straight or circular needles (worked flat).",
           lang),
        cast_on,
    )
    sec1.add(
        _l(f"Strik retstrik (alle pinde ret) i {spec.edge_rows} pinde for nederste kant.",
           f"Work garter stitch (knit every row) for {spec.edge_rows} rows as the lower border.",
           lang),
        cast_on,
    )

    sec2 = p.add_section(_l("Krop", "Body", lang), sts_before=cast_on)
    if spec.edge_sts > 0:
        sec2.add(
            _l(f"Mønsterpind: {spec.edge_sts} m ret (kant), {inner_sts} m i "
               f"{spec.pattern_description}, {spec.edge_sts} m ret (kant).",
               f"Pattern row: k{spec.edge_sts} (border), {inner_sts} sts in "
               f"{pat_en}, k{spec.edge_sts} (border).",
               lang),
            cast_on,
            note=_l(f"gentag i alt {body_rows} pinde",
                    f"repeat for a total of {body_rows} rows", lang),
        )
    else:
        sec2.add(
            _l(f"Strik {body_rows} pinde i {spec.pattern_description}.",
               f"Work {body_rows} rows in {pat_en}.",
               lang),
            cast_on,
        )

    sec3 = p.add_section(
        _l("Øverste kant og aflukning", "Upper border and bind off", lang),
        sts_before=cast_on,
    )
    sec3.add(
        _l(f"Strik {spec.edge_rows} pinde retstrik for øverste kant.",
           f"Work {spec.edge_rows} rows of garter stitch as the upper border.",
           lang),
        cast_on,
    )
    sec3.add(
        _l("Luk løst af på retsiden. Hæft ender. Blok efter behov.",
           "Bind off loosely on the right side. Weave in ends. Block as needed.",
           lang),
        cast_on,
    )

    p.validate_continuity()
    p.notes.append(
        _l(f"Bredde efter rounding: {inner_sts + 2*spec.edge_sts} m × "
           f"10/{g.sts_per_10cm} = "
           f"{(inner_sts + 2*spec.edge_sts) * 10/g.sts_per_10cm:.1f} cm.",
           f"Width after rounding: {inner_sts + 2*spec.edge_sts} sts × "
           f"10/{g.sts_per_10cm} = "
           f"{(inner_sts + 2*spec.edge_sts) * 10/g.sts_per_10cm:.1f} cm.",
           lang)
    )
    p.notes.append(
        _l(f"Længde efter rounding: {total_rows} pinde ≈ "
           f"{total_rows * 10/g.rows_per_10cm:.1f} cm.",
           f"Length after rounding: {total_rows} rows ≈ "
           f"{total_rows * 10/g.rows_per_10cm:.1f} cm.",
           lang)
    )
    return p
