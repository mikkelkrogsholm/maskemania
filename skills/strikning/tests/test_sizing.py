"""Tests for child-sizing tables + --age auto-fill in generate.py."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

# Repo layout: tests live at skills/strikning/tests/, repo root is two up.
_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_SKILL))

from knitlib.sizing import (  # noqa: E402
    CHILD_SIZES,
    child_size,
    chest_for_age,
    foot_for_age,
    head_for_age,
    known_age_labels,
    sleeve_for_age,
)


_GENERATE = _SKILL / "scripts" / "generate.py"


class ChildSizeLookupTests(unittest.TestCase):
    """The tables themselves and the lookup helpers."""

    def test_known_labels_cover_0_to_12_years(self):
        labels = known_age_labels()
        # Spec: 0-3M, 3-6M, 6-12M, 1-2y, 2-4y, 4-6y, 6-8y, 8-10y, 10-12y
        self.assertEqual(len(labels), 9)
        self.assertEqual(labels[0], "0-3M")
        self.assertEqual(labels[-1], "10-12y")

    def test_child_size_returns_dict_with_all_keys(self):
        sz = child_size("6-12M")
        self.assertIn("head_circumference_cm", sz)
        self.assertIn("chest_cm", sz)
        self.assertIn("foot_length_cm", sz)
        self.assertIn("sleeve_length_cm", sz)
        # Realistic 6-12-month head ~44 cm.
        self.assertAlmostEqual(sz["head_circumference_cm"], 44.0, delta=2.0)

    def test_helpers_match_table(self):
        self.assertEqual(head_for_age("6-12M"),
                         CHILD_SIZES["6-12M"]["head_circumference_cm"])
        self.assertEqual(chest_for_age("4-6y"),
                         CHILD_SIZES["4-6y"]["chest_cm"])
        self.assertEqual(foot_for_age("2-4y"),
                         CHILD_SIZES["2-4y"]["foot_length_cm"])
        self.assertEqual(sleeve_for_age("8-10y"),
                         CHILD_SIZES["8-10y"]["sleeve_length_cm"])

    def test_aliases_resolve(self):
        self.assertEqual(child_size("newborn"), child_size("0-3M"))
        self.assertEqual(child_size("6-12m"), child_size("6-12M"))
        self.assertEqual(child_size("toddler"), child_size("1-2y"))

    def test_unknown_age_label_raises(self):
        with self.assertRaises(ValueError):
            child_size("99y")

    def test_measurements_are_monotonic_with_age(self):
        """Older children should be bigger than younger ones in every dim."""
        labels = known_age_labels()
        for prev, nxt in zip(labels, labels[1:]):
            for key in ("head_circumference_cm", "chest_cm",
                        "foot_length_cm", "sleeve_length_cm"):
                self.assertGreaterEqual(
                    CHILD_SIZES[nxt][key], CHILD_SIZES[prev][key],
                    f"{key} should not decrease from {prev} to {nxt}"
                )


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_GENERATE), *args],
        capture_output=True,
        text=True,
        cwd=str(_REPO),
    )


class AgeFlagTests(unittest.TestCase):
    """The --age flag fills in body measurements (and explicit overrides win)."""

    def test_hue_with_age_6_12M_fills_head(self):
        r = _run_cli("hue", "--age", "6-12M", "--sts", "22", "--rows", "30")
        self.assertEqual(r.returncode, 0, r.stderr)
        # 6-12M head ~44 cm; rendered in the input dump.
        self.assertIn("head_circumference_cm:** 44", r.stdout)

    def test_explicit_head_overrides_age(self):
        r = _run_cli("hue", "--age", "6-12M",
                     "--head", "47",
                     "--sts", "22", "--rows", "30")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("head_circumference_cm:** 47", r.stdout)
        self.assertNotIn("head_circumference_cm:** 44", r.stdout)

    def test_raglan_with_age_fills_bust_and_sleeve(self):
        r = _run_cli("raglan", "--age", "4-6y",
                     "--sts", "22", "--rows", "30")
        self.assertEqual(r.returncode, 0, r.stderr)
        # 4-6y chest ~57 cm; sleeve ~30 cm (4-6y table).
        self.assertIn("bust_cm:** 57", r.stdout)
        self.assertIn("sleeve_length_cm:** 30", r.stdout)


if __name__ == "__main__":
    unittest.main()
