"""SVG knit-chart symbol library.

We render chart symbols as raw SVG geometry — no font dependency. Each symbol
is a single ``<g>`` containing primitive ``<path>``/``<line>``/``<circle>``/
``<rect>`` elements. The grid renderer (``chart_grid``) lays a 2D array of
symbol names out as a knitting chart with row numbers on the right (row 1
at the bottom, the standard knitting convention) and a frame around the grid.

The supported symbols are deliberately minimal — they cover the lace + simple-
decrease vocabulary needed by ``lace_shawl`` and most beginner/intermediate
lace patterns:

    knit       k       — empty cell (RS knit / WS purl)
    purl       p       — small filled square in the centre
    k2tog              — right-leaning slash
    ssk                — left-leaning slash
    yo                 — open circle
    cdd                — pointed triangle (centred double dec)
    k3tog              — double right-leaning slash
    sl1                — V-shape (slipped stitch)
    no-stitch          — diagonal-hatched grey cell

Style is intentionally line-art only: 0.6 px black strokes on a near-white
fill so the chart prints cleanly and can be re-coloured via CSS.
"""

from __future__ import annotations

# Aliases — accept several common spellings for each symbol.
_ALIASES: dict[str, str] = {
    "k": "knit",
    "knit": "knit",
    "p": "purl",
    "purl": "purl",
    "k2tog": "k2tog",
    "ssk": "ssk",
    "yo": "yo",
    "cdd": "cdd",
    "sk2p": "cdd",  # same shape, different name
    "k3tog": "k3tog",
    "sl": "sl1",
    "sl1": "sl1",
    "ns": "no-stitch",
    "no-stitch": "no-stitch",
    "nostitch": "no-stitch",
}

SUPPORTED_SYMBOLS: tuple[str, ...] = (
    "knit", "purl", "k2tog", "ssk", "yo", "cdd", "k3tog", "sl1", "no-stitch",
)

# Human-readable English / Danish text for each symbol — used by the legend.
SYMBOL_LABELS: dict[str, dict[str, str]] = {
    "knit":      {"en": "knit on RS, purl on WS",
                  "da": "ret på rs, vrang på vs"},
    "purl":      {"en": "purl on RS, knit on WS",
                  "da": "vrang på rs, ret på vs"},
    "k2tog":     {"en": "k2tog (right-leaning dec)",
                  "da": "2 r sm (højre-hældende)"},
    "ssk":       {"en": "ssk (left-leaning dec)",
                  "da": "drej r sm (venstre-hældende)"},
    "yo":        {"en": "yarn over",
                  "da": "slå om (SLO)"},
    "cdd":       {"en": "cdd (centred double dec, sl2-k1-p2sso)",
                  "da": "cdd (central dobbelt-indtagning)"},
    "k3tog":     {"en": "k3tog (3 sts → 1)",
                  "da": "3 r sm"},
    "sl1":       {"en": "slip 1 (held to back)",
                  "da": "tag 1 m løs af"},
    "no-stitch": {"en": "no stitch — grid placeholder",
                  "da": "ingen maske — grid-placeholder"},
}

STROKE = "#1a1a1a"
LIGHT_FILL = "#ffffff"
GREY_FILL = "#cfcec8"


def _normalise(name: str) -> str:
    n = name.strip().lower().replace("_", "-")
    if n not in _ALIASES:
        raise KeyError(
            f"unknown chart symbol {name!r}. Known: "
            + ", ".join(sorted(set(_ALIASES.values())))
        )
    return _ALIASES[n]


def symbol(name: str, x: float, y: float, cell: int = 24) -> str:
    """Return SVG markup for a single charted cell.

    The returned snippet is one ``<g>`` containing the cell's background
    rectangle plus the symbol geometry. ``x``/``y`` is the upper-left
    corner of the cell in the parent coordinate system.
    """
    if cell < 6:
        raise ValueError("cell size must be at least 6")
    sym = _normalise(name)
    cx = x + cell / 2
    cy = y + cell / 2
    # Background rectangle for every cell (so cells line up perfectly).
    fill = GREY_FILL if sym == "no-stitch" else LIGHT_FILL
    bg = (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{cell}" height="{cell}" '
        f'fill="{fill}" stroke="{STROKE}" stroke-width="0.6"/>'
    )
    body = ""

    if sym == "knit":
        # Empty cell. We add a faint vertical hint so the user can tell it
        # isn't accidentally blank (useful when printed).
        body = (
            f'<line x1="{cx:.2f}" y1="{y + cell*0.25:.2f}" '
            f'x2="{cx:.2f}" y2="{y + cell*0.75:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.4" opacity="0.0"/>'
        )
    elif sym == "purl":
        # Centre dot — represents the bumpy purl ridge.
        r = cell * 0.18
        body = (
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" '
            f'fill="{STROKE}" stroke="none"/>'
        )
    elif sym == "k2tog":
        # Right-leaning slash from lower-left to upper-right.
        pad = cell * 0.18
        body = (
            f'<line x1="{x + pad:.2f}" y1="{y + cell - pad:.2f}" '
            f'x2="{x + cell - pad:.2f}" y2="{y + pad:.2f}" '
            f'stroke="{STROKE}" stroke-width="1.4" stroke-linecap="round"/>'
        )
    elif sym == "ssk":
        # Left-leaning slash from upper-left to lower-right.
        pad = cell * 0.18
        body = (
            f'<line x1="{x + pad:.2f}" y1="{y + pad:.2f}" '
            f'x2="{x + cell - pad:.2f}" y2="{y + cell - pad:.2f}" '
            f'stroke="{STROKE}" stroke-width="1.4" stroke-linecap="round"/>'
        )
    elif sym == "yo":
        # Hollow circle in the middle.
        r = cell * 0.28
        body = (
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" '
            f'fill="none" stroke="{STROKE}" stroke-width="1.0"/>'
        )
    elif sym == "cdd":
        # Upward-pointing triangle.
        pad = cell * 0.18
        x0, y0 = cx, y + pad
        x1, y1 = x + pad, y + cell - pad
        x2, y2 = x + cell - pad, y + cell - pad
        body = (
            f'<path d="M {x0:.2f} {y0:.2f} L {x1:.2f} {y1:.2f} '
            f'L {x2:.2f} {y2:.2f} Z" fill="none" '
            f'stroke="{STROKE}" stroke-width="1.0" stroke-linejoin="round"/>'
        )
    elif sym == "k3tog":
        # Double right-leaning slash.
        pad = cell * 0.18
        offset = cell * 0.18
        body = (
            f'<line x1="{x + pad:.2f}" y1="{y + cell - pad:.2f}" '
            f'x2="{x + cell - pad:.2f}" y2="{y + pad:.2f}" '
            f'stroke="{STROKE}" stroke-width="1.2" stroke-linecap="round"/>'
            f'<line x1="{x + pad + offset:.2f}" y1="{y + cell - pad:.2f}" '
            f'x2="{x + cell - pad:.2f}" y2="{y + pad + offset:.2f}" '
            f'stroke="{STROKE}" stroke-width="1.2" stroke-linecap="round"/>'
        )
    elif sym == "sl1":
        # V-shape opening downward.
        pad = cell * 0.22
        body = (
            f'<path d="M {x + pad:.2f} {y + pad:.2f} '
            f'L {cx:.2f} {y + cell - pad:.2f} '
            f'L {x + cell - pad:.2f} {y + pad:.2f}" fill="none" '
            f'stroke="{STROKE}" stroke-width="1.2" stroke-linejoin="round"/>'
        )
    elif sym == "no-stitch":
        # Diagonal hatching across the grey cell.
        # Two diagonal lines for clarity; cell is already grey-filled.
        body = (
            f'<line x1="{x:.2f}" y1="{y + cell:.2f}" '
            f'x2="{x + cell:.2f}" y2="{y:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.5" opacity="0.7"/>'
            f'<line x1="{x:.2f}" y1="{y + cell*0.5:.2f}" '
            f'x2="{x + cell*0.5:.2f}" y2="{y:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.5" opacity="0.5"/>'
            f'<line x1="{x + cell*0.5:.2f}" y1="{y + cell:.2f}" '
            f'x2="{x + cell:.2f}" y2="{y + cell*0.5:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.5" opacity="0.5"/>'
        )

    return f'<g class="cs cs-{sym}">{bg}{body}</g>'


def chart_grid(rows: list[list[str]], cell_size: int = 24, *,
               repeat_marker: tuple[int, int] | None = None) -> str:
    """Render a 2D grid of symbol names as a knit-chart SVG.

    ``rows`` is read top-to-bottom — i.e. ``rows[0]`` is the highest-numbered
    row. Row numbers are drawn on the right side of the chart following the
    knitting convention that row 1 is at the bottom.

    ``repeat_marker``, if given, is ``(start_col, end_col)`` of a horizontal
    pattern repeat (0-indexed, both inclusive) that gets bracketed with thin
    lines below the chart so the reader sees which columns repeat.

    Returns a complete ``<svg>...</svg>`` element with viewBox; safe to embed
    in HTML.
    """
    if not rows:
        raise ValueError("chart_grid: rows must not be empty")
    n_rows = len(rows)
    width = max(len(r) for r in rows)
    if width == 0:
        raise ValueError("chart_grid: rows must not be empty")
    # Validate every cell-name up-front so we fail fast on typos.
    for r in rows:
        for s in r:
            _normalise(s)

    pad_left = 6
    pad_right = 30  # space for row numbers
    pad_top = 6
    pad_bottom = 24  # space for column-numbers + repeat-marker

    grid_w = width * cell_size
    grid_h = n_rows * cell_size
    svg_w = pad_left + grid_w + pad_right
    svg_h = pad_top + grid_h + pad_bottom

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="chart-grid" '
        f'viewBox="0 0 {svg_w} {svg_h}" preserveAspectRatio="xMidYMid meet">',
        f'<g transform="translate({pad_left},{pad_top})">',
    ]

    # Cells.
    for r_idx, row in enumerate(rows):
        # row 1 sits at the bottom of the chart, but rows[0] is the topmost
        # visual row. Row number = n_rows - r_idx.
        for c_idx, name in enumerate(row):
            x = c_idx * cell_size
            y = r_idx * cell_size
            parts.append(symbol(name, x, y, cell_size))
        # Row number on the right side.
        row_number = n_rows - r_idx
        ry = r_idx * cell_size + cell_size / 2 + 4
        parts.append(
            f'<text x="{grid_w + 6}" y="{ry:.2f}" '
            f'font-size="{int(cell_size * 0.42)}" font-family="Inter, sans-serif" '
            f'fill="{STROKE}">{row_number}</text>'
        )

    # Outer frame (covers any line-art that bleeds onto the edge).
    parts.append(
        f'<rect x="0" y="0" width="{grid_w}" height="{grid_h}" '
        f'fill="none" stroke="{STROKE}" stroke-width="1.0"/>'
    )

    # Column numbers across the bottom (every column).
    for c_idx in range(width):
        cx = c_idx * cell_size + cell_size / 2
        cy = grid_h + 12
        parts.append(
            f'<text x="{cx:.2f}" y="{cy:.2f}" text-anchor="middle" '
            f'font-size="{int(cell_size * 0.36)}" font-family="Inter, sans-serif" '
            f'fill="{STROKE}">{width - c_idx}</text>'
        )

    # Repeat marker.
    if repeat_marker is not None:
        c0, c1 = repeat_marker
        if not (0 <= c0 <= c1 < width):
            raise ValueError(
                f"repeat_marker {repeat_marker} is outside [0,{width-1}]"
            )
        x0 = c0 * cell_size
        x1 = (c1 + 1) * cell_size
        y_bracket = grid_h + 18
        parts.append(
            f'<line x1="{x0:.2f}" y1="{y_bracket:.2f}" '
            f'x2="{x1:.2f}" y2="{y_bracket:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.8"/>'
            f'<line x1="{x0:.2f}" y1="{y_bracket - 3:.2f}" '
            f'x2="{x0:.2f}" y2="{y_bracket + 3:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.8"/>'
            f'<line x1="{x1:.2f}" y1="{y_bracket - 3:.2f}" '
            f'x2="{x1:.2f}" y2="{y_bracket + 3:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.8"/>'
        )

    parts.append("</g></svg>")
    return "".join(parts)


def used_symbols(rows: list[list[str]]) -> list[str]:
    """Return the canonical names of every symbol used in ``rows``, in
    chart-encounter order. Useful for building a legend."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for r in rows:
        for s in r:
            n = _normalise(s)
            if n not in seen_set:
                seen_set.add(n)
                seen.append(n)
    return seen


def colorwork_chart(rows: list[list[str]],
                    colors: dict[str, str],
                    cell_size: int = 24,
                    *,
                    caption: str = "",
                    repeat_marker_x: tuple[int, int] | None = None,
                    color_names: dict[str, str] | None = None) -> str:
    """Render a stranded colorwork chart as SVG.

    ``rows`` is a 2D array of color-keys (strings — typically ``"A"``,
    ``"B"``, …). It is read top-to-bottom, so ``rows[0]`` is the topmost
    visual row (highest row number).

    ``colors`` maps each key to a CSS-compatible fill colour (e.g.
    ``{"A": "#1a1a1a", "B": "#f5f1e6"}``). Every key used in ``rows`` must
    appear in ``colors``.

    Each cell is rendered as a single filled rectangle — no stitch glyph
    (a stranded colorwork chart is read by colour alone).

    Row numbers are drawn alternating sides: odd-numbered (RS) rows on
    the right, even-numbered (WS) rows on the left, following the typical
    Ravelry / Schoolhouse Press convention so the reader knows which side
    they're working from.

    A colour legend is drawn below the grid showing each colour with its
    key (or, if ``color_names`` is given, a friendlier label per key).

    ``repeat_marker_x = (start_col, end_col)`` (0-indexed, inclusive) draws
    a bracket below the chart marking the horizontal pattern repeat.

    ``caption`` is rendered above the legend if non-empty.
    """
    if not rows:
        raise ValueError("colorwork_chart: rows must not be empty")
    n_rows = len(rows)
    width = max(len(r) for r in rows)
    if width == 0:
        raise ValueError("colorwork_chart: rows must not be empty")
    if not isinstance(colors, dict) or not colors:
        raise ValueError("colorwork_chart: colors palette must be a non-empty dict")
    # Validate every cell key is in colors
    for r in rows:
        for k in r:
            if k not in colors:
                raise KeyError(
                    f"colorwork_chart: cell key {k!r} not in colors palette "
                    f"{sorted(colors.keys())}"
                )

    pad_left = 24   # space for even-row numbers
    pad_right = 24  # space for odd-row numbers
    pad_top = 6
    legend_height = 36
    caption_height = 18 if caption else 0
    bracket_height = 14 if repeat_marker_x is not None else 0
    pad_bottom = 18 + bracket_height + caption_height + legend_height

    grid_w = width * cell_size
    grid_h = n_rows * cell_size
    svg_w = pad_left + grid_w + pad_right
    svg_h = pad_top + grid_h + pad_bottom

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="colorwork-chart" '
        f'viewBox="0 0 {svg_w} {svg_h}" preserveAspectRatio="xMidYMid meet">',
        f'<g transform="translate({pad_left},{pad_top})">',
    ]

    # Cells.
    for r_idx, row in enumerate(rows):
        for c_idx, key in enumerate(row):
            x = c_idx * cell_size
            y = r_idx * cell_size
            fill = colors[key]
            parts.append(
                f'<rect class="cw-cell cw-{key}" '
                f'x="{x:.2f}" y="{y:.2f}" '
                f'width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="{STROKE}" stroke-width="0.4"/>'
            )
        # Row number — alternate sides
        row_number = n_rows - r_idx  # row 1 at bottom
        ry = r_idx * cell_size + cell_size / 2 + 4
        if row_number % 2 == 1:
            # Odd rows (RS) on the right
            parts.append(
                f'<text x="{grid_w + 6}" y="{ry:.2f}" '
                f'font-size="{int(cell_size * 0.42)}" font-family="Inter, sans-serif" '
                f'fill="{STROKE}">{row_number}</text>'
            )
        else:
            # Even rows (WS) on the left
            parts.append(
                f'<text x="-6" y="{ry:.2f}" text-anchor="end" '
                f'font-size="{int(cell_size * 0.42)}" font-family="Inter, sans-serif" '
                f'fill="{STROKE}">{row_number}</text>'
            )

    # Outer frame.
    parts.append(
        f'<rect x="0" y="0" width="{grid_w}" height="{grid_h}" '
        f'fill="none" stroke="{STROKE}" stroke-width="1.0"/>'
    )

    # Repeat marker.
    y_below = grid_h + 8
    if repeat_marker_x is not None:
        c0, c1 = repeat_marker_x
        if not (0 <= c0 <= c1 < width):
            raise ValueError(
                f"repeat_marker_x {repeat_marker_x} is outside [0,{width-1}]"
            )
        x0 = c0 * cell_size
        x1 = (c1 + 1) * cell_size
        y_bracket = y_below + 4
        parts.append(
            f'<g class="cw-repeat-bracket">'
            f'<line x1="{x0:.2f}" y1="{y_bracket:.2f}" '
            f'x2="{x1:.2f}" y2="{y_bracket:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.9"/>'
            f'<line x1="{x0:.2f}" y1="{y_bracket - 4:.2f}" '
            f'x2="{x0:.2f}" y2="{y_bracket + 4:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.9"/>'
            f'<line x1="{x1:.2f}" y1="{y_bracket - 4:.2f}" '
            f'x2="{x1:.2f}" y2="{y_bracket + 4:.2f}" '
            f'stroke="{STROKE}" stroke-width="0.9"/>'
            f'</g>'
        )
        y_below = y_bracket + 8

    # Caption (if provided).
    if caption:
        cap_y = y_below + 12
        parts.append(
            f'<text class="cw-caption" x="{grid_w / 2:.2f}" y="{cap_y:.2f}" '
            f'text-anchor="middle" font-size="{int(cell_size * 0.40)}" '
            f'font-family="Inter, sans-serif" fill="{STROKE}">'
            f'{caption}</text>'
        )
        y_below = cap_y + 6

    # Legend — one swatch per used colour, in chart-encounter order.
    seen: list[str] = []
    seen_set: set[str] = set()
    for r in rows:
        for k in r:
            if k not in seen_set:
                seen_set.add(k)
                seen.append(k)

    legend_y = y_below + 6
    sw_size = int(cell_size * 0.7)
    item_pad = 8
    item_x = 0.0
    for key in seen:
        label = (color_names or {}).get(key, key)
        # Swatch
        parts.append(
            f'<rect class="cw-legend-swatch" '
            f'x="{item_x:.2f}" y="{legend_y:.2f}" '
            f'width="{sw_size}" height="{sw_size}" '
            f'fill="{colors[key]}" stroke="{STROKE}" stroke-width="0.5"/>'
        )
        # Label
        text_x = item_x + sw_size + 4
        text_y = legend_y + sw_size * 0.75
        parts.append(
            f'<text class="cw-legend-label" '
            f'x="{text_x:.2f}" y="{text_y:.2f}" '
            f'font-size="{int(cell_size * 0.40)}" font-family="Inter, sans-serif" '
            f'fill="{STROKE}">{label}</text>'
        )
        # Advance — approximate label width ~ 8 px per char
        item_x = text_x + max(20.0, len(label) * 7.0) + item_pad

    parts.append("</g></svg>")
    return "".join(parts)


def legend_entries(rows: list[list[str]], lang: str = "da") -> list[tuple[str, str, str]]:
    """Build legend tuples for every symbol used in the chart.

    Returns a list of ``(symbol_name, label, sample_svg)``. The sample SVG is
    a single-cell rendering suitable for inline display (its viewBox is the
    same size as a chart cell, so CSS can size it freely).
    """
    cell = 24
    entries: list[tuple[str, str, str]] = []
    for name in used_symbols(rows):
        label = SYMBOL_LABELS[name][lang] if lang in SYMBOL_LABELS[name] \
            else SYMBOL_LABELS[name]["da"]
        sample = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'class="chart-legend-cell" viewBox="0 0 {cell} {cell}" '
            f'width="{cell}" height="{cell}">'
            f'{symbol(name, 0, 0, cell)}'
            f'</svg>'
        )
        entries.append((name, label, sample))
    return entries
