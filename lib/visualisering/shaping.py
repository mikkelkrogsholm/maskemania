"""Shaping algorithms — even distribution.

The single most useful algorithm: distribute N events across M slots as
evenly as possible. Used for:
  - placing K decreases evenly across a row of N stitches
  - placing K shaping rounds evenly across M plain rounds
  - distributing increases on a sleeve over its length

Naive division (M // N) leaves a clump at the end. The algorithm below is
Bresenham's line algorithm adapted for knitting — same one used in graphics
to draw a line on integer pixels.
"""

from __future__ import annotations


def evenly_spaced(events: int, slots: int) -> list[int]:
    """Pick `events` slot indices out of range(slots), as evenly spread as possible.

    Returns a sorted list of 0-based indices. The first index is always 0 if
    events > 0 (i.e. the first event happens at the start). For knitting,
    callers usually want 1-based positions and may want to shift the offset.

    Example: evenly_spaced(4, 12) → [0, 3, 6, 9]
             evenly_spaced(5, 12) → [0, 2, 5, 7, 10]
             evenly_spaced(3, 10) → [0, 3, 7]
    """
    if events < 0 or slots < 0:
        raise ValueError("events and slots must be non-negative")
    if events == 0:
        return []
    if events > slots:
        raise ValueError(f"can't fit {events} events into {slots} slots")
    # Bresenham: pick i such that round(i * slots / events) for i in 0..events-1
    out: list[int] = []
    for i in range(events):
        idx = (i * slots) // events
        out.append(idx)
    return out


def distribute_decreases(decreases: int, total_sts: int,
                         *, edge_sts: int = 0) -> list[int]:
    """Distribute `decreases` k2tog operations across a row of `total_sts`
    stitches, returning the list of segment lengths between/around the
    decreases.

    Result format: [k_a, dec, k_b, dec, ..., k_z]
      The k_* values are the count of plain stitches in each segment.
      sum(k_*) + 2*decreases == total_sts (each k2tog consumes 2 sts).
      len(result) == 2*decreases + 1.

    edge_sts: stitches to keep plain at each edge before splitting. Useful
    for flat pieces where you want the decrease away from the selvedge.

    Example: distribute_decreases(4, 60) → [7, dec, 13, dec, 13, dec, 13, dec, 7]
             (60 - 8 = 52 plain sts split as evenly as possible across 5 gaps:
              one extra goes to the two end gaps for symmetry.)
    """
    if decreases < 0:
        raise ValueError("decreases must be >= 0")
    if decreases == 0:
        return [total_sts]
    plain_total = total_sts - 2 * decreases - 2 * edge_sts
    if plain_total < 0:
        raise ValueError(
            f"can't fit {decreases} decreases (using {2*decreases} sts) plus "
            f"{2*edge_sts} edge sts in row of {total_sts}"
        )
    gaps = decreases + 1  # plain segments between/around decs
    base = plain_total // gaps
    remainder = plain_total % gaps
    # Spread remainder symmetrically: prefer giving extras to outer gaps first.
    sizes = [base] * gaps
    # Pair-from-outside: 0, last, 1, last-1, ...
    order = []
    lo, hi = 0, gaps - 1
    while lo <= hi:
        if lo == hi:
            order.append(lo)
        else:
            order.extend([lo, hi])
        lo += 1; hi -= 1
    for i in range(remainder):
        sizes[order[i]] += 1
    # Build result list interleaving sizes and decreases (-1 sentinel for "dec")
    result: list[int] = []
    if edge_sts:
        result.append(edge_sts)
    for i, sz in enumerate(sizes):
        result.append(sz)
        if i < gaps - 1:
            result.append(-1)  # dec marker
    if edge_sts:
        result.append(edge_sts)
    return result


def format_decrease_row(segments: list[int], dec_name: str = "k2tog",
                        plain_name: str = "k") -> str:
    """Pretty-print a distribute_decreases result.

    Example: [7, -1, 13, -1, 13, -1, 13, -1, 7] →
             "k7, k2tog, k13, k2tog, k13, k2tog, k13, k2tog, k7"
    """
    parts: list[str] = []
    for s in segments:
        if s == -1:
            parts.append(dec_name)
        elif s > 0:
            parts.append(f"{plain_name}{s}")
    return ", ".join(parts)


def crown_decrease_plan(start_sts: int, sectors: int = 8,
                        min_finish_sts: int = 8) -> list[tuple[int, int, str]]:
    """Plan a beanie crown.

    Returns a list of (round_number, sts_after, instruction) tuples covering
    the entire crown until <= min_finish_sts remain.

    Pattern: alternate "decrease round" (one k2tog per sector) with "plain
    round". When sts per sector reaches ~2, drop the plain rounds and decrease
    every round until done.
    """
    if start_sts % sectors != 0:
        raise ValueError(
            f"start_sts ({start_sts}) must be divisible by sectors ({sectors})"
        )
    if start_sts <= sectors:
        raise ValueError(
            f"start_sts ({start_sts}) <= sectors ({sectors}); no decreases possible"
        )
    sts = start_sts
    per_sector = sts // sectors
    plan: list[tuple[int, int, str]] = []
    rnd = 0

    # Phase 1: dec round + plain round, until per_sector hits ~3
    while per_sector > 3:
        rnd += 1
        sts -= sectors
        per_sector = sts // sectors
        plan.append((
            rnd, sts,
            f"*strik {per_sector} m, k2tog* gentag {sectors} gange",
        ))
        if per_sector > 2:
            rnd += 1
            plan.append((rnd, sts, "strik 1 omg ret"))

    # Phase 2: dec every round until min_finish_sts
    while sts > min_finish_sts and sts > sectors:
        rnd += 1
        sts -= sectors
        per_sector = max(sts // sectors, 0)
        if per_sector >= 1:
            plan.append((
                rnd, sts,
                f"*strik {per_sector} m, k2tog* gentag {sectors} gange",
            ))
        else:
            plan.append((
                rnd, sts,
                f"*k2tog* gentag {sectors} gange",
            ))

    # Edge case: start_sts == 2*sectors → Phase 1 skipped, Phase 2 makes
    # one round of "k2tog" reducing to sectors, then loop exits. Plan is
    # correct (single round). No special handling needed.
    return plan
