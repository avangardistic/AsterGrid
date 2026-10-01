"""§7.1 grid geometry as a pure function (Phase 7g-1).

``compute_ladder_geometry`` returns the ladder prices for one group of one Cycle.
Pure, total, clock-free, Decimal-only. It takes every parameter as an argument —
config values NEVER flow into ``core/`` by import (geometry math is
config-source-agnostic; the OCaml reference model calls the same signature).

PINNED READINGS (Owner rulings; OCaml parity depends on them):

R1. CHAINED COMPOUNDING. "BU2 = BU1 + StepBps" / "Levels 2..N use normal StepBps
    spacing FROM THE PRECEDING LEVEL" (§7.1, §14 D-09 block; STR-0143/0145/0147)
    means each step is measured multiplicatively from the preceding level:
        BU: p_k = p_{k-1} * (1 + step_bps/10000)
        SL: p_k = p_{k-1} * (1 - step_bps/10000)
    NOT additive off the reference. The D-09 chained phrasing governs; L1 fixes
    the chain's START, not an additive anchor. (ref 100000, step 10, first 20 ->
    p1 = 100200, p2 = 100300.2 EXACTLY — never 100300.0.)

R2. SUCCESSOR RULE WINS FOR G1+ CONTINUATION CYCLES (specific-over-general).
    STR-0144's two lifetime statements ("Cycle 0 AND EVERY SUBSEQUENT Cycle ...
    persists for the Generation's LIFETIME ... NEVER recomputed per Cycle") govern
    over STR-0143's general continuation-cycle rule at G1+-C1+. So ``is_successor``
    is a per-Generation constant (ST-02: generation_id > 0), never per-Cycle:
    G0 -> base geometry in ALL cycles; G1+ -> asymmetric geometry in ALL cycles.
    The 7h arming caller passes ``is_successor=True`` for every cycle of G1+.

R3. BU/SL LABELS ARE ILLUSTRATIVE. The D-09 block's "Dominant side: BU1 / Weak
    side: SL1" is an instantiation, not a binding. Side selection comes ONLY from
    ST-14 dominance (§4.5, direction-agnostic); geometry takes ``is_dominant``
    independent of ``direction``.

NO ROUNDING (documented): §5.4/§7.1 tick-rounding is satisfied downstream — §6.3
places normalization at order-build time ("before every signed order"), and no
tick source exists in 7g-1; rounding here would invent venue data. Prices are kept
at full precision. NO SIZING: notionals (STR-0148/0150) are §7.3 / Phase 7g-2 —
geometry is prices only.
"""

from __future__ import annotations

from decimal import Decimal

_GROUPS = frozenset({"BU", "SL"})
_ONE = Decimal("1")
_BPS_DENOM = Decimal("10000")  # bps -> fraction (10^4; never the `^` operator)


def _require_pos_decimal(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} must be a Decimal instance")
    if value <= 0:
        raise ValueError(f"{name} must be > 0")


def compute_ladder_geometry(
    *,
    reference_price: Decimal,
    direction: str,
    grid_levels: int,
    step_bps: Decimal,
    first_level_distance_bps: Decimal,
    is_successor: bool,
    is_dominant: bool,
    gen2_distance_multiplier: Decimal,
    weak_side_first_level_multiplier: Decimal,
) -> tuple[Decimal, ...]:
    """Return exactly ``grid_levels`` ladder prices, in traversal order (§7.1).

    Base (G0, all cycles): L1 distance = first_level_distance_bps (both groups).
    Successor (G1+, all cycles): dominant L1 = gen2_distance_multiplier * step_bps;
    weak L1 = weak_side_first_level_multiplier * step_bps (the weak L1 LOCK is a
    state flag, §7.2 / protection_lock, not a geometry difference). Levels 2..N are
    chained (R1). ``is_dominant`` is IGNORED when ``is_successor`` is False.
    """
    if direction not in _GROUPS:
        raise ValueError(f"direction must be BU or SL: {direction!r}")
    if not (1 <= grid_levels <= 12):  # provenance: config GridGeometryParams bound
        raise ValueError("grid_levels must be within 1..12")
    _require_pos_decimal(reference_price, "reference_price")
    _require_pos_decimal(step_bps, "step_bps")
    _require_pos_decimal(first_level_distance_bps, "first_level_distance_bps")
    _require_pos_decimal(gen2_distance_multiplier, "gen2_distance_multiplier")
    _require_pos_decimal(
        weak_side_first_level_multiplier, "weak_side_first_level_multiplier"
    )
    # NOT validated here (documented): the Gen2DistanceMultiplier 1.1-2.0 range
    # (STR-0149) is a CONFIG-layer bound owned at config resolution (ST-11), not in
    # this pure math function.

    if not is_successor:
        d1_bps = first_level_distance_bps
    elif is_dominant:
        d1_bps = gen2_distance_multiplier * step_bps
    else:
        d1_bps = weak_side_first_level_multiplier * step_bps

    sign = _ONE if direction == "BU" else -_ONE
    first_price = reference_price * (_ONE + sign * d1_bps / _BPS_DENOM)
    step_factor = _ONE + sign * step_bps / _BPS_DENOM

    prices = [first_price]
    for _ in range(grid_levels - 1):
        prices.append(prices[-1] * step_factor)
    return tuple(prices)
