"""Yarn database — small lookup table for kendte garn-mærker.

Bruges af generatorerne (strik + hækl) til at fylde rimelige defaults ud
hvis brugeren har angivet ``--garn "Drops Air"`` men hverken ``--gauge``
eller ``--garnløbe``. Brugerens eksplicitte input vinder altid.

Værdier er typiske/anbefalede pr. label-bånd og garn-producenters
hjemmesider — de er udgangspunkt, ikke garantier. En prøvelap er stadig
nødvendig.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .pattern import Pattern

# Yarn weight classification (roughly the CYC/Standard Yarn Weight categories,
# extended with the European "DK"/"sport"/"aran" labels everyone uses in
# practice). The strings are stable IDs; localized labels live in
# translations.py if/when needed.
_VALID_WEIGHTS = {
    "lace", "fingering", "sport", "DK", "worsted", "aran",
    "chunky", "super-chunky",
}


@dataclass(frozen=True)
class Yarn:
    """En garn-record.

    Bemærk: ``typical_gauge_sts_per_10cm`` og ``rows_per_10cm`` er hvad
    bånd-gauge typisk siger på den anbefalede pind/nål — målt i glatstrik
    eller fm. Hækle-gauge er ofte 1–2 m mindre pr. 10 cm i fm.
    """
    name: str
    weight_class: str
    typical_gauge_sts_per_10cm: int       # knit gauge in stockinette
    typical_gauge_rows_per_10cm: int
    recommended_needle_mm: float
    recommended_hook_mm: float
    fiber: str
    meters_per_50g: int
    country: str = ""

    def __post_init__(self) -> None:
        if self.weight_class not in _VALID_WEIGHTS:
            raise ValueError(
                f"weight_class must be one of {sorted(_VALID_WEIGHTS)} "
                f"(got {self.weight_class!r} for {self.name!r})"
            )


def _y(*args, **kw) -> Yarn:  # tiny helper — keeps the table compact
    return Yarn(*args, **kw)


# A small but useful set: a mix of mainstream Scandinavian + international
# brands. Values are typical band-recommended numbers. Cross-reference
# yarn labels for a precise project — these are the AI's "best guess" for
# auto-fill.
YARNS: dict[str, Yarn] = {
    # ----- Drops -----
    "Drops Lima":            _y("Drops Lima", "DK", 21, 28, 4.0, 4.0,
                                "65% uld, 35% alpaca", 100, "DK"),
    "Drops Air":             _y("Drops Air", "aran", 17, 22, 5.5, 5.5,
                                "70% alpaca, 23% polyamid, 7% uld", 75, "DK"),
    "Drops Brushed Alpaca Silk": _y(
                                "Drops Brushed Alpaca Silk", "DK", 17, 23, 6.0, 6.0,
                                "77% alpaca, 23% silke", 140, "DK"),
    "Drops Alpaca":          _y("Drops Alpaca", "fingering", 23, 32, 3.5, 3.5,
                                "100% alpaca", 167, "DK"),
    "Drops Merino Extra Fine": _y("Drops Merino Extra Fine", "DK", 21, 28, 4.0, 4.0,
                                  "100% merinould", 105, "DK"),

    # ----- Sandnes -----
    "Sandnes Sunday":        _y("Sandnes Sunday", "fingering", 27, 36, 3.0, 3.0,
                                "100% merinould", 235, "NO"),
    "Sandnes Tynn Merinoull": _y("Sandnes Tynn Merinoull", "fingering",
                                 27, 36, 3.0, 3.0, "100% merinould", 175, "NO"),
    "Sandnes Tynn Line":     _y("Sandnes Tynn Line", "fingering", 26, 34, 3.0, 3.0,
                                "53% bomuld, 33% viskose, 14% hør", 220, "NO"),

    # ----- Önling / Knitting For Olive -----
    "Önling No 2":           _y("Önling No 2", "fingering", 27, 36, 3.0, 3.0,
                                "70% merinould, 30% akryl", 200, "DK"),
    "Knitting For Olive Merino": _y("Knitting For Olive Merino", "fingering",
                                    27, 36, 3.0, 3.0, "100% merinould", 250, "DK"),
    "Knitting For Olive Soft Silk Mohair": _y(
                                "Knitting For Olive Soft Silk Mohair", "lace",
                                30, 40, 3.5, 3.5, "70% mohair, 30% silke", 225, "DK"),

    # ----- Hobbii -----
    "Hobbii Friends":        _y("Hobbii Friends", "DK", 21, 28, 4.0, 4.0,
                                "50% bomuld, 50% akryl", 90, "DK"),
    "Hobbii Cotton 8/8":     _y("Hobbii Cotton 8/8", "DK", 22, 30, 4.0, 4.0,
                                "100% bomuld", 85, "DK"),

    # ----- International -----
    "Cascade 220":           _y("Cascade 220", "worsted", 18, 24, 4.5, 5.0,
                                "100% merinould", 100, "US"),
    "Rowan Felted Tweed":    _y("Rowan Felted Tweed", "DK", 23, 30, 3.75, 4.0,
                                "50% merinould, 25% alpaca, 25% viskose", 175, "UK"),

    # ----- Additional aran/worsted/lace candidates so weight-class
    # buckets are populated enough for substitution suggestions. -----
    "Drops Nepal":           _y("Drops Nepal", "aran", 17, 22, 5.0, 5.0,
                                "65% uld, 35% alpaca", 75, "DK"),
    "Drops Wish":            _y("Drops Wish", "aran", 16, 22, 5.5, 5.5,
                                "76% bomuld, 24% alpaca", 78, "DK"),
    "Hobbii Soft Like Cotton": _y("Hobbii Soft Like Cotton", "aran",
                                  16, 21, 5.5, 5.5,
                                  "100% akryl", 75, "DK"),
    "Sandnes Smart":         _y("Sandnes Smart", "aran", 18, 24, 5.0, 5.0,
                                "100% uld", 100, "NO"),
    "Cascade Eco+":           _y("Cascade Eco+", "worsted", 18, 24, 5.0, 5.0,
                                "100% merinould", 200, "US"),
    "Drops Sky":             _y("Drops Sky", "worsted", 19, 26, 5.0, 5.0,
                                "62% babyalpaca, 38% merinould", 190, "DK"),
    "Drops Lace":            _y("Drops Lace", "lace", 29, 38, 3.5, 3.5,
                                "70% babyalpaca, 30% silke", 400, "DK"),
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def _norm(name: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation that's just noise."""
    s = name.lower().strip()
    # collapse runs of whitespace
    parts = s.split()
    s = " ".join(parts)
    # drop hyphens / dots / commas — "drops-lima" should match "Drops Lima"
    for ch in ("-", ".", ",", "_"):
        s = s.replace(ch, " ")
    s = " ".join(s.split())
    return s


def lookup_yarn(name: str) -> Yarn | None:
    """Find a yarn by name (case-/whitespace-insensitive, with light fuzz).

    Strategy:
    1. Exact (normalized) match on the canonical name.
    2. Substring match where the query is contained in a canonical name
       (so "drops air" matches but also "air" matches "Drops Air").
    3. Substring match where the canonical name is contained in the query
       (so "Drops Air 50g" matches "Drops Air").
    """
    if not name:
        return None
    qn = _norm(name)
    by_norm = {_norm(k): v for k, v in YARNS.items()}
    # 1. exact
    if qn in by_norm:
        return by_norm[qn]
    # 2. query ⊂ canonical
    for cn, yarn in by_norm.items():
        if qn in cn:
            return yarn
    # 3. canonical ⊂ query
    best: Yarn | None = None
    best_len = 0
    for cn, yarn in by_norm.items():
        if cn in qn and len(cn) > best_len:
            best = yarn
            best_len = len(cn)
    return best


def suggest_substitute(yarn: Yarn) -> list[Yarn]:
    """Return all known yarns with the same weight_class (excluding ``yarn``).

    Caller can pick one based on fiber preference, country, etc.
    """
    return [
        y for y in YARNS.values()
        if y.weight_class == yarn.weight_class and y.name != yarn.name
    ]


def all_yarns() -> Iterable[Yarn]:
    """All known yarns — useful for tests, listings, autocomplete."""
    return YARNS.values()


# ---------------------------------------------------------------------------
# Auto-fill into a generator's runtime config
# ---------------------------------------------------------------------------

def apply_yarn_to_pattern(pattern: "Pattern", yarn_name: str) -> bool:
    """Stamp known yarn defaults onto a Pattern's metadata in-place.

    Returns True if the yarn was found, False otherwise.

    Sets metadata fields ``yarn`` and ``yarn_run`` (e.g. "167 m / 50 g")
    if they aren't already set. Does NOT overwrite existing user input.
    Does NOT touch ``inputs["gauge"]`` — auto-gauge belongs to the CLI
    layer (it has to convert to per-cm units that match the construction).
    """
    yarn = lookup_yarn(yarn_name)
    if yarn is None:
        return False
    md = pattern.inputs.setdefault("metadata", {})
    md.setdefault("yarn", f"{yarn.name} ({yarn.fiber})")
    md.setdefault("yarn_run", f"{yarn.meters_per_50g} m / 50 g")
    return True


def auto_gauge_from_yarn(yarn_name: str, *, domain: str = "knit"
                         ) -> tuple[float, float] | None:
    """Return ``(sts_per_cm, rows_per_cm)`` defaults for the yarn.

    For ``domain="crochet"`` the sts gauge is reduced ~15% from the knit-band
    gauge (typical fm-vs-glatstrik delta). The CLI uses these to fill in
    --gauge / --row-gauge when the user hasn't passed them. Returns None
    if the yarn is unknown.
    """
    yarn = lookup_yarn(yarn_name)
    if yarn is None:
        return None
    sts_per_10 = yarn.typical_gauge_sts_per_10cm
    rows_per_10 = yarn.typical_gauge_rows_per_10cm
    if domain == "crochet":
        sts_per_10 = sts_per_10 * 0.85
        rows_per_10 = rows_per_10 * 0.85
    return (sts_per_10 / 10.0, rows_per_10 / 10.0)


def auto_hook_or_needle(yarn_name: str, *, domain: str = "knit") -> str | None:
    """Return a printable string for hook/needle size (e.g. ``"4.0 mm"``)."""
    yarn = lookup_yarn(yarn_name)
    if yarn is None:
        return None
    if domain == "crochet":
        return f"{yarn.recommended_hook_mm:.1f} mm"
    return f"{yarn.recommended_needle_mm:.1f} mm"
