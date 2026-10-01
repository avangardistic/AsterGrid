"""P1 leaf types + EPSILON_H single-source (7g-3b)."""

import dataclasses
from decimal import Decimal

import pytest

from astergrid.core.serialization import canonical_dumps
from astergrid.core.transitions import (
    EPSILON_H,
    HedgeExecution,
    HedgeIntent,
    IntentTag,
    LevelFillState,
    MarketObservationState,
    P1ExposureMarkers,
    hedge,
    hedge_state,
)


def _markers(**over: object) -> P1ExposureMarkers:
    fields: dict[str, object] = {
        "level_fills": (LevelFillState(0, 0, "BU", 1, Decimal("1"), "FILLED"),),
        "net_position": Decimal("0"),
        "tau_acc": Decimal("0.00005"),
        "min_notional_usd": Decimal("10"),
        "mark_price": Decimal("50000"),
        "max_exposure_imbalance": Decimal("3"),
        "emergency_tolerance": Decimal("5"),
        "margin_distance": Decimal("100"),
        "normal_tolerance": Decimal("1"),
        "transient_tolerance": Decimal("3"),
    }
    fields.update(over)
    return P1ExposureMarkers(**fields)  # type: ignore[arg-type]


def test_epsilon_h_single_source() -> None:
    assert Decimal("1") == EPSILON_H
    assert hedge.EPSILON_H is hedge_state.EPSILON_H  # imported, not redefined


def test_markers_frozen_and_validated() -> None:
    m = _markers()
    with pytest.raises(dataclasses.FrozenInstanceError):
        m.mark_price = Decimal("1")  # type: ignore[misc]
    with pytest.raises(ValueError):  # tau_acc <= 0
        _markers(tau_acc=Decimal("0"))
    with pytest.raises(ValueError):  # min_notional <= 0
        _markers(min_notional_usd=Decimal("0"))
    with pytest.raises(ValueError):  # mark_price <= 0
        _markers(mark_price=Decimal("0"))
    with pytest.raises(ValueError):  # margin_distance < 0
        _markers(margin_distance=Decimal("-1"))
    with pytest.raises(ValueError):  # transient < normal
        _markers(normal_tolerance=Decimal("3"), transient_tolerance=Decimal("1"))
    with pytest.raises(ValueError):  # non-Decimal net_position
        _markers(net_position=0)


def test_market_observation_state() -> None:
    ok = MarketObservationState(Decimal("50000"))
    assert ok.mark_price == Decimal("50000")
    canonical_dumps(ok.to_canonical_obj())
    with pytest.raises(ValueError):
        MarketObservationState(Decimal("0"))
    with pytest.raises(ValueError):
        MarketObservationState(Decimal("-1"))
    with pytest.raises(ValueError):
        MarketObservationState(50000)  # type: ignore[arg-type]


def test_hedge_intent_frozen_and_serializes() -> None:
    intent = HedgeIntent(
        IntentTag.EXPOSURE_CORRECTION_INTENT,
        Decimal("1.5"),
        False,
        HedgeExecution.PREFER_MAKER,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        intent.amount = Decimal("2")  # type: ignore[misc]
    obj = intent.to_canonical_obj()
    assert obj["intent_tag"] == "EXPOSURE_CORRECTION_INTENT"
    assert obj["execution"] == "PREFER_MAKER"
    canonical_dumps(obj)


def test_all_to_canonical_pass_canonical_dumps() -> None:
    canonical_dumps(_markers().to_canonical_obj())
