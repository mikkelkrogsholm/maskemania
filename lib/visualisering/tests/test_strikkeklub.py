"""Tests for scripts/strikkeklub.py — Fase 5 iter 5."""

from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
sys.path.insert(0, str(_REPO))


def _import_strikkeklub():
    if "strikkeklub" in sys.modules:
        return sys.modules["strikkeklub"]
    spec = importlib.util.spec_from_file_location(
        "strikkeklub", _REPO / "scripts" / "strikkeklub.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["strikkeklub"] = mod
    spec.loader.exec_module(mod)
    return mod


class StrikkeklubTests(unittest.TestCase):

    def setUp(self) -> None:
        self.sk = _import_strikkeklub()
        self.tmp = Path(tempfile.mkdtemp(prefix="klub-test-"))

    def _write_csv(self, rows: list[dict], filename: str = "members.csv") -> Path:
        # Collect a stable column order so DictWriter doesn't crash.
        cols: list[str] = []
        for r in rows:
            for k in r.keys():
                if k not in cols:
                    cols.append(k)
        path = self.tmp / filename
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        return path

    def test_supported_constructions_includes_basics(self):
        self.assertIn("hue", self.sk.supported_constructions())
        self.assertIn("granny", self.sk.supported_constructions())
        self.assertIn("amigurumi", self.sk.supported_constructions())

    def test_csv_with_three_rows_produces_three_files(self):
        csv_path = self._write_csv([
            {"name": "A", "construction": "hue",
             "sts": 22, "rows": 30, "head_cm": 56},
            {"name": "B", "construction": "tørklæde",
             "sts": 22, "rows": 30, "width_cm": 30, "length_cm": 150},
            {"name": "C", "construction": "amigurumi",
             "diameter_cm": 8, "gauge": 5},
        ])
        out = self.tmp / "out"
        report = self.sk.run_batch(csv_path, out, lang="da", make_zip=False)
        self.assertEqual(report["ok"], 3)
        self.assertEqual(report["failed"], 0)
        # 3 HTML files + index + paged polyfill copied
        htmls = list(out.glob("*.html"))
        self.assertEqual(len(htmls), 4)  # 3 patterns + index.html
        self.assertTrue((out / "index.html").exists())
        self.assertTrue((out / "paged.polyfill.js").exists())

    def test_failed_row_is_skipped_and_reported(self):
        csv_path = self._write_csv([
            {"name": "Good", "construction": "hue",
             "sts": 22, "rows": 30, "head_cm": 56},
            {"name": "BadConstruction", "construction": "ufo",
             "sts": 22, "rows": 30},
            {"name": "MissingHead", "construction": "hue",
             "sts": 22, "rows": 30},  # head_cm missing → required
        ])
        out = self.tmp / "out"
        report = self.sk.run_batch(csv_path, out, make_zip=False)
        self.assertEqual(report["ok"], 1)
        self.assertEqual(report["failed"], 2)
        # The failed row should NOT have produced an HTML file
        names = {f.name for f in out.glob("*.html")}
        self.assertIn("index.html", names)
        good = [r for r in report["results"] if r.ok]
        self.assertEqual(len(good), 1)
        self.assertEqual(good[0].name, "Good")
        # The failed rows must carry an error message, not a filename
        for r in report["results"]:
            if not r.ok:
                self.assertIsNone(r.filename)
                self.assertIsNotNone(r.error)

    def test_zip_is_valid_and_contains_index(self):
        csv_path = self._write_csv([
            {"name": "A", "construction": "hue",
             "sts": 22, "rows": 30, "head_cm": 56},
            {"name": "B", "construction": "granny", "rounds": 4},
        ])
        out = self.tmp / "klub_z"
        report = self.sk.run_batch(csv_path, out, make_zip=True)
        self.assertIsNotNone(report["zip"])
        zp = Path(report["zip"])
        self.assertTrue(zp.exists())
        # Must be a valid zip
        with zipfile.ZipFile(zp) as zf:
            names = zf.namelist()
            self.assertTrue(any(n.endswith("/index.html") for n in names),
                            f"index.html missing from zip: {names}")
            # Each successful row's file should be in the zip
            self.assertTrue(any("01_a_hue.html" in n for n in names))
            self.assertTrue(any("02_b_granny.html" in n for n in names))

    def test_index_html_lists_each_member(self):
        csv_path = self._write_csv([
            {"name": "Anna", "construction": "hue",
             "sts": 22, "rows": 30, "head_cm": 56},
            {"name": "Bo", "construction": "amigurumi",
             "diameter_cm": 6, "gauge": 5},
        ])
        out = self.tmp / "klub_idx"
        report = self.sk.run_batch(csv_path, out, lang="da", make_zip=False)
        idx_text = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn("Anna", idx_text)
        self.assertIn("Bo", idx_text)
        self.assertIn("hue", idx_text)
        self.assertIn("amigurumi", idx_text)
        self.assertEqual(report["ok"], 2)

    def test_extra_columns_become_member_notes(self):
        csv_path = self._write_csv([
            {"name": "Cecilie", "construction": "hue",
             "sts": 22, "rows": 30, "head_cm": 56,
             "favorit_farve": "petroleum",
             "særligt_ønske": "extra langt skaft"},
        ])
        out = self.tmp / "klub_meta"
        self.sk.run_batch(csv_path, out, make_zip=False)
        html = (out / "01_cecilie_hue.html").read_text(encoding="utf-8")
        self.assertIn("favorit_farve", html)
        self.assertIn("petroleum", html)

    def test_bundled_example_csv_runs_end_to_end(self):
        csv_path = _REPO / "examples" / "strikkeklub_eksempel.csv"
        self.assertTrue(csv_path.exists(),
                        "examples/strikkeklub_eksempel.csv missing")
        out = self.tmp / "demo"
        report = self.sk.run_batch(csv_path, out, make_zip=True)
        # Demo CSV should have at least 5 successful members
        self.assertGreaterEqual(report["ok"], 5,
                                f"failed rows: "
                                f"{[r for r in report['results'] if not r.ok]}")


if __name__ == "__main__":
    unittest.main()
