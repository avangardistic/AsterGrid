"""§8 arm gates + policy wait + B1 inlet + B2 classifier (Phase 7h-2, E2).

All inputs literal (Decimal/int/str); no RNG, no clock. Boundaries per E2.
"""

from decimal import Decimal

import pytest

from astergrid.core.transitions import (
    ArmBlockCode,
    ArmOutcome,
    ArmPolicy,
    IntentTag,
    OperationalState,
    OperatorDecision,
    OrderIntent,
    OrderType,
    classify_intent,
    construct_order_intent,
    evaluate_arm_gates,
    evaluate_wait,
)


def _gates(**over: object) -> object:
    """evaluate_arm_gates with an all-passing ENTRY+AUTO baseline, overridden by kw."""
    base: dict[str, object] = {
        "intent": IntentTag.ENTRY_INTENT,
        "generation_disabled": False,
        "book_depth_at_target": Decimal("100"),
        "order_size": Decimal("1"),
        "distance_bps": 50,
        "min_order_size": Decimal("0.1"),
        "margin_available": Decimal("100"),
        "margin_required": Decimal("10"),
        "exposure_caps_ok": True,
        "open_order_count": 0,
        "price_normalized_ok": True,
        "size_normalized_ok": True,
        "market_state": OperationalState.ACTIVE,
        "net_expected_edge_bps": Decimal("5"),
        "policy": ArmPolicy.AUTO,
        "timeout_s": 30,
    }
    base.update(over)
    return evaluate_arm_gates(**base)  # type: ignore[arg-type]


_NON_ACTIVE = (
    OperationalState.INITIALIZING,
    OperationalState.FREEZE_REQUESTED,
    OperationalState.FREEZING,
    OperationalState.FROZEN,
    OperationalState.RESTARTING,
    OperationalState.ERROR,
    OperationalState.RECOVERY,
    OperationalState.CLOSED,
)


# --------------------------- per-gate pass/fail + boundaries -------------------


def test_gate1_depth_boundary() -> None:
    # depth == multiple x size passes.
    ev = _gates(book_depth_at_target=Decimal("10"), order_size=Decimal("1"))
    assert ev.outcome == ArmOutcome.ARMED
    ev = _gates(book_depth_at_target=Decimal("9.99"), order_size=Decimal("1"))
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.GATE_1_DEPTH


def test_gate2_distance_endpoints_inclusive() -> None:
    assert _gates(distance_bps=5).outcome == ArmOutcome.ARMED
    assert _gates(distance_bps=100).outcome == ArmOutcome.ARMED
    lo = _gates(distance_bps=4)
    assert lo.outcome == ArmOutcome.BLOCKED and lo.code == ArmBlockCode.GATE_2_DISTANCE
    hi = _gates(distance_bps=101)
    assert hi.outcome == ArmOutcome.BLOCKED and hi.code == ArmBlockCode.GATE_2_DISTANCE


def test_gate3_size_minimum() -> None:
    assert (
        _gates(
            order_size=Decimal("0.1"),
            min_order_size=Decimal("0.1"),
            book_depth_at_target=Decimal("100"),
        ).outcome
        == ArmOutcome.ARMED
    )
    ev = _gates(order_size=Decimal("0.05"), min_order_size=Decimal("0.1"))
    assert ev.outcome == ArmOutcome.BLOCKED and ev.code == ArmBlockCode.GATE_3_SIZE


def test_gate4_margin_additive_buffer_boundary() -> None:
    # margin == required + 0.20 x required passes (12 == 10 + 2).
    assert (
        _gates(margin_available=Decimal("12"), margin_required=Decimal("10")).outcome
        == ArmOutcome.ARMED
    )
    ev = _gates(margin_available=Decimal("11.99"), margin_required=Decimal("10"))
    assert ev.outcome == ArmOutcome.BLOCKED and ev.code == ArmBlockCode.GATE_4_MARGIN


def test_gate5_exposure_caps() -> None:
    ev = _gates(exposure_caps_ok=False)
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.GATE_5_EXPOSURE_CAPS


def test_gate6_open_order_count_strict() -> None:
    assert _gates(open_order_count=999, open_order_cap=1000).outcome == ArmOutcome.ARMED
    ev = _gates(open_order_count=1000, open_order_cap=1000)  # count == cap fails
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.GATE_6_OPEN_ORDER_COUNT


def test_gate7_and_8_normalization() -> None:
    p = _gates(price_normalized_ok=False)
    assert p.code == ArmBlockCode.GATE_7_PRICE_NORMALIZED
    s = _gates(size_normalized_ok=False)
    assert s.code == ArmBlockCode.GATE_8_SIZE_NORMALIZED


def test_gate9_only_active_passes() -> None:
    assert _gates(market_state=OperationalState.ACTIVE).outcome == ArmOutcome.ARMED
    for state in _NON_ACTIVE:
        ev = _gates(market_state=state)
        assert ev.outcome == ArmOutcome.BLOCKED, state
        assert ev.code == ArmBlockCode.GATE_9_MARKET_STATE, state


def test_gate10_edge_floor_strict() -> None:
    assert _gates(net_expected_edge_bps=Decimal("1.01")).outcome == ArmOutcome.ARMED
    ev = _gates(net_expected_edge_bps=Decimal("1"))  # edge == floor fails
    assert ev.outcome == ArmOutcome.BLOCKED and ev.code == ArmBlockCode.GATE_10_EDGE


# --------------------------- R-CORRECTION-SUBSET ---------------------------


def test_entry_disabled_blocks_even_with_gates_passing() -> None:
    ev = _gates(intent=IntentTag.ENTRY_INTENT, generation_disabled=True)
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.DISABLED_GENERATION_BLOCKS_ENTRY


def test_correction_skips_gate9_and_prohibition() -> None:
    # CORRECTION + disabled + FROZEN + gates 1-8/10 passing → ARMED.
    ev = _gates(
        intent=IntentTag.EXPOSURE_CORRECTION_INTENT,
        generation_disabled=True,
        market_state=OperationalState.FROZEN,
        policy=ArmPolicy.SEMI,
    )
    assert ev.outcome == ArmOutcome.ARMED
    assert ev.code is None
    # gate 9 was not evaluated for a correction.
    assert ArmBlockCode.GATE_9_MARKET_STATE.value not in ev.gates


def test_correction_mechanical_gates_still_apply() -> None:
    ev = _gates(
        intent=IntentTag.EXPOSURE_CORRECTION_INTENT,
        order_size=Decimal("0.05"),
        min_order_size=Decimal("0.1"),
    )
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.GATE_3_SIZE


def test_correction_semi_arms_without_wait() -> None:
    ev = _gates(
        intent=IntentTag.EXPOSURE_CORRECTION_INTENT,
        policy=ArmPolicy.SEMI,
        decision=None,
    )
    assert ev.outcome == ArmOutcome.ARMED  # inv.1: no policy wait
    assert ev.code is None


# --------------------------- R-TIMEOUT-FIRST ---------------------------


def test_timeout_none_blocks_all_policies() -> None:
    for policy in (ArmPolicy.AUTO, ArmPolicy.SEMI, ArmPolicy.WEBHOOK):
        ev = _gates(policy=policy, timeout_s=None)
        assert ev.outcome == ArmOutcome.BLOCKED, policy
        assert ev.code == ArmBlockCode.POLICY_ABSENT, policy


# --------------------------- policy / wait ---------------------------


def test_auto_pass_arms() -> None:
    assert _gates(policy=ArmPolicy.AUTO).outcome == ArmOutcome.ARMED


def test_semi_and_webhook_approve_arm() -> None:
    for policy in (ArmPolicy.SEMI, ArmPolicy.WEBHOOK):
        ev = _gates(policy=policy, decision=OperatorDecision.APPROVE)
        assert ev.outcome == ArmOutcome.ARMED, policy
        assert ev.code is None, policy


def test_deny_blocks_with_arm_denied() -> None:
    ev = _gates(policy=ArmPolicy.SEMI, decision=OperatorDecision.DENY)
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.ARM_DENIED


def test_timeout_boundary() -> None:
    expired = _gates(policy=ArmPolicy.SEMI, decision=None, elapsed_s=30, timeout_s=30)
    assert expired.outcome == ArmOutcome.BLOCKED
    assert expired.code == ArmBlockCode.ARM_TIMEOUT
    waiting = _gates(policy=ArmPolicy.SEMI, decision=None, elapsed_s=29, timeout_s=30)
    assert waiting.outcome == ArmOutcome.WAITING
    assert waiting.code is None


def test_webhook_error_blocks() -> None:
    ev = _gates(policy=ArmPolicy.WEBHOOK, decision=None, webhook_error=True)
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.ARM_WEBHOOK_ERROR


def test_evaluate_wait_direct() -> None:
    assert evaluate_wait(
        decision=OperatorDecision.APPROVE, elapsed_s=0, timeout_s=30
    ) == (ArmOutcome.ARMED, None)
    assert evaluate_wait(decision=None, elapsed_s=5, timeout_s=30) == (
        ArmOutcome.WAITING,
        None,
    )


# --------------------------- inv.3: approval never bypasses --------------------


def test_approval_never_bypasses_failed_gate() -> None:
    ev = _gates(
        policy=ArmPolicy.SEMI,
        decision=OperatorDecision.APPROVE,
        order_size=Decimal("0.05"),
        min_order_size=Decimal("0.1"),
    )
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.GATE_3_SIZE


# --------------------------- policy None / bogus ---------------------------


def test_policy_none_blocks_when_gates_pass() -> None:
    ev = _gates(policy=None, timeout_s=30)
    assert ev.outcome == ArmOutcome.BLOCKED
    assert ev.code == ArmBlockCode.POLICY_ABSENT


def test_bogus_policy_string_raises() -> None:
    with pytest.raises(ValueError):
        ArmPolicy("BOGUS")


# --------------------------- B2 classify_intent ---------------------------


def test_classify_shrinking_is_correction_ignoring_reduce_only() -> None:
    for reduce_only in (True, False):
        assert classify_intent(Decimal("10"), Decimal("5"), reduce_only) == (
            IntentTag.EXPOSURE_CORRECTION_INTENT
        )


def test_classify_equal_flat_growing_are_entry() -> None:
    assert (
        classify_intent(Decimal("10"), Decimal("10"), False) == IntentTag.ENTRY_INTENT
    )
    assert classify_intent(Decimal("0"), Decimal("5"), False) == IntentTag.ENTRY_INTENT
    assert classify_intent(Decimal("5"), Decimal("10"), True) == IntentTag.ENTRY_INTENT


def test_classify_full_close_and_opposite_hedge_are_correction() -> None:
    assert classify_intent(Decimal("10"), Decimal("0"), False) == (
        IntentTag.EXPOSURE_CORRECTION_INTENT
    )
    # opposite-direction hedge with reduce_only False (STR-0241): |after| < |before|.
    assert classify_intent(Decimal("5"), Decimal("-2"), False) == (
        IntentTag.EXPOSURE_CORRECTION_INTENT
    )
    # negative-side shrink.
    assert classify_intent(Decimal("-10"), Decimal("-5"), True) == (
        IntentTag.EXPOSURE_CORRECTION_INTENT
    )


# --------------------------- B1 inlet ---------------------------


def _intent(**over: object) -> OrderIntent:
    base: dict[str, object] = {
        "cloid": "c1",
        "target_generation_id": 0,
        "target_cycle_id": 0,
        "target_level_id": 1,
        "target_direction": "BU",
        "order_type": OrderType.LIMIT,
        "requested_size": Decimal("1"),
        "requested_price": Decimal("50000"),
        "intent_tag": IntentTag.ENTRY_INTENT,
        "acute": False,
    }
    base.update(over)
    return construct_order_intent(**base)  # type: ignore[arg-type]


def test_well_formed_intent_has_all_fields() -> None:
    oi = _intent()
    assert oi.cloid == "c1"
    assert oi.target_direction == "BU"
    assert oi.order_type == OrderType.LIMIT
    assert oi.requested_size == Decimal("1")
    assert oi.intent_tag == IntentTag.ENTRY_INTENT
    assert oi.acute is False


def test_malformed_intent_raises() -> None:
    with pytest.raises(ValueError):
        _intent(cloid="")
    with pytest.raises(ValueError):
        _intent(requested_size=Decimal("0"))
    with pytest.raises(ValueError):
        _intent(requested_price=Decimal("-1"))
    with pytest.raises(ValueError):
        _intent(target_direction="LONG")
    with pytest.raises(ValueError):
        _intent(acute=1)  # truthy int, not bool
