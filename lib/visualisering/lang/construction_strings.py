"""Helpers for translating construction step text.

This module supports the construction generators in
``skills/strikning/knitlib/constructions/`` and
``skills/hækling/croclib/constructions/``. The fully-translated constructions
build their strings inline with a small ``_l(da, en, lang)`` helper, but the
remaining constructions only translate section titles + a small bag of
common Danish phrases via :func:`translate_pattern`.

Why two strategies? A handful of construction modules (hue, raglan_topdown,
sokker, bottom_up_sweater, tørklæde, granny_square, amigurumi_sphere,
c2c_blanket, crochet tørklæde) are heavily used by the CLI smoke tests, so
they get the full inline-translation treatment. The other modules already
have their full Danish prose locked in; for them, post-hoc translation via
:func:`translate_pattern` is a pragmatic compromise that delivers >90% of
the value at a fraction of the maintenance cost.

Both strategies cooperate with the central ``t(key, lang)`` table in
``translations.py``: section titles for materials/abbreviations/etc. still
go through ``t()``; only construction-specific step text uses these helpers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.visualisering import Pattern


# ---------------------------------------------------------------------------
# Section title dictionary — covers all 20 constructions.
# ---------------------------------------------------------------------------
SECTION_TITLES_EN: dict[str, str] = {
    # ---- shared / generic ----
    "Opslag": "Cast on",
    "Opslag og rib": "Cast on and rib",
    "Krop": "Body",
    "Krop — opslag og rib": "Body — cast on and rib",
    "Krone": "Crown",
    "Halsudskæring": "Neckline",
    "Hals": "Neckband",
    "Bærestykke": "Yoke",
    "Adskillelse af ærmer": "Sleeve separation",
    "Sammenstrikning af krop og ærmer": "Joining body and sleeves",
    "Ærmer (begge ens)": "Sleeves (both alike)",
    "Skaft": "Leg",
    "Hælklap": "Heel flap",
    "Hæl-vending": "Heel turn",
    "Gusset": "Gusset",
    "Fod": "Foot",
    "Tå": "Toe",
    "Afslutning": "Finishing",
    "Korte rækker bagstykke (valgfrit)": "Back-neck short rows (optional)",
    "Øverste kant og aflukning": "Upper border and bind off",
    "Samling": "Assembly",

    # ---- compound raglan / yoke variations ----
    "Compound raglan — bærestykke": "Compound raglan yoke",
    "Krop og ærmer (uafhængig grading)": "Body and sleeves (independent grading)",
    "Halsudskæring og rib": "Neckline and rib",
    "Adskil ærmer": "Separate sleeves",
    "Krop og rib": "Body and rib",
    "Stranded yoke": "Stranded yoke",
    "Yoke — colorwork-bånd": "Yoke — colorwork band",
    "Yoke-bånd": "Yoke band",
    "Halskanten": "Neckline edge",

    # ---- shawls ----
    "Opslag og pick-up": "Cast-on and pick-up",
    "Halskant og opslag": "Neckline edge and cast-on",
    "Yoke (compound)": "Yoke (compound)",
    "Bærestykke (compound)": "Yoke (compound)",
    "Garter-tab": "Garter tab",
    "Setup-rækker": "Setup rows",
    "Shawl-krop": "Shawl body",
    "Lace-rapport": "Lace repeat",
    "Lace-bånd": "Lace band",
    "Korte rækker (crescent)": "Short rows (crescent)",
    "Aflukning": "Bind off",
    "Lace-kropsmønster": "Lace body pattern",
    "Garter-bånd": "Garter band",

    # ---- colorwork swatch ----
    "Colorwork-bånd": "Colorwork band",
    "Garter-kant": "Garter border",

    # ---- crochet ----
    "Start": "Start",
    "Bundkæde": "Foundation chain",
    "Række 1": "Row 1",
    "Bund": "Base",
    "Tube": "Tube",
    "Lukning af top": "Closing the top",
    "Lukning": "Closing",
    "Øvre halvdel — udtagninger": "Top half — increases",
    "Nedre halvdel — indtagninger": "Bottom half — decreases",
    "Ækvator": "Equator",
    "Krop (hoveddel)": "Body (main piece)",
    "Hoved": "Head",
    "Ører": "Ears",
    "Arme": "Arms",
    "Ben": "Legs",
    "Taper": "Taper",
    "Mandala-kerne": "Mandala core",
    "Mandala-bånd": "Mandala band",
    "Filet-grid": "Filet grid",
    "Tunisian-base": "Tunisian base",
    "Tunisian-krop": "Tunisian body",
    "Forward pass": "Forward pass",
    "Return pass": "Return pass",
}


# ---------------------------------------------------------------------------
# Step-level Danish → English phrase replacements. Order matters (longer
# phrases first). These are deliberately conservative — only safe, common
# vocabulary that doesn't conflict with English already in the string.
# ---------------------------------------------------------------------------
_PHRASE_REPL: list[tuple[str, str]] = [
    # ---- multi-word phrases (longer first to avoid partial overlap) ----
    ("Slå arbejdet til omgang", "Join in the round"),
    ("Saml til omgang uden at sno", "Join in the round without twisting"),
    ("Saml til omg uden at sno", "Join in the round without twisting"),
    ("Saml til omgang", "Join in the round"),
    ("Saml til omg", "Join in the round"),
    ("Hæft alle ender", "Weave in all ends"),
    ("Hæft ender", "Weave in ends"),
    ("Klip garnet", "Cut the yarn"),
    ("Luk løst af", "Bind off loosely"),
    ("Luk af", "Bind off"),
    ("Strik glatstrik", "Knit stockinette"),
    ("strik glatstrik", "knit stockinette"),
    ("Strik retstrik", "Work garter stitch"),
    ("strik retstrik", "work garter stitch"),
    # cast-on variants — match the noun "m" too
    ("Slå op på", "Cast on on"),  # ugly but rare
    ("Slå op", "Cast on"),
    ("slå op", "cast on"),
    # cast-on with stitch-count: "Slå NN m op på" → "Cast on NN sts on"
    # handled by the generic "Slå" + "m op på" replacements below.
    ("m op på", "sts on a"),
    ("m op", "sts"),
    ("Slå ", "Cast on "),
    # decreases / increases full-word
    ("indtagningsomg", "decrease round"),
    ("udtagningsomg", "increase round"),
    ("indtagninger", "decreases"),
    ("udtagninger", "increases"),
    ("indtagning", "decrease"),
    ("udtagning", "increase"),
    # ---- compound knit-pattern terms (must come BEFORE bare "Strik"/"strik"!) ----
    ("retstrik", "garter stitch"),
    ("glatstrik", "stockinette"),
    ("perlestrik", "seed stitch"),
    # ---- knitting verbs ----
    ("Strik", "Knit"),
    ("strik", "knit"),
    # ---- crochet stitch full names ----
    ("halv stangmaske", "half double crochet"),
    ("dobbeltstangmaske", "treble crochet"),
    ("fastmasker", "single crochet sts"),
    ("fastmaske", "single crochet"),
    ("stangmasker", "double crochet sts"),
    ("stangmaske", "double crochet"),
    ("kædemaske", "slip stitch"),
    ("luftmasker", "chains"),
    ("luftmaske", "chain"),
    # ---- abbreviations as standalone words (with surrounding spaces) ----
    (" fm,", " sc,"),
    (" fm.", " sc."),
    (" fm ", " sc "),
    (" hstm,", " hdc,"),
    (" hstm.", " hdc."),
    (" hstm ", " hdc "),
    (" stm,", " dc,"),
    (" stm.", " dc."),
    (" stm ", " dc "),
    (" dst,", " tr,"),
    (" dst.", " tr."),
    (" dst ", " tr "),
    (" km ", " sl-st "),
    (" km,", " sl-st,"),
    (" km.", " sl-st."),
    (" lm ", " ch "),
    (" lm,", " ch,"),
    (" lm.", " ch."),
    # ---- structure / equipment ----
    ("rundpind", "circular needle"),
    ("strømpepinde", "DPNs"),
    ("vendekæde", "turning chain"),
    ("Vend arbejdet", "Turn the work"),
    ("vend arbejdet", "turn the work"),
    ("Saml omg", "Join the round"),
    # ---- units & cardinality ----
    ("masker tilbage", "sts remain"),
    ("masker pr.", "sts per"),
    ("masker", "sts"),
    ("maske", "st"),
    ("rækker", "rows"),
    ("række", "row"),
    ("pinde", "rows"),
    ("pind", "row"),
    ("hjørne", "corner"),
    (" m,", " sts,"),
    (" m.", " sts."),
    (" m ", " sts "),
    (" m)", " sts)"),
    (" r,", " k,"),
    (" r ", " k "),
    (" vr ", " p "),
    (" vr,", " p,"),
    # ---- shape / state words ----
    ("retsiden", "the right side"),
    ("vrangsiden", "the wrong side"),
    ("vrang", "purl"),
    # don't translate bare "ret" / "vr" — too ambiguous and already handled above
    # ---- generic verbs/words ----
    ("Gentag", "Repeat"),
    ("gentag", "repeat"),
    ("gange", "times"),
    ("hver omg", "every rnd"),
    # don't replace "hver" — too ambiguous
    ("ca.", "approx."),
    ("i alt", "total"),
    ("rest af", "rest of"),
    ("til enden", "to the end"),
    ("til ende", "to end"),
    ("blokke", "blocks"),
    # ---- nouns commonly used in steps ----
    ("Bærestykke", "Yoke"),
    ("bærestykke", "yoke"),
    ("Halsudskæring", "Neckline"),
    ("halsudskæring", "neckline"),
    ("Krop og rib", "Body and rib"),
    ("Krop og ærmer", "Body and sleeves"),
    ("Adskillelse af ærmer", "Sleeve separation"),
    ("ærme", "sleeve"),
    ("Ærme", "Sleeve"),
    ("ærmer", "sleeves"),
    ("Ærmer", "Sleeves"),
    ("kant", "border"),
    ("kanten", "the border"),
    ("manchet", "cuff"),
    ("manchetten", "the cuff"),
    ("hælen", "the heel"),
    ("hæl", "heel"),
    ("vrist", "instep"),
    ("vristen", "the instep"),
    ("ringen", "the ring"),
    # ---- short tokens last ----
    ("indt-omg", "dec rnd"),
    ("udt-omg", "inc rnd"),
    ("indt", "dec"),
    ("udt", "inc"),
    ("omg", "rnd"),
]


def translate_pattern(pattern: "Pattern", lang: str) -> "Pattern":
    """Mutate a pattern in place, translating Danish strings to ``lang``.

    Only used by constructions that don't do inline translation. Translates:

    - section titles via ``SECTION_TITLES_EN``
    - step text + step notes via ``_PHRASE_REPL`` (best-effort word-level)
    - pattern.notes and pattern.warnings (same phrase replacement)

    For ``lang != "en"`` this is a no-op.
    """
    if lang != "en":
        return pattern
    for sec in pattern.sections:
        sec.title = SECTION_TITLES_EN.get(sec.title, _phrase_translate(sec.title))
        for step in sec.steps:
            step.text = _phrase_translate(step.text)
            if step.note:
                step.note = _phrase_translate(step.note)
    pattern.notes = [_phrase_translate(n) for n in pattern.notes]
    pattern.warnings = [_phrase_translate(w) for w in pattern.warnings]
    return pattern


def _phrase_translate(text: str) -> str:
    """Apply the Danish→English phrase replacements to ``text``."""
    out = text
    for da, en in _PHRASE_REPL:
        out = out.replace(da, en)
    return out
