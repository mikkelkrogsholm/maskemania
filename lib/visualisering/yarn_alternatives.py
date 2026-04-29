"""Yarn-substitute rendering helpers (Fase 5 iter 5).

Bridges :mod:`yarn_db` to the HTML / Markdown layer. The CLI flag
``--substitut`` (knit) and ``--garn-alternativer`` (crochet) attach a
list of suggested alternatives to ``pattern.inputs["yarn_alternatives"]``
which is a list of dicts. The HTML layer renders an ``<aside
class="yarn-alternatives">`` next to the materials box; markdown adds a
``## Garn-alternativer`` section.

All functions are pure: they take a Pattern + base yarn and return data,
they do not mutate global state. Tests can call them directly.
"""

from __future__ import annotations

import html as _htmllib
from dataclasses import asdict, dataclass
from typing import Iterable

from .yarn_db import Yarn, lookup_yarn, suggest_substitute
from .lang import t
from .pattern import Pattern


@dataclass(frozen=True)
class YarnAlternative:
    """Render-friendly substitute summary."""
    name: str
    weight_class: str
    fiber: str
    meters_per_50g: int
    needle_mm: float
    hook_mm: float
    sts_per_10cm: int
    rows_per_10cm: int
    gauge_diff_pct: float       # signed: positive = looser (fewer sts) than base
    hint: str                   # localised gauge-adjustment hint or empty


def _round_quarter(mm: float) -> float:
    """Round a needle/hook size to the nearest 0.25 mm step."""
    return round(mm * 4) / 4


def _suggest_needle(base: Yarn, alt: Yarn, *, domain: str = "knit") -> float:
    """Suggest a needle/hook size for ``alt`` to match ``base``'s gauge.

    Heuristic: if alt has fewer typical sts/10cm than base (looser), the
    knitter should compensate by using a smaller needle to tighten the
    fabric. We scale the recommended needle by ``base_sts / alt_sts``
    (ratio of densities), clamped to a reasonable range.
    """
    if domain == "crochet":
        base_size = alt.recommended_hook_mm
    else:
        base_size = alt.recommended_needle_mm
    if alt.typical_gauge_sts_per_10cm <= 0 or base.typical_gauge_sts_per_10cm <= 0:
        return base_size
    ratio = alt.typical_gauge_sts_per_10cm / base.typical_gauge_sts_per_10cm
    # ratio > 1 → alt knits tighter than base → compensate with bigger needle
    suggested = base_size * ratio
    suggested = max(2.0, min(suggested, 12.0))
    return _round_quarter(suggested)


def build_alternatives(yarn_name: str, *, lang: str = "da",
                       domain: str = "knit", limit: int = 5
                       ) -> list[YarnAlternative]:
    """Return up to ``limit`` substitute records for ``yarn_name``.

    If the yarn is unknown returns an empty list.
    """
    base = lookup_yarn(yarn_name)
    if base is None:
        return []
    pool: list[Yarn] = list(suggest_substitute(base))
    pool.sort(key=lambda y: (y.name,))  # deterministic
    out: list[YarnAlternative] = []
    base_sts = base.typical_gauge_sts_per_10cm
    for alt in pool[:limit]:
        if base_sts <= 0:
            diff_pct = 0.0
        else:
            diff_pct = (alt.typical_gauge_sts_per_10cm - base_sts) / base_sts * 100.0
        diff_pct_rounded = round(diff_pct, 1)
        hint = ""
        if abs(diff_pct_rounded) < 1.0:
            hint = t("yarn_alt.gauge_match", lang)
        else:
            suggested_needle = _suggest_needle(base, alt, domain=domain)
            # Format needle without trailing zeros where unnecessary
            needle_str = (f"{suggested_needle:.2f}".rstrip("0").rstrip("."))
            if diff_pct_rounded < 0:
                # alt has fewer sts → looser → diff is "higher gauge"
                # i.e. fewer sts/10cm than base. Use translation key
                # gauge_diff_higher (which translates to "fewer sts" in DA).
                hint = t("yarn_alt.gauge_diff_higher", lang,
                         diff_pct=abs(diff_pct_rounded), hint_needle=needle_str)
            else:
                hint = t("yarn_alt.gauge_diff_lower", lang,
                         diff_pct=abs(diff_pct_rounded), hint_needle=needle_str)
        out.append(YarnAlternative(
            name=alt.name,
            weight_class=alt.weight_class,
            fiber=alt.fiber,
            meters_per_50g=alt.meters_per_50g,
            needle_mm=alt.recommended_needle_mm,
            hook_mm=alt.recommended_hook_mm,
            sts_per_10cm=alt.typical_gauge_sts_per_10cm,
            rows_per_10cm=alt.typical_gauge_rows_per_10cm,
            gauge_diff_pct=diff_pct_rounded,
            hint=hint,
        ))
    return out


def attach_alternatives(pattern: Pattern, yarn_name: str, *, lang: str = "da",
                        domain: str = "knit", limit: int = 5) -> int:
    """Compute alternatives and attach them to ``pattern.inputs``.

    Returns the count of alternatives stored. The CLI uses this to decide
    whether to print a "no alternatives — yarn unknown" hint.
    """
    alts = build_alternatives(yarn_name, lang=lang, domain=domain, limit=limit)
    if not alts:
        return 0
    pattern.inputs["yarn_alternatives"] = [asdict(a) for a in alts]
    pattern.inputs["yarn_alternatives_base"] = yarn_name
    return len(alts)


# ---------------------------------------------------------------------------
# Markdown + HTML renderers
# ---------------------------------------------------------------------------


def render_markdown(pattern: Pattern, lang: str = "da") -> str:
    """Return a ``## Garn-alternativer`` block, or empty string."""
    raw = (pattern.inputs or {}).get("yarn_alternatives") or []
    if not raw:
        return ""
    base_name = (pattern.inputs or {}).get("yarn_alternatives_base", "")
    weight_class = raw[0]["weight_class"]
    heading = t("yarn_alt.heading", lang)
    intro = t("yarn_alt.intro", lang, yarn=base_name, weight_class=weight_class)
    needle_label = t("yarn_alt.needle", lang)
    fiber_label = t("yarn_alt.fiber", lang)
    run_label = t("yarn_alt.run", lang)
    lines = [f"## {heading}", "", intro, ""]
    for a in raw:
        lines.append(f"- **{a['name']}** — {fiber_label}: {a['fiber']}; "
                     f"{run_label}: {a['meters_per_50g']} m / 50 g; "
                     f"{needle_label}: {a['needle_mm']:.1f} mm. "
                     f"_{a['hint']}_")
    lines.append("")
    return "\n".join(lines)


def render_html_aside(pattern: Pattern, lang: str = "da", *, domain: str = "knit") -> str:
    """Return the ``<aside class="yarn-alternatives">`` block, or empty."""
    raw = (pattern.inputs or {}).get("yarn_alternatives") or []
    if not raw:
        return ""
    base_name = (pattern.inputs or {}).get("yarn_alternatives_base", "")
    weight_class = raw[0]["weight_class"]
    heading = _htmllib.escape(t("yarn_alt.heading", lang))
    intro = _htmllib.escape(t("yarn_alt.intro", lang, yarn=base_name,
                               weight_class=weight_class))
    needle_label = _htmllib.escape(
        t("yarn_alt.hook" if domain == "crochet" else "yarn_alt.needle", lang))
    fiber_label = _htmllib.escape(t("yarn_alt.fiber", lang))
    run_label = _htmllib.escape(t("yarn_alt.run", lang))
    items: list[str] = []
    for a in raw:
        size_mm = a["hook_mm"] if domain == "crochet" else a["needle_mm"]
        items.append(
            "<li>"
            f"<strong>{_htmllib.escape(a['name'])}</strong>"
            f" <span class='yarn-alt-meta'>"
            f"({fiber_label}: {_htmllib.escape(a['fiber'])};"
            f" {run_label}: {a['meters_per_50g']} m / 50 g;"
            f" {needle_label}: {size_mm:.1f} mm)</span>"
            f"<br><em class='yarn-alt-hint'>{_htmllib.escape(a['hint'])}</em>"
            "</li>"
        )
    return (
        f'<aside class="yarn-alternatives">\n'
        f'  <h3>{heading}</h3>\n'
        f'  <p class="yarn-alt-intro">{intro}</p>\n'
        f'  <ul class="yarn-alt-list">\n'
        f'    {chr(10).join(items)}\n'
        f'  </ul>\n'
        f'</aside>'
    )


def alternatives_set(pattern: Pattern) -> bool:
    """True if ``--substitut`` produced data on this pattern."""
    return bool((pattern.inputs or {}).get("yarn_alternatives"))
