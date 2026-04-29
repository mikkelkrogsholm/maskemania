#!/usr/bin/env python3
"""Live preview server for hækling patterns.

Usage::

    preview.py --serve --construction granny --rounds 6
    preview.py --serve --construction amigurumi --diameter 8 --gauge 5
    preview.py --serve --construction filet --width 10 --height 10
    preview.py --serve --construction tunisian --width 20 --length 30

Watches the shared lib + the croclib + scripts so editing any of them
auto-reloads the browser. Pure stdlib.
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_SKILL))

from croclib.constructions import (  # noqa: E402
    AmigurumiSphereSpec, amigurumi_sphere,
    AmigurumiCylinderSpec, amigurumi_cylinder,
    GrannySquareSpec, generate_granny_square,
    CrochetTørklædeSpec, generate_tørklæde,
    FiletSpec, generate_filet,
    TunisianSpec, generate_tunisian,
)
from croclib.html import render_html  # noqa: E402
from lib.visualisering.preview import serve_pattern, reload_script_tag  # noqa: E402

_VIS_DIR = _REPO / "lib" / "visualisering"


def _build(args) -> "object":
    c = args.construction
    if c == "amigurumi":
        return amigurumi_sphere(AmigurumiSphereSpec(
            diameter_cm=args.diameter, gauge_sc_per_cm=args.gauge,
            equator_rounds=args.equator,
            name=args.name or "Amigurumi-kugle",
        ))
    if c == "cylinder":
        return amigurumi_cylinder(AmigurumiCylinderSpec(
            diameter_cm=args.diameter, height_cm=args.height,
            gauge_sc_per_cm=args.gauge,
            name=args.name or "Amigurumi-cylinder",
        ))
    if c == "granny":
        return generate_granny_square(GrannySquareSpec(
            rounds=args.rounds,
            name=args.name or "Granny",
        ))
    if c in ("tørklæde", "scarf"):
        return generate_tørklæde(CrochetTørklædeSpec(
            width_cm=args.width, length_cm=args.length,
            gauge_sts_per_cm=args.gauge,
            name=args.name or "Hæklet tørklæde",
        ))
    if c == "filet":
        # default to a checkerboard if no grid is supplied
        grid = "\n".join(
            "".join("X" if (r + c) % 2 == 0 else "." for c in range(args.width))
            for r in range(args.height)
        )
        return generate_filet(FiletSpec(
            width_cells=args.width, height_cells=args.height, grid=grid,
            name=args.name or "Filet",
        ))
    if c == "tunisian":
        return generate_tunisian(TunisianSpec(
            width_cm=args.width, length_cm=args.length,
            gauge_sts_per_cm=args.gauge,
            name=args.name or "Tunisian",
        ))
    raise SystemExit(f"unknown construction: {c}")


def main() -> int:
    parser = argparse.ArgumentParser(prog="preview")
    parser.add_argument("--serve", action="store_true",
                        help="start live preview server")
    parser.add_argument("--construction", default="granny",
                        choices=["amigurumi", "cylinder", "granny",
                                  "tørklæde", "scarf", "filet", "tunisian"])
    parser.add_argument("--diameter", type=float, default=8)
    parser.add_argument("--gauge", type=float, default=5)
    parser.add_argument("--equator", type=int, default=0)
    parser.add_argument("--rounds", type=int, default=6)
    parser.add_argument("--width", type=int_or_float, default=10)
    parser.add_argument("--height", type=int_or_float, default=10)
    parser.add_argument("--length", type=float, default=30)
    parser.add_argument("--name", default=None)
    parser.add_argument("--lang", choices=["da", "en"], default="da")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    # Coerce filet/tunisian width/height
    if args.construction == "filet":
        args.width = int(args.width)
        args.height = int(args.height)
    elif args.construction == "tunisian":
        args.width = float(args.width)
        args.length = float(args.length)
    elif args.construction in ("tørklæde", "scarf"):
        args.width = float(args.width)

    if not args.serve:
        # No --serve: just dump the rendered HTML to stdout.
        pattern = _build(args)
        print(render_html(pattern, paged_js_path="paged.polyfill.js",
                          lang=args.lang))
        return 0

    def render() -> str:
        pattern = _build(args)
        return render_html(pattern, paged_js_path="/paged.polyfill.js",
                           lang=args.lang,
                           reload_script=reload_script_tag())

    watch = [
        _VIS_DIR / "assets",
        _VIS_DIR / "components",
        _VIS_DIR / "templates",
        _VIS_DIR / "lang",
        _SKILL / "croclib",
        _SKILL / "scripts",
    ]
    serve_pattern(render, watch=watch, port=args.port,
                  paged_js_path=_VIS_DIR / "assets" / "paged.polyfill.js")
    return 0


def int_or_float(s: str):
    """Permit ``20`` or ``20.5`` from argparse without committing to a type."""
    try:
        return int(s)
    except ValueError:
        return float(s)


if __name__ == "__main__":
    raise SystemExit(main())
