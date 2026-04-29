#!/usr/bin/env python3
"""Build the static example catalogue for GitHub Pages.

For each demo construction we generate a Pattern, render it as a
self-contained HTML page (style.css inlined, paged.polyfill.js copied
alongside) and write it to ``_site/examples/<name>.html``. We also build
an ``_site/index.html`` catalogue page that lists every example with
name, domain, difficulty and a link.

Usage::

    python3 scripts/build_examples.py [--out _site]
    python3 scripts/build_examples.py --out _site --quiet
"""

from __future__ import annotations

import argparse
import html as _html
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "skills" / "strikning"))
sys.path.insert(0, str(_REPO / "skills" / "hækling"))


# ---------------------------------------------------------------------------
# Imports of the two skills happen lazily inside _examples() so that
# import-failures in one skill don't tear down catalogue building.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Example:
    """One demo entry in the catalogue."""
    slug: str               # filename-safe slug (no spaces, ASCII)
    title: str              # human-readable title
    domain: str             # "strik" or "hækl"
    difficulty: str         # "let" / "mellem" / "svær"
    summary: str            # short Danish blurb for the index card
    builder: Callable       # callable(): -> (pattern, render_html_fn)


def _knit_examples() -> list[Example]:
    """Five strik demos covering diverse constructions."""
    from knitlib import Gauge
    from knitlib.constructions import (
        HueSpec, generate_hue,
        TørklædeSpec, generate_tørklæde,
        RaglanSpec, generate_raglan,
        SokkerSpec, generate_sokker,
        HalfPiShawlSpec, generate_half_pi_shawl,
    )
    from lib.visualisering.html import render_html as render_strik

    g = Gauge(22, 30)
    g_sock = Gauge(28, 36)
    g_lace = Gauge(18, 28)

    return [
        Example(
            slug="strik-hue",
            title="Hue 56 cm",
            domain="strik",
            difficulty="let",
            summary="Klassisk rib-hue med 8-sektor krone, voksenstr. 56 cm.",
            builder=lambda: (
                generate_hue(HueSpec(
                    head_circumference_cm=56,
                    gauge=g,
                    name="Hue 56 cm",
                )),
                render_strik,
            ),
        ),
        Example(
            slug="strik-torklaede",
            title="Tørklæde 30×180",
            domain="strik",
            difficulty="let",
            summary="Glatstrikket rektangel-tørklæde med garter-kant.",
            builder=lambda: (
                generate_tørklæde(TørklædeSpec(
                    width_cm=30, length_cm=180, gauge=g,
                    name="Tørklæde 30×180",
                )),
                render_strik,
            ),
        ),
        Example(
            slug="strik-raglan",
            title="Top-down raglan, str. M",
            domain="strik",
            difficulty="mellem",
            summary="Raglan-sweater oppefra og ned, brystmål 94 cm.",
            builder=lambda: (
                generate_raglan(RaglanSpec(
                    bust_cm=94, gauge=g,
                    name="Top-down raglan, str. M",
                )),
                render_strik,
            ),
        ),
        Example(
            slug="strik-sokker",
            title="Sokker, fod 24 cm",
            domain="strik",
            difficulty="mellem",
            summary="Top-down sokker med kilehæl + gusset, voksen.",
            builder=lambda: (
                generate_sokker(SokkerSpec(
                    foot_circ_cm=22, foot_length_cm=24, gauge=g_sock,
                    name="Sokker, fod 24 cm",
                )),
                render_strik,
            ),
        ),
        Example(
            slug="strik-halfpi",
            title="Half-pi shawl",
            domain="strik",
            difficulty="svær",
            summary="Elizabeth Zimmermanns halv-pi-sjal med 5 fordoblinger.",
            builder=lambda: (
                generate_half_pi_shawl(HalfPiShawlSpec(
                    gauge=g_lace, n_doublings=5,
                    name="Half-pi shawl",
                )),
                render_strik,
            ),
        ),
    ]


def _croc_examples() -> list[Example]:
    """Five hækl demos covering diverse constructions."""
    from croclib.constructions import (
        AmigurumiSphereSpec, amigurumi_sphere,
        GrannySquareSpec, generate_granny_square,
        CrochetTørklædeSpec, generate_tørklæde,
        TunisianSpec, generate_tunisian,
        MandalaSpec, generate_mandala,
    )
    from croclib.html import render_html as render_haekl

    return [
        Example(
            slug="haekl-amigurumi",
            title="Amigurumi-kugle 8 cm",
            domain="hækl",
            difficulty="let",
            summary="Klassisk magic-ring kugle, fast-masker, 8 cm diameter.",
            builder=lambda: (
                amigurumi_sphere(AmigurumiSphereSpec(
                    diameter_cm=8, gauge_sc_per_cm=5,
                    name="Amigurumi-kugle 8 cm",
                )),
                render_haekl,
            ),
        ),
        Example(
            slug="haekl-granny",
            title="Granny square, 6 omgange",
            domain="hækl",
            difficulty="let",
            summary="Klassisk granny square, 6 omg., farveskift hver omg.",
            builder=lambda: (
                generate_granny_square(GrannySquareSpec(
                    rounds=6,
                    colors=["lyseblå", "rosa", "creme"],
                    name="Granny square, 6 omgange",
                )),
                render_haekl,
            ),
        ),
        Example(
            slug="haekl-torklaede",
            title="Hæklet tørklæde 25×150",
            domain="hækl",
            difficulty="let",
            summary="Stangmaske-tørklæde, rektangulært, 25×150 cm.",
            builder=lambda: (
                generate_tørklæde(CrochetTørklædeSpec(
                    width_cm=25, length_cm=150,
                    gauge_sts_per_cm=2.5, stitch_type="dc",
                    name="Hæklet tørklæde 25×150",
                )),
                render_haekl,
            ),
        ),
        Example(
            slug="haekl-tunisian",
            title="Tunisian-rektangel 20×30",
            domain="hækl",
            difficulty="mellem",
            summary="Tunesisk grundsting (TSS), rektangel 20×30 cm.",
            builder=lambda: (
                generate_tunisian(TunisianSpec(
                    width_cm=20, length_cm=30,
                    gauge_sts_per_cm=2.5, row_gauge_per_cm=1.5,
                    name="Tunisian-rektangel 20×30",
                )),
                render_haekl,
            ),
        ),
        Example(
            slug="haekl-mandala",
            title="Mandala, 8 omgange",
            domain="hækl",
            difficulty="mellem",
            summary="Rund mandala med skiftende stitches og farver pr. omg.",
            builder=lambda: (
                generate_mandala(MandalaSpec(
                    rounds=8, start_count=12,
                    colors=["sennep", "petroleum", "creme",
                            "rust", "støvet rosa", "skifer",
                            "oliven", "natur"],
                    name="Mandala, 8 omgange",
                )),
                render_haekl,
            ),
        ),
    ]


def _all_examples() -> list[Example]:
    return _knit_examples() + _croc_examples()


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------

_INDEX_TEMPLATE = """<!doctype html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Strikke- og hækle-eksempler</title>
<link rel="stylesheet" href="assets/style.css">
<style>
body {{ font-family: system-ui, sans-serif; max-width: 960px;
  margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
h1 {{ margin-bottom: 0.2rem; }}
.lead {{ color: #555; margin-top: 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem; margin-top: 1.5rem; }}
.card {{ border: 1px solid #ddd; border-radius: 8px; padding: 1rem;
  background: #fafafa; }}
.card h3 {{ margin: 0 0 0.5rem 0; font-size: 1.05rem; }}
.card a {{ text-decoration: none; color: #1a4f8b; }}
.card a:hover {{ text-decoration: underline; }}
.tag {{ display: inline-block; padding: 0.1rem 0.5rem; margin-right: 0.3rem;
  border-radius: 999px; font-size: 0.75rem; background: #eee; color: #333; }}
.tag.strik {{ background: #e8f0fa; color: #1a4f8b; }}
.tag.hækl  {{ background: #fdecec; color: #903; }}
.tag.let    {{ background: #e7f5e8; color: #275f2c; }}
.tag.mellem {{ background: #fff3d6; color: #7a5300; }}
.tag.svær   {{ background: #fde2e2; color: #903; }}
.summary {{ color: #444; font-size: 0.9rem; margin-top: 0.5rem; }}
footer {{ margin-top: 3rem; color: #888; font-size: 0.85rem; }}
</style>
</head>
<body>
<h1>Strikke- og hækle-eksempler</h1>
<p class="lead">Auto-genereret katalog over demo-opskrifter fra
<code>maskemania</code>. Hver side er en fuld, print-klar HTML-opskrift
med skema, materialer og maskemath.</p>

<h2>Strik</h2>
<div class="grid">
{strik_cards}
</div>

<h2>Hækl</h2>
<div class="grid">
{haekl_cards}
</div>

<footer>
Bygget af <code>scripts/build_examples.py</code>.
Se kildekoden på GitHub for at lave din egen variant.
</footer>
</body>
</html>
"""


def _card(ex: Example) -> str:
    return (
        '<div class="card">'
        f'<h3><a href="examples/{_html.escape(ex.slug)}.html">'
        f'{_html.escape(ex.title)}</a></h3>'
        f'<span class="tag {_html.escape(ex.domain)}">'
        f'{_html.escape(ex.domain)}</span>'
        f'<span class="tag {_html.escape(ex.difficulty)}">'
        f'{_html.escape(ex.difficulty)}</span>'
        f'<p class="summary">{_html.escape(ex.summary)}</p>'
        '</div>'
    )


def _build_index(examples: list[Example]) -> str:
    strik = "\n".join(_card(e) for e in examples if e.domain == "strik")
    haekl = "\n".join(_card(e) for e in examples if e.domain == "hækl")
    return _INDEX_TEMPLATE.format(strik_cards=strik, haekl_cards=haekl)


# ---------------------------------------------------------------------------
# Build entry-point
# ---------------------------------------------------------------------------


def build(out_dir: Path, *, quiet: bool = False) -> dict:
    """Build the full _site/. Returns a small report dict."""
    out_dir = out_dir.resolve()
    examples_dir = out_dir / "examples"
    assets_dir = out_dir / "assets"
    examples_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Copy shared assets (paged.polyfill.js, style.css) into _site/assets/.
    src_assets = _REPO / "lib" / "visualisering" / "assets"
    for f in src_assets.iterdir():
        if f.is_file():
            shutil.copy2(f, assets_dir / f.name)

    examples = _all_examples()
    written: list[str] = []

    for ex in examples:
        pattern, render = ex.builder()
        # paged_js_path is relative to the HTML file: ../assets/paged.polyfill.js
        html_text = render(pattern,
                           paged_js_path="../assets/paged.polyfill.js",
                           lang="da")
        target = examples_dir / f"{ex.slug}.html"
        target.write_text(html_text, encoding="utf-8")
        written.append(str(target.relative_to(out_dir)))
        if not quiet:
            print(f"  wrote {target.relative_to(out_dir)}")

    index_path = out_dir / "index.html"
    index_path.write_text(_build_index(examples), encoding="utf-8")
    if not quiet:
        print(f"  wrote {index_path.relative_to(out_dir)}")

    return {
        "out_dir": str(out_dir),
        "examples": written,
        "index": str(index_path.relative_to(out_dir)),
        "count": len(examples),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build_examples",
        description="Build _site/ catalogue for GitHub Pages.",
    )
    parser.add_argument("--out", type=Path, default=Path("_site"),
                        help="output directory (default: _site)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    report = build(args.out, quiet=args.quiet)
    if not args.quiet:
        print(f"Built {report['count']} examples → {report['out_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
