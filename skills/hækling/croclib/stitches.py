"""Crochet-specific stitch dictionary.

The generic `Stitch` class lives in `lib/visualisering/bookkeeping.py`. This
module defines the concrete crochet stitches (US convention: sc / hdc / dc /
tr) plus a `CroStitch` subclass that adds two crochet-specific fields:

- ``works_into``: where the stitch is anchored — ``"stitch"`` (default),
  ``"ch_sp"`` (chain-space), ``"mr"`` (magic ring), ``"starting_ch"``.
- ``creates_ch_sp``: number of trailing chains that count as a usable chain
  space for the next round (e.g. corner clusters in a granny square).

These extra fields are pure metadata — the (consumes, produces) bookkeeping
in :class:`lib.visualisering.bookkeeping.RowValidator` keeps working
unchanged because ``CroStitch`` is a drop-in subclass of ``Stitch``.

Convention: **US terminology** throughout. UK and Danish aliases are mapped
in :data:`ALIASES` and exposed through :func:`stitch`.

Reference: Agent B's research report,
``PLAN-research/fase-1-agent-b-haekling.md`` §1 (stitch dictionary).
"""

from __future__ import annotations

from dataclasses import dataclass

from lib.visualisering.bookkeeping import Stitch


@dataclass(frozen=True)
class CroStitch(Stitch):
    """A crochet stitch with extra (works_into, creates_ch_sp) metadata.

    Subclass of the generic :class:`Stitch`, so the bookkeeping in
    :class:`Row`/:class:`RowValidator` keeps working unchanged. The new
    fields are pure metadata — useful for SVG rendering and for higher-level
    pattern-DSL helpers, but they don't affect (consumes, produces) math.
    """

    works_into: str = "stitch"     # "stitch" | "ch_sp" | "mr" | "starting_ch"
    creates_ch_sp: int = 0         # trailing chain-count that forms a ch-sp
    yarn_overs: int = 0            # 0 = sc, 1 = hdc/dc, 2 = tr, 3 = dtr
    counts_as_stitch: bool = True  # False for ch / sl st in the working row


# ---------------------------------------------------------------------------
# US-canonical stitch dictionary
# ---------------------------------------------------------------------------
#
# Modelling notes (see Agent B §1):
#
# * ``ch`` (chain) is modelled as ``(consumes=0, produces=1)`` so that a
#   foundation chain validates cleanly: starting from 0 sts, ``Row(0).ch(20)``
#   produces 20 sts. Turning chains *do not* normally count as the first
#   stitch (US sc convention) — the constructions handle that explicitly by
#   adding a separate ``ch`` op that is *not* counted into the row's
#   ``produces`` for the sake of the next-row stitch count. (We document this
#   choice rather than making it implicit.)
#
# * ``sl_st`` (slip stitch / kædemaske) consumes 1 stitch but produces 0
#   stitches in the next row — it's only used for joining or moving.
#
# * ``magic_ring`` is the crochet analogue of ``cast_on``: it produces N
#   stitches without consuming anything. A construction creates a custom
#   stitch with ``produces=N`` (typically 6 for amigurumi) — see
#   :func:`magic_ring`.
STITCHES: dict[str, CroStitch] = {
    # Foundation / structural
    "ch": CroStitch(
        "ch", consumes=0, produces=1,
        works_into="starting_ch", counts_as_stitch=False,
    ),
    "sl_st": CroStitch(
        "sl_st", consumes=1, produces=0,
        works_into="stitch", counts_as_stitch=False,
    ),
    # Basic stitches
    "sc": CroStitch(
        "sc", consumes=1, produces=1,
        works_into="stitch", yarn_overs=0,
    ),
    "hdc": CroStitch(
        "hdc", consumes=1, produces=1,
        works_into="stitch", yarn_overs=1,
    ),
    "dc": CroStitch(
        "dc", consumes=1, produces=1,
        works_into="stitch", yarn_overs=1,
    ),
    "tr": CroStitch(
        "tr", consumes=1, produces=1,
        works_into="stitch", yarn_overs=2,
    ),
    "dtr": CroStitch(
        "dtr", consumes=1, produces=1,
        works_into="stitch", yarn_overs=3,
    ),
    # Increases
    "sc_inc": CroStitch(
        "sc_inc", consumes=1, produces=2,
        works_into="stitch", yarn_overs=0,
    ),
    "dc_inc": CroStitch(
        "dc_inc", consumes=1, produces=2,
        works_into="stitch", yarn_overs=1,
    ),
    # Decreases
    "sc2tog": CroStitch(
        "sc2tog", consumes=2, produces=1,
        works_into="stitch", yarn_overs=0,
    ),
    "hdc2tog": CroStitch(
        "hdc2tog", consumes=2, produces=1,
        works_into="stitch", yarn_overs=1,
    ),
    "dc2tog": CroStitch(
        "dc2tog", consumes=2, produces=1,
        works_into="stitch", yarn_overs=1,
    ),
    # Decorative / texture stitches
    #
    # ``popcorn`` (popkorn): typically 5 dc worked into the same stitch,
    # then dropped and pulled through to form a "puff". The cluster lands
    # back in a single stitch on the next round, so (consumes=1, produces=1)
    # in the bookkeeping sense — the texture is metadata.
    "pop": CroStitch(
        "pop", consumes=1, produces=1,
        works_into="stitch", yarn_overs=1, counts_as_stitch=True,
    ),
    # ``picot``: ch 3 + sl st back into the first ch — a tiny decorative
    # bump. Doesn't consume any stitch from the previous round and doesn't
    # leave a usable stitch in the working row, so (0, 0). Used purely for
    # edge decoration.
    "pic": CroStitch(
        "pic", consumes=0, produces=0,
        works_into="stitch", yarn_overs=0, counts_as_stitch=False,
    ),
    # ``cl3`` / 3-dc cluster: 3 dc joined at the top — counts as 1 stitch
    # in the next round but consumes 1 stitch from the previous round (when
    # worked into a single anchor; granny-square-style 3-dc-into-ch-sp is
    # different and is modelled at the section level, not per-stitch).
    "cl3": CroStitch(
        "cl3", consumes=1, produces=1,
        works_into="stitch", yarn_overs=1, counts_as_stitch=True,
    ),
}


# ---------------------------------------------------------------------------
# Aliases — US (canonical), UK, Danish
# ---------------------------------------------------------------------------
#
# Reference: Agent B's research §7. Note the classic US/UK collision: UK ``dc``
# is US ``sc``, UK ``tr`` is US ``dc``, etc. We always normalise to US.
ALIASES: dict[str, str] = {
    # US canonical → US canonical (identity)
    "ch": "ch",
    "sl_st": "sl_st", "slst": "sl_st", "sl-st": "sl_st",
    "sc": "sc",
    "hdc": "hdc",
    "dc": "dc",
    "tr": "tr",
    "dtr": "dtr",
    "sc_inc": "sc_inc", "inc": "sc_inc",
    "dc_inc": "dc_inc",
    "sc2tog": "sc2tog", "dec": "sc2tog",
    "hdc2tog": "hdc2tog",
    "dc2tog": "dc2tog",
    "pop": "pop", "popcorn": "pop",
    "pic": "pic", "picot": "pic",
    "cl3": "cl3", "cluster": "cl3", "3dc_cluster": "cl3",

    # UK aliases
    "uk_dc": "sc",   # UK double crochet = US single crochet
    "uk_htr": "hdc",
    "uk_tr": "dc",
    "uk_dtr": "tr",
    "uk_trtr": "dtr",

    # Danish aliases (rito.dk / haekleskolen.dk)
    "lm": "ch",       # luftmaske
    "km": "sl_st",    # kædemaske
    "fm": "sc",       # fastmaske
    "hstm": "hdc",    # halvstangmaske
    "stm": "dc",      # stangmaske
    "dst": "tr",      # dobbeltstangmaske
    "dbstm": "tr",    # dobbeltstangmaske, alternate spelling
    "tdst": "dtr",    # tredobbeltstangmaske
    "udt": "sc_inc",  # udtagning (single crochet increase)
    "indt": "sc2tog", # indtagning
    "2_fm_sm": "sc2tog",
    "2_stm_sm": "dc2tog",
    "popkorn": "pop",   # danish for popcorn
    "puf": "pop",       # nogle danske mønstre kalder den puf-maske
    "picotmaske": "pic",
    "klynge": "cl3",    # dansk klynge = cluster
}


def stitch(name: str) -> CroStitch:
    """Look up a crochet stitch by code, US/UK/Danish.

    Lookup is case-insensitive. ``-`` and spaces are normalised to ``_``.
    Use US convention for new code; aliases exist for legacy / Danish input.
    """
    key = name.lower().strip().replace(" ", "_").replace("-", "_")
    canonical = ALIASES.get(key, key)
    if canonical not in STITCHES:
        raise KeyError(
            f"unknown crochet stitch '{name}'. Known stitches: "
            f"{sorted(STITCHES)}. Known aliases: {sorted(ALIASES)}."
        )
    return STITCHES[canonical]


def magic_ring(n: int = 6) -> CroStitch:
    """Build an ad-hoc CroStitch representing a magic ring of N sc.

    The first round of an amigurumi piece typically starts with a magic ring
    holding N stitches. We model this as an "init" stitch with
    ``consumes=0, produces=n`` — analogous to ``cast_on`` in knit.
    """
    return CroStitch(
        f"mr{n}", consumes=0, produces=n,
        works_into="mr", yarn_overs=0, counts_as_stitch=True,
    )
