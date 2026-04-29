"""Rectangular lace shawl with a repeating lace motif (e.g. feather-and-fan).

A simple but real lace shawl: garter top, lace body of N feather-and-fan
repeats, garter bottom. The construction validates the repeat (each row of
the lace pattern must be balanced — the number of yarn-overs must equal the
number of decreases — so the stitch count stays constant) and emits both
prose instructions and a stitch-chart payload that the HTML renderer turns
into an embedded SVG.

The default repeat is the classic Old-Shale / feather-and-fan motif:

    Repeat width  : 18 sts
    Repeat height : 4 rows

    RS row 1   k all
    WS row 2   p all
    RS row 3   *k2tog × 3, (yo, k1) × 6, k2tog × 3*  ← shaping row
    RS row 4   k all          (= "garter ridge" effect — looks like waves)

Row 3 produces ridges/waves: every yo adds a stitch and every k2tog removes
one — six yos vs. six dec → balanced. The chart we render shows only the
shaping row (row 3) over one 18-stitch repeat, since rows 1, 2 and 4 are
trivial in symbol terms (knit/purl). For didactic value we show the whole
4-row repeat using ``knit`` (RS) and ``purl`` (WS) symbols on the plain
rows.
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import Gauge, cm_to_sts, cm_to_rows, Pattern


# ---------------------------------------------------------------------------
# Built-in lace repeats. Each entry is (name → ``LaceRepeat``).
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LaceRepeat:
    """A repeating lace stitch pattern.

    ``rows`` is read top-to-bottom, with row 1 of the knitting at the bottom
    of the chart (so ``rows[-1]`` is the *first* row knitted). Each row is a
    list of canonical chart-symbol names. Symbols are validated against
    ``chart_symbols``; the row's net stitch change must be zero so the
    overall stitch count is preserved.
    """
    name: str
    rows: list[list[str]]
    repeat_sts: int
    repeat_rows: int
    description: str = ""


_FEATHER_AND_FAN: list[list[str]] = [
    # Top of chart (highest row number) first.
    ["knit"] * 18,                                                 # row 4 (RS)
    ["k2tog"] * 3 + ["yo", "knit"] * 6 + ["k2tog"] * 3,             # row 3 (RS)
    ["purl"] * 18,                                                  # row 2 (WS)
    ["knit"] * 18,                                                  # row 1 (RS)
]


REPEATS: dict[str, LaceRepeat] = {
    "feather_and_fan": LaceRepeat(
        name="feather_and_fan",
        rows=_FEATHER_AND_FAN,
        repeat_sts=18,
        repeat_rows=4,
        description="Klassisk feather-and-fan / old shale: 18 m × 4 p",
    ),
}


# ---------------------------------------------------------------------------
# Stitch-balance validation
# ---------------------------------------------------------------------------

# net stitches produced minus consumed per symbol
_NET: dict[str, int] = {
    "knit":   0,
    "purl":   0,
    "sl1":    0,
    "yo":    +1,
    "k2tog": -1,
    "ssk":   -1,
    "k3tog": -2,
    "cdd":   -2,
    "no-stitch": 0,
}


def validate_repeat_balance(repeat: LaceRepeat) -> None:
    """Raise ``ValueError`` if any row in the repeat changes the stitch count.

    Each row must consume the same number of stitches it produces — otherwise
    the repeat doesn't tile vertically and the shawl's stitch count drifts.
    """
    for r_idx, row in enumerate(repeat.rows):
        net = sum(_NET[s] for s in row)
        if net != 0:
            # row index 0 is the top; row 1 is at the bottom. Translate.
            row_no = len(repeat.rows) - r_idx
            raise ValueError(
                f"lace repeat {repeat.name!r}: row {row_no} is not balanced "
                f"(net {net:+d} sts). Each row in a body lace repeat must "
                "have equal yarn-overs and decreases."
            )
    if repeat.repeat_sts <= 0 or repeat.repeat_rows <= 0:
        raise ValueError("repeat_sts and repeat_rows must be positive")


# ---------------------------------------------------------------------------
# Spec + generator
# ---------------------------------------------------------------------------

@dataclass
class LaceShawlSpec:
    width_cm: float
    length_cm: float
    gauge: Gauge
    repeat: str = "feather_and_fan"
    name: str = "Lace shawl"
    edge_sts: int = 4         # garter selvedge each side
    garter_band_cm: float = 5.0  # top + bottom garter
    metadata: dict | None = None


def generate_lace_shawl(spec: LaceShawlSpec, lang: str = "da") -> Pattern:
    g = spec.gauge

    if spec.repeat not in REPEATS:
        known = ", ".join(sorted(REPEATS))
        raise ValueError(
            f"unknown lace repeat {spec.repeat!r}. Known: {known}"
        )
    repeat = REPEATS[spec.repeat]
    validate_repeat_balance(repeat)

    # Stitch math --------------------------------------------------------
    # Body sts (the part inside the garter selvedge) must be a multiple of
    # the lace-repeat width. Round-down so the selvedge can absorb leftover.
    inner_target = spec.width_cm * g.sts_per_10cm / 10.0 - 2 * spec.edge_sts
    if inner_target < repeat.repeat_sts:
        raise ValueError(
            f"width {spec.width_cm} cm too narrow for lace repeat "
            f"({repeat.repeat_sts} sts) + {spec.edge_sts}-st edges."
        )
    n_repeats = max(1, int(inner_target // repeat.repeat_sts))
    inner_sts = n_repeats * repeat.repeat_sts
    cast_on = inner_sts + 2 * spec.edge_sts

    # Row math
    band_rows = cm_to_rows(spec.garter_band_cm, g)
    # Force band_rows to be even so we end on a WS row before lace.
    if band_rows % 2 == 1:
        band_rows += 1
    total_rows = cm_to_rows(spec.length_cm, g)
    body_rows_target = max(repeat.repeat_rows,
                           total_rows - 2 * band_rows)
    n_body_repeats = max(1, round(body_rows_target / repeat.repeat_rows))
    body_rows = n_body_repeats * repeat.repeat_rows
    actual_total_rows = body_rows + 2 * band_rows
    actual_length_cm = actual_total_rows * 10.0 / g.rows_per_10cm
    actual_width_cm = cast_on * 10.0 / g.sts_per_10cm

    metadata = dict(spec.metadata or {})

    # Chart payload — embedded as a plain dict so it survives JSON
    # serialisation. The HTML renderer reads ``inputs["lace_chart"]``.
    chart_rows = [list(r) for r in repeat.rows]
    lace_chart = {
        "rows": chart_rows,
        "caption": (
            f"Lace-rapport ({repeat.repeat_sts} m × {repeat.repeat_rows} p) — "
            f"læs nedefra og op."
        ),
        "repeat_marker": (0, repeat.repeat_sts - 1),
    }

    p = Pattern(
        name=spec.name,
        construction="lace_shawl",
        difficulty="intermediate",
        inputs={
            "_domain": "knit",
            "width_cm": spec.width_cm,
            "length_cm": spec.length_cm,
            "actual_width_cm": round(actual_width_cm, 1),
            "actual_length_cm": round(actual_length_cm, 1),
            "cast_on": cast_on,
            "inner_sts": inner_sts,
            "edge_sts": spec.edge_sts,
            "n_lace_repeats_width": n_repeats,
            "n_lace_repeats_length": n_body_repeats,
            "garter_band_rows": band_rows,
            "garter_band_cm": spec.garter_band_cm,
            "body_rows": body_rows,
            "actual_total_rows": actual_total_rows,
            "repeat_name": repeat.name,
            "repeat_sts": repeat.repeat_sts,
            "repeat_rows": repeat.repeat_rows,
            "repeat_description": repeat.description,
            "gauge": {
                "sts_per_10cm": g.sts_per_10cm,
                "rows_per_10cm": g.rows_per_10cm,
            },
            "metadata": metadata,
            "lace_chart": lace_chart,
        },
    )

    # ---- Opslag --------------------------------------------------------
    sec1 = p.add_section("Opslag og garter-bånd", sts_before=cast_on)
    sec1.add(
        f"Slå {cast_on} m op med en elastisk metode "
        f"(fx long-tail). {n_repeats} × {repeat.repeat_sts} m lace + "
        f"2 × {spec.edge_sts} m garter-kant.",
        cast_on,
        note=f"masker = {cast_on} (= {spec.edge_sts} kant + "
             f"{n_repeats} × {repeat.repeat_sts} lace + {spec.edge_sts} kant)",
    )
    sec1.add(
        f"Strik {band_rows} pinde retstrik (alle pinde ret) som øverste "
        f"garter-bånd.",
        cast_on,
        note=f"~{spec.garter_band_cm:.1f} cm",
    )

    # ---- Lace-body -----------------------------------------------------
    sec2 = p.add_section("Lace-body", sts_before=cast_on)
    sec2.add(
        f"Skift til lace-rapporten ({repeat.repeat_sts} m × "
        f"{repeat.repeat_rows} p, {repeat.description}).",
        cast_on,
    )
    sec2.add(
        f"Pind 1 (rs): {spec.edge_sts} m ret (kant), strik lace-rapporten "
        f"{n_repeats} gange (følg diagrammet), {spec.edge_sts} m ret (kant).",
        cast_on,
    )
    sec2.add(
        f"Pind 2 (vs): {spec.edge_sts} m ret, vrang resten til de sidste "
        f"{spec.edge_sts} m, strik {spec.edge_sts} m ret.",
        cast_on,
        note="garter-kanten er ret på begge sider; lace-feltet er glat-vrang på vs",
    )
    sec2.add(
        f"Pind 3 (rs, shaping): {spec.edge_sts} m ret, gentag *2 r sm × 3, "
        f"(slå om, 1 r) × 6, 2 r sm × 3* {n_repeats} gange, {spec.edge_sts} m ret.",
        cast_on,
        note="dette er bølge-pinden — yo og k2tog balancerer hinanden",
    )
    sec2.add(
        f"Pind 4 (vs): {spec.edge_sts} m ret, vrang resten til de sidste "
        f"{spec.edge_sts} m, strik {spec.edge_sts} m ret.",
        cast_on,
    )
    sec2.add(
        f"Gentag pind 1-4 i alt {n_body_repeats} gange "
        f"({body_rows} pinde ≈ {body_rows * 10/g.rows_per_10cm:.1f} cm).",
        cast_on,
        note="fastsidder lace-rapporten, gentag præcis antal gange",
    )

    # ---- Bund-bånd + aflukning -----------------------------------------
    sec3 = p.add_section("Garter-bånd + aflukning", sts_before=cast_on)
    sec3.add(
        f"Strik {band_rows} pinde retstrik som nederste garter-bånd.",
        cast_on,
        note=f"~{spec.garter_band_cm:.1f} cm",
    )
    sec3.add(
        "Luk meget løst af på rs (Jenny's stretchy bind-off anbefales — "
        "stram aflukning ødelægger bølgerne).",
        cast_on,
    )
    sec3.add(
        "Hæft ender. Vådblok på flade nåle: stræk på langs så bølgerne "
        "spredes ~30 % bredere end strikket størrelse.",
        cast_on,
    )

    p.validate_continuity()

    # ---- Notes / warnings ---------------------------------------------
    p.notes.append(
        f"Faktiske mål før blok: {actual_width_cm:.1f} cm × "
        f"{actual_length_cm:.1f} cm. Efter blok ~+25 % i begge retninger."
    )
    p.notes.append(
        f"Lace-rapport: {repeat.repeat_sts} m × {repeat.repeat_rows} p, "
        f"{n_repeats} rapporter på bredden, {n_body_repeats} på højden."
    )
    p.notes.append(
        "Diagrammet vises sammen med opskriften og bruger SVG-symboler — "
        "ingen font-licensafhængighed."
    )

    if abs(actual_width_cm - spec.width_cm) > 2.0:
        p.warnings.append(
            f"Bredden er rundet til {actual_width_cm:.1f} cm "
            f"(ønsket {spec.width_cm:.1f} cm). For at passe lace-rapporten "
            f"{repeat.repeat_sts} m skal bredden være et multiplum + kant."
        )
    if abs(actual_length_cm - spec.length_cm) > 4.0:
        p.warnings.append(
            f"Længden er rundet til {actual_length_cm:.1f} cm "
            f"(ønsket {spec.length_cm:.1f} cm) for at passe "
            f"hele {repeat.repeat_rows}-pinde-rapporter."
        )

    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
