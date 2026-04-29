"""Tests for CLI flag-aliases (Danish ↔ English).

Verifies that:

1. The argparse parsers accept both the English primary flag-name and the
   Danish alias for technical inputs (and the new English aliases for the
   Danish-primary materials flags).
2. Existing flag-name fixtures (the README quick-start examples) still work
   without modification — backwards compatibility.
3. End-to-end via subprocess: invoking the CLI with old vs new flag-names
   produces structurally identical JSON output.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
_KNIT_GENERATE = _REPO / "skills" / "strikning" / "scripts" / "generate.py"
_CROCHET_GENERATE = _REPO / "skills" / "hækling" / "scripts" / "generate.py"


def _load_module(name: str, path: Path):
    """Import a generate.py file as a uniquely-named module so we can
    exercise its `argparse` parser without spawning a subprocess. We
    monkey-patch ``sys.argv`` and call ``main`` indirectly via parser
    construction; here we re-create the parser by extracting the logic.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Make sure the same sys.path tweaks as the real CLI run.
    sys.path.insert(0, str(_REPO))
    sys.path.insert(0, str(path.parent.parent))  # skill root
    spec.loader.exec_module(mod)
    return mod


class KnitFlagAliasTests(unittest.TestCase):
    """Verify Danish + English aliases land on the same argparse `dest`."""

    @classmethod
    def setUpClass(cls):
        # Replace any previously-imported module: knit and crochet share
        # constructions imports under different package names so naming
        # collisions are unlikely, but we use unique names anyway.
        cls.knit = _load_module("_knit_generate_for_flagtest", _KNIT_GENERATE)

    def _parse(self, argv: list[str]):
        # We rebuild the parser by calling main() with --help suppressed is
        # awkward; instead we inline-build by invoking the public function.
        # Easier: import the parser-building code by duplicating the parser
        # via the module's `main` after we monkey-patch sys.argv. To avoid
        # main()'s side effects (which writes to stdout and returns int)
        # we'll instead use subprocess for end-to-end and use direct argparse
        # checks via a tiny helper that parses without executing.
        raise NotImplementedError  # only used by smoke tests below

    def test_hue_head_aliases_same_dest(self):
        # Build a parser locally that mirrors the real one for `hue`:
        # the real generate.py's main() builds the parser, but we cannot
        # call main() without it executing. Instead we run it as subprocess.
        out_old = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "json", "hue",
             "--head", "56", "--sts", "22", "--rows", "30"]
        )
        out_new = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "json", "hue",
             "--hovedmål", "56", "--sts", "22", "--row-gauge", "30"]
        )
        d_old = json.loads(out_old)
        d_new = json.loads(out_new)
        self.assertEqual(
            d_old["inputs"]["head_circumference_cm"],
            d_new["inputs"]["head_circumference_cm"],
        )
        self.assertEqual(
            d_old["inputs"]["gauge"],
            d_new["inputs"]["gauge"],
        )

    def test_hue_height_danish_alias(self):
        out = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "json", "hue",
             "--head", "56", "--sts", "22", "--rows", "30",
             "--højde", "23"]
        )
        d = json.loads(out)
        self.assertEqual(d["inputs"]["total_height_cm"], 23.0)

    def test_sokker_danish_aliases(self):
        out = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "json", "sokker",
             "--fod", "22", "--fodlængde", "24", "--sts", "28", "--rows", "36",
             "--skostørrelse", "EU 38"]
        )
        d = json.loads(out)
        # Constructions accept these via the spec; the generator forwards
        # them. We just need to verify the CLI parsed without error.
        self.assertEqual(d["construction"], "sokker")

    def test_raglan_danish_aliases(self):
        out = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "json", "raglan",
             "--bryst", "94", "--sts", "22", "--rows", "30",
             "--hals", "42", "--overarm", "31", "--håndled", "18",
             "--ærme", "45", "--yokedybde", "23", "--kropslængde", "36"]
        )
        d = json.loads(out)
        self.assertEqual(d["construction"], "raglan_topdown")

    def test_lace_danish_width_length_aliases(self):
        out = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "json", "lace",
             "--bredde", "60", "--længde", "180",
             "--sts", "20", "--rows", "26"]
        )
        d = json.loads(out)
        self.assertEqual(d["construction"], "lace_shawl")

    def test_materials_english_aliases_knit(self):
        out = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "json", "hue",
             "--head", "56", "--sts", "22", "--rows", "30",
             "--yarn", "Drops Air", "--yarn-run", "150m/50g",
             "--needles", "4 mm", "--year", "2026", "--notes", "test"]
        )
        d = json.loads(out)
        md = d["inputs"]["metadata"]
        self.assertEqual(md["yarn"], "Drops Air")
        self.assertEqual(md["yarn_run"], "150m/50g")
        self.assertEqual(md["needles"], "4 mm")
        self.assertEqual(md["year"], 2026)
        self.assertEqual(md["notes"], ["test"])


class CrochetFlagAliasTests(unittest.TestCase):

    def test_filet_danish_aliases(self):
        out = subprocess.check_output(
            [sys.executable, str(_CROCHET_GENERATE), "--format", "json",
             "filet", "--bredde", "12", "--højde", "12",
             "--gauge", "2", "--row-gauge", "0.5"]
        )
        d = json.loads(out)
        self.assertEqual(d["inputs"]["width_cells"], 12)
        self.assertEqual(d["inputs"]["height_cells"], 12)

    def test_tørklæde_danish_aliases_crochet(self):
        out = subprocess.check_output(
            [sys.executable, str(_CROCHET_GENERATE), "--format", "json",
             "tørklæde", "--bredde", "25", "--længde", "150",
             "--gauge", "2.5"]
        )
        d = json.loads(out)
        self.assertEqual(d["construction"], "haekle_tørklæde")

    def test_materials_english_aliases_crochet(self):
        out = subprocess.check_output(
            [sys.executable, str(_CROCHET_GENERATE), "--format", "json",
             "amigurumi", "--diameter", "8", "--gauge", "5",
             "--yarn", "Drops Lima", "--hook", "4 mm",
             "--yarn-run", "100m/50g"]
        )
        d = json.loads(out)
        md = d["inputs"]["metadata"]
        self.assertIn("Drops Lima", md["yarn"])
        self.assertEqual(md["hook"], "4 mm")
        self.assertEqual(md["yarn_run"], "100m/50g")


class BackwardsCompatTests(unittest.TestCase):
    """The exact flag-strings used in the README quick-start must keep working."""

    def test_readme_hue_old_flags(self):
        out = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "md", "hue",
             "--head", "56", "--sts", "22", "--rows", "30"]
        )
        self.assertIn(b"Hue", out)

    def test_readme_amigurumi_old_flags(self):
        out = subprocess.check_output(
            [sys.executable, str(_CROCHET_GENERATE), "--format", "md",
             "amigurumi", "--diameter", "8", "--garn", "Drops Air"]
        )
        self.assertIn(b"Amigurumi", out)

    def test_old_garn_flag_still_works(self):
        # --garn is still primary; we only added --yarn as an alias.
        out = subprocess.check_output(
            [sys.executable, str(_KNIT_GENERATE), "--format", "json", "hue",
             "--head", "56", "--sts", "22", "--rows", "30",
             "--garn", "Drops Air"]
        )
        d = json.loads(out)
        self.assertEqual(d["inputs"]["metadata"]["yarn"], "Drops Air")


class CLIEquivalenceTests(unittest.TestCase):
    """End-to-end smoke: old + new flag combos should yield equivalent output."""

    def _run_json(self, argv: list[str]) -> dict:
        out = subprocess.check_output(
            [sys.executable, *argv]
        )
        return json.loads(out)

    def test_hue_old_vs_new_equivalence(self):
        old = self._run_json([
            str(_KNIT_GENERATE), "--format", "json", "hue",
            "--head", "56", "--sts", "22", "--rows", "30"])
        new = self._run_json([
            str(_KNIT_GENERATE), "--format", "json", "hue",
            "--hovedmål", "56", "--sts", "22", "--row-gauge", "30"])
        self.assertEqual(old["sections"], new["sections"])

    def test_filet_old_vs_new_equivalence(self):
        old = self._run_json([
            str(_CROCHET_GENERATE), "--format", "json", "filet",
            "--width", "10", "--height", "10", "--gauge", "2"])
        new = self._run_json([
            str(_CROCHET_GENERATE), "--format", "json", "filet",
            "--bredde", "10", "--højde", "10", "--gauge", "2"])
        self.assertEqual(old["sections"], new["sections"])

    def test_materials_garn_vs_yarn_equivalence(self):
        old = self._run_json([
            str(_KNIT_GENERATE), "--format", "json", "hue",
            "--head", "56", "--sts", "22", "--rows", "30",
            "--garn", "Drops Air"])
        new = self._run_json([
            str(_KNIT_GENERATE), "--format", "json", "hue",
            "--head", "56", "--sts", "22", "--rows", "30",
            "--yarn", "Drops Air"])
        self.assertEqual(
            old["inputs"]["metadata"], new["inputs"]["metadata"])


if __name__ == "__main__":
    unittest.main()
