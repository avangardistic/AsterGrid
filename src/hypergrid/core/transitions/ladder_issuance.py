"""§5.2 step-8 one-direction ladder issuance (Phase 7h-4b-1). Pure.

Composes 7g-1 ``compute_ladder_geometry`` + ``is_protection_locked_initial`` +
``LevelState`` construction to issue ONE direction's fresh ladder. Gated on the §10
edge bool (the §8 half is P6-compositional, 7h-4b-2). Rows are RETURNED, never stored
(the caller stores them). A LEAF module: stdlib + same-package geometry/protection_lock/
level_state ONLY. It MUST NOT import ``core.state``/``core.pass_engine``.

Cite: §5.2 step 8 ("Issue a fresh ladder for BOTH groups …, subject to all strategy
gates (§8, §10)"); STR-0080; §7.1 R1/R2; STR-0146 (L1 lock).
"""

from __future__ import annotations

from decimal import Decimal

from hypergrid.core.transitions.geometry import compute_ladder_geometry
from hypergrid.core.transitions.level_state import LevelState
from hypergrid.core.transitions.protection_lock import is_protection_locked_initial


def issue_fresh_ladder(
    *,
    reference_price: Decimal,
    direction: str,
    grid_levels: int,
    step_bps: Decimal,
    first_level_distance_bps: Decimal,
    is_dominant: bool,
    gen2_distance_multiplier: Decimal,
    weak_side_first_level_multiplier: Decimal,
    size_notional_usd: Decimal,
    edge_clears_floor: bool,
    current_generation_id: int,
    current_cycle_id: int,
) -> tuple[LevelState, ...]:
    """Issue one direction's fresh ladder (§5.2 step 8). ``()`` iff edge blocked.

    ``is_successor`` is DERIVED ``current_generation_id > 0`` (R2 per-Generation
    constant; passed to BOTH geometry and the lock fn — a param would invite R2
    violations). ``current_generation_id``/``current_cycle_id`` are the ids the ladder
    is issued FOR (post-transition G-(C+1): step 6 creates it, step 8 fills it).

    Order: exact-type checks FIRST → ``compute_ladder_geometry`` (validates direction/
    numerics + the 1..12 range and computes prices) → the §10 gate → row build. Geometry
    runs before the gate so malformed inputs raise even when blocked (E2 / P12 matrix:
    "garbage + False STILL raises"; the ONLY empty-tuple path is ``edge_clears_floor
    is False``, never a vacuous grid).
    """
    # Exact-type checks B2 owns (the bool-hole: True passes int range checks — 7h-3
    # track_remainder precedent). Direction/numerics/ranges are geometry's + the ctor's.
    if type(edge_clears_floor) is not bool:
        raise ValueError("edge_clears_floor must be a bool")
    if type(is_dominant) is not bool:
        raise ValueError("is_dominant must be a bool")
    if type(grid_levels) is not int:
        raise ValueError("grid_levels must be an int")
    if type(current_generation_id) is not int:
        raise ValueError("current_generation_id must be an int")
    if type(current_cycle_id) is not int:
        raise ValueError("current_cycle_id must be an int")
    if not isinstance(size_notional_usd, Decimal):
        raise ValueError("size_notional_usd must be a Decimal instance")
    if size_notional_usd <= 0:
        raise ValueError("size_notional_usd must be > 0")

    is_successor = current_generation_id > 0  # R2: per-Generation, never per-Cycle

    prices = compute_ladder_geometry(
        reference_price=reference_price,
        direction=direction,
        grid_levels=grid_levels,
        step_bps=step_bps,
        first_level_distance_bps=first_level_distance_bps,
        is_successor=is_successor,
        is_dominant=is_dominant,
        gen2_distance_multiplier=gen2_distance_multiplier,
        weak_side_first_level_multiplier=weak_side_first_level_multiplier,
    )

    if edge_clears_floor is False:  # §10 gate (STR-0197 fail -> §9.3 Skip, caller-side)
        return ()

    return tuple(
        LevelState(
            current_generation_id,
            current_cycle_id,
            direction,
            level_id,
            price,
            is_protection_locked_initial(
                is_successor=is_successor,
                is_dominant=is_dominant,
                level_id=level_id,
            ),
            size_notional_usd=size_notional_usd,
            # pre-observation rows: lifecycle/filled None (R10c skipped by ctor).
        )
        for level_id, price in enumerate(prices, start=1)
    )


__all__ = ["issue_fresh_ladder"]
