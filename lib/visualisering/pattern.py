"""Pattern data classes — the structured intermediate form.

A Pattern is a list of Sections. Each Section has a title, an ordered list
of Steps, and stitch counts at start and end. Steps are short sentences in
language-agnostic form (we render them in Danish or English at the end).

This is the contract between the math layer and the prose layer. Never let
free-form text leak into the math layer — only structured Steps.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Step:
    """A single instruction step within a section.

    text:   short imperative sentence, may include a placeholder like {sts}
    sts_after: stitch count after this step (for validator + report)
    repeats: optional number of times this step is repeated
    note:    optional clarification (often becomes a parenthetical in prose)
    """
    text: str
    sts_after: int
    repeats: int = 1
    note: str = ""


@dataclass
class Section:
    title: str
    sts_before: int
    steps: list[Step] = field(default_factory=list)

    @property
    def sts_after(self) -> int:
        return self.steps[-1].sts_after if self.steps else self.sts_before

    def add(self, text: str, sts_after: int, *, repeats: int = 1,
            note: str = "") -> Step:
        s = Step(text=text, sts_after=sts_after, repeats=repeats, note=note)
        self.steps.append(s)
        return s


@dataclass
class Pattern:
    """The structured pattern. Pass this to a formatter to produce prose."""
    name: str
    construction: str          # "hue", "tørklæde", "raglan_topdown", ...
    inputs: dict[str, Any]     # echo of the spec: gauge, mål, ease, garn...
    sections: list[Section] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # Difficulty rating. One of: "beginner" / "easy" / "intermediate" /
    # "advanced" (en) — the renderer translates to localized labels via
    # the t("difficulty.<value>", lang) keys. Empty string means
    # "unknown / not yet rated" and the renderer omits the line.
    difficulty: str = ""

    def add_section(self, title: str, sts_before: int) -> Section:
        s = Section(title=title, sts_before=sts_before)
        self.sections.append(s)
        return s

    def validate_continuity(self) -> None:
        """Verify each section's sts_before matches the previous section's
        sts_after, except for the first."""
        prev_after: int | None = None
        for sec in self.sections:
            if prev_after is not None and sec.sts_before != prev_after:
                raise ValueError(
                    f"section '{sec.title}' starts with {sec.sts_before} sts "
                    f"but previous section ended with {prev_after}"
                )
            prev_after = sec.sts_after

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "construction": self.construction,
            "inputs": self.inputs,
            "sections": [
                {
                    "title": s.title,
                    "sts_before": s.sts_before,
                    "sts_after": s.sts_after,
                    "steps": [
                        {
                            "text": st.text,
                            "sts_after": st.sts_after,
                            "repeats": st.repeats,
                            "note": st.note,
                        }
                        for st in s.steps
                    ],
                }
                for s in self.sections
            ],
            "notes": self.notes,
            "warnings": self.warnings,
            "difficulty": self.difficulty,
        }
