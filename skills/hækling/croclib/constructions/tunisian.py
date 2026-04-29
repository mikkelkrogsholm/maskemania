"""Tunisian crochet basics — Tunisian Simple Stitch (TSS).

Per Agent B's research §5, Tunisian doesn't fit the simple
``(consumes, produces)`` model cleanly because each "row" is two passes:

* **Forward pass (FP)**: right→left, picks up loops onto a long hook.
* **Return pass (RP)**: left→right, ``ch 1`` then repeatedly ``yo, pull
  through 2 loops`` until 1 loop remains.

We follow Agent B's recommendation and use a separate ``TunisianRow``
class so the asymmetric passes are explicit. The data model:

    TunisianRow(width: int)
        .forward()   # populates `forward_loops = width`
        .return_()   # collapses to 1 loop on the hook

Stitch counts are constant across rows (TSS doesn't shape by default), so
on a per-row level the row-after-RP count = ``width``. Increases /
decreases happen on the forward pass and are *not* implemented here —
this construction sticks to the rectangle case.
"""

from __future__ import annotations
from dataclasses import dataclass

from lib.visualisering import Pattern, RowValidator
from ..crorow import CrochetRow


@dataclass
class TunisianRow:
    """A single Tunisian row = forward pass + return pass.

    Invariants:
      - ``forward_loops == width``
      - after ``return_()`` only 1 loop remains on the hook
      - the row "exposes" ``width`` vertical bars to the next row
    """

    width: int
    label: str = ""

    @property
    def sts_after(self) -> int:
        return self.width

    @property
    def forward_loops(self) -> int:
        return self.width

    def validate(self) -> None:
        if self.width < 1:
            raise ValueError(f"width must be >= 1 (got {self.width})")


@dataclass
class TunisianSpec:
    """Parameters for a flat Tunisian rectangle in TSS."""

    width_cm: float
    length_cm: float
    gauge_sts_per_cm: float = 2.5
    row_gauge_per_cm: float = 1.5
    base_stitch: str = "tss"   # "tss" | "tks" | "tps"
    name: str = "Tunisian-rektangel"
    metadata: dict | None = None


_BASE_STITCH_LABEL = {
    "tss": "Tunisian Simple Stitch (TSS)",
    "tks": "Tunisian Knit Stitch (TKS)",
    "tps": "Tunisian Purl Stitch (TPS)",
}


def generate_tunisian(spec: TunisianSpec, lang: str = "da") -> Pattern:
    if spec.width_cm <= 0 or spec.length_cm <= 0:
        raise ValueError("width_cm and length_cm must both be > 0")
    if spec.base_stitch not in _BASE_STITCH_LABEL:
        raise ValueError(
            f"unsupported base_stitch {spec.base_stitch!r}. "
            f"Allowed: {sorted(_BASE_STITCH_LABEL)}."
        )

    width_sts = max(2, round(spec.width_cm * spec.gauge_sts_per_cm))
    rows = max(1, round(spec.length_cm * spec.row_gauge_per_cm))
    foundation_ch = width_sts  # TSS conventionally chains W

    metadata = dict(spec.metadata or {})

    p = Pattern(
        name=spec.name,
        construction="tunisian",
        difficulty="intermediate",
        inputs={
            "_domain": "crochet",
            "width_cm": spec.width_cm,
            "length_cm": spec.length_cm,
            "width_sts": width_sts,
            "rows": rows,
            "base_stitch": spec.base_stitch,
            "base_stitch_label": _BASE_STITCH_LABEL[spec.base_stitch],
            "gauge_sts_per_cm": spec.gauge_sts_per_cm,
            "row_gauge_per_cm": spec.row_gauge_per_cm,
            "foundation_ch": foundation_ch,
            "gauge": {
                "sts_per_10cm": int(round(spec.gauge_sts_per_cm * 10)),
                "rows_per_10cm": int(round(spec.row_gauge_per_cm * 10)),
            },
            "metadata": metadata,
        },
    )

    validator = RowValidator()

    # ---- Foundation -----------------------------------------------------
    sec1 = p.add_section("Bundkæde", sts_before=0)
    sec1.add(
        f"Hækl {foundation_ch} lm med en lang Tunisian-hæklenål.",
        sts_after=foundation_ch,
        note=f"W = {width_sts} (= {spec.width_cm:.1f} cm × "
             f"{spec.gauge_sts_per_cm:.2f} m/cm)",
    )
    r0 = CrochetRow(sts_before=0, label="bundkæde")
    r0.ch(foundation_ch)
    validator.add(r0)

    # ---- Row 1 — foundation forward + return ---------------------------
    sec2 = p.add_section("Række 1 — opsamling", sts_before=foundation_ch)
    sec2.add(
        f"Forward pass (FP): pluk loops op gennem hver lm — "
        f"slut med {width_sts} loops på krogen.",
        sts_after=width_sts,
        note="ingen vending — RS er altid ud",
    )
    sec2.add(
        f"Return pass (RP): yo, træk gennem 1 loop. Derefter "
        f"*yo, træk gennem 2 loops* gentag til 1 loop tilbage.",
        sts_after=width_sts,
        note="RP'en lukker hver loop indtil kun den arbejdende loop er tilbage",
    )
    rows_log: list[TunisianRow] = []
    tr_first = TunisianRow(width=width_sts, label="R 1 FP+RP")
    tr_first.validate()
    rows_log.append(tr_first)

    # ---- Body rows ------------------------------------------------------
    sec3 = p.add_section("Krop", sts_before=width_sts)
    label = _BASE_STITCH_LABEL[spec.base_stitch]
    sec3.add(
        f"R 2: FP — for hver vertical bar: indsæt krogen under fronten "
        f"(eller ifølge {label}), yo, træk loop op. "
        f"Slut igen med {width_sts} loops.",
        sts_after=width_sts,
        note="første vertical bar springes over (kanten håndteres af "
             "sidste maske der hækles gennem begge lag)",
    )
    sec3.add(
        f"R 2: RP — som R 1.",
        sts_after=width_sts,
    )
    sec3.add(
        f"Gentag FP + RP i alt {rows - 1} gange efter R 1, "
        f"så arbejdet har {rows} rækker i alt "
        f"(≈ {rows / spec.row_gauge_per_cm:.1f} cm).",
        sts_after=width_sts,
    )
    for i in range(2, rows + 1):
        tr = TunisianRow(width=width_sts, label=f"R {i}")
        tr.validate()
        rows_log.append(tr)

    # ---- Bind off ------------------------------------------------------
    sec4 = p.add_section("Aflukning", sts_before=width_sts)
    sec4.add(
        "Aflukningsrække: *indsæt krogen i næste vertical bar, yo, træk "
        "gennem bar og loop på krog* — gentag på tværs. Klip garnet, "
        "hæft enden.",
        sts_after=width_sts,
        note="aflukning er en variant af sl-st langs hele kanten",
    )

    # ---- Notes & warnings ----------------------------------------------
    p.notes.append(
        f"Tunisian rektangel i {label}. {width_sts} m × {rows} rækker."
    )
    p.notes.append(
        "Tunisian curls — blok arbejdet vådt og strækk det ud, før det "
        "tørrer."
    )
    p.notes.append(
        f"Tunisian-rækker = FP + RP. Vi modellerer dem som "
        f"`TunisianRow(width={width_sts})` (separat klasse fra den "
        "almindelige (consumes, produces)-Row, jf. Agent B §5)."
    )

    p.validate_continuity()
    # attach the raw row log as inputs metadata for tests
    p.inputs["tunisian_rows"] = [
        {"width": r.width, "label": r.label, "forward": r.forward_loops}
        for r in rows_log
    ]
    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)
