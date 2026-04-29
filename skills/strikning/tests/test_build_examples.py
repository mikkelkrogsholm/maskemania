"""Smoke tests for scripts/build_examples.py.

These live under skills/strikning/tests so the standard
``unittest discover`` from CI picks them up. The script lives at the
repo root and exercises both strik and hækl skills.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))


def _import_build_examples():
    if "build_examples" in sys.modules:
        return sys.modules["build_examples"]
    spec = importlib.util.spec_from_file_location(
        "build_examples", _REPO / "scripts" / "build_examples.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_examples"] = mod
    spec.loader.exec_module(mod)
    return mod


class BuildExamplesTests(unittest.TestCase):

    def test_build_produces_index_and_examples(self):
        mod = _import_build_examples()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "_site"
            report = mod.build(out, quiet=True)
            self.assertGreaterEqual(report["count"], 8)
            self.assertTrue((out / "index.html").exists())
            self.assertTrue((out / "examples").is_dir())
            # At least 8 example HTML files (5 strik + 5 hækl ≈ 10).
            html_files = list((out / "examples").glob("*.html"))
            self.assertGreaterEqual(len(html_files), 8)
            # Assets copied over.
            self.assertTrue((out / "assets" / "style.css").exists())

    def test_index_html_contains_examples(self):
        mod = _import_build_examples()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "_site"
            mod.build(out, quiet=True)
            index = (out / "index.html").read_text(encoding="utf-8")
            # Catalogue page lists both domains.
            self.assertIn("Strik", index)
            self.assertIn("Hækl", index)
            # Cards link into examples/.
            self.assertIn('href="examples/strik-hue.html"', index)
            self.assertIn('href="examples/haekl-amigurumi.html"', index)

    def test_example_pages_have_pattern_content(self):
        mod = _import_build_examples()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "_site"
            mod.build(out, quiet=True)
            page = (out / "examples" / "strik-hue.html").read_text(
                encoding="utf-8")
            self.assertIn("<html", page.lower())
            # Pattern content rendered (cover or pattern title).
            self.assertIn("Hue", page)


if __name__ == "__main__":
    unittest.main()
