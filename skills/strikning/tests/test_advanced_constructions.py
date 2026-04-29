"""Tests for the Fase 5 iter 1 advanced constructions:
compound_raglan, half_pi_shawl, yoke_stranded.

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

from knitlib import Gauge, ValidationError  # noqa: E402
from knitlib.constructions import (  # noqa: E402
    CompoundRaglanSpec, generate_compound_raglan,
    HalfPiShawlSpec, generate_half_pi_shawl, pi_shawl_progression,
    YokeStrandedSpec, generate_yoke_stranded,
    repeat_fit, render_color_chart, DEFAULT_MOTIF,
    ShortRowsShawlSpec, generate_short_rows_shawl,
    HueSpec, generate_hue,
    TørklædeSpec, generate_tørklæde,
    RaglanSpec, generate_raglan,
    SokkerSpec, generate_sokker,
    BottomUpSweaterSpec, generate_bottom_up_sweater,
)
from lib.visualisering.html import render_html  # noqa: E402


# --- Compound raglan ---------------------------------------------------

class TestCompoundRaglan(unittest.TestCase):
    def _basic(self, **kw):
        defaults = dict(bust_cm=94, upper_arm_cm=33, gauge=Gauge(22, 30),
                        ease_cm=5)
        defaults.update(kw)
        return generate_compound_raglan(CompoundRaglanSpec(**defaults))

    def test_construction_name(self):
        p = self._basic()
        self.assertEqual(p.construction, "compound_raglan")

    def test_body_hits_bust_target(self):
        """Body sts should land within 2 cm of finished bust."""
        p = self._basic()
        body = p.inputs["body_sts"]
        target_cm = p.inputs["finished_bust_cm"]
        body_cm = body * 10 / p.inputs["gauge"]["sts_per_10cm"]
        self.assertLess(abs(body_cm - target_cm), 2.5,
                        f"body {body_cm:.1f} cm vs target {target_cm} cm")

    def test_sleeve_hits_upper_arm_target(self):
        """Sleeve sts should land within 2 cm of upper-arm target."""
        p = self._basic()
        sleeve = p.inputs["sleeve_sts"]
        target_cm = p.inputs["upper_arm_cm"]
        sleeve_cm = sleeve * 10 / p.inputs["gauge"]["sts_per_10cm"]
        self.assertLess(abs(sleeve_cm - target_cm), 2.5,
                        f"sleeve {sleeve_cm:.1f} cm vs target {target_cm} cm")

    def test_body_and_sleeve_independent(self):
        """Compound raglan: changing upper_arm doesn't change body sts."""
        p1 = self._basic(upper_arm_cm=30)
        p2 = self._basic(upper_arm_cm=36)
        # Body should stay (or nearly stay) the same; sleeve should differ
        self.assertEqual(p1.inputs["body_sts"], p2.inputs["body_sts"])
        self.assertNotEqual(p1.inputs["sleeve_sts"], p2.inputs["sleeve_sts"])

    def test_inc_budgets_fit_yoke_window(self):
        """Both body_inc_rounds and sleeve_inc_rounds must fit in available."""
        p = self._basic()
        avail = p.inputs["yoke_inc_rounds_available"]
        self.assertLessEqual(p.inputs["body_inc_rounds"], avail)
        self.assertLessEqual(p.inputs["sleeve_inc_rounds"], avail)

    def test_neck_distribution_balances(self):
        """back + 2*sleeve_seed + front == neck_sts."""
        p = self._basic()
        total = (p.inputs["back_sts"] + p.inputs["front_sts"] +
                 2 * p.inputs["sleeve_seed_sts"])
        self.assertEqual(total, p.inputs["neck_sts"])

    def test_back_greater_than_front(self):
        """back > front by 2 sts (anti-rideup)."""
        p = self._basic()
        self.assertEqual(p.inputs["back_sts"] - p.inputs["front_sts"], 2)

    def test_raises_on_too_small_neck(self):
        """Tiny neck circ should raise ValueError."""
        with self.assertRaises(ValueError):
            self._basic(neck_circumference_cm=10)

    def test_raises_on_too_shallow_yoke(self):
        """If yoke_depth is way too shallow, should raise."""
        with self.assertRaises(ValueError):
            # Forcing a tiny yoke and a huge bust with low gauge
            generate_compound_raglan(CompoundRaglanSpec(
                bust_cm=140, upper_arm_cm=42, gauge=Gauge(28, 36),
                ease_cm=8, yoke_depth_cm=8,
            ))

    def test_pattern_has_all_sections(self):
        p = self._basic()
        titles = [s.title for s in p.sections]
        self.assertIn("Halsudskæring", titles)
        self.assertIn("Bærestykke (compound)", titles)
        self.assertIn("Krop", titles)
        self.assertIn("Ærmer (begge ens)", titles)


# --- Half-pi shawl ----------------------------------------------------

class TestHalfPiShawl(unittest.TestCase):

    def test_progression_matches_zimmermann_table(self):
        """Verified from Agent A: 0,3,9,21,45,93,189 center-sts."""
        progression = pi_shawl_progression(6, edge_sts=4)
        centers = [c for _, _, c in progression]
        self.assertEqual(centers, [0, 3, 9, 21, 45, 93, 189])

    def test_totals_match_zimmermann_table(self):
        """Total sts (center + 2*edge=8) = 8,11,17,29,53,101,197."""
        progression = pi_shawl_progression(6, edge_sts=4)
        totals = [c + 8 for _, _, c in progression]
        self.assertEqual(totals, [8, 11, 17, 29, 53, 101, 197])

    def test_plain_rows_double(self):
        """Plain rows: 1, 3, 6, 12, 24, 48, 96 (each doubles)."""
        progression = pi_shawl_progression(6, edge_sts=4)
        plain_rows = [pr for _, pr, _ in progression]
        self.assertEqual(plain_rows, [1, 3, 6, 12, 24, 48, 96])

    def test_basic_pattern_generates(self):
        p = generate_half_pi_shawl(HalfPiShawlSpec(
            gauge=Gauge(18, 24), n_doublings=5,
        ))
        self.assertEqual(p.construction, "half_pi_shawl")
        # 5 doublings → final center = 93, total 101
        self.assertEqual(p.inputs["final_total_sts"], 101)

    def test_pattern_has_one_section_per_band(self):
        """Setup + n_doublings doubling-sections + aflukning."""
        p = generate_half_pi_shawl(HalfPiShawlSpec(
            gauge=Gauge(18, 24), n_doublings=4,
        ))
        # Setup section + 4 bands + aflukning = 6 sections
        self.assertEqual(len(p.sections), 6)

    def test_warns_on_few_doublings(self):
        p = generate_half_pi_shawl(HalfPiShawlSpec(
            gauge=Gauge(18, 24), n_doublings=3,
        ))
        self.assertTrue(any("for små" in w.lower() or "lille" in w.lower()
                            for w in p.warnings))

    def test_raises_on_excessive_doublings(self):
        with self.assertRaises(ValueError):
            generate_half_pi_shawl(HalfPiShawlSpec(
                gauge=Gauge(18, 24), n_doublings=10,
            ))

    def test_lace_motifs_attach_to_bands(self):
        p = generate_half_pi_shawl(HalfPiShawlSpec(
            gauge=Gauge(18, 24), n_doublings=4,
            lace_motifs=["leaf", "feather", "diamond", "fan"],
        ))
        # The motifs are stored
        self.assertEqual(p.inputs["lace_motifs"],
                          ["leaf", "feather", "diamond", "fan"])


# --- Yoke stranded ----------------------------------------------------

class TestYokeStranded(unittest.TestCase):
    def _basic(self, **kw):
        defaults = dict(bust_cm=94, gauge=Gauge(22, 30), ease_cm=5,
                        repeat_width=8)
        defaults.update(kw)
        return generate_yoke_stranded(YokeStrandedSpec(**defaults))

    def test_construction_name(self):
        p = self._basic()
        self.assertEqual(p.construction, "yoke_stranded")

    def test_yoke_start_is_repeat_multiple(self):
        """yoke_start must be a multiple of repeat_width."""
        p = self._basic(repeat_width=8)
        self.assertEqual(p.inputs["yoke_start_sts"] % 8, 0)

    def test_all_yoke_bands_are_repeat_multiples(self):
        """Each shaping band must align with the motif repeat."""
        p = self._basic(repeat_width=8)
        R = 8
        self.assertEqual(p.inputs["yoke_start_sts"] % R, 0)
        self.assertEqual(p.inputs["after_dec1_sts"] % R, 0)
        self.assertEqual(p.inputs["after_dec2_sts"] % R, 0)
        self.assertEqual(p.inputs["after_dec3_sts"] % R, 0)
        self.assertEqual(p.inputs["neck_sts"] % R, 0)

    def test_decrease_factors_approximate_research(self):
        """after_dec1 ≈ 0.75*yoke_start; after_dec2 ≈ 0.70*after_dec1."""
        p = self._basic()
        ys = p.inputs["yoke_start_sts"]
        d1 = p.inputs["after_dec1_sts"]
        d2 = p.inputs["after_dec2_sts"]
        # Snapped to multiple of 8 down — within one R
        self.assertLessEqual(d1, ys * 0.75 + 8)
        self.assertGreaterEqual(d1, ys * 0.75 - 8)
        self.assertLessEqual(d2, d1 * 0.70 + 8)
        self.assertGreaterEqual(d2, d1 * 0.70 - 8)

    def test_progression_is_monotone(self):
        """yoke_start > after_dec1 > after_dec2 > neck."""
        p = self._basic()
        self.assertGreater(p.inputs["yoke_start_sts"], p.inputs["after_dec1_sts"])
        self.assertGreater(p.inputs["after_dec1_sts"], p.inputs["after_dec2_sts"])
        self.assertGreater(p.inputs["after_dec2_sts"], p.inputs["neck_sts"])

    def test_repeat_fit_basic(self):
        self.assertEqual(repeat_fit(100, 8, mode="down"), 96)
        self.assertEqual(repeat_fit(100, 8, mode="up"), 104)
        # 100 mod 8 = 4 (exactly halfway); convention rounds down.
        self.assertEqual(repeat_fit(100, 8, mode="nearest"), 96)
        # 101 mod 8 = 5 (closer to 104).
        self.assertEqual(repeat_fit(101, 8, mode="nearest"), 104)
        self.assertEqual(repeat_fit(96, 8), 96)
        self.assertEqual(repeat_fit(0, 8), 0)

    def test_repeat_fit_invalid(self):
        with self.assertRaises(ValueError):
            repeat_fit(100, 0)
        with self.assertRaises(ValueError):
            repeat_fit(-5, 8)

    def test_color_chart_renders(self):
        chart = render_color_chart(DEFAULT_MOTIF)
        # 6 rows + separator
        lines = chart.split("\n")
        self.assertEqual(len(lines), 7)
        # Top row labelled "6"
        self.assertTrue(lines[0].lstrip().startswith("6"))
        # Bottom data row labelled "1"
        self.assertTrue(lines[5].lstrip().startswith("1"))

    def test_chart_in_pattern_inputs(self):
        p = self._basic()
        self.assertIn("color_chart", p.inputs)
        self.assertIn("■", p.inputs["color_chart"])
        self.assertIn("□", p.inputs["color_chart"])

    def test_raises_on_too_small_arm(self):
        """Tiny upper_arm with chunky yarn → sleeve_after_join < 4."""
        with self.assertRaises(ValueError):
            generate_yoke_stranded(YokeStrandedSpec(
                bust_cm=94, gauge=Gauge(22, 30), ease_cm=5,
                upper_arm_cm=10,
            ))

    def test_custom_repeat_width_4(self):
        p = self._basic(repeat_width=4)
        self.assertEqual(p.inputs["repeat_width"], 4)
        self.assertEqual(p.inputs["yoke_start_sts"] % 4, 0)

    def test_pattern_has_yoke_section(self):
        p = self._basic()
        titles = [s.title for s in p.sections]
        self.assertIn("Hals (top-down)", titles)
        self.assertIn("Bærestykke (top-down)", titles)
        self.assertIn("Krop", titles)


# --- Short-row crescent shawl ----------------------------------------

class TestShortRowsShawl(unittest.TestCase):
    def _basic(self, **kw):
        defaults = dict(gauge=Gauge(22, 30), cast_on=3, increase_rows=80)
        defaults.update(kw)
        return generate_short_rows_shawl(ShortRowsShawlSpec(**defaults))

    def test_construction_name(self):
        p = self._basic()
        self.assertEqual(p.construction, "short_rows_shawl")

    def test_final_sts_formula(self):
        """final_sts = cast_on + 2 * increase_rows."""
        p = self._basic(cast_on=3, increase_rows=80)
        self.assertEqual(p.inputs["final_sts"], 3 + 2 * 80)
        p2 = self._basic(cast_on=5, increase_rows=50)
        self.assertEqual(p2.inputs["final_sts"], 5 + 2 * 50)

    def test_short_row_pairs_match_cadence(self):
        """short_row_pairs = increase_rows // cadence."""
        p = self._basic(increase_rows=80, short_row_cadence=8)
        self.assertEqual(p.inputs["short_row_pairs"], 10)
        p2 = self._basic(increase_rows=60, short_row_cadence=10)
        self.assertEqual(p2.inputs["short_row_pairs"], 6)

    def test_pattern_has_expected_sections(self):
        p = self._basic()
        titles = [s.title for s in p.sections]
        self.assertIn("Garter-tab og opslag", titles)
        self.assertIn("Forøgelser (rygsøjle af shawlet)", titles)
        self.assertIn("Korte rækker (kurve-formning)", titles)
        self.assertIn("Aflukning", titles)

    def test_raises_on_too_few_increase_rows(self):
        with self.assertRaises(ValueError):
            generate_short_rows_shawl(ShortRowsShawlSpec(
                gauge=Gauge(22, 30), increase_rows=2,
            ))

    def test_raises_on_too_small_cast_on(self):
        with self.assertRaises(ValueError):
            generate_short_rows_shawl(ShortRowsShawlSpec(
                gauge=Gauge(22, 30), cast_on=1,
            ))

    def test_raises_on_excessive_increase_rows(self):
        with self.assertRaises(ValueError):
            generate_short_rows_shawl(ShortRowsShawlSpec(
                gauge=Gauge(22, 30), increase_rows=10_000,
            ))

    def test_validator_reaches_final_sts(self):
        """Last section ends at final_sts, plus continuity is intact."""
        p = self._basic()
        # validate continuity (no exceptions)
        p.validate_continuity()
        self.assertEqual(p.sections[-1].sts_after, p.inputs["final_sts"])

    def test_warns_when_no_short_rows_fit(self):
        """If short_row_cadence > increase_rows, no short rows are scheduled."""
        p = self._basic(increase_rows=10, short_row_cadence=99)
        self.assertEqual(p.inputs["short_row_pairs"], 0)
        self.assertTrue(any("crescent" in w.lower() or "triangel" in w.lower()
                            for w in p.warnings))


# --- Difficulty rating ------------------------------------------------

class TestDifficultyRating(unittest.TestCase):
    """Verify each construction sets a difficulty + render shows it."""

    def test_difficulty_per_construction(self):
        cases = [
            (generate_hue(HueSpec(
                head_circumference_cm=56, gauge=Gauge(22, 30))),
                "beginner"),
            (generate_tørklæde(TørklædeSpec(
                width_cm=30, length_cm=180, gauge=Gauge(22, 30))),
                "beginner"),
            (generate_raglan(RaglanSpec(
                bust_cm=94, gauge=Gauge(22, 30))),
                "easy"),
            (generate_sokker(SokkerSpec(
                foot_circ_cm=22, foot_length_cm=24, gauge=Gauge(28, 36))),
                "intermediate"),
            (generate_bottom_up_sweater(BottomUpSweaterSpec(
                bust_cm=94, gauge=Gauge(22, 30))),
                "easy"),
            (generate_compound_raglan(CompoundRaglanSpec(
                bust_cm=94, upper_arm_cm=33, gauge=Gauge(22, 30))),
                "intermediate"),
            (generate_half_pi_shawl(HalfPiShawlSpec(
                gauge=Gauge(18, 24), n_doublings=5)),
                "intermediate"),
            (generate_yoke_stranded(YokeStrandedSpec(
                bust_cm=94, gauge=Gauge(22, 30))),
                "advanced"),
            (generate_short_rows_shawl(ShortRowsShawlSpec(
                gauge=Gauge(22, 30))),
                "intermediate"),
        ]
        for pat, expected in cases:
            self.assertEqual(pat.difficulty, expected,
                             f"{pat.construction}: got {pat.difficulty!r}, "
                             f"want {expected!r}")

    def test_html_contains_difficulty_da(self):
        p = generate_hue(HueSpec(
            head_circumference_cm=56, gauge=Gauge(22, 30)))
        out = render_html(p, lang="da")
        self.assertIn("Sværhedsgrad", out)
        self.assertIn("Begynder", out)
        # And the html class
        self.assertIn('class="difficulty"', out)

    def test_html_contains_difficulty_en(self):
        p = generate_hue(HueSpec(
            head_circumference_cm=56, gauge=Gauge(22, 30)))
        out = render_html(p, lang="en")
        self.assertIn("Difficulty", out)
        self.assertIn("Beginner", out)


if __name__ == "__main__":
    unittest.main()
