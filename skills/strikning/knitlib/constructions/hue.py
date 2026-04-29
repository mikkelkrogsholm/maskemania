"""Hat (hue) generator — bottom-up, knit in the round.

Construction:
  1. Cast on a multiple-of-8 number of stitches sized to head − ease.
  2. Work 2x2 rib for ~5 cm.
  3. Switch to stockinette and work until the hat is ~18 cm from cast-on
     (less for shallow beanies, more for slouches).
  4. Crown: 8 sectors, decrease one stitch per sector every other round
     until ~16 sts remain; then decrease every round until ~8 sts.
  5. Pull yarn through remaining stitches.

The 8-sector crown is forgiving: it works for most adult head circumferences
since cast-on is rounded to multiples of 8, and gives a tidy 8-pointed star
on top.
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import Gauge, cm_to_sts, cm_to_rows, Pattern
from lib.visualisering.shaping import crown_decrease_plan


@dataclass
class HueSpec:
    head_circumference_cm: float
    gauge: Gauge
    name: str = "Klassisk hue"
    ease_cm: float = -3.0          # negative; brim grips
    rib_height_cm: float = 5.0
    total_height_cm: float = 21.0  # cast-on to crown center
    sectors: int = 8               # crown sectors


def _l(da: str, en: str, lang: str) -> str:
    """Pick a localized string. Defaults to Danish."""
    return en if lang == "en" else da


def generate_hue(spec: HueSpec, lang: str = "da") -> Pattern:
    g = spec.gauge
    finished_circ = spec.head_circumference_cm + spec.ease_cm

    # Cast-on must be divisible by 8 (sectors) and by 4 (2x2 rib).
    # 8 covers both since 8 is divisible by 4.
    cast_on = cm_to_sts(finished_circ, g, multiple=spec.sectors)
    if cast_on < spec.sectors * 4:
        raise ValueError(
            f"cast-on {cast_on} is too small for {spec.sectors} sectors. "
            f"Increase head circumference or check gauge."
        )

    rib_rounds = cm_to_rows(spec.rib_height_cm, g)
    crown_rounds = _crown_rounds_estimate(cast_on, spec.sectors)
    body_rounds = cm_to_rows(spec.total_height_cm - spec.rib_height_cm, g) - crown_rounds
    body_was_clipped = body_rounds < 0
    if body_was_clipped:
        body_rounds = 0  # very short hat — go straight from rib to crown

    p = Pattern(
        name=spec.name,
        construction="hue",
        difficulty="beginner",
        inputs={
            "_domain": "knit",
            "head_circumference_cm": spec.head_circumference_cm,
            "ease_cm": spec.ease_cm,
            "finished_circumference_cm": round(finished_circ, 1),
            "gauge": {"sts_per_10cm": g.sts_per_10cm,
                      "rows_per_10cm": g.rows_per_10cm},
            "rib_height_cm": spec.rib_height_cm,
            "total_height_cm": spec.total_height_cm,
            "sectors": spec.sectors,
        },
    )

    sec1 = p.add_section(
        _l("Opslag og rib", "Cast on and rib", lang),
        sts_before=cast_on,
    )
    sec1.add(
        _l(f"Slå {cast_on} m op på rundpind. Saml til omgang uden at sno.",
           f"Cast on {cast_on} sts on a circular needle. Join in the round without twisting.",
           lang),
        cast_on,
    )
    sec1.add(
        _l(f"Strik 2 r, 2 vr rib i {rib_rounds} omgange (ca. {spec.rib_height_cm} cm).",
           f"Work k2, p2 rib for {rib_rounds} rounds (about {spec.rib_height_cm} cm).",
           lang),
        cast_on,
    )

    sec2 = p.add_section(
        _l("Krop", "Body", lang),
        sts_before=cast_on,
    )
    sec2.add(
        _l(f"Strik glatstrik (ret hver omg) i {body_rounds} omgange.",
           f"Knit stockinette (knit every round) for {body_rounds} rounds.",
           lang),
        cast_on,
        note=_l(
            f"arbejdet måler nu ca. {spec.rib_height_cm + body_rounds * 10/g.rows_per_10cm:.0f} cm fra opslag",
            f"piece now measures about {spec.rib_height_cm + body_rounds * 10/g.rows_per_10cm:.0f} cm from cast-on",
            lang,
        ),
    )
    sec2.add(
        _l(f"Sæt {spec.sectors} markører jævnt fordelt: efter hver "
           f"{cast_on // spec.sectors}. m.",
           f"Place {spec.sectors} markers evenly spaced: after every "
           f"{cast_on // spec.sectors} sts.",
           lang),
        cast_on,
    )

    sec3 = p.add_section(
        _l("Krone", "Crown", lang),
        sts_before=cast_on,
    )
    plan = crown_decrease_plan(cast_on, sectors=spec.sectors, min_finish_sts=spec.sectors)
    for rnd, sts_after, instruction in plan:
        sec3.add(
            _l(f"Omg {rnd}: {instruction}.",
               f"Rnd {rnd}: {_translate_crown_instruction(instruction, lang)}.",
               lang),
            sts_after,
        )
    sec3.add(
        _l("Klip garnet, træk gennem de resterende masker med en stoppenål, "
           "stram og fastgør. Hæft alle ender. Damp/blok let.",
           "Cut the yarn, thread through the remaining sts with a tapestry "
           "needle, pull tight and fasten. Weave in all ends. Steam-block lightly.",
           lang),
        plan[-1][1] if plan else cast_on,
    )

    p.validate_continuity()
    p.notes.append(
        _l("Mål altid din strikkefasthed på en prøvelap (mindst 15×15 cm) før "
           "du går i gang. Strikkefastheden er det eneste tal der bestemmer "
           "om huen passer.",
           "Always measure your gauge on a swatch (at least 15×15 cm) before "
           "you start. Gauge is the only number that determines whether the "
           "hat will fit.",
           lang)
    )
    if abs(spec.ease_cm) < 1:
        p.warnings.append(
            _l("Ease er sat tæt på 0. Huer falder normalt af uden negativ ease.",
               "Ease is set close to 0. Hats normally slip off without negative ease.",
               lang)
        )
    if body_was_clipped:
        p.warnings.append(
            _l(f"total_height_cm ({spec.total_height_cm}) er for lav til at "
               f"rumme rib + krone — kropssektionen blev sat til 0 omg. "
               f"Huen bliver kortere end ønsket.",
               f"total_height_cm ({spec.total_height_cm}) is too short to fit "
               f"rib + crown — the body section was set to 0 rounds. The hat "
               f"will end up shorter than requested.",
               lang)
        )
    return p


def _translate_crown_instruction(instruction: str, lang: str) -> str:
    """Translate a Danish crown decrease instruction to English.

    The instruction strings come from ``crown_decrease_plan`` and use a
    small fixed vocabulary, so a literal phrase-replacement is enough.
    """
    if lang != "en":
        return instruction
    # Order matters — longer phrases first.
    repl = [
        ("strik 1 omg ret", "knit 1 plain rnd"),
        ("gentag", "repeat"),
        ("gange", "times"),
        ("strik", "k"),
        (" m,", " sts,"),
        (" m ", " sts "),
        ("omg", "rnd"),
    ]
    out = instruction
    for da, en in repl:
        out = out.replace(da, en)
    return out


def _crown_rounds_estimate(cast_on: int, sectors: int) -> int:
    """Rough estimate of how many rounds the crown will take, used to
    subtract from body rounds so total height matches the spec."""
    plan = crown_decrease_plan(cast_on, sectors=sectors)
    return len(plan)
