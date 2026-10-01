"""§11.1 classification bands R6 + ExposureClass enum (Phase 7g-3a)."""

from decimal import Decimal

import pytest

from astergrid.core.transitions import ExposureClass, classify_exposure


def _c(delta: str, normal: str = "1", transient: str = "3") -> ExposureClass:
    return classify_exposure(
        exposure_delta=Decimal(delta),
        normal_tolerance=Decimal(normal),
        transient_tolerance=Decimal(transient),
    )


def test_band_boundaries() -> None:
    assert _c("1") == ExposureClass.NORMAL  # |Δ| == normal
    assert _c("3") == ExposureClass.TRANSIENT  # |Δ| == transient
    assert _c("3.0001") == ExposureClass.ESCALATE  # just above transient
    assert _c("0") == ExposureClass.NORMAL  # zero -> NORMAL


def test_mid_bands() -> None:
    assert _c("0.5") == ExposureClass.NORMAL
    assert _c("2") == ExposureClass.TRANSIENT
    assert _c("100") == ExposureClass.ESCALATE


def test_negative_delta_by_magnitude() -> None:
    assert _c("-2") == ExposureClass.TRANSIENT
    assert _c("-100") == ExposureClass.ESCALATE


def test_degenerate_two_class() -> None:
    # normal == transient: at the shared boundary the first rule wins -> NORMAL.
    assert _c("2", normal="2", transient="2") == ExposureClass.NORMAL
    assert _c("2.0001", normal="2", transient="2") == ExposureClass.ESCALATE


def test_validation() -> None:
    with pytest.raises(ValueError):
        _c("1", normal="0")  # normal <= 0
    with pytest.raises(ValueError):
        _c("1", normal="3", transient="1")  # inversion
    with pytest.raises(ValueError):
        classify_exposure(
            exposure_delta=1,  # non-Decimal
            normal_tolerance=Decimal("1"),
            transient_tolerance=Decimal("3"),
        )


def test_enum_members() -> None:
    assert {m.name for m in ExposureClass} == {"NORMAL", "TRANSIENT", "ESCALATE"}
    for m in ExposureClass:
        assert m.value == m.name  # value == name
        assert isinstance(m.value, str)
