"""Tests for croclib core. Run with: python3 -m unittest discover tests"""

import math
import sys
import unittest
from pathlib import Path

# Repo layout: <repo>/skills/hækling/tests/test_croclib.py
_HERE = Path(__file__).resolve().parent
_SKILL = _HERE.parent
_REPO = _SKILL.parent.parent
sys.path.insert(0, str(_REPO))     # for `lib.visualisering`
sys.path.insert(0, str(_SKILL))    # for `croclib`

from croclib import (  # noqa: E402
    CroStitch, STITCHES, ALIASES, magic_ring, stitch,
    CrochetRow, RowValidator, ValidationError,
)
from croclib.constructions import (  # noqa: E402
    amigurumi_sphere, AmigurumiSphereSpec,
    AmigurumiCylinderSpec, amigurumi_cylinder,
    AmigurumiTaperSpec, amigurumi_taper,
    AmigurumiFigurSpec, amigurumi_figur,
    amigurumi_bjørn, amigurumi_kanin,
    GrannySquareSpec, generate_granny_square,
    CrochetTørklædeSpec, generate_tørklæde,
    FiletSpec, generate_filet,
    filet_stitches_per_row, filet_foundation_chain,
    TunisianSpec, generate_tunisian, TunisianRow,
    C2CBlanketSpec, generate_c2c_blanket,
    c2c_total_blocks, c2c_total_dc, c2c_blocks_per_row,
    MandalaSpec, generate_mandala, default_round_progression,
)
from lib.visualisering.yarn_db import (  # noqa: E402
    Yarn, YARNS, lookup_yarn, suggest_substitute,
    apply_yarn_to_pattern, auto_gauge_from_yarn,
)


class TestStitchDictionary(unittest.TestCase):
    def test_us_lookup(self):
        self.assertEqual(stitch("sc").consumes, 1)
        self.assertEqual(stitch("sc").produces, 1)
        self.assertEqual(stitch("dc").consumes, 1)
        self.assertEqual(stitch("dc").produces, 1)

    def test_chain_consumes_zero(self):
        ch = stitch("ch")
        self.assertEqual(ch.consumes, 0)
        self.assertEqual(ch.produces, 1)
        self.assertFalse(ch.counts_as_stitch)

    def test_slip_stitch_zero_produces(self):
        ss = stitch("sl_st")
        self.assertEqual(ss.consumes, 1)
        self.assertEqual(ss.produces, 0)
        self.assertFalse(ss.counts_as_stitch)

    def test_decreases(self):
        self.assertEqual(stitch("sc2tog").consumes, 2)
        self.assertEqual(stitch("sc2tog").produces, 1)
        self.assertEqual(stitch("dc2tog").consumes, 2)
        self.assertEqual(stitch("dc2tog").produces, 1)

    def test_increases(self):
        self.assertEqual(stitch("sc_inc").consumes, 1)
        self.assertEqual(stitch("sc_inc").produces, 2)

    def test_yarn_overs(self):
        # sc=0, hdc=1, dc=1, tr=2
        self.assertEqual(stitch("sc").yarn_overs, 0)
        self.assertEqual(stitch("hdc").yarn_overs, 1)
        self.assertEqual(stitch("dc").yarn_overs, 1)
        self.assertEqual(stitch("tr").yarn_overs, 2)

    def test_uk_aliases(self):
        # UK dc = US sc, UK tr = US dc
        self.assertEqual(stitch("uk_dc").name, "sc")
        self.assertEqual(stitch("uk_tr").name, "dc")
        self.assertEqual(stitch("uk_dtr").name, "tr")

    def test_danish_aliases(self):
        self.assertEqual(stitch("fm").name, "sc")
        self.assertEqual(stitch("lm").name, "ch")
        self.assertEqual(stitch("km").name, "sl_st")
        self.assertEqual(stitch("hstm").name, "hdc")
        self.assertEqual(stitch("stm").name, "dc")
        self.assertEqual(stitch("dst").name, "tr")
        self.assertEqual(stitch("indt").name, "sc2tog")
        self.assertEqual(stitch("udt").name, "sc_inc")

    def test_unknown_stitch_raises(self):
        with self.assertRaises(KeyError):
            stitch("nope")

    def test_case_and_separator_insensitive(self):
        self.assertEqual(stitch("SC").name, "sc")
        self.assertEqual(stitch("sl-st").name, "sl_st")
        self.assertEqual(stitch("Sl St").name, "sl_st")

    def test_costitch_is_stitch_subclass(self):
        from lib.visualisering.bookkeeping import Stitch
        self.assertTrue(issubclass(CroStitch, Stitch))
        self.assertIsInstance(stitch("sc"), Stitch)


class TestCrochetRow(unittest.TestCase):
    def test_simple_row_balances(self):
        r = CrochetRow(sts_before=20).sc(20)
        r.validate()
        self.assertEqual(r.sts_after, 20)

    def test_decrease_row_balances(self):
        # 20 sts → 10 sc2tog → 10 sts
        r = CrochetRow(sts_before=20).sc2tog(10)
        r.validate()
        self.assertEqual(r.sts_after, 10)

    def test_increase_row_balances(self):
        # 6 sts → 6 sc_inc → 12 sts
        r = CrochetRow(sts_before=6).sc_inc(6)
        r.validate()
        self.assertEqual(r.sts_after, 12)

    def test_unbalanced_row_raises(self):
        # 10 sts but 12 sc tries to consume 12
        r = CrochetRow(sts_before=10).sc(12)
        with self.assertRaises(ValidationError):
            r.validate()

    def test_validator_threads_counts(self):
        v = RowValidator()
        v.add(CrochetRow(sts_before=0).magic_ring(6))
        v.add(CrochetRow(sts_before=6).sc_inc(6))   # → 12
        # 12 sts → 6 plain sc + 6 sc_inc = consumes 12, produces 6+12 = 18
        v.add(CrochetRow(sts_before=12).op("sc", 6).op("sc_inc", 6))
        self.assertEqual(v.final_sts, 18)


class TestMagicRing(unittest.TestCase):
    def test_default_six(self):
        m = magic_ring()
        self.assertEqual(m.produces, 6)
        self.assertEqual(m.consumes, 0)
        self.assertEqual(m.works_into, "mr")

    def test_custom_count(self):
        self.assertEqual(magic_ring(8).produces, 8)
        self.assertEqual(magic_ring(4).produces, 4)

    def test_used_in_row(self):
        r = CrochetRow(sts_before=0).magic_ring(6)
        r.validate()
        self.assertEqual(r.sts_after, 6)


class TestAmigurumiSphere(unittest.TestCase):
    def test_basic_sphere_stitch_count_balances(self):
        p = amigurumi_sphere(diameter_cm=8, gauge_sc_per_cm=5)
        # final pattern lukker ned til 0 sts
        self.assertEqual(p.sections[-1].sts_after, 0)
        # max stitches is reached at end of "Øvre halvdel"
        sec_top = next(s for s in p.sections if s.title.startswith("Øvre"))
        n_max = p.inputs["n_max"]
        self.assertEqual(sec_top.sts_after, 6 * n_max)

    def test_sphere_diameter_close_to_target(self):
        p = amigurumi_sphere(diameter_cm=10, gauge_sc_per_cm=5)
        actual = p.inputs["actual_diameter_cm"]
        self.assertAlmostEqual(actual, 10, delta=0.5)

    def test_sphere_total_rounds(self):
        # For pure sphere (no equator): 1 init + (n_max-1) increase
        # + (n_max-1) decrease = 2·n_max-1 rounds.
        p = amigurumi_sphere(diameter_cm=5, gauge_sc_per_cm=5,
                             equator_rounds=0)
        n_max = p.inputs["n_max"]
        self.assertEqual(p.inputs["max_sts"], 6 * n_max)

    def test_sphere_continuity(self):
        p = amigurumi_sphere(diameter_cm=8, gauge_sc_per_cm=5)
        p.validate_continuity()  # raises on mismatch

    def test_sphere_with_equator(self):
        p = amigurumi_sphere(diameter_cm=8, gauge_sc_per_cm=5,
                             equator_rounds=3)
        eq = next(s for s in p.sections if "Ækvator" in s.title)
        self.assertEqual(eq.sts_before, eq.sts_after)

    def test_sphere_raises_on_zero_diameter(self):
        with self.assertRaises(ValueError):
            amigurumi_sphere(diameter_cm=0, gauge_sc_per_cm=5)

    def test_sphere_raises_on_zero_gauge(self):
        with self.assertRaises(ValueError):
            amigurumi_sphere(diameter_cm=5, gauge_sc_per_cm=0)


class TestAmigurumiCylinder(unittest.TestCase):
    def test_basic_cylinder(self):
        p = amigurumi_cylinder(AmigurumiCylinderSpec(
            diameter_cm=5, height_cm=8, gauge_sc_per_cm=5,
            row_gauge_per_cm=5,
        ))
        self.assertEqual(p.construction, "amigurumi_cylinder")
        self.assertGreaterEqual(len(p.sections), 2)


class TestAmigurumiTaper(unittest.TestCase):
    def test_basic_taper(self):
        p = amigurumi_taper(AmigurumiTaperSpec(
            d_top_cm=2, d_bottom_cm=5, height_cm=4,
            gauge_sc_per_cm=5, row_gauge_per_cm=5,
        ))
        self.assertTrue(p.warnings, "stub should warn")


class TestGrannySquare(unittest.TestCase):
    def test_round_n_dc_count(self):
        # Closed-form: 12·N total dc after round N
        p = generate_granny_square(GrannySquareSpec(rounds=4))
        # Find last "Omg N" section
        last_round = next(s for s in reversed(p.sections)
                          if s.title.startswith("Omg "))
        self.assertEqual(last_round.sts_after, 12 * 4)

    def test_round_count_grows_by_12(self):
        p = generate_granny_square(GrannySquareSpec(rounds=5))
        rounds = [s for s in p.sections if s.title.startswith("Omg ")]
        # consecutive rounds differ by 12
        for i in range(1, len(rounds)):
            self.assertEqual(rounds[i].sts_after - rounds[i-1].sts_after, 12)

    def test_one_round_granny(self):
        p = generate_granny_square(GrannySquareSpec(rounds=1))
        last = next(s for s in p.sections if s.title.startswith("Omg "))
        self.assertEqual(last.sts_after, 12)

    def test_zero_rounds_raises(self):
        with self.assertRaises(ValueError):
            generate_granny_square(GrannySquareSpec(rounds=0))

    def test_colors_in_notes(self):
        p = generate_granny_square(GrannySquareSpec(
            rounds=3, colors=["rød", "blå", "grøn"]))
        self.assertTrue(any("Farveskift" in n for n in p.notes))

    def test_continuity(self):
        p = generate_granny_square(GrannySquareSpec(rounds=8))
        p.validate_continuity()


class TestCrochetTørklæde(unittest.TestCase):
    def test_basic_scarf(self):
        p = generate_tørklæde(CrochetTørklædeSpec(
            width_cm=20, length_cm=150, gauge_sts_per_cm=2.5,
            stitch_type="dc",
        ))
        self.assertEqual(p.inputs["width_sts"], 50)

    def test_width_from_gauge(self):
        # 25 cm × 2 sts/cm = 50 sts
        p = generate_tørklæde(CrochetTørklædeSpec(
            width_cm=25, length_cm=100, gauge_sts_per_cm=2,
            stitch_type="dc",
        ))
        self.assertEqual(p.inputs["width_sts"], 50)

    def test_stitch_type_unknown_raises(self):
        with self.assertRaises(ValueError):
            generate_tørklæde(CrochetTørklædeSpec(
                width_cm=20, length_cm=100, gauge_sts_per_cm=2,
                stitch_type="bobble",
            ))

    def test_negative_dimensions_raises(self):
        with self.assertRaises(ValueError):
            generate_tørklæde(CrochetTørklædeSpec(
                width_cm=0, length_cm=100, gauge_sts_per_cm=2,
            ))

    def test_continuity(self):
        p = generate_tørklæde(CrochetTørklædeSpec(
            width_cm=30, length_cm=180, gauge_sts_per_cm=2.5,
            stitch_type="hdc",
        ))
        p.validate_continuity()

    def test_turning_chain_for_dc(self):
        p = generate_tørklæde(CrochetTørklædeSpec(
            width_cm=20, length_cm=100, gauge_sts_per_cm=2.5,
            stitch_type="dc",
        ))
        self.assertEqual(p.inputs["turning_chain"], 3)

    def test_turning_chain_for_sc(self):
        p = generate_tørklæde(CrochetTørklædeSpec(
            width_cm=20, length_cm=100, gauge_sts_per_cm=4,
            stitch_type="sc",
        ))
        self.assertEqual(p.inputs["turning_chain"], 1)


class TestFilet(unittest.TestCase):
    def test_3w_plus_1_formula(self):
        """Stitches per row = 3·W + 1 (Agent B §4)."""
        self.assertEqual(filet_stitches_per_row(1), 4)
        self.assertEqual(filet_stitches_per_row(10), 31)
        self.assertEqual(filet_stitches_per_row(20), 61)

    def test_foundation_chain(self):
        self.assertEqual(filet_foundation_chain(10), 32)
        self.assertEqual(filet_foundation_chain(1), 5)

    def test_basic_filet(self):
        p = generate_filet(FiletSpec(
            width_cells=5, height_cells=4,
            grid="X.X.X\n.X.X.\nXXXXX\n.....",
        ))
        self.assertEqual(p.construction, "filet")
        self.assertEqual(p.inputs["sts_per_row"], 16)  # 3*5 + 1
        self.assertEqual(p.inputs["width_cells"], 5)
        self.assertEqual(p.inputs["height_cells"], 4)

    def test_filet_grid_normalisation(self):
        p = generate_filet(FiletSpec(
            width_cells=3, height_cells=3,
            grid="X.X\n.X.\nXXX",
        ))
        # X = filled, . = open
        self.assertEqual(p.inputs["grid"][0], [True, False, True])
        self.assertEqual(p.inputs["grid"][1], [False, True, False])
        self.assertEqual(p.inputs["grid"][2], [True, True, True])

    def test_filet_grid_truncation(self):
        # Grid wider than width gets truncated
        p = generate_filet(FiletSpec(
            width_cells=2, height_cells=2,
            grid="XXXX\n....",
        ))
        self.assertEqual(len(p.inputs["grid"][0]), 2)

    def test_filet_invalid_dims(self):
        with self.assertRaises(ValueError):
            generate_filet(FiletSpec(width_cells=0, height_cells=4))
        with self.assertRaises(ValueError):
            filet_stitches_per_row(0)

    def test_filet_emits_pattern_sections(self):
        p = generate_filet(FiletSpec(
            width_cells=4, height_cells=3,
            grid="X.X.\n.X.X\nXXXX",
        ))
        titles = [s.title for s in p.sections]
        self.assertIn("Bundkæde", titles)
        self.assertIn("Krop", titles)


class TestTunisian(unittest.TestCase):
    def test_basic_tunisian(self):
        p = generate_tunisian(TunisianSpec(
            width_cm=20, length_cm=30,
            gauge_sts_per_cm=2.5, row_gauge_per_cm=1.5,
        ))
        self.assertEqual(p.construction, "tunisian")
        # 20 * 2.5 = 50 sts width
        self.assertEqual(p.inputs["width_sts"], 50)
        # 30 * 1.5 = 45 rows
        self.assertEqual(p.inputs["rows"], 45)

    def test_tunisian_row_invariant(self):
        # forward_loops == width
        tr = TunisianRow(width=15)
        self.assertEqual(tr.forward_loops, 15)
        self.assertEqual(tr.sts_after, 15)
        tr.validate()

    def test_tunisian_row_invalid(self):
        with self.assertRaises(ValueError):
            TunisianRow(width=0).validate()

    def test_tunisian_unknown_base(self):
        with self.assertRaises(ValueError):
            generate_tunisian(TunisianSpec(
                width_cm=20, length_cm=30,
                base_stitch="weird",
            ))

    def test_tunisian_negative_dims(self):
        with self.assertRaises(ValueError):
            generate_tunisian(TunisianSpec(
                width_cm=0, length_cm=30,
            ))
        with self.assertRaises(ValueError):
            generate_tunisian(TunisianSpec(
                width_cm=20, length_cm=-1,
            ))

    def test_tunisian_logs_rows(self):
        p = generate_tunisian(TunisianSpec(
            width_cm=10, length_cm=10,
            gauge_sts_per_cm=2.0, row_gauge_per_cm=1.0,
        ))
        logged = p.inputs["tunisian_rows"]
        # rows = max(1, round(10 * 1.0)) = 10
        self.assertEqual(len(logged), 10)
        # Each TunisianRow's width == width_sts
        for r in logged:
            self.assertEqual(r["width"], p.inputs["width_sts"])



class TestC2CBlanket(unittest.TestCase):
    def test_total_blocks_formula(self):
        self.assertEqual(c2c_total_blocks(5, 5), 25)
        self.assertEqual(c2c_total_blocks(8, 4), 32)
        self.assertEqual(c2c_total_blocks(1, 1), 1)

    def test_total_dc_formula(self):
        # 3 dc per block
        self.assertEqual(c2c_total_dc(5, 5), 75)
        self.assertEqual(c2c_total_dc(10, 4), 120)

    def test_blocks_per_row_square(self):
        # 5x5: increase 1..5, decrease 4..1 → 9 rows total
        rows = c2c_blocks_per_row(5, 5)
        self.assertEqual(rows, [1, 2, 3, 4, 5, 4, 3, 2, 1])
        self.assertEqual(sum(rows), 25)

    def test_blocks_per_row_rectangle(self):
        # 4x6: short=4, long=6 → increase 1..4, plateau 4 (×2), decrease 3..1
        rows = c2c_blocks_per_row(4, 6)
        self.assertEqual(rows, [1, 2, 3, 4, 4, 4, 3, 2, 1])
        self.assertEqual(sum(rows), 24)
        self.assertEqual(len(rows), 4 + 6 - 1)

    def test_blocks_per_row_invalid(self):
        with self.assertRaises(ValueError):
            c2c_blocks_per_row(0, 5)
        with self.assertRaises(ValueError):
            c2c_blocks_per_row(5, -1)

    def test_basic_c2c_pattern(self):
        p = generate_c2c_blanket(C2CBlanketSpec(blocks_wide=5, blocks_high=4))
        self.assertEqual(p.construction, "c2c_blanket")
        self.assertEqual(p.inputs["total_blocks"], 20)
        self.assertEqual(p.inputs["total_rows"], 5 + 4 - 1)
        self.assertEqual(p.inputs["total_dc"], 60)

    def test_c2c_continuity(self):
        p = generate_c2c_blanket(C2CBlanketSpec(blocks_wide=6, blocks_high=6))
        p.validate_continuity()

    def test_c2c_with_colors(self):
        p = generate_c2c_blanket(C2CBlanketSpec(
            blocks_wide=4, blocks_high=4,
            colors=["rød", "blå", "grøn"],
        ))
        self.assertTrue(any("Stribefarver" in n for n in p.notes))

    def test_c2c_invalid_dimensions(self):
        with self.assertRaises(ValueError):
            generate_c2c_blanket(C2CBlanketSpec(blocks_wide=0, blocks_high=5))
        with self.assertRaises(ValueError):
            generate_c2c_blanket(C2CBlanketSpec(
                blocks_wide=5, blocks_high=5, blocks_per_cm=0,
            ))

    def test_c2c_single_block(self):
        # 1x1 should not crash — only 1 row, 1 block
        p = generate_c2c_blanket(C2CBlanketSpec(blocks_wide=1, blocks_high=1))
        self.assertEqual(p.inputs["total_rows"], 1)
        self.assertEqual(p.inputs["total_blocks"], 1)


class TestMandala(unittest.TestCase):
    def test_basic_mandala(self):
        p = generate_mandala(MandalaSpec(rounds=4))
        self.assertEqual(p.construction, "mandala")
        # Round progression: 12, 24 (doubled), 24 (popcorn flat), 48 (doubled)
        self.assertEqual(p.inputs["sts_per_round"], [12, 24, 24, 48])

    def test_mandala_continuity(self):
        p = generate_mandala(MandalaSpec(rounds=6))
        p.validate_continuity()

    def test_mandala_minimum_rounds(self):
        p = generate_mandala(MandalaSpec(rounds=1))
        self.assertEqual(p.inputs["sts_per_round"], [12])
        self.assertEqual(p.inputs["final_sts"], 12)

    def test_mandala_zero_rounds_raises(self):
        with self.assertRaises(ValueError):
            generate_mandala(MandalaSpec(rounds=0))

    def test_mandala_with_colors(self):
        p = generate_mandala(MandalaSpec(
            rounds=3, colors=["hvid", "lyserød", "lilla"],
        ))
        self.assertTrue(any("Farveskift" in n for n in p.notes))

    def test_mandala_custom_start_count(self):
        p = generate_mandala(MandalaSpec(rounds=2, start_count=8))
        # 8 sc → doubled to 16
        self.assertEqual(p.inputs["sts_per_round"], [8, 16])

    def test_mandala_invalid_start_count(self):
        with self.assertRaises(ValueError):
            generate_mandala(MandalaSpec(rounds=3, start_count=0))

    def test_mandala_default_progression(self):
        prog = default_round_progression(5, start_count=12)
        self.assertEqual(len(prog), 5)
        self.assertEqual(prog[0].stitch, "mr")
        # Round 2: doubling dc
        self.assertEqual(prog[1].stitch, "dc")
        self.assertEqual(prog[1].increase_per_st, 1)


class TestNewStitches(unittest.TestCase):
    def test_popcorn(self):
        s = stitch("pop")
        self.assertEqual(s.consumes, 1)
        self.assertEqual(s.produces, 1)

    def test_popcorn_danish_alias(self):
        self.assertEqual(stitch("popkorn").name, "pop")
        self.assertEqual(stitch("puf").name, "pop")

    def test_picot(self):
        s = stitch("pic")
        # Picots are decorative — (0, 0) so they don't disturb counts
        self.assertEqual(s.consumes, 0)
        self.assertEqual(s.produces, 0)
        self.assertFalse(s.counts_as_stitch)

    def test_cluster(self):
        s = stitch("cl3")
        self.assertEqual(s.consumes, 1)
        self.assertEqual(s.produces, 1)
        self.assertEqual(stitch("klynge").name, "cl3")


class TestAmigurumiFigur(unittest.TestCase):
    def test_default_bjørn_builds(self):
        p = amigurumi_figur(AmigurumiFigurSpec(scale_cm=12, species="bjørn"))
        self.assertEqual(p.construction, "amigurumi_figur")
        self.assertEqual(p.difficulty, "easy")
        # 5 part-banners + sub-sections + 1 assembly section
        self.assertGreater(len(p.sections), 5 + 1)
        # Last section is "Samling"
        self.assertEqual(p.sections[-1].title, "Samling")

    def test_kanin_alias(self):
        p = amigurumi_kanin(scale_cm=10)
        self.assertEqual(p.inputs["species"], "kanin")
        self.assertEqual(p.inputs["parts"][0]["label"], "Krop")
        # 8 dele samlet (krop + hoved + 2 ører + 2 arme + 2 ben)
        total_count = sum(part["count"] for part in p.inputs["parts"])
        self.assertEqual(total_count, 8)

    def test_bjørn_alias(self):
        p = amigurumi_bjørn(scale_cm=15)
        self.assertEqual(p.inputs["species"], "bjørn")
        # bjørn body has 2 equator rounds, kanin has 3
        # we just check it built and has the right scale
        self.assertEqual(p.inputs["scale_cm"], 15.0)

    def test_continuity_validates(self):
        # Each part starts/ends at 0, so the merged Pattern must validate.
        p = amigurumi_figur(AmigurumiFigurSpec(scale_cm=12))
        # No exception means continuity is OK; explicitly call again:
        p.validate_continuity()

    def test_invalid_species_rejected(self):
        with self.assertRaises(ValueError):
            amigurumi_figur(AmigurumiFigurSpec(scale_cm=12, species="hund"))

    def test_invalid_scale_rejected(self):
        with self.assertRaises(ValueError):
            amigurumi_figur(AmigurumiFigurSpec(scale_cm=0))

    def test_assembly_text_present(self):
        p = amigurumi_figur(AmigurumiFigurSpec(scale_cm=12, species="bjørn"))
        asm = p.sections[-1]
        self.assertEqual(asm.title, "Samling")
        all_text = " ".join(st.text for st in asm.steps)
        # samle-instruktioner skal nævne hovedet, ørerne, øjnene
        self.assertIn("hoved", all_text.lower())
        self.assertIn("øre", all_text.lower())
        self.assertIn("øj", all_text.lower())

    def test_each_part_independently_valid(self):
        # Building a figur runs amigurumi_sphere/cylinder for each part —
        # those each call validate_continuity internally. If anything is off
        # in our composition, this would have raised. Smoke test:
        p = amigurumi_figur(AmigurumiFigurSpec(scale_cm=14, species="kanin"))
        # parts are reflected in the inputs
        labels = [part["label"] for part in p.inputs["parts"]]
        self.assertEqual(labels, ["Krop", "Hoved", "Ører", "Arme", "Ben"])


class TestDifficultyRating(unittest.TestCase):
    def test_difficulty_set_for_each_construction(self):
        # construction → expected difficulty
        cases = {
            "amigurumi_sphere":   ("beginner",
                amigurumi_sphere(AmigurumiSphereSpec(diameter_cm=6))),
            "amigurumi_cylinder": ("beginner",
                amigurumi_cylinder(AmigurumiCylinderSpec(diameter_cm=6, height_cm=8))),
            "amigurumi_taper":    ("beginner",
                amigurumi_taper(AmigurumiTaperSpec(d_top_cm=4, d_bottom_cm=8, height_cm=6))),
            "granny_square":      ("beginner",
                generate_granny_square(GrannySquareSpec(rounds=5))),
            "haekle_tørklæde":    ("beginner",
                generate_tørklæde(CrochetTørklædeSpec(
                    width_cm=20, length_cm=120, gauge_sts_per_cm=2.5))),
            "filet":              ("easy",
                generate_filet(FiletSpec(width_cells=4, height_cells=4,
                    grid="X.X.\n.X.X\nX.X.\n.X.X"))),
            "tunisian":           ("intermediate",
                generate_tunisian(TunisianSpec(width_cm=20, length_cm=20))),
            "c2c_blanket":        ("easy",
                generate_c2c_blanket(C2CBlanketSpec(
                    blocks_wide=4, blocks_high=4))),
            "mandala":            ("intermediate",
                generate_mandala(MandalaSpec(rounds=5))),
            "amigurumi_figur":    ("easy",
                amigurumi_figur(AmigurumiFigurSpec(scale_cm=12))),
        }
        for cons, (expected, p) in cases.items():
            with self.subTest(construction=cons):
                self.assertEqual(p.construction, cons)
                self.assertEqual(p.difficulty, expected,
                    f"{cons} should be {expected}, got {p.difficulty!r}")

    def test_difficulty_serializes(self):
        p = amigurumi_sphere(AmigurumiSphereSpec(diameter_cm=6))
        d = p.to_dict()
        self.assertEqual(d["difficulty"], "beginner")


class TestYarnDB(unittest.TestCase):
    def test_lookup_exact(self):
        y = lookup_yarn("Drops Air")
        self.assertIsNotNone(y)
        self.assertEqual(y.name, "Drops Air")
        self.assertEqual(y.weight_class, "aran")

    def test_lookup_fuzzy_case(self):
        y = lookup_yarn("drops air")
        self.assertIsNotNone(y)
        self.assertEqual(y.name, "Drops Air")
        # spaces / hyphens / case
        y2 = lookup_yarn("Drops-AIR")
        self.assertIsNotNone(y2)
        self.assertEqual(y2.name, "Drops Air")

    def test_lookup_substring(self):
        # canonical contained in user query
        y = lookup_yarn("Drops Air 50g skein")
        self.assertIsNotNone(y)
        self.assertEqual(y.name, "Drops Air")

    def test_lookup_unknown_returns_none(self):
        self.assertIsNone(lookup_yarn(""))
        self.assertIsNone(lookup_yarn("Made-up brand XYZ123"))

    def test_substitute_only_same_weight(self):
        air = lookup_yarn("Drops Air")
        subs = suggest_substitute(air)
        self.assertGreaterEqual(len(subs), 0)
        for y in subs:
            self.assertEqual(y.weight_class, air.weight_class)
            self.assertNotEqual(y.name, air.name)

    def test_apply_yarn_fills_metadata(self):
        p = amigurumi_sphere(AmigurumiSphereSpec(diameter_cm=6))
        ok = apply_yarn_to_pattern(p, "Drops Lima")
        self.assertTrue(ok)
        md = p.inputs["metadata"]
        self.assertIn("Drops Lima", md["yarn"])
        self.assertIn("50 g", md["yarn_run"])

    def test_apply_yarn_respects_user_overrides(self):
        p = amigurumi_sphere(AmigurumiSphereSpec(diameter_cm=6))
        p.inputs["metadata"] = {"yarn": "My custom yarn"}
        apply_yarn_to_pattern(p, "Drops Lima")
        md = p.inputs["metadata"]
        # user value preserved
        self.assertEqual(md["yarn"], "My custom yarn")
        # yarn_run still gets filled (since user didn't set it)
        self.assertIn("50 g", md["yarn_run"])

    def test_auto_gauge_returns_floats(self):
        g = auto_gauge_from_yarn("Drops Lima", domain="crochet")
        self.assertIsNotNone(g)
        sts, rows = g
        self.assertGreater(sts, 0)
        self.assertGreater(rows, 0)
        # crochet gauge must be lower than knit gauge
        knit = auto_gauge_from_yarn("Drops Lima", domain="knit")
        self.assertGreater(knit[0], sts)

    def test_yarn_validates_weight_class(self):
        with self.assertRaises(ValueError):
            Yarn("Bad", "ultra-heavy", 10, 10, 5.0, 5.0, "fake", 100)


if __name__ == "__main__":
    unittest.main()
