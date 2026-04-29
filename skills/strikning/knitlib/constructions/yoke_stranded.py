"""Top-down stranded yoke sweater (Icelandic / Lopapeysa style).

Three decrease rounds with the classic Tin Can Knits / EZ "Strange Brew"
factors. Stranded motifs require the stitch count of each band to be a
multiple of the motif repeat width R; we use ``repeat_fit(sts, R)`` to snap
to the closest multiple after each shaping round.

Construction outline (Agent A's research §5):

    yoke_start_sts ≈ 1.45 × K   (K = bust_sts at chest)
    yoke_depth_cm  ≈ (bust + ease) / 4

    Decrease #1 at 30 % yoke depth:  after = round(yoke_start * 0.75)
    Decrease #2 at 60 % yoke depth:  after = round(after_dec1 * 0.70)
    Decrease #3 at 85 % yoke depth:  after = neck_sts

After each decrease we snap the resulting count to the nearest multiple of
the motif repeat (default R = 8). We err *down* so the band has at least
the right number of repeats.

Inputs:
  - bust_cm, ease_cm, gauge
  - upper_arm_cm (for sleeve grading), wrist_cm
  - body_length_cm, sleeve_length_cm
  - neck_circumference_cm
  - rib_height_cm
  - repeat_width (R, default 8)
  - color_motif (list[list[str]] — optional grid of "A"/"B" per row, per st)
  - underarm_cast_on_cm (default auto)
"""

from __future__ import annotations
from dataclasses import dataclass, field

from lib.visualisering import (
    Gauge, cm_to_sts, cm_to_rows, Pattern, RowValidator,
)
from lib.visualisering.motifs import MOTIFS, get_motif
from ..knitrow import KnitRow as Row


_UNDERARM_MIN_CM = 3.0
_UNDERARM_MAX_CM = 8.0


def repeat_fit(sts: int, R: int, mode: str = "down") -> int:
    """Snap ``sts`` to a multiple of ``R``.

    mode = "down" / "up" / "nearest". Default down so the resulting band has
    no leftover stitches (Agent A §5).
    """
    if R < 1:
        raise ValueError("R must be >= 1")
    if sts < 0:
        raise ValueError("sts must be >= 0")
    rem = sts % R
    if rem == 0:
        return sts
    if mode == "down":
        return sts - rem
    if mode == "up":
        return sts + (R - rem)
    if mode == "nearest":
        return sts - rem if rem * 2 <= R else sts + (R - rem)
    raise ValueError(f"unknown mode {mode!r}")


# Default 8-st Icelandic-ish motif (placeholder), 6 rows, A/B grid.
DEFAULT_MOTIF: list[list[str]] = [
    ["A", "A", "B", "A", "A", "A", "B", "A"],
    ["A", "B", "B", "B", "A", "B", "B", "B"],
    ["B", "B", "A", "B", "B", "B", "A", "B"],
    ["B", "B", "A", "B", "B", "B", "A", "B"],
    ["A", "B", "B", "B", "A", "B", "B", "B"],
    ["A", "A", "B", "A", "A", "A", "B", "A"],
]


def render_color_chart(motif: list[list[str]],
                        color_a: str = "■", color_b: str = "□") -> str:
    """Render a stranded chart as a text grid for markdown.

    Reads top-row first (row 1 at top, like Ravelry charts). Returns a string
    where each row is one motif row, with characters separated by spaces.
    """
    if not motif:
        return ""
    lines: list[str] = []
    n_rows = len(motif)
    for i, row in enumerate(motif):
        # Row label: count from bottom so row 1 is at the bottom (knit upward)
        row_label = n_rows - i
        cells = " ".join(color_a if c.upper() == "A" else color_b for c in row)
        lines.append(f"{row_label:>2} | {cells}")
    sep = "   +" + "-" * (2 * len(motif[0]))
    lines.append(sep)
    return "\n".join(lines)


@dataclass
class YokeStrandedSpec:
    bust_cm: float
    gauge: Gauge
    name: str = "Stranded yoke sweater"
    ease_cm: float = 5.0
    yoke_depth_cm: float | None = None
    body_length_cm: float = 36.0
    sleeve_length_cm: float = 45.0
    upper_arm_cm: float = 31.0
    wrist_cm: float = 18.0
    neck_circumference_cm: float = 44.0
    rib_height_cm: float = 5.0
    repeat_width: int = 8
    color_motif: list[list[str]] | None = field(default=None)
    motif: str = "stars"  # name from lib.visualisering.motifs.MOTIFS
    underarm_cast_on_cm: float | None = None
    metadata: dict | None = None


def generate_yoke_stranded(spec: YokeStrandedSpec, lang: str = "da") -> Pattern:
    g = spec.gauge
    R = spec.repeat_width
    if R < 2:
        raise ValueError("repeat_width must be >= 2")

    finished_bust = spec.bust_cm + spec.ease_cm
    K = cm_to_sts(finished_bust, g, multiple=2)
    body_target_sts = K

    # Yoke depth
    if spec.yoke_depth_cm is None:
        yoke_depth_cm = max(finished_bust / 4.0, spec.upper_arm_cm / 2.0 + 4.0)
    else:
        yoke_depth_cm = spec.yoke_depth_cm
    if yoke_depth_cm < 18:
        # research: < 18 cm crowds three decrease zones
        pass
    yoke_rows = cm_to_rows(yoke_depth_cm, g)

    # Sleeve & neck targets
    upper_arm_sts = cm_to_sts(spec.upper_arm_cm, g, multiple=2)
    wrist_sts = cm_to_sts(spec.wrist_cm, g, multiple=4)
    neck_target_sts = cm_to_sts(spec.neck_circumference_cm, g, multiple=4)
    # Pad neck a little so rib doesn't strangle: research suggests +5-10%
    neck_sts = repeat_fit(neck_target_sts, R, mode="nearest")
    if neck_sts == 0:
        neck_sts = R

    # Underarm
    if spec.underarm_cast_on_cm is None:
        underarm_each_cm = max(_UNDERARM_MIN_CM,
                                min(_UNDERARM_MAX_CM, finished_bust * 0.05))
    else:
        underarm_each_cm = spec.underarm_cast_on_cm
    underarm_each = cm_to_sts(underarm_each_cm, g)

    # Yoke start: body - 2u + 2*(arm_top - 2u) (same as bottom-up join)
    body_after_join = body_target_sts - 2 * underarm_each
    sleeve_after_join = upper_arm_sts - 2 * underarm_each
    if sleeve_after_join < 4:
        raise ValueError(
            f"yoke stranded: sleeve_after_join={sleeve_after_join} too small. "
            "Increase upper_arm_cm or reduce ease."
        )
    yoke_start_raw = body_after_join + 2 * sleeve_after_join
    yoke_start = repeat_fit(yoke_start_raw, R, mode="nearest")
    if yoke_start == 0:
        raise ValueError("yoke_start rounds to 0; check inputs")

    # Three decreases, factors 0.75 / 0.70, then to neck.
    after_dec1 = repeat_fit(round(yoke_start * 0.75), R, mode="down")
    after_dec2 = repeat_fit(round(after_dec1 * 0.70), R, mode="down")
    after_dec3 = neck_sts  # already snapped above

    if after_dec3 >= after_dec2:
        # Neck must be smaller than after_dec2 — bump dec2 down
        # by another R until it is.
        while after_dec2 <= after_dec3 and after_dec2 > R:
            after_dec2 -= R
    if after_dec2 >= after_dec1:
        while after_dec1 <= after_dec2 and after_dec1 > R:
            after_dec1 -= R

    dec1_sts = yoke_start - after_dec1
    dec2_sts = after_dec1 - after_dec2
    dec3_sts = after_dec2 - after_dec3

    # Position decreases at 30% / 60% / 85% of yoke
    dec1_round = round(yoke_rows * 0.30)
    dec2_round = round(yoke_rows * 0.60)
    dec3_round = round(yoke_rows * 0.85)

    # Sleeve & body rib
    body_rib_rows = cm_to_rows(spec.rib_height_cm, g)
    body_plain_rows = cm_to_rows(spec.body_length_cm - spec.rib_height_cm, g)
    sleeve_rib_rows = cm_to_rows(spec.rib_height_cm, g)
    sleeve_plain_rows = cm_to_rows(spec.sleeve_length_cm - spec.rib_height_cm, g)

    # Sleeve decreases (cuff to upper arm)
    sleeve_inc_pairs = max(0, (upper_arm_sts - wrist_sts) // 2)
    sleeve_inc_cadence = (sleeve_plain_rows / sleeve_inc_pairs
                          if sleeve_inc_pairs > 0 else 0)

    # Color motif chart — explicit grid wins, otherwise look up by name in
    # the shared motif library; fall back to DEFAULT_MOTIF if neither is
    # available.
    motif_meta: dict | None = None
    if spec.color_motif is not None:
        motif = spec.color_motif
        motif_name = "custom"
        motif_colors = {"A": "#1f3a5f", "B": "#f5f1e6"}
    else:
        if spec.motif in MOTIFS:
            motif_meta = get_motif(spec.motif)
            motif = motif_meta["grid"]
            motif_name = spec.motif
            motif_colors = motif_meta["default_colors"]
        else:
            motif = DEFAULT_MOTIF
            motif_name = "default"
            motif_colors = {"A": "#1f3a5f", "B": "#f5f1e6"}
    motif_repeat_width = len(motif[0]) if motif else R
    chart_text = render_color_chart(motif)

    metadata = dict(spec.metadata or {})
    p = Pattern(
        name=spec.name,
        construction="yoke_stranded",
        difficulty="advanced",
        inputs={
            "_domain": "knit",
            "bust_cm": spec.bust_cm,
            "ease_cm": spec.ease_cm,
            "finished_bust_cm": round(finished_bust, 1),
            "K": K,
            "upper_arm_cm": spec.upper_arm_cm,
            "wrist_cm": spec.wrist_cm,
            "neck_circumference_cm": spec.neck_circumference_cm,
            "yoke_depth_cm": round(yoke_depth_cm, 1),
            "yoke_rows": yoke_rows,
            "repeat_width": R,
            "yoke_start_sts": yoke_start,
            "after_dec1_sts": after_dec1,
            "after_dec2_sts": after_dec2,
            "after_dec3_sts": after_dec3,
            "dec1_sts": dec1_sts,
            "dec2_sts": dec2_sts,
            "dec3_sts": dec3_sts,
            "dec1_round": dec1_round,
            "dec2_round": dec2_round,
            "dec3_round": dec3_round,
            "body_sts": body_target_sts,
            "wrist_sts": wrist_sts,
            "upper_arm_sts": upper_arm_sts,
            "underarm_each": underarm_each,
            "neck_sts": neck_sts,
            "rib_height_cm": spec.rib_height_cm,
            "body_length_cm": spec.body_length_cm,
            "sleeve_length_cm": spec.sleeve_length_cm,
            "color_motif_rows": len(motif),
            "color_motif_width": motif_repeat_width,
            "color_chart": chart_text,
            "motif_name": motif_name,
            "colorwork_chart": {
                "rows": [list(r) for r in motif],
                "colors": dict(motif_colors),
                "caption": (
                    f"Stranded motiv-rapport ({motif_repeat_width} m × "
                    f"{len(motif)} p)"
                ),
                "repeat_marker_x": (0, motif_repeat_width - 1),
                "color_names": {k: f"Farve {k}" for k in motif_colors},
            },
            "gauge": {
                "sts_per_10cm": g.sts_per_10cm,
                "rows_per_10cm": g.rows_per_10cm,
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- Hals & opslag ----------------------------------------------
    sec0 = p.add_section("Hals (top-down)", sts_before=neck_sts)
    sec0.add(
        f"Slå {neck_sts} m op på rundpind. Saml til omg.",
        neck_sts,
        note=f"halsmasker = {neck_sts} (multiplum af {R} til mønsterrapport)",
    )
    sec0.add(
        f"Strik 2 r, 2 vr rib i {body_rib_rows} omg "
        f"(ca. {spec.rib_height_cm:.0f} cm).",
        neck_sts,
    )
    validator.add(Row(sts_before=neck_sts).k(neck_sts))

    # ---- Top-down yoke: 3 increase rounds ---------------------------
    # The Tin Can Knits / EZ factors (×0.75, ×0.70) describe what's left
    # after each *decrease* when reading the yoke bottom-up. For a
    # top-down yoke we walk the same progression in reverse: cast on at
    # neck and INCREASE through three rounds until we reach yoke_start.
    # Mirror image: after_inc1 == after_dec2, after_inc2 == after_dec1.
    after_inc1 = after_dec2
    after_inc2 = after_dec1
    inc1_sts = after_inc1 - neck_sts
    inc2_sts = after_inc2 - after_inc1
    inc3_sts = yoke_start - after_inc2
    inc1_round = round(yoke_rows * 0.15)
    inc2_round = round(yoke_rows * 0.50)
    inc3_round = round(yoke_rows * 0.85)

    sec_inc = p.add_section("Bærestykke (top-down)", sts_before=neck_sts)
    sec_inc.add(
        f"Strik {inc1_round} omg stranded mønster — fra {neck_sts} m. "
        f"Lille motiv-rapport her, da {neck_sts} m kun rummer "
        f"{neck_sts // motif_repeat_width} fulde rapporter.",
        neck_sts,
    )
    sec_inc.add(
        f"1. udtagningsomg: øg {inc1_sts} m jævnt fordelt "
        f"({neck_sts} → {after_inc1} m).",
        after_inc1,
        note=f"praktisk: *strik X m, M1* hvor X ≈ "
             f"{(neck_sts // inc1_sts) if inc1_sts > 0 else 0}",
    )
    sec_inc.add(
        f"Strik {inc2_round - inc1_round} omg stranded mønster.",
        after_inc1,
    )
    sec_inc.add(
        f"2. udtagningsomg: øg {inc2_sts} m jævnt fordelt "
        f"({after_inc1} → {after_inc2} m).",
        after_inc2,
    )
    sec_inc.add(
        f"Strik {inc3_round - inc2_round} omg stranded mønster.",
        after_inc2,
    )
    sec_inc.add(
        f"3. udtagningsomg: øg {inc3_sts} m jævnt fordelt "
        f"({after_inc2} → {yoke_start} m).",
        yoke_start,
        note=f"yoke_start = {yoke_start} = "
             f"{yoke_start // motif_repeat_width} rapporter à {motif_repeat_width} m",
    )
    sec_inc.add(
        f"Strik {yoke_rows - inc3_round} omg stranded mønster.",
        yoke_start,
        note="afslut bærestykket på fuld bredde",
    )
    validator.add(Row(sts_before=yoke_start).k(yoke_start))

    # ---- Adskillelse -------------------------------------------------
    sec3 = p.add_section("Adskillelse af ærmer", sts_before=yoke_start)
    body_sts = body_after_join + 2 * underarm_each
    sec3.add(
        f"Strik over halv ryg, læg {sleeve_after_join} m ærme på vente-snor, "
        f"slå {underarm_each} m op, strik forstykke "
        f"({body_after_join} m), læg andet ærme på vente-snor, "
        f"slå {underarm_each} m op. Saml til omg.",
        body_sts,
        note=f"krop: {body_sts} m ({body_sts*10/g.sts_per_10cm:.1f} cm)",
    )

    # ---- Krop ----------------------------------------------------------
    sec4 = p.add_section("Krop", sts_before=body_sts)
    sec4.add(
        f"Strik glatstrik i {body_plain_rows} omg "
        f"(ca. {spec.body_length_cm - spec.rib_height_cm:.0f} cm).",
        body_sts,
    )
    sec4.add(
        f"Strik 2 r, 2 vr rib i {body_rib_rows} omg.",
        body_sts,
    )
    sec4.add("Luk løst af i rib.", body_sts)

    # ---- Ærmer ----------------------------------------------------------
    sleeve_total_sts = sleeve_after_join + underarm_each
    sec5 = p.add_section("Ærmer (begge ens)", sts_before=sleeve_total_sts)
    sec5.add(
        f"Saml {sleeve_after_join} m fra vente-snor, saml {underarm_each} m "
        f"fra ærmegab. Saml til omg ({sleeve_total_sts} m).",
        sleeve_total_sts,
    )
    sleeve_dec_pairs = max(0, (sleeve_total_sts - wrist_sts) // 2)
    if sleeve_dec_pairs > 0:
        cadence = sleeve_plain_rows / sleeve_dec_pairs
        sec5.add(
            f"Indtagningsomg: k1, ssk, strik til 3 m før omg-slut, k2tog, k1.",
            sleeve_total_sts - 2,
        )
        sec5.add(
            f"Gentag indtagningsomg ca. hver {cadence:.1f}. omg, i alt "
            f"{sleeve_dec_pairs} gange (slut på {wrist_sts} m).",
            wrist_sts,
        )
    sec5.add(
        f"Strik 2 r, 2 vr rib i {sleeve_rib_rows} omg.",
        wrist_sts,
    )
    sec5.add("Luk løst af i rib.", wrist_sts)

    # ---- Afslutning ----------------------------------------------------
    sec6 = p.add_section("Afslutning", sts_before=wrist_sts)
    sec6.add(
        "Hæft alle ender (stranded giver mange ender). Blok efter mål.",
        wrist_sts,
    )

    # ---- Notes ---------------------------------------------------------
    p.notes.append(
        f"Yoke-progression (top-down): {neck_sts} → {after_inc1} → "
        f"{after_inc2} → {yoke_start} m. "
        f"Faktorer (læst nedefra): ×0.75, ×0.70."
    )
    p.notes.append(
        f"Hvert motiv-rapport er {motif_repeat_width} m. "
        f"Antal rapporter: {neck_sts // motif_repeat_width} → "
        f"{after_inc1 // motif_repeat_width} → "
        f"{after_inc2 // motif_repeat_width} → "
        f"{yoke_start // motif_repeat_width}."
    )
    p.notes.append(
        f"Krop: {body_sts} m. Ærme ved overarm: {sleeve_total_sts} m."
    )
    if chart_text:
        p.notes.append("Color-chart (■ = farve A, □ = farve B):")
        p.notes.append(chart_text)

    if yoke_depth_cm < 18:
        p.warnings.append(
            f"Yoke-depth ({yoke_depth_cm:.1f} cm) < 18 cm — 3 indtagningszoner "
            "+ stranded mønster bliver komprimeret. Anbefalet: ≥ 18 cm."
        )
    if neck_sts < motif_repeat_width:
        p.warnings.append(
            f"Halsmasker ({neck_sts}) < motiv-rapport ({motif_repeat_width}). "
            "Mønsteret kan ikke gentages én gang ved halsen."
        )
    if yoke_start_raw % R != 0:
        p.warnings.append(
            f"yoke_start blev rundet fra {yoke_start_raw} til {yoke_start} "
            f"for at passe i {R}-st rapport (afvigelse "
            f"{(yoke_start - yoke_start_raw)*10/g.sts_per_10cm:+.1f} cm)."
        )

    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
