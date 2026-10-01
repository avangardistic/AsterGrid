"""§11.4 remainder tri-state (7g-3b) + 7g-3a cross-test."""

from decimal import Decimal

import pytest

from hypergrid.core.transitions import (
    LevelFillState,
    RemainderHedgeStatus,
    classify_remainder_hedge_status,
    compute_expected_exposure,
)


def test_skipped_wins_precedence() -> None:
    assert (
        classify_remainder_hedge_status(within_timeout=True, skipped=True)
        == RemainderHedgeStatus.SKIPPED_RESIDUAL_ZERO
    )
    assert (
        classify_remainder_hedge_status(within_timeout=False, skipped=True)
        == RemainderHedgeStatus.SKIPPED_RESIDUAL_ZERO
    )


def test_working_and_pending() -> None:
    assert (
        classify_remainder_hedge_status(within_timeout=True, skipped=False)
        == RemainderHedgeStatus.WORKING_NOT_YET_EXPOSURE
    )
    assert (
        classify_remainder_hedge_status(within_timeout=False, skipped=False)
        == RemainderHedgeStatus.PENDING_EMERGENCY_EXECUTION
    )


def test_truthy_int_rejected() -> None:
    with pytest.raises(ValueError):
        classify_remainder_hedge_status(within_timeout=1, skipped=False)
    with pytest.raises(ValueError):
        classify_remainder_hedge_status(within_timeout=True, skipped=0)


def test_skipped_level_contributes_zero_cross_test() -> None:
    # 7g-3a link: a SKIPPED level contributes zero to ExpectedExposure (no new code).
    fills = (LevelFillState(0, 0, "BU", 1, Decimal("5"), "SKIPPED"),)
    assert compute_expected_exposure(level_fills=fills) == Decimal("0")
