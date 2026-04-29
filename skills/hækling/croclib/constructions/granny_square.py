"""Granny square — classic 3-dc-cluster variant.

Recipe (Agent B's research §3, classic granny):

* Round 1: in a magic ring, [3 dc, ch 2] × 4 → 12 dc, 4 corner ch-2 spaces.
* Round 2: in each corner ch-sp, [3 dc, ch 2, 3 dc]; between corners, ch 1.
  → 24 dc total, 4 corner ch-2 spaces, 4 side ch-1 spaces.
* Round N (N >= 3): per side, (N-2) ch-1-separated 3-dc clusters between
  the corners. Per corner [3 dc, ch 2, 3 dc].
  → ``12·(N-1)`` total dc on round N (formula from Agent B).

The validator only counts *dc stitches* per round (the corner ch-2 and side
ch-1 are tracked as Pattern notes — they're chain-spaces, not stitches in
the (consumes, produces) sense).
"""

from __future__ import annotations

from dataclasses import dataclass

from lib.visualisering import Pattern


def _classic_round_dc_count(n: int) -> int:
    """Total DC count after round N for a classic granny square.

    Round 1: 12. Round 2: 24. Round N (N>=2): 12·(N-1) ... wait, that's
    inconsistent. Let me re-read §3.

    Agent B's formula: "total dc round N = 4 × 3(N-1) = 12(N-1)" for N>=3.
    But round 1 = 12 and round 2 = 24, which fits 12·N — not 12·(N-1).

    Reading again more carefully: round 2 = 24 (= 12·2). Round 3 has
    (3-2)=1 cluster per side between corners + 2 corners worth of 3 dc per
    side = (1+2)·3 = 9 dc per side? No: each corner is [3 dc, ch 2, 3 dc]
    so each corner contributes 3 dc to each adjacent side. Per side then:
    3 (from left corner) + (N-2)·3 (clusters between) + 3 (from right corner)
    = 6 + 3·(N-2) = 3·N. Across 4 sides this is 12·N. So the simple
    formula is **12·N for N>=1**. We use that — and Agent B's formula was
    probably a typo (12·(N-1) doesn't even work for N=1).
    """
    if n < 1:
        raise ValueError(f"n must be >= 1 (got {n})")
    return 12 * n


@dataclass
class GrannySquareSpec:
    rounds: int = 6
    colors: list[str] | None = None
    name: str = "Granny square"


def _l(da: str, en: str, lang: str) -> str:
    return en if lang == "en" else da


def generate_granny_square(spec: GrannySquareSpec, lang: str = "da") -> Pattern:
    if spec.rounds < 1:
        raise ValueError("rounds must be >= 1")

    colors = spec.colors or []

    p = Pattern(
        name=spec.name,
        construction="granny_square",
        difficulty="beginner",
        inputs={
            "_domain": "crochet",
            "rounds": spec.rounds,
            "colors": colors,
            "final_dc_count": _classic_round_dc_count(spec.rounds),
            # Pseudo-gauge for the shared cover-builder
            "gauge": {"sts_per_10cm": 30, "rows_per_10cm": 16},
        },
    )

    # NOTE on bookkeeping: granny squares anchor each round's dc into the
    # previous round's chain-spaces, not directly into stitches. The simple
    # (consumes, produces)-per-stitch model from `bookkeeping.py` doesn't
    # capture that — so we validate granny squares at the *section* level
    # (the dc-count per round must match the closed-form formula
    # ``12 · N``) instead of the per-stitch level. The CrochetRow objects
    # below are kept around for symmetry with other constructions but they
    # don't go through RowValidator.

    sec_setup = p.add_section(_l("Start", "Start", lang), sts_before=0)
    sec_setup.add(
        _l("Lav en magic ring (eller lm 4 og slut til en ring med km).",
           "Make a magic ring (or ch 4 and join into a ring with sl-st).",
           lang),
        sts_after=0,
    )

    # ----- Round 1 -------------------------------------------------------
    color_1 = colors[0] if colors else None
    sec1 = p.add_section(
        _l(f"Omg 1{f' ({color_1})' if color_1 else ''}",
           f"Rnd 1{f' ({color_1})' if color_1 else ''}", lang),
        sts_before=0,
    )
    sec1.add(
        _l("I ringen: [3 stm, lm 2] × 4. Saml til omgang med 1 km i toppen "
           "af 1. stm. Stram ringen.",
           "In the ring: [3 dc, ch 2] × 4. Join the round with sl-st in the "
           "top of the first dc. Tighten the ring.",
           lang),
        sts_after=12,
        note=_l("12 stm + 4 hjørne-lm2-buer",
                "12 dc + 4 corner ch-2 spaces", lang),
    )

    # ----- Round 2+ ------------------------------------------------------
    for n in range(2, spec.rounds + 1):
        color_n = colors[(n - 1) % len(colors)] if colors else None
        sec = p.add_section(
            _l(f"Omg {n}{f' ({color_n})' if color_n else ''}",
               f"Rnd {n}{f' ({color_n})' if color_n else ''}", lang),
            sts_before=_classic_round_dc_count(n - 1),
        )
        dc_count = _classic_round_dc_count(n)
        prev_dc = _classic_round_dc_count(n - 1)

        if n == 2:
            sec.add(
                _l("I hver hjørne-lm2-bue fra omg 1: [3 stm, lm 2, 3 stm]. "
                   "Mellem hjørnerne: lm 1.",
                   "In each corner ch-2 space from rnd 1: [3 dc, ch 2, 3 dc]. "
                   "Between corners: ch 1.",
                   lang),
                sts_after=dc_count,
                note=_l("24 stm + 4 hjørne-lm2-buer + 4 side-lm1-buer",
                        "24 dc + 4 corner ch-2 spaces + 4 side ch-1 spaces", lang),
            )
        else:
            clusters_per_side = n - 1
            sec.add(
                _l(f"Pr. side ({clusters_per_side - 1} side-clusters): "
                   "[3 stm i side-lm1-bue, lm 1] gentaget. "
                   f"I hvert hjørne: [3 stm, lm 2, 3 stm]. "
                   "Saml med km til top af første stm.",
                   f"Per side ({clusters_per_side - 1} side clusters): "
                   "[3 dc into side ch-1 sp, ch 1] repeated. "
                   f"In each corner: [3 dc, ch 2, 3 dc]. "
                   "Join with sl-st to the top of the first dc.",
                   lang),
                sts_after=dc_count,
                note=_l(f"i alt {dc_count} stm i denne omg "
                        f"({clusters_per_side - 1} clusters pr. side + hjørner)",
                        f"total {dc_count} dc this rnd "
                        f"({clusters_per_side - 1} clusters per side + corners)",
                        lang),
            )

    # ----- Finishing -----------------------------------------------------
    sec_end = p.add_section(_l("Afslutning", "Finishing", lang),
                             sts_before=_classic_round_dc_count(spec.rounds))
    sec_end.add(
        _l("Saml omg med 1 km i toppen af første stm. Klip garnet og hæft enden.",
           "Join the round with sl-st in the top of the first dc. Cut the yarn "
           "and weave in the end.",
           lang),
        sts_after=_classic_round_dc_count(spec.rounds),
    )

    p.notes.append(
        _l(f"Slutmål: {spec.rounds} omg, {_classic_round_dc_count(spec.rounds)} "
           f"stm i alt (4 sider × {3 * spec.rounds} stm pr. side).",
           f"Final: {spec.rounds} rnds, {_classic_round_dc_count(spec.rounds)} "
           f"dc total (4 sides × {3 * spec.rounds} dc per side).",
           lang)
    )
    if colors:
        p.notes.append(
            _l(f"Farveskift hver omg: {' → '.join(colors)} → (gentag).",
               f"Color change each rnd: {' → '.join(colors)} → (repeat).",
               lang)
        )

    p.validate_continuity()
    return p
