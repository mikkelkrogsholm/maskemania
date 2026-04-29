"""Compound raglan — top-down with independent body and sleeve targets.

Vanilla top-down raglan locks body width and sleeve width together: every
"M1, sm, M1" round adds 2 sts to each panel, so once the yoke has run for
N inc-rounds you have body = back+front+4N and each sleeve = sleeve_seed+2N.
You can't hit a target body width AND a target upper-arm width simultaneously
unless they happen to land at the same N.

Compound raglan fixes that by **staggering** the increase rates: some inc
rounds increase only at body raglans, some only at sleeve raglans, the rest
on all four. The increase budget is computed from the desired final stitch
counts on each panel and distributed evenly across the yoke depth using the
magic formula (Bresenham-style spacing in :mod:`lib.visualisering.shaping`).

Inputs:
  - bust_cm, ease_cm                    → finished bust target
  - upper_arm_cm                        → finished bicep target
  - gauge (Gauge)
  - yoke_depth_cm                       → if None, max(bust/4, upper_arm/2 + 4)
  - body_length_cm, sleeve_length_cm
  - wrist_cm, neck_circumference_cm
  - rib_height_cm
  - underarm_cast_on_cm                 → if None, 5 % of finished bust capped 3-8 cm

Construction model (no raglan stitches at the markers — see raglan_topdown
for the same math reasoning):

  After cast-on (neck_sts), neck is split as back + 2*sleeve_seed + front.
  We define:
      body_seed   = back + front
      arm_seed    = 2 * sleeve_seed
      body_target_after_yoke = bust_sts - underarm_total
      arm_target_after_yoke  = upper_arm_sts - underarm_each (per sleeve)

  Total inc rounds (yoke) ≈ yoke_rows / 2 (every other round).

  body_inc_pairs  = (body_target_after_yoke - body_seed) // 2
  arm_inc_pairs   = (arm_target_after_yoke - sleeve_seed) // 2 (per sleeve)

  In a vanilla raglan, both panels see the same N inc-rounds.
  Here we let them differ: body raglans increase on `body_inc_rounds` rounds,
  sleeve raglans increase on `sleeve_inc_rounds` rounds. The rounds may
  overlap (full raglan round) or be staggered (alternating).

This produces patterns like Tin Can Knits' "Flax Light" or Joji Locatelli's
"Boxy" where bust and bicep are graded independently.
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import (
    Gauge, cm_to_sts, cm_to_rows, Pattern, RowValidator, evenly_spaced,
)
from ..knitrow import KnitRow as Row


_UNDERARM_MIN_CM = 3.0
_UNDERARM_MAX_CM = 8.0


@dataclass
class CompoundRaglanSpec:
    bust_cm: float
    upper_arm_cm: float
    gauge: Gauge
    name: str = "Compound raglan"
    ease_cm: float = 5.0
    yoke_depth_cm: float | None = None
    body_length_cm: float = 36.0
    sleeve_length_cm: float = 45.0
    wrist_cm: float = 18.0
    neck_circumference_cm: float = 42.0
    rib_height_cm: float = 5.0
    underarm_cast_on_cm: float | None = None
    metadata: dict | None = None


def _magic_formula(events: int, slots: int) -> list[int]:
    """Return event indices for `events` increases over `slots` rounds.

    Wraps :func:`evenly_spaced` with a friendlier error: returns ``[]`` if
    events == 0, raises if events > slots.
    """
    if events <= 0:
        return []
    if events > slots:
        raise ValueError(
            f"compound raglan: cannot fit {events} inc events into {slots} "
            "rounds — yoke too shallow or seeds too small"
        )
    return evenly_spaced(events, slots)


def generate_compound_raglan(spec: CompoundRaglanSpec, lang: str = "da") -> Pattern:
    g = spec.gauge
    finished_bust = spec.bust_cm + spec.ease_cm

    # --- yoke depth ---
    if spec.yoke_depth_cm is None:
        yoke_depth_cm = max(finished_bust / 4.0, spec.upper_arm_cm / 2.0 + 4.0)
    else:
        yoke_depth_cm = spec.yoke_depth_cm
    yoke_rows = cm_to_rows(yoke_depth_cm, g)
    inc_rounds_avail = max(1, yoke_rows // 2)  # every-other-round inc

    # --- neck cast-on, distributed back / sleeves / front ---
    neck_sts_total = cm_to_sts(spec.neck_circumference_cm, g, multiple=4)
    if neck_sts_total < 24:
        raise ValueError(
            f"neck circumference {spec.neck_circumference_cm} cm is too small "
            f"({neck_sts_total} sts) for raglan distribution"
        )
    target_back = round(neck_sts_total / 3) + 1
    target_front = round(neck_sts_total / 3) - 1
    target_sleeve = (neck_sts_total - target_back - target_front) // 2
    leftover = neck_sts_total - target_back - target_front - 2 * target_sleeve
    target_back += leftover
    back, front, sleeve_seed = target_back, target_front, target_sleeve

    if sleeve_seed < 4:
        raise ValueError(
            f"compound raglan: only {sleeve_seed} stitches per sleeve at "
            "neck — increase neck_circumference_cm"
        )

    # --- targets at end of yoke ---
    bust_sts = cm_to_sts(finished_bust, g, multiple=2)
    upper_arm_sts = cm_to_sts(spec.upper_arm_cm, g, multiple=2)

    # --- underarm cast-on ---
    if spec.underarm_cast_on_cm is None:
        underarm_each_cm = max(_UNDERARM_MIN_CM,
                                min(_UNDERARM_MAX_CM, finished_bust * 0.05))
    else:
        underarm_each_cm = spec.underarm_cast_on_cm
    underarm_each = cm_to_sts(underarm_each_cm, g)
    underarm_total = 2 * underarm_each

    body_target_after_yoke = bust_sts - underarm_total
    arm_target_after_yoke = upper_arm_sts - underarm_each  # per sleeve

    # --- compute increase budgets ---
    # Body grows by 4 sts per "body inc round" (M1 each side of back AND front).
    # Sleeve grows by 2 sts per "sleeve inc round" (M1 each side, per sleeve).
    body_inc_rounds = max(0, (body_target_after_yoke - (back + front)) // 4)
    sleeve_inc_rounds = max(0, (arm_target_after_yoke - sleeve_seed) // 2)

    # Both must fit inside the yoke window
    if body_inc_rounds > inc_rounds_avail or sleeve_inc_rounds > inc_rounds_avail:
        raise ValueError(
            f"compound raglan: yoke depth ({yoke_depth_cm:.1f} cm, "
            f"{inc_rounds_avail} inc-rounds available) is too short for "
            f"body_inc={body_inc_rounds}, sleeve_inc={sleeve_inc_rounds}. "
            "Increase yoke_depth_cm, upper_arm_cm, or neck_circumference_cm."
        )

    # Place each kind of increase round evenly across the yoke window.
    body_round_idx = set(_magic_formula(body_inc_rounds, inc_rounds_avail))
    sleeve_round_idx = set(_magic_formula(sleeve_inc_rounds, inc_rounds_avail))

    # Final post-yoke counts (panels)
    body_after_yoke = back + front + 4 * body_inc_rounds
    sleeve_after_yoke = sleeve_seed + 2 * sleeve_inc_rounds

    body_sts = body_after_yoke + underarm_total
    sleeve_sts = sleeve_after_yoke + underarm_each

    body_diff_cm = (body_sts - bust_sts) * 10 / g.sts_per_10cm
    sleeve_diff_cm = (sleeve_sts - upper_arm_sts) * 10 / g.sts_per_10cm

    # --- sleeve decreases to wrist ---
    cuff_sts = cm_to_sts(spec.wrist_cm, g, multiple=4)
    sleeve_decreases_pairs = max(0, (sleeve_sts - cuff_sts) // 2)
    sleeve_total_rows = cm_to_rows(spec.sleeve_length_cm - spec.rib_height_cm, g)
    cuff_rib_rows = cm_to_rows(spec.rib_height_cm, g)
    body_rib_rows = cm_to_rows(spec.rib_height_cm, g)
    body_plain_rows = cm_to_rows(spec.body_length_cm - spec.rib_height_cm, g)

    metadata = dict(spec.metadata or {})
    p = Pattern(
        name=spec.name,
        construction="compound_raglan",
        difficulty="intermediate",
        inputs={
            "_domain": "knit",
            "bust_cm": spec.bust_cm,
            "ease_cm": spec.ease_cm,
            "finished_bust_cm": round(finished_bust, 1),
            "upper_arm_cm": spec.upper_arm_cm,
            "wrist_cm": spec.wrist_cm,
            "neck_circumference_cm": spec.neck_circumference_cm,
            "yoke_depth_cm": round(yoke_depth_cm, 1),
            "yoke_inc_rounds_available": inc_rounds_avail,
            "body_inc_rounds": body_inc_rounds,
            "sleeve_inc_rounds": sleeve_inc_rounds,
            "neck_sts": neck_sts_total,
            "back_sts": back,
            "front_sts": front,
            "sleeve_seed_sts": sleeve_seed,
            "body_after_yoke_sts": body_after_yoke,
            "sleeve_after_yoke_sts": sleeve_after_yoke,
            "underarm_each": underarm_each,
            "body_sts": body_sts,
            "sleeve_sts": sleeve_sts,
            "cuff_sts": cuff_sts,
            "body_length_cm": spec.body_length_cm,
            "sleeve_length_cm": spec.sleeve_length_cm,
            "rib_height_cm": spec.rib_height_cm,
            "gauge": {
                "sts_per_10cm": g.sts_per_10cm,
                "rows_per_10cm": g.rows_per_10cm,
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- Halsudskæring -------------------------------------------------
    sec1 = p.add_section("Halsudskæring", sts_before=neck_sts_total)
    sec1.add(
        f"Slå {neck_sts_total} m op på rundpind. Saml til omg.",
        neck_sts_total,
    )
    sec1.add(
        f"Sæt 4 markører: {back} m bag, M1, {sleeve_seed} m ærme, M2, "
        f"{front} m for, M3, {sleeve_seed} m ærme, M4 (= omg-start).",
        neck_sts_total,
        note=f"compound raglan: bust {finished_bust:.0f} cm og overarm "
             f"{spec.upper_arm_cm:.0f} cm grades uafhængigt",
    )
    sec1.add(
        f"Strik 2 r, 2 vr rib i {cuff_rib_rows} omg "
        f"(ca. {spec.rib_height_cm:.0f} cm).",
        neck_sts_total,
    )
    validator.add(Row(sts_before=neck_sts_total).k(neck_sts_total))

    # ---- Bærestykke ----------------------------------------------------
    sec2 = p.add_section("Bærestykke (compound)", sts_before=neck_sts_total)
    sec2.add(
        f"Skift mellem indtagningsomg og plain omg. {inc_rounds_avail} "
        f"indtagningsomg er til rådighed over {yoke_rows} omg yoke.",
        neck_sts_total,
        note=f"yoke depth ≈ {yoke_depth_cm:.1f} cm",
    )
    sec2.add(
        f"Heraf strikkes {body_inc_rounds} *body-inc-omg* "
        f"(M1L, sm, M1R kun ved M1 og M3 — ryg + forstykke vokser, +4 m). "
        f"Fordeles jævnt i indt-omg #: "
        f"{sorted([i+1 for i in body_round_idx])[:8]}{' ...' if len(body_round_idx) > 8 else ''}.",
        neck_sts_total + 4 * body_inc_rounds,
        note="øger kun body-panelerne",
    )
    sec2.add(
        f"Og {sleeve_inc_rounds} *sleeve-inc-omg* "
        f"(M1L, sm, M1R kun ved M2 og M4 — ærmer vokser, +4 m). "
        f"Fordeles jævnt i indt-omg #: "
        f"{sorted([i+1 for i in sleeve_round_idx])[:8]}{' ...' if len(sleeve_round_idx) > 8 else ''}.",
        neck_sts_total + 4 * body_inc_rounds + 4 * sleeve_inc_rounds,
        note="øger kun ærmerne",
    )
    sts_after_yoke = body_after_yoke + 2 * sleeve_after_yoke
    sec2.add(
        f"Yoke-slut: {body_after_yoke} m krop "
        f"+ {2*sleeve_after_yoke} m ærmer ({sleeve_after_yoke} pr. ærme) "
        f"= {sts_after_yoke} m i alt.",
        sts_after_yoke,
        note=f"body-mål {body_target_after_yoke}, "
             f"ærme-mål {arm_target_after_yoke} pr. ærme",
    )
    # validator: representative inc round (4 inc total when both fire)
    # We just validate one plain round at yoke-end for sanity.
    validator.add(Row(sts_before=sts_after_yoke).k(sts_after_yoke))

    # ---- Adskillelse ---------------------------------------------------
    sec3 = p.add_section("Adskillelse af ærmer", sts_before=sts_after_yoke)
    sec3.add(
        f"Strik over ryg, læg ærme på vente-snor, slå {underarm_each} m op, "
        f"strik over forstykke, læg andet ærme på vente-snor, "
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

    # ---- Ærmer ---------------------------------------------------------
    sec5 = p.add_section("Ærmer (begge ens)", sts_before=sleeve_sts)
    sec5.add(
        f"Saml {sleeve_after_yoke} m fra vente-snor, saml {underarm_each} m "
        f"fra ærmegab. Saml til omg ({sleeve_sts} m).",
        sleeve_sts,
    )
    if sleeve_decreases_pairs > 0:
        cadence = sleeve_total_rows / max(sleeve_decreases_pairs, 1)
        sec5.add(
            f"Indtagningsomg: k1, ssk, strik til 3 m før omg-slut, k2tog, k1.",
            sleeve_sts - 2,
            note="-2 m pr. indtagningsomg",
        )
        sec5.add(
            f"Gentag indtagningsomg ca. hver {cadence:.1f}. omg, i alt "
            f"{sleeve_decreases_pairs} gange.",
            cuff_sts,
            note=f"slut på {cuff_sts} m",
        )
    sec5.add(
        f"Strik 2 r, 2 vr rib i {cuff_rib_rows} omg.",
        cuff_sts,
    )
    sec5.add("Luk løst af i rib.", cuff_sts)

    # ---- Afslutning ----------------------------------------------------
    sec6 = p.add_section("Afslutning", sts_before=cuff_sts)
    sec6.add("Hæft alle ender. Blok til mål.", cuff_sts)

    # ---- Notes & warnings ---------------------------------------------
    p.notes.append(
        f"Compound raglan: {body_inc_rounds} body-inc-omg + "
        f"{sleeve_inc_rounds} sleeve-inc-omg fordelt jævnt over "
        f"{inc_rounds_avail} mulige indt-omg i bærestykket."
    )
    p.notes.append(
        f"Krop {body_sts} m → mål {bust_sts} m. Afvigelse: {body_diff_cm:+.1f} cm."
    )
    p.notes.append(
        f"Ærme ved overarm {sleeve_sts} m → mål {upper_arm_sts} m. "
        f"Afvigelse: {sleeve_diff_cm:+.1f} cm."
    )

    if abs(body_diff_cm) > 2:
        p.warnings.append(
            f"Krop afviger {body_diff_cm:+.1f} cm fra brystmålet — overvej "
            "at justere underarm_cast_on_cm eller ease_cm."
        )
    if abs(sleeve_diff_cm) > 2:
        p.warnings.append(
            f"Ærme afviger {sleeve_diff_cm:+.1f} cm fra overarm — yoke kan "
            "være for kort eller dybt; juster yoke_depth_cm."
        )
    if body_inc_rounds + sleeve_inc_rounds > inc_rounds_avail:
        # this state is unreachable because we error above, but keep for safety
        p.warnings.append(
            "Body- og sleeve-inc-omg overlapper i flere omg end ventet — "
            "yoke er meget tæt pakket."
        )

    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
