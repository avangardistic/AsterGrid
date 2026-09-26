"""§5.2 step-8 one-direction ladder issuance (Phase 7h-4b-1, E2/E3)."""

from decimal import Decimal

import pytest

from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.transitions import compute_ladder_geometry, issue_fresh_ladder


def _issue(**over: object):  # type: ignore[no-untyped-def]
    base: dict[str, object] = {
        "reference_price": Decimal("100000"),
        "direction": "BU",
        "grid_levels": 6,
        "step_bps": Decimal("10"),
        "first_level_distance_bps": Decimal("20"),
        "is_dominant": True,
        "gen2_distance_multiplier": Decimal("2"),
        "weak_side_first_level_multiplier": Decimal("1.5"),
        "size_notional_usd": Decimal("5000"),
        "edge_clears_floor": True,
        "current_generation_id": 0,
        "current_cycle_id": 0,
    }
    base.update(over)
    return issue_fresh_ladder(**base)  # type: ignore[arg-type]


# --------------------------- gate ---------------------------


def test_blocked_returns_empty() -> None:
    assert _issue(edge_clears_floor=False) == ()


# --------------------------- validate-first (raises even when blocked) ---------


def test_validates_first_even_when_blocked() -> None:
    with pytest.raises(ValueError):  # bad flag type
        _issue(edge_clears_floor=False, is_dominant="yes")
    with pytest.raises(ValueError):  # bad direction (geometry runs before the gate)
        _issue(edge_clears_floor=False, direction="LONG")
    with pytest.raises(ValueError):  # grid_levels 0 (no vacuous-empty path)
        _issue(edge_clears_floor=False, grid_levels=0)


# --------------------------- issued G0 ---------------------------


def test_issued_g0_shape_and_prices() -> None:
    rows = _issue()
    assert len(rows) == 6
    assert [r.level_id for r in rows] == [1, 2, 3, 4, 5, 6]
    prices = compute_ladder_geometry(
        reference_price=Decimal("100000"),
        direction="BU",
        grid_levels=6,
        step_bps=Decimal("10"),
        first_level_distance_bps=Decimal("20"),
        is_successor=False,
        is_dominant=True,
        gen2_distance_multiplier=Decimal("2"),
        weak_side_first_level_multiplier=Decimal("1.5"),
    )
    assert tuple(r.target_price for r in rows) == prices
    # R1 exact vector.
    assert rows[0].target_price == Decimal("100200")
    assert rows[1].target_price == Decimal("100300.2")
    # all unlocked (G0 → not successor), size set, pre-observation.
    assert all(r.is_protection_locked is False for r in rows)
    assert all(r.size_notional_usd == Decimal("5000") for r in rows)
    assert all(r.lifecycle is None and r.filled_quantity is None for r in rows)


# --------------------------- issued G1+ (successor) ---------------------------


def test_issued_g1_weak_side_locks_l1() -> None:
    rows = _issue(current_generation_id=1, is_dominant=False)
    assert rows[0].is_protection_locked is True  # weak L1 locked (is_successor derived)
    assert all(r.is_protection_locked is False for r in rows[1:])


def test_issued_g1_dominant_all_unlocked() -> None:
    rows = _issue(current_generation_id=1, is_dominant=True)
    assert all(r.is_protection_locked is False for r in rows)


# --------------------------- direction monotonicity ---------------------------


def test_bu_ascending_sl_descending() -> None:
    bu = _issue(direction="BU")
    sl = _issue(direction="SL")
    bu_prices = [r.target_price for r in bu]
    sl_prices = [r.target_price for r in sl]
    assert bu_prices == sorted(bu_prices)
    assert sl_prices == sorted(sl_prices, reverse=True)


# --------------------------- int-exactness + range ---------------------------


def test_bool_hole_rejected() -> None:
    with pytest.raises(ValueError):
        _issue(grid_levels=True)
    with pytest.raises(ValueError):
        _issue(current_generation_id=True)
    with pytest.raises(ValueError):
        _issue(current_cycle_id=True)


def test_grid_levels_out_of_range_raises() -> None:
    with pytest.raises(ValueError):
        _issue(grid_levels=13)


# --------------------------- E3 end-to-end + persistence ---------------------------


def test_end_to_end_economics_to_ladder() -> None:
    from hypergrid.core.transitions import (
        PathEconomicsVerdict,
        classify_path_economics,
        compute_gross_grid_edge,
        compute_net_expected_edge,
    )

    gge = compute_gross_grid_edge(step_bps=Decimal("10"))
    net = compute_net_expected_edge(
        gross_edge_bps=gge,
        fee_bps=Decimal("1.5"),
        slippage_bps=Decimal("0.5"),
        funding_bps=Decimal("0"),
        other_bps=Decimal("0"),
    )
    verdict = classify_path_economics(
        net_expected_edge_bps=net, floor_bps=Decimal("1"), is_emergency_or_hedge=False
    )
    rows = _issue(edge_clears_floor=(verdict != PathEconomicsVerdict.BELOW_FLOOR))
    assert len(rows) == 6
    for row in rows:
        canonical_dumps(row.to_canonical_obj())
