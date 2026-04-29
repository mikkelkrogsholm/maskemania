#!/usr/bin/env python3
"""CLI for generating crochet patterns.

Usage::

    generate.py amigurumi --diameter 8 --gauge 5 [--equator 0]
    generate.py granny --rounds 6 [--colors red,blue,green]
    generate.py tørklæde --width 25 --length 150 --gauge 2.5 [--stitch dc]
    generate.py filet --width 12 --height 12 --grid '...'
    generate.py tunisian --width 20 --length 30 --gauge 2.5

Output is markdown by default. ``--format json`` emits the structured
intermediate (machine-readable). ``--format html --out FILE.html`` writes
a print-ready HTML using the shared :mod:`lib.visualisering` template.
``--pdf FILE.pdf`` writes a PDF directly (requires Chrome / Chromium).
``--lang en`` produces English output (default ``da``).

Materials flags (``--garn``, ``--garnløbe``, ``--nål``, ``--designer``,
``--år``, ``--note``) flow through to the materials box.
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Repo layout:
#   <repo>/lib/visualisering/...        ← shared package
#   <repo>/skills/hækling/croclib/...   ← crochet-specific package
#   <repo>/skills/hækling/scripts/generate.py  (this file)
_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))    # for `lib.visualisering`
sys.path.insert(0, str(_SKILL))   # for `croclib`

from croclib.constructions import (  # noqa: E402
    AmigurumiSphereSpec, amigurumi_sphere,
    AmigurumiCylinderSpec, amigurumi_cylinder,
    AmigurumiFigurSpec, amigurumi_figur,
    GrannySquareSpec, generate_granny_square,
    CrochetTørklædeSpec, generate_tørklæde,
    FiletSpec, generate_filet,
    TunisianSpec, generate_tunisian,
    C2CBlanketSpec, generate_c2c_blanket,
    MandalaSpec, generate_mandala,
    Pattern,
)
from croclib.html import render_html  # noqa: E402
from lib.visualisering.html import set_prosa_enabled  # noqa: E402
from lib.visualisering.yarn_db import (  # noqa: E402
    auto_gauge_from_yarn, lookup_yarn,
)
from lib.visualisering import yarn_alternatives as _yarn_alt  # noqa: E402
from lib.visualisering.cli_helpers import (  # noqa: E402
    add_common_args,
    add_metadata_args,
    apply_yarn_defaults,
    attach_metadata,
    metadata_from_args,
    route_output,
)

_PAGED_JS_PATH = _REPO / "lib" / "visualisering" / "assets" / "paged.polyfill.js"


def to_markdown(p: Pattern) -> str:
    """Render a Pattern as a structured markdown skeleton."""
    lines: list[str] = []
    lines.append(f"# {p.name}")
    lines.append("")
    lines.append(f"**Konstruktion:** {p.construction}")
    lines.append("")
    md = p.inputs.get("metadata") or {}
    if md:
        lines.append("## Materialer")
        for k, label in [("yarn", "Garn"), ("yarn_run", "Løbelængde"),
                          ("hook", "Nål"), ("designer", "Designer"),
                          ("year", "År")]:
            if md.get(k):
                lines.append(f"- **{label}:** {md[k]}")
        for n in md.get("notes") or []:
            lines.append(f"- _{n}_")
        lines.append("")
    lines.append("## Input")
    lines.append("")
    for k, v in p.inputs.items():
        if k in ("metadata", "_domain", "grid", "tunisian_rows"):
            continue
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    for sec in p.sections:
        lines.append(f"## {sec.title}")
        lines.append(f"_({sec.sts_before} m → {sec.sts_after} m)_")
        lines.append("")
        for st in sec.steps:
            note = f"  — _{st.note}_" if st.note else ""
            lines.append(f"- {st.text} **({st.sts_after} m)**{note}")
        lines.append("")
    if p.notes:
        lines.append("## Noter")
        for n in p.notes:
            lines.append(f"- {n}")
        lines.append("")
    if p.warnings:
        lines.append("## ⚠️ Advarsler")
        for w in p.warnings:
            lines.append(f"- {w}")
        lines.append("")
    if (p.inputs or {}).get("yarn_alternatives"):
        alt_md = _yarn_alt.render_markdown(p, lang="da")
        if alt_md:
            lines.append(alt_md)
    lines.append("---")
    lines.append("")
    lines.append(
        "_Genereret af hækling-skill. Maskeantal er valideret. Lav altid en "
        "prøvelap og test-hækl før du stoler på opskriften._"
    )
    return "\n".join(lines)


def _crochet_metadata(args: argparse.Namespace) -> dict:
    """Crochet-domain metadata extraction (uses yarn DB lookup)."""
    return metadata_from_args(args, lookup_yarn=lookup_yarn)


def cmd_amigurumi(args: argparse.Namespace) -> Pattern:
    p = amigurumi_sphere(AmigurumiSphereSpec(
        diameter_cm=args.diameter,
        gauge_sc_per_cm=args.gauge,
        start_count=args.start,
        equator_rounds=args.equator,
        name=args.name or "Amigurumi-kugle",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def cmd_cylinder(args: argparse.Namespace) -> Pattern:
    p = amigurumi_cylinder(AmigurumiCylinderSpec(
        diameter_cm=args.diameter,
        height_cm=args.height,
        gauge_sc_per_cm=args.gauge,
        row_gauge_per_cm=args.row_gauge or args.gauge,
        start_count=args.start,
        closed_top=not args.open_top,
        name=args.name or "Amigurumi-cylinder",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def cmd_granny(args: argparse.Namespace) -> Pattern:
    colors = (args.colors.split(",") if args.colors else None)
    p = generate_granny_square(GrannySquareSpec(
        rounds=args.rounds,
        colors=colors,
        name=args.name or "Granny square",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def cmd_tørklæde(args: argparse.Namespace) -> Pattern:
    p = generate_tørklæde(CrochetTørklædeSpec(
        width_cm=args.width,
        length_cm=args.length,
        gauge_sts_per_cm=args.gauge,
        stitch_type=args.stitch,
        row_gauge_per_cm=args.row_gauge,
        name=args.name or "Hæklet tørklæde",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def cmd_filet(args: argparse.Namespace) -> Pattern:
    grid_str: str
    if args.grid_file:
        grid_str = Path(args.grid_file).read_text(encoding="utf-8")
    elif args.grid:
        grid_str = args.grid
    else:
        # No grid specified: generate a checkerboard placeholder
        grid_str = "\n".join(
            "".join("X" if (r + c) % 2 == 0 else "." for c in range(args.width))
            for r in range(args.height)
        )
    p = generate_filet(FiletSpec(
        width_cells=args.width,
        height_cells=args.height,
        grid=grid_str,
        gauge_sts_per_cm=args.gauge,
        row_gauge_per_cm=args.row_gauge,
        name=args.name or "Filet hækling",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def cmd_tunisian(args: argparse.Namespace) -> Pattern:
    p = generate_tunisian(TunisianSpec(
        width_cm=args.width,
        length_cm=args.length,
        gauge_sts_per_cm=args.gauge,
        row_gauge_per_cm=args.row_gauge,
        base_stitch=args.base,
        name=args.name or "Tunisian-rektangel",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def cmd_c2c(args: argparse.Namespace) -> Pattern:
    colors = args.colors.split(",") if args.colors else None
    p = generate_c2c_blanket(C2CBlanketSpec(
        blocks_wide=args.width,
        blocks_high=args.height,
        blocks_per_cm=args.blocks_per_cm,
        colors=colors,
        name=args.name or "C2C-tæppe",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def cmd_figur(args: argparse.Namespace) -> Pattern:
    species = args.species
    if species is None:
        species = "kanin" if args.construction == "kanin" else "bjørn"
    p = amigurumi_figur(AmigurumiFigurSpec(
        scale_cm=args.scale,
        species=species,
        gauge_sc_per_cm=args.gauge or 5.0,
        row_gauge_per_cm=args.row_gauge or args.gauge or 5.0,
        start_count=args.start,
        name=args.name or "",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def cmd_mandala(args: argparse.Namespace) -> Pattern:
    colors = args.colors.split(",") if args.colors else None
    p = generate_mandala(MandalaSpec(
        rounds=args.rounds,
        start_count=args.start,
        colors=colors,
        name=args.name or "Mandala",
    ), lang=args.lang)
    return attach_metadata(p, _crochet_metadata(args))


def _add_materials_flags(parser: argparse.ArgumentParser) -> None:
    """Local wrapper around :func:`add_metadata_args` for the crochet domain."""
    add_metadata_args(parser, hook_or_needle="nål")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="hækling",
        description="Genererer parametriske hækleopskrifter med valideret maskemath.",
    )
    add_common_args(parser)
    sub = parser.add_subparsers(dest="construction", required=True)

    # --- amigurumi (sphere) ---
    a = sub.add_parser("amigurumi", aliases=["sphere", "kugle"],
                       help="Amigurumi-kugle (sphere)")
    a.add_argument("--diameter", type=float, required=True)
    a.add_argument("--gauge", type=float, default=None,
                   help="m/cm (kan udledes af --garn hvis udeladt)")
    a.add_argument("--start", type=int, default=6)
    a.add_argument("--equator", type=int, default=0)
    _add_materials_flags(a)
    a.set_defaults(func=cmd_amigurumi)

    # --- cylinder ---
    c = sub.add_parser("cylinder", help="Amigurumi-cylinder (lukket eller åben)")
    c.add_argument("--diameter", type=float, required=True)
    c.add_argument("--height", "--højde", "--hoejde", type=float, required=True,
                   dest="height")
    c.add_argument("--gauge", type=float, default=None)
    c.add_argument("--row-gauge", "--række-gauge", "--raekke-gauge",
                   type=float, default=None, dest="row_gauge")
    c.add_argument("--start", type=int, default=6)
    c.add_argument("--open-top", action="store_true")
    _add_materials_flags(c)
    c.set_defaults(func=cmd_cylinder)

    # --- granny ---
    g = sub.add_parser("granny", help="Klassisk granny square")
    g.add_argument("--rounds", type=int, required=True)
    g.add_argument("--colors", default=None)
    _add_materials_flags(g)
    g.set_defaults(func=cmd_granny)

    # --- tørklæde ---
    t = sub.add_parser("tørklæde", aliases=["torklaede", "scarf"],
                       help="Hæklet tørklæde (rektangel)")
    t.add_argument("--width", "--bredde", type=float, required=True,
                   dest="width")
    t.add_argument("--length", "--længde", "--laengde", type=float, required=True,
                   dest="length")
    t.add_argument("--gauge", type=float, default=None)
    t.add_argument("--row-gauge", "--række-gauge", "--raekke-gauge",
                   type=float, default=None, dest="row_gauge")
    t.add_argument("--stitch", choices=["sc", "hdc", "dc", "tr"], default="dc")
    _add_materials_flags(t)
    t.set_defaults(func=cmd_tørklæde)

    # --- filet ---
    f = sub.add_parser("filet", help="Filet hækling — pixel-grid")
    f.add_argument("--width", "--bredde", type=int, required=True, dest="width",
                   help="grid-bredde i celler")
    f.add_argument("--height", "--højde", "--hoejde", type=int, required=True,
                   dest="height", help="grid-højde i celler")
    f.add_argument("--grid", type=str, default=None,
                   help="multi-line string. X/# = fyldt, ./0/space = åben")
    f.add_argument("--grid-file", type=Path, default=None,
                   help="læs grid fra fil i stedet")
    f.add_argument("--gauge", type=float, default=2.0,
                   help="dc gauge (m/cm) — default 2.0")
    f.add_argument("--row-gauge", "--række-gauge", "--raekke-gauge",
                   type=float, default=0.5, dest="row_gauge")
    _add_materials_flags(f)
    f.set_defaults(func=cmd_filet)

    # --- tunisian ---
    tu = sub.add_parser("tunisian", help="Tunisian — TSS rektangel")
    tu.add_argument("--width", "--bredde", type=float, required=True,
                    dest="width", help="bredde i cm")
    tu.add_argument("--length", "--længde", "--laengde", type=float, required=True,
                    dest="length", help="længde i cm")
    tu.add_argument("--gauge", type=float, default=2.5,
                    help="m/cm i grundsting")
    tu.add_argument("--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, default=1.5, dest="row_gauge")
    tu.add_argument("--base", choices=["tss", "tks", "tps"], default="tss")
    _add_materials_flags(tu)
    tu.set_defaults(func=cmd_tunisian)

    # --- c2c blanket ---
    c2c = sub.add_parser("c2c", aliases=["c2c-blanket", "tæppe"],
                         help="Corner-to-corner tæppe (diagonal-blokke)")
    c2c.add_argument("--width", "--bredde", type=int, required=True,
                     dest="width", help="bredde i blokke")
    c2c.add_argument("--height", "--højde", "--hoejde", type=int, required=True,
                     dest="height", help="højde i blokke")
    c2c.add_argument("--blocks-per-cm", type=float, default=1.0,
                     help="blokke pr. cm (default 1.0)")
    c2c.add_argument("--colors", default=None,
                     help="komma-separeret stribefarver, fx 'rød,blå,grøn'")
    _add_materials_flags(c2c)
    c2c.set_defaults(func=cmd_c2c)

    # --- figur (amigurumi-figur, krop+hoved+ører+arme+ben) ---
    fig = sub.add_parser("figur", aliases=["bear", "kanin", "bjørn"],
                          help="Sammensat amigurumi-figur (bjørn/kanin)")
    fig.add_argument("--scale", type=float, default=12.0,
                     help="samlet højde i cm (default 12)")
    fig.add_argument("--gauge", type=float, default=None,
                     help="m/cm (default 5.0 hvis ikke angivet)")
    fig.add_argument("--row-gauge", "--række-gauge", "--raekke-gauge",
                     type=float, default=None, dest="row_gauge")
    fig.add_argument("--species", choices=["bjørn", "kanin"], default=None,
                     help="art (default afhænger af alias: bjørn/bear → bjørn, "
                          "kanin → kanin)")
    fig.add_argument("--start", type=int, default=6)
    _add_materials_flags(fig)
    fig.set_defaults(func=cmd_figur)

    # --- mandala ---
    md = sub.add_parser("mandala", help="Rund mandala med skiftende stitches pr. omg")
    md.add_argument("--rounds", type=int, required=True,
                    help="antal omgange")
    md.add_argument("--start", type=int, default=12,
                    help="masker i magic ring (default 12)")
    md.add_argument("--colors", default=None,
                    help="komma-separeret farver, en pr. omg")
    _add_materials_flags(md)
    md.set_defaults(func=cmd_mandala)

    args = parser.parse_args()
    apply_yarn_defaults(args, auto_gauge_from_yarn=auto_gauge_from_yarn,
                        domain="crochet")
    set_prosa_enabled(not getattr(args, "no_prosa", False))
    if hasattr(args, "gauge") and getattr(args, "gauge", None) in (None, 0):
        # gauge is mandatory for constructions that compute physical size.
        # Constructions with a hardcoded default (filet, tunisian) will
        # already have a non-None default; this only fires for the original
        # required=True commands (amigurumi/cylinder/tørklæde) when neither
        # --gauge nor a known --garn was supplied.
        if args.construction in {"amigurumi", "sphere", "kugle",
                                  "cylinder",
                                  "tørklæde", "torklaede", "scarf"}:
            print(
                "error: --gauge is required (or pass --garn with a known "
                "yarn so it can be inferred)",
                file=sys.stderr,
            )
            return 2
    pattern = args.func(args)

    # Garn-alternativer (Fase 5 iter 5)
    if getattr(args, "substitut", False):
        garn = getattr(args, "garn", None)
        if not garn:
            print("hint: --substitut kræver --garn med et kendt garn — "
                  "tilføj fx --garn 'Drops Lima' for at få alternativer.",
                  file=sys.stderr)
        else:
            n = _yarn_alt.attach_alternatives(
                pattern, garn, lang=args.lang, domain="crochet")
            if n == 0:
                print(f"hint: '{garn}' findes ikke i garn-databasen — "
                      "ingen alternativer kunne foreslås.", file=sys.stderr)

    return route_output(
        pattern, args,
        render_html=render_html,
        paged_js_path=_PAGED_JS_PATH,
        to_markdown=to_markdown,
        social_handle="@hækleopskrift",
        set_domain="crochet",
    )


if __name__ == "__main__":
    raise SystemExit(main())
