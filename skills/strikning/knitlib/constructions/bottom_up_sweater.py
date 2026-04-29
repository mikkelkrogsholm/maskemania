"""Bottom-up sweater generator using Elizabeth Zimmermann's EPS percentages.

Construction (Agent A's research §1):

  K = body_sts at chest = round((bust_cm + ease_cm) / 10 · gauge_st)

  Standard EPS percentages of K:
    body cast-on:  90 %
    sleeve cuff:   20 %
    sleeve top:    35 %
    underarm hold:  8 %  (held at each underarm, on body and on sleeve)
    neck:          40 %
    yoke depth:    (bust_cm + ease_cm) / 4

  After working body to ``body_length - yoke_depth`` and each sleeve to
  ``sleeve_length - yoke_depth`` with magic-formula increases from cuff
  to top, we *join* by knitting body sts → first sleeve sts (skipping
  the underarm hold on each) → body → second sleeve. Yoke is then
  shaped raglan-style (8 dec / 2nd round) until neck stitches remain.

This implementation focuses on bottom-up + yoke-style raglan join. It
emits a Pattern with the same structural shape as ``raglan_topdown.py``
so the renderer treats them analogously.
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import (
    Gauge, cm_to_sts, cm_to_rows, Pattern, RowValidator,
)
from ..knitrow import KnitRow as Row


# EPS percentage table — keep separate from the function so callers can read
# the canonical recipe.
EPS_PERCENTAGES_DEFAULT = {
    "body":      0.90,
    "sleeve_cuff": 0.20,
    "sleeve_top":  0.35,
    "underarm":    0.08,
    "neck":        0.40,
}


def eps_percentages(K: int, style: str = "yoke") -> dict[str, int]:
    """Return the EPS counts for a given key number K.

    ``style``:
      - ``"yoke"`` / ``"raglan"`` → standard EPS (default)
      - ``"drop"``                → boxier silhouette (body 100 % of K)
    """
    pct = dict(EPS_PERCENTAGES_DEFAULT)
    if style == "drop":
        pct["body"] = 1.00
    elif style not in ("yoke", "raglan"):
        raise ValueError(f"unknown style {style!r}")
    return {name: max(2, round(K * p)) for name, p in pct.items()}


@dataclass
class BottomUpSweaterSpec:
    bust_cm: float
    gauge: Gauge
    name: str = "Bottom-up sweater"
    ease_cm: float = 5.0
    body_length_cm: float = 36.0      # cast-on to underarm
    sleeve_length_cm: float = 45.0    # cuff to underarm
    upper_arm_cm: float | None = None  # if None: derived from EPS 35 %
    wrist_cm: float | None = None      # if None: derived from EPS 20 %
    neck_circumference_cm: float | None = None  # if None: EPS 40 %
    rib_height_cm: float = 5.0
    style: str = "yoke"
    metadata: dict | None = None


def _l(da: str, en: str, lang: str) -> str:
    return en if lang == "en" else da


def generate_bottom_up_sweater(spec: BottomUpSweaterSpec, lang: str = "da") -> Pattern:
    g = spec.gauge
    finished_bust = spec.bust_cm + spec.ease_cm

    # K = body sts at the chest (the EPS "key number")
    K = cm_to_sts(finished_bust, g, multiple=2)
    if K < 80:
        # Tiny K means tiny sweater; warn but proceed
        pass

    eps = eps_percentages(K, style=spec.style)
    body_sts = eps["body"]
    sleeve_cuff_sts = eps["sleeve_cuff"]
    sleeve_top_sts = eps["sleeve_top"]
    underarm_sts = eps["underarm"]
    neck_sts = eps["neck"]

    # Make sure sleeve & body underarm holds match exactly (round both ways)
    underarm_sts = max(underarm_sts, 2)
    yoke_depth_cm = finished_bust / 4.0
    yoke_rounds = cm_to_rows(yoke_depth_cm, g)

    # If user provided physical sizes, override the EPS-derived counts
    if spec.upper_arm_cm:
        sleeve_top_sts = cm_to_sts(spec.upper_arm_cm, g, multiple=2)
    if spec.wrist_cm:
        sleeve_cuff_sts = cm_to_sts(spec.wrist_cm, g, multiple=4)
    if spec.neck_circumference_cm:
        neck_sts = cm_to_sts(spec.neck_circumference_cm, g, multiple=4)

    # Body & sleeve plain rounds before underarm
    body_rib_rows = cm_to_rows(spec.rib_height_cm, g)
    body_plain_rows = max(0,
        cm_to_rows(spec.body_length_cm - spec.rib_height_cm, g) - 0)
    sleeve_rib_rows = cm_to_rows(spec.rib_height_cm, g)
    sleeve_plain_rows = max(0,
        cm_to_rows(spec.sleeve_length_cm - spec.rib_height_cm, g) - 0)

    # Sleeve increases (magic formula): grow from cuff to top
    sleeve_inc_pairs = max(0, (sleeve_top_sts - sleeve_cuff_sts) // 2)
    if sleeve_plain_rows > 0 and sleeve_inc_pairs > 0:
        sleeve_inc_cadence = sleeve_plain_rows / sleeve_inc_pairs
    else:
        sleeve_inc_cadence = 0

    # After joining: body has body_sts, each sleeve has sleeve_top_sts.
    # We hold ``underarm_sts`` on each side of the body and on each sleeve.
    body_after_join = body_sts - 2 * underarm_sts
    sleeve_after_join = sleeve_top_sts - 2 * underarm_sts
    if sleeve_after_join < 4:
        raise ValueError(
            f"sleeve_top_sts ({sleeve_top_sts}) - 2·underarm "
            f"({2 * underarm_sts}) = {sleeve_after_join} < 4. "
            "Bump upper_arm_cm or reduce ease."
        )
    yoke_start_sts = body_after_join + 2 * sleeve_after_join

    # Yoke: 8 decreases per shaping round (raglan-style), every other round
    decreases_target = yoke_start_sts - neck_sts
    if decreases_target < 0:
        decreases_target = 0
    yoke_dec_rounds = max(0, decreases_target // 8)

    metadata = dict(spec.metadata or {})
    p = Pattern(
        name=spec.name,
        construction="bottom_up_sweater",
        difficulty="easy",
        inputs={
            "_domain": "knit",
            "bust_cm": spec.bust_cm,
            "ease_cm": spec.ease_cm,
            "finished_bust_cm": round(finished_bust, 1),
            "K": K,
            "body_sts": body_sts,
            "sleeve_cuff_sts": sleeve_cuff_sts,
            "sleeve_top_sts": sleeve_top_sts,
            "underarm_sts": underarm_sts,
            "neck_sts": neck_sts,
            "yoke_start_sts": yoke_start_sts,
            "yoke_depth_cm": round(yoke_depth_cm, 1),
            "yoke_dec_rounds": yoke_dec_rounds,
            "body_length_cm": spec.body_length_cm,
            "sleeve_length_cm": spec.sleeve_length_cm,
            "neck_circumference_cm": (spec.neck_circumference_cm
                                       or round(neck_sts * 10 / g.sts_per_10cm, 1)),
            "upper_arm_cm": (spec.upper_arm_cm
                              or round(sleeve_top_sts * 10 / g.sts_per_10cm, 1)),
            "wrist_cm": (spec.wrist_cm
                          or round(sleeve_cuff_sts * 10 / g.sts_per_10cm, 1)),
            "rib_height_cm": spec.rib_height_cm,
            "style": spec.style,
            "gauge": {
                "sts_per_10cm": g.sts_per_10cm,
                "rows_per_10cm": g.rows_per_10cm,
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- Krop ----------------------------------------------------------
    sec1 = p.add_section(
        _l("Krop — opslag og rib", "Body — cast on and rib", lang),
        sts_before=body_sts,
    )
    sec1.add(
        _l(f"Slå {body_sts} m op på rundpind. Saml til omg uden at sno.",
           f"Cast on {body_sts} sts on a circular needle. Join in the round without twisting.",
           lang),
        body_sts,
        note=_l(f"K = {K} (EPS key number); kropsmasker = round(K·90 %) = {body_sts}",
                f"K = {K} (EPS key number); body sts = round(K·90%) = {body_sts}",
                lang),
    )
    sec1.add(
        _l(f"Strik 2 r, 2 vr rib i {body_rib_rows} omg "
           f"(ca. {spec.rib_height_cm:.0f} cm).",
           f"Work k2, p2 rib for {body_rib_rows} rounds "
           f"(about {spec.rib_height_cm:.0f} cm).",
           lang),
        body_sts,
    )
    sec1.add(
        _l(f"Skift til glatstrik. Strik {body_plain_rows} omg "
           f"(ca. {spec.body_length_cm - spec.rib_height_cm:.0f} cm) "
           "til underarm-niveau.",
           f"Switch to stockinette. Knit {body_plain_rows} rounds "
           f"(about {spec.body_length_cm - spec.rib_height_cm:.0f} cm) "
           "to the underarm.",
           lang),
        body_sts,
    )
    validator.add(Row(sts_before=body_sts).k(body_sts))

    # ---- Ærmer ---------------------------------------------------------
    sec2 = p.add_section(
        _l("Ærmer (begge ens)", "Sleeves (both alike)", lang),
        sts_before=sleeve_cuff_sts,
    )
    sec2.add(
        _l(f"Slå {sleeve_cuff_sts} m op på strømpepinde / magic-loop. "
           "Saml til omg.",
           f"Cast on {sleeve_cuff_sts} sts on DPNs / magic-loop. "
           "Join in the round.",
           lang),
        sleeve_cuff_sts,
        note=_l(f"manchet = round(K·20 %) = {sleeve_cuff_sts}",
                f"cuff = round(K·20%) = {sleeve_cuff_sts}", lang),
    )
    sec2.add(
        _l(f"Strik 2 r, 2 vr rib i {sleeve_rib_rows} omg.",
           f"Work k2, p2 rib for {sleeve_rib_rows} rounds.",
           lang),
        sleeve_cuff_sts,
    )
    if sleeve_inc_pairs > 0:
        sec2.add(
            _l(f"Glatstrik med jævnt fordelte udtagninger: "
               f"udtagningsomg = k1, M1L, strik til 1 m før omg-slut, M1R, k1 "
               f"(+2 m). "
               f"Gentag hver {sleeve_inc_cadence:.1f}. omg, i alt "
               f"{sleeve_inc_pairs} gange — slut på {sleeve_top_sts} m.",
               f"Stockinette with evenly spaced increases: "
               f"increase round = k1, M1L, knit to 1 st before end of round, M1R, k1 "
               f"(+2 sts). "
               f"Repeat every {sleeve_inc_cadence:.1f} rounds, a total of "
               f"{sleeve_inc_pairs} times — end on {sleeve_top_sts} sts.",
               lang),
            sleeve_top_sts,
            note=_l(f"top = round(K·35 %) = {sleeve_top_sts} m",
                    f"top = round(K·35%) = {sleeve_top_sts} sts", lang),
        )
    else:
        sec2.add(
            _l(f"Strik glatstrik uden indtagninger i {sleeve_plain_rows} omg.",
               f"Knit stockinette without decreases for {sleeve_plain_rows} rounds.",
               lang),
            sleeve_cuff_sts,
        )

    # ---- Underarm hold + join ------------------------------------------
    sec3 = p.add_section(
        _l("Sammenstrikning af krop og ærmer", "Joining body and sleeves", lang),
        sts_before=sleeve_top_sts,
    )
    sec3.add(
        _l(f"Aflæg {underarm_sts} m fra hver underarm på begge sider af "
           f"kroppen og på hvert ærme. Underarm-held = round(K·8 %) "
           f"= {underarm_sts} m. "
           "Disse maskemask'es senere.",
           f"Place {underarm_sts} sts on hold at each underarm on both sides of "
           f"the body and on each sleeve. Underarm hold = round(K·8%) "
           f"= {underarm_sts} sts. "
           "These will be grafted later.",
           lang),
        sleeve_top_sts,
        note=_l(f"krop efter held: {body_after_join} m. "
                f"Hvert ærme efter held: {sleeve_after_join} m.",
                f"body after hold: {body_after_join} sts. "
                f"Each sleeve after hold: {sleeve_after_join} sts.",
                lang),
    )
    sec4 = p.add_section(_l("Bærestykke", "Yoke", lang), sts_before=yoke_start_sts)
    sec4.add(
        _l(f"Saml til omg: strik over halv ryg ({body_after_join // 2} m), "
           f"strik første ærme ({sleeve_after_join} m) "
           f"+ 4 markører ved overgangene, "
           f"strik forstykke ({body_after_join} m), "
           f"andet ærme ({sleeve_after_join} m), "
           "rest af ryg.",
           f"Join in the round: knit half of the back ({body_after_join // 2} sts), "
           f"knit the first sleeve ({sleeve_after_join} sts) "
           f"placing 4 markers at the transitions, "
           f"knit the front ({body_after_join} sts), "
           f"second sleeve ({sleeve_after_join} sts), "
           "rest of the back.",
           lang),
        yoke_start_sts,
        note=_l(f"yoke-cast-on (= body − 2u + 2·(arm_top − 2u)) = {yoke_start_sts}",
                f"yoke cast-on (= body − 2u + 2·(arm_top − 2u)) = {yoke_start_sts}",
                lang),
    )
    if yoke_dec_rounds > 0:
        sec4.add(
            _l("Indtagningsomg (4 raglan-markører): "
               "*strik til 2 m før markør, k2tog, sm, ssk* gentag for alle 4 "
               "= -8 m pr. omg.",
               "Decrease round (4 raglan markers): "
               "*knit to 2 sts before marker, k2tog, sm, ssk* repeat for all 4 "
               "= -8 sts per round.",
               lang),
            yoke_start_sts - 8,
        )
        sec4.add(
            _l(f"Skift mellem indt-omg og plain omg. Gentag i alt "
               f"{yoke_dec_rounds} indt-omg.",
               f"Alternate dec round and plain round. Repeat for a total of "
               f"{yoke_dec_rounds} dec rounds.",
               lang),
            yoke_start_sts - 8 * yoke_dec_rounds,
            note=_l(f"slutter på ≈ {neck_sts} m halsmasker",
                    f"ends on ≈ {neck_sts} neck sts", lang),
        )

    # ---- Hals ----------------------------------------------------------
    sec5 = p.add_section(_l("Hals", "Neckband", lang), sts_before=neck_sts)
    sec5.add(
        _l(f"Strik 2 r, 2 vr rib i {body_rib_rows} omg over halsmaskerne.",
           f"Work k2, p2 rib for {body_rib_rows} rounds across the neck sts.",
           lang),
        neck_sts,
    )
    sec5.add(_l("Luk løst af i rib.", "Bind off loosely in rib.", lang), neck_sts)

    # ---- Afslutning ----------------------------------------------------
    sec6 = p.add_section(_l("Afslutning", "Finishing", lang), sts_before=neck_sts)
    sec6.add(
        _l(f"Maskemask de {underarm_sts} held-masker fra krop og ærme sammen "
           "i hver underarm. Hæft alle ender. Blok efter mål.",
           f"Kitchener-graft the {underarm_sts} held sts from body and sleeve "
           "together at each underarm. Weave in all ends. Block to measurements.",
           lang),
        neck_sts,
    )

    # ---- Notes & warnings ----------------------------------------------
    p.notes.append(
        f"EPS key number K = {K}. "
        f"Krop = round(K·90 %) = {body_sts}. "
        f"Ærme cuff = round(K·20 %) = {sleeve_cuff_sts}. "
        f"Ærme top = round(K·35 %) = {sleeve_top_sts}. "
        f"Underarm = round(K·8 %) = {underarm_sts}. "
        f"Hals = round(K·40 %) = {neck_sts}."
    )
    p.notes.append(
        f"Yoke depth = (bust + ease)/4 = {yoke_depth_cm:.1f} cm "
        f"≈ {yoke_rounds} omg."
    )
    if sleeve_after_join < 4:
        p.warnings.append(
            "Ærmet bliver meget smalt efter underarm-held — overvej større "
            "upper_arm_cm eller mindre ease."
        )
    if yoke_dec_rounds == 0:
        p.warnings.append(
            "Yoke-decreases blev nul — yoke_start_sts allerede ≤ neck_sts. "
            "Tjek bust + neck_circumference inputs."
        )

    return p
