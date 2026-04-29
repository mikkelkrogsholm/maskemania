"""Tests for child-sizing helpers re-exported by croclib."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_SKILL))

from croclib.sizing import (  # noqa: E402
    CHILD_SIZES,
    child_size,
    head_for_age,
    known_age_labels,
)


class CrocSizingReExportTests(unittest.TestCase):

    def test_known_age_labels_present(self):
        labels = known_age_labels()
        self.assertIn("0-3M", labels)
        self.assertIn("6-12M", labels)
        self.assertIn("10-12y", labels)

    def test_child_size_returns_expected_keys(self):
        sz = child_size("3-6M")
        for k in ("head_circumference_cm", "chest_cm",
                  "foot_length_cm", "sleeve_length_cm"):
            self.assertIn(k, sz)

    def test_helpers_match_table(self):
        self.assertEqual(head_for_age("4-6y"),
                         CHILD_SIZES["4-6y"]["head_circumference_cm"])


if __name__ == "__main__":
    unittest.main()
