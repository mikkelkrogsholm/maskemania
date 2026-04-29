#!/usr/bin/env python3
"""Visual preview / live-reload server for strikning patterns.

Two modes:

* **Static component preview** (legacy): ``preview.py cover`` etc. dumps a
  single component wrapped in the page shell to stdout — useful for
  iterating on a single component without re-rendering the whole pattern.

* **Live preview server** (new): ``preview.py --serve --construction hue
  --head 56 --sts 22 --rows 30`` starts a local HTTP server at
  http://localhost:8765/. Editing any HTML / Python source under the
  watched directories triggers a browser reload via JS polling.

Both modes use pure stdlib — no ``watchdog``, no ``flask``.
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))    # for `lib.visualisering`
sys.path.insert(0, str(_SKILL))   # for `knitlib`

from knitlib import Gauge  # noqa: E402
from knitlib.constructions import (  # noqa: E402
    HueSpec, generate_hue,
    RaglanSpec, generate_raglan,
    TørklædeSpec, generate_tørklæde,
    SokkerSpec, generate_sokker,
    BottomUpSweaterSpec, generate_bottom_up_sweater,
)
from lib.visualisering import html as html_mod  # noqa: E402
from lib.visualisering.html import render_html  # noqa: E402
from lib.visualisering.preview import serve_pattern, reload_script_tag  # noqa: E402

_VIS_DIR = _REPO / "lib" / "visualisering"


# Sample data — used by the static component previews
SAMPLE_HUE = generate_hue(HueSpec(
    head_circumference_cm=56, gauge=Gauge(22, 30), name="Eksempel-hue",
))
SAMPLE_RAGLAN = generate_raglan(RaglanSpec(
    bust_cm=94, gauge=Gauge(22, 30), ease_cm=5, name="Eksempel-raglan",
))


def _wrap(content: str, title: str = "Preview") -> str:
    css = (_VIS_DIR / "assets" / "style.css").read_text()
    return f"""<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{css}</style>
<style>
  body {{ background: #f0f0f0; padding: 1cm; }}
  .preview-page {{
    width: 210mm; min-height: 100mm;
    background: white;
    margin: 0 auto;
    padding: 2.2cm 2.4cm;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  }}
  .preview-page.cover-page {{ padding: 0; }}
  .preview-label {{
    max-width: 210mm; margin: 0 auto 1em auto;
    font-family: 'Inter', sans-serif; font-size: 11pt;
    color: #666; text-transform: uppercase; letter-spacing: 0.1em;
  }}
</style>
</head>
<body>
<p class="preview-label">{title}</p>
<div class="preview-page {('cover-page' if 'cover' in title.lower() else '')}">
{content}
</div>
</body></html>"""


def preview_cover() -> str:
    return _wrap(html_mod._build_cover(SAMPLE_RAGLAN), "Cover (raglan)")


def preview_schematic() -> str:
    raglan = html_mod._build_schematics_default(SAMPLE_RAGLAN)
    hue = html_mod._build_schematics_default(SAMPLE_HUE)
    body = (
        '<h2>Skematik (raglan)</h2>'
        '<section class="schematic-page">' + raglan + '</section>'
        '<hr style="margin:3em 0;">'
        '<h2>Skematik (hue)</h2>'
        '<section class="schematic-page">' + hue + '</section>'
    )
    return _wrap(body, "Schematics")


def preview_materials() -> str:
    body = (
        '<h2>Materialer & mål</h2>'
        '<div class="materials-grid">'
        + html_mod._build_materials_box(SAMPLE_RAGLAN)
        + html_mod._build_measurements_box(SAMPLE_RAGLAN)
        + '</div>'
        + html_mod._build_warnings(SAMPLE_RAGLAN)
    )
    return _wrap(body, "Materials & measurements (raglan)")


def preview_pattern_steps() -> str:
    body = (
        '<h2>Opskrift</h2>'
        + html_mod._build_notes(SAMPLE_RAGLAN)
        + html_mod._build_pattern_sections(SAMPLE_RAGLAN)
    )
    return _wrap(body, "Pattern steps (raglan)")


def preview_crown_chart() -> str:
    body = html_mod._build_crown_chart(SAMPLE_HUE)
    return _wrap(body, "Crown chart (hue)")


def preview_abbreviations() -> str:
    body = (
        '<h2>Forkortelser</h2>'
        '<p>Dansk strikkesprog er ikke standardiseret. Denne opskrift bruger '
        'nedenstående konvention.</p>'
        + html_mod._build_abbreviations()
    )
    return _wrap(body, "Abbreviations")


PREVIEWS = {
    "cover": preview_cover,
    "schematic": preview_schematic,
    "materials": preview_materials,
    "pattern_steps": preview_pattern_steps,
    "crown_chart": preview_crown_chart,
    "abbreviations": preview_abbreviations,
}


def _build_pattern(args) -> "object":
    c = args.construction
    if c == "hue":
        return generate_hue(HueSpec(
            head_circumference_cm=args.head, gauge=Gauge(args.sts, args.rows),
            name=args.name or "Hue",
        ))
    if c in ("tørklæde", "scarf"):
        return generate_tørklæde(TørklædeSpec(
            width_cm=args.width, length_cm=args.length,
            gauge=Gauge(args.sts, args.rows),
            name=args.name or "Tørklæde",
        ))
    if c == "raglan":
        return generate_raglan(RaglanSpec(
            bust_cm=args.bust, gauge=Gauge(args.sts, args.rows), ease_cm=5,
            name=args.name or "Top-down raglan",
        ))
    if c in ("sokker", "socks"):
        return generate_sokker(SokkerSpec(
            foot_circ_cm=args.foot, foot_length_cm=args.foot_length,
            gauge=Gauge(args.sts, args.rows),
            name=args.name or "Sokker",
        ))
    if c in ("sweater", "bottom-up"):
        return generate_bottom_up_sweater(BottomUpSweaterSpec(
            bust_cm=args.bust, gauge=Gauge(args.sts, args.rows), ease_cm=5,
            name=args.name or "Sweater",
        ))
    raise SystemExit(f"unknown construction: {c}")


def main() -> int:
    parser = argparse.ArgumentParser(prog="preview")
    parser.add_argument("--serve", action="store_true",
                        help="start live preview server (otherwise: static "
                             "component preview)")
    parser.add_argument("component", nargs="?", default=None,
                        help=("static preview component name; one of "
                              + ", ".join(PREVIEWS)))
    parser.add_argument("--construction", default="hue",
                        choices=["hue", "tørklæde", "scarf", "raglan",
                                  "sokker", "socks", "sweater", "bottom-up"])
    parser.add_argument("--head", type=float, default=56)
    parser.add_argument("--sts", type=float, default=22)
    parser.add_argument("--rows", type=float, default=30)
    parser.add_argument("--bust", type=float, default=94)
    parser.add_argument("--width", type=float, default=30)
    parser.add_argument("--length", type=float, default=180)
    parser.add_argument("--foot", type=float, default=22)
    parser.add_argument("--foot-length", type=float, default=24)
    parser.add_argument("--name", default=None)
    parser.add_argument("--lang", choices=["da", "en"], default="da")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.serve:
        # Use --construction defaults if user supplied sock/sweater specifics
        # adjust for sock gauge (default 28/36 makes more sense)
        if args.construction in ("sokker", "socks") and args.sts == 22:
            args.sts, args.rows = 28, 36

        def render() -> str:
            pattern = _build_pattern(args)
            return render_html(pattern, paged_js_path="/paged.polyfill.js",
                               lang=args.lang,
                               reload_script=reload_script_tag())

        watch = [
            _VIS_DIR / "assets",
            _VIS_DIR / "components",
            _VIS_DIR / "templates",
            _VIS_DIR / "lang",
            _SKILL / "knitlib",
            _SKILL / "scripts",
        ]
        serve_pattern(render, watch=watch, port=args.port,
                      paged_js_path=_VIS_DIR / "assets" / "paged.polyfill.js")
        return 0

    if args.component is None or args.component not in PREVIEWS:
        parser.print_usage()
        print(f"static components: {', '.join(PREVIEWS)}", file=sys.stderr)
        return 2
    print(PREVIEWS[args.component]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
