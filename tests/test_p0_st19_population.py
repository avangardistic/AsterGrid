"""ST-19 population by the real P0 (Phase 7h-1)."""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.transitions.market_observation_state import MarketObservationState
from hypergrid.core.transitions.observation_state import P0ObservationMarkers


def _markers(**over: object) -> P0ObservationMarkers:
    fields: dict[str, object] = {
        "observations": (),
        "net_position": Decimal("0"),
        "mark_price": Decimal("50000"),
        "tau_acc": Decimal("0.00005"),
        "min_notional_usd": Decimal("10"),
        "max_exposure_imbalance": Decimal("3"),
        "emergency_tolerance": Decimal("5"),
        "margin_distance": Decimal("100"),
        "normal_tolerance": Decimal("1"),
        "transient_tolerance": Decimal("3"),
    }
    fields.update(over)
    return P0ObservationMarkers(**fields)  # type: ignore[arg-type]


def test_st19_absent_before_present_after() -> None:
    state = _empty_state()
    assert state.st19_market_observation_cache is None
    new_state, _ = run_pass(
        dataclasses.replace(state, p0_observation_markers=_markers()), []
    )
    st19 = new_state.st19_market_observation_cache
    assert isinstance(st19, MarketObservationState)


def test_mark_price_carried_exactly() -> None:
    m = _markers(mark_price=Decimal("63125.5"))
    new_state, _ = run_pass(
        dataclasses.replace(_empty_state(), p0_observation_markers=m), []
    )
    st19 = new_state.st19_market_observation_cache
    assert st19 is not None
    assert st19.mark_price == Decimal("63125.5")


def test_mark_price_nonpositive_or_nondecimal_rejected() -> None:
    with pytest.raises(ValueError):
        _markers(mark_price=Decimal("0"))
    with pytest.raises(ValueError):
        _markers(mark_price=Decimal("-1"))
    with pytest.raises(ValueError):
        _markers(mark_price=50000.0)  # float rejected


def test_st19_unwritten_when_p0_markers_absent() -> None:
    # 7d-compat pin: no p0 markers -> NO_OP -> ST-19 stays None.
    new_state, report = run_pass(_empty_state(), [])
    p0 = {s.stage: s for s in report.stages}["P0"]
    assert p0.status == "NO_OP"
    assert new_state.st19_market_observation_cache is None
