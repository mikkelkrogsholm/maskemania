"""Crochet-specific SVG schematics.

Builds on the generic primitives in :mod:`lib.visualisering.svg` (style
constants, padding, dimension lines) and adds crochet-specific diagrams:

* :func:`amigurumi_diagram` — side and top views of a sphere with rounds.
* :func:`granny_square_diagram` — concentric coloured rounds.
* :func:`scarf_schematic` — flat rectangle (re-exports the generic one).
"""

from __future__ import annotations
import math

from lib.visualisering.svg import (
    STROKE, FILL, ACCENT, GRID_LINE, LABEL_SIZE, DIM_SIZE,
    _svg_open, _svg_close, _dim_h, _dim_v,
    tørklæde_schematic as _generic_tørklæde,
    filet_grid as _filet_grid,
)


# ---------------------------------------------------------------------------
# Amigurumi
# ---------------------------------------------------------------------------

def amigurumi_diagram(*, rounds: int, max_sts: int,
                      diameter_cm: float | None = None) -> str:
    """Side + top view of a sphere divided into ``rounds`` rings.

    The "side view" is two halves: an upper half drawn as concentric arcs
    (one per increase round) and a lower half drawn as concentric arcs (one
    per decrease round). The "top view" is concentric circles, one per
    ring, with stitch counts labelled at the equator and at every other
    ring.
    """
    if rounds < 1:
        raise ValueError("rounds must be >= 1")

    radius = 90
    cx, cy = radius + 30, radius + 30
    out = [_svg_open(2 * radius + 60, 2 * radius + 80, padding=20)]

    # Sphere outline
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.5"/>'
    )

    # Concentric rings (latitude lines): for each round, draw an ellipse
    # at the equivalent latitude. Round 1 is at the top pole, round
    # ``rounds`` is at the bottom pole, round (rounds+1)/2 is at the equator.
    for i in range(1, rounds + 1):
        # latitude angle: -π/2 (top) → +π/2 (bottom)
        t = (i - 1) / max(1, rounds - 1)
        phi = -math.pi / 2 + t * math.pi
        ry = radius * math.cos(phi)        # vertical squish
        y = cy + radius * math.sin(phi)
        if abs(ry) < 0.5:
            continue  # poles
        # Latitude lines as horizontal ellipses
        out.append(
            f'<ellipse cx="{cx}" cy="{y:.1f}" rx="{radius * 0.999}" '
            f'ry="{abs(ry):.1f}" fill="none" stroke="{ACCENT}" '
            f'stroke-width="0.6" stroke-dasharray="2 2"/>'
        )

    # Equator highlight
    out.append(
        f'<line x1="{cx-radius}" y1="{cy}" x2="{cx+radius}" y2="{cy}" '
        f'stroke="{ACCENT}" stroke-width="1.2"/>'
    )
    out.append(
        f'<text x="{cx+radius+8}" y="{cy+4}" font-size="{LABEL_SIZE}" '
        f'fill="{STROKE}">ækvator: {max_sts} m</text>'
    )

    # Pole labels
    out.append(
        f'<text x="{cx}" y="{cy-radius-6}" text-anchor="middle" '
        f'font-size="{LABEL_SIZE}" fill="{STROKE}">start (magic ring)</text>'
    )
    out.append(
        f'<text x="{cx}" y="{cy+radius+18}" text-anchor="middle" '
        f'font-size="{LABEL_SIZE}" fill="{STROKE}">lukning</text>'
    )

    # Caption / dimension
    if diameter_cm is not None:
        out.append(
            _dim_h(cx - radius, cx + radius, cy + radius + 38,
                   f"diameter {diameter_cm:.1f} cm")
        )

    out.append(_svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# Granny square
# ---------------------------------------------------------------------------

_DEFAULT_GRANNY_PALETTE = [
    "#a64b4b", "#d9a44b", "#5b8a8a", "#7a5b8a",
    "#5b7a8a", "#8a7a5b", "#5b8a5b", "#8a5b7a",
]


def granny_square_diagram(*, rounds: int,
                          colors: list[str] | None = None) -> str:
    """Concentric coloured squares — one per round.

    Each round is drawn as a square with side length ``2·N·step``. Colours
    cycle through the input list (or a default palette).
    """
    if rounds < 1:
        raise ValueError("rounds must be >= 1")
    palette = colors or _DEFAULT_GRANNY_PALETTE
    step = 14
    side = rounds * 2 * step + 2 * step
    out = [_svg_open(side, side, padding=30)]

    cx = side / 2
    cy = side / 2
    for n in range(rounds, 0, -1):
        s = n * 2 * step + step
        x = cx - s / 2
        y = cy - s / 2
        color = palette[(n - 1) % len(palette)]
        out.append(
            f'<rect x="{x}" y="{y}" width="{s}" height="{s}" '
            f'fill="{color}" stroke="{STROKE}" stroke-width="0.8" '
            f'opacity="0.85"/>'
        )
        # Label this round on the right edge
        out.append(
            f'<text x="{x + s + 4}" y="{cy + 4}" '
            f'font-size="{DIM_SIZE}" fill="{STROKE}">o.{n}</text>'
        )

    # Centre dot
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="3" fill="{STROKE}"/>'
    )
    out.append(_svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# Scarf — re-export the generic rectangle schematic
# ---------------------------------------------------------------------------

def scarf_schematic(*, width_cm: float, length_cm: float) -> str:
    return _generic_tørklæde(width_cm=width_cm, length_cm=length_cm)


# ---------------------------------------------------------------------------
# Filet — re-export pixel-grid schematic from the generic library
# ---------------------------------------------------------------------------

def filet_diagram(grid: list[list[bool]]) -> str:
    return _filet_grid(grid)


# ---------------------------------------------------------------------------
# Tunisian — flat rectangle with a stitch grid showing vertical bars
# ---------------------------------------------------------------------------

def tunisian_diagram(*, width_sts: int, rows: int) -> str:
    """A grid suggesting Tunisian vertical bars: ``width × rows`` cells."""
    if width_sts < 1 or rows < 1:
        raise ValueError("width_sts and rows must both be >= 1")
    cell_w = 10
    cell_h = 10
    w = width_sts * cell_w
    h = rows * cell_h
    out = [_svg_open(w, h, padding=40)]
    out.append(
        f'<rect x="0" y="0" width="{w}" height="{h}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.0"/>'
    )
    # vertical bars (the defining feature of TSS)
    for i in range(width_sts):
        x = i * cell_w + cell_w / 2
        out.append(
            f'<line x1="{x}" y1="2" x2="{x}" y2="{h - 2}" '
            f'stroke="{ACCENT}" stroke-width="1.0" opacity="0.6"/>'
        )
    # row separators
    for j in range(1, rows):
        y = j * cell_h
        out.append(
            f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" '
            f'stroke="{GRID_LINE}" stroke-width="0.4"/>'
        )
    out.append(_dim_h(0, w, h + 18, f"{width_sts} m"))
    out.append(_dim_v(0, h, -8, f"{rows} rækker"))
    out.append(_svg_close())
    return "".join(out)
