"""Tiny translation table.

Usage:

    from lib.visualisering.lang import t
    t("materials.heading", "da")  # → "Materialer"
    t("materials.heading", "en")  # → "Materials"

If a key is missing in the requested language, we fall back to ``da``.
If the key is missing in ``da`` too we return the key unchanged so the
caller still gets *something* and we don't crash a generator. Skills can
``register_translations({...}, lang="en")`` to extend the dictionary
with construction-specific keys without touching this file.
"""

from __future__ import annotations

# ----- Default Danish strings -----------------------------------------
_DA: dict[str, str] = {
    # ---- shell ----
    "skill.knit.eyebrow": "Strikkeopskrift",
    "skill.crochet.eyebrow": "Hækleopskrift",
    "skill.knit.generator": "Genereret med strikkeopskrift-skill · maskeantal valideret automatisk",
    "skill.crochet.generator": "Genereret med hækleopskrift-skill · maskeantal valideret automatisk",
    "section.schematic": "Skematik",
    "section.materials": "Materialer & mål",
    "section.pattern": "Opskrift",
    "section.abbreviations": "Forkortelser",
    "section.notes": "Noter",
    "section.warnings": "⚠ Bemærkninger",

    # ---- materials_box ----
    "materials.heading": "Materialer",
    "materials.gauge_heading": "Strikkefasthed",
    "materials.yarn": "Garn",
    "materials.yarn_lineweight": "Løbelængde",
    "materials.needles": "Pinde",
    "materials.hook": "Nål",
    "materials.designer": "Designer",
    "materials.year": "År",
    "materials.notions": "Tilbehør",
    "materials.notions_text": "4–8 markører, stoppenål.",
    "materials.swatch_warning": "Strik altid en prøvelap (mindst 15 × 15 cm) og mål før du går i gang.",
    "materials.swatch_warning_crochet": "Hækl altid en prøvelap (mindst 15 × 15 cm) og mål før du går i gang.",
    "materials.gauge_value_knit": "{sts} masker × {rows} pinde på 10 × 10 cm i glatstrik.",
    "materials.gauge_value_crochet": "{sts} masker × {rows} omg. på 10 × 10 cm i grundsting.",
    "materials.placeholder_knit":
        "Garn (anbefalet sammensætning + løbelængde): _____.<br>"
        "Pinde: rundpind / strømpepinde i passende størrelse til at opnå strikkefasthed.<br>"
        "Tilbehør: 4–8 markører, stoppenål.",
    "materials.placeholder_crochet":
        "Garn (anbefalet sammensætning + løbelængde): _____.<br>"
        "Hæklenål: passende til at opnå hæklefasthed.<br>"
        "Tilbehør: maskemarkører, stoppenål.",

    # ---- measurements_box ----
    "measurements.heading": "Mål",

    # ---- abbreviations ----
    "abbr.col.abbr": "Forkortelse",
    "abbr.col.da": "Dansk",
    "abbr.col.en": "English",
    "abbr.intro_knit": "Dansk strikkesprog er ikke standardiseret. Denne opskrift bruger nedenstående konvention.",
    "abbr.intro_crochet": "Dansk hæklesprog er ikke standardiseret. Denne opskrift bruger nedenstående konvention.",

    # ---- last page ----
    "lastpage.body_knit":
        "Opskriften er beregnet og maskevalideret. Den er <em>ikke</em> testet med "
        "nål og garn — strik en prøvelap først, og overvej en mini-version af "
        "trøjen før du forpligter dig til en stor mængde garn.",
    "lastpage.body_crochet":
        "Opskriften er beregnet og maskevalideret. Den er <em>ikke</em> testet med "
        "nål og garn — hækl en prøvelap først.",
    "lastpage.tag_knit": "Genereret af strikkeopskrift-skill",
    "lastpage.tag_crochet": "Genereret af hækleopskrift-skill",

    # ---- cover ----
    "cover.label.bust_finished": "Brystmål, færdig",
    "cover.label.head_finished": "Hovedmål, færdig",
    "cover.label.width": "Bredde",
    "cover.label.length": "Længde",
    "cover.label.gauge": "Strikkefasthed",
    "cover.label.gauge_crochet": "Hæklefasthed",
    "cover.label.diameter_target": "Diameter, mål",
    "cover.label.diameter_actual": "Diameter, faktisk",
    "cover.label.rounds": "Antal omg",
    "cover.label.foot_length": "Fodlængde",
    "cover.label.foot_circ": "Fodomkreds",
    "cover.label.shoe_size": "Skostørrelse",

    # ---- difficulty rating ----
    "difficulty": "Sværhedsgrad",
    "difficulty.beginner": "Begynder",
    "difficulty.easy": "Let øvet",
    "difficulty.intermediate": "Øvet",
    "difficulty.advanced": "Avanceret",

    # ---- construction labels (knit) ----
    "construction.hue": "Hue, strikket fra opslag og opad",
    "construction.tørklæde": "Tørklæde, flat",
    "construction.raglan_topdown": "Top-down raglan-trøje",
    "construction.sokker": "Sokker, top-down med kilehæl",
    "construction.bottom_up_sweater": "Bottom-up sweater (Zimmermann EPS)",
    "construction.compound_raglan": "Compound raglan (uafhængig krop/ærme)",
    "construction.half_pi_shawl": "Half-pi shawl (Zimmermann)",
    "construction.yoke_stranded": "Top-down yoke-sweater med stranded mønster",
    "construction.short_rows_shawl": "Korte rækker crescent shawl",

    # ---- construction labels (crochet) ----
    "construction.amigurumi_sphere": "Amigurumi-kugle (rounds, magic ring)",
    "construction.amigurumi_cylinder": "Amigurumi-cylinder (rounds, magic ring)",
    "construction.amigurumi_taper": "Amigurumi-taper (rounds)",
    "construction.amigurumi_figur": "Amigurumi-figur (krop + hoved + ører + arme + ben)",
    "construction.granny_square": "Granny square (3-stm-clusters)",
    "construction.haekle_tørklæde": "Hæklet tørklæde, fladt",
    "construction.filet": "Filet hækling (mesh + blokke)",
    "construction.tunisian": "Tunisian — TSS",

    # ---- generic measurement labels ----
    "measure.bust_finished": "Brystmål, færdig",
    "measure.bust_body": "Brystmål, krop",
    "measure.ease": "Ease",
    "measure.yoke_depth": "Bærestykkedybde",
    "measure.body_length": "Kropslængde (u.arm → kant)",
    "measure.sleeve_length": "Ærmelængde",
    "measure.neck_circ": "Halsomkreds",
    "measure.wrist_circ": "Håndledsmål",
    "measure.head_finished": "Hovedomkreds, færdig",
    "measure.head_body": "Hovedomkreds, kropsmål",
    "measure.height": "Højde",
    "measure.rib_height": "Rib-højde",
    "measure.width": "Bredde",
    "measure.length": "Længde",
    "measure.pattern": "Mønster",

    # ---- schematic captions ----
    "fig.gauge": "Strikkefasthed (10 × 10 cm)",
    "fig.gauge_crochet": "Hæklefasthed (10 × 10 cm)",
    "fig.hue_side": "Hue (sideprofil)",
    "fig.crown_top": "Krone set ovenfra ({sectors} sektorer)",
    "fig.tørklæde": "Tørklæde — flat",
    "fig.raglan": "Krop og ærme — flat skematik",
    "fig.sock": "Sok — skaft + fod (L-form)",
    "fig.sweater": "Bottom-up sweater (krop + ærme)",
    "fig.filet": "Filet — pixel-grid",
    "fig.tunisian": "Tunisian — fladt rektangel",
    "fig.granny": "Granny square, {rounds} omg",
    "fig.amigurumi_sphere": "Amigurumi-kugle, {rounds} omg",
    "fig.amigurumi_cylinder": "Amigurumi-cylinder, {rows} tube-omg",
    "fig.haekle_scarf": "Tørklæde, fladt",

    # ---- chart legend ----
    "chart.legend_heading": "Symbol-forklaring",
    "chart.section_heading": "Lace-diagram",
    "chart.lace_caption": "Lace-rapport — læs nedefra og op, højre mod venstre på rs-pinde.",
    "chart.colorwork_section_heading": "Stranded farve-diagram",
    "chart.colorwork_caption": "Stranded farve-rapport — læs nedefra og op, RS-omg.",
    "construction.lace_shawl": "Lace shawl, aflang med rapport-mønster",
    "construction.colorwork_swatch": "Colorwork prøvelap (fladt rektangel)",
    "fig.lace_shawl": "Lace shawl — flat",
    "fig.colorwork_swatch": "Colorwork prøvelap — fladt rektangel",

    # ---- yarn alternatives (Fase 5 iter 5) ----
    "yarn_alt.heading": "Garn-alternativer",
    "yarn_alt.intro":
        "Hvis du ikke kan få fat i {yarn}, så er disse garner i samme "
        "vægtklasse ({weight_class}) gode alternativer. Strik altid en "
        "prøvelap først.",
    "yarn_alt.gauge_match": "Samme strikkefasthed.",
    "yarn_alt.gauge_diff_higher":
        "Vil typisk give {diff_pct} % færre masker pr. 10 cm — "
        "prøv en {hint_needle} mm pind for at ramme samme fasthed.",
    "yarn_alt.gauge_diff_lower":
        "Vil typisk give {diff_pct} % flere masker pr. 10 cm — "
        "prøv en {hint_needle} mm pind for at ramme samme fasthed.",
    "yarn_alt.fiber": "Fiber",
    "yarn_alt.run": "Løbelængde",
    "yarn_alt.needle": "Anbefalet pind",
    "yarn_alt.hook": "Anbefalet nål",
}


# ----- English overrides ---------------------------------------------
_EN: dict[str, str] = {
    # ---- shell ----
    "skill.knit.eyebrow": "Knitting pattern",
    "skill.crochet.eyebrow": "Crochet pattern",
    "skill.knit.generator": "Generated by the strikkeopskrift skill · stitch counts validated",
    "skill.crochet.generator": "Generated by the hækleopskrift skill · stitch counts validated",
    "section.schematic": "Schematic",
    "section.materials": "Materials & measurements",
    "section.pattern": "Pattern",
    "section.abbreviations": "Abbreviations",
    "section.notes": "Notes",
    "section.warnings": "⚠ Notes & warnings",

    # ---- materials ----
    "materials.heading": "Materials",
    "materials.gauge_heading": "Gauge",
    "materials.yarn": "Yarn",
    "materials.yarn_lineweight": "Length per skein",
    "materials.needles": "Needles",
    "materials.hook": "Hook",
    "materials.designer": "Designer",
    "materials.year": "Year",
    "materials.notions": "Notions",
    "materials.notions_text": "4–8 stitch markers, tapestry needle.",
    "materials.swatch_warning":
        "Always knit a swatch (at least 15 × 15 cm) and measure before you start.",
    "materials.swatch_warning_crochet":
        "Always crochet a swatch (at least 15 × 15 cm) and measure before you start.",
    "materials.gauge_value_knit": "{sts} stitches × {rows} rows over 10 × 10 cm in stockinette.",
    "materials.gauge_value_crochet": "{sts} stitches × {rows} rows over 10 × 10 cm in the base stitch.",
    "materials.placeholder_knit":
        "Yarn (recommended fibre + length per skein): _____.<br>"
        "Needles: circular / DPN in the size needed to obtain gauge.<br>"
        "Notions: 4–8 markers, tapestry needle.",
    "materials.placeholder_crochet":
        "Yarn (recommended fibre + length per skein): _____.<br>"
        "Hook: size needed to obtain gauge.<br>"
        "Notions: stitch markers, tapestry needle.",

    # ---- measurements ----
    "measurements.heading": "Measurements",

    # ---- abbreviations ----
    "abbr.col.abbr": "Abbreviation",
    "abbr.col.da": "Dansk",
    "abbr.col.en": "English",
    "abbr.intro_knit":
        "Knitting abbreviations vary by tradition. This pattern uses the convention below.",
    "abbr.intro_crochet":
        "Crochet abbreviations vary by tradition. This pattern uses the US convention below.",

    # ---- last page ----
    "lastpage.body_knit":
        "This pattern is computed and stitch-validated. It has <em>not</em> been "
        "tested with needles and yarn — knit a swatch first, and consider a "
        "mini version before committing to a full sweater.",
    "lastpage.body_crochet":
        "This pattern is computed and stitch-validated. It has <em>not</em> "
        "been tested with hook and yarn — crochet a swatch first.",
    "lastpage.tag_knit": "Generated by the strikkeopskrift skill",
    "lastpage.tag_crochet": "Generated by the hækleopskrift skill",

    # ---- cover ----
    "cover.label.bust_finished": "Bust, finished",
    "cover.label.head_finished": "Head circ., finished",
    "cover.label.width": "Width",
    "cover.label.length": "Length",
    "cover.label.gauge": "Gauge",
    "cover.label.gauge_crochet": "Gauge",
    "cover.label.diameter_target": "Diameter, target",
    "cover.label.diameter_actual": "Diameter, actual",
    "cover.label.rounds": "Rounds",
    "cover.label.foot_length": "Foot length",
    "cover.label.foot_circ": "Foot circ.",
    "cover.label.shoe_size": "Shoe size",

    # ---- difficulty rating ----
    "difficulty": "Difficulty",
    "difficulty.beginner": "Beginner",
    "difficulty.easy": "Easy",
    "difficulty.intermediate": "Intermediate",
    "difficulty.advanced": "Advanced",

    # ---- construction labels (knit) ----
    "construction.hue": "Hat, knit bottom-up",
    "construction.tørklæde": "Scarf, flat",
    "construction.raglan_topdown": "Top-down raglan sweater",
    "construction.sokker": "Socks, top-down with heel flap & gusset",
    "construction.bottom_up_sweater": "Bottom-up sweater (Zimmermann EPS)",
    "construction.compound_raglan": "Compound raglan (independent body/sleeve)",
    "construction.half_pi_shawl": "Half-pi shawl (Zimmermann)",
    "construction.yoke_stranded": "Top-down yoke sweater with stranded yoke",
    "construction.short_rows_shawl": "Short-row crescent shawl",

    # ---- construction labels (crochet) ----
    "construction.amigurumi_sphere": "Amigurumi sphere (rounds, magic ring)",
    "construction.amigurumi_cylinder": "Amigurumi cylinder (rounds, magic ring)",
    "construction.amigurumi_taper": "Amigurumi taper (rounds)",
    "construction.amigurumi_figur": "Amigurumi figure (body + head + ears + arms + legs)",
    "construction.granny_square": "Granny square (3-dc clusters)",
    "construction.haekle_tørklæde": "Crochet scarf, flat",
    "construction.filet": "Filet crochet (mesh + blocks)",
    "construction.tunisian": "Tunisian — TSS",

    # ---- generic measurement labels ----
    "measure.bust_finished": "Bust, finished",
    "measure.bust_body": "Bust, body",
    "measure.ease": "Ease",
    "measure.yoke_depth": "Yoke depth",
    "measure.body_length": "Body length (underarm → hem)",
    "measure.sleeve_length": "Sleeve length",
    "measure.neck_circ": "Neck circ.",
    "measure.wrist_circ": "Wrist circ.",
    "measure.head_finished": "Head circ., finished",
    "measure.head_body": "Head circ., body",
    "measure.height": "Height",
    "measure.rib_height": "Rib height",
    "measure.width": "Width",
    "measure.length": "Length",
    "measure.pattern": "Stitch pattern",

    # ---- schematic captions ----
    "fig.gauge": "Gauge (10 × 10 cm)",
    "fig.gauge_crochet": "Gauge (10 × 10 cm)",
    "fig.hue_side": "Hat (side view)",
    "fig.crown_top": "Crown, top view ({sectors} sectors)",
    "fig.tørklæde": "Scarf — flat",
    "fig.raglan": "Body & sleeve — flat schematic",
    "fig.sock": "Sock — leg + foot (L-shape)",
    "fig.sweater": "Bottom-up sweater (body + sleeve)",
    "fig.filet": "Filet — pixel grid",
    "fig.tunisian": "Tunisian — flat rectangle",
    "fig.granny": "Granny square, {rounds} rnds",
    "fig.amigurumi_sphere": "Amigurumi sphere, {rounds} rnds",
    "fig.amigurumi_cylinder": "Amigurumi cylinder, {rows} tube rnds",
    "fig.haekle_scarf": "Scarf, flat",

    # ---- chart legend ----
    "chart.legend_heading": "Chart legend",
    "chart.section_heading": "Lace chart",
    "chart.lace_caption": "Lace repeat — read bottom-up, right-to-left on RS rows.",
    "chart.colorwork_section_heading": "Stranded colorwork chart",
    "chart.colorwork_caption": "Stranded colorwork repeat — read bottom-up, RS rounds.",
    "construction.lace_shawl": "Lace shawl, rectangular with repeating motif",
    "construction.colorwork_swatch": "Colorwork swatch (flat rectangle)",
    "fig.lace_shawl": "Lace shawl — flat",
    "fig.colorwork_swatch": "Colorwork swatch — flat rectangle",

    # ---- yarn alternatives (Fase 5 iter 5) ----
    "yarn_alt.heading": "Yarn alternatives",
    "yarn_alt.intro":
        "If you can't source {yarn}, these yarns in the same weight class "
        "({weight_class}) are good substitutes. Always knit a swatch first.",
    "yarn_alt.gauge_match": "Same gauge.",
    "yarn_alt.gauge_diff_higher":
        "Typically gives {diff_pct} % fewer stitches per 10 cm — "
        "try a {hint_needle} mm needle to match gauge.",
    "yarn_alt.gauge_diff_lower":
        "Typically gives {diff_pct} % more stitches per 10 cm — "
        "try a {hint_needle} mm needle to match gauge.",
    "yarn_alt.fiber": "Fibre",
    "yarn_alt.run": "Length per skein",
    "yarn_alt.needle": "Recommended needle",
    "yarn_alt.hook": "Recommended hook",
}


_TABLES: dict[str, dict[str, str]] = {"da": _DA, "en": _EN}


def t(key: str, lang: str = "da", **kwargs) -> str:
    """Look up a translation. Falls back to Danish, then to the key itself.

    ``kwargs`` are passed through ``str.format``, so the value can contain
    placeholders like ``{sts}`` or ``{rounds}``.
    """
    table = _TABLES.get(lang) or _DA
    val = table.get(key)
    if val is None and lang != "da":
        val = _DA.get(key)
    if val is None:
        return key
    if kwargs:
        try:
            return val.format(**kwargs)
        except (KeyError, IndexError):
            return val
    return val


def available_languages() -> list[str]:
    return sorted(_TABLES)


def register_translations(extra: dict[str, str], *, lang: str = "da") -> None:
    """Merge extra translations into ``lang`` (no override-tracking — last
    writer wins). Useful from a skill's `__init__.py` to add construction-
    specific labels without hardcoding them in lib/visualisering."""
    _TABLES.setdefault(lang, {}).update(extra)
