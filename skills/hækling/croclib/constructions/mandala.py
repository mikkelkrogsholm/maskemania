"""Mandala — round, multi-round decorative motif with mixed stitches.

A mandala is a flat circular piece worked in rounds, where each round
typically uses a different stitch type or texture (sc, dc, popcorn, picot,
shells, …). The classical recipe is:

* Round 1: magic ring with N sc (default 12).
* Round 2: per stitch, a (ch + dc) pair → 2N stitches.
* Round 3: popcorn-cluster textures into every other stitch.
* Round 4+: alternating shells / picots / sc rounds — increasing 6 or 12
  stitches per round so the piece stays flat (a "flat-circle" rule).

We model the mandala as a stack of rounds, each described by a small
record (the stitch code, the increase factor, and a free-text note). The
default progression is intentionally simple so it works at any
``rounds`` value. Callers can supply a custom progression too.

Bookkeeping: each round consumes the previous round's stitch count (so
the validator catches off-by-one progressions). Decorative stitches
(``picot``) don't consume / produce — they're tracked as notes only,
matching the (0, 0) modeling in :mod:`croclib.stitches`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from lib.visualisering import Pattern, RowValidator
from ..crorow import CrochetRow


# ---------------------------------------------------------------------------
# Round-progression DSL
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RoundSpec:
    """One round of a mandala.

    stitch:    short code — "sc", "dc", "hdc", "tr", "pop", "pic", or "mr".
    multiplier: how many of the previous round's stitches each new stitch
                consumes — fractional values aren't allowed; use ints. So
                ``multiplier=1`` means *one stitch in each previous st*
                (no increase), ``multiplier=2`` means *two stitches in
                each previous st* (double the count), etc.
    increase_per_st: extra stitches added per previous st. ``0`` for
                straight rounds, ``1`` for double-it rounds, fractions
                approximated by alternating.
    note:      Danish description, used verbatim in the Pattern.
    """
    stitch: str
    increase_per_st: int = 0
    note: str = ""


def default_round_progression(rounds: int, start_count: int = 12) -> list[RoundSpec]:
    """Sensible default progression.

    Pattern (designed to keep the piece flat — increase by 6/12 sts per
    round on average):

    * Round 1: magic ring of ``start_count`` sc.
    * Round 2: 1 dc + 1 ch in each st → ``2·start_count`` stitches (we
      track only the dc — the ch's are spaces).
    * Round 3: popcorn-cluster every 2nd st, sc between → same count.
    * Round 4: 2 dc in each st → doubles the count.
    * Round 5: alternating sc + picot decoration → same count.
    * Round 6+: (2 dc, 1 dc) repeating → +half-count per round.

    Picots and chains aren't counted as working stitches.
    """
    if rounds < 1:
        raise ValueError("rounds must be >= 1")

    progression: list[RoundSpec] = []
    progression.append(RoundSpec(
        "mr", increase_per_st=0,
        note=f"magic ring med {start_count} fm",
    ))
    if rounds >= 2:
        progression.append(RoundSpec(
            "dc", increase_per_st=1,
            note="2 stm i hver fm fra omg 1 (fordobler antallet)",
        ))
    if rounds >= 3:
        progression.append(RoundSpec(
            "pop", increase_per_st=0,
            note="skift mellem 1 popkorn og 1 fm hele omgangen rundt",
        ))
    if rounds >= 4:
        progression.append(RoundSpec(
            "dc", increase_per_st=1,
            note="2 stm i hver maske (fordobler antallet)",
        ))
    if rounds >= 5:
        progression.append(RoundSpec(
            "sc", increase_per_st=0,
            note="1 fm + 1 picot i hver 4. m, ellers 1 fm",
        ))
    # Round 6+: cycle through "shell-doubling" and "straight" in turn.
    # We pick increase=0 for even-numbered rounds and increase=1 for odd
    # to keep the piece flat-ish.
    for n in range(6, rounds + 1):
        if n % 2 == 0:
            progression.append(RoundSpec(
                "hdc", increase_per_st=0,
                note=f"omg {n}: 1 hstm i hver maske",
            ))
        else:
            progression.append(RoundSpec(
                "dc", increase_per_st=1,
                note=f"omg {n}: 2 stm i hver maske (fordobler antallet)",
            ))
    return progression[:rounds]


# ---------------------------------------------------------------------------
# Spec + generator
# ---------------------------------------------------------------------------


@dataclass
class MandalaSpec:
    rounds: int
    start_count: int = 12
    colors: list[str] | None = None
    progression: list[RoundSpec] | None = None
    name: str = "Mandala"
    # Pseudo-gauge for the cover box; mandalas are flat so we tag it.
    gauge_sts_per_cm: float = 3.0
    gauge_rows_per_cm: float = 3.0


def generate_mandala(spec: MandalaSpec, lang: str = "da") -> Pattern:
    if spec.rounds < 1:
        raise ValueError("rounds must be >= 1")
    if spec.start_count < 1:
        raise ValueError("start_count must be >= 1")

    colors = spec.colors or []
    progression = spec.progression or default_round_progression(
        spec.rounds, spec.start_count
    )
    if len(progression) != spec.rounds:
        raise ValueError(
            f"progression has {len(progression)} entries, expected {spec.rounds}"
        )

    # ----- Walk the progression to compute stitch counts -----------------
    sts_per_round: list[int] = []
    current = 0
    for i, rd in enumerate(progression):
        if i == 0:
            # Round 1 must be a magic-ring init
            if rd.stitch != "mr":
                raise ValueError("first round must be a magic ring (stitch='mr')")
            current = spec.start_count
        else:
            current = current + current * rd.increase_per_st
        sts_per_round.append(current)

    p = Pattern(
        name=spec.name,
        construction="mandala",
        difficulty="intermediate",
        inputs={
            "_domain": "crochet",
            "rounds": spec.rounds,
            "start_count": spec.start_count,
            "colors": colors,
            "sts_per_round": sts_per_round,
            "final_sts": sts_per_round[-1],
            "gauge": {
                "sts_per_10cm": int(round(spec.gauge_sts_per_cm * 10)),
                "rows_per_10cm": int(round(spec.gauge_rows_per_cm * 10)),
            },
        },
    )

    validator = RowValidator()

    # ----- Section: Start ----------------------------------------------
    sec_start = p.add_section("Start", sts_before=0)
    sec_start.add(
        f"Lav en magic ring med {spec.start_count} fm. Saml til omg med 1 km.",
        sts_after=spec.start_count,
        note=f"alt: lm 4 + 11 fm i 1. lm",
    )
    r0 = CrochetRow(sts_before=0, label="Omg 1 (magic ring)")
    r0.magic_ring(spec.start_count)
    validator.add(r0)

    # ----- Section: each round -----------------------------------------
    prev_sts = spec.start_count
    for i in range(1, spec.rounds):
        rd = progression[i]
        new_sts = sts_per_round[i]
        color = colors[i % len(colors)] if colors else None
        color_label = f" ({color})" if color else ""
        sec = p.add_section(
            f"Omg {i + 1}{color_label}", sts_before=prev_sts,
        )
        sec.add(
            rd.note,
            sts_after=new_sts,
            note=f"{prev_sts} m → {new_sts} m",
        )
        # Validate this round through CrochetRow when the recipe is a
        # uniform stitch with a clean (consumes, produces) ratio. For
        # "mixed" rounds (popcorn alternated with sc, picot decorations)
        # we skip per-stitch validation — the section-level continuity
        # check already covers it.
        if rd.stitch in ("sc", "hdc", "dc", "tr") and rd.increase_per_st in (0, 1):
            r = CrochetRow(sts_before=prev_sts, label=f"Omg {i + 1}")
            if rd.increase_per_st == 0:
                r.op(rd.stitch, prev_sts)
            else:
                # 2 sts in every previous st: model as inc-style — only
                # sc has a ready-made sc_inc, so for dc/hdc/tr we add the
                # raw count and rely on consumption math: each previous
                # st consumes 1 and produces 2, so we emit ``prev_sts``
                # base stitches that each "consume 1 produce 1" plus
                # ``prev_sts`` extra dc that "consume 0 produce 1". We
                # approximate by emitting ``prev_sts`` of sc_inc when
                # the stitch is sc, else by skipping per-stitch validation
                # (still validated via section continuity).
                if rd.stitch == "sc":
                    r.sc_inc(prev_sts)
                else:
                    # Skip per-stitch; section continuity covers it.
                    r = None
            if r is not None:
                validator.add(r)
        prev_sts = new_sts

    # ----- Finishing ---------------------------------------------------
    sec_end = p.add_section("Afslutning", sts_before=prev_sts)
    sec_end.add(
        "Klip garnet, hæft enden bag på arbejdet og blok mandalaen flad.",
        sts_after=prev_sts,
    )

    # Notes
    p.notes.append(
        f"Slutmål: {spec.rounds} omg, {prev_sts} masker i sidste omg."
    )
    if colors:
        p.notes.append(
            f"Farveskift hver omg: {' → '.join(colors)} → (gentag)."
        )
    p.notes.append(
        "Hvis mandalaen bølger, har du øget for hurtigt — tag færre "
        "udtagninger pr. omg. Hvis den krummer som en skål, har du øget "
        "for lidt."
    )

    p.validate_continuity()
    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
