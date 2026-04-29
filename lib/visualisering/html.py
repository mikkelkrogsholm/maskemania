"""HTML formatter — loads templates + components and assembles the page.

Architecture:
  templates/pattern.html  — outer shell with {{PLACEHOLDERS}}
  components/*.html       — small reusable HTML fragments
  assets/style.css        — all CSS (lives outside Python)
  lang/translations.py    — small translation dict (``t(key, lang)``)

The Python here is an orchestrator: it loads templates, fills placeholders
with data from the Pattern object, and returns a final string. No CSS or
HTML structure is built in code — change the look by editing the .html/.css
files.

Skills register a per-construction renderer via :func:`register_renderer`
so the dispatch is open: knit registers ``hue``, ``raglan_topdown``, …;
crochet registers ``amigurumi_sphere``, ``granny_square``, … . Each
renderer is a callable returning a dict with the keys the template
expects (``cover``, ``schematics``, ``materials_box``, …). The dict-based
contract lets each skill compose components however it likes while the
default builders below are still available as a fallback.
"""

from __future__ import annotations
import html
import re
from pathlib import Path
from typing import Callable
from .pattern import Pattern
from . import svg as svg_mod
from . import chart_symbols as _chart_symbols
from . import prosa as _prosa
from . import yarn_alternatives as _yarn_alt
from .lang import t


# Module-level toggle so callers (CLI ``--no-prosa``) can opt out without
# rewiring every renderer. Default: prose intro is rendered.
_PROSA_ENABLED = True


def set_prosa_enabled(enabled: bool) -> None:
    """Globally toggle the prose-intro section.

    Used by the CLI ``--no-prosa`` flag. The flag is process-global because
    the renderer reaches prose via the parts dict; threading a kwarg through
    every registered renderer would be invasive. Tests and CLI flip it
    explicitly; production callers leave it on.
    """
    global _PROSA_ENABLED
    _PROSA_ENABLED = bool(enabled)


def is_prosa_enabled() -> bool:
    return _PROSA_ENABLED


_HERE = Path(__file__).resolve().parent
_ASSETS = _HERE / "assets"
_COMPONENTS = _HERE / "components"
_TEMPLATES = _HERE / "templates"


def _h(text) -> str:
    return html.escape(str(text))


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _component(name: str) -> str:
    return _load(_COMPONENTS / f"{name}.html")


def _fill(template: str, **kwargs) -> str:
    """Replace {{KEY}} tokens with values. Missing keys become empty strings."""
    out = template
    placeholders = set(re.findall(r"\{\{(\w+)\}\}", template))
    for key in placeholders:
        value = kwargs.get(key, "")
        out = out.replace("{{" + key + "}}", str(value))
    return out


# ---------------------------------------------------------------------------
# Pluggable construction renderers
# ---------------------------------------------------------------------------

# Each renderer is a callable (Pattern, str lang) -> dict. Returned dict keys
# correspond to template placeholders ("cover", "schematics",
# "materials_box", "measurements_box", "abbreviations", "abbr_intro",
# "crown_chart" (optional)). Skills call register_renderer() at import time.

ConstructionRenderer = Callable[[Pattern, str], dict]
_RENDERERS: dict[str, ConstructionRenderer] = {}
# Fallback renderer per "domain" (knit, crochet) that knows the abbrevations
# and the materials box. Skills register one for each domain.
_DOMAIN_RENDERERS: dict[str, ConstructionRenderer] = {}


def register_renderer(construction: str, renderer: ConstructionRenderer) -> None:
    _RENDERERS[construction] = renderer


def register_domain_renderer(domain: str, renderer: ConstructionRenderer) -> None:
    """Register a fallback renderer for a whole domain (e.g. ``"knit"`` or
    ``"crochet"``). Used when the construction-specific renderer is missing,
    or as a base layer for shared parts like abbreviations."""
    _DOMAIN_RENDERERS[domain] = renderer


def _domain_for(p: Pattern) -> str:
    return str(p.inputs.get("_domain", "knit"))


# ---------------------------------------------------------------------------
# Default component builders (knit-leaning; crochet has its own in croclib)
# ---------------------------------------------------------------------------

def _construction_label(construction: str, lang: str) -> str:
    return t(f"construction.{construction}", lang)


def _build_cover(p: Pattern, lang: str = "da", *,
                 eyebrow_key: str = "skill.knit.eyebrow",
                 footer_key: str = "skill.knit.generator",
                 stats: list[tuple[str, str]] | None = None) -> str:
    """Generic cover builder. Skills usually pass their own ``stats`` list."""
    stat_tpl = _component("cover_stat")
    stats = stats or _default_cover_stats(p, lang)
    rendered_stats = [
        _fill(stat_tpl, LABEL=_h(label), VALUE=_h(value))
        for label, value in stats
    ]

    md = p.inputs.get("metadata") or {}
    designer_line = ""
    bits: list[str] = []
    if md.get("designer"):
        bits.append(f"{t('materials.designer', lang)}: {_h(md['designer'])}")
    if md.get("year"):
        bits.append(str(md["year"]))
    if bits:
        designer_line = f'<p class="cover-designer">{" · ".join(bits)}</p>'

    difficulty_line = ""
    diff = getattr(p, "difficulty", "") or ""
    if diff:
        diff_label = t("difficulty", lang)
        diff_value = t(f"difficulty.{diff}", lang)
        difficulty_line = (
            f'<div class="difficulty">{_h(diff_label)}: '
            f'<strong>{_h(diff_value)}</strong></div>'
        )

    return _fill(_component("cover"),
                 EYEBROW=_h(t(eyebrow_key, lang)),
                 NAME=_h(p.name),
                 SUBTITLE=_h(_construction_label(p.construction, lang)),
                 DESIGNER_LINE=designer_line,
                 DIFFICULTY_LINE=difficulty_line,
                 STATS="".join(rendered_stats),
                 FOOTER=_h(t(footer_key, lang)))


def _default_cover_stats(p: Pattern, lang: str) -> list[tuple[str, str]]:
    inputs = p.inputs
    g = inputs.get("gauge", {"sts_per_10cm": 0, "rows_per_10cm": 0})
    out: list[tuple[str, str]] = []
    if "finished_bust_cm" in inputs:
        out.append((t("cover.label.bust_finished", lang),
                    f"{inputs['finished_bust_cm']:.0f} cm"))
    if "finished_circumference_cm" in inputs:
        out.append((t("cover.label.head_finished", lang),
                    f"{inputs['finished_circumference_cm']:.0f} cm"))
    if "width_cm" in inputs:
        out.append((t("cover.label.width", lang),
                    f"{inputs['width_cm']:.0f} cm"))
    if "length_cm" in inputs:
        out.append((t("cover.label.length", lang),
                    f"{inputs['length_cm']:.0f} cm"))
    out.append((
        t("cover.label.gauge", lang),
        f"{int(g.get('sts_per_10cm', 0))} m × "
        f"{int(g.get('rows_per_10cm', 0))} p / 10 cm",
    ))
    return out


def _build_schematics_default(p: Pattern, lang: str = "da") -> str:
    """Generic knit schematics dispatch. Construction-specific dispatch goes
    through registered renderers; this is the fallback used by the knit
    skill."""
    inputs = p.inputs
    g = inputs["gauge"]
    figures: list[tuple[str, str, str]] = []

    if p.construction == "hue":
        figures.append((
            t("fig.hue_side", lang),
            svg_mod.hue_schematic(
                finished_circumference_cm=inputs["finished_circumference_cm"],
                total_height_cm=inputs["total_height_cm"],
                rib_height_cm=inputs["rib_height_cm"],
                sectors=inputs["sectors"],
            ),
            "",
        ))
        figures.append((
            t("fig.crown_top", lang, sectors=inputs["sectors"]),
            svg_mod.crown_top_view(
                sectors=inputs["sectors"],
                finished_circumference_cm=inputs["finished_circumference_cm"],
            ),
            "",
        ))
    elif p.construction == "tørklæde":
        figures.append((
            t("fig.tørklæde", lang),
            svg_mod.tørklæde_schematic(
                width_cm=inputs["width_cm"],
                length_cm=inputs["length_cm"],
            ),
            "",
        ))
    elif p.construction == "lace_shawl":
        figures.append((
            t("fig.lace_shawl", lang),
            svg_mod.tørklæde_schematic(
                width_cm=inputs.get("actual_width_cm", inputs["width_cm"]),
                length_cm=inputs.get("actual_length_cm", inputs["length_cm"]),
            ),
            "",
        ))
    elif p.construction == "raglan_topdown":
        figures.append((
            t("fig.raglan", lang),
            svg_mod.raglan_schematic(
                finished_bust_cm=inputs["finished_bust_cm"],
                body_length_cm=inputs["body_length_cm"],
                yoke_depth_cm=inputs["yoke_depth_cm"],
                neck_circumference_cm=inputs["neck_circumference_cm"],
                upper_arm_cm=inputs["upper_arm_cm"],
                wrist_cm=inputs["wrist_cm"],
                sleeve_length_cm=inputs["sleeve_length_cm"],
            ),
            "",
        ))
    elif p.construction == "sokker":
        figures.append((
            t("fig.sock", lang),
            svg_mod.sock_schematic(
                foot_length_cm=inputs["foot_length_cm"],
                foot_circ_cm=inputs["foot_circ_cm"],
                leg_length_cm=inputs["leg_length_cm"],
            ),
            "",
        ))
    elif p.construction == "bottom_up_sweater":
        figures.append((
            t("fig.sweater", lang),
            svg_mod.raglan_schematic(
                finished_bust_cm=inputs["finished_bust_cm"],
                body_length_cm=inputs["body_length_cm"],
                yoke_depth_cm=inputs["yoke_depth_cm"],
                neck_circumference_cm=inputs["neck_circumference_cm"],
                upper_arm_cm=inputs["upper_arm_cm"],
                wrist_cm=inputs["wrist_cm"],
                sleeve_length_cm=inputs["sleeve_length_cm"],
            ),
            "",
        ))

    figures.append((
        t("fig.gauge", lang),
        svg_mod.gauge_swatch(g["sts_per_10cm"], g["rows_per_10cm"]),
        "gauge-fig",
    ))

    fig_tpl = _component("schematic_figure")
    return "".join(
        _fill(fig_tpl, SVG=svg, CAPTION=_h(caption), EXTRA_CLASS=cls)
        for caption, svg, cls in figures
    )


def _build_materials_box(p: Pattern, lang: str = "da", *,
                         crochet: bool = False) -> str:
    g = p.inputs.get("gauge", {"sts_per_10cm": 0, "rows_per_10cm": 0})
    md = p.inputs.get("metadata") or {}
    items: list[str] = []
    if md.get("yarn"):
        items.append(f"<li><strong>{_h(t('materials.yarn', lang))}:</strong> {_h(md['yarn'])}</li>")
    if md.get("yarn_run"):
        items.append(f"<li><strong>{_h(t('materials.yarn_lineweight', lang))}:</strong> {_h(md['yarn_run'])}</li>")
    if md.get("hook" if crochet else "needles"):
        key = "materials.hook" if crochet else "materials.needles"
        items.append(
            f"<li><strong>{_h(t(key, lang))}:</strong> "
            f"{_h(md['hook' if crochet else 'needles'])}</li>"
        )
    if md.get("designer"):
        items.append(f"<li><strong>{_h(t('materials.designer', lang))}:</strong> {_h(md['designer'])}</li>")
    if md.get("year"):
        items.append(f"<li><strong>{_h(t('materials.year', lang))}:</strong> {_h(md['year'])}</li>")
    notes_md = md.get("notes") or []
    for n in notes_md:
        items.append(f"<li>{_h(n)}</li>")

    if items:
        items.append(f"<li><strong>{_h(t('materials.notions', lang))}:</strong> "
                     f"{_h(t('materials.notions_text', lang))}</li>")
        materials_list = f"<ul class='materials-list'>{''.join(items)}</ul>"
    else:
        placeholder_key = "materials.placeholder_crochet" if crochet else "materials.placeholder_knit"
        materials_list = f"<p class='placeholder'>{t(placeholder_key, lang)}</p>"

    gauge_value_key = "materials.gauge_value_crochet" if crochet else "materials.gauge_value_knit"
    gauge_value = t(gauge_value_key, lang,
                    sts=int(g.get("sts_per_10cm", 0)),
                    rows=int(g.get("rows_per_10cm", 0)))
    swatch_warning_key = "materials.swatch_warning_crochet" if crochet else "materials.swatch_warning"
    return _fill(_component("materials_box"),
                 HEADING=_h(t("materials.heading", lang)),
                 GAUGE_HEADING=_h(t("materials.gauge_heading", lang)),
                 MATERIALS_LIST=materials_list,
                 GAUGE_VALUE=gauge_value,
                 SWATCH_WARNING=_h(t(swatch_warning_key, lang)))


def _build_measurements_box(p: Pattern, lang: str = "da") -> str:
    inputs = p.inputs
    row_tpl = _component("measurement_row")
    rows: list[str] = []

    def add(label: str, value: str) -> None:
        rows.append(_fill(row_tpl, LABEL=_h(label), VALUE=_h(value)))

    if "finished_bust_cm" in inputs:
        add(t("measure.bust_finished", lang), f"{inputs['finished_bust_cm']:.1f} cm")
        if "bust_cm" in inputs:
            add(t("measure.bust_body", lang), f"{inputs['bust_cm']:.0f} cm")
        add(t("measure.ease", lang), f"{inputs['ease_cm']:+.0f} cm")
        if "yoke_depth_cm" in inputs:
            add(t("measure.yoke_depth", lang), f"{inputs['yoke_depth_cm']:.0f} cm")
        if "body_length_cm" in inputs:
            add(t("measure.body_length", lang), f"{inputs['body_length_cm']:.0f} cm")
        if "sleeve_length_cm" in inputs:
            add(t("measure.sleeve_length", lang), f"{inputs['sleeve_length_cm']:.0f} cm")
        if "neck_circumference_cm" in inputs:
            add(t("measure.neck_circ", lang), f"{inputs['neck_circumference_cm']:.0f} cm")
        if "wrist_cm" in inputs:
            add(t("measure.wrist_circ", lang), f"{inputs['wrist_cm']:.0f} cm")
    elif "finished_circumference_cm" in inputs:
        add(t("measure.head_finished", lang),
            f"{inputs['finished_circumference_cm']:.0f} cm")
        add(t("measure.head_body", lang),
            f"{inputs['head_circumference_cm']:.0f} cm")
        add(t("measure.ease", lang), f"{inputs['ease_cm']:+.0f} cm")
        add(t("measure.height", lang), f"{inputs['total_height_cm']:.0f} cm")
        add(t("measure.rib_height", lang), f"{inputs['rib_height_cm']:.0f} cm")
    elif "width_cm" in inputs:
        add(t("measure.width", lang), f"{inputs['width_cm']:.0f} cm")
        add(t("measure.length", lang), f"{inputs['length_cm']:.0f} cm")
        if "pattern" in inputs:
            add(t("measure.pattern", lang), str(inputs.get("pattern", "")))
    elif "foot_length_cm" in inputs:
        add(t("cover.label.foot_length", lang), f"{inputs['foot_length_cm']:.1f} cm")
        add(t("cover.label.foot_circ", lang), f"{inputs['foot_circ_cm']:.1f} cm")
        if inputs.get("shoe_size"):
            add(t("cover.label.shoe_size", lang), str(inputs["shoe_size"]))

    return _fill(_component("measurements_box"),
                 HEADING=_h(t("measurements.heading", lang)),
                 ROWS="".join(rows))


def _build_pattern_sections(p: Pattern) -> str:
    sec_tpl = _component("pattern_section")
    step_tpl = _component("pattern_step")
    parts: list[str] = []
    for sec in p.sections:
        delta = ""
        if sec.sts_before != sec.sts_after:
            delta = (f'<span class="section-delta">'
                     f'{sec.sts_before} → {sec.sts_after} m</span>')
        steps_html = "".join(
            _fill(step_tpl,
                  TEXT=_h(st.text),
                  COUNT=str(st.sts_after),
                  NOTE=(f'<div class="note">{_h(st.note)}</div>' if st.note else ""))
            for st in sec.steps
        )
        parts.append(_fill(sec_tpl, TITLE=_h(sec.title),
                           DELTA=delta, STEPS=steps_html))
    return "".join(parts)


def _build_warnings(p: Pattern, lang: str = "da") -> str:
    if not p.warnings:
        return ""
    items = "".join(f"<li>{_h(w)}</li>" for w in p.warnings)
    return _fill(_component("warnings_box"),
                 HEADING=_h(t("section.warnings", lang)),
                 ITEMS=items)


def _build_notes(p: Pattern, lang: str = "da") -> str:
    if not p.notes:
        return ""
    items = "".join(f"<li>{_h(n)}</li>" for n in p.notes)
    return _fill(_component("notes_box"),
                 HEADING=_h(t("section.notes", lang)),
                 ITEMS=items)


_KNIT_ABBREVIATIONS = [
    ("r", "ret", "knit"),
    ("vr", "vrang", "purl"),
    ("m", "maske(r)", "stitch(es)"),
    ("omg", "omgang(e)", "round(s)"),
    ("p", "pind", "row"),
    ("rs / vs", "retside / vrangside", "RS / WS"),
    ("2 r sm", "2 ret sammen", "k2tog"),
    ("dr r sm", "overtrukket maske", "ssk"),
    ("SLO", "slå om", "yo"),
    ("M1L", "venstre-hældende udtagning (tråd op forfra, strik drejet)", "make 1 left"),
    ("M1R", "højre-hældende udtagning (tråd op bagfra, strik ret)", "make 1 right"),
    ("kfb", "1 r i forreste + bageste maskeben", "kfb"),
    ("sm", "flyt markøren", "slip marker"),
    ("pm", "sæt markør", "place marker"),
    ("luk af", "luk masker af", "BO / bind off"),
]


def _build_abbreviations(rows: list[tuple[str, str, str]] | None = None,
                          lang: str = "da") -> str:
    rows = rows if rows is not None else _KNIT_ABBREVIATIONS
    row_tpl = _component("abbreviation_row")
    body = "".join(
        _fill(row_tpl, ABBR=_h(d), DA=_h(da), EN=_h(en))
        for d, da, en in rows
    )
    return _fill(_component("abbreviations_table"),
                 COL_ABBR=_h(t("abbr.col.abbr", lang)),
                 COL_DA=_h(t("abbr.col.da", lang)),
                 COL_EN=_h(t("abbr.col.en", lang)),
                 ROWS=body)


def render_colorwork_figure(rows: list[list[str]],
                             colors: dict[str, str], *,
                             caption: str = "",
                             lang: str = "da",
                             cell_size: int = 24,
                             repeat_marker_x: tuple[int, int] | None = None,
                             color_names: dict[str, str] | None = None,
                             extra_class: str = "") -> str:
    """Render a stranded colorwork chart as a ``<figure>`` block.

    Wraps the SVG produced by :func:`chart_symbols.colorwork_chart` in a
    figure with a caption. The legend is drawn inside the SVG itself so we
    don't need a separate HTML legend table.
    """
    svg = _chart_symbols.colorwork_chart(
        rows, colors, cell_size=cell_size,
        caption="",
        repeat_marker_x=repeat_marker_x,
        color_names=color_names,
    )
    cls = f"chart colorwork {extra_class}".strip()
    return (
        f'<figure class="{_h(cls)}">'
        f'{svg}'
        + (f'<figcaption>{_h(caption)}</figcaption>' if caption else '')
        + f'</figure>'
    )


def _build_colorwork_chart(p: Pattern, lang: str = "da") -> str:
    """If the pattern carries a colorwork chart in its inputs, render it.

    Constructions opt-in by storing ``inputs["colorwork_chart"]`` as a
    dict with keys ``rows`` (2D list of colour-keys), ``colors``
    (dict of key → CSS colour), optional ``caption``, ``repeat_marker_x``
    and ``color_names``.
    """
    chart = p.inputs.get("colorwork_chart")
    if not chart:
        return ""
    rows = chart.get("rows")
    colors = chart.get("colors")
    if not rows or not colors:
        return ""
    caption = chart.get("caption") or t("chart.colorwork_caption", lang)
    rm = chart.get("repeat_marker_x")
    if rm is not None:
        rm = (int(rm[0]), int(rm[1]))
    color_names = chart.get("color_names")
    figure = render_colorwork_figure(
        rows, colors, caption=caption, lang=lang,
        repeat_marker_x=rm, color_names=color_names,
    )
    heading = t("chart.colorwork_section_heading", lang)
    return (
        f'<section class="colorwork-chart-section">'
        f'<h2>{_h(heading)}</h2>{figure}</section>'
    )


def render_chart_figure(rows: list[list[str]], *, caption: str,
                         lang: str = "da",
                         cell_size: int = 24,
                         repeat_marker: tuple[int, int] | None = None,
                         extra_class: str = "") -> str:
    """Render a stitch-chart figure with caption + legend.

    Wraps a chart-grid SVG in a ``<figure class="chart">`` element with a
    caption and a small legend that maps every symbol used in the chart to
    its textual meaning (translated via ``t()``).
    """
    chart_svg = _chart_symbols.chart_grid(rows, cell_size=cell_size,
                                          repeat_marker=repeat_marker)
    legend = _chart_symbols.legend_entries(rows, lang=lang)
    legend_rows = "".join(
        f'<tr><td class="chart-legend-symbol">{sample}</td>'
        f'<td class="chart-legend-label">{_h(label)}</td></tr>'
        for _name, label, sample in legend
    )
    legend_heading = t("chart.legend_heading", lang)
    return _fill(_component("chart_figure"),
                 SVG=chart_svg,
                 CAPTION=_h(caption),
                 LEGEND_HEADING=_h(legend_heading),
                 LEGEND_ROWS=legend_rows,
                 EXTRA_CLASS=extra_class)


def _build_crown_chart(p: Pattern) -> str:
    if p.construction != "hue":
        return ""
    crown_sec = next((s for s in p.sections if s.title == "Krone"), None)
    if crown_sec is None:
        return ""
    plan: list[tuple[int, int, str]] = []
    for st in crown_sec.steps:
        if st.text.startswith("Klip"):
            continue
        m = re.match(r"Omg (\d+):\s*(.*)", st.text)
        if not m:
            continue
        plan.append((int(m.group(1)), st.sts_after, m.group(2)))
    sectors = p.inputs.get("sectors", 8)
    start_sts = crown_sec.sts_before
    cc_svg = svg_mod.crown_chart(plan, sectors=sectors,
                                 start_per_sector=start_sts // sectors)
    return _fill(_component("crown_chart_section"),
                 SECTORS=str(sectors), SVG=cc_svg)


def _build_lace_chart(p: Pattern, lang: str = "da") -> str:
    """If the pattern carries a lace chart in its inputs, render it.

    Constructions opt-in by storing ``inputs["lace_chart"]`` as a dict with
    keys ``rows`` (2D list of symbol names), optional ``caption`` and
    ``repeat_marker``. The dict is preserved through the JSON round-trip so
    the chart survives serialisation.
    """
    chart = p.inputs.get("lace_chart")
    if not chart:
        return ""
    rows = chart.get("rows")
    if not rows:
        return ""
    caption = chart.get("caption") or t("chart.lace_caption", lang)
    rm = chart.get("repeat_marker")
    if rm is not None:
        rm = (int(rm[0]), int(rm[1]))
    figure = render_chart_figure(rows, caption=caption, lang=lang,
                                  repeat_marker=rm)
    return f'<section class="lace-chart-section"><h2>{_h(t("chart.section_heading", lang))}</h2>{figure}</section>'


def _build_last_page(lang: str = "da", *, crochet: bool = False) -> str:
    body_key = "lastpage.body_crochet" if crochet else "lastpage.body_knit"
    tag_key = "lastpage.tag_crochet" if crochet else "lastpage.tag_knit"
    return _fill(_component("last_page"),
                 BODY=t(body_key, lang),  # contains <em> markup, do NOT escape
                 TAG=_h(t(tag_key, lang)))


# ---------------------------------------------------------------------------
# Main entry — render_html
# ---------------------------------------------------------------------------

def render_html(p: Pattern, *, paged_js_path: str = "paged.polyfill.js",
                style_path: str | None = None, lang: str = "da",
                reload_script: str = "") -> str:
    """Render a Pattern as a full HTML document.

    paged_js_path: where the browser should find paged.polyfill.js (relative
    to the HTML file). Default 'paged.polyfill.js' (same directory).

    style_path: where the browser should find style.css. Default: an
    embedded <style> block reading from assets/style.css.

    lang: ``da`` (default) or ``en``. Strings unknown in the requested
    language fall back to Danish.

    reload_script: optional extra HTML (typically a <script> tag) injected
    just before </body>. Used by the live preview server to add
    auto-reload polling.
    """
    if style_path is None:
        css = _load(_ASSETS / "style.css")
        style_marker = f"<style>\n{css}\n</style>"
        template = _load(_TEMPLATES / "pattern.html")
        template = template.replace(
            '<link rel="stylesheet" href="{{STYLE_PATH}}">', style_marker)
    else:
        template = _load(_TEMPLATES / "pattern.html")
        template = template.replace("{{STYLE_PATH}}", style_path)

    # Construction-specific renderer wins, then domain renderer, else default.
    parts = _render_parts(p, lang)

    return _fill(template,
                 HTML_LANG=("en" if lang == "en" else "da"),
                 TITLE=_h(p.name),
                 PAGED_JS_PATH=_h(paged_js_path),
                 H_SCHEMATIC=_h(t("section.schematic", lang)),
                 H_MATERIALS=_h(t("section.materials", lang)),
                 H_PATTERN=_h(t("section.pattern", lang)),
                 H_ABBREVIATIONS=_h(t("section.abbreviations", lang)),
                 ABBR_INTRO=_h(parts.get("abbr_intro", t("abbr.intro_knit", lang))),
                 COVER=parts["cover"],
                 PROSA=parts.get("prosa", ""),
                 SCHEMATICS=parts["schematics"],
                 MATERIALS_BOX=parts["materials_box"],
                 MEASUREMENTS_BOX=parts["measurements_box"],
                 YARN_ALTERNATIVES=parts.get("yarn_alternatives", ""),
                 WARNINGS=parts.get("warnings", ""),
                 NOTES=parts.get("notes", ""),
                 PATTERN_SECTIONS=parts["pattern_sections"],
                 CROWN_CHART=parts.get("crown_chart", ""),
                 EXTRA_CHARTS=parts.get("extra_charts", ""),
                 ABBREVIATIONS=parts["abbreviations"],
                 LAST_PAGE=parts["last_page"],
                 RELOAD_SCRIPT=reload_script)


def _render_parts(p: Pattern, lang: str) -> dict:
    """Resolve which parts dict to use: per-construction → domain → default."""
    if p.construction in _RENDERERS:
        parts = _RENDERERS[p.construction](p, lang)
    else:
        domain = _domain_for(p)
        if domain in _DOMAIN_RENDERERS:
            parts = _DOMAIN_RENDERERS[domain](p, lang)
        else:
            parts = _default_knit_parts(p, lang)
    # Fill in any missing keys from defaults so the template always succeeds.
    defaults = _default_knit_parts(p, lang)
    for k, v in defaults.items():
        parts.setdefault(k, v)
    return parts


def _default_knit_parts(p: Pattern, lang: str) -> dict:
    return {
        "cover": _build_cover(p, lang),
        "prosa": _prosa.format_intro_html(p, lang) if _PROSA_ENABLED else "",
        "schematics": _build_schematics_default(p, lang),
        "materials_box": _build_materials_box(p, lang, crochet=False),
        "measurements_box": _build_measurements_box(p, lang),
        "yarn_alternatives": _yarn_alt.render_html_aside(p, lang, domain="knit"),
        "warnings": _build_warnings(p, lang),
        "notes": _build_notes(p, lang),
        "pattern_sections": _build_pattern_sections(p),
        "crown_chart": _build_crown_chart(p),
        "extra_charts": _build_lace_chart(p, lang) + _build_colorwork_chart(p, lang),
        "abbreviations": _build_abbreviations(_KNIT_ABBREVIATIONS, lang),
        "abbr_intro": t("abbr.intro_knit", lang),
        "last_page": _build_last_page(lang, crochet=False),
    }
