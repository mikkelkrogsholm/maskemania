"""Shared CLI helpers for the strik / hækl ``generate.py`` scripts.

Both skills' ``generate.py`` historically duplicated:

* the top-level argparse flags (``--format``, ``--out``, ``--pdf``, ``--lang``,
  ``--name``, ``--no-prosa``, ``--social``, ``--substitut``, ``--pdf-renderer``)
* the materials flags (``--garn``, ``--garnløbe``, ``--designer``, ``--år``,
  ``--note`` and the domain-specific ``--pinde`` / ``--nål``)
* metadata extraction from ``args``
* age-based default backfill (knit only)
* yarn-database backfill (crochet only)
* output-routing (write md / json / html / pdf / social PNG)

This module centralises those so both CLIs can call the same helpers and
the duplication-rule (AR002) goes quiet. Function names are domain-neutral
where possible; behaviour that genuinely differs between domains is gated
on a small ``hook_or_needle`` literal or domain string parameter.

Public helpers:

    add_common_args(parser)
    add_metadata_args(subparser, *, hook_or_needle="pinde")
    metadata_from_args(args, *, lookup_yarn=None)
    apply_age_defaults(args)
    apply_yarn_defaults(args, *, domain="crochet")
    route_output(pattern, args, *, render_html, paged_js_path,
                 to_markdown, social_handle=None, set_domain=None)
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Callable, Literal, Optional

from .pattern import Pattern
from .pdf import ChromeNotFoundError, render_pdf
from .social import (
    available_formats as _social_formats,
    generate_social_preview,
)


HookOrNeedle = Literal["pinde", "nål"]


# ---------------------------------------------------------------------------
# argparse setup
# ---------------------------------------------------------------------------


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Attach the format/out/pdf/lang/name/no-prosa/social/substitut flags."""
    parser.add_argument(
        "--format", choices=["json", "md", "html"], default="md",
        help="output-format (default: md). Skal stå før konstruktion.",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="output-fil (kræves for html-format; ellers stdout)",
    )
    parser.add_argument(
        "--pdf", type=Path, default=None,
        help="skriv også PDF til denne sti (kræver WeasyPrint "
             "eller Chrome/Chromium)",
    )
    parser.add_argument(
        "--pdf-renderer", choices=["auto", "weasy", "chrome"],
        default="auto", dest="pdf_renderer",
        help="vælg PDF-renderer: auto (default; WeasyPrint hvis installeret, "
             "ellers Chrome), weasy (tving WeasyPrint), chrome (tving headless "
             "Chrome).",
    )
    parser.add_argument(
        "--lang", choices=["da", "en"], default="da",
        help="output-sprog (default: da)",
    )
    parser.add_argument("--name", help="navn på opskriften")
    parser.add_argument(
        "--no-prosa", dest="no_prosa", action="store_true",
        help="udelad den template-genererede prosa-intro.",
    )
    parser.add_argument(
        "--social", choices=sorted(set(_social_formats())),
        default=None,
        help="generér social-media preview (PNG) i det valgte format. "
             "Kræver --out FILE.png.",
    )
    parser.add_argument(
        "--substitut", "--garn-alternativer",
        dest="substitut", action="store_true",
        help="vis garn-alternativer fra yarn-databasen "
             "(kræver --garn med kendt garn).",
    )


def add_metadata_args(parser: argparse.ArgumentParser, *,
                      hook_or_needle: HookOrNeedle = "pinde") -> None:
    """Attach materials flags. Danish primary, English aliases.

    ``hook_or_needle="pinde"`` adds the knit-flavoured ``--pinde``/``--needles``
    flag; ``"nål"`` adds the crochet-flavoured ``--nål``/``--hook`` flag.
    """
    parser.add_argument(
        "--garn", "--yarn", type=str, default=None, dest="garn",
        help="garn-mærke / sammensætning, fx 'Drops Alpaca, 100% alpaca'",
    )
    parser.add_argument(
        "--garnløbe", "--garnloebe", "--yarn-run", "--meterage",
        type=str, default=None, dest="garnløbe",
        help="løbelængde, fx '167m/50g'",
    )
    if hook_or_needle == "pinde":
        parser.add_argument(
            "--pinde", "--needles", type=str, default=None, dest="pinde",
            help="pind-størrelse(r), fx 'Rundpind 4.0 mm + 3.5 mm til rib'",
        )
    else:
        parser.add_argument(
            "--nål", "--naal", "--hook", type=str, default=None, dest="nål",
            help="nål-størrelse, fx 'Hæklenål 4.0 mm'",
        )
    parser.add_argument(
        "--designer", type=str, default=None,
        help="designer-navn (vises på cover)",
    )
    parser.add_argument(
        "--år", "--aar", "--year", type=int, default=None, dest="år",
        help="udgivelsesår",
    )
    parser.add_argument(
        "--note", "--notes", action="append", default=[], dest="note",
        help="ekstra note til materialer-boks (kan repeteres)",
    )


# ---------------------------------------------------------------------------
# metadata extraction
# ---------------------------------------------------------------------------


def metadata_from_args(args: argparse.Namespace, *,
                       lookup_yarn: Optional[Callable[[str], Any]] = None,
                       ) -> dict:
    """Pull ``--garn`` / ``--pinde`` / ``--nål`` / etc. into a metadata dict.

    If ``lookup_yarn`` is supplied (the crochet path passes
    :func:`lib.visualisering.yarn_db.lookup_yarn`), unknown-key lookups also
    backfill ``yarn_run`` and ``hook`` from the yarn database when the user
    didn't pass explicit values.
    """
    md: dict[str, Any] = {}
    yarn_name = getattr(args, "garn", None)
    yarn_record = lookup_yarn(yarn_name) if (lookup_yarn and yarn_name) else None
    if yarn_name:
        if yarn_record is not None:
            md["yarn"] = f"{yarn_record.name} ({yarn_record.fiber})"
        else:
            md["yarn"] = yarn_name
    if getattr(args, "garnløbe", None):
        md["yarn_run"] = args.garnløbe
    elif yarn_record is not None:
        md["yarn_run"] = f"{yarn_record.meters_per_50g} m / 50 g"
    # knit uses dest="pinde"; crochet uses dest="nål".
    if getattr(args, "pinde", None):
        md["needles"] = args.pinde
    if getattr(args, "nål", None):
        md["hook"] = args.nål
    elif yarn_record is not None and not getattr(args, "pinde", None):
        # crochet auto-fill from yarn DB only if user didn't pass --nål.
        md["hook"] = f"{yarn_record.recommended_hook_mm:.1f} mm"
    if getattr(args, "designer", None):
        md["designer"] = args.designer
    if getattr(args, "år", None):
        md["year"] = args.år
    if getattr(args, "note", None):
        md["notes"] = list(args.note)
    return md


def attach_metadata(p: Pattern, metadata: dict) -> Pattern:
    """Set ``inputs["metadata"]`` (overriding any default)."""
    if metadata:
        p.inputs["metadata"] = metadata
    return p


# ---------------------------------------------------------------------------
# default backfill
# ---------------------------------------------------------------------------


def apply_age_defaults(args: argparse.Namespace,
                       *, child_size: Callable[[str], dict]) -> None:
    """If ``--age`` was given, fill matching size attributes with child-table
    averages. **User-supplied values always win** — we only set attributes
    that are still ``None``.
    """
    age = getattr(args, "age", None)
    if not age:
        return
    sz = child_size(age)
    if hasattr(args, "head") and getattr(args, "head", None) in (None,):
        args.head = sz["head_circumference_cm"]
    if hasattr(args, "bust") and getattr(args, "bust", None) in (None,):
        args.bust = sz["chest_cm"]
    if (hasattr(args, "foot_length")
            and getattr(args, "foot_length", None) in (None,)):
        args.foot_length = sz["foot_length_cm"]
    if hasattr(args, "foot") and getattr(args, "foot", None) in (None,):
        # Approximate foot circumference from foot length for kids; ratio
        # ~0.95 for slim children's feet (negative ease handled downstream).
        args.foot = round(sz["foot_length_cm"] * 0.95, 1)
    if (hasattr(args, "sleeve_length")
            and getattr(args, "sleeve_length", None) in (None,)):
        args.sleeve_length = sz["sleeve_length_cm"]


def apply_yarn_defaults(args: argparse.Namespace, *,
                        auto_gauge_from_yarn: Callable[..., Any],
                        domain: str = "crochet") -> None:
    """If ``--garn`` matches a known yarn and ``--gauge``/``--row-gauge`` are
    unset, fill in defaults from the yarn database. User-provided values
    always win.
    """
    yarn_name = getattr(args, "garn", None)
    if not yarn_name:
        return
    auto = auto_gauge_from_yarn(yarn_name, domain=domain)
    if auto is None:
        return
    sts_per_cm, rows_per_cm = auto
    if hasattr(args, "gauge") and getattr(args, "gauge", None) in (None, 0):
        args.gauge = round(sts_per_cm, 2)
    if (hasattr(args, "row_gauge") and getattr(args, "row_gauge", None)
            in (None, 0)):
        args.row_gauge = round(rows_per_cm, 2)


# ---------------------------------------------------------------------------
# output routing
# ---------------------------------------------------------------------------


def route_output(pattern: Pattern, args: argparse.Namespace, *,
                 render_html: Callable[..., str],
                 paged_js_path: Path,
                 to_markdown: Callable[[Pattern], str],
                 social_handle: Optional[str] = None,
                 set_domain: Optional[str] = None) -> int:
    """Write the pattern as md/json/html/pdf/social PNG based on ``args``.

    Returns the CLI exit code. The caller should ``return`` this value
    directly from ``main``.

    ``render_html`` is the skill-specific HTML renderer (knit and crochet
    have separate templates). ``paged_js_path`` is the path to the
    ``paged.polyfill.js`` asset. ``to_markdown`` produces the markdown
    body. ``social_handle`` injects an optional handle into the social
    preview. ``set_domain`` (if provided) is stamped onto
    ``pattern.inputs["_domain"]`` before social-rendering.
    """
    out_path = args.out
    pdf_path = args.pdf

    # Social preview short-circuits everything else.
    if getattr(args, "social", None):
        if out_path is None:
            print("error: --social requires --out FILE.png", file=sys.stderr)
            return 2
        if set_domain is not None:
            pattern.inputs.setdefault("_domain", set_domain)
        kwargs = {"format": args.social, "output_path": out_path,
                  "lang": args.lang}
        if social_handle is not None:
            kwargs["handle"] = social_handle
        try:
            png = generate_social_preview(pattern, **kwargs)
            print(f"Wrote {png}", file=sys.stderr)
        except ChromeNotFoundError as e:
            html_path = Path(out_path).with_suffix(".html").resolve()
            print(f"warning: {e}", file=sys.stderr)
            print(f"Wrote standalone HTML: {html_path}", file=sys.stderr)
            print("Open it in any browser and screenshot manually.",
                  file=sys.stderr)
            return 3
        return 0

    if args.format == "json":
        out_text = json.dumps(pattern.to_dict(), ensure_ascii=False, indent=2)
    elif args.format == "html" or pdf_path is not None:
        if args.format == "html" and out_path is None and pdf_path is None:
            print("error: --format html requires --out FILE.html or --pdf FILE.pdf",
                  file=sys.stderr)
            return 2
        html_text = render_html(pattern, paged_js_path="paged.polyfill.js",
                                lang=args.lang)

        if out_path is not None and args.format == "html":
            out_path = out_path.resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            paged_target = out_path.parent / "paged.polyfill.js"
            if not paged_target.exists():
                shutil.copy2(paged_js_path, paged_target)
            out_path.write_text(html_text, encoding="utf-8")
            print(f"Wrote {out_path}", file=sys.stderr)
            print(f"Wrote {paged_target}", file=sys.stderr)
            print("Open in Chrome → Print → Save as PDF, or use --pdf",
                  file=sys.stderr)

        if pdf_path is not None:
            try:
                produced = render_pdf(
                    html_text, pdf_path,
                    paged_js_path=paged_js_path,
                    renderer=getattr(args, "pdf_renderer", "auto"),
                )
                print(f"Wrote {produced}", file=sys.stderr)
            except (ChromeNotFoundError, ValueError) as e:
                print(f"error: {e}", file=sys.stderr)
                return 3
        return 0
    else:
        out_text = to_markdown(pattern)

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text, encoding="utf-8")
        print(f"Wrote {out_path}", file=sys.stderr)
    else:
        print(out_text)
    return 0
