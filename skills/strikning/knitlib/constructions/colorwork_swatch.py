"""Flat colorwork swatch — a simple stranded sampler rectangle.

This is a deliberately small construction whose primary purpose is to
exercise the colorwork chart system without committing the knitter to a
whole yoke sweater. It produces a flat rectangle worked back and forth
with garter-stitch edges, the chosen motif repeated horizontally and
vertically inside the inner panel, and a colorwork chart embedded in the
HTML output.

Inputs:
  - ``width_cm`` — desired width before garter edges (rounded down to a
    multiple of the motif width so the repeat tiles cleanly).
  - ``height_cm`` — desired height (rounded to whole motif rows).
  - ``gauge`` — sts/rows per 10 cm.
  - ``motif`` — name from ``lib.visualisering.motifs.MOTIFS``.
  - ``edge_sts`` / ``edge_rows`` — garter borders.

Outputs:
  - A Pattern with sections: opslag, garter-bånd, mønstret krop, garter-bånd,
    aflukning. Each section has validated stitch counts.
  - ``inputs["colorwork_chart"]`` payload picked up by the HTML renderer
    to produce an SVG chart with legend.
  - A markdown text-grid in ``notes`` as a printable fallback.
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import (
    Gauge, cm_to_sts, cm_to_rows, Pattern, RowValidator,
)
from lib.visualisering.motifs import MOTIFS, get_motif
from ..knitrow import KnitRow as Row
from .yoke_stranded import render_color_chart


@dataclass
class ColorworkSwatchSpec:
    width_cm: float
    height_cm: float
    gauge: Gauge
    motif: str = "stars"
    edge_sts: int = 3
    edge_rows: int = 4
    name: str = "Colorwork prøvelap"
    metadata: dict | None = None


def generate_colorwork_swatch(spec: ColorworkSwatchSpec, lang: str = "da") -> Pattern:
    if spec.width_cm <= 0:
        raise ValueError("width_cm must be > 0")
    if spec.height_cm <= 0:
        raise ValueError("height_cm must be > 0")
    if spec.edge_sts < 0 or spec.edge_rows < 0:
        raise ValueError("edge_sts and edge_rows must be >= 0")
    if spec.motif not in MOTIFS:
        raise KeyError(
            f"unknown motif {spec.motif!r}. Known: {', '.join(sorted(MOTIFS))}"
        )

    motif_data = get_motif(spec.motif)
    motif_grid: list[list[str]] = motif_data["grid"]
    motif_width: int = motif_data["width"]
    motif_height: int = motif_data["height"]
    motif_colors: dict[str, str] = motif_data["default_colors"]

    g = spec.gauge

    # Inner sts must be a multiple of the motif width.
    inner_sts_target = cm_to_sts(spec.width_cm, g, multiple=1)
    n_repeats_w = max(1, inner_sts_target // motif_width)
    inner_sts = n_repeats_w * motif_width
    cast_on = inner_sts + 2 * spec.edge_sts
    actual_width_cm = cast_on * 10.0 / g.sts_per_10cm

    # Body rows must be a multiple of motif height.
    body_rows_target = cm_to_rows(spec.height_cm, g) - 2 * spec.edge_rows
    if body_rows_target < motif_height:
        n_repeats_h = 1
    else:
        n_repeats_h = max(1, round(body_rows_target / motif_height))
    body_rows = n_repeats_h * motif_height
    total_rows = body_rows + 2 * spec.edge_rows
    actual_height_cm = total_rows * 10.0 / g.rows_per_10cm

    metadata = dict(spec.metadata or {})
    chart_text = render_color_chart(motif_grid)

    p = Pattern(
        name=spec.name,
        construction="colorwork_swatch",
        difficulty="easy",
        inputs={
            "_domain": "knit",
            "width_cm": spec.width_cm,
            "height_cm": spec.height_cm,
            # length_cm alias so the generic measurements_box renderer
            # (which keys off width_cm + length_cm) succeeds.
            "length_cm": spec.height_cm,
            "actual_width_cm": round(actual_width_cm, 1),
            "actual_length_cm": round(actual_height_cm, 1),
            "cast_on": cast_on,
            "inner_sts": inner_sts,
            "edge_sts": spec.edge_sts,
            "edge_rows": spec.edge_rows,
            "motif_name": spec.motif,
            "motif_width": motif_width,
            "motif_height": motif_height,
            "n_repeats_w": n_repeats_w,
            "n_repeats_h": n_repeats_h,
            "body_rows": body_rows,
            "total_rows": total_rows,
            "color_chart": chart_text,
            "colorwork_chart": {
                "rows": [list(r) for r in motif_grid],
                "colors": dict(motif_colors),
                "caption": (
                    f"{motif_data['name']} — "
                    f"{motif_width} m × {motif_height} p rapport"
                ),
                "repeat_marker_x": (0, motif_width - 1),
                "color_names": {k: f"Farve {k}" for k in motif_colors},
            },
            "gauge": {
                "sts_per_10cm": g.sts_per_10cm,
                "rows_per_10cm": g.rows_per_10cm,
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- Opslag --------------------------------------------------------
    sec1 = p.add_section("Opslag og garter-bånd", sts_before=cast_on)
    sec1.add(
        f"Slå {cast_on} m op med farve A i en elastisk metode "
        f"(fx long-tail). {n_repeats_w} × {motif_width} m motiv + "
        f"2 × {spec.edge_sts} m garter-kant.",
        cast_on,
    )
    if spec.edge_rows > 0:
        sec1.add(
            f"Strik {spec.edge_rows} p garter (= ret hver række) i farve A.",
            cast_on,
        )
    validator.add(Row(sts_before=cast_on).k(cast_on))

    # ---- Mønstret krop --------------------------------------------------
    sec2 = p.add_section("Mønstret krop", sts_before=cast_on)
    sec2.add(
        f"Strik {body_rows} p stranded mønster i {n_repeats_h} fulde "
        f"motiv-højder. Hold {spec.edge_sts} m garter i farve A i begge "
        f"sider; mønsteret arbejdes kun over de inderste {inner_sts} m.",
        cast_on,
        note=(
            f"motiv: {motif_data['name']}, "
            f"{motif_width} m × {motif_height} p, "
            f"gentag {n_repeats_w} gange i bredden."
        ),
    )
    sec2.add(
        "Læs charten nedefra og op. På RS-pinde læses fra højre mod venstre, "
        "på WS-pinde fra venstre mod højre.",
        cast_on,
    )

    # ---- Slut-bånd + aflukning -----------------------------------------
    sec3 = p.add_section("Garter-bånd og aflukning", sts_before=cast_on)
    if spec.edge_rows > 0:
        sec3.add(
            f"Strik {spec.edge_rows} p garter i farve A.",
            cast_on,
        )
    sec3.add(
        f"Luk løst af i farve A. Hæft enderne. Blok prøvelappen og "
        f"mål gauge.",
        cast_on,
    )

    # ---- Notes ---------------------------------------------------------
    p.notes.append(
        f"Færdig prøvelap: ca. {actual_width_cm:.1f} × {actual_height_cm:.1f} cm "
        f"({cast_on} m × {total_rows} p)."
    )
    p.notes.append(
        f"Stranded teknik: hold begge garn i samme hånd eller én i hver. "
        f"Vrid trådene hvert 4.-5. m for at undgå lange floats."
    )
    if chart_text:
        p.notes.append(f"Tekst-grid (■ = farve A, □ = farve B):")
        p.notes.append(chart_text)

    if cast_on < motif_width + 2 * spec.edge_sts:
        p.warnings.append(
            f"Prøvelappen er smallere end én motiv-rapport "
            f"({cast_on} m, motiv = {motif_width} m). Øg width_cm."
        )

    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
