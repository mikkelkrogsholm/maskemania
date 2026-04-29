"""Stitch bookkeeping — the validator that catches LLM-style errors.

Every textile operation has an integer (consumed, produced) pair. A row
or round is valid iff sum(consumed) == sts_at_start_of_row and
sum(produced) == sts_at_end_of_row. If those don't agree, the pattern is
broken — full stop, no excuses.

This module is **domain-agnostic**. It defines the `Stitch`, `Op`, `Row`
and `RowValidator` primitives but ships no concrete stitch dictionary.
Concrete stitches (k, p, k2tog… for knit; ch, sc, dc… for crochet) live
in the per-skill `stitches.py` modules together with a domain-specific
`Row` subclass that adds convenience helpers.
"""

from __future__ import annotations
from dataclasses import dataclass, field


class ValidationError(ValueError):
    """Raised when a row's stitch count doesn't balance."""


@dataclass(frozen=True)
class Stitch:
    """A single stitch operation.

    name:     short code, e.g. "k", "p", "k2tog", "yo", "kfb", "ssk", "sl1"
    consumes: stitches taken from the left needle / previous round
    produces: stitches placed on the right needle / current round
    """
    name: str
    consumes: int
    produces: int

    @property
    def delta(self) -> int:
        return self.produces - self.consumes


@dataclass
class Op:
    """An operation: a stitch repeated `count` times."""
    stitch: Stitch
    count: int = 1

    @property
    def consumes(self) -> int:
        return self.stitch.consumes * self.count

    @property
    def produces(self) -> int:
        return self.stitch.produces * self.count


@dataclass
class Row:
    """A row or round.

    sts_before: stitch count at start of the row
    ops:        sequence of operations
    label:      free-form description, e.g. "Indtagningsomg 3"

    This is the abstract / domain-agnostic version: it has no .k() / .p() /
    .op() helpers because there's no built-in stitch lookup. Domain-specific
    subclasses (e.g. `KnitRow`) add those convenience methods on top.
    """
    sts_before: int
    ops: list[Op] = field(default_factory=list)
    label: str = ""

    def add_op(self, stitch: Stitch, n: int = 1) -> "Row":
        """Append a stitch op. Returns self for chaining."""
        self.ops.append(Op(stitch, n))
        return self

    @property
    def consumed(self) -> int:
        return sum(o.consumes for o in self.ops)

    @property
    def produced(self) -> int:
        return sum(o.produces for o in self.ops)

    @property
    def sts_after(self) -> int:
        return self.sts_before + (self.produced - self.consumed)

    def validate(self) -> None:
        if self.consumed != self.sts_before:
            raise ValidationError(
                f"row '{self.label}' consumes {self.consumed} sts but starts with "
                f"{self.sts_before}. Diff = {self.consumed - self.sts_before}."
            )


@dataclass
class RowValidator:
    """Run a sequence of rows, threading stitch count through them.

    Use this on every construction. If any row fails to balance, the whole
    pattern is rejected — never fall back to "close enough".
    """
    rows: list[Row] = field(default_factory=list)

    def add(self, row: Row) -> Row:
        row.validate()
        self.rows.append(row)
        return row

    @property
    def final_sts(self) -> int:
        return self.rows[-1].sts_after if self.rows else 0

    def report(self) -> str:
        lines = ["row | label | start | consumed | produced | end"]
        lines.append("----|-------|-------|----------|----------|-----")
        for i, r in enumerate(self.rows, 1):
            lines.append(
                f"{i:>3} | {r.label[:30]:<30} | {r.sts_before:>5} | "
                f"{r.consumed:>8} | {r.produced:>8} | {r.sts_after:>5}"
            )
        return "\n".join(lines)


def validate_repeat(repeat_consumes: int, repeat_produces: int,
                    total_sts: int, *, label: str = "") -> int:
    """Validate that a stitch-pattern repeat divides into the total stitch count.

    Returns the number of repeats. Raises if total_sts is not a multiple of
    the pattern repeat width (consumes), or if multiplying out doesn't match.
    """
    if total_sts % repeat_consumes != 0:
        raise ValidationError(
            f"pattern '{label}' has repeat width {repeat_consumes} but row has "
            f"{total_sts} sts. Off by {total_sts % repeat_consumes}."
        )
    return total_sts // repeat_consumes
