#!/usr/bin/env python3
"""CLI for generating knitting patterns.

Usage:
  generate.py hue --head 56 --sts 22 --rows 30 [--ease -3] [--height 21]
  generate.py tørklæde --width 30 --length 180 --sts 22 --rows 30
  generate.py raglan --bust 94 --sts 22 --rows 30 [--ease 5] [--yoke 21]
  generate.py sokker --foot 22 --foot-length 24 --sts 28 --rows 36
  generate.py sweater --bust 94 --sts 22 --rows 30
  generate.py --help

Output is markdown by default. ``--format json`` emits the structured
intermediate. ``--format html --out FILE.html`` writes a print-ready HTML.
``--pdf FILE.pdf`` writes a PDF directly (requires Chrome/Chromium).
``--lang en`` produces English output (default ``da``).

Materials flags (``--garn``, ``--garnløbe``, ``--pinde``, ``--designer``,
``--år``, ``--note``) flow into the pattern's metadata and render in the
materials box / cover.
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Make `lib.visualisering` and `knitlib` importable when this file is invoked
# directly. Repo layout:
#   <repo>/lib/visualisering/...        ← shared package
#   <repo>/skills/strikning/knitlib/... ← knit-specific package
#   <repo>/skills/strikning/scripts/generate.py  (this file)
_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))    # for `lib.visualisering`
sys.path.insert(0, str(_SKILL))   # for `knitlib`

from knitlib import Gauge  # noqa: E402
from knitlib.sizing import (  # noqa: E402
    child_size, known_age_labels,
)
from knitlib.constructions import (  # noqa: E402
    HueSpec, generate_hue,
    TørklædeSpec, generate_tørklæde,
    RaglanSpec, generate_raglan,
    SokkerSpec, generate_sokker,
    BottomUpSweaterSpec, generate_bottom_up_sweater,
    CompoundRaglanSpec, generate_compound_raglan,
    HalfPiShawlSpec, generate_half_pi_shawl,
    YokeStrandedSpec, generate_yoke_stranded,
    ShortRowsShawlSpec, generate_short_rows_shawl,
    LaceShawlSpec, generate_lace_shawl,
    Pattern,
)
from lib.visualisering.html import render_html, set_prosa_enabled  # noqa: E402
from lib.visualisering import yarn_alternatives as _yarn_alt  # noqa: E402
from lib.visualisering.cli_helpers import (  # noqa: E402
    add_common_args,
    add_metadata_args,
    apply_age_defaults,
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
                          ("needles", "Pinde"), ("designer", "Designer"),
                          ("year", "År")]:
            if md.get(k):
                lines.append(f"- **{label}:** {md[k]}")
        for n in md.get("notes") or []:
            lines.append(f"- _{n}_")
        lines.append("")
    lines.append("## Input")
    lines.append("")
    for k, v in p.inputs.items():
        if k in ("metadata", "_domain"):
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
        "_Genereret af strikkeopskrift-skill. Maskeantal er valideret. "
        "Skriv altid en prøvelap og test-strik før du stoler på opskriften._"
    )
    return "\n".join(lines)


def cmd_hue(args: argparse.Namespace) -> Pattern:
    p = generate_hue(HueSpec(
        head_circumference_cm=args.head,
        gauge=Gauge(args.sts, args.rows),
        ease_cm=args.ease,
        rib_height_cm=args.rib,
        total_height_cm=args.height,
        sectors=args.sectors,
        name=args.name or "Hue",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_tørklæde(args: argparse.Namespace) -> Pattern:
    p = generate_tørklæde(TørklædeSpec(
        width_cm=args.width,
        length_cm=args.length,
        gauge=Gauge(args.sts, args.rows),
        edge_sts=args.edge_sts,
        edge_rows=args.edge_rows,
        pattern_repeat_sts=args.repeat_sts,
        pattern_repeat_rows=args.repeat_rows,
        pattern_description=args.pattern,
        name=args.name or "Tørklæde",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_raglan(args: argparse.Namespace) -> Pattern:
    p = generate_raglan(RaglanSpec(
        bust_cm=args.bust,
        gauge=Gauge(args.sts, args.rows),
        ease_cm=args.ease,
        yoke_depth_cm=args.yoke,
        body_length_cm=args.body_length,
        sleeve_length_cm=args.sleeve_length,
        upper_arm_cm=args.upper_arm,
        wrist_cm=args.wrist,
        neck_circumference_cm=args.neck,
        rib_height_cm=args.rib,
        underarm_cast_on_cm=args.underarm,
        name=args.name or "Top-down raglan",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_sokker(args: argparse.Namespace) -> Pattern:
    p = generate_sokker(SokkerSpec(
        foot_circ_cm=args.foot,
        foot_length_cm=args.foot_length,
        gauge=Gauge(args.sts, args.rows),
        leg_length_cm=args.leg,
        rib_height_cm=args.rib,
        neg_ease_pct=args.neg_ease,
        shoe_size=args.shoe_size,
        name=args.name or "Sokker",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_compound_raglan(args: argparse.Namespace) -> Pattern:
    p = generate_compound_raglan(CompoundRaglanSpec(
        bust_cm=args.bust,
        upper_arm_cm=args.upper_arm,
        gauge=Gauge(args.sts, args.rows),
        ease_cm=args.ease,
        yoke_depth_cm=args.yoke,
        body_length_cm=args.body_length,
        sleeve_length_cm=args.sleeve_length,
        wrist_cm=args.wrist,
        neck_circumference_cm=args.neck,
        rib_height_cm=args.rib,
        underarm_cast_on_cm=args.underarm,
        name=args.name or "Compound raglan",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_half_pi(args: argparse.Namespace) -> Pattern:
    motifs = list(args.motif) if getattr(args, "motif", None) else None
    p = generate_half_pi_shawl(HalfPiShawlSpec(
        gauge=Gauge(args.sts, args.rows),
        n_doublings=args.doublings,
        cast_on_sts=args.cast_on,
        edge_sts=args.edge,
        lace_motifs=motifs,
        name=args.name or "Half-pi shawl",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_short_rows(args: argparse.Namespace) -> Pattern:
    p = generate_short_rows_shawl(ShortRowsShawlSpec(
        gauge=Gauge(args.sts, args.rows),
        cast_on=args.cast_on,
        increase_rows=args.increase_rows,
        short_row_cadence=args.short_row_cadence,
        short_row_setback=args.short_row_setback,
        edge_garter=args.edge_garter,
        name=args.name or "Korte rækker shawl",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_lace_shawl(args: argparse.Namespace) -> Pattern:
    p = generate_lace_shawl(LaceShawlSpec(
        width_cm=args.width,
        length_cm=args.length,
        gauge=Gauge(args.sts, args.rows),
        repeat=args.repeat,
        edge_sts=args.edge_sts,
        garter_band_cm=args.garter_band,
        name=args.name or "Lace shawl",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_yoke_stranded(args: argparse.Namespace) -> Pattern:
    motif_name = getattr(args, "motif", None) or "stars"
    # repeat_width must match the chosen motif's width for shaping math.
    from lib.visualisering.motifs import MOTIFS as _MOTIFS  # local import
    repeat_width = args.repeat
    if motif_name in _MOTIFS:
        repeat_width = _MOTIFS[motif_name]["width"]
    p = generate_yoke_stranded(YokeStrandedSpec(
        bust_cm=args.bust,
        gauge=Gauge(args.sts, args.rows),
        ease_cm=args.ease,
        yoke_depth_cm=args.yoke,
        body_length_cm=args.body_length,
        sleeve_length_cm=args.sleeve_length,
        upper_arm_cm=args.upper_arm,
        wrist_cm=args.wrist,
        neck_circumference_cm=args.neck,
        rib_height_cm=args.rib,
        repeat_width=repeat_width,
        motif=motif_name,
        underarm_cast_on_cm=args.underarm,
        name=args.name or "Stranded yoke sweater",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_colorwork(args: argparse.Namespace) -> Pattern:
    from knitlib.constructions import (
        ColorworkSwatchSpec, generate_colorwork_swatch,
    )
    p = generate_colorwork_swatch(ColorworkSwatchSpec(
        width_cm=args.width,
        height_cm=args.height,
        gauge=Gauge(args.sts, args.rows),
        motif=args.motif,
        edge_sts=args.edge_sts,
        edge_rows=args.edge_rows,
        name=args.name or "Colorwork prøvelap",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def cmd_sweater(args: argparse.Namespace) -> Pattern:
    p = generate_bottom_up_sweater(BottomUpSweaterSpec(
        bust_cm=args.bust,
        gauge=Gauge(args.sts, args.rows),
        ease_cm=args.ease,
        body_length_cm=args.body_length,
        sleeve_length_cm=args.sleeve_length,
        upper_arm_cm=args.upper_arm,
        wrist_cm=args.wrist,
        neck_circumference_cm=args.neck,
        rib_height_cm=args.rib,
        style=args.style,
        name=args.name or "Bottom-up sweater",
    ), lang=args.lang)
    return attach_metadata(p, metadata_from_args(args))


def _add_materials_flags(parser: argparse.ArgumentParser) -> None:
    """Local wrapper around :func:`add_metadata_args` for the knit domain."""
    add_metadata_args(parser, hook_or_needle="pinde")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="strikkeopskrift",
        description="Genererer parametriske strikkeopskrifter med valideret maskemath.",
    )
    add_common_args(parser)
    sub = parser.add_subparsers(dest="construction", required=True)

    # --- hue ---
    h = sub.add_parser("hue", help="Hue / beanie")
    h.add_argument("--head", "--hovedmål", "--hovedmaal", type=float, default=None,
                   dest="head", help="hovedomkreds i cm")
    h.add_argument("--sts", type=float, required=True, help="masker pr. 10 cm")
    h.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                   type=float, required=True, dest="rows",
                   help="pinde pr. 10 cm")
    h.add_argument("--ease", type=float, default=-3.0, help="ease i cm (default: -3)")
    h.add_argument("--rib", type=float, default=5.0, help="rib-højde i cm")
    h.add_argument("--height", "--højde", "--hoejde", type=float, default=21.0,
                   dest="height", help="samlet højde i cm")
    h.add_argument("--sectors", type=int, default=8, help="antal kronesektorer")
    h.add_argument("--age", type=str, default=None,
                   choices=known_age_labels(),
                   help="alders-bånd til auto-fyld af head (eksplicitte mål "
                        "vinder altid)")
    _add_materials_flags(h)
    h.set_defaults(func=cmd_hue)

    # --- tørklæde ---
    t = sub.add_parser("tørklæde", aliases=["torklaede", "scarf"],
                       help="Tørklæde / scarf")
    t.add_argument("--width", "--bredde", type=float, required=True,
                   dest="width", help="bredde i cm")
    t.add_argument("--length", "--længde", "--laengde", type=float, required=True,
                   dest="length", help="længde i cm")
    t.add_argument("--sts", type=float, required=True)
    t.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                   type=float, required=True, dest="rows")
    t.add_argument("--edge-sts", type=int, default=4)
    t.add_argument("--edge-rows", type=int, default=6)
    t.add_argument("--repeat-sts", type=int, default=1)
    t.add_argument("--repeat-rows", type=int, default=1)
    t.add_argument("--pattern", default="glatstrik")
    _add_materials_flags(t)
    t.set_defaults(func=cmd_tørklæde)

    # --- raglan ---
    r = sub.add_parser("raglan", help="Top-down raglan sweater")
    r.add_argument("--bust", "--bryst", type=float, default=None, dest="bust",
                   help="brystmål i cm")
    r.add_argument("--sts", type=float, required=True)
    r.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                   type=float, required=True, dest="rows")
    r.add_argument("--ease", type=float, default=5.0)
    r.add_argument("--yoke", "--yoke-depth", "--yokedybde", type=float,
                   default=None, dest="yoke",
                   help="bærestykkedybde (default: brystmål/4)")
    r.add_argument("--body-length", "--kropslængde", "--kropslaengde",
                   type=float, default=36.0, dest="body_length")
    r.add_argument("--sleeve-length", "--ærme", "--aerme", "--ærmelængde",
                   "--aermelaengde", type=float, default=None,
                   dest="sleeve_length",
                   help="ærmelængde i cm (default: 45 voksen, alder hvis --age)")
    r.add_argument("--upper-arm", "--overarm", type=float, default=31.0,
                   dest="upper_arm")
    r.add_argument("--wrist", "--håndled", "--haandled", type=float, default=18.0,
                   dest="wrist")
    r.add_argument("--neck", "--hals", type=float, default=42.0, dest="neck")
    r.add_argument("--rib", type=float, default=5.0)
    r.add_argument("--underarm", type=float, default=None,
                   help="underarm-cast-on cm pr. side (default: auto-beregn så krop rammer brystmål)")
    r.add_argument("--age", type=str, default=None,
                   choices=known_age_labels(),
                   help="alders-bånd til auto-fyld af bust + sleeve_length")
    _add_materials_flags(r)
    r.set_defaults(func=cmd_raglan)

    # --- sokker ---
    so = sub.add_parser("sokker", aliases=["socks", "strømper"],
                        help="Top-down sokker med kilehæl + gusset")
    so.add_argument("--foot", "--fod", type=float, default=None, dest="foot",
                    help="fodomkreds i cm (bredeste sted)")
    so.add_argument("--foot-length", "--fodlængde", "--fodlaengde",
                    type=float, default=None, dest="foot_length",
                    help="fodlængde hæl→tå i cm")
    so.add_argument("--sts", type=float, required=True)
    so.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, required=True, dest="rows")
    so.add_argument("--leg", "--skaft", type=float, default=18.0, dest="leg",
                    help="skaftlængde i cm (default: 18)")
    so.add_argument("--rib", type=float, default=5.0)
    so.add_argument("--neg-ease", type=float, default=0.10,
                    help="negativ ease som fraktion (default: 0.10)")
    so.add_argument("--shoe-size", "--skostørrelse", "--skostoerrelse",
                    type=str, default=None, dest="shoe_size",
                    help="skostørrelse (informativt)")
    so.add_argument("--age", type=str, default=None,
                    choices=known_age_labels(),
                    help="alders-bånd til auto-fyld af foot + foot_length")
    _add_materials_flags(so)
    so.set_defaults(func=cmd_sokker)

    # --- bottom-up sweater ---
    sw = sub.add_parser("sweater", aliases=["bottom-up", "bottomup"],
                        help="Bottom-up sweater (Zimmermann EPS)")
    sw.add_argument("--bust", "--bryst", type=float, default=None, dest="bust")
    sw.add_argument("--sts", type=float, required=True)
    sw.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, required=True, dest="rows")
    sw.add_argument("--ease", type=float, default=5.0)
    sw.add_argument("--body-length", "--kropslængde", "--kropslaengde",
                    type=float, default=36.0, dest="body_length")
    sw.add_argument("--sleeve-length", "--ærme", "--aerme", "--ærmelængde",
                    "--aermelaengde", type=float, default=None,
                    dest="sleeve_length",
                    help="ærmelængde i cm (default: 45 voksen)")
    sw.add_argument("--upper-arm", "--overarm", type=float, default=None,
                    dest="upper_arm",
                    help="overarm cm (default: udledt fra EPS 35 pct)")
    sw.add_argument("--wrist", "--håndled", "--haandled", type=float, default=None,
                    dest="wrist", help="håndled cm (default: udledt fra EPS 20 pct)")
    sw.add_argument("--neck", "--hals", type=float, default=None, dest="neck",
                    help="halsomkreds cm (default: udledt fra EPS 40 pct)")
    sw.add_argument("--rib", type=float, default=5.0)
    sw.add_argument("--style", choices=["yoke", "raglan", "drop"], default="yoke")
    sw.add_argument("--age", type=str, default=None,
                    choices=known_age_labels(),
                    help="alders-bånd til auto-fyld af bust + sleeve_length")
    _add_materials_flags(sw)
    sw.set_defaults(func=cmd_sweater)

    # --- compound raglan ---
    cr = sub.add_parser("compound-raglan", aliases=["compound_raglan"],
                        help="Top-down raglan med uafhængig krop/ærme-grading")
    cr.add_argument("--bust", "--bryst", type=float, default=None, dest="bust")
    cr.add_argument("--upper-arm", "--overarm", type=float, required=True,
                    dest="upper_arm", help="overarm-omkreds i cm (bicep)")
    cr.add_argument("--sts", type=float, required=True)
    cr.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, required=True, dest="rows")
    cr.add_argument("--ease", type=float, default=5.0)
    cr.add_argument("--yoke", "--yoke-depth", "--yokedybde", type=float,
                    default=None, dest="yoke")
    cr.add_argument("--body-length", "--kropslængde", "--kropslaengde",
                    type=float, default=36.0, dest="body_length")
    cr.add_argument("--sleeve-length", "--ærme", "--aerme", "--ærmelængde",
                    "--aermelaengde", type=float, default=None,
                    dest="sleeve_length")
    cr.add_argument("--wrist", "--håndled", "--haandled", type=float, default=18.0,
                    dest="wrist")
    cr.add_argument("--neck", "--hals", type=float, default=42.0, dest="neck")
    cr.add_argument("--rib", type=float, default=5.0)
    cr.add_argument("--underarm", type=float, default=None)
    cr.add_argument("--age", type=str, default=None,
                    choices=known_age_labels(),
                    help="alders-bånd til auto-fyld af bust + sleeve_length")
    _add_materials_flags(cr)
    cr.set_defaults(func=cmd_compound_raglan)

    # --- half-pi shawl ---
    hp = sub.add_parser("half-pi", aliases=["halfpi", "pi-shawl"],
                        help="Elizabeth Zimmermann half-pi shawl")
    hp.add_argument("--sts", type=float, required=True,
                    help="masker pr. 10 cm (blokket lace gauge)")
    hp.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, required=True, dest="rows")
    hp.add_argument("--doublings", type=int, default=5,
                    help="antal fordoblinger (3-7 typisk)")
    hp.add_argument("--cast-on", type=int, default=3,
                    help="opslagsmasker for garter-tab")
    hp.add_argument("--edge", type=int, default=4,
                    help="garter-kantmasker hver side")
    hp.add_argument("--motif", action="append", default=[],
                    help="lace-motivnavn pr. bånd (kan repeteres)")
    _add_materials_flags(hp)
    hp.set_defaults(func=cmd_half_pi)

    # --- short-row crescent shawl ---
    sr = sub.add_parser("short-rows",
                        aliases=["short_rows", "kort-rækker", "kort_raekker",
                                 "crescent"],
                        help="Korte-rækker crescent shawl")
    sr.add_argument("--sts", type=float, required=True,
                    help="masker pr. 10 cm (blokket gauge)")
    sr.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, required=True, dest="rows",
                    help="pinde pr. 10 cm")
    sr.add_argument("--cast-on", type=int, default=3,
                    help="opslagsmasker for garter-tab (default: 3)")
    sr.add_argument("--increase-rows", type=int, default=80,
                    help="antal RS forøgelses-rækker (default: 80)")
    sr.add_argument("--short-row-cadence", type=int, default=8,
                    help="korte-rækker-par hver N. forøgelses-række (default: 8)")
    sr.add_argument("--short-row-setback", type=int, default=6,
                    help="masker korte rækker stopper før kanten (default: 6)")
    sr.add_argument("--edge-garter", type=int, default=3,
                    help="garter-selvkant-masker pr. side (default: 3)")
    _add_materials_flags(sr)
    sr.set_defaults(func=cmd_short_rows)

    # --- yoke stranded ---
    ys = sub.add_parser("yoke-stranded", aliases=["yoke", "icelandic"],
                        help="Top-down yoke-sweater med stranded mønster")
    ys.add_argument("--bust", "--bryst", type=float, default=None, dest="bust")
    ys.add_argument("--sts", type=float, required=True)
    ys.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, required=True, dest="rows")
    ys.add_argument("--ease", type=float, default=5.0)
    ys.add_argument("--yoke", "--yoke-depth", "--yokedybde", type=float,
                    default=None, dest="yoke",
                    help="bærestykkedybde (default: max(bust/4, upper_arm/2+4))")
    ys.add_argument("--body-length", "--kropslængde", "--kropslaengde",
                    type=float, default=36.0, dest="body_length")
    ys.add_argument("--sleeve-length", "--ærme", "--aerme", "--ærmelængde",
                    "--aermelaengde", type=float, default=None,
                    dest="sleeve_length")
    ys.add_argument("--upper-arm", "--overarm", type=float, default=31.0,
                    dest="upper_arm")
    ys.add_argument("--wrist", "--håndled", "--haandled", type=float, default=18.0,
                    dest="wrist")
    ys.add_argument("--neck", "--hals", type=float, default=44.0, dest="neck")
    ys.add_argument("--rib", type=float, default=5.0)
    ys.add_argument("--repeat", type=int, default=8,
                    help="motiv-rapportbredde (default: 8 — overskrives af --motif)")
    ys.add_argument("--motif", type=str, default="stars",
                    help="motiv-navn fra lib.visualisering.motifs "
                         "(stars / diagonal / simple_dots / snowflake_band / "
                         "icelandic_rose_band, default: stars)")
    ys.add_argument("--underarm", type=float, default=None)
    ys.add_argument("--age", type=str, default=None,
                    choices=known_age_labels(),
                    help="alders-bånd til auto-fyld af bust + sleeve_length")
    _add_materials_flags(ys)
    ys.set_defaults(func=cmd_yoke_stranded)

    # --- lace shawl ---
    la = sub.add_parser("lace", aliases=["lace-shawl", "kniplerud"],
                        help="Aflang lace shawl med rapport-mønster")
    la.add_argument("--width", "--bredde", type=float, required=True,
                    dest="width",
                    help="bredde i cm (lace-rapport rundes ned for at passe)")
    la.add_argument("--length", "--længde", "--laengde", type=float, required=True,
                    dest="length",
                    help="længde i cm (rundes til hele rapport-højder)")
    la.add_argument("--sts", type=float, required=True,
                    help="masker pr. 10 cm (blokket lace-gauge)")
    la.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, required=True, dest="rows",
                    help="pinde pr. 10 cm")
    la.add_argument("--repeat", type=str, default="feather_and_fan",
                    help="lace-rapportnavn (default: feather_and_fan)")
    la.add_argument("--edge-sts", type=int, default=4,
                    help="garter-kantmasker pr. side (default: 4)")
    la.add_argument("--garter-band", type=float, default=5.0,
                    help="garter-bånd top + bund i cm (default: 5)")
    _add_materials_flags(la)
    la.set_defaults(func=cmd_lace_shawl)

    # --- colorwork swatch ---
    cw = sub.add_parser("colorwork",
                        aliases=["colour-chart", "mønster-prøvelap",
                                 "moenster-proevelap"],
                        help="Flad colorwork-prøvelap til at teste motiv "
                             "+ farver inden et helt yoke-projekt")
    cw.add_argument("--width", "--bredde", type=float, required=True,
                    dest="width",
                    help="bredde i cm (rundes ned til hele rapporter)")
    cw.add_argument("--height", "--højde", "--hoejde", type=float, required=True,
                    dest="height",
                    help="højde i cm (rundes til hele rapport-højder)")
    cw.add_argument("--sts", type=float, required=True,
                    help="masker pr. 10 cm")
    cw.add_argument("--rows", "--row-gauge", "--række-gauge", "--raekke-gauge",
                    type=float, required=True, dest="rows",
                    help="pinde pr. 10 cm")
    cw.add_argument("--motif", type=str, default="stars",
                    help="motiv-navn (stars / diagonal / simple_dots / "
                         "snowflake_band / icelandic_rose_band)")
    cw.add_argument("--edge-sts", type=int, default=3,
                    help="garter-kantmasker pr. side (default: 3)")
    cw.add_argument("--edge-rows", type=int, default=4,
                    help="garter-kantrækker top + bund (default: 4)")
    _add_materials_flags(cw)
    cw.set_defaults(func=cmd_colorwork)

    args = parser.parse_args()
    apply_age_defaults(args, child_size=child_size)
    set_prosa_enabled(not getattr(args, "no_prosa", False))

    # Required size-args (no --age, no explicit value) raise a clean error
    # here instead of crashing inside the spec.
    _REQUIRED_BY_CMD = {
        "hue": ["head"],
        "raglan": ["bust"],
        "sweater": ["bust"], "bottom-up": ["bust"], "bottomup": ["bust"],
        "compound-raglan": ["bust"], "compound_raglan": ["bust"],
        "yoke-stranded": ["bust"], "yoke": ["bust"], "icelandic": ["bust"],
        "sokker": ["foot", "foot_length"],
        "socks": ["foot", "foot_length"],
        "strømper": ["foot", "foot_length"],
    }
    for attr in _REQUIRED_BY_CMD.get(args.construction, []):
        if getattr(args, attr, None) is None:
            print(
                f"error: --{attr.replace('_', '-')} is required "
                f"(or pass --age to auto-fill from child sizing table)",
                file=sys.stderr,
            )
            return 2

    # After requirement check: backfill non-required sleeve_length so
    # specs that need a value get the adult default when neither --age
    # nor explicit value was given.
    if hasattr(args, "sleeve_length") and getattr(args, "sleeve_length") is None:
        args.sleeve_length = 45.0

    pattern = args.func(args)

    # Garn-alternativer (Fase 5 iter 5)
    if getattr(args, "substitut", False):
        garn = getattr(args, "garn", None)
        if not garn:
            print("hint: --substitut kræver --garn med et kendt garn — "
                  "tilføj fx --garn 'Drops Air' for at få alternativer.",
                  file=sys.stderr)
        else:
            n = _yarn_alt.attach_alternatives(
                pattern, garn, lang=args.lang, domain="knit")
            if n == 0:
                print(f"hint: '{garn}' findes ikke i garn-databasen — "
                      "ingen alternativer kunne foreslås.", file=sys.stderr)

    return route_output(
        pattern, args,
        render_html=render_html,
        paged_js_path=_PAGED_JS_PATH,
        to_markdown=to_markdown,
    )


if __name__ == "__main__":
    raise SystemExit(main())
