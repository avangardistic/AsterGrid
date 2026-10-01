"""ST-07/08/09 + LevelFillState dataclasses (Phase 7g-3a)."""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.transitions import (
    ActualExposureState,
    ExpectedExposureState,
    ExposureClass,
    ExposureDeltaState,
    LevelFillState,
)


def test_all_frozen() -> None:
    fill = LevelFillState(0, 0, "BU", 1, Decimal("1"), "FILLED")
    with pytest.raises(dataclasses.FrozenInstanceError):
        fill.level_id = 2  # type: ignore[misc]
    exp = ExpectedExposureState(Decimal("1"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        exp.value = Decimal("2")  # type: ignore[misc]


def test_level_fill_validation() -> None:
    with pytest.raises(ValueError):  # bad direction
        LevelFillState(0, 0, "XX", 1, Decimal("1"), "FILLED")
    with pytest.raises(ValueError):  # bad gen id
        LevelFillState(100, 0, "BU", 1, Decimal("1"), "FILLED")
    with pytest.raises(ValueError):  # bad level id
        LevelFillState(0, 0, "BU", 13, Decimal("1"), "FILLED")
    with pytest.raises(ValueError):  # non-Decimal qty
        LevelFillState(0, 0, "BU", 1, 1, "FILLED")  # type: ignore[arg-type]
    with pytest.raises(ValueError):  # negative qty
        LevelFillState(0, 0, "BU", 1, Decimal("-1"), "FILLED")
    with pytest.raises(ValueError):  # bad lifecycle
        LevelFillState(0, 0, "BU", 1, Decimal("1"), "BOGUS")


def test_expected_exposure_signed() -> None:
    assert ExpectedExposureState(Decimal("-5")).value == Decimal("-5")  # negative ok
    with pytest.raises(ValueError):
        ExpectedExposureState(5)  # type: ignore[arg-type]


def test_actual_exposure_source_enforced() -> None:
    ok = ActualExposureState(Decimal("-2"), "clearinghouseState")
    assert ok.value == Decimal("-2")
    with pytest.raises(ValueError):  # DECISION-002 enforcement
        ActualExposureState(Decimal("1"), "webData2")
    with pytest.raises(ValueError):
        ActualExposureState(1, "clearinghouseState")  # type: ignore[arg-type]


def test_delta_state_coherence() -> None:
    ok = ExposureDeltaState(
        expected_value=Decimal("2"),
        actual_value=Decimal("5"),
        delta=Decimal("-3"),
        classification=ExposureClass.TRANSIENT,
        is_acute=False,
    )
    assert ok.delta == Decimal("-3")
    with pytest.raises(ValueError):  # delta != expected - actual
        ExposureDeltaState(
            expected_value=Decimal("2"),
            actual_value=Decimal("5"),
            delta=Decimal("3"),
            classification=ExposureClass.NORMAL,
            is_acute=False,
        )
    with pytest.raises(ValueError):  # classification not an ExposureClass
        ExposureDeltaState(
            expected_value=Decimal("0"),
            actual_value=Decimal("0"),
            delta=Decimal("0"),
            classification="NORMAL",  # type: ignore[arg-type]
            is_acute=False,
        )
    with pytest.raises(ValueError):  # is_acute must be a bool (no truthy int)
        ExposureDeltaState(
            expected_value=Decimal("0"),
            actual_value=Decimal("0"),
            delta=Decimal("0"),
            classification=ExposureClass.NORMAL,
            is_acute=1,  # type: ignore[arg-type]
        )


def test_serialization() -> None:
    canonical_dumps(
        LevelFillState(0, 0, "BU", 1, Decimal("1"), "FILLED").to_canonical_obj()
    )
    canonical_dumps(ExpectedExposureState(Decimal("-5")).to_canonical_obj())
    canonical_dumps(
        ActualExposureState(Decimal("-2"), "clearinghouseState").to_canonical_obj()
    )
    delta = ExposureDeltaState(
        expected_value=Decimal("2"),
        actual_value=Decimal("5"),
        delta=Decimal("-3"),
        classification=ExposureClass.TRANSIENT,
        is_acute=True,
    )
    obj = delta.to_canonical_obj()
    assert obj["classification"] == "TRANSIENT"  # plain string
    canonical_dumps(obj)


def test_equal_instances_serialize_identically() -> None:
    a = ExpectedExposureState(Decimal("-5"))
    b = ExpectedExposureState(Decimal("-5"))
    assert a == b
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )
