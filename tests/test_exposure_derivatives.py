"""§11.1 exposure derivatives + R7 signs (Phase 7g-3a)."""

from decimal import Decimal

import pytest

from hypergrid.core.transitions import (
    LevelFillState,
    compute_actual_exposure,
    compute_expected_exposure,
    compute_exposure_delta,
)

_EXCLUDED = (
    "CANCELLED",
    "SKIPPED",
    "ERROR",
    "IDLE",
    "LOCKED",
    "EMERGENCY",
    "INTENT_CREATED",
    "ORDER_SUBMITTED",
    "ORDER_ACKNOWLEDGED",
    "ORDER_ACTIVE",
)
_COUNTED = ("PARTIALLY_FILLED", "FILLED", "POSITION_VERIFIED")


def _fill(
    direction: str, qty: str, lifecycle: str, level_id: int = 1
) -> LevelFillState:
    return LevelFillState(0, 0, direction, level_id, Decimal(qty), lifecycle)


def test_empty_is_zero() -> None:
    assert compute_expected_exposure(level_fills=()) == Decimal("0")


def test_single_bu_partial() -> None:
    assert compute_expected_exposure(
        level_fills=(_fill("BU", "0.3", "PARTIALLY_FILLED"),)
    ) == Decimal("0.3")


def test_single_sl_filled_negative() -> None:
    assert compute_expected_exposure(
        level_fills=(_fill("SL", "0.3", "FILLED"),)
    ) == Decimal("-0.3")


def test_flat_book_is_zero_r7() -> None:
    # R7 money test: unsigned summation would give 2.0; signed net is 0.
    fills = (
        _fill("BU", "1.0", "POSITION_VERIFIED", 1),
        _fill("SL", "1.0", "POSITION_VERIFIED", 2),
    )
    assert compute_expected_exposure(level_fills=fills) == Decimal("0")


def test_mixed_book() -> None:
    fills = (
        _fill("BU", "2.5", "POSITION_VERIFIED", 1),
        _fill("BU", "1.0", "FILLED", 2),
        _fill("SL", "4.0", "POSITION_VERIFIED", 3),
    )
    assert compute_expected_exposure(level_fills=fills) == Decimal("-0.5")


def test_excluded_lifecycles_contribute_zero() -> None:
    for lifecycle in _EXCLUDED:
        fills = (_fill("BU", "5.0", lifecycle),)
        assert compute_expected_exposure(level_fills=fills) == Decimal("0"), lifecycle


def test_counted_lifecycles_contribute() -> None:
    for lifecycle in _COUNTED:
        fills = (_fill("BU", "5.0", lifecycle),)
        assert compute_expected_exposure(level_fills=fills) == Decimal("5.0"), lifecycle


def test_actual_exposure_identity() -> None:
    assert compute_actual_exposure(net_position=Decimal("3.5")) == Decimal("3.5")
    assert compute_actual_exposure(net_position=Decimal("-2.0")) == Decimal("-2.0")
    assert compute_actual_exposure(net_position=Decimal("0")) == Decimal("0")
    with pytest.raises(ValueError):
        compute_actual_exposure(net_position=3.5)  # float


def test_exposure_delta() -> None:
    assert compute_exposure_delta(
        expected_exposure=Decimal("2"), actual_exposure=Decimal("5")
    ) == Decimal("-3")
    assert compute_exposure_delta(
        expected_exposure=Decimal("5"), actual_exposure=Decimal("5")
    ) == Decimal("0")
    with pytest.raises(ValueError):
        compute_exposure_delta(expected_exposure=2, actual_exposure=Decimal("5"))
