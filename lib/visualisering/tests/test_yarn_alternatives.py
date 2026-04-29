"""Tests for yarn_alternatives + --substitut CLI flag (Fase 5 iter 5)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "skills" / "strikning"))
sys.path.insert(0, str(_REPO / "skills" / "hækling"))


class YarnAlternativesTests(unittest.TestCase):

    def test_known_yarn_produces_alternatives(self):
        from lib.visualisering import yarn_alternatives as ya
        alts = ya.build_alternatives("Drops Air", lang="da", domain="knit")
        self.assertGreaterEqual(len(alts), 3)
        self.assertLessEqual(len(alts), 5)

    def test_alternatives_share_weight_class(self):
        from lib.visualisering import yarn_alternatives as ya
        from lib.visualisering.yarn_db import lookup_yarn
        base = lookup_yarn("Drops Air")
        self.assertIsNotNone(base)
        alts = ya.build_alternatives("Drops Air", lang="da")
        self.assertTrue(alts)
        for a in alts:
            self.assertEqual(a.weight_class, base.weight_class)

    def test_gauge_diff_hint_set_when_gauges_differ(self):
        from lib.visualisering import yarn_alternatives as ya
        alts = ya.build_alternatives("Drops Air", lang="da")
        # At least one alternative in a populated weight class will have a
        # non-zero gauge difference and produce a needle suggestion hint.
        differing = [a for a in alts if abs(a.gauge_diff_pct) >= 1.0]
        self.assertTrue(differing,
                        f"expected at least one alt with gauge diff: {alts}")
        for a in differing:
            self.assertIn("mm", a.hint)

    def test_unknown_yarn_returns_empty_list_no_crash(self):
        from lib.visualisering import yarn_alternatives as ya
        alts = ya.build_alternatives("Helt Ukendt Garn 12345", lang="da")
        self.assertEqual(alts, [])

    def test_attach_alternatives_writes_to_pattern_inputs(self):
        from lib.visualisering import yarn_alternatives as ya
        from knitlib import Gauge
        from knitlib.constructions import HueSpec, generate_hue
        p = generate_hue(HueSpec(head_circumference_cm=56, gauge=Gauge(22, 30)))
        n = ya.attach_alternatives(p, "Drops Air", lang="da", domain="knit")
        self.assertGreater(n, 0)
        self.assertIn("yarn_alternatives", p.inputs)
        self.assertEqual(len(p.inputs["yarn_alternatives"]), n)
        self.assertEqual(p.inputs["yarn_alternatives_base"], "Drops Air")

    def test_html_aside_present_when_alternatives_attached(self):
        from lib.visualisering import yarn_alternatives as ya
        from knitlib import Gauge
        from knitlib.constructions import HueSpec, generate_hue
        from lib.visualisering.html import render_html
        p = generate_hue(HueSpec(head_circumference_cm=56, gauge=Gauge(22, 30)))
        ya.attach_alternatives(p, "Drops Air", lang="da", domain="knit")
        html = render_html(p)
        self.assertIn("<aside class=\"yarn-alternatives\">", html)
        self.assertIn("Garn-alternativer", html)

    def test_html_aside_absent_when_no_alternatives(self):
        from knitlib import Gauge
        from knitlib.constructions import HueSpec, generate_hue
        from lib.visualisering.html import render_html
        p = generate_hue(HueSpec(head_circumference_cm=56, gauge=Gauge(22, 30)))
        html = render_html(p)
        # The aside element must not be emitted (CSS rules are still in the
        # stylesheet, so we look for the actual <aside> element).
        self.assertNotIn("<aside class=\"yarn-alternatives\">", html)
        self.assertNotIn("Garn-alternativer", html)

    def test_english_translation(self):
        from lib.visualisering import yarn_alternatives as ya
        from knitlib import Gauge
        from knitlib.constructions import HueSpec, generate_hue
        from lib.visualisering.html import render_html
        p = generate_hue(HueSpec(head_circumference_cm=56, gauge=Gauge(22, 30)))
        ya.attach_alternatives(p, "Drops Air", lang="en", domain="knit")
        html = render_html(p, lang="en")
        self.assertIn("Yarn alternatives", html)


if __name__ == "__main__":
    unittest.main()
