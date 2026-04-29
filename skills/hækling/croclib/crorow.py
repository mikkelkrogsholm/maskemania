"""Crochet-specific Row subclass.

Adds convenient ``.ch()`` / ``.sc()`` / ``.dc()`` / ``.hdc()`` / ``.tr()``
helpers plus a generic ``.op(name, n)`` that looks stitches up in
:data:`croclib.stitches.STITCHES` (US convention, with UK/Danish aliases).

The generic :class:`Row` in ``lib.visualisering.bookkeeping`` is dictionary-
agnostic and exposes only ``add_op(stitch, n)``; this subclass wires the
crochet dictionary into the same shape that :class:`KnitRow` uses for knit.
"""

from __future__ import annotations

from lib.visualisering.bookkeeping import Op, Row
from .stitches import CroStitch, magic_ring, stitch


class CrochetRow(Row):
    """A :class:`Row` with crochet shorthand helpers."""

    # --- shorthand methods (US naming) ----------------------------------

    def ch(self, n: int = 1) -> "CrochetRow":
        """Append ``n`` chains."""
        return self.op("ch", n)

    def sl_st(self, n: int = 1) -> "CrochetRow":
        return self.op("sl_st", n)

    def sc(self, n: int = 1) -> "CrochetRow":
        return self.op("sc", n)

    def hdc(self, n: int = 1) -> "CrochetRow":
        return self.op("hdc", n)

    def dc(self, n: int = 1) -> "CrochetRow":
        return self.op("dc", n)

    def tr(self, n: int = 1) -> "CrochetRow":
        return self.op("tr", n)

    def sc_inc(self, n: int = 1) -> "CrochetRow":
        return self.op("sc_inc", n)

    def sc2tog(self, n: int = 1) -> "CrochetRow":
        return self.op("sc2tog", n)

    def dc2tog(self, n: int = 1) -> "CrochetRow":
        return self.op("dc2tog", n)

    # --- generic helpers -------------------------------------------------

    def op(self, name: str, n: int = 1) -> "CrochetRow":
        """Append ``n`` stitches of the named type."""
        self.ops.append(Op(stitch(name), n))
        return self

    def magic_ring(self, n: int = 6) -> "CrochetRow":
        """Append a magic-ring init stitch producing ``n`` sc."""
        self.ops.append(Op(magic_ring(n), 1))
        return self

    def add_stitch(self, s: CroStitch, n: int = 1) -> "CrochetRow":
        """Append a custom :class:`CroStitch` (e.g. corner cluster)."""
        self.ops.append(Op(s, n))
        return self
