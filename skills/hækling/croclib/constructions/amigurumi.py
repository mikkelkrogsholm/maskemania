"""Amigurumi shapes — sphere, cylinder, taper.

Standard amigurumi recipe (see Agent B's research §2):

* Magic ring with N start stitches (6 is the ubiquitous default).
* Each round increases by N stitches (6, 12, 18, 24, …) until the desired
  diameter — the math is just ``circumference ≈ 2·π·radius``, rounded to
  the start count.
* Without staggering the increases land on top of each other and the piece
  becomes a hexagon, not a circle. We stagger by shifting the increase
  position one stitch per round.
* For a sphere we increase up to ``N_max``, optionally hold for a few
  equator rounds, then mirror the increase plan as decreases.

All rounds are validated through :class:`RowValidator`: a row that doesn't
balance raises :class:`ValidationError` immediately. No stitch count is
ever guessed.
"""

from __future__ import annotations
from dataclasses import dataclass

import math

from lib.visualisering import Pattern, RowValidator
from ..crorow import CrochetRow
from ..stitches import magic_ring, stitch


# Default amigurumi gauge if the caller didn't measure one.
# Tightly worked sc on a smaller hook than yarn label suggests; ~5 sc/cm
# horizontally, ~5 rows/cm vertically.
DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM = 5.0


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _flat_circle_round(round_n: int, start_count: int = 6) -> tuple[int, list[tuple[str, int]]]:
    """Stitch recipe for the N-th flat-circle round (1-indexed).

    Returns ``(stitches_after, ops)`` where ``ops`` is a list of
    ``(stitch_code, count)`` pairs — a stylised text recipe like
    ``[("sc", 1), ("sc_inc", 1)]`` repeated 6 times.

    For round N (N >= 1):

    * Round 1: ``magic_ring(start_count)`` — ``start_count`` sc.
    * Round 2: ``start_count`` × ``sc_inc`` → ``2·start_count``.
    * Round N (N>=3): ``start_count`` repeats of ``[(N-2) sc, 1 sc_inc]``
      → ``N·start_count`` stitches.
    """
    if round_n <= 0:
        raise ValueError(f"round_n must be >= 1 (got {round_n})")
    if round_n == 1:
        return start_count, [("mr", start_count)]
    plain_per_repeat = round_n - 2  # 0 for round 2, 1 for round 3, ...
    return round_n * start_count, _repeat_recipe(plain_per_repeat, start_count)


def _repeat_recipe(plain_sc: int, n_repeats: int) -> list[tuple[str, int]]:
    """``n_repeats × [plain_sc sc, 1 sc_inc]``, flattened."""
    out: list[tuple[str, int]] = []
    if plain_sc > 0:
        # we keep the per-repeat structure visible by chunking
        for _ in range(n_repeats):
            out.append(("sc", plain_sc))
            out.append(("sc_inc", 1))
    else:
        out.append(("sc_inc", n_repeats))
    return out


def _decrease_recipe(plain_sc: int, n_repeats: int) -> list[tuple[str, int]]:
    """``n_repeats × [plain_sc sc, 1 sc2tog]``, flattened."""
    out: list[tuple[str, int]] = []
    if plain_sc > 0:
        for _ in range(n_repeats):
            out.append(("sc", plain_sc))
            out.append(("sc2tog", 1))
    else:
        out.append(("sc2tog", n_repeats))
    return out


def _l(da: str, en: str, lang: str) -> str:
    return en if lang == "en" else da


def _round_text(ops: list[tuple[str, int]], *, repeats_label: int | None,
                stagger_offset: int = 0, lang: str = "da") -> str:
    """Pretty-print a list of ops with optional repeat-bracket and stagger."""
    parts: list[str] = []
    if repeats_label is not None and len(ops) > 1:
        first_two = ops[: 2 if ops[0][0] == "sc" else 1]
        inner = ", ".join(_op_to_text(name, n, lang) for name, n in first_two)
        parts.append(f"[{inner}] × {repeats_label}")
    else:
        parts.extend(_op_to_text(name, n, lang) for name, n in ops)
    text = ", ".join(parts)
    if stagger_offset:
        text += _l(f" (forskyd start med {stagger_offset} m)",
                   f" (shift the start by {stagger_offset} sts)", lang)
    return text


def _op_to_text(name: str, n: int, lang: str = "da") -> str:
    if name == "mr":
        return _l(f"magic ring med {n} fm",
                  f"magic ring with {n} sc", lang)
    if name == "sc":
        if lang == "en":
            return f"{n} sc" if n > 1 else "1 sc"
        return f"{n} fm" if n > 1 else "1 fm"
    if name == "sc_inc":
        if lang == "en":
            return f"{n} inc" if n > 1 else "1 inc (2 sc in same st)"
        return f"{n} udt" if n > 1 else "1 udt (2 fm i samme m)"
    if name == "sc2tog":
        if lang == "en":
            return f"{n} dec" if n > 1 else "1 dec (sc2tog)"
        return f"{n} indt" if n > 1 else "1 indt (2 fm sm)"
    return f"{n} {name}"


# ---------------------------------------------------------------------------
# Sphere
# ---------------------------------------------------------------------------

@dataclass
class AmigurumiSphereSpec:
    """Parameters for an amigurumi sphere."""
    diameter_cm: float
    gauge_sc_per_cm: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM
    start_count: int = 6
    name: str = "Amigurumi-kugle"
    equator_rounds: int = 0  # extra straight rounds at max diameter (0 = pure sphere)


def amigurumi_sphere(spec: AmigurumiSphereSpec | None = None, *,
                     diameter_cm: float | None = None,
                     gauge_sc_per_cm: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM,
                     start_count: int = 6,
                     equator_rounds: int = 0,
                     name: str = "Amigurumi-kugle",
                     lang: str = "da") -> Pattern:
    """Generate a parametric amigurumi sphere of the given diameter.

    The math (Agent B §2): a flat circle of N rounds has stitch-count
    ``start_count·N`` and a circumference of the same number of stitches.
    Real diameter is ``(start_count·N) / π / gauge``.

    For a sphere we pick ``N_max`` so the equator diameter matches the spec,
    increase 1..N_max, optionally hold ``equator_rounds`` straight, then
    decrease N_max..1 (mirror).
    """
    if spec is None:
        if diameter_cm is None:
            raise ValueError("either spec or diameter_cm must be given")
        spec = AmigurumiSphereSpec(
            diameter_cm=diameter_cm,
            gauge_sc_per_cm=gauge_sc_per_cm,
            start_count=start_count,
            equator_rounds=equator_rounds,
            name=name,
        )

    if spec.diameter_cm <= 0:
        raise ValueError(f"diameter_cm must be > 0 (got {spec.diameter_cm})")
    if spec.gauge_sc_per_cm <= 0:
        raise ValueError(
            f"gauge_sc_per_cm must be > 0 (got {spec.gauge_sc_per_cm})"
        )

    # Pick N_max so that the equator circumference matches diameter.
    target_circ_sts = math.pi * spec.diameter_cm * spec.gauge_sc_per_cm
    n_max = max(2, round(target_circ_sts / spec.start_count))

    max_sts = spec.start_count * n_max
    real_diameter_cm = max_sts / math.pi / spec.gauge_sc_per_cm

    p = Pattern(
        name=spec.name,
        construction="amigurumi_sphere",
        difficulty="beginner",
        inputs={
            "_domain": "crochet",
            "diameter_cm": spec.diameter_cm,
            "actual_diameter_cm": round(real_diameter_cm, 2),
            "gauge_sc_per_cm": spec.gauge_sc_per_cm,
            "start_count": spec.start_count,
            "n_max": n_max,
            "max_sts": max_sts,
            "equator_rounds": spec.equator_rounds,
            # gauge in the format the shared HTML cover-builder expects
            "gauge": {
                "sts_per_10cm": int(round(spec.gauge_sc_per_cm * 10)),
                "rows_per_10cm": int(round(spec.gauge_sc_per_cm * 10)),
            },
        },
    )

    validator = RowValidator()

    # ----- Section 1: materials / start ----------------------------------
    sec1 = p.add_section(_l("Start", "Start", lang), sts_before=0)
    sec1.add(
        _l(f"Lav en magic ring med {spec.start_count} fm.",
           f"Make a magic ring with {spec.start_count} sc.",
           lang),
        sts_after=spec.start_count,
        note=_l(f"alternativt: lm 2, derefter {spec.start_count} fm i 2. lm fra hægten.",
                f"alternative: ch 2, then {spec.start_count} sc in the 2nd ch from the hook.",
                lang),
    )
    # validate
    r0 = CrochetRow(sts_before=0, label="Omg 1 (magic ring)")
    r0.magic_ring(spec.start_count)
    validator.add(r0)

    # ----- Section 2: top half (increases) -------------------------------
    sec2 = p.add_section(
        _l("Øvre halvdel — udtagninger", "Top half — increases", lang),
        sts_before=spec.start_count,
    )
    for n in range(2, n_max + 1):
        sts_after, ops = _flat_circle_round(n, spec.start_count)
        r = CrochetRow(sts_before=(n - 1) * spec.start_count, label=f"Omg {n}")
        for code, cnt in ops:
            r.op(code, cnt)
        validator.add(r)
        rnd_label = _l(f"Omg {n}", f"Rnd {n}", lang)
        text = (f"{rnd_label}: "
                + _round_text(ops, repeats_label=spec.start_count,
                              stagger_offset=(n - 2) % max(1, n - 1),
                              lang=lang))
        sec2.add(
            f"{text}.",
            sts_after=sts_after,
            note=_l("6 udt jævnt fordelt; forskyd starten 1 m pr. omg",
                    "6 inc evenly spaced; shift the start by 1 st each rnd",
                    lang),
        )

    # ----- Section 3: equator --------------------------------------------
    sec3 = p.add_section(_l("Ækvator", "Equator", lang), sts_before=max_sts)
    if spec.equator_rounds > 0:
        for k in range(spec.equator_rounds):
            r = CrochetRow(sts_before=max_sts, label=f"Omg {n_max + 1 + k} (lige)")
            r.sc(max_sts)
            validator.add(r)
        sec3.add(
            _l(f"Strik {spec.equator_rounds} omg lige fm ({max_sts} m pr. omg) "
               "— skaber ækvator.",
               f"Work {spec.equator_rounds} plain rnds of sc ({max_sts} sts per rnd) "
               "— creates the equator.",
               lang),
            sts_after=max_sts,
        )
    else:
        sec3.add(
            _l("Ingen ækvator-omg (ren matematisk kugle).",
               "No equator rounds (pure mathematical sphere).",
               lang),
            sts_after=max_sts,
            note=_l("tilføj equator_rounds=1..N for stuffer-friendly oval form",
                    "add equator_rounds=1..N for a stuffer-friendly oval shape",
                    lang),
        )

    # ----- Section 4: bottom half (decreases) ----------------------------
    sec4 = p.add_section(
        _l("Nedre halvdel — indtagninger", "Bottom half — decreases", lang),
        sts_before=max_sts,
    )
    for k in range(1, n_max):
        sts_before = (n_max - k + 1) * spec.start_count
        sts_after = (n_max - k) * spec.start_count
        plain_sc = (n_max - k) - 1
        ops = _decrease_recipe(plain_sc, spec.start_count)
        r = CrochetRow(sts_before=sts_before,
                       label=f"Indt-omg {k}")
        for code, cnt in ops:
            r.op(code, cnt)
        validator.add(r)
        rnd_label = _l(f"Indt-omg {k}", f"Dec rnd {k}", lang)
        text = (f"{rnd_label}: "
                + _round_text(ops, repeats_label=spec.start_count,
                              stagger_offset=(k - 1) % max(1, n_max - k),
                              lang=lang))
        sec4.add(f"{text}.", sts_after=sts_after)

    # ----- Section 5: closing --------------------------------------------
    sec5 = p.add_section(_l("Lukning", "Closing", lang),
                         sts_before=spec.start_count)
    sec5.add(
        _l("Stop med fyld før den er helt lukket.",
           "Stuff with fiberfill before fully closing.",
           lang),
        sts_after=spec.start_count,
    )
    sec5.add(
        _l(f"Klip garnet, træk gennem de sidste {spec.start_count} fm med "
           "en stoppenål, stram til og hæft enden ind i kuglen.",
           f"Cut the yarn, thread through the last {spec.start_count} sc with "
           "a tapestry needle, pull tight and weave the end into the sphere.",
           lang),
        sts_after=0,
    )

    # Notes
    p.notes.append(
        _l(f"Faktisk diameter: {real_diameter_cm:.2f} cm (mål: "
           f"{spec.diameter_cm:.2f} cm) ved gauge {spec.gauge_sc_per_cm} fm/cm.",
           f"Actual diameter: {real_diameter_cm:.2f} cm (target: "
           f"{spec.diameter_cm:.2f} cm) at gauge {spec.gauge_sc_per_cm} sc/cm.",
           lang)
    )
    p.notes.append(
        _l("Stagger increases (forskyd udtagningerne 1 m pr. omg) så kuglen "
           "ikke bliver hexagonal. Marker første m i hver omg med en "
           "maskemarkør.",
           "Stagger the increases (shift them 1 st per rnd) so the sphere "
           "does not become hexagonal. Mark the first st of each rnd with a "
           "stitch marker.",
           lang)
    )
    p.notes.append(
        _l(f"Total antal omg: {2 * n_max - 1 + spec.equator_rounds} "
           f"({n_max - 1} udt + {spec.equator_rounds} lige + {n_max - 1} indt + "
           "1 magic-ring start).",
           f"Total rounds: {2 * n_max - 1 + spec.equator_rounds} "
           f"({n_max - 1} inc + {spec.equator_rounds} plain + {n_max - 1} dec + "
           "1 magic-ring start).",
           lang)
    )

    p.validate_continuity()
    return p


# ---------------------------------------------------------------------------
# Cylinder (best-effort: increase to N_max, hold for height, decrease)
# ---------------------------------------------------------------------------

@dataclass
class AmigurumiCylinderSpec:
    diameter_cm: float
    height_cm: float
    gauge_sc_per_cm: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM
    row_gauge_per_cm: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM
    start_count: int = 6
    name: str = "Amigurumi-cylinder"
    closed_top: bool = True


def amigurumi_cylinder(spec: AmigurumiCylinderSpec, lang: str = "da") -> Pattern:
    """Closed (or open) cylinder: flat-disc bottom, straight tube, optional decrease cap."""
    if spec.diameter_cm <= 0 or spec.height_cm <= 0:
        raise ValueError("diameter_cm and height_cm must both be > 0")
    target_circ_sts = math.pi * spec.diameter_cm * spec.gauge_sc_per_cm
    n_max = max(2, round(target_circ_sts / spec.start_count))
    max_sts = spec.start_count * n_max
    tube_rows = max(1, round(spec.height_cm * spec.row_gauge_per_cm))

    p = Pattern(
        name=spec.name,
        construction="amigurumi_cylinder",
        difficulty="beginner",
        inputs={
            "_domain": "crochet",
            "diameter_cm": spec.diameter_cm,
            "height_cm": spec.height_cm,
            "n_max": n_max,
            "max_sts": max_sts,
            "tube_rows": tube_rows,
            "closed_top": spec.closed_top,
            "gauge_sc_per_cm": spec.gauge_sc_per_cm,
            "gauge": {
                "sts_per_10cm": int(round(spec.gauge_sc_per_cm * 10)),
                "rows_per_10cm": int(round(spec.row_gauge_per_cm * 10)),
            },
        },
    )

    validator = RowValidator()

    sec1 = p.add_section(_l("Bund", "Base", lang), sts_before=0)
    sec1.add(
        _l(f"Magic ring med {spec.start_count} fm.",
           f"Magic ring with {spec.start_count} sc.",
           lang),
        sts_after=spec.start_count,
    )
    r = CrochetRow(sts_before=0)
    r.magic_ring(spec.start_count)
    validator.add(r)

    for n in range(2, n_max + 1):
        sts_after, ops = _flat_circle_round(n, spec.start_count)
        r = CrochetRow(sts_before=(n - 1) * spec.start_count)
        for code, cnt in ops:
            r.op(code, cnt)
        validator.add(r)
        rnd_label = _l(f"Omg {n}", f"Rnd {n}", lang)
        sec1.add(
            f"{rnd_label}: " + _round_text(ops, repeats_label=spec.start_count, lang=lang) + ".",
            sts_after=sts_after,
        )

    sec2 = p.add_section(_l("Tube", "Tube", lang), sts_before=max_sts)
    sec2.add(
        _l(f"Strik {tube_rows} omg lige fm i hver maske ({max_sts} m pr. omg).",
           f"Work {tube_rows} plain rnds of sc into each st ({max_sts} sts per rnd).",
           lang),
        sts_after=max_sts,
        note=_l(f"≈ {spec.height_cm:.0f} cm højde",
                f"≈ {spec.height_cm:.0f} cm tall", lang),
    )
    for _ in range(tube_rows):
        r = CrochetRow(sts_before=max_sts)
        r.sc(max_sts)
        validator.add(r)

    if spec.closed_top:
        sec3 = p.add_section(
            _l("Lukning af top", "Closing the top", lang), sts_before=max_sts)
        for k in range(1, n_max):
            sts_before = (n_max - k + 1) * spec.start_count
            sts_after = (n_max - k) * spec.start_count
            plain_sc = (n_max - k) - 1
            ops = _decrease_recipe(plain_sc, spec.start_count)
            r = CrochetRow(sts_before=sts_before)
            for code, cnt in ops:
                r.op(code, cnt)
            validator.add(r)
            rnd_label = _l(f"Indt-omg {k}", f"Dec rnd {k}", lang)
            sec3.add(
                f"{rnd_label}: "
                + _round_text(ops, repeats_label=spec.start_count, lang=lang) + ".",
                sts_after=sts_after,
            )
        sec3.add(
            _l(f"Klip garnet, træk gennem de sidste {spec.start_count} fm.",
               f"Cut the yarn, thread through the last {spec.start_count} sc.",
               lang),
            sts_after=0,
        )

    p.notes.append(
        _l(f"Tube-omg: {tube_rows} (≈ {tube_rows / spec.row_gauge_per_cm:.1f} cm).",
           f"Tube rounds: {tube_rows} (≈ {tube_rows / spec.row_gauge_per_cm:.1f} cm).",
           lang)
    )
    p.validate_continuity()
    return p


# ---------------------------------------------------------------------------
# Taper (linear cone) — TODO, leaving a minimal stub
# ---------------------------------------------------------------------------

@dataclass
class AmigurumiTaperSpec:
    d_top_cm: float
    d_bottom_cm: float
    height_cm: float
    gauge_sc_per_cm: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM
    row_gauge_per_cm: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM
    start_count: int = 6
    name: str = "Amigurumi-taper"


def amigurumi_taper(spec: AmigurumiTaperSpec, lang: str = "da") -> Pattern:
    """Linear taper from d_bottom to d_top over height_cm.

    NOTE: minimal implementation — just increases or decreases evenly across
    rounds to interpolate between the two diameters. Stagger-friendly. For
    proper amigurumi shaping (head/body/torso) use a chain of taper +
    cylinder + sphere parts. TODO: smarter shaping.
    """
    if spec.height_cm <= 0:
        raise ValueError("height_cm must be > 0")
    n_top = max(1, round(math.pi * spec.d_top_cm * spec.gauge_sc_per_cm / spec.start_count))
    n_bot = max(1, round(math.pi * spec.d_bottom_cm * spec.gauge_sc_per_cm / spec.start_count))
    rows = max(abs(n_top - n_bot), round(spec.height_cm * spec.row_gauge_per_cm))

    p = Pattern(
        name=spec.name,
        construction="amigurumi_taper",
        difficulty="beginner",
        inputs={
            "_domain": "crochet",
            "d_top_cm": spec.d_top_cm,
            "d_bottom_cm": spec.d_bottom_cm,
            "height_cm": spec.height_cm,
            "n_top": n_top,
            "n_bot": n_bot,
            "rows": rows,
            "gauge_sc_per_cm": spec.gauge_sc_per_cm,
            "gauge": {
                "sts_per_10cm": int(round(spec.gauge_sc_per_cm * 10)),
                "rows_per_10cm": int(round(spec.row_gauge_per_cm * 10)),
            },
        },
    )
    p.warnings.append(
        "Taper-konstruktionen er en minimal stub. Den interpolerer kun "
        "diameter lineært og laver IKKE staggered shaping. Brug "
        "`amigurumi_sphere` + `amigurumi_cylinder` til seriøse projekter."
    )
    sec = p.add_section("Taper", sts_before=spec.start_count * n_bot)
    sec.add(
        f"Start fra {spec.start_count * n_bot} m, slut på "
        f"{spec.start_count * n_top} m over {rows} omg.",
        sts_after=spec.start_count * n_top,
    )
    p.validate_continuity()
    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
