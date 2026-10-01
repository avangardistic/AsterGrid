"""STR-0357 acute predicate (strict on both disjuncts) (Phase 7g-3a)."""

from decimal import Decimal

import pytest

from astergrid.core.transitions import is_acute


def _acute(**over: object) -> bool:
    kw: dict[str, object] = {
        "exposure_delta": Decimal("0"),
        "max_exposure_imbalance": Decimal("3"),  # τ_I
        "margin_distance": Decimal("100"),
        "emergency_tolerance": Decimal("5"),  # d_emergency; 2·d = 10
    }
    kw.update(over)
    return is_acute(**kw)  # type: ignore[arg-type]


def test_imbalance_alone() -> None:
    assert _acute(exposure_delta=Decimal("4")) is True  # |4| > 3


def test_margin_alone() -> None:
    assert _acute(margin_distance=Decimal("9")) is True  # 9 < 10


def test_neither() -> None:
    assert _acute() is False


def test_both() -> None:
    assert _acute(exposure_delta=Decimal("4"), margin_distance=Decimal("9")) is True


def test_boundary_imbalance_equal_false() -> None:
    assert _acute(exposure_delta=Decimal("3")) is False  # |3| > 3 is False


def test_boundary_margin_equal_false() -> None:
    assert _acute(margin_distance=Decimal("10")) is False  # 10 < 10 is False


def test_just_inside_both_false() -> None:
    assert (
        _acute(exposure_delta=Decimal("2.999"), margin_distance=Decimal("10.001"))
        is False
    )


def test_negative_delta_uses_magnitude() -> None:
    assert _acute(exposure_delta=Decimal("-5")) is True  # |-5| > 3


def test_validation() -> None:
    with pytest.raises(ValueError):
        _acute(exposure_delta=0)  # non-Decimal
    with pytest.raises(ValueError):
        _acute(max_exposure_imbalance=Decimal("0"))
    with pytest.raises(ValueError):
        _acute(emergency_tolerance=Decimal("0"))
    with pytest.raises(ValueError):
        _acute(margin_distance=Decimal("-1"))
