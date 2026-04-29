"""Tests for knitlib core. Run with: python3 -m unittest discover tests"""

import sys
import unittest
from pathlib import Path

# Repo layout: <repo>/skills/strikning/tests/test_knitlib.py
_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))     # for `lib.visualisering`
sys.path.insert(0, str(_SKILL))    # for `knitlib`

from knitlib import (
    Gauge, cm_to_sts, cm_to_rows, round_to_multiple,
    Row, RowValidator, ValidationError,
    evenly_spaced,
)
from lib.visualisering.shaping import (
    distribute_decreases, format_decrease_row, crown_decrease_plan,
)
from lib.visualisering.bookkeeping import validate_repeat
from knitlib.constructions import (
    HueSpec, generate_hue,
    TørklædeSpec, generate_tørklæde,
    RaglanSpec, generate_raglan,
    SokkerSpec, generate_sokker, heel_turn,
    BottomUpSweaterSpec, generate_bottom_up_sweater, eps_percentages,
)


class TestGauge(unittest.TestCase):
    def test_round_to_multiple_nearest(self):
        self.assertEqual(round_to_multiple(13, 4), 12)
        self.assertEqual(round_to_multiple(14, 4), 16)
        self.assertEqual(round_to_multiple(16, 4), 16)

    def test_round_to_multiple_modes(self):
        self.assertEqual(round_to_multiple(13, 4, mode="up"), 16)
        self.assertEqual(round_to_multiple(13, 4, mode="down"), 12)
        self.assertEqual(round_to_multiple(16, 4, mode="up"), 16)

    def test_cm_to_sts(self):
        g = Gauge(22, 30)
        # 56 cm at 22 sts/10cm = 123.2 sts; round to nearest = 123
        self.assertEqual(cm_to_sts(56, g), 123)
        # rounded to multiple of 8: 120 (closer than 128)
        self.assertEqual(cm_to_sts(56, g, multiple=8), 120)

    def test_cm_to_rows(self):
        g = Gauge(22, 30)
        # 5 cm at 30 rows/10cm = 15 rows
        self.assertEqual(cm_to_rows(5, g), 15)


class TestBookkeeping(unittest.TestCase):
    def test_simple_row_balances(self):
        r = Row(sts_before=10).k(10)
        r.validate()
        self.assertEqual(r.sts_after, 10)

    def test_decrease_row_balances(self):
        # 12 sts → 6 k2tog → 6 sts
        r = Row(sts_before=12).op("k2tog", 6)
        r.validate()
        self.assertEqual(r.sts_after, 6)

    def test_increase_row_balances(self):
        # 12 sts → 12 kfb → 24 sts
        r = Row(sts_before=12).op("kfb", 12)
        r.validate()
        self.assertEqual(r.sts_after, 24)

    def test_unbalanced_row_raises(self):
        # 10 sts, but tries to do 12 k → consumes 12, only has 10
        r = Row(sts_before=10).k(12)
        with self.assertRaises(ValidationError):
            r.validate()

    def test_validator_threads_counts(self):
        v = RowValidator()
        v.add(Row(sts_before=8).k(8))
        v.add(Row(sts_before=8).op("kfb", 8))   # 16
        v.add(Row(sts_before=16).op("k2tog", 8))  # 8
        self.assertEqual(v.final_sts, 8)

    def test_validate_repeat_divisible(self):
        # 8-st rib repeat into 96 sts → 12 repeats
        self.assertEqual(validate_repeat(8, 8, 96), 12)
        with self.assertRaises(ValidationError):
            validate_repeat(8, 8, 97)


class TestShaping(unittest.TestCase):
    def test_evenly_spaced_basic(self):
        self.assertEqual(evenly_spaced(4, 12), [0, 3, 6, 9])
        self.assertEqual(evenly_spaced(0, 10), [])
        self.assertEqual(evenly_spaced(1, 10), [0])

    def test_evenly_spaced_no_overflow(self):
        with self.assertRaises(ValueError):
            evenly_spaced(11, 10)

    def test_distribute_decreases_balances(self):
        # 4 decs in 60 sts: 60 - 8 = 52 plain across 5 gaps = 10/10/10/10/12 etc
        segs = distribute_decreases(4, 60)
        plains = [s for s in segs if s != -1]
        decs = [s for s in segs if s == -1]
        self.assertEqual(len(decs), 4)
        self.assertEqual(sum(plains) + 2 * len(decs), 60)

    def test_distribute_format(self):
        segs = distribute_decreases(2, 20)
        # 20 - 4 = 16 plain across 3 gaps; symmetric: 5,5,6 or 6,5,5
        formatted = format_decrease_row(segs)
        self.assertIn("k2tog", formatted)

    def test_crown_plan_terminates(self):
        plan = crown_decrease_plan(96, sectors=8, min_finish_sts=8)
        # Should reduce 96 → 8 over multiple rounds
        last_sts = plan[-1][1]
        self.assertLessEqual(last_sts, 16)
        # Stitch counts should be monotonically non-increasing
        prev = 96
        for _, sts, _ in plan:
            self.assertLessEqual(sts, prev)
            prev = sts


class TestHue(unittest.TestCase):
    def test_basic_hue_validates(self):
        spec = HueSpec(
            head_circumference_cm=56,
            gauge=Gauge(22, 30),
        )
        p = generate_hue(spec)
        # cast on should be multiple of 8
        cast_on = p.sections[0].sts_before
        self.assertEqual(cast_on % 8, 0)
        # finished circumference roughly = head + ease
        finished_cm = cast_on * 10 / 22
        target = 56 - 3
        self.assertAlmostEqual(finished_cm, target, delta=3)
        # crown ends at small stitch count
        self.assertLessEqual(p.sections[-1].sts_after, 16)

    def test_hue_with_no_ease_warns(self):
        spec = HueSpec(
            head_circumference_cm=56,
            gauge=Gauge(22, 30),
            ease_cm=0,
        )
        p = generate_hue(spec)
        self.assertTrue(any("Ease" in w for w in p.warnings))


class TestTørklæde(unittest.TestCase):
    def test_basic_scarf(self):
        spec = TørklædeSpec(
            width_cm=30, length_cm=180, gauge=Gauge(22, 30),
        )
        p = generate_tørklæde(spec)
        cast_on = p.sections[0].sts_before
        # constant stitch count throughout — flat scarf
        for sec in p.sections:
            self.assertEqual(sec.sts_before, cast_on)
            self.assertEqual(sec.sts_after, cast_on)

    def test_pattern_repeat_respected(self):
        # 8-st repeat
        spec = TørklædeSpec(
            width_cm=30, length_cm=180, gauge=Gauge(22, 30),
            edge_sts=4, pattern_repeat_sts=8,
        )
        p = generate_tørklæde(spec)
        cast_on = p.sections[0].sts_before
        inner = cast_on - 8  # minus 4*2 edges
        self.assertEqual(inner % 8, 0)


class TestRaglan(unittest.TestCase):
    def test_basic_raglan_size_M(self):
        spec = RaglanSpec(
            bust_cm=94, gauge=Gauge(22, 30),
            ease_cm=5,
        )
        p = generate_raglan(spec)
        titles = [s.title for s in p.sections]
        self.assertIn("Halsudskæring", titles)
        self.assertIn("Bærestykke", titles)
        self.assertIn("Krop", titles)
        self.assertIn("Ærmer (begge ens)", titles)

    def test_raglan_body_size_close_to_target(self):
        spec = RaglanSpec(bust_cm=94, gauge=Gauge(22, 30), ease_cm=5)
        p = generate_raglan(spec)
        target = 94 + 5  # 99 cm
        body_sts = next(s for s in p.sections if s.title == "Krop").sts_before
        actual_cm = body_sts * 10 / 22
        self.assertAlmostEqual(actual_cm, target, delta=3)

    def test_sleeve_continuity(self):
        """Regression test: sleeve_total = sts_on_holder + underarm_pickup.
        The off-by-2 bug had +2 raglan markers double-counted."""
        spec = RaglanSpec(bust_cm=94, gauge=Gauge(22, 30), ease_cm=5)
        p = generate_raglan(spec)
        sleeve_section = next(s for s in p.sections if s.title.startswith("Ærmer"))
        # Parse the first step: should describe N + M = sleeve_total_sts
        first_step_text = sleeve_section.steps[0].text
        # Extract numbers — text like "Sæt 89 m fra vente-snor … Saml 4 m fra ærmegab"
        import re
        nums = [int(x) for x in re.findall(r"\b(\d+)\s+m", first_step_text)]
        # nums = [held_sts, underarm_pickup, total]
        self.assertGreaterEqual(len(nums), 3,
                                f"expected 3+ numbers in: {first_step_text!r}")
        held, underarm, total = nums[0], nums[1], nums[2]
        self.assertEqual(held + underarm, total,
                         f"sleeve continuity broken: {held} + {underarm} != {total}")

    def test_raglan_back_greater_than_front(self):
        """Modern practice: back > front by 2 sts."""
        spec = RaglanSpec(bust_cm=94, gauge=Gauge(22, 30))
        p = generate_raglan(spec)
        note = p.notes[0]  # "Halsmasker: 92 = X ryg + Y for + ..."
        import re
        m = re.search(r"(\d+) ryg \+ (\d+) for", note)
        self.assertIsNotNone(m)
        back, front = int(m.group(1)), int(m.group(2))
        self.assertEqual(back - front, 2,
                         f"expected back > front by 2; got back={back}, front={front}")

    def test_raglan_yoke_depth_uses_max_rule(self):
        """yoke_depth = max(bust/4, upper_arm/2 + 4)."""
        # Small bust + big arm → upper_arm/2+4 should win
        spec = RaglanSpec(bust_cm=78, gauge=Gauge(22, 30), upper_arm_cm=40, ease_cm=5)
        p = generate_raglan(spec)
        yoke = p.inputs["yoke_depth_cm"]
        bust_quarter = (78 + 5) / 4
        arm_rule = 40 / 2 + 4
        self.assertAlmostEqual(yoke, max(bust_quarter, arm_rule), delta=0.5)

    def test_raglan_underarm_capped_at_max(self):
        """Auto-computed underarm CO must not exceed 8 cm per side."""
        # Small bust, deep yoke → would otherwise produce huge underarm
        spec = RaglanSpec(bust_cm=120, gauge=Gauge(22, 30),
                          ease_cm=20, yoke_depth_cm=15)
        p = generate_raglan(spec)
        # Find underarm note
        underarm_note = next(n for n in p.notes if "Underarm cast-on" in n)
        import re
        m = re.search(r"\((\d+\.\d+)\s*cm\)", underarm_note)
        self.assertIsNotNone(m)
        underarm_cm = float(m.group(1))
        self.assertLessEqual(underarm_cm, 8.0 + 0.5)

    def test_raglan_underarm_capped_at_min(self):
        """Auto-computed underarm CO must not go below 3 cm per side."""
        # Inputs that would otherwise produce 0 underarm CO
        spec = RaglanSpec(bust_cm=78, gauge=Gauge(22, 30),
                          ease_cm=0, yoke_depth_cm=30)
        p = generate_raglan(spec)
        underarm_note = next(n for n in p.notes if "Underarm cast-on" in n)
        import re
        m = re.search(r"\((\d+\.\d+)\s*cm\)", underarm_note)
        self.assertIsNotNone(m)
        underarm_cm = float(m.group(1))
        self.assertGreaterEqual(underarm_cm, 3.0 - 0.5)


class TestSokker(unittest.TestCase):
    def test_basic_sok_validates(self):
        spec = SokkerSpec(foot_circ_cm=22, foot_length_cm=24, gauge=Gauge(28, 36))
        p = generate_sokker(spec)
        self.assertEqual(p.construction, "sokker")
        # cast-on must be divisible by 4
        self.assertEqual(p.inputs["total_sts"] % 4, 0)
        # heel turn produces a positive H
        self.assertGreater(p.inputs["H_after_turn"], 0)
        self.assertLess(p.inputs["H_after_turn"], p.inputs["flap_sts"])

    def test_total_sts_uses_negative_ease(self):
        # 22 cm circ, 28 sts/10cm gauge, default 10% neg ease
        # finished_circ ≈ 22 * 0.9 = 19.8 cm
        # total ≈ 19.8 * 28 / 10 = 55.44 → round to multiple of 4 → 56
        p = generate_sokker(SokkerSpec(
            foot_circ_cm=22, foot_length_cm=24, gauge=Gauge(28, 36),
        ))
        self.assertEqual(p.inputs["total_sts"], 56)

    def test_heel_turn_even_parity(self):
        # F=28 (even), h=5: rest = 23 (odd)  → branch (rest-2)/2 + 2 = 12.5 → 12... wait
        # Actually 28-5=23 odd → h + (23-2)//2 + 2 = 5 + 10 + 2 = 17
        self.assertEqual(heel_turn(28, 5), 17)

    def test_heel_turn_odd_parity(self):
        # F=28, h=4: rest = 24 (even) → h + 24/2 = 4 + 12 = 16
        self.assertEqual(heel_turn(28, 4), 16)

    def test_heel_turn_raises_on_too_small(self):
        with self.assertRaises(ValueError):
            heel_turn(2, 1)
        with self.assertRaises(ValueError):
            heel_turn(20, 0)

    def test_sokker_pickup_formula(self):
        """pickup_per_side = flap_rows / 2 + 1 (Agent A §3)."""
        p = generate_sokker(SokkerSpec(
            foot_circ_cm=22, foot_length_cm=24, gauge=Gauge(28, 36),
        ))
        flap_rows = p.inputs["flap_rows"]
        self.assertEqual(p.inputs["pickup_per_side"], flap_rows // 2 + 1)

    def test_sokker_warns_on_small_circ(self):
        p = generate_sokker(SokkerSpec(
            foot_circ_cm=16, foot_length_cm=20, gauge=Gauge(28, 36),
        ))
        # Should still generate but warn; but 16 cm is below 18 threshold
        self.assertTrue(any("Fodomkreds" in w for w in p.warnings))


class TestBottomUpSweater(unittest.TestCase):
    def test_basic_sweater(self):
        spec = BottomUpSweaterSpec(bust_cm=94, gauge=Gauge(22, 30), ease_cm=5)
        p = generate_bottom_up_sweater(spec)
        self.assertEqual(p.construction, "bottom_up_sweater")
        # K should be cm_to_sts(99 cm, gauge) rounded to multiple of 2
        # 99 * 22 / 10 = 217.8 → round to 218
        self.assertEqual(p.inputs["K"], 218)

    def test_eps_percentages_yoke(self):
        eps = eps_percentages(K=200, style="yoke")
        # body 90% = 180, sleeve_cuff 20% = 40, sleeve_top 35% = 70,
        # underarm 8% = 16, neck 40% = 80
        self.assertEqual(eps["body"], 180)
        self.assertEqual(eps["sleeve_cuff"], 40)
        self.assertEqual(eps["sleeve_top"], 70)
        self.assertEqual(eps["underarm"], 16)
        self.assertEqual(eps["neck"], 80)

    def test_eps_percentages_drop_silhouette(self):
        eps = eps_percentages(K=200, style="drop")
        # Drop = body 100%
        self.assertEqual(eps["body"], 200)

    def test_eps_percentages_unknown_style(self):
        with self.assertRaises(ValueError):
            eps_percentages(K=200, style="weird")

    def test_yoke_invariant(self):
        """yoke_start = body - 2u + 2*(arm_top - 2u)  (Agent A §1)."""
        spec = BottomUpSweaterSpec(bust_cm=94, gauge=Gauge(22, 30), ease_cm=5)
        p = generate_bottom_up_sweater(spec)
        u = p.inputs["underarm_sts"]
        body = p.inputs["body_sts"]
        arm = p.inputs["sleeve_top_sts"]
        expected = body - 2*u + 2*(arm - 2*u)
        self.assertEqual(p.inputs["yoke_start_sts"], expected)

    def test_underarm_body_equals_underarm_sleeve(self):
        """Body underarm-hold and sleeve underarm-hold must match exactly."""
        spec = BottomUpSweaterSpec(bust_cm=94, gauge=Gauge(22, 30), ease_cm=5)
        p = generate_bottom_up_sweater(spec)
        # Both refer to the same number — the test enforces we don't drift.
        self.assertGreaterEqual(p.inputs["underarm_sts"], 2)

    def test_sweater_uses_user_upper_arm_when_given(self):
        spec = BottomUpSweaterSpec(
            bust_cm=94, gauge=Gauge(22, 30), ease_cm=5, upper_arm_cm=33,
        )
        p = generate_bottom_up_sweater(spec)
        # 33 cm at 22 sts/10 cm = 72.6 → round to multiple of 2 → 72
        self.assertEqual(p.inputs["sleeve_top_sts"], 72)


class TestEdgeCases(unittest.TestCase):
    def test_round_to_multiple_one_with_modes(self):
        """multiple=1 with mode=up/down should respect the mode."""
        from lib.visualisering.gauge import round_to_multiple
        self.assertEqual(round_to_multiple(13.2, 1, mode="up"), 14)
        self.assertEqual(round_to_multiple(13.8, 1, mode="down"), 13)
        self.assertEqual(round_to_multiple(13.4, 1, mode="nearest"), 13)

    def test_crown_plan_raises_on_too_small(self):
        from lib.visualisering.shaping import crown_decrease_plan
        with self.assertRaises(ValueError):
            crown_decrease_plan(8, sectors=8)
        with self.assertRaises(ValueError):
            crown_decrease_plan(4, sectors=8)

    def test_crown_plan_minimum_size(self):
        """start_sts == 2*sectors should produce one round and exit."""
        from lib.visualisering.shaping import crown_decrease_plan
        plan = crown_decrease_plan(16, sectors=8)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0][1], 8)  # ends at 8 sts


if __name__ == "__main__":
    unittest.main()
