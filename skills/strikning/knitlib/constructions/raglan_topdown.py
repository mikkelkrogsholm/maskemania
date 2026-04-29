"""Top-down raglan sweater generator.

Construction model: **0-stitch raglan** — increases happen at 4 markers, no
raglan-line stitches. This is mathematically the cleanest model and matches
many modern patterns (e.g., Tin Can Knits Flax). For visible raglan seams,
the formatter can render the increase round as "M1R, k1, sm, k1, M1L" and
the user can choose to read those as "raglan stitches"; the math doesn't
care.

Steps:
  1. Cast on neck stitches; distribute back / right-sleeve / front / left-sleeve.
     Bias back > front by 2 sts (back-of-neck arc is longer).
  2. Optional back-neck short rows before joining (default: on for adult sizes).
  3. Increase 8 sts every other round (2 increases at each of 4 markers).
  4. After yoke, separate body from sleeves; cast on underarm sts.
  5. Body: knit straight to hem - rib, work rib, bind off.
  6. Sleeves: pick up + underarm. Reserve top/bottom buffers, then
     distribute decreases evenly across the middle to reach cuff sts.

The auto-derived defaults follow modern best practice:
  - yoke_depth_cm = max(bust/4, upper_arm/2 + 4)  — research consensus
  - underarm_cast_on capped to 3-8 cm per side (avoids tight underarm)

Sources for the design choices: Tin Can Knits, PetiteKnit, Susanna Winter,
Sister Mountain, EZ Percentage System (see reference/workflow.md).
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import Gauge, cm_to_sts, cm_to_rows, evenly_spaced, Pattern


@dataclass
class RaglanSpec:
    bust_cm: float                         # body bust circumference
    gauge: Gauge
    name: str = "Top-down raglan"
    ease_cm: float = 5.0                   # standard fit
    yoke_depth_cm: float | None = None     # default: max(bust/4, upper_arm/2 + 4)
    body_length_cm: float = 36.0           # underarm to hem
    sleeve_length_cm: float = 45.0         # underarm to cuff
    upper_arm_cm: float = 31.0             # bicep target circumference
    wrist_cm: float = 18.0                 # cuff target circumference
    neck_circumference_cm: float = 42.0
    rib_height_cm: float = 5.0
    underarm_cast_on_cm: float | None = None  # auto if None
    back_neck_shortrows: bool = True       # adult default; set False for kids
    sleeve_top_buffer_cm: float = 4.0      # plain rounds before sleeve dec start
    sleeve_bottom_buffer_cm: float = 4.0   # plain rounds after last sleeve dec


# --- bounds for auto-computed underarm cast-on ---
_UNDERARM_MIN_CM = 3.0
_UNDERARM_MAX_CM = 8.0


def _l(da: str, en: str, lang: str) -> str:
    return en if lang == "en" else da


def generate_raglan(spec: RaglanSpec, lang: str = "da") -> Pattern:
    g = spec.gauge
    finished_bust = spec.bust_cm + spec.ease_cm

    # --- yoke depth: max of bust/4 and upper_arm/2 + 4 ---
    yoke_from_bust = finished_bust / 4.0
    yoke_from_arm = spec.upper_arm_cm / 2.0 + 4.0
    if spec.yoke_depth_cm is None:
        yoke_depth_cm = max(yoke_from_bust, yoke_from_arm)
    else:
        yoke_depth_cm = spec.yoke_depth_cm
    yoke_rounds = cm_to_rows(yoke_depth_cm, g)
    increase_rounds = yoke_rounds // 2

    # --- neck: distribute over 4 panels (no raglan stitches) ---
    neck_sts_total = cm_to_sts(spec.neck_circumference_cm, g, multiple=4)
    if neck_sts_total < 24:
        raise ValueError(
            f"neck circumference {spec.neck_circumference_cm} cm is too small "
            f"({neck_sts_total} sts) for raglan distribution"
        )
    # back ≈ 1/3, front ≈ 1/3 - 2 sts (front bias correction), each sleeve ≈ 1/6.
    # Modern practice: back > front by 2 sts so neckline doesn't ride up.
    target_back = round(neck_sts_total / 3) + 1
    target_front = round(neck_sts_total / 3) - 1
    target_sleeve = (neck_sts_total - target_back - target_front) // 2
    leftover = neck_sts_total - target_back - target_front - 2 * target_sleeve
    target_back += leftover  # absorb rounding remainder into back

    back, front, sleeve = target_back, target_front, target_sleeve
    if sleeve < 4:
        raise ValueError(f"neck distribution leaves only {sleeve} sleeve sts; "
                         "increase neck_circumference_cm")

    # --- yoke increases ---
    # 8 incs/round (2 at each of 4 markers): each panel grows by 2 per inc round
    body_after_yoke = back + front + 4 * increase_rounds
    each_sleeve_after_yoke = sleeve + 2 * increase_rounds
    sts_after_yoke = neck_sts_total + 8 * increase_rounds

    # --- body separation: cast on underarm sts ---
    target_body_sts = cm_to_sts(finished_bust, g, multiple=2)

    if spec.underarm_cast_on_cm is None:
        # Try to close the gap with auto underarm CO, but cap to physical bounds
        gap = target_body_sts - body_after_yoke  # may be negative
        gap_per_side = max(0, gap) // 2
        # Convert physical bounds to sts
        min_sts_per_side = cm_to_sts(_UNDERARM_MIN_CM, g)
        max_sts_per_side = cm_to_sts(_UNDERARM_MAX_CM, g)
        underarm_each = max(min_sts_per_side,
                            min(max_sts_per_side, gap_per_side))
    else:
        underarm_each = cm_to_sts(spec.underarm_cast_on_cm, g)
    underarm_total = 2 * underarm_each

    body_sts = body_after_yoke + underarm_total
    body_diff_cm = (body_sts - target_body_sts) * 10 / g.sts_per_10cm

    # --- sleeve sts after picking up underarm ---
    sleeve_total_sts = each_sleeve_after_yoke + underarm_each
    target_upper_arm_sts = cm_to_sts(spec.upper_arm_cm, g, multiple=2)
    sleeve_diff_cm = (sleeve_total_sts - target_upper_arm_sts) * 10 / g.sts_per_10cm

    # --- sleeve decreases (with top/bottom buffers) ---
    cuff_sts = cm_to_sts(spec.wrist_cm, g, multiple=4)
    sleeve_decreases_pairs = max(0, (sleeve_total_sts - cuff_sts) // 2)
    sleeve_total_rows = cm_to_rows(spec.sleeve_length_cm - spec.rib_height_cm, g)
    top_buffer_rows = cm_to_rows(spec.sleeve_top_buffer_cm, g)
    bot_buffer_rows = cm_to_rows(spec.sleeve_bottom_buffer_cm, g)
    sleeve_dec_window = max(1, sleeve_total_rows - top_buffer_rows - bot_buffer_rows)
    cuff_rib_rows = cm_to_rows(spec.rib_height_cm, g)
    body_rib_rows = cm_to_rows(spec.rib_height_cm, g)
    body_plain_rows = cm_to_rows(spec.body_length_cm - spec.rib_height_cm, g)

    # --- build pattern ---
    p = Pattern(
        name=spec.name,
        construction="raglan_topdown",
        difficulty="easy",
        inputs={
            "_domain": "knit",
            "bust_cm": spec.bust_cm,
            "ease_cm": spec.ease_cm,
            "finished_bust_cm": round(finished_bust, 1),
            "gauge": {"sts_per_10cm": g.sts_per_10cm,
                      "rows_per_10cm": g.rows_per_10cm},
            "yoke_depth_cm": round(yoke_depth_cm, 1),
            "yoke_depth_source":
                "max(bust/4, upper_arm/2 + 4)" if spec.yoke_depth_cm is None
                else "user-specified",
            "body_length_cm": spec.body_length_cm,
            "sleeve_length_cm": spec.sleeve_length_cm,
            "neck_circumference_cm": spec.neck_circumference_cm,
            "wrist_cm": spec.wrist_cm,
            "upper_arm_cm": spec.upper_arm_cm,
            "back_neck_shortrows": spec.back_neck_shortrows,
        },
    )

    # 1. Halsudskæring
    sec1 = p.add_section(
        _l("Halsudskæring", "Neckline", lang), sts_before=neck_sts_total)
    sec1.add(
        _l(f"Slå {neck_sts_total} m op på rundpind. Saml til omgang.",
           f"Cast on {neck_sts_total} sts on a circular needle. Join in the round.",
           lang),
        neck_sts_total,
    )
    sec1.add(
        _l(f"Fordel og sæt 4 markører: {back} m bag, sæt markør (M1), "
           f"{sleeve} m ærme, M2, {front} m forstykke, M3, "
           f"{sleeve} m ærme, M4 (= omgangens start).",
           f"Distribute and place 4 markers: {back} sts back, place marker (M1), "
           f"{sleeve} sts sleeve, M2, {front} sts front, M3, "
           f"{sleeve} sts sleeve, M4 (= start of round).",
           lang),
        neck_sts_total,
        note=_l(f"back {back} > front {front} (2 m) for at undgå at halsen rider op",
                f"back {back} > front {front} (2 sts) so the neckline does not ride up",
                lang),
    )
    sec1.add(
        _l(f"Strik 2 r, 2 vr rib i {cuff_rib_rows} omg "
           f"(ca. {spec.rib_height_cm} cm).",
           f"Work k2, p2 rib for {cuff_rib_rows} rounds "
           f"(about {spec.rib_height_cm} cm).",
           lang),
        neck_sts_total,
    )

    # 2. Optional back-neck short rows
    if spec.back_neck_shortrows:
        sec_sr = p.add_section(
            _l("Korte rækker bagstykke (valgfrit)",
               "Back-neck short rows (optional)", lang),
            sts_before=neck_sts_total,
        )
        sr_pairs = 4  # standard: 4-6 short-row pairs work well
        sec_sr.add(
            _l(f"Strik {sr_pairs} korte-rækker-par hen over bagstykket "
               f"(tysk korte rækker eller 'wrap & turn'). Hver kort række "
               f"strækker bagstykket {sr_pairs} pinde højere end forstykket.",
               f"Work {sr_pairs} pairs of short rows across the back "
               f"(German short rows or 'wrap & turn'). Each pair raises the "
               f"back {sr_pairs} rows above the front.",
               lang),
            neck_sts_total,
            note=_l("modvirker at halsen kvæler. Spring over for små str/børn",
                    "prevents the neckline from choking. Skip for small sizes / kids",
                    lang),
        )

    # 3. Bærestykke
    sec2 = p.add_section(_l("Bærestykke", "Yoke", lang), sts_before=neck_sts_total)
    sec2.add(
        _l("Indtagningsomg: *strik til 1 m før markør, M1R, sm, M1L* "
           "gentag for alle 4 markører.",
           "Increase round: *knit to 1 st before marker, M1R, sm, M1L* "
           "repeat for all 4 markers.",
           lang),
        neck_sts_total + 8,
        note=_l("8 udtagninger pr. omgang", "8 increases per round", lang),
    )
    sec2.add(
        _l(f"Skift mellem en udtagningsomg og en plain omg. "
           f"Gentag i alt {increase_rounds} udtagningsomgange "
           f"({2 * increase_rounds} omg total ≈ {yoke_depth_cm:.0f} cm).",
           f"Alternate increase round and plain round. "
           f"Repeat for a total of {increase_rounds} increase rounds "
           f"({2 * increase_rounds} rnds total ≈ {yoke_depth_cm:.0f} cm).",
           lang),
        sts_after_yoke,
        note=_l(f"slut: {sts_after_yoke} m = {body_after_yoke} m krop "
                f"+ {2*each_sleeve_after_yoke} m ærmer "
                f"({each_sleeve_after_yoke} pr. ærme)",
                f"end: {sts_after_yoke} sts = {body_after_yoke} sts body "
                f"+ {2*each_sleeve_after_yoke} sts sleeves "
                f"({each_sleeve_after_yoke} per sleeve)",
                lang),
    )

    # 4. Adskil ærmer fra krop
    body_back_panel = back + 2 * increase_rounds
    body_front_panel = front + 2 * increase_rounds
    sec3 = p.add_section(
        _l("Adskillelse af ærmer", "Sleeve separation", lang),
        sts_before=sts_after_yoke,
    )
    sec3.add(
        _l(f"Strik over ryg ({body_back_panel} m), "
           f"sæt {each_sleeve_after_yoke} m på vente-snor (ærme), "
           f"slå {underarm_each} m op til ærmegab, "
           f"strik over forstykke ({body_front_panel} m), "
           f"sæt næste {each_sleeve_after_yoke} m på vente-snor, "
           f"slå {underarm_each} m op til ærmegab. Saml til omgang.",
           f"Knit across the back ({body_back_panel} sts), "
           f"place {each_sleeve_after_yoke} sts on waste yarn (sleeve), "
           f"cast on {underarm_each} sts at the underarm, "
           f"knit across the front ({body_front_panel} sts), "
           f"place the next {each_sleeve_after_yoke} sts on waste yarn, "
           f"cast on {underarm_each} sts at the underarm. Join in the round.",
           lang),
        body_sts,
        note=_l(f"krop: {body_sts} m ({body_sts*10/g.sts_per_10cm:.1f} cm)",
                f"body: {body_sts} sts ({body_sts*10/g.sts_per_10cm:.1f} cm)",
                lang),
    )

    # 5. Krop
    sec4 = p.add_section(_l("Krop", "Body", lang), sts_before=body_sts)
    sec4.add(
        _l(f"Strik glatstrik i {body_plain_rows} omg "
           f"(ca. {spec.body_length_cm - spec.rib_height_cm:.0f} cm).",
           f"Knit stockinette for {body_plain_rows} rounds "
           f"(about {spec.body_length_cm - spec.rib_height_cm:.0f} cm).",
           lang),
        body_sts,
    )
    sec4.add(
        _l(f"Strik 2 r, 2 vr rib i {body_rib_rows} omg "
           f"(ca. {spec.rib_height_cm} cm).",
           f"Work k2, p2 rib for {body_rib_rows} rounds "
           f"(about {spec.rib_height_cm} cm).",
           lang),
        body_sts,
    )
    sec4.add(_l("Luk løst af i rib.", "Bind off loosely in rib.", lang), body_sts)

    # 6. Ærmer
    sec5 = p.add_section(
        _l("Ærmer (begge ens)", "Sleeves (both alike)", lang),
        sts_before=sleeve_total_sts,
    )
    sec5.add(
        _l(f"Sæt {each_sleeve_after_yoke} m fra vente-snor på rundpind. "
           f"Saml {underarm_each} m fra ærmegab. Saml til omgang. "
           f"({sleeve_total_sts} m i alt — ca. {sleeve_total_sts*10/g.sts_per_10cm:.1f} cm).",
           f"Place {each_sleeve_after_yoke} sts from waste yarn onto a circular needle. "
           f"Pick up {underarm_each} sts at the underarm. Join in the round. "
           f"({sleeve_total_sts} sts total — about {sleeve_total_sts*10/g.sts_per_10cm:.1f} cm).",
           lang),
        sleeve_total_sts,
    )
    if sleeve_decreases_pairs > 0:
        cadence = sleeve_dec_window / max(sleeve_decreases_pairs, 1)
        sec5.add(
            _l(f"Strik {top_buffer_rows} omg ret som plain bicep-buffer.",
               f"Knit {top_buffer_rows} plain rounds as a bicep buffer.",
               lang),
            sleeve_total_sts,
            note=_l(f"~{spec.sleeve_top_buffer_cm} cm uden indtagninger ved oversiden",
                    f"~{spec.sleeve_top_buffer_cm} cm without decreases at the top",
                    lang),
        )
        sec5.add(
            _l(f"Indtagningsomg: k1, ssk (= 2 dr r sm), strik til 3 m før omg-slut, "
               f"k2tog (= 2 r sm), k1.",
               f"Decrease round: k1, ssk, knit to 3 sts before end of round, "
               f"k2tog, k1.",
               lang),
            sleeve_total_sts - 2,
            note=_l("-2 m pr. indtagningsomg", "-2 sts per decrease round", lang),
        )
        sec5.add(
            _l(f"Gentag indtagningsomg ca. hver {cadence:.1f}. omg, i alt "
               f"{sleeve_decreases_pairs} gange jævnt fordelt over "
               f"{sleeve_dec_window} omg.",
               f"Repeat the decrease round about every {cadence:.1f} rnds, a "
               f"total of {sleeve_decreases_pairs} times spread evenly over "
               f"{sleeve_dec_window} rnds.",
               lang),
            cuff_sts,
            note=_l(f"slut på {cuff_sts} m ({cuff_sts*10/g.sts_per_10cm:.1f} cm)",
                    f"end on {cuff_sts} sts ({cuff_sts*10/g.sts_per_10cm:.1f} cm)",
                    lang),
        )
        sec5.add(
            _l(f"Strik {bot_buffer_rows} omg ret som plain manchet-buffer.",
               f"Knit {bot_buffer_rows} plain rounds as a cuff buffer.",
               lang),
            cuff_sts,
            note=_l(f"~{spec.sleeve_bottom_buffer_cm} cm uden indtagninger før manchetten",
                    f"~{spec.sleeve_bottom_buffer_cm} cm without decreases before the cuff",
                    lang),
        )
    else:
        sec5.add(
            _l(f"Strik glatstrik uden indtagninger i {sleeve_total_rows} omg.",
               f"Knit stockinette without decreases for {sleeve_total_rows} rounds.",
               lang),
            sleeve_total_sts,
        )
    sec5.add(
        _l(f"Strik 2 r, 2 vr rib i {cuff_rib_rows} omg.",
           f"Work k2, p2 rib for {cuff_rib_rows} rounds.",
           lang),
        cuff_sts,
    )
    sec5.add(
        _l("Luk løst af i rib. Strik andet ærme magen til.",
           "Bind off loosely in rib. Knit the second sleeve the same way.",
           lang),
        cuff_sts,
    )

    # 7. Afslutning
    sec6 = p.add_section(
        _l("Afslutning", "Finishing", lang), sts_before=cuff_sts)
    sec6.add(
        _l("Hæft alle ender. Blok trøjen til ønskede mål.",
           "Weave in all ends. Block the sweater to the desired measurements.",
           lang),
        cuff_sts,
    )

    # --- notes & warnings ---
    p.notes.append(
        f"Halsmasker: {neck_sts_total} = {back} ryg + {front} for + "
        f"{sleeve}+{sleeve} ærmer (back > front med 2 m)."
    )
    p.notes.append(
        f"Krop: {body_sts} m. Mål-bryst {finished_bust:.1f} cm "
        f"({target_body_sts} m). Afvigelse: {body_diff_cm:+.1f} cm."
    )
    p.notes.append(
        f"Ærme ved overarm: {sleeve_total_sts} m "
        f"({sleeve_total_sts*10/g.sts_per_10cm:.1f} cm). "
        f"Mål-overarm {spec.upper_arm_cm:.0f} cm "
        f"({target_upper_arm_sts} m). Afvigelse: {sleeve_diff_cm:+.1f} cm."
    )
    p.notes.append(
        f"Underarm cast-on: {underarm_each} m pr. side "
        f"({underarm_each*10/g.sts_per_10cm:.1f} cm)."
    )

    # Fit warnings
    if abs(body_diff_cm) > 3:
        p.warnings.append(
            f"Kroppens bredde afviger {body_diff_cm:+.1f} cm fra brystmålet. "
            f"Justér yoke_depth_cm, neck_circumference_cm eller "
            f"underarm_cast_on_cm — eller acceptér afvigelsen."
        )
    if abs(sleeve_diff_cm) > 3:
        p.warnings.append(
            f"Ærmet ved overarm afviger {sleeve_diff_cm:+.1f} cm fra "
            f"upper_arm_cm. Top-down raglans tillader ikke uafhængig "
            f"styring af ærmebredde uden compound-raglan; overvej at "
            f"justere yoke_depth_cm og/eller upper_arm_cm."
        )
    if yoke_depth_cm < spec.upper_arm_cm / 2 + 3:
        p.warnings.append(
            f"Bærestykket ({yoke_depth_cm:.1f} cm) er lavt i forhold til "
            f"overarmen ({spec.upper_arm_cm} cm). Risiko for stramme "
            f"ærmegab. Anbefalet minimum: {spec.upper_arm_cm/2 + 3:.0f} cm."
        )
    underarm_cm = underarm_each * 10 / g.sts_per_10cm
    if underarm_cm < _UNDERARM_MIN_CM + 0.5:
        p.warnings.append(
            f"Underarm cast-on er kun {underarm_cm:.1f} cm pr. side. "
            f"Mindre end {_UNDERARM_MIN_CM} cm giver ofte stramme ærmegab."
        )
    if underarm_cm > _UNDERARM_MAX_CM - 0.5:
        p.warnings.append(
            f"Underarm cast-on er {underarm_cm:.1f} cm pr. side — "
            f"i den høje ende. Ærmegabet kan blive 'sækket'."
        )
    if spec.neck_circumference_cm < 40:
        p.warnings.append(
            f"Halsomkreds ({spec.neck_circumference_cm} cm) er smal — "
            f"tjek at trøjen kan trækkes over hovedet (≈ 56 cm omkreds for "
            f"voksne). Brug en stretchy aflukning."
        )
    if sleeve_decreases_pairs > 0:
        cadence = sleeve_dec_window / sleeve_decreases_pairs
        if cadence < 4:
            p.warnings.append(
                f"Ærmeindtagninger sker hver {cadence:.1f}. omg — meget "
                f"aggressiv (under hver 4. omg). Ærmet kan blive 'kegleformet'."
            )
    if increase_rounds < 12:
        p.warnings.append(
            "Få bærestykke-udtagninger — bærestykket bliver kort. "
            "Tjek yoke_depth_cm og row gauge."
        )

    return p
