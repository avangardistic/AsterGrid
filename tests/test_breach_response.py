"""§12.1 three-layer breach ladder (Phase 7h-4a, E2). All 8 cells + boundaries."""

from decimal import Decimal

import pytest

from hypergrid.core.transitions import (
    BreachLayer,
    RiskReasonCode,
    apply_breach_response,
)

_PRIORS = (
    BreachLayer.NONE,
    BreachLayer.ALERT,
    BreachLayer.SOFT_PROTECTIVE_ACTION,
    BreachLayer.OPERATOR_DECISION,
)


def _resp(current: str, bound: str, prior: BreachLayer):  # type: ignore[no-untyped-def]
    return apply_breach_response(
        current_value=Decimal(current), bound_value=Decimal(bound), prior_layer=prior
    )


def test_not_breached_clears_from_every_prior() -> None:
    for prior in _PRIORS:
        assert _resp("10", "20", prior) == (BreachLayer.NONE, None)


def test_boundary_equal_is_not_breached() -> None:
    # current == bound is compliant (STRICT >).
    for prior in _PRIORS:
        assert _resp("20", "20", prior) == (BreachLayer.NONE, None)


def test_breach_escalation_chain() -> None:
    assert _resp("21", "20", BreachLayer.NONE) == (
        BreachLayer.ALERT,
        RiskReasonCode.RISK_BOUND_ALERT,
    )
    assert _resp("21", "20", BreachLayer.ALERT) == (
        BreachLayer.SOFT_PROTECTIVE_ACTION,
        RiskReasonCode.RISK_BOUND_SOFT_ACTION,
    )
    assert _resp("21", "20", BreachLayer.SOFT_PROTECTIVE_ACTION) == (
        BreachLayer.OPERATOR_DECISION,
        RiskReasonCode.RISK_BOUND_OPERATOR_REQUIRED,
    )


def test_operator_is_sticky_no_new_code() -> None:
    assert _resp("21", "20", BreachLayer.OPERATOR_DECISION) == (
        BreachLayer.OPERATOR_DECISION,
        None,
    )


def test_all_eight_cells_return_never_raise() -> None:
    count = 0
    for breached in (False, True):
        for prior in _PRIORS:
            current = "21" if breached else "10"
            layer, _ = _resp(current, "20", prior)
            assert isinstance(layer, BreachLayer)
            count += 1
    assert count == 8


def test_validation() -> None:
    with pytest.raises(ValueError):  # non-Decimal current
        apply_breach_response(
            current_value=1.0,  # type: ignore[arg-type]
            bound_value=Decimal("20"),
            prior_layer=BreachLayer.NONE,
        )
    with pytest.raises(ValueError):  # bound <= 0
        _resp("1", "0", BreachLayer.NONE)
    with pytest.raises(ValueError):  # current < 0
        _resp("-1", "20", BreachLayer.NONE)
    with pytest.raises(ValueError):  # non-BreachLayer prior
        apply_breach_response(
            current_value=Decimal("1"),
            bound_value=Decimal("20"),
            prior_layer="NONE",  # type: ignore[arg-type]
        )
