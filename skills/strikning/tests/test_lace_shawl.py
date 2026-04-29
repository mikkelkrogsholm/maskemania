"""Tests for Fase 5 iter 3: lace_shawl construction + SVG chart symbols.

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
    LaceShawlSpec, generate_lace_shawl, LACE_REPEATS, LaceRepeat,
    validate_repeat_balance,
)
from lib.visualisering import chart_symbols  # noqa: E402
from lib.visualisering.html import render_html, render_chart_figure  # noqa: E402


# ---------------------------------------------------------------------------
# Chart-symbol tests (3)
# ---------------------------------------------------------------------------

class TestChartSymbols(unittest.TestCase):
    def test_each_symbol_is_unique(self):
        """Every supported symbol must produce a *different* SVG snippet so
        they are visually distinguishable on the chart."""
        snippets = {}
        for name in chart_symbols.SUPPORTED_SYMBOLS:
            snippet = chart_symbols.symbol(name, 0, 0, 24)
            self.assertIn(f"cs-{name}", snippet,
                          f"symbol {name} missing CSS class")
            self.assertNotIn(snippet, snippets.values(),
                             f"symbol {name} produced a duplicate SVG")
            snippets[name] = snippet
        # Also confirm CSS-class ids look different so CSS targeting works.
        self.assertEqual(len(set(snippets.values())),
                         len(chart_symbols.SUPPORTED_SYMBOLS))

    def test_chart_grid_dimensions_and_row_numbers(self):
        rows = [
            ["knit", "yo", "knit"],
            ["k2tog", "knit", "ssk"],
        ]
        svg = chart_symbols.chart_grid(rows, cell_size=20)
        # viewBox must reflect 3 cols × 2 rows × 20px + paddings.
        self.assertIn('class="chart-grid"', svg)
        # Row numbers: row 1 at the bottom (so the LAST visual row gets "1").
        self.assertIn(">1<", svg)  # row 1 number
        self.assertIn(">2<", svg)  # row 2 number
        # Cells: 3 cols × 2 rows = 6 symbol groups.
        self.assertEqual(svg.count("<g class=\"cs"), 6)
        # Empty rows must raise.
        with self.assertRaises(ValueError):
            chart_symbols.chart_grid([], cell_size=20)

    def test_legend_includes_only_used_symbols(self):
        rows = [
            ["knit", "yo", "k2tog"],
            ["knit", "knit", "knit"],
        ]
        used = chart_symbols.used_symbols(rows)
        self.assertEqual(set(used), {"knit", "yo", "k2tog"})
        legend = chart_symbols.legend_entries(rows, lang="da")
        self.assertEqual(len(legend), 3)
        names = [name for name, _label, _svg in legend]
        # 'knit' is encountered first, then 'yo', then 'k2tog'.
        self.assertEqual(names[0], "knit")
        # Each entry's sample-svg must be a valid <svg>...</svg> string.
        for _name, label, sample in legend:
            self.assertTrue(label)
            self.assertTrue(sample.startswith("<svg"))
            self.assertTrue(sample.endswith("</svg>"))
        # English legend must produce different labels for at least some rows.
        legend_en = chart_symbols.legend_entries(rows, lang="en")
        self.assertNotEqual([l for _, l, _ in legend],
                            [l for _, l, _ in legend_en])


# ---------------------------------------------------------------------------
# Lace shawl tests (5)
# ---------------------------------------------------------------------------

class TestLaceShawl(unittest.TestCase):
    GAUGE = Gauge(22, 30)

    def test_repeat_validate_balanced(self):
        # The bundled feather-and-fan repeat must pass validation.
        validate_repeat_balance(LACE_REPEATS["feather_and_fan"])

    def test_unbalanced_repeat_raises(self):
        bad = LaceRepeat(
            name="bad",
            rows=[["knit", "yo", "knit"]],   # adds 1 stitch — illegal
            repeat_sts=3, repeat_rows=1,
        )
        with self.assertRaises(ValueError):
            validate_repeat_balance(bad)

    def test_dimensions_and_repeat_fit(self):
        p = generate_lace_shawl(LaceShawlSpec(
            width_cm=60, length_cm=180, gauge=self.GAUGE,
        ))
        # cast_on must = inner_sts + 2*edge_sts; inner divisible by 18.
        cast_on = p.inputs["cast_on"]
        inner = p.inputs["inner_sts"]
        edge = p.inputs["edge_sts"]
        repeat_sts = p.inputs["repeat_sts"]
        self.assertEqual(cast_on, inner + 2 * edge)
        self.assertEqual(inner % repeat_sts, 0)
        self.assertGreaterEqual(p.inputs["n_lace_repeats_width"], 1)
        # Every section ends with the same stitch count (lace is balanced).
        for sec in p.sections:
            self.assertEqual(sec.sts_after, cast_on)
        # Body rows are a multiple of repeat_rows.
        self.assertEqual(p.inputs["body_rows"] % p.inputs["repeat_rows"], 0)

    def test_too_narrow_raises(self):
        # Width too narrow for one full 18-st repeat + edges → ValueError.
        with self.assertRaises(ValueError):
            generate_lace_shawl(LaceShawlSpec(
                width_cm=5, length_cm=80, gauge=self.GAUGE,
            ))

    def test_chart_payload_and_html_embeds_chart(self):
        p = generate_lace_shawl(LaceShawlSpec(
            width_cm=60, length_cm=180, gauge=self.GAUGE,
        ))
        chart = p.inputs.get("lace_chart")
        self.assertIsNotNone(chart)
        self.assertEqual(len(chart["rows"]), 4)
        self.assertEqual(len(chart["rows"][0]), 18)
        # HTML output includes chart-grid + chart-legend.
        out = render_html(p)
        self.assertIn("chart-grid", out)
        self.assertIn("chart-legend", out)
        self.assertIn("<svg", out)

    def test_unknown_repeat_raises(self):
        with self.assertRaises(ValueError):
            generate_lace_shawl(LaceShawlSpec(
                width_cm=60, length_cm=180, gauge=self.GAUGE,
                repeat="not_a_real_repeat",
            ))


if __name__ == "__main__":
    unittest.main()
