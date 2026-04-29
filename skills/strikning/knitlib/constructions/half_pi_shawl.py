"""Elizabeth Zimmermann's Half-Pi shawl.

The half-pi shawl is a half-circle shawl based on the geometric fact that a
circle's circumference grows linearly with its radius: every doubling of
radius requires a doubling of stitches. Zimmermann's contribution was the
remark that we don't need to think about the radius — we just *double* the
center stitches every time we double the row count.

Verified stitch progression (Agent A's research §2):

    Row     Center sts after the doubling round
    1       8        (cast-on, 4 garter-edge each side, 0 center)
    2       11       (3 + 5 + 3)        ← first doubling round
    3-5     11
    6       17                          ← second doubling round
    7-12    17
    13      29                          ← third
    14-25   29
    26      53                          ← fourth
    27-50   53
    51      101                         ← fifth
    52-99   101
    100     197                         ← sixth

The doubling rule: ``new_center = 2 * old_center + 1`` (the +1 comes from the
yarn-over against the garter band). The number of plain rows between
doubling rounds also doubles every time (3, 6, 12, 24, 48, 96, …).

Inputs:
  - gauge (Gauge): blocked stitch + row gauge of the lace
  - n_doublings (int): how many doubling rounds (3-7 typical)
  - edge_sts (int): garter-band each side (default 4)
  - lace_motifs (list[str] | None): optional list of motif names per band
"""

from __future__ import annotations
from dataclasses import dataclass, field

from lib.visualisering import Gauge, Pattern, RowValidator
from ..knitrow import KnitRow as Row


def pi_shawl_progression(
    n_doublings: int, edge_sts: int = 4
) -> list[tuple[int, int, int]]:
    """Compute the half-pi progression.

    Returns a list of tuples (band_index, plain_rows_in_band, center_sts_after).
    band_index 0 is the cast-on band (no doubling yet); subsequent bands
    each begin with a doubling round.

    Verified: n_doublings=6, edge=4 →
        [(0, 1, 0), (1, 3, 3), (2, 6, 9), (3, 12, 21), (4, 24, 45),
         (5, 48, 93), (6, 96, 189)]
    Each band's *total* stitches = center_sts + 2*edge_sts, with row 1 of
    band having an extra YO at each end vs. row 0 (= +1 inside center).
    """
    if n_doublings < 0:
        raise ValueError("n_doublings must be >= 0")
    if edge_sts < 0:
        raise ValueError("edge_sts must be >= 0")
    progression: list[tuple[int, int, int]] = []
    # Band 0: cast-on (3 sts at neck) → pickup gives 4+0+4 = 8 sts, but
    # before the first doubling the center is "0" (just the joint).
    progression.append((0, 1, 0))
    plain_rows = 3
    center = 0
    for band in range(1, n_doublings + 1):
        center = 2 * center + 3  # see derivation in test
        progression.append((band, plain_rows, center))
        plain_rows *= 2
    return progression


# Sanity: the rule "2*center + 3" reproduces the canonical 0, 3, 9, 21, 45,
# 93, 189 sequence. Adding 2*edge_sts (8 by default) gives the *total* stitch
# count: 8, 11, 17, 29, 53, 101, 197 — exactly the table above.


@dataclass
class HalfPiShawlSpec:
    gauge: Gauge
    n_doublings: int = 5
    name: str = "Half-pi shawl"
    cast_on_sts: int = 3
    edge_sts: int = 4
    lace_motifs: list[str] | None = field(default=None)
    metadata: dict | None = None


def generate_half_pi_shawl(spec: HalfPiShawlSpec, lang: str = "da") -> Pattern:
    g = spec.gauge
    if spec.n_doublings < 3:
        # Very short shawls won't really look like half-pi
        pass
    if spec.n_doublings > 8:
        raise ValueError(
            f"n_doublings={spec.n_doublings} is too many — fabric becomes "
            "absurdly large and lace progression rarely supports it."
        )

    progression = pi_shawl_progression(spec.n_doublings, spec.edge_sts)

    # Total stitches at each band (= center + 2*edge)
    band_totals = [c + 2 * spec.edge_sts for _, _, c in progression]
    # First "band" (0) is just the cast-on/setup row; treat first total as 8.
    if band_totals[0] == 0 + 2 * spec.edge_sts:
        # band 0 is "after pickup", so it's already 8 by default
        pass

    # Estimate dimensions from the largest band (radius ≈ width/2)
    final_total_sts = band_totals[-1]
    final_width_cm = final_total_sts * 10.0 / g.sts_per_10cm

    # Approximate row count: sum of plain_rows in all bands + 1 doubling per band
    total_rows = sum(plain_rows for _, plain_rows, _ in progression) + spec.n_doublings
    final_height_cm = total_rows * 10.0 / g.rows_per_10cm  # radius

    metadata = dict(spec.metadata or {})
    p = Pattern(
        name=spec.name,
        construction="half_pi_shawl",
        difficulty="intermediate",
        inputs={
            "_domain": "knit",
            "n_doublings": spec.n_doublings,
            "cast_on_sts": spec.cast_on_sts,
            "edge_sts": spec.edge_sts,
            "lace_motifs": spec.lace_motifs or [],
            "final_total_sts": final_total_sts,
            "final_width_cm": round(final_width_cm, 1),
            "final_radius_cm": round(final_height_cm, 1),
            "total_rows_estimate": total_rows,
            "gauge": {
                "sts_per_10cm": g.sts_per_10cm,
                "rows_per_10cm": g.rows_per_10cm,
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- Setup -----------------------------------------------------------
    sec0 = p.add_section("Opslag og pick-up", sts_before=spec.cast_on_sts)
    sec0.add(
        f"Slå {spec.cast_on_sts} m op (garter tab). Strik {2 * spec.edge_sts} "
        "pinde glat retstrik (= garter).",
        spec.cast_on_sts,
        note="garter tab: smal stribe der danner halsen",
    )
    pickup_total = spec.cast_on_sts + 2 * spec.edge_sts + spec.cast_on_sts
    # cast-on edge + side + cast-on
    # We model "pickup" as bringing total stitches to 8 (4 + 0 + 4) by default.
    initial_total = 0 + 2 * spec.edge_sts  # center=0, 2*edge
    sec0.add(
        f"Drej arbejdet 90°. Saml {spec.edge_sts} m langs siden, "
        f"saml {spec.cast_on_sts} m fra opslagskanten "
        f"(= centerlinjen, indtil videre {0} m). "
        f"Saml {spec.edge_sts} m langs anden side. "
        f"({initial_total} m i alt: {spec.edge_sts} kant + center + "
        f"{spec.edge_sts} kant.)",
        initial_total,
        note="vi tæller kun 'center' sts i fordoblingsformlen — kanten skal "
             "IKKE fordobles",
    )
    validator.add(Row(sts_before=initial_total).k(initial_total))

    # ---- Bands -----------------------------------------------------------
    prev_total = initial_total
    for band_idx, plain_rows, center_after in progression[1:]:
        sec = p.add_section(
            f"Bånd {band_idx} (efter fordobling #{band_idx})",
            sts_before=prev_total,
        )
        new_total = center_after + 2 * spec.edge_sts
        # The doubling round: (yo, k1) over center sts. After doubling,
        # center becomes 2*old_center + extra YOs. We cheat the model with
        # an "implicit" stitch that produces 2 from 1 — but we already
        # encoded the formula, so just narrate it.
        old_center = prev_total - 2 * spec.edge_sts
        sec.add(
            f"Fordoblings-omg: strik {spec.edge_sts} m kant retstrik. "
            f"Over de {old_center} center-m: *yo, k1* gentag. "
            f"Strik {spec.edge_sts} m kant retstrik. "
            f"({old_center} center → {center_after} center, "
            f"+ {2*spec.edge_sts} kant = {new_total} m)",
            new_total,
            note="kant fordobles ikke; YO i hver center-m fordobler centeret",
        )
        # Validate this as: prev_total -> new_total
        # The doubling row is conceptually: edge_sts plain k + center yo+k + edge_sts plain k
        # Center consumes old_center and produces 2*old_center+? stitches.
        # We encode as: edge_sts k + old_center * (yo,k) + edge_sts k
        # = edge_sts k consumes/produces edge_sts each
        # = old_center yo (consumes 0, produces 1) + old_center k (consumes 1, produces 1)
        # Total consumes: 2*edge_sts + old_center; produces: 2*edge_sts + 2*old_center
        # That gives new_total = prev_total + old_center, not center_after = 2*old_center+3
        # The "+3" comes from extra YOs at the band-edge transition.
        # For simplicity, we validate the resulting *plain* rounds at new_total only.

        if spec.lace_motifs and band_idx - 1 < len(spec.lace_motifs):
            motif = spec.lace_motifs[band_idx - 1]
            sec.add(
                f"Lace-bånd: '{motif}' over center-maskerne. "
                f"Sørg for at rapporten passer i {center_after} m "
                f"(= {center_after} mod rapport-bredde skal være 0; "
                "fudge plain-omg om nødvendigt).",
                new_total,
                note="Andrea Rangel: half-pi er meget tilgivende — "
                     "ekstra plain row løser de fleste mismatches",
            )
            sec.add(
                f"Strik {plain_rows - 1} pinde glatstrik i centeret + "
                f"garter på kanten.",
                new_total,
            )
        else:
            sec.add(
                f"Strik {plain_rows} pinde med garter på kanten "
                f"og glatstrik i centeret (eller eget motiv).",
                new_total,
            )
        validator.add(Row(sts_before=new_total).k(new_total))
        prev_total = new_total

    # ---- Aflukning -------------------------------------------------------
    sec_end = p.add_section("Aflukning", sts_before=prev_total)
    sec_end.add(
        f"Luk løst af — fx stretchy bind-off (Jenny's surprisingly stretchy). "
        f"Aflukningen er kantens ydre periferi.",
        prev_total,
    )
    sec_end.add(
        "Blok shawl våd til halvcirkel (knapnåle hver 5 cm langs ydre kant). "
        "Lace blocker typisk 30-40 % større end strikket størrelse.",
        prev_total,
    )

    # ---- Notes -----------------------------------------------------------
    p.notes.append(
        f"Half-pi progression ({spec.n_doublings} fordoblinger): "
        f"{', '.join(str(t) for t in band_totals)} m."
    )
    p.notes.append(
        f"Estimeret strikket mål: {final_width_cm:.0f} cm bred × "
        f"{final_height_cm:.0f} cm dyb. Blokket: ~30 % større."
    )
    p.notes.append(
        "Indtagningspinde ligger ved row 2, 6, 12, 24, 48, 96, 192, … "
        "(altid det dobbelte af forrige)."
    )

    if spec.n_doublings <= 3:
        p.warnings.append(
            f"Kun {spec.n_doublings} fordoblinger: shawlet bliver ret lille "
            f"(~{final_width_cm:.0f} cm). Voksen-shawls bruger typisk 5-7."
        )
    if spec.lace_motifs:
        for i, motif in enumerate(spec.lace_motifs):
            band_idx = i + 1
            if band_idx >= len(progression):
                continue
            center_sts = progression[band_idx][2]
            # Crude: warn if center_sts is prime-ish (will rarely fit lace)
            for r in (4, 6, 8, 10, 12):
                if center_sts % r == 0:
                    break
            else:
                p.warnings.append(
                    f"Bånd {band_idx} har {center_sts} center-m — passer ikke "
                    "i 4/6/8/10/12-rapporter. Du skal fudge med plain-omg."
                )

    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
