"""Template-based prose intro generator.

Given a :class:`Pattern`, produces 2–3 paragraphs of "about this pattern"
prose by Mad-Libs-style filling fragments from a per-construction
sentence library. No API calls, no LLM — pure templating with deterministic
RNG seeded on the pattern name + gauge.

This package is split into focused modules:

* :mod:`._facts` — fact-extraction helper used to fill template fields.
* :mod:`.fragments_da` / :mod:`.fragments_en` — per-construction sentence
  fragment dictionaries keyed by language.
* :mod:`._render` — renders paragraphs and HTML from facts + fragments.

Public API (re-exported here so existing imports keep working):

    intro_paragraphs(pattern, lang="da") -> list[str]
    format_intro_html(pattern, lang="da") -> str
"""

from __future__ import annotations

from ._render import intro_paragraphs, format_intro_html

__all__ = ["intro_paragraphs", "format_intro_html"]
