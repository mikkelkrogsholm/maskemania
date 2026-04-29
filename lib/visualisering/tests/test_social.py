"""Tests for the social-media preview generator.

We avoid invoking Chrome — the templating + format-resolution + fallback
behaviour is what we want to lock down. The Chrome-launch path is
exercised manually via the CLI when a developer has Chrome installed.
"""

from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
sys.path.insert(0, str(_REPO))

from lib.visualisering.pattern import Pattern  # noqa: E402
from lib.visualisering import social  # noqa: E402
from lib.visualisering.pdf import ChromeNotFoundError  # noqa: E402


def _hue_pattern() -> Pattern:
    p = Pattern(
        name="Test-hue",
        construction="hue",
        inputs={
            "gauge": {"sts_per_10cm": 22, "rows_per_10cm": 30},
            "head_circumference_cm": 56.0,
            "finished_circumference_cm": 53.0,
            "ease_cm": -3.0,
            "rib_height_cm": 5.0,
            "total_height_cm": 21.0,
            "sectors": 8,
            "_domain": "knit",
            "metadata": {
                "yarn": "Drops Alpaca",
                "designer": "Test Designer",
            },
        },
        difficulty="easy",
    )
    s = p.add_section("Rib", 117)
    s.add("k1, p1 around", 117)
    return p


class SocialTemplatingTest(unittest.TestCase):
    def test_build_html_contains_core_fields(self):
        html = social.build_social_html(_hue_pattern(), format="square",
                                        lang="da")
        self.assertIn("Test-hue", html)
        # Construction subtitle (translated).
        self.assertIn("Hue", html)
        # Yarn badge populated when metadata.yarn is set.
        self.assertIn("Drops Alpaca", html)
        # Difficulty value.
        self.assertIn("Let øvet", html)
        # Format css class.
        self.assertIn('class="format-square"', html)

    def test_format_aliases_resolve(self):
        # Each of these aliases must produce HTML without raising.
        for fmt in ("square", "1:1", "1x1", "story", "9:16"):
            html = social.build_social_html(_hue_pattern(), format=fmt,
                                            lang="da")
            self.assertTrue(html.strip().startswith("<!DOCTYPE html>"),
                            msg=f"format {fmt!r} produced bogus HTML")

    def test_format_dimensions_mapping(self):
        self.assertEqual(social.format_dimensions("square"), (1080, 1080))
        self.assertEqual(social.format_dimensions("1:1"), (1080, 1080))
        self.assertEqual(social.format_dimensions("story"), (1080, 1920))
        self.assertEqual(social.format_dimensions("9:16"), (1080, 1920))

    def test_unknown_format_raises(self):
        with self.assertRaises(ValueError):
            social.build_social_html(_hue_pattern(), format="banana")

    def test_english_renders_without_danish_strings(self):
        html = social.build_social_html(_hue_pattern(), format="square",
                                        lang="en")
        # English construction label.
        self.assertIn("Hat", html)
        # English difficulty label.
        self.assertIn("Easy", html)


class SocialChromeFallbackTest(unittest.TestCase):
    def test_falls_back_to_html_when_chrome_missing(self):
        """When find_chrome() raises, the standalone HTML is still written
        and ChromeNotFoundError is propagated for the CLI to catch."""
        with tempfile.TemporaryDirectory() as tdir:
            out = Path(tdir) / "card.png"
            with mock.patch.object(social, "find_chrome",
                                    side_effect=ChromeNotFoundError(
                                        "no chrome here")):
                with self.assertRaises(ChromeNotFoundError):
                    social.generate_social_preview(
                        _hue_pattern(), format="square", output_path=out)
            # HTML fallback must exist next to the requested PNG path.
            html_fallback = out.with_suffix(".html")
            self.assertTrue(html_fallback.exists(),
                            msg="HTML fallback should be written before "
                                "raising ChromeNotFoundError")
            content = html_fallback.read_text(encoding="utf-8")
            self.assertIn("Test-hue", content)

    def test_output_path_is_resolved_absolute(self):
        with tempfile.TemporaryDirectory() as tdir:
            out = Path(tdir) / "sub" / "card.png"
            with mock.patch.object(social, "find_chrome",
                                    side_effect=ChromeNotFoundError("nope")):
                try:
                    social.generate_social_preview(
                        _hue_pattern(), format="story", output_path=out)
                except ChromeNotFoundError:
                    pass
            # Even with subdirectory, the parent dir is created.
            self.assertTrue(out.parent.exists())
            self.assertTrue(out.with_suffix(".html").exists())


if __name__ == "__main__":
    unittest.main()
