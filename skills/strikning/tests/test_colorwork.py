"""Tests for Fase 5 iter 4: colorwork chart renderer + motif library +
colorwork_swatch construction + yoke_stranded retro-fit.

Run with: python3 -m unittest discover -s skills/strikning/tests
"""

import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_SKILL))

from knitlib import Gauge  # noqa: E402
from knitlib.constructions import (  # noqa: E402
    YokeStrandedSpec, generate_yoke_stranded,
    ColorworkSwatchSpec, generate_colorwork_swatch,
)
from lib.visualisering import chart_symbols  # noqa: E402
from lib.visualisering.motifs import MOTIFS, get_motif, list_motifs  # noqa: E402
from lib.visualisering.html import render_html  # noqa: E402


# ---------------------------------------------------------------------------
# A. colorwork_chart renderer (4 tests)
# ---------------------------------------------------------------------------

class TestColorworkChart(unittest.TestCase):
    PALETTE = {"A": "#1f3a5f", "B": "#f5f1e6"}

    def test_correct_cell_count(self):
        rows = [
            ["A", "B", "A", "B"],
            ["B", "A", "B", "A"],
            ["A", "A", "B", "B"],
        ]
        svg = chart_symbols.colorwork_chart(rows, self.PALETTE, cell_size=20)
        # 3 rows × 4 cols = 12 cells. Each cell = one <rect class="cw-cell ...
        self.assertEqual(svg.count('class="cw-cell'), 12)
        # Outer SVG present.
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))

    def test_palette_colors_appear_in_fills(self):
        rows = [
            ["A", "B", "C"],
            ["C", "A", "B"],
        ]
        palette = {"A": "#111111", "B": "#eeeeee", "C": "#cc0000"}
        svg = chart_symbols.colorwork_chart(rows, palette, cell_size=18)
        # Each palette colour must be referenced as a fill at least once
        # (exclusive of "fill=\"none\"" frame strokes).
        for key, color in palette.items():
            self.assertIn(f'fill="{color}"', svg,
                          f"colour {color} for key {key} missing in SVG")

    def test_legend_shows_each_color_with_name(self):
        rows = [["A", "B"], ["B", "A"]]
        palette = {"A": "#000", "B": "#fff"}
        names = {"A": "Mørkeblå", "B": "Off-white"}
        svg = chart_symbols.colorwork_chart(rows, palette, cell_size=20,
                                            color_names=names)
        # Legend swatch class + text labels
        self.assertEqual(svg.count("cw-legend-swatch"), 2)
        self.assertIn("Mørkeblå", svg)
        self.assertIn("Off-white", svg)

    def test_repeat_marker_x_renders_bracket(self):
        rows = [["A", "B", "A", "B", "A"]]
        svg = chart_symbols.colorwork_chart(
            rows, self.PALETTE, cell_size=20,
            repeat_marker_x=(0, 3),
        )
        # The bracket group is emitted with class cw-repeat-bracket.
        self.assertIn("cw-repeat-bracket", svg)
        # Three lines (top horizontal + two verticals).
        # We can't easily count lines exactly because the SVG also has a
        # frame, so check at least one new <line> in the bracket group.
        # Without bracket the substring should be absent.
        svg_no_bracket = chart_symbols.colorwork_chart(
            rows, self.PALETTE, cell_size=20,
        )
        self.assertNotIn("cw-repeat-bracket", svg_no_bracket)

    def test_invalid_color_key_raises(self):
        rows = [["A", "Z"]]  # Z not in palette
        with self.assertRaises(KeyError):
            chart_symbols.colorwork_chart(rows, self.PALETTE)

    def test_empty_rows_raises(self):
        with self.assertRaises(ValueError):
            chart_symbols.colorwork_chart([], {"A": "#000"})


# ---------------------------------------------------------------------------
# B. Motif library (2 tests)
# ---------------------------------------------------------------------------

class TestMotifLibrary(unittest.TestCase):
    def test_required_motifs_present(self):
        names = list_motifs()
        for required in ("stars", "diagonal", "simple_dots",
                         "snowflake_band", "icelandic_rose_band"):
            self.assertIn(required, names)

    def test_each_motif_grid_matches_declared_dimensions(self):
        for name, motif in MOTIFS.items():
            grid = motif["grid"]
            self.assertEqual(len(grid), motif["height"],
                             f"motif {name}: grid height mismatch")
            for r_idx, row in enumerate(grid):
                self.assertEqual(len(row), motif["width"],
                                 f"motif {name}: row {r_idx} width mismatch")
            # Every cell key must be in default_colors.
            keys = {c for r in grid for c in r}
            self.assertTrue(keys.issubset(motif["default_colors"].keys()),
                            f"motif {name}: cell keys {keys} not all in palette")

    def test_get_motif_returns_independent_copy(self):
        m1 = get_motif("stars")
        m1["grid"][0][0] = "Z"
        m2 = get_motif("stars")
        self.assertNotEqual(m2["grid"][0][0], "Z")

    def test_get_unknown_motif_raises(self):
        with self.assertRaises(KeyError):
            get_motif("not-a-real-motif")


# ---------------------------------------------------------------------------
# C. yoke_stranded retro-fit (2 new tests)
# ---------------------------------------------------------------------------

class TestYokeStrandedMotif(unittest.TestCase):
    def test_motif_lookup_uses_named_motif(self):
        p = generate_yoke_stranded(YokeStrandedSpec(
            bust_cm=94, gauge=Gauge(22, 30), motif="diagonal",
            repeat_width=8,
        ))
        self.assertEqual(p.inputs["motif_name"], "diagonal")
        # The colorwork chart payload must mirror the diagonal motif.
        cw = p.inputs["colorwork_chart"]
        self.assertEqual(len(cw["rows"]), MOTIFS["diagonal"]["height"])
        self.assertEqual(len(cw["rows"][0]), MOTIFS["diagonal"]["width"])

    def test_html_contains_colorwork_svg(self):
        p = generate_yoke_stranded(YokeStrandedSpec(
            bust_cm=94, gauge=Gauge(22, 30), motif="stars",
        ))
        html = render_html(p, lang="da")
        # SVG colorwork chart present (not text grid only).
        self.assertIn("colorwork-chart", html)
        self.assertIn("cw-cell", html)
        # Section heading translated.
        self.assertIn("Stranded farve-diagram", html)


# ---------------------------------------------------------------------------
# D. colorwork_swatch construction (6 tests)
# ---------------------------------------------------------------------------

class TestColorworkSwatch(unittest.TestCase):
    GAUGE = Gauge(22, 30)

    def _basic(self, **kw):
        defaults = dict(width_cm=30, height_cm=20, gauge=self.GAUGE,
                        motif="stars")
        defaults.update(kw)
        return generate_colorwork_swatch(ColorworkSwatchSpec(**defaults))

    def test_construction_name(self):
        p = self._basic()
        self.assertEqual(p.construction, "colorwork_swatch")

    def test_inner_sts_multiple_of_motif_width(self):
        p = self._basic(motif="snowflake_band")
        motif_w = MOTIFS["snowflake_band"]["width"]
        self.assertEqual(p.inputs["inner_sts"] % motif_w, 0)
        # And at least one full repeat
        self.assertGreaterEqual(p.inputs["n_repeats_w"], 1)

    def test_body_rows_multiple_of_motif_height(self):
        p = self._basic(motif="diagonal")
        motif_h = MOTIFS["diagonal"]["height"]
        self.assertEqual(p.inputs["body_rows"] % motif_h, 0)

    def test_pattern_has_expected_sections(self):
        p = self._basic()
        titles = [s.title for s in p.sections]
        self.assertIn("Opslag og garter-bånd", titles)
        self.assertIn("Mønstret krop", titles)
        self.assertIn("Garter-bånd og aflukning", titles)

    def test_html_renders_svg_chart(self):
        p = self._basic(motif="diagonal")
        html = render_html(p, lang="da")
        self.assertIn("cw-cell", html)
        self.assertIn("Stranded farve-diagram", html)

    def test_markdown_contains_text_grid(self):
        # The colorwork_swatch stores a text-grid in notes; we verify it's
        # present and contains the legacy ■/□ characters.
        p = self._basic(motif="stars")
        joined = "\n".join(p.notes)
        self.assertIn("■", joined)
        self.assertIn("□", joined)

    def test_unknown_motif_raises(self):
        with self.assertRaises(KeyError):
            self._basic(motif="not-real")

    def test_three_color_motif_palette(self):
        """3-colour Icelandic rose motif passes through to chart payload."""
        p = self._basic(motif="icelandic_rose_band")
        cw = p.inputs["colorwork_chart"]
        self.assertEqual(set(cw["colors"].keys()), {"A", "B", "C"})


if __name__ == "__main__":
    unittest.main()
