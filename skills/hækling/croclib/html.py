"""Hækling-specific HTML rendering.

Reuses 100 % of :mod:`lib.visualisering.html` (template, components, CSS,
generic builders). Skill-specific behaviour:

* Crochet-flavoured cover stats (diameter, rounds, colours, …).
* Crochet schematics — amigurumi spheres / cylinders, granny squares,
  filet grids, Tunisian fabric.
* Crochet abbreviations (fm/lm/km/hstm/stm/dst).
* Materials box uses the *crochet* swatch warning + placeholder text.

The shared library exposes ``register_renderer`` /
``register_domain_renderer``. We register a domain renderer so any
construction with ``inputs["_domain"] == "crochet"`` lands here even if
the construction-specific renderer isn't registered.
"""

from __future__ import annotations
from pathlib import Path

from lib.visualisering import html as _shared_html
from lib.visualisering import svg as _shared_svg
from lib.visualisering.pattern import Pattern
from lib.visualisering.lang import t

from . import svg as _haekle_svg


# ---------------------------------------------------------------------------
# Cover-stat builder
# ---------------------------------------------------------------------------

def _crochet_cover_stats(p: Pattern, lang: str) -> list[tuple[str, str]]:
    inputs = p.inputs
    g = inputs.get("gauge", {"sts_per_10cm": 0, "rows_per_10cm": 0})
    out: list[tuple[str, str]] = []
    if "diameter_cm" in inputs:
        out.append((t("cover.label.diameter_target", lang),
                    f"{inputs['diameter_cm']:.1f} cm"))
    if "actual_diameter_cm" in inputs:
        out.append((t("cover.label.diameter_actual", lang),
                    f"{inputs['actual_diameter_cm']:.1f} cm"))
    if "rounds" in inputs and p.construction == "granny_square":
        out.append((t("cover.label.rounds", lang), str(inputs["rounds"])))
    if "width_cm" in inputs:
        out.append((t("cover.label.width", lang),
                    f"{inputs['width_cm']:.0f} cm"))
    if "length_cm" in inputs:
        out.append((t("cover.label.length", lang),
                    f"{inputs['length_cm']:.0f} cm"))
    if "width_cells" in inputs:
        out.append(("Celler / Cells",
                    f"{inputs['width_cells']} × {inputs['height_cells']}"))
    out.append((
        t("cover.label.gauge_crochet", lang),
        f"{int(g.get('sts_per_10cm', 0))} m × "
        f"{int(g.get('rows_per_10cm', 0))} omg / 10 cm",
    ))
    return out


# ---------------------------------------------------------------------------
# Schematics
# ---------------------------------------------------------------------------

def _build_haekle_schematics(p: Pattern, lang: str) -> str:
    inputs = p.inputs
    g = inputs.get("gauge", {"sts_per_10cm": 0, "rows_per_10cm": 0})
    figures: list[tuple[str, str, str]] = []

    if p.construction == "amigurumi_sphere":
        figures.append((
            t("fig.amigurumi_sphere", lang,
              rounds=inputs["n_max"] * 2 - 1),
            _haekle_svg.amigurumi_diagram(
                rounds=inputs["n_max"] * 2 - 1,
                max_sts=inputs["max_sts"],
                diameter_cm=inputs.get("actual_diameter_cm"),
            ),
            "",
        ))
    elif p.construction == "amigurumi_cylinder":
        figures.append((
            t("fig.amigurumi_cylinder", lang, rows=inputs["tube_rows"]),
            _haekle_svg.amigurumi_diagram(
                rounds=inputs["n_max"],
                max_sts=inputs["max_sts"],
                diameter_cm=inputs["diameter_cm"],
            ),
            "",
        ))
    elif p.construction == "granny_square":
        figures.append((
            t("fig.granny", lang, rounds=inputs["rounds"]),
            _haekle_svg.granny_square_diagram(
                rounds=inputs["rounds"],
                colors=inputs.get("colors") or None,
            ),
            "",
        ))
    elif p.construction == "haekle_tørklæde":
        figures.append((
            t("fig.haekle_scarf", lang),
            _haekle_svg.scarf_schematic(
                width_cm=inputs["width_cm"],
                length_cm=inputs["length_cm"],
            ),
            "",
        ))
    elif p.construction == "filet":
        figures.append((
            t("fig.filet", lang),
            _haekle_svg.filet_diagram(inputs["grid"]),
            "",
        ))
    elif p.construction == "tunisian":
        figures.append((
            t("fig.tunisian", lang),
            _haekle_svg.tunisian_diagram(
                width_sts=inputs["width_sts"],
                rows=inputs["rows"],
            ),
            "",
        ))

    figures.append((
        t("fig.gauge_crochet", lang),
        _shared_svg.gauge_swatch(
            g.get("sts_per_10cm", 0), g.get("rows_per_10cm", 0)
        ),
        "gauge-fig",
    ))

    fig_tpl = _shared_html._component("schematic_figure")
    return "".join(
        _shared_html._fill(fig_tpl, SVG=svg,
                           CAPTION=_shared_html._h(caption),
                           EXTRA_CLASS=cls)
        for caption, svg, cls in figures
    )


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------

def _build_haekle_measurements(p: Pattern, lang: str) -> str:
    inputs = p.inputs
    row_tpl = _shared_html._component("measurement_row")
    h = _shared_html._h
    rows: list[str] = []

    def add(label: str, value: str) -> None:
        rows.append(_shared_html._fill(row_tpl, LABEL=h(label), VALUE=h(value)))

    if "diameter_cm" in inputs:
        add(t("cover.label.diameter_target", lang),
            f"{inputs['diameter_cm']:.1f} cm")
    if "actual_diameter_cm" in inputs:
        add(t("cover.label.diameter_actual", lang),
            f"{inputs['actual_diameter_cm']:.1f} cm")
    if "n_max" in inputs:
        add("Største omg (n_max)", str(inputs["n_max"]))
        add("Største stitch-count", str(inputs["max_sts"]))
    if "equator_rounds" in inputs:
        add("Ækvator-omg / equator rnds", str(inputs["equator_rounds"]))
    if "rounds" in inputs and p.construction == "granny_square":
        add(t("cover.label.rounds", lang), str(inputs["rounds"]))
        add("Slut-stitch-count / final dc count",
            str(inputs.get("final_dc_count", "?")))
    if "width_cm" in inputs:
        add(t("measure.width", lang), f"{inputs['width_cm']:.1f} cm")
        add(t("measure.length", lang), f"{inputs['length_cm']:.1f} cm")
        if "stitch_type" in inputs:
            add("Grundsting / base stitch", inputs["stitch_type"])
    if "width_cells" in inputs:
        add("Celler bredde / cells wide", str(inputs["width_cells"]))
        add("Celler højde / cells tall", str(inputs["height_cells"]))
        add("Stitches pr. række (3W+1)",
            str(inputs.get("sts_per_row", "?")))
    if "width_sts" in inputs and p.construction == "tunisian":
        add("Width (m / sts)", str(inputs["width_sts"]))
        add("Rækker / rows", str(inputs["rows"]))
        add("Grundsting / base", inputs.get("base_stitch_label",
                                             inputs.get("base_stitch", "TSS")))

    return _shared_html._fill(_shared_html._component("measurements_box"),
                              HEADING=h(t("measurements.heading", lang)),
                              ROWS="".join(rows))


# ---------------------------------------------------------------------------
# Abbreviations (crochet-specific)
# ---------------------------------------------------------------------------

_HAEKLE_ABBREVIATIONS = [
    ("lm", "luftmaske", "ch — chain"),
    ("km", "kædemaske", "sl st — slip stitch"),
    ("fm", "fastmaske", "sc — single crochet"),
    ("hstm", "halvstangmaske", "hdc — half double crochet"),
    ("stm", "stangmaske", "dc — double crochet"),
    ("dst", "dobbeltstangmaske", "tr — treble crochet"),
    ("udt", "udtagning (2 fm i samme m)", "inc"),
    ("indt", "indtagning (2 fm sm)", "sc2tog"),
    ("omg", "omgang(e)", "round(s)"),
    ("R", "række", "row"),
    ("MR", "magisk ring", "magic ring"),
    ("stch", "vendekæde", "turning chain"),
    ("FP / RP", "forward pass / return pass (Tunisian)",
     "forward pass / return pass"),
    ("åben celle", "1 stm + 2 lm (filet mesh)", "open mesh — 1 dc + 2 ch"),
    ("fyldt celle", "3 stm (filet block)", "filled block — 3 dc"),
]


def _build_haekle_abbreviations(lang: str) -> str:
    return _shared_html._build_abbreviations(_HAEKLE_ABBREVIATIONS, lang)


# ---------------------------------------------------------------------------
# Domain renderer — registers as the fallback for crochet patterns.
# ---------------------------------------------------------------------------

def _crochet_parts(p: Pattern, lang: str) -> dict:
    cover = _shared_html._build_cover(
        p, lang,
        eyebrow_key="skill.crochet.eyebrow",
        footer_key="skill.crochet.generator",
        stats=_crochet_cover_stats(p, lang),
    )
    from lib.visualisering import yarn_alternatives as _yarn_alt
    return {
        "cover": cover,
        "schematics": _build_haekle_schematics(p, lang),
        "materials_box": _shared_html._build_materials_box(
            p, lang, crochet=True),
        "measurements_box": _build_haekle_measurements(p, lang),
        "yarn_alternatives": _yarn_alt.render_html_aside(
            p, lang, domain="crochet"),
        "warnings": _shared_html._build_warnings(p, lang),
        "notes": _shared_html._build_notes(p, lang),
        "pattern_sections": _shared_html._build_pattern_sections(p),
        "crown_chart": "",   # crochet doesn't have a crown chart
        "abbreviations": _build_haekle_abbreviations(lang),
        "abbr_intro": t("abbr.intro_crochet", lang),
        "last_page": _shared_html._build_last_page(lang, crochet=True),
    }


# Register at import time so the shared dispatcher routes any pattern with
# ``_domain == "crochet"`` here without each construction needing its own
# renderer.
_shared_html.register_domain_renderer("crochet", _crochet_parts)


# ---------------------------------------------------------------------------
# render_html — thin wrapper that ensures domain marker is set, then
# delegates to lib.visualisering.html.render_html.
# ---------------------------------------------------------------------------

def render_html(p: Pattern, *, paged_js_path: str = "paged.polyfill.js",
                style_path: str | None = None, lang: str = "da",
                reload_script: str = "") -> str:
    """Render a crochet :class:`Pattern` to HTML using the shared template
    machinery and the crochet domain renderer."""
    p.inputs.setdefault("_domain", "crochet")
    return _shared_html.render_html(
        p,
        paged_js_path=paged_js_path,
        style_path=style_path,
        lang=lang,
        reload_script=reload_script,
    )
