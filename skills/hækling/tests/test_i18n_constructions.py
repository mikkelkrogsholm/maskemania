"""i18n smoke tests for crochet constructions.

Mirrors ``skills/strikning/tests/test_i18n_constructions.py`` but targets the
crochet generators. Anchor markers: "Magic ring", "single crochet" / "sc",
"double crochet" / "dc", "Bind off" / "Cut the yarn".
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_SKILL))

from croclib.constructions import (  # noqa: E402
    GrannySquareSpec, generate_granny_square,
    AmigurumiSphereSpec, amigurumi_sphere,
    AmigurumiCylinderSpec, amigurumi_cylinder,
    C2CBlanketSpec, generate_c2c_blanket,
    CrochetTørklædeSpec, generate_tørklæde,
    FiletSpec, generate_filet,
)


def _all_step_text(pattern) -> str:
    parts = []
    for sec in pattern.sections:
        parts.append(sec.title)
        for step in sec.steps:
            parts.append(step.text)
            if step.note:
                parts.append(step.note)
    return "\n".join(parts)


class GrannySquareLangTests(unittest.TestCase):
    def test_english_granny(self) -> None:
        p = generate_granny_square(GrannySquareSpec(rounds=4), lang="en")
        text = _all_step_text(p)
        self.assertIn("magic ring", text)
        self.assertIn("dc", text)
        self.assertIn("ch ", text)
        self.assertIn("Finishing", text)
        self.assertNotIn("stm", text)
        self.assertNotIn("hjørne", text)

    def test_danish_default(self) -> None:
        p = generate_granny_square(GrannySquareSpec(rounds=4))
        text = _all_step_text(p)
        self.assertIn("stm", text)
        self.assertIn("magic ring", text)  # untranslated in DA too


class AmigurumiLangTests(unittest.TestCase):
    def test_english_sphere(self) -> None:
        p = amigurumi_sphere(AmigurumiSphereSpec(diameter_cm=8), lang="en")
        text = _all_step_text(p)
        self.assertIn("magic ring", text)
        self.assertIn("sc", text)
        self.assertIn("inc", text)
        self.assertIn("dec", text)
        # sphere structure
        self.assertIn("Top half", text)
        self.assertIn("Bottom half", text)

    def test_english_cylinder(self) -> None:
        p = amigurumi_cylinder(
            AmigurumiCylinderSpec(diameter_cm=6, height_cm=10),
            lang="en",
        )
        text = _all_step_text(p)
        self.assertIn("Magic ring", text)
        self.assertIn("Tube", text)
        # No leftover Danish abbreviations
        self.assertNotIn(" fm", text)
        self.assertNotIn("Indt-", text)


class C2CBlanketLangTests(unittest.TestCase):
    def test_english_c2c(self) -> None:
        p = generate_c2c_blanket(
            C2CBlanketSpec(blocks_wide=10, blocks_high=8),
            lang="en",
        )
        text = _all_step_text(p)
        self.assertIn("ch ", text)
        self.assertIn("block", text.lower())
        self.assertIn("Finishing", text)


class CrochetTørklædeLangTests(unittest.TestCase):
    def test_english_torklaede(self) -> None:
        p = generate_tørklæde(
            CrochetTørklædeSpec(
                width_cm=30, length_cm=180,
                gauge_sts_per_cm=2.0, stitch_type="dc",
            ),
            lang="en",
        )
        text = _all_step_text(p)
        self.assertIn("Crochet", text)
        self.assertIn("Foundation chain", text)
        self.assertIn("dc", text)


class FiletLangTests(unittest.TestCase):
    """Fallback construction."""

    def test_english_filet(self) -> None:
        p = generate_filet(
            FiletSpec(width_cells=10, height_cells=10),
            lang="en",
        )
        text = _all_step_text(p)
        # Section titles + at least some translated tokens
        self.assertIn("dc", text)


if __name__ == "__main__":
    unittest.main()
