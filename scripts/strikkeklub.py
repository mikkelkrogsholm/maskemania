#!/usr/bin/env python3
"""Strikkeklub batch-mode (Fase 5 iter 5).

Tager en CSV med medlems-rækker og genererer en HTML-opskrift pr. medlem
plus et samlet ``index.html`` + en zip-fil over outputmappen. Ideelt til
en strikkeklub eller hækle-aften hvor 6-12 medlemmer hver vil have deres
egen opskrift baseret på deres egne mål.

Brug::

    python3 scripts/strikkeklub.py members.csv --out klub_2026
    python3 scripts/strikkeklub.py members.csv --out /tmp/klub --lang en

CSV-spec:
    - Påkrævede kolonner: ``name``, ``construction``.
    - Resterende kolonner er konstruktions-input (head_cm, sts, rows,
      foot_length_cm, ...). Ukendte kolonner gemmes som metadata-noter
      pr. medlem.
    - Rækker der fejler validering springes over (logget). Rapporten
      tilbage rummer hvor mange OK / fejlede + hvad fejlede.

Outputstruktur::

    <out>/
      index.html              # oversigt over alle medlemmer + links
      <n>_<name>_<construction>.html
      paged.polyfill.js
      style.css
    <out>.zip                 # zip-fil med samme indhold

Konstruktionerne der understøttes (alias → spec):
    hue, tørklæde, raglan, sokker, sweater
    amigurumi (kugle), granny, haekle_torklaede, mandala
"""

from __future__ import annotations

import argparse
import csv
import html as _htmllib
import shutil
import sys
import traceback
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "skills" / "strikning"))
sys.path.insert(0, str(_REPO / "skills" / "hækling"))

_PAGED_JS_PATH = _REPO / "lib" / "visualisering" / "assets" / "paged.polyfill.js"
_STYLE_CSS_PATH = _REPO / "lib" / "visualisering" / "assets" / "style.css"


# ---------------------------------------------------------------------------
# Construction adapters: each maps a CSV row → (Pattern, render_html).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BuiltPattern:
    pattern: Any
    render: Callable[..., str]
    domain: str  # "knit" | "crochet"


def _f(row: dict, key: str, default: float | None = None,
       *, required: bool = False) -> float | None:
    """Read a float-ish field from the row. Empty → default. Missing+required → ValueError."""
    val = row.get(key)
    if val is None or str(val).strip() == "":
        if required:
            raise ValueError(f"missing required column '{key}'")
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        raise ValueError(f"column '{key}' must be a number, got {val!r}")


def _i(row: dict, key: str, default: int | None = None) -> int | None:
    val = row.get(key)
    if val is None or str(val).strip() == "":
        return default
    try:
        return int(float(val))
    except (TypeError, ValueError):
        raise ValueError(f"column '{key}' must be an integer, got {val!r}")


def _s(row: dict, key: str, default: str | None = None) -> str | None:
    v = row.get(key)
    if v is None:
        return default
    s = str(v).strip()
    return s if s else default


def _build_hue(row: dict) -> BuiltPattern:
    from knitlib import Gauge
    from knitlib.constructions import HueSpec, generate_hue
    from lib.visualisering.html import render_html
    sts = _f(row, "sts", required=True)
    rows_ = _f(row, "rows", required=True)
    head = _f(row, "head_cm", required=True)
    p = generate_hue(HueSpec(
        head_circumference_cm=head,
        gauge=Gauge(sts, rows_),
        ease_cm=_f(row, "ease_cm", -3.0),
        rib_height_cm=_f(row, "rib_cm", 5.0),
        total_height_cm=_f(row, "height_cm", 21.0),
        sectors=_i(row, "sectors", 8),
        name=_s(row, "name", "Hue"),
    ))
    return BuiltPattern(p, render_html, "knit")


def _build_torklaede(row: dict) -> BuiltPattern:
    from knitlib import Gauge
    from knitlib.constructions import TørklædeSpec, generate_tørklæde
    from lib.visualisering.html import render_html
    sts = _f(row, "sts", required=True)
    rows_ = _f(row, "rows", required=True)
    p = generate_tørklæde(TørklædeSpec(
        width_cm=_f(row, "width_cm", required=True),
        length_cm=_f(row, "length_cm", required=True),
        gauge=Gauge(sts, rows_),
        edge_sts=_i(row, "edge_sts", 4),
        edge_rows=_i(row, "edge_rows", 6),
        pattern_repeat_sts=_i(row, "repeat_sts", 1),
        pattern_repeat_rows=_i(row, "repeat_rows", 1),
        pattern_description=_s(row, "pattern", "glatstrik"),
        name=_s(row, "name", "Tørklæde"),
    ))
    return BuiltPattern(p, render_html, "knit")


def _build_raglan(row: dict) -> BuiltPattern:
    from knitlib import Gauge
    from knitlib.constructions import RaglanSpec, generate_raglan
    from lib.visualisering.html import render_html
    sts = _f(row, "sts", required=True)
    rows_ = _f(row, "rows", required=True)
    p = generate_raglan(RaglanSpec(
        bust_cm=_f(row, "bust_cm", required=True),
        gauge=Gauge(sts, rows_),
        ease_cm=_f(row, "ease_cm", 5.0),
        body_length_cm=_f(row, "body_length_cm", 36.0),
        sleeve_length_cm=_f(row, "sleeve_length_cm", 45.0),
        upper_arm_cm=_f(row, "upper_arm_cm", 31.0),
        wrist_cm=_f(row, "wrist_cm", 18.0),
        neck_circumference_cm=_f(row, "neck_cm", 42.0),
        rib_height_cm=_f(row, "rib_cm", 5.0),
        name=_s(row, "name", "Raglan"),
    ))
    return BuiltPattern(p, render_html, "knit")


def _build_sokker(row: dict) -> BuiltPattern:
    from knitlib import Gauge
    from knitlib.constructions import SokkerSpec, generate_sokker
    from lib.visualisering.html import render_html
    sts = _f(row, "sts", required=True)
    rows_ = _f(row, "rows", required=True)
    p = generate_sokker(SokkerSpec(
        foot_circ_cm=_f(row, "foot_circ_cm", required=True),
        foot_length_cm=_f(row, "foot_length_cm", required=True),
        gauge=Gauge(sts, rows_),
        leg_length_cm=_f(row, "leg_cm", 18.0),
        rib_height_cm=_f(row, "rib_cm", 5.0),
        shoe_size=_s(row, "shoe_size"),
        name=_s(row, "name", "Sokker"),
    ))
    return BuiltPattern(p, render_html, "knit")


def _build_amigurumi(row: dict) -> BuiltPattern:
    from croclib.constructions import AmigurumiSphereSpec, amigurumi_sphere
    from croclib.html import render_html
    p = amigurumi_sphere(AmigurumiSphereSpec(
        diameter_cm=_f(row, "diameter_cm", required=True),
        gauge_sc_per_cm=_f(row, "gauge", 5.0),
        start_count=_i(row, "start", 6),
        equator_rounds=_i(row, "equator", 0),
        name=_s(row, "name", "Amigurumi-kugle"),
    ))
    return BuiltPattern(p, render_html, "crochet")


def _build_granny(row: dict) -> BuiltPattern:
    from croclib.constructions import GrannySquareSpec, generate_granny_square
    from croclib.html import render_html
    colors_raw = _s(row, "colors")
    colors = [c.strip() for c in colors_raw.split(",")] if colors_raw else None
    p = generate_granny_square(GrannySquareSpec(
        rounds=_i(row, "rounds", 6),
        colors=colors,
        name=_s(row, "name", "Granny square"),
    ))
    return BuiltPattern(p, render_html, "crochet")


def _build_haekle_torklaede(row: dict) -> BuiltPattern:
    from croclib.constructions import CrochetTørklædeSpec, generate_tørklæde
    from croclib.html import render_html
    p = generate_tørklæde(CrochetTørklædeSpec(
        width_cm=_f(row, "width_cm", required=True),
        length_cm=_f(row, "length_cm", required=True),
        gauge_sts_per_cm=_f(row, "gauge", 2.5),
        stitch_type=_s(row, "stitch", "dc"),
        row_gauge_per_cm=_f(row, "row_gauge"),
        name=_s(row, "name", "Hæklet tørklæde"),
    ))
    return BuiltPattern(p, render_html, "crochet")


def _build_mandala(row: dict) -> BuiltPattern:
    from croclib.constructions import MandalaSpec, generate_mandala
    from croclib.html import render_html
    colors_raw = _s(row, "colors")
    colors = [c.strip() for c in colors_raw.split(",")] if colors_raw else None
    p = generate_mandala(MandalaSpec(
        rounds=_i(row, "rounds", 6),
        start_count=_i(row, "start", 12),
        colors=colors,
        name=_s(row, "name", "Mandala"),
    ))
    return BuiltPattern(p, render_html, "crochet")


# Map of canonical construction name → builder. Aliases (Danish + English).
_CONSTRUCTIONS: dict[str, Callable[[dict], BuiltPattern]] = {
    "hue": _build_hue, "hat": _build_hue, "beanie": _build_hue,
    "tørklæde": _build_torklaede, "torklaede": _build_torklaede,
    "scarf": _build_torklaede,
    "raglan": _build_raglan, "raglan_topdown": _build_raglan,
    "sokker": _build_sokker, "socks": _build_sokker, "strømper": _build_sokker,
    "amigurumi": _build_amigurumi, "kugle": _build_amigurumi,
    "sphere": _build_amigurumi,
    "granny": _build_granny, "granny_square": _build_granny,
    "haekle_torklaede": _build_haekle_torklaede,
    "haekle_tørklæde": _build_haekle_torklaede,
    "crochet_scarf": _build_haekle_torklaede,
    "mandala": _build_mandala,
}


def supported_constructions() -> list[str]:
    """Return canonical construction names — exposed for help / tests."""
    return sorted(set(_CONSTRUCTIONS))


# ---------------------------------------------------------------------------
# CSV → row processing
# ---------------------------------------------------------------------------


_KNOWN_INPUT_COLS = {
    "name", "construction", "sts", "rows", "head_cm", "ease_cm", "rib_cm",
    "height_cm", "sectors", "width_cm", "length_cm", "edge_sts", "edge_rows",
    "repeat_sts", "repeat_rows", "pattern", "bust_cm", "body_length_cm",
    "sleeve_length_cm", "upper_arm_cm", "wrist_cm", "neck_cm",
    "foot_circ_cm", "foot_length_cm", "leg_cm", "shoe_size",
    "diameter_cm", "gauge", "start", "equator", "rounds", "colors",
    "stitch", "row_gauge", "garn", "age",
}


def _designer_notes_from_row(row: dict) -> list[str]:
    """Any extra column we don't recognise becomes a note in metadata."""
    notes: list[str] = []
    for k, v in row.items():
        if k in _KNOWN_INPUT_COLS:
            continue
        if v is None:
            continue
        s = str(v).strip()
        if not s:
            continue
        notes.append(f"{k}: {s}")
    return notes


def _slug(s: str) -> str:
    """ASCII-safe filename slug."""
    out = []
    for ch in s.strip().lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "-", "_"):
            out.append("_")
        elif ch == "ø": out.append("oe")
        elif ch == "æ": out.append("ae")
        elif ch == "å": out.append("aa")
        # else drop
    s2 = "".join(out)
    while "__" in s2:
        s2 = s2.replace("__", "_")
    return s2.strip("_") or "x"


@dataclass
class RowResult:
    rownum: int
    name: str
    construction: str
    ok: bool
    filename: str | None
    error: str | None


def _process_row(rownum: int, row: dict, out_dir: Path, *,
                 lang: str = "da") -> RowResult:
    name = _s(row, "name") or f"medlem-{rownum}"
    construction = (_s(row, "construction") or "").lower()
    if not construction:
        return RowResult(rownum, name, "", False, None,
                         "missing 'construction' column")
    builder = _CONSTRUCTIONS.get(construction)
    if builder is None:
        return RowResult(
            rownum, name, construction, False, None,
            f"unknown construction '{construction}'. "
            f"Supported: {', '.join(supported_constructions())}",
        )
    try:
        built = builder(row)
    except Exception as e:  # noqa: BLE001 — broad on purpose for batch mode
        return RowResult(rownum, name, construction, False, None,
                         f"{type(e).__name__}: {e}")

    pattern = built.pattern
    # Decorate with member metadata (designer-note pr medlem)
    md = pattern.inputs.setdefault("metadata", {}).copy() \
        if pattern.inputs.get("metadata") else {}
    notes = list(md.get("notes") or [])
    notes.extend(_designer_notes_from_row(row))
    notes.append(f"Strikkeklub-medlem: {name}")
    md["notes"] = notes
    if _s(row, "garn"):
        md.setdefault("yarn", _s(row, "garn"))
    pattern.inputs["metadata"] = md

    filename = f"{rownum:02d}_{_slug(name)}_{_slug(construction)}.html"
    target = out_dir / filename
    try:
        html_text = built.render(
            pattern, paged_js_path="paged.polyfill.js", lang=lang)
        target.write_text(html_text, encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return RowResult(rownum, name, construction, False, None,
                         f"render failed — {type(e).__name__}: {e}")
    return RowResult(rownum, name, construction, True, filename, None)


# ---------------------------------------------------------------------------
# Index page + zip
# ---------------------------------------------------------------------------


_INDEX_TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font-family: 'Inter', system-ui, sans-serif; max-width: 880px;
  margin: 2rem auto; padding: 0 1rem; line-height: 1.5; color: #222; }}
h1 {{ margin-bottom: 0.2rem; font-family: 'EB Garamond', serif;
  font-weight: 500; }}
.lead {{ color: #555; margin-top: 0; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 1.5rem; }}
th, td {{ text-align: left; padding: 0.5rem 0.6rem;
  border-bottom: 1px solid #e6e0d0; }}
th {{ background: #f7f1de; font-size: 0.85rem; text-transform: uppercase;
  letter-spacing: 0.04em; color: #6a5510; }}
a {{ color: #6a4d10; }}
.failed {{ color: #903; }}
footer {{ margin-top: 3rem; color: #888; font-size: 0.85rem; }}
.summary {{ background: #faf6ea; padding: 0.8em 1em; border-radius: 4px;
  margin-top: 1rem; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="lead">{lead}</p>
<div class="summary">
  <strong>{ok_label}:</strong> {ok_count}<br>
  <strong>{failed_label}:</strong> {failed_count}
</div>
<table>
<thead><tr>
  <th>#</th><th>{col_name}</th><th>{col_construction}</th><th>{col_link}</th>
</tr></thead>
<tbody>
{rows}
</tbody>
</table>
<footer>{footer}</footer>
</body>
</html>
"""


def _build_index(results: list[RowResult], *, lang: str = "da",
                 title: str = "Strikkeklub") -> str:
    if lang == "en":
        lead = ("Auto-generated batch of patterns, one per club member. "
                "Each link opens a print-ready HTML.")
        ok_label = "Successful"
        failed_label = "Failed"
        col_name, col_construction, col_link = "Member", "Construction", "Pattern"
        footer = "Generated by scripts/strikkeklub.py."
    else:
        lead = ("Auto-genereret samling af opskrifter, ét pr. medlem. "
                "Hvert link åbner en print-klar HTML.")
        ok_label = "Lykkedes"
        failed_label = "Fejlede"
        col_name, col_construction, col_link = "Medlem", "Konstruktion", "Opskrift"
        footer = "Genereret af scripts/strikkeklub.py."

    ok = sum(1 for r in results if r.ok)
    failed = sum(1 for r in results if not r.ok)

    rows_html: list[str] = []
    for r in results:
        if r.ok:
            link = (f'<a href="{_htmllib.escape(r.filename)}">'
                    f'{_htmllib.escape(r.filename)}</a>')
        else:
            link = f'<span class="failed">{_htmllib.escape(r.error or "?")}</span>'
        rows_html.append(
            "<tr>"
            f"<td>{r.rownum}</td>"
            f"<td>{_htmllib.escape(r.name)}</td>"
            f"<td>{_htmllib.escape(r.construction or '—')}</td>"
            f"<td>{link}</td>"
            "</tr>"
        )

    return _INDEX_TEMPLATE.format(
        lang=("en" if lang == "en" else "da"),
        title=_htmllib.escape(title),
        lead=lead,
        ok_label=ok_label, ok_count=ok,
        failed_label=failed_label, failed_count=failed,
        col_name=col_name, col_construction=col_construction, col_link=col_link,
        rows="\n".join(rows_html),
        footer=footer,
    )


def _zip_dir(src: Path, zip_path: Path) -> Path:
    """Zip every file under ``src`` recursively into ``zip_path``."""
    zip_path = zip_path.resolve()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(src.rglob("*")):
            if f.is_file():
                zf.write(f, arcname=f.relative_to(src.parent))
    return zip_path


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------


def run_batch(csv_path: Path, out_dir: Path, *, lang: str = "da",
              title: str = "Strikkeklub", make_zip: bool = True
              ) -> dict:
    """Run the batch. Returns a report dict.

    Keys: ``ok``, ``failed``, ``results`` (list[RowResult]), ``index``,
    ``zip`` (None if make_zip=False), ``out_dir``.
    """
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy shared assets so the HTML files look right when opened locally.
    paged_target = out_dir / "paged.polyfill.js"
    if not paged_target.exists():
        shutil.copy2(_PAGED_JS_PATH, paged_target)

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        results: list[RowResult] = []
        for i, row in enumerate(reader, start=1):
            res = _process_row(i, row, out_dir, lang=lang)
            results.append(res)

    index_path = out_dir / "index.html"
    index_path.write_text(_build_index(results, lang=lang, title=title),
                          encoding="utf-8")

    zip_path: Path | None = None
    if make_zip:
        zip_path = out_dir.parent / f"{out_dir.name}.zip"
        _zip_dir(out_dir, zip_path)

    return {
        "ok": sum(1 for r in results if r.ok),
        "failed": sum(1 for r in results if not r.ok),
        "results": results,
        "index": index_path,
        "zip": zip_path,
        "out_dir": out_dir,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="strikkeklub",
        description="Batch-generér strikke-/hækleopskrifter for en klub fra CSV.",
    )
    parser.add_argument("csv", type=Path, help="CSV-fil med medlems-rækker")
    parser.add_argument("--out", type=Path, required=True,
                        help="output-mappe (oprettes hvis den ikke findes)")
    parser.add_argument("--lang", choices=["da", "en"], default="da")
    parser.add_argument("--title", default="Strikkeklub",
                        help="titel på index-siden")
    parser.add_argument("--no-zip", action="store_true",
                        help="udeluk zip-fil")
    parser.add_argument("--format", default="html",
                        choices=["html"],
                        help="kun html understøttet (lader CLI matche andre)")
    args = parser.parse_args(argv)

    if not args.csv.exists():
        print(f"error: CSV-fil findes ikke: {args.csv}", file=sys.stderr)
        return 2

    report = run_batch(
        args.csv, args.out, lang=args.lang, title=args.title,
        make_zip=not args.no_zip,
    )

    print(f"OK:      {report['ok']}", file=sys.stderr)
    print(f"Fejlede: {report['failed']}", file=sys.stderr)
    for r in report["results"]:
        if r.ok:
            print(f"  [ok] #{r.rownum} {r.name} → {r.filename}",
                  file=sys.stderr)
        else:
            print(f"  [FEJL] #{r.rownum} {r.name} ({r.construction}): "
                  f"{r.error}", file=sys.stderr)
    print(f"Index:   {report['index']}", file=sys.stderr)
    if report["zip"]:
        print(f"Zip:     {report['zip']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
