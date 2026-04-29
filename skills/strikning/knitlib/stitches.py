"""Knit-specific stitch dictionary.

The generic `Stitch` class lives in `lib/visualisering/bookkeeping.py`.
Here we register the concrete knitting stitches that knitlib uses.

Crochet has its own dictionary in `skills/hækling/croclib/stitches.py`.
"""

from __future__ import annotations

from lib.visualisering.bookkeeping import Stitch


# Standard knit-stitch dictionary. Add to this as patterns require.
STITCHES: dict[str, Stitch] = {
    "k":      Stitch("k",      1, 1),  # knit
    "p":      Stitch("p",      1, 1),  # purl
    "sl":     Stitch("sl",     1, 1),  # slip 1 (counts as consuming + producing)
    "yo":     Stitch("yo",     0, 1),  # yarn over
    "k2tog":  Stitch("k2tog",  2, 1),
    "p2tog":  Stitch("p2tog",  2, 1),
    "ssk":    Stitch("ssk",    2, 1),
    "ssp":    Stitch("ssp",    2, 1),
    "k3tog":  Stitch("k3tog",  3, 1),
    "sssk":   Stitch("sssk",   3, 1),
    "cdd":    Stitch("cdd",    3, 1),  # central double dec (sl2-k1-p2sso)
    "kfb":    Stitch("kfb",    1, 2),  # knit front and back
    "pfb":    Stitch("pfb",    1, 2),
    "m1l":    Stitch("m1l",    0, 1),  # make 1 left
    "m1r":    Stitch("m1r",    0, 1),  # make 1 right
    "m1":     Stitch("m1",     0, 1),
    # cables don't change count: e.g. C4F = 4 in, 4 out
    "c4f":    Stitch("c4f",    4, 4),
    "c4b":    Stitch("c4b",    4, 4),
    "c6f":    Stitch("c6f",    6, 6),
    "c6b":    Stitch("c6b",    6, 6),
}


def stitch(name: str) -> Stitch:
    """Look up a knit stitch by short code. Use lower-case names."""
    key = name.lower()
    if key not in STITCHES:
        raise KeyError(
            f"unknown stitch '{name}'. Add it to STITCHES with (consumes, produces)."
        )
    return STITCHES[key]
