"""Core rendering logic for the prose intro generator.

Picks one fragment per slot from the per-construction library, fills
placeholders with facts, prunes empty paragraphs, and (for HTML) wraps
the result in a styled ``<section class="prosa">``.
"""

from __future__ import annotations

import html as _htmllib
import random

from ..pattern import Pattern
from ._facts import _facts
from .fragments_da import FRAGMENTS_DA
from .fragments_en import FRAGMENTS_EN


_DA_YARN_ALT_NOTE = (
    "Hvis dit lokale garn er udsolgt, har vi tilføjet {n_alternatives} "
    "alternativer i samme vægtklasse — se boksen 'Garn-alternativer' nedenfor."
)
_EN_YARN_ALT_NOTE = (
    "If your preferred yarn is sold out we've added {n_alternatives} "
    "alternatives in the same weight class — see the 'Yarn alternatives' "
    "box below."
)


def _seed_for(p: Pattern) -> int:
    """Stable RNG seed from name + gauge so repeated runs yield same prose."""
    g = (p.inputs or {}).get("gauge", {}) or {}
    parts = (
        p.name or "",
        p.construction or "",
        str(int(g.get("sts_per_10cm", 0))),
        str(int(g.get("rows_per_10cm", 0))),
    )
    s = "|".join(parts)
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return h or 1


def _select(rng: random.Random, fragments: dict, group: str,
            slot: str, default_group: dict) -> str | None:
    """Pick a template from group → slot, else from default_group → slot."""
    pool = (fragments.get(group) or {}).get(slot)
    if not pool:
        pool = (default_group or {}).get(slot)
    if not pool:
        return None
    return rng.choice(list(pool))


def _yarn_alt_fragment(pattern: Pattern, lang: str) -> str | None:
    """Optional sentence that references attached yarn alternatives.

    Returns ``None`` if no alternatives are present so the caller can skip
    appending the fragment.
    """
    alts = (pattern.inputs or {}).get("yarn_alternatives") or []
    if not alts:
        return None
    template = _EN_YARN_ALT_NOTE if lang == "en" else _DA_YARN_ALT_NOTE
    return template.format(n_alternatives=len(alts))


def _clean(s: str) -> str:
    # Collapse leftover whitespace from format(); also strip orphan-em-dash
    # sequences that come from unfilled facts (e.g. "med — cm ease").
    while "  " in s:
        s = s.replace("  ", " ")
    return s.strip()


def _is_blank(s: str) -> bool:
    plain = s.replace("—", "").replace("-", "").strip()
    return not plain


def intro_paragraphs(pattern: Pattern, lang: str = "da") -> list[str]:
    """Return 2–3 paragraphs of "about this pattern" prose.

    Deterministic for a given (name, construction, gauge): same input
    → same output. The output mixes a per-construction intro fragment,
    a size/gauge fact, an optional yarn-yardage estimate, a difficulty
    note and a closing sentence. Empty placeholders ("—") are pruned out
    of the rendered string so we don't show "raglan med — cm ease".
    """
    fragments = FRAGMENTS_DA if lang != "en" else FRAGMENTS_EN
    default_group = fragments.get("_default", {})
    group = pattern.construction
    facts = _facts(pattern, lang)

    rng = random.Random(_seed_for(pattern))

    para1_parts: list[str] = []
    intro = _select(rng, fragments, group, "intro", default_group)
    if intro:
        para1_parts.append(intro.format(**facts))
    size = _select(rng, fragments, group, "size", default_group)
    if size:
        para1_parts.append(size.format(**facts))

    para2_parts: list[str] = []
    yarn = _select(rng, fragments, group, "yarn", default_group)
    if yarn:
        para2_parts.append(yarn.format(**facts))
    yarn_alt_note = _yarn_alt_fragment(pattern, lang)
    if yarn_alt_note:
        para2_parts.append(yarn_alt_note)
    diff = _select(rng, fragments, group, "difficulty", default_group)
    if diff:
        para2_parts.append(diff.format(**facts))

    para3_parts: list[str] = []
    closing = _select(rng, fragments, group, "closing", default_group)
    if closing:
        para3_parts.append(closing.format(**facts))

    paragraphs = [" ".join(parts).strip() for parts in
                  (para1_parts, para2_parts, para3_parts) if parts]
    # Filter out paragraphs that are essentially empty (e.g. all em-dashes).
    paragraphs = [_clean(p) for p in paragraphs if p]
    paragraphs = [p for p in paragraphs if p and not _is_blank(p)]
    return paragraphs[:3]


def format_intro_html(pattern: Pattern, lang: str = "da") -> str:
    """Wrap :func:`intro_paragraphs` in a styled ``<section class="prosa">``.

    Empty input (no paragraphs returned) produces an empty string so the
    template-slot collapses gracefully.
    """
    paragraphs = intro_paragraphs(pattern, lang)
    if not paragraphs:
        return ""
    body = "\n".join(
        f"  <p>{_htmllib.escape(p)}</p>" for p in paragraphs
    )
    label = "Om opskriften" if lang != "en" else "About this pattern"
    return (
        f'<section class="prosa">\n'
        f'  <h2 class="prosa-heading">{_htmllib.escape(label)}</h2>\n'
        f'{body}\n'
        f'</section>'
    )
