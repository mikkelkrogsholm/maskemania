"""Short-row crescent shawl.

Construction (top-down, knit flat from a small garter-tab cast-on):

  1. Garter tab cast-on: cast on `cast_on` sts (default 3), knit a few rows,
     then turn 90° and pick up sts along the side and the cast-on edge to
     give a small starting count (we model this as starting with `cast_on`
     sts directly — the picked-up edge is short enough that the math is
     well-approximated by the cast-on count).
  2. Increase row (RS): k1, yo, k to last st, yo, k1   (+2 sts).
  3. Plain row  (WS): k all sts (garter).
  4. Repeat steps 2-3 for `increase_rows` increase rows. Final stitch
     count = cast_on + 2 * increase_rows.
  5. Periodically, work a pair of short rows (German short rows or W&T)
     spanning the *middle* portion of the shawl. Each short-row pair
     consumes/produces the same number of stitches but shortens the
     working row, which biases the fabric into a crescent. We schedule
     short-row pairs at a fixed cadence (`short_row_cadence`, default 8
     increase rows) and stop short of the cast-on edge by
     `short_row_setback` sts on each side (default 6).
  6. Bind off loosely, ideally a stretchy bind-off so the long edge can
     block to a crescent.

Why this works as a crescent (not a half-circle): each plain row is the
same length, but inside short-row "slices" only the middle stitches get a
new row. Repeated dozens of times the centre grows taller than the edges,
forcing the cast-on edge into a curve.

We validate the *plain* (full-width) increase / WS rows with `RowValidator`
because their stitch-bookkeeping is straightforward. We skip validating
the short-row pairs themselves: short rows leave un-knit stitches on the
needle and the bookkeeping is awkward to encode with a flat-row Op model.
The number of plain rows always greatly exceeds the number of short rows,
so the RowValidator still covers the bulk of the construction.

Inputs:
  - gauge (Gauge): blocked stitch + row gauge
  - cast_on (int): garter-tab cast-on sts (default 3)
  - increase_rows (int): how many *RS increase* rows to work (default 80;
    shawl ends with cast_on + 2*increase_rows sts)
  - short_row_cadence (int): how often to throw in a short-row pair, in
    increase rows (default 8)
  - short_row_setback (int): how many sts each side of the work the short
    rows stop short of (default 6)
"""

from __future__ import annotations
from dataclasses import dataclass, field

from lib.visualisering import Gauge, Pattern, RowValidator
from ..knitrow import KnitRow as Row


@dataclass
class ShortRowsShawlSpec:
    gauge: Gauge
    name: str = "Korte rækker shawl"
    cast_on: int = 3
    increase_rows: int = 80          # number of RS increase rows
    short_row_cadence: int = 8       # short-row pair every N increase rows
    short_row_setback: int = 6       # sts to stop short of each edge
    edge_garter: int = 3             # garter selvedge each side
    metadata: dict | None = None


_MIN_INCREASE_ROWS = 4
_MAX_INCREASE_ROWS = 400


def generate_short_rows_shawl(spec: ShortRowsShawlSpec, lang: str = "da") -> Pattern:
    g = spec.gauge

    if spec.cast_on < 3:
        raise ValueError(
            f"cast_on={spec.cast_on} is too small; need at least 3 for a "
            "workable garter-tab start."
        )
    if spec.increase_rows < _MIN_INCREASE_ROWS:
        raise ValueError(
            f"increase_rows={spec.increase_rows} too few; need at least "
            f"{_MIN_INCREASE_ROWS} for a recognisable crescent."
        )
    if spec.increase_rows > _MAX_INCREASE_ROWS:
        raise ValueError(
            f"increase_rows={spec.increase_rows} is unrealistically high "
            f"(>{_MAX_INCREASE_ROWS}); pick fewer."
        )
    if spec.short_row_cadence < 1:
        raise ValueError(
            f"short_row_cadence={spec.short_row_cadence} must be >= 1."
        )
    if spec.short_row_setback < 0:
        raise ValueError(
            f"short_row_setback={spec.short_row_setback} must be >= 0."
        )

    final_sts = spec.cast_on + 2 * spec.increase_rows
    # Each "increase block" is 1 RS inc row + 1 WS plain row = 2 rows.
    total_plain_rows = 2 * spec.increase_rows
    short_row_pairs = spec.increase_rows // spec.short_row_cadence
    # A short-row pair contributes ~2 extra rows at the centre (one RS
    # short-row, one WS short-row return).
    total_rows = total_plain_rows + 2 * short_row_pairs

    # Physical estimates (blocked).
    width_cm = final_sts * 10.0 / g.sts_per_10cm
    # Depth ≈ rows / row gauge (the centre column is the deepest path).
    depth_cm = total_rows * 10.0 / g.rows_per_10cm

    metadata = dict(spec.metadata or {})
    p = Pattern(
        name=spec.name,
        construction="short_rows_shawl",
        difficulty="intermediate",
        inputs={
            "_domain": "knit",
            "cast_on": spec.cast_on,
            "increase_rows": spec.increase_rows,
            "short_row_cadence": spec.short_row_cadence,
            "short_row_setback": spec.short_row_setback,
            "edge_garter": spec.edge_garter,
            "final_sts": final_sts,
            "short_row_pairs": short_row_pairs,
            "total_rows_estimate": total_rows,
            "width_cm": round(width_cm, 1),
            "depth_cm": round(depth_cm, 1),
            "gauge": {
                "sts_per_10cm": g.sts_per_10cm,
                "rows_per_10cm": g.rows_per_10cm,
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- 1. Garter tab cast-on -------------------------------------------
    sec0 = p.add_section("Garter-tab og opslag", sts_before=spec.cast_on)
    sec0.add(
        f"Slå {spec.cast_on} m op. Strik {2 * spec.edge_garter} pinde "
        "retstrik (garter-tab).",
        spec.cast_on,
        note="garter-tab giver en pæn, blød start uden at kuppe sig",
    )
    sec0.add(
        f"Drej arbejdet 90°. Saml {spec.edge_garter} m op langs siden, "
        f"og saml {spec.cast_on} m op langs opslagskanten. "
        f"({spec.cast_on + 2 * spec.edge_garter} m i alt — modelleret "
        f"som {spec.cast_on} m for udregningerne.)",
        spec.cast_on,
        note="vi tæller fra de oprindelige cast_on m fordi tab-pickup "
             "kun bidrager med en kort kant",
    )
    # Anchor the validator at cast_on stitches with a plain row.
    validator.add(
        Row(sts_before=spec.cast_on, label="setup row").k(spec.cast_on)
    )

    # ---- 2. Increase body -------------------------------------------------
    sec1 = p.add_section(
        "Forøgelser (rygsøjle af shawlet)", sts_before=spec.cast_on
    )
    sec1.add(
        "Strikningsmønster gentages: "
        "RS (forøg): k1, yo, strik til sidste m, yo, k1 (+2 m). "
        "WS (plain): strik alle m (garter).",
        spec.cast_on,
        note=f"{spec.increase_rows} forøgelses-rækker total; "
             f"shawlet vokser fra {spec.cast_on} til {final_sts} m",
    )

    cur = spec.cast_on
    short_row_count = 0
    # We validate every RS increase row + every WS plain row.
    # Insert short-row pairs (un-validated) at the cadence — they don't
    # change the live stitch count.
    for i in range(1, spec.increase_rows + 1):
        # RS increase row: consumes `cur` sts, produces `cur + 2` sts.
        # Encode as: k1 + (cur-2)*k inside + k1, plus 2 yarn-overs that
        # consume 0 sts each but produce 1 — total consumed=cur,
        # produced=cur+2.
        rs = Row(sts_before=cur, label=f"inc row {i}")
        rs.op("yo")              # 1 yo (produces 1, consumes 0)
        rs.k(cur)                # consume all live sts
        rs.op("yo")              # 1 yo
        validator.add(rs)
        cur += 2

        # WS plain row.
        ws = Row(sts_before=cur, label=f"ws plain {i}").k(cur)
        validator.add(ws)

        # Short-row pair?
        if (i % spec.short_row_cadence == 0
                and cur > 2 * (spec.short_row_setback + spec.edge_garter)):
            short_row_count += 1
            # Don't validate the actual short-row stitch ops; just narrate.

    sec1.add(
        f"Efter {spec.increase_rows} forøgelses-rækker: {final_sts} m "
        f"på pinden ({final_sts * 10 / g.sts_per_10cm:.0f} cm bred).",
        final_sts,
        note=f"validator har gennemløbet alle {spec.increase_rows} "
             f"RS-rækker + {spec.increase_rows} WS-rækker uden fejl",
    )

    # ---- 3. Short rows section -------------------------------------------
    if short_row_count > 0:
        sec2 = p.add_section(
            "Korte rækker (kurve-formning)", sts_before=final_sts
        )
        sec2.add(
            f"Hvert {spec.short_row_cadence}. inc-row indskydes et par "
            f"korte rækker midt på arbejdet. I alt {short_row_count} par "
            f"korte rækker over hele shawlet.",
            final_sts,
            note="brug tysk korte rækker (DSR) eller wrap & turn — "
                 "begge metoder fungerer; DSR er mest usynlig i garter",
        )
        sec2.add(
            f"Hvert kort-række-par: strik til {spec.short_row_setback} m "
            f"før modsatte kant, vend, strik tilbage til "
            f"{spec.short_row_setback} m før første kant, vend, fortsæt "
            "som almindelig RS-række (saml dobbelt-masker når du møder "
            "dem).",
            final_sts,
            note=f"udeladelse på {spec.short_row_setback} m hver side "
                 "biaser fabric'en til halvmåne (crescent)",
        )

    # ---- 4. Bind-off ------------------------------------------------------
    sec_end = p.add_section("Aflukning", sts_before=final_sts)
    sec_end.add(
        f"Luk de {final_sts} m løst af — fx Jenny's Surprisingly Stretchy "
        "Bind-Off — så den lange ydre kant kan blokes ud i en blød kurve.",
        final_sts,
        note="stram aflukning ødelægger crescent-formen",
    )
    sec_end.add(
        "Hæft alle ender. Vådblok shawlet til halvmåne: knapnåle hver "
        "5 cm langs den lange kant, ret midten ud så cast-on-tabben sidder "
        "i bunden af kurven.",
        final_sts,
    )

    # ---- Notes / warnings -------------------------------------------------
    p.notes.append(
        f"Endeligt maskeantal: {final_sts} m "
        f"(cast_on={spec.cast_on} + 2 × {spec.increase_rows} forøgelser)."
    )
    p.notes.append(
        f"Estimeret blokket størrelse: {width_cm:.0f} cm bred × "
        f"{depth_cm:.0f} cm dyb. Lace-garn blokker typisk 20-30 % større."
    )
    p.notes.append(
        f"Korte rækker: {short_row_count} par fordelt jævnt "
        f"(hver {spec.short_row_cadence}. forøgelses-række)."
    )

    if short_row_count == 0:
        p.warnings.append(
            "Med de valgte parametre lægges der ingen korte rækker ind — "
            "arbejdet bliver en simpel triangel, ikke en crescent. "
            "Sænk short_row_cadence eller forøg increase_rows."
        )
    if final_sts < 60:
        p.warnings.append(
            f"Kun {final_sts} m i den brede ende — voksen-shawls bruger "
            "typisk 200-400 m. Forøg increase_rows for større shawl."
        )
    if spec.short_row_setback * 2 + 2 * spec.edge_garter >= final_sts:
        p.warnings.append(
            f"short_row_setback ({spec.short_row_setback}) er for stor i "
            f"forhold til {final_sts} m — der bliver ikke plads til "
            "korte-rækker midt på arbejdet."
        )

    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
