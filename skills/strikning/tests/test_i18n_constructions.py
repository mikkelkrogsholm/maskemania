"""i18n smoke tests for knit constructions.

Verifies that ``generate_X(spec, lang="en")`` produces step text containing
recognizable English vocabulary, while ``lang="da"`` (or the default) still
returns Danish output. We deliberately don't pin every word — the underlying
prose can change — but we do anchor on a few high-signal markers like
"Cast on", "Knit", "Bind off" / their Danish counterparts.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Make repo root + skill root importable.
_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_SKILL))

from knitlib import Gauge  # noqa: E402
from knitlib.constructions import (  # noqa: E402
    HueSpec, generate_hue,
    TørklædeSpec, generate_tørklæde,
    RaglanSpec, generate_raglan,
    SokkerSpec, generate_sokker,
    BottomUpSweaterSpec, generate_bottom_up_sweater,
    CompoundRaglanSpec, generate_compound_raglan,
)


def _all_step_text(pattern) -> str:
    """Concatenate every section title + step text for fuzzy assertion."""
    parts = []
    for sec in pattern.sections:
        parts.append(sec.title)
        for step in sec.steps:
            parts.append(step.text)
            if step.note:
                parts.append(step.note)
    return "\n".join(parts)


class HueLangTests(unittest.TestCase):
    def test_english_step_text_contains_cast_on_and_knit(self) -> None:
        p = generate_hue(
            HueSpec(head_circumference_cm=56, gauge=Gauge(22, 30)),
            lang="en",
        )
        text = _all_step_text(p)
        self.assertIn("Cast on", text)
        self.assertIn("Knit", text)
        self.assertIn("Crown", text)
        # No leftover Danish marker words
        self.assertNotIn("Slå ", text)
        self.assertNotIn("masker", text)

    def test_danish_default_still_works(self) -> None:
        p = generate_hue(
            HueSpec(head_circumference_cm=56, gauge=Gauge(22, 30)),
        )
        text = _all_step_text(p)
        self.assertIn("Slå", text)
        self.assertIn("Strik", text)
        self.assertNotIn("Cast on", text)


class RaglanLangTests(unittest.TestCase):
    def test_english_raglan(self) -> None:
        p = generate_raglan(
            RaglanSpec(bust_cm=94, gauge=Gauge(22, 30)),
            lang="en",
        )
        text = _all_step_text(p)
        self.assertIn("Cast on", text)
        self.assertIn("Yoke", text)
        self.assertIn("Bind off", text)
        # crucially: section titles are translated
        sec_titles = [sec.title for sec in p.sections]
        self.assertIn("Neckline", sec_titles)
        self.assertIn("Body", sec_titles)


class SokkerLangTests(unittest.TestCase):
    def test_english_sokker(self) -> None:
        p = generate_sokker(
            SokkerSpec(foot_circ_cm=22, foot_length_cm=24, gauge=Gauge(28, 36)),
            lang="en",
        )
        text = _all_step_text(p)
        self.assertIn("Cast on", text)
        self.assertIn("heel", text.lower())  # heel/heel flap/heel turn
        self.assertIn("Toe", text)


class BottomUpSweaterLangTests(unittest.TestCase):
    def test_english_sweater(self) -> None:
        p = generate_bottom_up_sweater(
            BottomUpSweaterSpec(bust_cm=94, gauge=Gauge(22, 30)),
            lang="en",
        )
        text = _all_step_text(p)
        self.assertIn("Cast on", text)
        self.assertIn("Yoke", text)
        self.assertIn("Bind off", text)


class TørklædeLangTests(unittest.TestCase):
    def test_english_torklaede(self) -> None:
        p = generate_tørklæde(
            TørklædeSpec(width_cm=30, length_cm=180, gauge=Gauge(22, 30)),
            lang="en",
        )
        text = _all_step_text(p)
        self.assertIn("Cast on", text)
        self.assertIn("garter", text.lower())


class CompoundRaglanLangTests(unittest.TestCase):
    """Fallback-translated construction — uses ``translate_pattern``."""

    def test_english_partially_translated(self) -> None:
        p = generate_compound_raglan(
            CompoundRaglanSpec(
                bust_cm=94, upper_arm_cm=31, gauge=Gauge(22, 30),
            ),
            lang="en",
        )
        text = _all_step_text(p)
        # Even though step text isn't 100% bilingually authored, the
        # phrase-replace pass should land on at least "Cast on" + a few
        # English nouns.
        self.assertIn("Cast on", text)
        self.assertIn("Yoke", text)


if __name__ == "__main__":
    unittest.main()
