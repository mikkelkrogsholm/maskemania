"""Amigurumi-figur — sammensæt af eksisterende sphere/cylinder-helpers.

Bygger en samlet "bjørn" eller "kanin" af 7 dele:

* krop  — ``amigurumi_sphere`` (lidt æg-formet via equator-omg)
* hoved — ``amigurumi_sphere``
* 2 ører — små ``amigurumi_cylinder`` med lukket bund (kanin: lange; bjørn: korte/runde)
* 2 arme — ``amigurumi_cylinder``
* 2 ben — ``amigurumi_cylinder``

Hver del valideres individuelt via dens egen ``RowValidator`` (ved at
genbruge ``amigurumi_sphere``/``amigurumi_cylinder``-funktionerne, som
allerede gør validering før de returnerer). Vi flader så sektionerne ud i
én samlet :class:`Pattern` — hver delkomponent får en banner-sektion +
arvede sektioner fra dens sub-pattern. Til slut tilføjer vi en
samle-sektion med tekst-instruktioner ("sy hovedet på kroppen ved …").

Alle sub-patterns slutter på 0 m (closed_top på cylindre, lukning på
sfærer), så ``validate_continuity`` på den samlede Pattern går igennem
uden problemer.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from lib.visualisering import Pattern

from .amigurumi import (
    AmigurumiSphereSpec, amigurumi_sphere,
    AmigurumiCylinderSpec, amigurumi_cylinder,
    DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM,
)


# Hver "art" har lidt forskellige proportioner. Stadig samme syv dele.
_SPECIES_PROFILES: dict[str, dict] = {
    "bjørn": {
        "name_default": "Amigurumi-bjørn",
        "body_diameter_factor": 0.75,
        "body_equator": 2,           # let æggeformet
        "head_diameter_factor": 0.60,
        "head_equator": 0,
        "ear_diameter_factor": 0.18,
        "ear_height_factor": 0.18,
        "arm_diameter_factor": 0.22,
        "arm_height_factor": 0.45,
        "leg_diameter_factor": 0.25,
        "leg_height_factor": 0.40,
    },
    "kanin": {
        "name_default": "Amigurumi-kanin",
        "body_diameter_factor": 0.70,
        "body_equator": 3,
        "head_diameter_factor": 0.55,
        "head_equator": 1,
        "ear_diameter_factor": 0.14,
        "ear_height_factor": 0.55,   # lange ører
        "arm_diameter_factor": 0.20,
        "arm_height_factor": 0.45,
        "leg_diameter_factor": 0.22,
        "leg_height_factor": 0.40,
    },
}


@dataclass
class AmigurumiFigurSpec:
    """Parametre for en amigurumi-figur (bjørn eller kanin)."""
    scale_cm: float = 12.0          # samlet højde (krop + hoved) — ca.
    species: str = "bjørn"          # "bjørn" eller "kanin"
    gauge_sc_per_cm: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM
    row_gauge_per_cm: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM
    start_count: int = 6
    name: str = ""                  # "" = brug arts-default
    extras: list[str] = field(default_factory=list)  # fx ["hale", "snude"] — TODO


def amigurumi_figur(spec: AmigurumiFigurSpec | None = None, *,
                    scale_cm: float | None = None,
                    species: str = "bjørn",
                    gauge: float | None = None,
                    name: str = "",
                    lang: str = "da") -> Pattern:
    """Generér en sammensat amigurumi-figur.

    Returnerer ÉN :class:`Pattern` med flere sektioner — én banner-sektion
    per delkomponent + de validerede rounds fra hver sub-pattern. Alle
    delkomponenter er individuelt mask-validerede via deres respektive
    ``amigurumi_sphere`` / ``amigurumi_cylinder``-kald.
    """
    if spec is None:
        if scale_cm is None:
            raise ValueError("either spec or scale_cm must be given")
        spec = AmigurumiFigurSpec(
            scale_cm=scale_cm,
            species=species,
            gauge_sc_per_cm=gauge or DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM,
            name=name,
        )

    if spec.scale_cm <= 0:
        raise ValueError(f"scale_cm must be > 0 (got {spec.scale_cm})")
    if spec.species not in _SPECIES_PROFILES:
        raise ValueError(
            f"species must be one of {sorted(_SPECIES_PROFILES)} "
            f"(got {spec.species!r})"
        )

    prof = _SPECIES_PROFILES[spec.species]
    name = spec.name or prof["name_default"]
    s = spec.scale_cm

    # ----- Build sub-patterns (each is itself fully validated) ---------------
    body_pat = amigurumi_sphere(AmigurumiSphereSpec(
        diameter_cm=s * prof["body_diameter_factor"],
        gauge_sc_per_cm=spec.gauge_sc_per_cm,
        start_count=spec.start_count,
        equator_rounds=prof["body_equator"],
        name=f"{name} — krop",
    ))
    head_pat = amigurumi_sphere(AmigurumiSphereSpec(
        diameter_cm=s * prof["head_diameter_factor"],
        gauge_sc_per_cm=spec.gauge_sc_per_cm,
        start_count=spec.start_count,
        equator_rounds=prof["head_equator"],
        name=f"{name} — hoved",
    ))
    ear_pat = amigurumi_cylinder(AmigurumiCylinderSpec(
        diameter_cm=s * prof["ear_diameter_factor"],
        height_cm=s * prof["ear_height_factor"],
        gauge_sc_per_cm=spec.gauge_sc_per_cm,
        row_gauge_per_cm=spec.row_gauge_per_cm,
        start_count=spec.start_count,
        closed_top=True,
        name=f"{name} — øre",
    ))
    arm_pat = amigurumi_cylinder(AmigurumiCylinderSpec(
        diameter_cm=s * prof["arm_diameter_factor"],
        height_cm=s * prof["arm_height_factor"],
        gauge_sc_per_cm=spec.gauge_sc_per_cm,
        row_gauge_per_cm=spec.row_gauge_per_cm,
        start_count=spec.start_count,
        closed_top=True,
        name=f"{name} — arm",
    ))
    leg_pat = amigurumi_cylinder(AmigurumiCylinderSpec(
        diameter_cm=s * prof["leg_diameter_factor"],
        height_cm=s * prof["leg_height_factor"],
        gauge_sc_per_cm=spec.gauge_sc_per_cm,
        row_gauge_per_cm=spec.row_gauge_per_cm,
        start_count=spec.start_count,
        closed_top=True,
        name=f"{name} — ben",
    ))

    parts: list[tuple[str, Pattern, int]] = [
        ("Krop", body_pat, 1),
        ("Hoved", head_pat, 1),
        ("Ører", ear_pat, 2),
        ("Arme", arm_pat, 2),
        ("Ben", leg_pat, 2),
    ]

    # ----- Compose top-level Pattern ----------------------------------------
    p = Pattern(
        name=name,
        construction="amigurumi_figur",
        difficulty="easy",
        inputs={
            "_domain": "crochet",
            "species": spec.species,
            "scale_cm": spec.scale_cm,
            "gauge_sc_per_cm": spec.gauge_sc_per_cm,
            "start_count": spec.start_count,
            "gauge": {
                "sts_per_10cm": int(round(spec.gauge_sc_per_cm * 10)),
                "rows_per_10cm": int(round(spec.row_gauge_per_cm * 10)),
            },
            "parts": [
                {"label": label, "count": count,
                 "construction": sub.construction,
                 "diameter_cm": sub.inputs.get("diameter_cm"),
                 "height_cm": sub.inputs.get("height_cm")}
                for label, sub, count in parts
            ],
        },
    )

    # Each sub-pattern starts at 0 m and ends at 0 m (closed_top / lukning),
    # so we can flatten sections in sequence without breaking continuity.
    for label, sub, count in parts:
        banner = p.add_section(
            f"Del: {label} ({count}×)" if count > 1 else f"Del: {label}",
            sts_before=0,
        )
        # Inkluder en kort opsummering af målene som en "step" på 0 m (uden
        # masker — det er rent informativt).
        d_cm = sub.inputs.get("diameter_cm")
        h_cm = sub.inputs.get("height_cm")
        if d_cm is not None and h_cm is not None:
            summary = (f"{count}× cylinder, ⌀ {d_cm:.1f} cm × "
                       f"{h_cm:.1f} cm. Hækl én ad gangen.")
        elif d_cm is not None:
            summary = (f"{count}× kugle, ⌀ {d_cm:.1f} cm. Hækl én ad gangen."
                       if count > 1 else f"Kugle, ⌀ {d_cm:.1f} cm.")
        else:
            summary = f"{count}× delkomponent."
        banner.add(summary, sts_after=0,
                   note=f"se sub-omgangene nedenfor — gentag {count} gang(e)")
        # Append all sub-sections inline. Each starts/ends at 0, so continuity
        # holds.
        for sub_sec in sub.sections:
            new_sec = p.add_section(f"  {label} · {sub_sec.title}",
                                    sts_before=sub_sec.sts_before)
            for st in sub_sec.steps:
                new_sec.add(st.text, sts_after=st.sts_after,
                            repeats=st.repeats, note=st.note)
        # Forward sub-pattern notes/warnings prefixed with the part label.
        for n in sub.notes:
            p.notes.append(f"[{label}] {n}")
        for w in sub.warnings:
            p.warnings.append(f"[{label}] {w}")

    # ----- Final assembly section -------------------------------------------
    asm = p.add_section("Samling", sts_before=0)
    asm.add(
        "Læg alle 8 dele klar (krop, hoved, 2 ører, 2 arme, 2 ben) "
        "med fyldet pakket fast. Brug en lang stoppenål og samme garn.",
        sts_after=0,
    )
    asm.add(
        "Sy hovedet til kroppen: placér hovedet centreret på toppen af kroppen, "
        "og sy hele vejen rundt med små, tætte fm-sting gennem begge dele.",
        sts_after=0,
        note="2 omgange sting giver en stærkere samling",
    )
    if spec.species == "kanin":
        ear_note = (
            "Ørerne placeres øverst på hovedet med ca. 2 fm imellem og let bagudvendt. "
            "Sy nederste kant på ørerne ind i hovedet."
        )
    else:
        ear_note = (
            "Ørerne placeres øverst på hovedet, ca. 1 cm fra hinanden. "
            "Klem ørerne lidt flade før de sys på, så de holder formen."
        )
    asm.add(f"Sæt ørerne på hovedet: {ear_note}", sts_after=0)
    asm.add(
        "Sy armene på siderne af kroppen: tæt under hovedet, ca. ⅓ ned ad kroppen. "
        "Sørg for at armene står symmetrisk.",
        sts_after=0,
    )
    asm.add(
        "Sy benene fast i bunden af kroppen: med en afstand på ca. 1 fm imellem, "
        "så figuren kan stå/sidde balanceret.",
        sts_after=0,
    )
    asm.add(
        "Pres øjnene ind på hovedet (sikkerheds-øjne sættes FØR samling, broderede "
        "øjne kan sys på til sidst). Placér øjnene ca. midt på hovedet med 4–6 fm "
        "imellem og 2–3 omg over halsen.",
        sts_after=0,
        note="for små børn: brug broderet øje, ikke sikkerheds-øjne",
    )
    asm.add(
        "Broder næse + mund med kontrastgarn lige under øjnene. Hæft alle ender "
        "ind i kroppen.",
        sts_after=0,
    )

    p.notes.append(
        f"Samlet figur: {spec.species} på ~{spec.scale_cm:.0f} cm "
        f"(krop + hoved). Total: 8 dele."
    )
    p.notes.append(
        "Hver delkomponent er individuelt maskevalideret via samme math som "
        "amigurumi_sphere / amigurumi_cylinder."
    )

    p.validate_continuity()
    from lib.visualisering.lang.construction_strings import translate_pattern
    return translate_pattern(p, lang)


# Convenience aliases used by the CLI / tests.
def amigurumi_bjørn(scale_cm: float = 12.0, *,
                    gauge: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM,
                    name: str = "",
                    lang: str = "da") -> Pattern:
    return amigurumi_figur(AmigurumiFigurSpec(
        scale_cm=scale_cm,
        species="bjørn",
        gauge_sc_per_cm=gauge,
        name=name,
    ), lang=lang)


def amigurumi_kanin(scale_cm: float = 12.0, *,
                    gauge: float = DEFAULT_AMIGURUMI_GAUGE_SC_PER_CM,
                    name: str = "",
                    lang: str = "da") -> Pattern:
    return amigurumi_figur(AmigurumiFigurSpec(
        scale_cm=scale_cm,
        species="kanin",
        gauge_sc_per_cm=gauge,
        name=name,
    ), lang=lang)
