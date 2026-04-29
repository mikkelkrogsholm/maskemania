"""SVG schematic generators.

Each function takes a Pattern (or specific inputs) and returns an SVG string
sized via viewBox. Schematics use industry-standard knitting magazine style:
thin black lines, light-gray fill, sans-serif labels, dimension arrows on
the outside of the piece.
"""

from __future__ import annotations
from typing import Iterable

# Style constants
STROKE = "#1a1a1a"
FILL = "#f0ece4"  # warm cream — feels like wool
ACCENT = "#8b1a1a"
LABEL_SIZE = 11
DIM_SIZE = 10
GRID_LINE = "#d0d0d0"


def _svg_open(width: int, height: int, *, padding: int = 30) -> str:
    """Open an SVG with viewBox and consistent padding."""
    vb_w = width + 2 * padding
    vb_h = height + 2 * padding
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" '
        f'class="schematic" preserveAspectRatio="xMidYMid meet">'
        f'<g transform="translate({padding},{padding})">'
    )


def _svg_close() -> str:
    return "</g></svg>"


def _dim_h(x1: float, x2: float, y: float, label: str, *, above: bool = True) -> str:
    """Horizontal dimension line with arrows + label."""
    # tick lines and the dimension line
    tick = 4
    yt = y - tick if above else y + tick
    label_y = y - 8 if above else y + 16
    return (
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{STROKE}" stroke-width="0.6"/>'
        f'<line x1="{x1}" y1="{y-tick}" x2="{x1}" y2="{y+tick}" stroke="{STROKE}" stroke-width="0.6"/>'
        f'<line x1="{x2}" y1="{y-tick}" x2="{x2}" y2="{y+tick}" stroke="{STROKE}" stroke-width="0.6"/>'
        f'<text x="{(x1+x2)/2}" y="{label_y}" text-anchor="middle" '
        f'font-size="{DIM_SIZE}" fill="{STROKE}">{label}</text>'
    )


def _dim_v(y1: float, y2: float, x: float, label: str, *, left: bool = True) -> str:
    """Vertical dimension line with arrows + label."""
    tick = 4
    label_x = x - 8 if left else x + 8
    anchor = "end" if left else "start"
    return (
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{STROKE}" stroke-width="0.6"/>'
        f'<line x1="{x-tick}" y1="{y1}" x2="{x+tick}" y2="{y1}" stroke="{STROKE}" stroke-width="0.6"/>'
        f'<line x1="{x-tick}" y1="{y2}" x2="{x+tick}" y2="{y2}" stroke="{STROKE}" stroke-width="0.6"/>'
        f'<text x="{label_x}" y="{(y1+y2)/2 + 4}" text-anchor="{anchor}" '
        f'font-size="{DIM_SIZE}" fill="{STROKE}">{label}</text>'
    )


# ---------------------------------------------------------------------------
# Hue
# ---------------------------------------------------------------------------

def hue_schematic(*, finished_circumference_cm: float, total_height_cm: float,
                  rib_height_cm: float, sectors: int) -> str:
    """Side view of a hat: rectangle for body + curved crown."""
    # scale: 4 px per cm
    s = 4.0
    half_circ = finished_circumference_cm / 2  # show flat half (it's a tube)
    w = half_circ * s
    body_h = (total_height_cm - rib_height_cm) * s * 0.65  # crown takes ~35%
    crown_h = (total_height_cm - rib_height_cm) * s * 0.35
    rib_h = rib_height_cm * s
    total_h = rib_h + body_h + crown_h

    # Layout: rib at bottom, body in middle, crown curves to point at top
    out = [_svg_open(int(w), int(total_h), padding=80)]

    # rib (zigzag pattern band)
    out.append(
        f'<rect x="0" y="{body_h+crown_h}" width="{w}" height="{rib_h}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )
    # rib lines
    for i in range(0, int(w), 6):
        out.append(
            f'<line x1="{i}" y1="{body_h+crown_h}" x2="{i}" y2="{body_h+crown_h+rib_h}" '
            f'stroke="{GRID_LINE}" stroke-width="0.5"/>'
        )

    # body
    out.append(
        f'<rect x="0" y="{crown_h}" width="{w}" height="{body_h}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )

    # crown (curve to point)
    out.append(
        f'<path d="M 0 {crown_h} '
        f'Q {w/2} {-crown_h*0.3} {w} {crown_h} Z" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )

    # dimensions
    out.append(_dim_h(0, w, total_h + 24, f"{half_circ:.0f} cm (= ½ omkreds)"))
    out.append(_dim_v(crown_h, crown_h + body_h + rib_h, w + 18,
                      f"{total_height_cm - 0:.0f} cm i alt", left=False))
    out.append(_dim_v(body_h + crown_h, total_h, -8,
                      f"{rib_height_cm:.0f} cm rib"))

    out.append(_svg_close())
    return "".join(out)


def crown_top_view(*, sectors: int, finished_circumference_cm: float) -> str:
    """Bird's-eye view of crown: circle divided into N sectors with spiral
    decrease lines. Pure geometric SVG."""
    import math
    r = 90  # radius
    cx, cy = r + 20, r + 20
    out = [_svg_open(2 * r, 2 * r + 30, padding=20)]

    # outer circle
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )

    # sector lines (decrease seams) — slightly spiraled
    for i in range(sectors):
        a0 = (i / sectors) * 2 * math.pi
        a1 = ((i + 0.95) / sectors) * 2 * math.pi  # slight spiral
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        out.append(
            f'<path d="M {cx} {cy} L {x0:.1f} {y0:.1f}" '
            f'stroke="{ACCENT}" stroke-width="1.4" fill="none"/>'
        )

    # center dot (final closed point)
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="3" fill="{ACCENT}"/>'
    )
    # caption
    out.append(
        f'<text x="{cx}" y="{2*r+30}" text-anchor="middle" '
        f'font-size="{LABEL_SIZE}" fill="{STROKE}">'
        f'{sectors} sektorer set ovenfra</text>'
    )
    out.append(_svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# Tørklæde
# ---------------------------------------------------------------------------

def tørklæde_schematic(*, width_cm: float, length_cm: float) -> str:
    """A simple rectangle with measurements."""
    s = 1.5  # px per cm — scarves are long
    w = length_cm * s
    h = width_cm * s
    # Cap the aspect ratio so very long thin scarves still render
    if w > 600:
        s = 600 / length_cm
        w = 600
        h = width_cm * s

    out = [_svg_open(int(w), int(h), padding=50)]
    out.append(
        f'<rect x="0" y="0" width="{w}" height="{h}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )
    # garter ridges (horizontal lines)
    for i in range(int(h / 4) + 1):
        y = i * 4
        out.append(
            f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" '
            f'stroke="{GRID_LINE}" stroke-width="0.4"/>'
        )
    out.append(_dim_h(0, w, h + 28, f"{length_cm:.0f} cm"))
    out.append(_dim_v(0, h, -8, f"{width_cm:.0f} cm"))
    out.append(_svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# Raglan: flat schematic of body (back/front) + one sleeve
# ---------------------------------------------------------------------------

def raglan_schematic(*, finished_bust_cm: float, body_length_cm: float,
                     yoke_depth_cm: float, neck_circumference_cm: float,
                     upper_arm_cm: float, wrist_cm: float,
                     sleeve_length_cm: float) -> str:
    """Two-part schematic: front/back panel on left, sleeve on right.
    Industry-standard flat layout."""
    s = 2.5  # px per cm
    half_bust = finished_bust_cm / 2
    half_neck = neck_circumference_cm / 2
    body_w = half_bust * s
    body_total_h = (body_length_cm + yoke_depth_cm) * s
    yoke_h = yoke_depth_cm * s
    body_main_h = body_length_cm * s
    neck_w = half_neck * s

    # Sleeve trapezoid
    sleeve_top_w = upper_arm_cm * s
    sleeve_bot_w = wrist_cm * s
    sleeve_h = sleeve_length_cm * s

    gap = 140  # gap between body and sleeve (must fit yoke-depth label)
    total_w = body_w + gap + sleeve_top_w
    total_h = max(body_total_h, sleeve_h)

    out = [_svg_open(int(total_w), int(total_h), padding=70)]

    # ---- BODY panel (back/front) ----
    # Trapezoidal yoke at top: narrower at neck, wider at bust
    bx, by = 0, 0
    # Bust hem corner points
    bot_left, bot_right = (bx, by + body_total_h), (bx + body_w, by + body_total_h)
    # Underarm corner points (where yoke meets body sides)
    underarm_left = (bx, by + yoke_h)
    underarm_right = (bx + body_w, by + yoke_h)
    # Neck top points (centered horizontally)
    neck_left = (bx + (body_w - neck_w) / 2, by)
    neck_right = (bx + (body_w + neck_w) / 2, by)

    body_path = (
        f'M {neck_left[0]:.1f} {neck_left[1]:.1f} '
        f'L {underarm_left[0]:.1f} {underarm_left[1]:.1f} '
        f'L {bot_left[0]:.1f} {bot_left[1]:.1f} '
        f'L {bot_right[0]:.1f} {bot_right[1]:.1f} '
        f'L {underarm_right[0]:.1f} {underarm_right[1]:.1f} '
        f'L {neck_right[0]:.1f} {neck_right[1]:.1f} '
        # neck curve
        f'Q {(neck_left[0]+neck_right[0])/2:.1f} {neck_left[1]+8:.1f} '
        f'{neck_left[0]:.1f} {neck_left[1]:.1f} Z'
    )
    out.append(
        f'<path d="{body_path}" fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )

    # Body label
    out.append(
        f'<text x="{bx + body_w/2}" y="{by + body_total_h/2}" '
        f'text-anchor="middle" font-size="{LABEL_SIZE}" fill="{STROKE}" '
        f'font-style="italic">Krop (for/bag)</text>'
    )

    # Body dimensions
    out.append(_dim_h(bx, bx + body_w, by + body_total_h + 28,
                      f"½ bryst: {half_bust:.0f} cm"))
    out.append(_dim_v(by + yoke_h, by + body_total_h, bx - 8,
                      f"{body_length_cm:.0f} cm"))
    out.append(_dim_v(by, by + yoke_h, bx + body_w + 12,
                      f"bærestykke {yoke_depth_cm:.0f} cm", left=False))
    out.append(_dim_h(neck_left[0], neck_right[0], by - 12,
                      f"hals: {half_neck:.0f} cm", above=True))

    # ---- SLEEVE trapezoid ----
    sx = bx + body_w + gap
    sy = by + (body_total_h - sleeve_h) / 2  # vertically centered with body
    sleeve_top_left = (sx, sy)
    sleeve_top_right = (sx + sleeve_top_w, sy)
    sleeve_bot_left = (sx + (sleeve_top_w - sleeve_bot_w) / 2, sy + sleeve_h)
    sleeve_bot_right = (sx + (sleeve_top_w + sleeve_bot_w) / 2, sy + sleeve_h)
    sleeve_path = (
        f'M {sleeve_top_left[0]:.1f} {sleeve_top_left[1]:.1f} '
        f'L {sleeve_top_right[0]:.1f} {sleeve_top_right[1]:.1f} '
        f'L {sleeve_bot_right[0]:.1f} {sleeve_bot_right[1]:.1f} '
        f'L {sleeve_bot_left[0]:.1f} {sleeve_bot_left[1]:.1f} Z'
    )
    out.append(
        f'<path d="{sleeve_path}" fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )

    # Sleeve label
    out.append(
        f'<text x="{sx + sleeve_top_w/2}" y="{sy + sleeve_h/2}" '
        f'text-anchor="middle" font-size="{LABEL_SIZE}" fill="{STROKE}" '
        f'font-style="italic">Ærme</text>'
    )

    # Sleeve dimensions
    out.append(_dim_h(sleeve_top_left[0], sleeve_top_right[0], sy - 12,
                      f"overarm: {upper_arm_cm:.0f} cm"))
    out.append(_dim_h(sleeve_bot_left[0], sleeve_bot_right[0], sy + sleeve_h + 28,
                      f"håndled: {wrist_cm:.0f} cm"))
    out.append(_dim_v(sy, sy + sleeve_h, sx + sleeve_top_w + 8,
                      f"{sleeve_length_cm:.0f} cm", left=False))

    out.append(_svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# Sock schematic — leg + foot in an L-shape
# ---------------------------------------------------------------------------

def sock_schematic(*, foot_length_cm: float, foot_circ_cm: float,
                    leg_length_cm: float) -> str:
    """L-shaped schematic: vertical leg + horizontal foot meeting at the heel.

    The leg is a rectangle with width = ½ circumference (flat-view) and
    height = leg length. The foot is a rectangle attached to the bottom of
    the leg with length = foot length, height = ½ circ. A small triangle
    inside the corner indicates the heel turn.
    """
    s = 4.0  # px per cm
    leg_w = (foot_circ_cm / 2) * s
    leg_h = leg_length_cm * s
    foot_w = foot_length_cm * s
    foot_h = (foot_circ_cm / 2) * s

    pad_y = 30
    total_w = max(leg_w, foot_w + leg_w * 0.0) + 30
    total_h = leg_h + foot_h + pad_y

    out = [_svg_open(int(total_w), int(total_h), padding=70)]

    # leg rectangle (top)
    out.append(
        f'<rect x="0" y="0" width="{leg_w}" height="{leg_h}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )
    # foot rectangle (extends right from leg base)
    out.append(
        f'<rect x="0" y="{leg_h}" width="{foot_w}" height="{foot_h}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>'
    )
    # heel turn — a little triangle in the corner
    out.append(
        f'<path d="M 0 {leg_h} L {leg_w * 0.6:.1f} {leg_h:.1f} '
        f'L 0 {leg_h + foot_h * 0.7:.1f} Z" '
        f'fill="{ACCENT}" fill-opacity="0.15" stroke="{ACCENT}" stroke-width="0.8"/>'
    )
    # toe — small wedge at far right
    out.append(
        f'<path d="M {foot_w - foot_h * 0.5:.1f} {leg_h:.1f} '
        f'L {foot_w:.1f} {leg_h + foot_h / 2:.1f} '
        f'L {foot_w - foot_h * 0.5:.1f} {leg_h + foot_h:.1f} Z" '
        f'fill="{ACCENT}" fill-opacity="0.15" stroke="{ACCENT}" stroke-width="0.8"/>'
    )

    # dimensions
    out.append(_dim_h(0, leg_w, -8, f"½ omkreds: {foot_circ_cm/2:.0f} cm"))
    out.append(_dim_v(0, leg_h, -8, f"{leg_length_cm:.0f} cm"))
    out.append(_dim_h(0, foot_w, leg_h + foot_h + 20,
                      f"fodlængde: {foot_length_cm:.0f} cm"))

    out.append(_svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# Filet pixel grid
# ---------------------------------------------------------------------------

def filet_grid(grid: list[list[bool]]) -> str:
    """Pixel-grid schematic for a filet pattern.

    ``grid`` is a list of rows, top→bottom, each row a list of bool: True =
    filled block (3 dc), False = open mesh (1 dc + 2 ch).
    """
    if not grid:
        return _svg_open(40, 40) + "</g></svg>"
    h_cells = len(grid)
    w_cells = max(len(r) for r in grid)
    cell = 14
    w = w_cells * cell
    h = h_cells * cell
    out = [_svg_open(w, h, padding=40)]
    out.append(
        f'<rect x="0" y="0" width="{w}" height="{h}" '
        f'fill="white" stroke="{STROKE}" stroke-width="1.0"/>'
    )
    for r, row in enumerate(grid):
        for c, filled in enumerate(row):
            x = c * cell
            y = r * cell
            if filled:
                out.append(
                    f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                    f'fill="{ACCENT}" fill-opacity="0.85" '
                    f'stroke="{STROKE}" stroke-width="0.4"/>'
                )
            else:
                out.append(
                    f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                    f'fill="white" stroke="{GRID_LINE}" stroke-width="0.4"/>'
                )
    out.append(_dim_h(0, w, h + 20, f"{w_cells} celler"))
    out.append(_dim_v(0, h, -8, f"{h_cells} rækker"))
    out.append(_svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# Gauge swatch visualizer
# ---------------------------------------------------------------------------

def gauge_swatch(sts_per_10cm: float, rows_per_10cm: float) -> str:
    """A 10×10 cm grid showing how many sts × rows in 10 cm."""
    cell = 8
    sts = int(round(sts_per_10cm))
    rows = int(round(rows_per_10cm))
    w = sts * cell
    h = rows * cell

    out = [_svg_open(w, h, padding=80)]
    # frame
    out.append(
        f'<rect x="0" y="0" width="{w}" height="{h}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="1.5"/>'
    )
    # vertical grid (stitch columns)
    for i in range(1, sts):
        out.append(
            f'<line x1="{i*cell}" y1="0" x2="{i*cell}" y2="{h}" '
            f'stroke="{GRID_LINE}" stroke-width="0.4"/>'
        )
    # horizontal grid (rows)
    for i in range(1, rows):
        out.append(
            f'<line x1="0" y1="{i*cell}" x2="{w}" y2="{i*cell}" '
            f'stroke="{GRID_LINE}" stroke-width="0.4"/>'
        )
    # 10 cm dimension labels
    out.append(_dim_h(0, w, h + 20, f"{sts} m / 10 cm"))
    out.append(_dim_v(0, h, -8, f"{rows} p / 10 cm"))
    out.append(_svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# Crown decrease chart — one sector
# ---------------------------------------------------------------------------

def crown_chart(plan: list[tuple[int, int, str]], *, sectors: int = 8,
                start_per_sector: int) -> str:
    """A stitch chart for one of the N identical sectors.
    Each row corresponds to one round in the plan; cells are k or k2tog.
    """
    cell = 14
    # Determine max width (= start_per_sector)
    max_w = start_per_sector
    # Filter plan: only decrease rounds (those with "*" in instruction), and
    # we'll add plain rounds visually as a single small marker.
    rows_to_show = []
    for rnd_num, sts, instr in plan:
        is_dec = "k2tog" in instr
        rows_to_show.append((rnd_num, sts, instr, is_dec))

    n_rows = len(rows_to_show)
    chart_w = max_w * cell
    chart_h = n_rows * cell

    out = [_svg_open(chart_w, chart_h + 60, padding=40)]

    # chart frame
    out.append(
        f'<rect x="0" y="0" width="{chart_w}" height="{chart_h}" '
        f'fill="{FILL}" stroke="{STROKE}" stroke-width="0.8"/>'
    )

    # Render each row from bottom up (knitting convention: row 1 at bottom)
    for i, (rnd_num, sts, instr, is_dec) in enumerate(rows_to_show):
        y = chart_h - (i + 1) * cell  # bottom row = first round
        per_sector = sts // sectors
        # Row label
        out.append(
            f'<text x="-6" y="{y + cell - 4}" text-anchor="end" '
            f'font-size="9" fill="{STROKE}">o.{rnd_num}</text>'
        )
        # Cells for this row (only show one sector)
        if is_dec:
            # k(per_sector) cells, then 1 k2tog
            for j in range(per_sector):
                x = j * cell
                out.append(
                    f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                    f'fill="white" stroke="{GRID_LINE}" stroke-width="0.4"/>'
                )
            x = per_sector * cell
            out.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'fill="{ACCENT}" stroke="{STROKE}" stroke-width="0.6"/>'
                f'<text x="{x + cell/2}" y="{y + cell - 3}" text-anchor="middle" '
                f'font-size="9" fill="white" font-weight="600">∧</text>'
            )
        else:
            # plain round: just k cells
            for j in range(per_sector + 1):
                x = j * cell
                out.append(
                    f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                    f'fill="white" stroke="{GRID_LINE}" stroke-width="0.4"/>'
                )

    # Legend
    legend_y = chart_h + 18
    out.append(
        f'<rect x="0" y="{legend_y}" width="{cell}" height="{cell}" '
        f'fill="white" stroke="{GRID_LINE}" stroke-width="0.4"/>'
        f'<text x="{cell + 4}" y="{legend_y + cell - 3}" font-size="10" fill="{STROKE}">'
        f'= 1 ret</text>'
    )
    out.append(
        f'<rect x="80" y="{legend_y}" width="{cell}" height="{cell}" '
        f'fill="{ACCENT}" stroke="{STROKE}" stroke-width="0.6"/>'
        f'<text x="{80 + cell/2}" y="{legend_y + cell - 3}" text-anchor="middle" '
        f'font-size="9" fill="white" font-weight="600">∧</text>'
        f'<text x="{80 + cell + 4}" y="{legend_y + cell - 3}" font-size="10" fill="{STROKE}">'
        f'= k2tog (2 r sm)</text>'
    )

    out.append(_svg_close())
    return "".join(out)
