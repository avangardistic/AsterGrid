"""§11.1 exposure functions: determinism + no input mutation (Phase 7g-3a)."""

from decimal import Decimal

from astergrid.core.serialization import canonical_dumps
from astergrid.core.transitions import (
    LevelFillState,
    classify_exposure,
    compute_expected_exposure,
    compute_exposure_delta,
    is_acute,
)

_FILLS = (
    LevelFillState(0, 0, "BU", 1, Decimal("2.5"), "POSITION_VERIFIED"),
    LevelFillState(0, 0, "SL", 2, Decimal("4.0"), "FILLED"),
)


def test_expected_byte_identical_no_mutation() -> None:
    before = canonical_dumps([f.to_canonical_obj() for f in _FILLS])
    a = compute_expected_exposure(level_fills=_FILLS)
    b = compute_expected_exposure(level_fills=_FILLS)
    assert canonical_dumps([a]) == canonical_dumps([b])
    assert canonical_dumps([f.to_canonical_obj() for f in _FILLS]) == before


def test_delta_and_classify_and_acute_deterministic() -> None:
    d1 = compute_exposure_delta(
        expected_exposure=Decimal("-1.5"), actual_exposure=Decimal("0")
    )
    d2 = compute_exposure_delta(
        expected_exposure=Decimal("-1.5"), actual_exposure=Decimal("0")
    )
    assert canonical_dumps([d1]) == canonical_dumps([d2])
    c1 = classify_exposure(
        exposure_delta=d1,
        normal_tolerance=Decimal("1"),
        transient_tolerance=Decimal("3"),
    )
    c2 = classify_exposure(
        exposure_delta=d2,
        normal_tolerance=Decimal("1"),
        transient_tolerance=Decimal("3"),
    )
    assert c1.value == c2.value
    a1 = is_acute(
        exposure_delta=d1,
        max_exposure_imbalance=Decimal("3"),
        margin_distance=Decimal("100"),
        emergency_tolerance=Decimal("5"),
    )
    a2 = is_acute(
        exposure_delta=d2,
        max_exposure_imbalance=Decimal("3"),
        margin_distance=Decimal("100"),
        emergency_tolerance=Decimal("5"),
    )
    assert a1 == a2
