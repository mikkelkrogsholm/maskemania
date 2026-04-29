"""Filet crochet — pixel grid on a mesh of dc + ch.

Recipe (Agent B's research §4):

* A filet "cell" is either:
    - **open mesh**: 1 dc + 2 ch (= 3 stitches wide if you count the
      shared dc with the next cell)
    - **filled block**: 3 dc

* Stitches per row, given a grid width W cells: ``3·W + 1``.
  (W cells × 3 stitches each + 1 extra dc to close the last cell — adjacent
  cells share their boundary dc.)

* Foundation chain is conventionally ``3·W + 2`` ch (varies by source).

The grid is supplied as a 2D array of bool/int — top-down order, with the
top of the design at row 0. We render it bottom-up the way crochet rows
are worked, and emit a Pattern with one section per row plus turning-chain
notes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence

from lib.visualisering import Pattern, RowValidator
from ..crorow import CrochetRow


def filet_stitches_per_row(width_cells: int) -> int:
    """``3·W + 1`` (Agent B §4)."""
    if width_cells < 1:
        raise ValueError("width_cells must be >= 1")
    return 3 * width_cells + 1


def filet_foundation_chain(width_cells: int) -> int:
    """``3·W + 2``, the conventional foundation-chain length."""
    if width_cells < 1:
        raise ValueError("width_cells must be >= 1")
    return 3 * width_cells + 2


def _normalize_grid(
    grid: Sequence[Sequence[bool | int | str]] | str,
    width_cells: int,
    height_cells: int,
) -> list[list[bool]]:
    """Accept several grid shapes:

    * a sequence of sequences with truthy/falsy cells;
    * a multi-line string with ``X``/``#``/``1`` for filled, ``.``/``0``/' '
      for open.
    """
    if isinstance(grid, str):
        rows = [r.strip("\r") for r in grid.strip("\n").splitlines()]
    else:
        rows = list(grid)

    out: list[list[bool]] = []
    for r in rows:
        if isinstance(r, str):
            row = [c not in (".", "0", " ", "_", "-") for c in r]
        else:
            row = [bool(c) and (c not in (0, "0", "."))
                   if not isinstance(c, bool) else bool(c)
                   for c in r]
        # Pad/truncate to width
        if len(row) < width_cells:
            row = row + [False] * (width_cells - len(row))
        elif len(row) > width_cells:
            row = row[:width_cells]
        out.append(row)
    if len(out) < height_cells:
        out += [[False] * width_cells for _ in range(height_cells - len(out))]
    elif len(out) > height_cells:
        out = out[:height_cells]
    return out


@dataclass
class FiletSpec:
    width_cells: int
    height_cells: int
    grid: Sequence[Sequence[bool | int | str]] | str = field(default_factory=list)
    name: str = "Filet hækling"
    gauge_sts_per_cm: float = 2.0      # rough dc gauge per cm (US dc)
    row_gauge_per_cm: float = 0.5      # rough dc-row gauge per cm
    metadata: dict | None = None


def generate_filet(spec: FiletSpec, lang: str = "da") -> Pattern:
    if spec.width_cells < 1 or spec.height_cells < 1:
        raise ValueError("width_cells and height_cells must both be >= 1")
    grid = _normalize_grid(spec.grid, spec.width_cells, spec.height_cells)

    sts_per_row = filet_stitches_per_row(spec.width_cells)
    foundation_ch = filet_foundation_chain(spec.width_cells)

    metadata = dict(spec.metadata or {})

    p = Pattern(
        name=spec.name,
        construction="filet",
        difficulty="easy",
        inputs={
            "_domain": "crochet",
            "width_cells": spec.width_cells,
            "height_cells": spec.height_cells,
            "sts_per_row": sts_per_row,
            "foundation_chain": foundation_ch,
            "grid": grid,
            "gauge_sts_per_cm": spec.gauge_sts_per_cm,
            "row_gauge_per_cm": spec.row_gauge_per_cm,
            "width_cm": round(spec.width_cells * 3 / spec.gauge_sts_per_cm, 1),
            "length_cm": round(spec.height_cells / spec.row_gauge_per_cm, 1),
            "gauge": {
                "sts_per_10cm": int(round(spec.gauge_sts_per_cm * 10)),
                "rows_per_10cm": int(round(spec.row_gauge_per_cm * 10)),
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- Foundation chain ----------------------------------------------
    sec1 = p.add_section("Bundkæde", sts_before=0)
    sec1.add(
        f"Hækl {foundation_ch} lm.",
        sts_after=foundation_ch,
        note=f"3·W + 2 = 3·{spec.width_cells} + 2 = {foundation_ch}",
    )
    r0 = CrochetRow(sts_before=0, label="bundkæde")
    r0.ch(foundation_ch)
    validator.add(r0)

    # ---- Row 1: anchor into foundation ---------------------------------
    sec2 = p.add_section("Række 1", sts_before=foundation_ch)
    # Row 1 first cell decides turning-chain height: open=ch3, filled=normal dc
    first_cell_open = not grid[-1][0]   # bottom row of grid = first row crocheted
    if first_cell_open:
        first_text = (
            "Spring de første 4 lm over. Begynd med 1 stm i den 5. lm: "
            "(åben celle 1) 2 lm, spring 2 lm over, 1 stm i næste lm."
        )
    else:
        first_text = (
            "Hækl 1 stm i 4. lm fra hægten + 2 stm i de næste 2 lm "
            "(første fyldte celle = 3 stm + den indledende stm)."
        )
    sec2.add(first_text, sts_after=sts_per_row,
             note=f"i alt {sts_per_row} stm pr. række")

    # Bookkeeping: validate row 1 consumes the entire foundation
    r1 = CrochetRow(sts_before=foundation_ch, label="R 1")
    r1.sl_st(foundation_ch - sts_per_row)  # slip-skip the chains we don't anchor
    r1.dc(sts_per_row)
    validator.add(r1)

    # ---- Body rows -----------------------------------------------------
    sec3 = p.add_section("Krop", sts_before=sts_per_row)
    # We render rows 2..H, reading the grid bottom-up
    for i in range(2, spec.height_cells + 1):
        cells = grid[spec.height_cells - i]
        recipe = _row_recipe(cells)
        first_cell_open = not cells[0]
        turn = "lm 3 (åben start)" if first_cell_open else "lm 5 (fyldt start)"
        sec3.add(
            f"R {i}: vend, {turn}, " + recipe + ".",
            sts_after=sts_per_row,
            note=("læseretning skifter hver række (R lige: v→h, "
                  "R ulige: h→v)"),
        )
        r = CrochetRow(sts_before=sts_per_row, label=f"R {i}")
        r.dc(sts_per_row)
        validator.add(r)

    # ---- Finishing -----------------------------------------------------
    sec4 = p.add_section("Afslutning", sts_before=sts_per_row)
    sec4.add(
        "Klip garnet, træk gennem løkken, hæft alle ender. Damp/blok så "
        "celler bliver kvadratiske.",
        sts_after=sts_per_row,
    )

    # ---- Notes & warnings ----------------------------------------------
    p.notes.append(
        f"Stitch-count pr. række = 3·W + 1 = 3·{spec.width_cells} + 1 "
        f"= {sts_per_row} (Agent B §4)."
    )
    p.notes.append(
        f"Grid = {spec.width_cells} × {spec.height_cells} celler. "
        f"≈ {p.inputs['width_cm']:.1f} × {p.inputs['length_cm']:.1f} cm "
        "ved opgivet gauge."
    )
    if spec.width_cells * spec.height_cells == 0:
        p.warnings.append("Grid er tomt.")

    p.validate_continuity()
    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)


def _row_recipe(cells: list[bool]) -> str:
    """Translate a row of cells into a compact instruction.

    Adjacent same-type cells get grouped: "3 åbne, 2 fyldte" → cleaner text.
    """
    if not cells:
        return "(tom række)"
    out: list[str] = []
    run_type = cells[0]
    run_count = 1
    for c in cells[1:]:
        if c == run_type:
            run_count += 1
        else:
            out.append(_describe_run(run_type, run_count))
            run_type = c
            run_count = 1
    out.append(_describe_run(run_type, run_count))
    return ", ".join(out)


def _describe_run(filled: bool, n: int) -> str:
    if filled:
        if n == 1:
            return "1 fyldt celle (3 stm)"
        return f"{n} fyldte celler ({n} × 3 stm i træk)"
    if n == 1:
        return "1 åben celle (lm 2, spring 2 over, 1 stm)"
    return (f"{n} åbne celler ([lm 2, spring 2 over, 1 stm] × {n})")
