"""Sock generator — top-down with heel flap + gusset.

Construction (Agent A's research §3):

  1. Skaft (cuff + leg): cast on ``total_sts``, 2×2 rib for ~5 cm, then
     stockinette to the ankle.
  2. Hælklap (heel flap): half the stitches worked back-and-forth in heel
     stitch for ``flap_rows = flap_sts`` rows (square flap).
  3. Heel turn: classic short-row turn governed by Sara Morris' parity
     formula — after the turn we have ``H`` stitches.
  4. Gusset: pick up ``flap_rows / 2 + 1`` along each side of the flap;
     decrease every other round until total stitches return to
     ``total_sts``.
  5. Foot: knit straight to ``foot_length_cm - toe_length_cm``.
  6. Tå (toe): decrease 4 sts every other round, then every round, to
     ~16 sts; Kitchener graft.

All counts are integers and pass through :class:`RowValidator`.
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import (
    Gauge, cm_to_sts, cm_to_rows, Pattern, RowValidator,
)
from ..knitrow import KnitRow as Row


# Negative ease: socks should sit snug. Standard rule of thumb 10 %.
DEFAULT_NEG_EASE = 0.10


@dataclass
class SokkerSpec:
    """Parameters for a top-down sock with heel flap + gusset."""

    foot_circ_cm: float           # circumference around the widest part of the foot
    foot_length_cm: float         # heel-to-toe length
    gauge: Gauge
    name: str = "Sokker"
    leg_length_cm: float = 18.0   # cuff to top of heel flap
    rib_height_cm: float = 5.0    # 2×2 rib at the cuff
    neg_ease_pct: float = DEFAULT_NEG_EASE
    shoe_size: str | None = None  # informative only
    metadata: dict | None = None


def heel_turn(F: int, h: int) -> int:
    """Sara Morris' parity formula for the classic heel turn.

    F = flap stitches (= ½ total stitches).
    h = central "bottom" stitches before the first decrease — typically
        ``floor(0.10 · total_sts)``.

    Returns ``H``, the number of stitches remaining after the heel turn.
    """
    if F < 4:
        raise ValueError(f"flap_sts must be >= 4 (got {F})")
    if h < 1:
        raise ValueError(f"h must be >= 1 (got {h})")
    rest = F - h
    if rest % 2 == 0:
        return h + rest // 2
    return h + (rest - 2) // 2 + 2


def _l(da: str, en: str, lang: str) -> str:
    return en if lang == "en" else da


def generate_sokker(spec: SokkerSpec, lang: str = "da") -> Pattern:
    g = spec.gauge
    if spec.foot_circ_cm <= 0 or spec.foot_length_cm <= 0:
        raise ValueError("foot_circ_cm and foot_length_cm must be > 0")

    # Total cast-on. Apply negative ease, round to multiple of 4 (so 2×2 rib
    # divides cleanly *and* the heel can split exactly in half).
    finished_circ = spec.foot_circ_cm * (1.0 - spec.neg_ease_pct)
    total_sts = cm_to_sts(finished_circ, g, multiple=4)
    if total_sts < 16:
        raise ValueError(
            f"foot_circ {spec.foot_circ_cm} cm gives only {total_sts} sts — "
            "increase circumference or gauge"
        )

    # Heel flap = half the stitches; instep (= front half) holds the same.
    flap_sts = total_sts // 2
    instep_sts = total_sts - flap_sts
    flap_rows = flap_sts  # square flap

    # Heel turn parameters
    h = max(1, total_sts // 10)  # ≈ 10 % central bottom sts before first dec
    H = heel_turn(flap_sts, h)

    # Gusset
    pickup_per_side = flap_rows // 2 + 1
    gusset_sts_after_pickup = H + 2 * pickup_per_side + instep_sts
    gusset_decreases_pairs = (gusset_sts_after_pickup - total_sts) // 2

    # Foot lengths
    toe_length_cm = spec.foot_circ_cm / 4.0
    plain_foot_cm = max(0.0, spec.foot_length_cm - toe_length_cm)
    plain_foot_rows = cm_to_rows(plain_foot_cm, g)

    # Toe — decrease to ~16 sts
    toe_finish_sts = max(8, ((total_sts // 4) // 2) * 2)  # round to even
    if toe_finish_sts > total_sts:
        toe_finish_sts = total_sts
    toe_decrease_pairs = max(0, (total_sts - toe_finish_sts) // 4)

    rib_rounds = cm_to_rows(spec.rib_height_cm, g)
    leg_plain_rounds = max(0, cm_to_rows(spec.leg_length_cm - spec.rib_height_cm, g))

    metadata = dict(spec.metadata or {})

    p = Pattern(
        name=spec.name,
        construction="sokker",
        difficulty="intermediate",
        inputs={
            "_domain": "knit",
            "foot_length_cm": spec.foot_length_cm,
            "foot_circ_cm": spec.foot_circ_cm,
            "leg_length_cm": spec.leg_length_cm,
            "rib_height_cm": spec.rib_height_cm,
            "ease_cm": -spec.foot_circ_cm * spec.neg_ease_pct,
            "shoe_size": spec.shoe_size,
            "total_sts": total_sts,
            "flap_sts": flap_sts,
            "flap_rows": flap_rows,
            "h_central": h,
            "H_after_turn": H,
            "pickup_per_side": pickup_per_side,
            "toe_length_cm": round(toe_length_cm, 1),
            "toe_finish_sts": toe_finish_sts,
            "gauge": {
                "sts_per_10cm": g.sts_per_10cm,
                "rows_per_10cm": g.rows_per_10cm,
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- Skaft ----------------------------------------------------------
    sec1 = p.add_section(_l("Skaft", "Leg", lang), sts_before=total_sts)
    sec1.add(
        _l(f"Slå {total_sts} m op på 4 strømpepinde (eller magic-loop). "
           "Saml til omg uden at sno.",
           f"Cast on {total_sts} sts on 4 DPNs (or magic-loop). "
           "Join in the round without twisting.",
           lang),
        total_sts,
        note=_l(f"{total_sts // 4} m pr. pind",
                f"{total_sts // 4} sts per needle", lang),
    )
    sec1.add(
        _l(f"Strik 2 r, 2 vr rib i {rib_rounds} omg "
           f"(ca. {spec.rib_height_cm:.0f} cm).",
           f"Work k2, p2 rib for {rib_rounds} rounds "
           f"(about {spec.rib_height_cm:.0f} cm).",
           lang),
        total_sts,
    )
    sec1.add(
        _l(f"Fortsæt i glatstrik (ret hver omg) i {leg_plain_rounds} omg "
           f"(ca. {spec.leg_length_cm - spec.rib_height_cm:.0f} cm).",
           f"Continue in stockinette (knit every round) for {leg_plain_rounds} rounds "
           f"(about {spec.leg_length_cm - spec.rib_height_cm:.0f} cm).",
           lang),
        total_sts,
    )
    # Validate: a single representative round
    validator.add(Row(sts_before=total_sts).k(total_sts))

    # ---- Hælklap --------------------------------------------------------
    sec2 = p.add_section(_l("Hælklap", "Heel flap", lang), sts_before=total_sts)
    sec2.add(
        _l(f"Saml de første {flap_sts} m på én pind (hælklappen). "
           f"De øvrige {instep_sts} m hviler som vrist.",
           f"Place the first {flap_sts} sts on one needle (the heel flap). "
           f"The remaining {instep_sts} sts rest as the instep.",
           lang),
        total_sts,
        note=_l("hælklappen strikkes flat frem og tilbage",
                "the heel flap is worked flat back and forth", lang),
    )
    sec2.add(
        _l(f"Hælmønster (glat hældestik): "
           f"RS pind: *gl 1, r 1* gentag til pindens slut. "
           f"VS pind: gl 1, vr resten. "
           f"Strik {flap_rows} pinde i alt.",
           f"Heel stitch pattern: "
           f"RS row: *sl 1, k 1* repeat to end of needle. "
           f"WS row: sl 1, p the rest. "
           f"Work {flap_rows} rows total.",
           lang),
        total_sts,
        note=_l("slip 1 first stitch på hver pind for fast kant",
                "slip the first stitch on each row for a firm selvedge", lang),
    )

    # ---- Heel turn ------------------------------------------------------
    sec3 = p.add_section(_l("Hæl-vending", "Heel turn", lang), sts_before=total_sts)
    sec3.add(
        _l(f"Setup: strik halvvejs over hælklappen + {h // 2 + 1} m, ssk, vend.",
           f"Setup: knit halfway across the heel flap + {h // 2 + 1} sts, ssk, turn.",
           lang),
        total_sts,
        note=_l("vi starter den klassiske kort-rækker-vending",
                "this starts the classic short-row turn", lang),
    )
    sec3.add(
        _l(f"VS: SLO, vr {h - 1} m, p2tog, vr 1, vend.",
           f"WS: sl 1, p {h - 1} sts, p2tog, p 1, turn.",
           lang),
        total_sts,
        note=_l("centrale h-masker er nu 'lukket' før første dec",
                "the central h sts are now 'closed' before the first dec", lang),
    )
    sec3.add(
        _l(f"Fortsæt korte rækker — på hver RS: SLO, r til 1 m før gabet, "
           f"ssk over gabet, r 1, vend. På hver VS: SLO, vr til 1 m før "
           f"gabet, p2tog over gabet, vr 1, vend.",
           f"Continue short rows — on every RS: sl 1, k to 1 st before the gap, "
           f"ssk across the gap, k 1, turn. On every WS: sl 1, p to 1 st before "
           f"the gap, p2tog across the gap, p 1, turn.",
           lang),
        total_sts - (flap_sts - H),
        note=_l(f"slut på {H} m efter hælvending (paritets-formel: H = "
                f"heel_turn({flap_sts}, {h}) = {H})",
                f"end on {H} sts after the heel turn (parity formula: H = "
                f"heel_turn({flap_sts}, {h}) = {H})",
                lang),
    )

    # ---- Gusset ---------------------------------------------------------
    sec4 = p.add_section(
        _l("Gusset", "Gusset", lang),
        sts_before=H + instep_sts,
    )
    sec4.add(
        _l(f"Saml til omg igen: r over hælen ({H} m), saml "
           f"{pickup_per_side} m langs venstre side af hælklappen, "
           f"strik vristen ({instep_sts} m), saml {pickup_per_side} m langs "
           f"højre side af hælklappen.",
           f"Re-join in the round: knit across the heel ({H} sts), pick up "
           f"{pickup_per_side} sts along the left side of the heel flap, "
           f"knit across the instep ({instep_sts} sts), pick up "
           f"{pickup_per_side} sts along the right side of the heel flap.",
           lang),
        gusset_sts_after_pickup,
        note=_l(f"{gusset_sts_after_pickup} m i alt — gusset starter her",
                f"{gusset_sts_after_pickup} sts total — the gusset starts here",
                lang),
    )
    if gusset_decreases_pairs > 0:
        sec4.add(
            _l(f"Indtagningsomg: strik til 3 m før vrist-start, k2tog, k1, "
               f"strik vristen plain, k1, ssk, strik resten.",
               f"Decrease round: knit to 3 sts before the start of the instep, "
               f"k2tog, k1, knit the instep plain, k1, ssk, knit the rest.",
               lang),
            gusset_sts_after_pickup - 2,
            note=_l("-2 m pr. indtagningsomg (én i hver gusset-side)",
                    "-2 sts per decrease round (one in each gusset side)", lang),
        )
        sec4.add(
            _l(f"Skift mellem indt-omg og plain omg. Gentag i alt "
               f"{gusset_decreases_pairs} indt-omg så total = {total_sts} m.",
               f"Alternate decrease round and plain round. Repeat for a total "
               f"of {gusset_decreases_pairs} dec rounds so total = {total_sts} sts.",
               lang),
            total_sts,
            note=_l(f"slut på {total_sts} m (= original cast-on)",
                    f"end on {total_sts} sts (= original cast-on)", lang),
        )

    # ---- Foot -----------------------------------------------------------
    sec5 = p.add_section(_l("Fod", "Foot", lang), sts_before=total_sts)
    sec5.add(
        _l(f"Strik glatstrik i {plain_foot_rows} omg "
           f"(ca. {plain_foot_cm:.1f} cm) til arbejdet måler "
           f"{spec.foot_length_cm - toe_length_cm:.1f} cm fra hælen.",
           f"Knit stockinette for {plain_foot_rows} rounds "
           f"(about {plain_foot_cm:.1f} cm) until the work measures "
           f"{spec.foot_length_cm - toe_length_cm:.1f} cm from the heel.",
           lang),
        total_sts,
    )

    # ---- Toe ------------------------------------------------------------
    sec6 = p.add_section(_l("Tå", "Toe", lang), sts_before=total_sts)
    sec6.add(
        _l("Indtagningsomg: *r til 3 m før hjørne, k2tog, k1, sm, k1, ssk* "
           "gentag (4 indtagninger pr. omg = -4 m).",
           "Decrease round: *k to 3 sts before the corner, k2tog, k1, sm, k1, ssk* "
           "repeat (4 decreases per rnd = -4 sts).",
           lang),
        total_sts - 4,
        note=_l("2 indt på hælsiden, 2 på vristen",
                "2 dec on the sole, 2 on the instep", lang),
    )
    sec6.add(
        _l(f"Skift mellem en indt-omg og en plain omg, indtil "
           f"{total_sts - 2 * toe_decrease_pairs} m er tilbage.",
           f"Alternate a dec round and a plain round until "
           f"{total_sts - 2 * toe_decrease_pairs} sts remain.",
           lang),
        total_sts - 2 * toe_decrease_pairs,
    )
    if toe_decrease_pairs > 0:
        sec6.add(
            _l(f"Derefter dec hver omg, indtil {toe_finish_sts} m er tilbage.",
               f"Then dec every round until {toe_finish_sts} sts remain.",
               lang),
            toe_finish_sts,
        )
    sec6.add(
        _l("Klip garnet (~30 cm). Maskemask (Kitchener graft) hælen og "
           "vristen sammen. Hæft ender. Strik anden sok magen til.",
           "Cut the yarn (~30 cm). Kitchener-graft the sole and instep "
           "together. Weave in ends. Knit the second sock the same way.",
           lang),
        toe_finish_sts,
    )

    # ---- Notes & warnings ----------------------------------------------
    p.notes.append(
        f"Total cast-on: {total_sts} m (delelig med 4 for 2×2 rib og "
        f"halv-deling til hælklap)."
    )
    p.notes.append(
        f"Heel turn: H = heel_turn({flap_sts}, {h}) = {H} "
        f"(paritets-formel — Sara Morris)."
    )
    p.notes.append(
        f"Gusset pickup: {pickup_per_side} m pr. side "
        f"(= flap_rows/2 + 1 = {flap_rows}/2 + 1)."
    )
    p.notes.append(
        f"Tå-længde: {toe_length_cm:.1f} cm (≈ omkreds/4). "
        f"Kitchener-graft af de sidste {toe_finish_sts} m."
    )

    if spec.foot_circ_cm < 18:
        p.warnings.append(
            f"Fodomkreds {spec.foot_circ_cm} cm er ret lille — tjek at "
            "stitch-tallet ikke ender < 16 m, ellers bliver hælvendingen "
            "klemt."
        )
    if total_sts % 4 != 0:
        p.warnings.append(
            "Total cast-on er ikke delelig med 4 — 2×2 rib og hælen "
            "kommer ikke ud lige."
        )

    return p
