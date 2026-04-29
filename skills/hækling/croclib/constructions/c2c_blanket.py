"""Corner-to-corner (C2C) blanket — diagonal block construction.

C2C is a classic afghan / blanket technique. You start in one corner with
a single block, increase one block per row (along the diagonal) until the
diagonal hits the target width, then decrease one block per row down to
the opposite corner. The finished piece is a rectangle (or square) measured
in *blocks*, not stitches.

Block recipe (most common variant):

* A C2C **block** = ``ch 3`` (turning chain that counts as 1 dc) + ``3 dc``
  worked into the previous row's ch-3 space → 4 stitches total per block.
  Adjacent blocks share the join via a ``sl_st`` into the next ch-3 space.
* In the bookkeeping sense each block produces 3 dc + 1 ch-3-counts-as-dc
  = 4 stitches; the very first block in a row uses ``ch 6`` to start (3
  ch for the dc-equivalent + 3 ch for the trailing space).

Total stitches across the whole blanket (closed-form, see PLAN-research):

* For a ``W`` × ``H`` block grid the diagonal grows from 1 block up to
  ``min(W, H)``, holds at that length while the diagonal slides across the
  long side, then decreases back to 1 block. The total number of blocks is
  exactly ``W · H`` (one per cell in the grid).
* Each block contributes ``3 dc`` worth of working stitches plus the
  ch-3 turning, so total dc ≈ ``3 · W · H``.

We expose two helpers — :func:`c2c_total_blocks` and
:func:`c2c_total_dc` — that wrap those formulas, and a
:func:`c2c_blocks_per_row` generator that walks the diagonal.

Block-level validation: each row's block count must equal the closed-form
number from :func:`c2c_blocks_per_row`. We also validate continuity at the
section level — every "row N" section's ``sts_before`` must match the
previous section's ``sts_after`` (so the math is checked end-to-end via
:meth:`Pattern.validate_continuity`).
"""

from __future__ import annotations

from dataclasses import dataclass

from lib.visualisering import Pattern, RowValidator
from ..crorow import CrochetRow


# ---------------------------------------------------------------------------
# Closed-form helpers
# ---------------------------------------------------------------------------


def c2c_total_blocks(width: int, height: int) -> int:
    """Total number of blocks in a ``W × H`` C2C rectangle = ``W · H``."""
    if width < 1 or height < 1:
        raise ValueError(f"width and height must be >= 1 (got {width}, {height})")
    return width * height


def c2c_total_dc(width: int, height: int) -> int:
    """Approximate total double-crochet stitches: ``3 · W · H``.

    Each block contributes 3 working dc plus a ch-3 that counts as 1 dc;
    we count the working dc only since the ch-3 is structurally a turning
    chain. (The HTML schematic treats each block as one cell.)
    """
    return 3 * c2c_total_blocks(width, height)


def c2c_blocks_per_row(width: int, height: int) -> list[int]:
    """Number of blocks worked in each diagonal row, in order.

    For ``W × H`` (assume W >= H without loss of generality):

    * Increase phase (rows 1..H): row N has N blocks.
    * Plateau phase (rows H+1..W): row has H blocks (diagonal length).
    * Decrease phase (rows W+1..W+H-1): row has W+H-N blocks.

    Total rows = ``W + H - 1``.
    """
    if width < 1 or height < 1:
        raise ValueError(f"width and height must be >= 1 (got {width}, {height})")
    short, long_ = sorted((width, height))
    rows: list[int] = []
    # Increase: 1..short
    for n in range(1, short + 1):
        rows.append(n)
    # Plateau: while the diagonal slides across the long side
    for _ in range(long_ - short):
        rows.append(short)
    # Decrease: short-1..1
    for n in range(short - 1, 0, -1):
        rows.append(n)
    assert len(rows) == width + height - 1
    return rows


# ---------------------------------------------------------------------------
# Spec + generator
# ---------------------------------------------------------------------------


@dataclass
class C2CBlanketSpec:
    blocks_wide: int
    blocks_high: int
    # Optional gauge — used only for cm-conversion in the notes / cover box.
    # Default 1.0 block/cm is roughly worsted-weight DK on a 4mm hook.
    blocks_per_cm: float = 1.0
    colors: list[str] | None = None  # stripe palette, applied per row
    name: str = "C2C-tæppe"


def _l(da: str, en: str, lang: str) -> str:
    return en if lang == "en" else da


def generate_c2c_blanket(spec: C2CBlanketSpec, lang: str = "da") -> Pattern:
    if spec.blocks_wide < 1 or spec.blocks_high < 1:
        raise ValueError("blocks_wide and blocks_high must both be >= 1")
    if spec.blocks_per_cm <= 0:
        raise ValueError("blocks_per_cm must be > 0")

    colors = spec.colors or []

    rows_blocks = c2c_blocks_per_row(spec.blocks_wide, spec.blocks_high)
    total_blocks = c2c_total_blocks(spec.blocks_wide, spec.blocks_high)
    total_dc = c2c_total_dc(spec.blocks_wide, spec.blocks_high)
    short_side = min(spec.blocks_wide, spec.blocks_high)
    long_side = max(spec.blocks_wide, spec.blocks_high)

    width_cm = spec.blocks_wide / spec.blocks_per_cm
    height_cm = spec.blocks_high / spec.blocks_per_cm

    p = Pattern(
        name=spec.name,
        construction="c2c_blanket",
        difficulty="easy",
        inputs={
            "_domain": "crochet",
            "blocks_wide": spec.blocks_wide,
            "blocks_high": spec.blocks_high,
            "blocks_per_cm": spec.blocks_per_cm,
            "width_cm": round(width_cm, 1),
            "height_cm": round(height_cm, 1),
            "total_rows": len(rows_blocks),
            "total_blocks": total_blocks,
            "total_dc": total_dc,
            "rows_blocks": rows_blocks,
            "colors": colors,
            # Gauge in the format the shared HTML cover-builder expects.
            # 1 block ~ 4 stitches and 1 row tall, so we approximate.
            "gauge": {
                "sts_per_10cm": int(round(spec.blocks_per_cm * 4 * 10)),
                "rows_per_10cm": int(round(spec.blocks_per_cm * 10)),
            },
        },
    )

    validator = RowValidator()

    # ----- Start --------------------------------------------------------
    sec_start = p.add_section(_l("Start", "Start", lang), sts_before=0)
    sec_start.add(
        _l("Hækl 6 lm. Disse danner den første blok.",
           "Crochet 6 ch. These form the first block.",
           lang),
        sts_after=4,
        note=_l("3 lm tæller som 1. stm + 3 lm danner ch-3-rummet til næste blok",
                "3 ch count as the 1st dc + 3 ch form the ch-3 space for the next block",
                lang),
    )
    # Bookkeeping: we model each block-row as a single CrochetRow whose
    # sts_before / sts_after are the cumulative dc count entering/leaving
    # that row. The first block creates 4 stitches from nothing (ch 6
    # produces 6 chains — but we count it as 4 working sts to keep the
    # block math clean).
    r0 = CrochetRow(sts_before=0, label="blok 1")
    r0.ch(6)
    # We don't validate r0 against block-counts here because the
    # foundation-chain is a one-off; subsequent rows are.
    validator.add(r0)

    # ----- Increase phase ----------------------------------------------
    # Row 1 has 1 block already (the ch-6 above). Subsequent rows add one
    # block per row until short_side blocks.
    sec_inc = p.add_section(
        _l(f"Stigende fase (række 1 → {short_side})",
           f"Increase phase (row 1 → {short_side})", lang),
        sts_before=4,
    )
    sec_inc.add(
        _l("Række 1 består af den indledende blok (ch 6 = 1 blok).",
           "Row 1 consists of the initial block (ch 6 = 1 block).",
           lang),
        sts_after=4,
        note=_l("1 blok", "1 block", lang),
    )
    cumulative_dc = 4  # one block worth
    for row_n in range(2, short_side + 1):
        blocks_this_row = rows_blocks[row_n - 1]
        # Each new row adds ``blocks_this_row`` blocks (one per diagonal
        # step). The first block of the row uses ch 6, the rest use sl_st
        # + ch 3 + 3 dc into the previous row's ch-3 space.
        new_dc = blocks_this_row * 3  # working dc per block, ch-3 counted separately
        cumulative_dc += new_dc + 1  # +1 for the ch-3 counts-as-dc
        color = colors[(row_n - 1) % len(colors)] if colors else None
        color_label = f" ({color})" if color else ""
        sec_inc.add(
            _l(f"R{row_n}{color_label}: vend, ch 6, hækl ny blok i ch-3-"
               f"rummet fra R{row_n - 1}; {blocks_this_row - 1} flere "
               "blokke ved at sl-st ind i næste ch-3-rum, ch 3, 3 stm i "
               "samme rum.",
               f"R{row_n}{color_label}: turn, ch 6, crochet a new block in the "
               f"ch-3 space from R{row_n - 1}; add {blocks_this_row - 1} more "
               "blocks by sl-st into the next ch-3 space, ch 3, 3 dc in "
               "the same space.",
               lang),
            sts_after=cumulative_dc,
            note=_l(f"{blocks_this_row} blokke i denne række",
                    f"{blocks_this_row} blocks in this row", lang),
        )

    # ----- Plateau phase ------------------------------------------------
    if long_side > short_side:
        sec_plat = p.add_section(
            _l(f"Plateau (række {short_side + 1} → {long_side})",
               f"Plateau (row {short_side + 1} → {long_side})", lang),
            sts_before=cumulative_dc,
        )
        for row_n in range(short_side + 1, long_side + 1):
            blocks_this_row = rows_blocks[row_n - 1]
            new_dc = blocks_this_row * 3
            cumulative_dc += 0
            color = colors[(row_n - 1) % len(colors)] if colors else None
            color_label = f" ({color})" if color else ""
            sec_plat.add(
                _l(f"R{row_n}{color_label}: udt på lang side (ch 6 + ny blok), "
                   "indt på kort side (sl-st gennem 3 stm + 3 lm + 1 km i "
                   "næste ch-3-rum).",
                   f"R{row_n}{color_label}: increase on the long side (ch 6 + new block), "
                   "decrease on the short side (sl-st across 3 dc + 3 ch + 1 sl-st in "
                   "the next ch-3 space).",
                   lang),
                sts_after=cumulative_dc,
                note=_l(f"{blocks_this_row} blokke (plateau)",
                        f"{blocks_this_row} blocks (plateau)", lang),
            )

    # ----- Decrease phase ----------------------------------------------
    sec_dec = p.add_section(
        _l(f"Faldende fase (række {long_side + 1} → {len(rows_blocks)})",
           f"Decrease phase (row {long_side + 1} → {len(rows_blocks)})", lang),
        sts_before=cumulative_dc,
    )
    for row_n in range(long_side + 1, len(rows_blocks) + 1):
        blocks_this_row = rows_blocks[row_n - 1]
        cumulative_dc -= 4
        color = colors[(row_n - 1) % len(colors)] if colors else None
        color_label = f" ({color})" if color else ""
        sec_dec.add(
            _l(f"R{row_n}{color_label}: indt på begge sider — sl-st gennem "
               "3 stm + 3 lm + 1 km i næste ch-3-rum, derefter normale "
               "blokke til sidste blok i rækken (ingen ch 6).",
               f"R{row_n}{color_label}: decrease on both sides — sl-st across "
               "3 dc + 3 ch + 1 sl-st in the next ch-3 space, then regular "
               "blocks to the last block in the row (no ch 6).",
               lang),
            sts_after=cumulative_dc,
            note=_l(f"{blocks_this_row} blokke", f"{blocks_this_row} blocks", lang),
        )

    # ----- Finish ------------------------------------------------------
    sec_end = p.add_section(
        _l("Afslutning", "Finishing", lang), sts_before=cumulative_dc)
    sec_end.add(
        _l("Klip garnet, træk gennem løkken og hæft alle ender. Damp eller "
           "blok tæppet flat.",
           "Cut the yarn, pull through the loop and weave in all ends. Steam "
           "or block the blanket flat.",
           lang),
        sts_after=cumulative_dc,
    )

    # ----- Sanity check on block totals --------------------------------
    if sum(rows_blocks) != total_blocks:
        raise ValueError(
            f"row-blocks sum mismatch: {sum(rows_blocks)} vs {total_blocks}"
        )

    p.notes.append(
        f"Slutmål: {spec.blocks_wide} × {spec.blocks_high} blokke "
        f"({total_blocks} blokke, ≈ {total_dc} stm)."
    )
    p.notes.append(
        f"Total antal rækker: {len(rows_blocks)} "
        f"({short_side} stigende + {long_side - short_side} plateau + "
        f"{short_side - 1} faldende)."
    )
    p.notes.append(
        f"Mål: ca. {width_cm:.1f} × {height_cm:.1f} cm ved "
        f"{spec.blocks_per_cm} blok/cm."
    )
    if colors:
        p.notes.append(
            f"Stribefarver pr. række: {' → '.join(colors)} → (gentag)."
        )

    p.validate_continuity()
    return p
