"""Stranded colorwork motif library.

Each motif is a small dict describing a horizontal repeat: a 2D string-grid
of colour-keys ('A', 'B', 'C', …), the explicit width / height, a name,
and a default colour palette for preview rendering.

Usage::

    from lib.visualisering.motifs import MOTIFS, get_motif
    motif = get_motif("stars")
    # motif["grid"] is list[list[str]], rows[0] is the topmost visual row
    # motif["default_colors"] is dict[key -> css colour]

The grid convention matches the rest of the chart system: ``rows[0]`` is
the topmost visual row, ``rows[-1]`` is the bottom row (knit first when
working bottom-up).

Motifs are intentionally small and stylised — they are placeholder
patterns, not faithful reproductions of historical Lopapeysa designs. Use
them as a starting point and override colours / motif-grid in your own
design.
"""

from __future__ import annotations
from copy import deepcopy

# ---------------------------------------------------------------------------
# Helper: parse a list of strings into a list[list[str]].
# ---------------------------------------------------------------------------

def _parse(rows: list[str]) -> list[list[str]]:
    """Turn ``["ABAB", "BABA"]`` into ``[["A","B","A","B"], ["B","A","B","A"]]``."""
    return [list(r) for r in rows]


# ---------------------------------------------------------------------------
# Motif: stars (8-wide, 5-high) — classic Icelandic-ish small star band.
# ---------------------------------------------------------------------------
_STARS_GRID = _parse([
    "AAABAAAB",
    "ABBBABBB",
    "BBABBBAB",
    "ABBBABBB",
    "AAABAAAB",
])

# ---------------------------------------------------------------------------
# Motif: diagonal (8-wide, 8-high) — repeating diagonal stripe.
# ---------------------------------------------------------------------------
_DIAGONAL_GRID = _parse([
    "ABBBBBBB",
    "BABBBBBB",
    "BBABBBBB",
    "BBBABBBB",
    "BBBBABBB",
    "BBBBBABB",
    "BBBBBBAB",
    "BBBBBBBA",
])

# ---------------------------------------------------------------------------
# Motif: simple_dots (4-wide, 4-high) — beginner-friendly tiny dots.
# ---------------------------------------------------------------------------
_SIMPLE_DOTS_GRID = _parse([
    "BBBB",
    "BABB",
    "BBBB",
    "BBBA",
])

# ---------------------------------------------------------------------------
# Motif: snowflake_band (12-wide, 9-high) — single classic snowflake.
# ---------------------------------------------------------------------------
_SNOWFLAKE_GRID = _parse([
    "BBBBBABBBBBB",
    "BABBBABBBABB",
    "BBABBABBABBB",
    "BBBAAAAABBBB",
    "BAAAAAAAAABB",
    "BBBAAAAABBBB",
    "BBABBABBABBB",
    "BABBBABBBABB",
    "BBBBBABBBBBB",
])

# ---------------------------------------------------------------------------
# Motif: icelandic_rose_band (16-wide, 11-high) — stylised rose / cross
# medallion in three colours (A = main, B = background, C = accent).
# ---------------------------------------------------------------------------
_ICELANDIC_ROSE_GRID = _parse([
    "BBBBBBBAABBBBBBB",
    "BBBBBBAAAABBBBBB",
    "BBBABAACCAABBABB",
    "BBAAAACCCCAAAABB",
    "BABACCCAACCCABAB",
    "AAAACCAAAACCAAAA",
    "BABACCCAACCCABAB",
    "BBAAAACCCCAAAABB",
    "BBBABAACCAABBABB",
    "BBBBBBAAAABBBBBB",
    "BBBBBBBAABBBBBBB",
])


# ---------------------------------------------------------------------------
# Public registry.
# ---------------------------------------------------------------------------

MOTIFS: dict[str, dict] = {
    "stars": {
        "name": "Stars (8-wide band)",
        "width": 8,
        "height": 5,
        "grid": _STARS_GRID,
        "default_colors": {"A": "#1f3a5f", "B": "#f5f1e6"},
    },
    "diagonal": {
        "name": "Diagonal stripe (8-wide)",
        "width": 8,
        "height": 8,
        "grid": _DIAGONAL_GRID,
        "default_colors": {"A": "#7a1f1f", "B": "#f5f1e6"},
    },
    "simple_dots": {
        "name": "Simple dots (4-wide)",
        "width": 4,
        "height": 4,
        "grid": _SIMPLE_DOTS_GRID,
        "default_colors": {"A": "#3b6e3b", "B": "#f5f1e6"},
    },
    "snowflake_band": {
        "name": "Snowflake band (12-wide)",
        "width": 12,
        "height": 9,
        "grid": _SNOWFLAKE_GRID,
        "default_colors": {"A": "#f5f1e6", "B": "#1f3a5f"},
    },
    "icelandic_rose_band": {
        "name": "Icelandic rose band (16-wide, 3-color)",
        "width": 16,
        "height": 11,
        "grid": _ICELANDIC_ROSE_GRID,
        "default_colors": {"A": "#7a1f1f", "B": "#f5f1e6", "C": "#1f3a5f"},
    },
}


def get_motif(name: str) -> dict:
    """Return a deep copy of the motif registered under ``name``.

    Returns a deep copy so callers can mutate the grid / colours without
    polluting the shared registry.
    """
    if name not in MOTIFS:
        raise KeyError(
            f"unknown motif {name!r}. Known: {', '.join(sorted(MOTIFS))}"
        )
    return deepcopy(MOTIFS[name])


def list_motifs() -> list[str]:
    """Return the list of registered motif names."""
    return sorted(MOTIFS.keys())


__all__ = ["MOTIFS", "get_motif", "list_motifs"]
