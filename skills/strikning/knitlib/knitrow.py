"""Knit-specific Row subclass.

Adds the convenient `.k()` / `.p()` / `.op(name, n)` helpers that look
stitches up in the knit-only `STITCHES` dictionary. The generic `Row`
class in `lib/visualisering` is dictionary-agnostic and exposes only
`add_op(stitch, n)`.
"""

from __future__ import annotations

from lib.visualisering.bookkeeping import Row
from .stitches import stitch


class KnitRow(Row):
    """A `Row` with `.k()`, `.p()` and `.op(name, n)` helpers."""

    def k(self, n: int = 1) -> "KnitRow":
        self.ops.append(self._op_for("k", n))
        return self

    def p(self, n: int = 1) -> "KnitRow":
        self.ops.append(self._op_for("p", n))
        return self

    def op(self, name: str, n: int = 1) -> "KnitRow":
        self.ops.append(self._op_for(name, n))
        return self

    @staticmethod
    def _op_for(name: str, n: int):
        from lib.visualisering.bookkeeping import Op
        return Op(stitch(name), n)
