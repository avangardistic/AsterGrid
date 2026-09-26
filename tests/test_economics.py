"""§10 economics pure functions (Phase 7h-4b-1, E2)."""

from decimal import Decimal

import pytest

from hypergrid.core.transitions import (
    PathEconomicsVerdict,
    check_arming_validity,
    classify_path_economics,
    compute_gross_grid_edge,
    compute_net_expected_edge,
)

# --------------------------- B1.1 gross grid edge ---------------------------


def test_gross_grid_edge_passthrough() -> None:
    assert compute_gross_grid_edge(step_bps=Decimal("10")) == Decimal("10")


def test_gross_grid_edge_rejects_nonpositive_and_nondecimal() -> None:
    with pytest.raises(ValueError):
        compute_gross_grid_edge(step_bps=Decimal("0"))
    with pytest.raises(ValueError):
        compute_gross_grid_edge(step_bps=Decimal("-1"))
    with pytest.raises(ValueError):
        compute_gross_grid_edge(step_bps=10)  # type: ignore[arg-type]


# --------------------------- B1.2 net expected edge ---------------------------


def test_net_expected_edge_exact() -> None:
    assert compute_net_expected_edge(
        gross_edge_bps=Decimal("10"),
        fee_bps=Decimal("1.5"),
        slippage_bps=Decimal("0.5"),
        funding_bps=Decimal("0.25"),
        other_bps=Decimal("0.25"),
    ) == Decimal("7.5")


def test_net_expected_edge_terms_any_sign() -> None:
    # rebate (negative fee) and price improvement (negative other) increase net.
    assert compute_net_expected_edge(
        gross_edge_bps=Decimal("10"),
        fee_bps=Decimal("-1"),
        slippage_bps=Decimal("0"),
        funding_bps=Decimal("-2"),
        other_bps=Decimal("0"),
    ) == Decimal("13")


def test_net_expected_edge_validation() -> None:
    with pytest.raises(ValueError):  # gross <= 0
        compute_net_expected_edge(
            gross_edge_bps=Decimal("0"),
            fee_bps=Decimal("1"),
            slippage_bps=Decimal("0"),
            funding_bps=Decimal("0"),
            other_bps=Decimal("0"),
        )
    with pytest.raises(ValueError):  # non-Decimal term
        compute_net_expected_edge(
            gross_edge_bps=Decimal("10"),
            fee_bps=1.5,  # type: ignore[arg-type]
            slippage_bps=Decimal("0"),
            funding_bps=Decimal("0"),
            other_bps=Decimal("0"),
        )


# --------------------------- B1.3 path classification ---------------------------


def test_classify_maker_taker_below() -> None:
    assert (
        classify_path_economics(
            net_expected_edge_bps=Decimal("5"),
            floor_bps=Decimal("1"),
            is_emergency_or_hedge=False,
        )
        == PathEconomicsVerdict.MAKER_PREFERRED
    )
    assert (
        classify_path_economics(
            net_expected_edge_bps=Decimal("5"),
            floor_bps=Decimal("1"),
            is_emergency_or_hedge=True,
        )
        == PathEconomicsVerdict.TAKER_REQUIRED
    )
    # boundary net == floor → BELOW (STR-0197 ≤).
    assert (
        classify_path_economics(
            net_expected_edge_bps=Decimal("1"),
            floor_bps=Decimal("1"),
            is_emergency_or_hedge=False,
        )
        == PathEconomicsVerdict.BELOW_FLOOR
    )
    # emergency but uneconomic → still BELOW (either path).
    assert (
        classify_path_economics(
            net_expected_edge_bps=Decimal("0.5"),
            floor_bps=Decimal("1"),
            is_emergency_or_hedge=True,
        )
        == PathEconomicsVerdict.BELOW_FLOOR
    )
    # negative net → BELOW.
    assert (
        classify_path_economics(
            net_expected_edge_bps=Decimal("-3"),
            floor_bps=Decimal("1"),
            is_emergency_or_hedge=False,
        )
        == PathEconomicsVerdict.BELOW_FLOOR
    )


def test_classify_validation() -> None:
    with pytest.raises(ValueError):  # floor < 0
        classify_path_economics(
            net_expected_edge_bps=Decimal("5"),
            floor_bps=Decimal("-1"),
            is_emergency_or_hedge=False,
        )
    with pytest.raises(ValueError):  # non-Decimal
        classify_path_economics(
            net_expected_edge_bps=5,  # type: ignore[arg-type]
            floor_bps=Decimal("1"),
            is_emergency_or_hedge=False,
        )
    with pytest.raises(ValueError):  # non-bool flag
        classify_path_economics(
            net_expected_edge_bps=Decimal("5"),
            floor_bps=Decimal("1"),
            is_emergency_or_hedge=1,  # type: ignore[arg-type]
        )


# --------------------------- B1.4 arming validity ---------------------------


def test_arming_validity_vector_and_boundary() -> None:
    # STR-0350 worked vector: 10 - 2*1.5 - 0 = 7 > 1 ✓.
    assert (
        check_arming_validity(
            gge_bps=Decimal("10"),
            fee_maker_bps=Decimal("1.5"),
            funding_est_bps=Decimal("0"),
            floor_bps=Decimal("1"),
        )
        is True
    )
    # boundary: 4 - 2*1.5 - 0 = 1, NOT > 1 → False (strict).
    assert (
        check_arming_validity(
            gge_bps=Decimal("4"),
            fee_maker_bps=Decimal("1.5"),
            funding_est_bps=Decimal("0"),
            floor_bps=Decimal("1"),
        )
        is False
    )


def test_arming_validity_validation() -> None:
    with pytest.raises(ValueError):  # gge <= 0
        check_arming_validity(
            gge_bps=Decimal("0"),
            fee_maker_bps=Decimal("1"),
            funding_est_bps=Decimal("0"),
            floor_bps=Decimal("1"),
        )
    with pytest.raises(ValueError):  # floor < 0
        check_arming_validity(
            gge_bps=Decimal("10"),
            fee_maker_bps=Decimal("1"),
            funding_est_bps=Decimal("0"),
            floor_bps=Decimal("-1"),
        )
    with pytest.raises(ValueError):  # non-Decimal
        check_arming_validity(
            gge_bps=Decimal("10"),
            fee_maker_bps=1.5,  # type: ignore[arg-type]
            funding_est_bps=Decimal("0"),
            floor_bps=Decimal("1"),
        )
