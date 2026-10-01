"""§11.2 hedge urgency + HedgeIntent (no quantity formula; R8) (7g-3b)."""

from decimal import Decimal

import pytest

from hypergrid.core.transitions import (
    HedgeExecution,
    HedgeIntent,
    IntentTag,
    build_hedge_intent,
    hedge_execution_for,
)


def test_execution_branch() -> None:
    assert hedge_execution_for(acute=True) == HedgeExecution.IOC
    assert hedge_execution_for(acute=False) == HedgeExecution.PREFER_MAKER
    with pytest.raises(ValueError):
        hedge_execution_for(acute=1)  # truthy int


def test_ioc_value_is_verbatim() -> None:
    assert HedgeExecution.IOC.value == "Ioc"  # verbatim TIF, NOT "IOC"
    assert HedgeExecution.PREFER_MAKER.value == "PREFER_MAKER"


def test_intent_tag_members() -> None:
    assert IntentTag.EXPOSURE_CORRECTION_INTENT.value == "EXPOSURE_CORRECTION_INTENT"
    assert IntentTag.ENTRY_INTENT.value == "ENTRY_INTENT"


def test_intent_coherence_enforced() -> None:
    ok = build_hedge_intent(delta_hat=Decimal("0.5"), acute=True)
    assert ok.execution == HedgeExecution.IOC
    assert ok.acute is True
    # wrong tag rejected
    with pytest.raises(ValueError):
        HedgeIntent(IntentTag.ENTRY_INTENT, Decimal("0.5"), True, HedgeExecution.IOC)
    # acute<=>IOC coherence enforced
    with pytest.raises(ValueError):
        HedgeIntent(
            IntentTag.EXPOSURE_CORRECTION_INTENT,
            Decimal("0.5"),
            True,
            HedgeExecution.PREFER_MAKER,
        )
    # truthy-int acute rejected
    with pytest.raises(ValueError):
        HedgeIntent(
            IntentTag.EXPOSURE_CORRECTION_INTENT, Decimal("0"), 1, HedgeExecution.IOC
        )


def test_no_rounding_site_fractional_delta_r8() -> None:
    # A fractional Δ above T_exit passes through EXACTLY (no rounding to a q_min lot).
    delta = Decimal("2.0001")
    intent = build_hedge_intent(delta_hat=delta, acute=False)
    assert intent.amount == Decimal("2.0001")
    assert intent.execution == HedgeExecution.PREFER_MAKER


def test_amount_bounded_by_delta_property() -> None:
    # |amount| <= |Δ| holds by construction (Δ̂ ∈ {0, Δ}).
    for raw, hat in ((Decimal("5"), Decimal("5")), (Decimal("-3"), Decimal("0"))):
        intent = build_hedge_intent(delta_hat=hat, acute=False)
        assert abs(intent.amount) <= abs(raw)


def test_zero_amount_intent_constructed() -> None:
    intent = build_hedge_intent(delta_hat=Decimal("0"), acute=True)
    assert intent.amount == Decimal("0")
    assert intent.execution == HedgeExecution.IOC  # execution from acute alone
