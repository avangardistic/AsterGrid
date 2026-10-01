"""ST-17/20/21/22 row types + State slot wiring (Phase 7h-4a, E2/E3)."""

import dataclasses
from decimal import Decimal

import pytest

from astergrid.core.fold import _empty_state
from astergrid.core.serialization import canonical_dumps
from astergrid.core.state import _TYPED_ST_FIELD_NAMES, State
from astergrid.core.transitions import (
    AccountEquityState,
    BasketNetPnLState,
    BoundLayerState,
    BreachLayer,
    FreezeErrorRecoveryOverlayState,
    RiskBoundTrackerState,
)
from astergrid.core.transitions.arm_state import OperationalState

_TS = "2026-09-25T00:00:00.000000Z"


# --------------------------- ST-17 ---------------------------


def _equity(**over: object) -> AccountEquityState:
    fields: dict[str, object] = {
        "capital_base_usd": Decimal("100000"),
        "source": "clearinghouseState",
        "read_at_ts": _TS,
    }
    fields.update(over)
    return AccountEquityState(**fields)  # type: ignore[arg-type]


def test_st17_frozen_and_source_verbatim_trap() -> None:
    eq = _equity()
    with pytest.raises(dataclasses.FrozenInstanceError):
        eq.capital_base_usd = Decimal("1")  # type: ignore[misc]
    assert eq.source == "clearinghouseState"
    for bad in (
        "clearinghouseState.accountValue",
        "clearinghouseState accountValue",
        "webData2",
        "",
    ):
        with pytest.raises(ValueError):
            _equity(source=bad)


def test_st17_capital_and_ts_validation() -> None:
    with pytest.raises(ValueError):
        _equity(capital_base_usd=Decimal("0"))
    with pytest.raises(ValueError):
        _equity(capital_base_usd=Decimal("-1"))
    for bad_ts in ("2026-09-25 00:00:00", "2026-09-25T00:00:00Z", "nope"):
        with pytest.raises(ValueError):
            _equity(read_at_ts=bad_ts)


# --------------------------- ST-21 ---------------------------


def test_st21_invariant() -> None:
    ok = BasketNetPnLState(
        realized_usd=Decimal("100"),
        unrealized_usd=Decimal("50"),
        fees_usd=Decimal("10"),
        funding_usd=Decimal("-5"),
        net_usd=Decimal("135"),  # 100 + 50 - 10 + (-5)
    )
    assert ok.net_usd == Decimal("135")
    with pytest.raises(ValueError):  # wrong net
        BasketNetPnLState(
            realized_usd=Decimal("100"),
            unrealized_usd=Decimal("50"),
            fees_usd=Decimal("10"),
            funding_usd=Decimal("-5"),
            net_usd=Decimal("999"),
        )
    with pytest.raises(ValueError):  # non-Decimal
        BasketNetPnLState(
            realized_usd=1.0,  # type: ignore[arg-type]
            unrealized_usd=Decimal("0"),
            fees_usd=Decimal("0"),
            funding_usd=Decimal("0"),
            net_usd=Decimal("1"),
        )


# --------------------------- ST-20 ---------------------------


def _tracker(**over: object) -> RiskBoundTrackerState:
    fields: dict[str, object] = {
        "cumulative_execution_cost_usd": Decimal("0"),
        "cumulative_hedge_cost_usd": Decimal("0"),
        "failed_level_rate_pct": Decimal("0"),
        "range_induced_dd_pct": Decimal("0"),
        "bound_layers": (),
    }
    fields.update(over)
    return RiskBoundTrackerState(**fields)  # type: ignore[arg-type]


def test_st20_ranges_and_empty_layers_ok() -> None:
    assert _tracker().bound_layers == ()
    with pytest.raises(ValueError):
        _tracker(failed_level_rate_pct=Decimal("101"))
    with pytest.raises(ValueError):
        _tracker(range_induced_dd_pct=Decimal("-1"))
    with pytest.raises(ValueError):
        _tracker(cumulative_hedge_cost_usd=Decimal("-1"))


def test_st20_bound_layers_sorted_no_dup_and_bad_id() -> None:
    good = (
        BoundLayerState("MaxExecutionCost", BreachLayer.ALERT, _TS),
        BoundLayerState("MaxHedgeCost", BreachLayer.NONE, _TS),
    )
    assert _tracker(bound_layers=good).bound_layers == good
    unsorted_ = (
        BoundLayerState("MaxHedgeCost", BreachLayer.NONE, _TS),
        BoundLayerState("MaxExecutionCost", BreachLayer.ALERT, _TS),
    )
    with pytest.raises(ValueError):
        _tracker(bound_layers=unsorted_)
    dup = (
        BoundLayerState("MaxHedgeCost", BreachLayer.NONE, _TS),
        BoundLayerState("MaxHedgeCost", BreachLayer.ALERT, _TS),
    )
    with pytest.raises(ValueError):
        _tracker(bound_layers=dup)
    with pytest.raises(ValueError):  # bad bound_id
        BoundLayerState("NotABound", BreachLayer.NONE, _TS)
    with pytest.raises(ValueError):  # bad layer type
        BoundLayerState("MaxHedgeCost", "ALERT", _TS)  # type: ignore[arg-type]


# --------------------------- ST-22 ---------------------------


def test_st22_accepts_all_operational_states() -> None:
    for state in OperationalState:
        row = FreezeErrorRecoveryOverlayState(operational_state=state, since_ts=_TS)
        assert row.operational_state == state
    assert len(list(OperationalState)) == 9


def test_st22_last_reason_code_str_or_none() -> None:
    assert (
        FreezeErrorRecoveryOverlayState(
            operational_state=OperationalState.FROZEN, since_ts=_TS
        ).last_reason_code
        is None
    )
    ok = FreezeErrorRecoveryOverlayState(
        operational_state=OperationalState.ERROR, since_ts=_TS, last_reason_code="X"
    )
    assert ok.last_reason_code == "X"
    with pytest.raises(ValueError):  # empty string
        FreezeErrorRecoveryOverlayState(
            operational_state=OperationalState.ERROR, since_ts=_TS, last_reason_code=""
        )
    with pytest.raises(ValueError):  # non-str
        FreezeErrorRecoveryOverlayState(
            operational_state=OperationalState.ERROR,
            since_ts=_TS,
            last_reason_code=5,  # type: ignore[arg-type]
        )


# --------------------------- slots / persistence ---------------------------


def test_four_slots_default_none() -> None:
    s = _empty_state()
    assert s.st17_account_equity_capital_base is None
    assert s.st20_risk_bound_trackers is None
    assert s.st21_basket_pnl_accounting_net is None
    assert s.st22_freeze_error_recovery_overlay is None


def test_four_names_in_typed_frozenset() -> None:
    for name in (
        "st17_account_equity_capital_base",
        "st20_risk_bound_trackers",
        "st21_basket_pnl_accounting_net",
        "st22_freeze_error_recovery_overlay",
    ):
        assert name in _TYPED_ST_FIELD_NAMES


def _full_state() -> State:
    return dataclasses.replace(
        _empty_state(),
        st17_account_equity_capital_base=_equity(),
        st20_risk_bound_trackers=_tracker(
            bound_layers=(BoundLayerState("MaxHedgeCost", BreachLayer.ALERT, _TS),)
        ),
        st21_basket_pnl_accounting_net=BasketNetPnLState(
            realized_usd=Decimal("100"),
            unrealized_usd=Decimal("0"),
            fees_usd=Decimal("0"),
            funding_usd=Decimal("0"),
            net_usd=Decimal("100"),
        ),
        st22_freeze_error_recovery_overlay=FreezeErrorRecoveryOverlayState(
            operational_state=OperationalState.ACTIVE, since_ts=_TS
        ),
    )


def test_fully_populated_state_serializes() -> None:
    state = _full_state()
    canonical_dumps(state.to_canonical_obj())  # no None/float at any depth
    # assert on the typed rows (mypy-clean) — the serializer round-trips them above.
    st17 = state.st17_account_equity_capital_base
    assert st17 is not None and st17.source == "clearinghouseState"
    st20 = state.st20_risk_bound_trackers
    assert st20 is not None and st20.bound_layers[0].bound_id == "MaxHedgeCost"
    st21 = state.st21_basket_pnl_accounting_net
    assert st21 is not None and st21.net_usd == Decimal("100")
    st22 = state.st22_freeze_error_recovery_overlay
    assert st22 is not None and st22.operational_state == OperationalState.ACTIVE


# --------------------------- E3 end-to-end ---------------------------


def test_end_to_end_pnl_to_bound_to_ladder() -> None:
    from astergrid.core.transitions import (
        apply_breach_response,
        compute_max_execution_cost_pnl_regime,
    )

    pnl = BasketNetPnLState(
        realized_usd=Decimal("1000"),
        unrealized_usd=Decimal("0"),
        fees_usd=Decimal("0"),
        funding_usd=Decimal("0"),
        net_usd=Decimal("1000"),
    )
    bound = compute_max_execution_cost_pnl_regime(
        basket_net_pnl=pnl.net_usd, max_basket_notional=Decimal("30000")
    )
    assert bound == Decimal("300.0")
    layer, code = apply_breach_response(
        current_value=Decimal("400"), bound_value=bound, prior_layer=BreachLayer.NONE
    )
    assert layer == BreachLayer.ALERT
    tracker = RiskBoundTrackerState(
        cumulative_execution_cost_usd=Decimal("400"),
        cumulative_hedge_cost_usd=Decimal("0"),
        failed_level_rate_pct=Decimal("0"),
        range_induced_dd_pct=Decimal("0"),
        bound_layers=(BoundLayerState("MaxExecutionCost", layer, _TS),),
    )
    state = dataclasses.replace(_empty_state(), st20_risk_bound_trackers=tracker)
    canonical_dumps(state.to_canonical_obj())
    assert code is not None
