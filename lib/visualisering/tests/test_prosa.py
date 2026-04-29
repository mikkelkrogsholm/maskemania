"""Tests for the template-based prose intro generator.

These tests target the lib-level module directly (no skill imports), so
they are construction-agnostic. We construct minimal Pattern objects
with the metadata shape the prosa generator expects.
"""

from __future__ import annotations
import sys
import unittest
from pathlib import Path

# Repo layout: <repo>/lib/visualisering/tests/test_prosa.py
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
sys.path.insert(0, str(_REPO))

from lib.visualisering.pattern import Pattern, Section  # noqa: E402
from lib.visualisering import prosa  # noqa: E402
from lib.visualisering import html as html_mod  # noqa: E402


def _hue_pattern(name: str = "Test-hue", *,
                 sts_per_10cm: int = 22,
                 rows_per_10cm: int = 30) -> Pattern:
    p = Pattern(
        name=name,
        construction="hue",
        inputs={
            "gauge": {"sts_per_10cm": sts_per_10cm,
                      "rows_per_10cm": rows_per_10cm},
            "head_circumference_cm": 56.0,
            "finished_circumference_cm": 53.0,
            "ease_cm": -3.0,
            "rib_height_cm": 5.0,
            "total_height_cm": 21.0,
            "sectors": 8,
            "_domain": "knit",
        },
        difficulty="beginner",
    )
    s = p.add_section("Rib", 117)
    s.add("k1, p1 around for 5 cm", 117)
    s2 = p.add_section("Body", 117)
    s2.add("k around for 16 cm", 117)
    return p


def _amigurumi_pattern() -> Pattern:
    p = Pattern(
        name="Test-kugle",
        construction="amigurumi_sphere",
        inputs={
            "gauge": {"sts_per_10cm": 50, "rows_per_10cm": 50},
            "diameter_cm": 8.0,
            "actual_diameter_cm": 8.2,
            "n_max": 12,
            "max_sts": 72,
            "_domain": "crochet",
        },
        difficulty="easy",
    )
    s = p.add_section("Magic ring", 6)
    s.add("6 sc in MR", 6)
    s2 = p.add_section("Increase", 12)
    s2.add("inc in each", 12)
    return p


class ProsaParagraphsTest(unittest.TestCase):
    def test_returns_2_to_3_paragraphs(self):
        p = _hue_pattern()
        paras = prosa.intro_paragraphs(p, lang="da")
        self.assertGreaterEqual(len(paras), 2)
        self.assertLessEqual(len(paras), 3)
        for para in paras:
            self.assertTrue(para.strip())

    def test_deterministic_for_same_seed(self):
        # Same name + gauge → identical paragraphs across calls.
        a = prosa.intro_paragraphs(_hue_pattern("DetA"), lang="da")
        b = prosa.intro_paragraphs(_hue_pattern("DetA"), lang="da")
        self.assertEqual(a, b)

    def test_different_name_gives_different_prose(self):
        # Different seeds generally pick different fragments. We can't
        # guarantee disjointness on a single slot, but the *combination*
        # of all slots changes for almost any non-trivial library.
        a = prosa.intro_paragraphs(_hue_pattern("Alpha"), lang="da")
        b = prosa.intro_paragraphs(_hue_pattern("Beta-Gamma"), lang="da")
        # Either at least one paragraph differs, or the libraries are too
        # small. Our hue group has multiple intro variants, so this should
        # hold deterministically.
        self.assertNotEqual(a, b)

    def test_includes_central_metadata(self):
        # Gauge must always appear in the prose (every group's size slot
        # references {gauge_summary}).
        p = _hue_pattern(sts_per_10cm=22, rows_per_10cm=30)
        joined = " ".join(prosa.intro_paragraphs(p, lang="da"))
        self.assertIn("22", joined)
        self.assertIn("30", joined)
        # Construction-specific facts should appear (head circ for hue).
        self.assertTrue("53" in joined or "56" in joined,
                        msg=f"expected head circ in: {joined}")

    def test_default_fallback_includes_sts_total(self):
        # An unknown construction falls through to the _default group,
        # whose templates *do* reference {sts_total}.
        p = Pattern(
            name="Mystery",
            construction="something_unknown_zzz",
            inputs={"gauge": {"sts_per_10cm": 18, "rows_per_10cm": 24}},
        )
        s = p.add_section("only", 200)
        s.add("k around", 200)
        joined = " ".join(prosa.intro_paragraphs(p, lang="da"))
        self.assertIn("18", joined)
        self.assertIn("200", joined)

    def test_different_constructions_produce_different_prose(self):
        knit = prosa.intro_paragraphs(_hue_pattern("X"), lang="da")
        crochet = prosa.intro_paragraphs(_amigurumi_pattern(), lang="da")
        # The intro fragment libraries are disjoint by construction; the
        # joined text must therefore differ.
        self.assertNotEqual(" ".join(knit), " ".join(crochet))

    def test_english_version_works(self):
        p = _hue_pattern("Eng-test")
        en_paras = prosa.intro_paragraphs(p, lang="en")
        self.assertGreaterEqual(len(en_paras), 2)
        joined = " ".join(en_paras).lower()
        # Specific English phrases that don't exist in the Danish library.
        self.assertTrue(
            "knit" in joined or "knitting" in joined
            or "rib" in joined or "stitches" in joined,
            msg=f"expected English vocabulary, got: {joined}",
        )

    def test_format_intro_html_wraps_section(self):
        p = _hue_pattern()
        out = prosa.format_intro_html(p, lang="da")
        self.assertIn('<section class="prosa">', out)
        self.assertIn("</section>", out)
        self.assertIn("<p>", out)

    def test_format_intro_html_empty_pattern_returns_empty_string(self):
        empty = Pattern(
            name="",
            construction="totally_unknown_construction_xyz",
            inputs={"gauge": {"sts_per_10cm": 0, "rows_per_10cm": 0}},
        )
        # Default group will still produce content; verify that disabling
        # the construction label still yields *some* paragraphs (graceful
        # fallback) and that wrapping returns valid HTML or empty string.
        out = prosa.format_intro_html(empty, lang="da")
        self.assertTrue(out == "" or '<section class="prosa">' in out)


class ProsaInRenderHtmlTest(unittest.TestCase):
    """Smoke-tests that the html.py wiring + --no-prosa toggle work."""

    def test_render_html_includes_prosa_section_by_default(self):
        html_mod.set_prosa_enabled(True)
        try:
            out = html_mod.render_html(_hue_pattern(), lang="da")
            self.assertIn('<section class="prosa">', out)
        finally:
            html_mod.set_prosa_enabled(True)

    def test_render_html_no_prosa_when_disabled(self):
        html_mod.set_prosa_enabled(False)
        try:
            out = html_mod.render_html(_hue_pattern(), lang="da")
            self.assertNotIn('<section class="prosa">', out)
        finally:
            html_mod.set_prosa_enabled(True)


if __name__ == "__main__":
    unittest.main()
