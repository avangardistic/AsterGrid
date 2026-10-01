"""§8 arm-gate evaluation (Phase 7h-2): the 10 gates + generation rule + policy wait.

Pure, total, clock-free, no I/O. Imports the stdlib, ``hedge_state.IntentTag``, and
the ``arm_state`` vocabulary leaf (one-way — ``arm_state`` never imports ``arm``).
It MUST NOT import ``core.state`` or ``core.pass_engine``.

Pinned reconciliations (Owner-decided; do not re-argue — see the phase prompt B3):
  * R-TIMEOUT-FIRST (inv.5, §8 L734): ``timeout_s is None`` blocks ALL policies
    (incl. AUTO), checked FIRST.
  * R-CORRECTION-SUBSET (inv.1 x STR-0180, §8 L730/L758-759): a CORRECTION is exempt
    from gate 9 (FREEZE) and the DISABLED-generation prohibition, passes gates
    {1-8,10}, and arms immediately with NO policy wait.
  * Deny → BLOCKED + ARM_DENIED (STR-0165); timeout → ARM_TIMEOUT (§8 L726);
    webhook error → ARM_WEBHOOK_ERROR (STR-0166 outcome-convergence, cause-split).
  * inv.3 (§8 L732): gates evaluate BEFORE any approval is honored.

D-09 Group D defaults live here as module constants (CALIBRATABLE per §14 L1178;
7h-4's config surface reuses, never redefines). ``ARM_TIMEOUT_S`` cites D-10 FIXED.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from astergrid.core.transitions.arm_state import (
    ArmBlockCode,
    ArmOutcome,
    ArmPolicy,
    OperationalState,
    OperatorDecision,
)
from astergrid.core.transitions.hedge_state import IntentTag

# --- §14 D-09 Group D defaults (§8 arm gates); CALIBRATABLE per §14 L1178; 7h-4's
# config surface reuses, never redefines. ---
MIN_DEPTH_MULTIPLE = 10  # §8 gate 1 L737-738 (MinDepthMultiple, D-09 Group D)
DISTANCE_BAND = (5, 100)  # §8 gate 2 L739-741 (DistanceBand bps, D-09 Group D)
MARGIN_BUFFER_MULT = Decimal("0.20")  # §8 gate 4 L743-744 (MarginSafetyBuffer, D-09 D)
OPEN_ORDER_CAP = 1000  # §8 gate 6 L746-749 (per-account cap [HC], D-09 Group D)
EDGE_FLOOR_BPS = Decimal("1")  # §8 gate 10 L752-754 (NetExpectedEdgeFloor, D-09 D)
# --- §14 D-10 FIXED (policy + timeout). ---
ARM_TIMEOUT_S = 30  # §8 L725 ArmRequestTimeoutSeconds (D-10 FIXED)


@dataclass(frozen=True, slots=True)
class GateResult:
    """One §8 gate's outcome."""

    gate: str  # the gate's ArmBlockCode value (e.g. "GATE_1_DEPTH")
    passed: bool

    def to_canonical_obj(self) -> dict[str, object]:
        return {"gate": self.gate, "passed": self.passed}


@dataclass(frozen=True, slots=True)
class ArmEvaluation:
    """The ``evaluate_arm_gates`` result: outcome + block cause + per-gate results."""

    outcome: ArmOutcome
    code: ArmBlockCode | None  # the BLOCKED cause, or None when ARMED/WAITING
    gates: dict[str, GateResult]  # gate value → result (empty for pre-gate blocks)

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "outcome": self.outcome.value,
            "gates": {k: v.to_canonical_obj() for k, v in self.gates.items()},
        }
        if self.code is not None:  # R-JSON-6: omit absent optional
            obj["code"] = self.code.value
        return obj


def evaluate_wait(
    *,
    decision: OperatorDecision | None,
    elapsed_s: int,
    timeout_s: int,
    webhook_error: bool = False,
) -> tuple[ArmOutcome, ArmBlockCode | None]:
    """SEMI/WEBHOOK approval-wait verdict (B3). Clock-free: ``elapsed_s`` is a param.

    APPROVE → ARMED; DENY → BLOCKED+ARM_DENIED; None+webhook_error →
    BLOCKED+ARM_WEBHOOK_ERROR; None+``elapsed_s >= timeout_s`` → BLOCKED+ARM_TIMEOUT
    (boundary ``elapsed == timeout`` has expired); else WAITING. No sleeping/I/O/clock.
    """
    if decision == OperatorDecision.APPROVE:
        return (ArmOutcome.ARMED, None)
    if decision == OperatorDecision.DENY:
        return (ArmOutcome.BLOCKED, ArmBlockCode.ARM_DENIED)
    if webhook_error:
        return (ArmOutcome.BLOCKED, ArmBlockCode.ARM_WEBHOOK_ERROR)
    if elapsed_s >= timeout_s:
        return (ArmOutcome.BLOCKED, ArmBlockCode.ARM_TIMEOUT)
    return (ArmOutcome.WAITING, None)


def evaluate_arm_gates(
    *,
    intent: IntentTag,
    generation_disabled: bool,
    book_depth_at_target: Decimal,
    order_size: Decimal,
    min_depth_multiple: int = MIN_DEPTH_MULTIPLE,
    distance_bps: int,
    distance_band: tuple[int, int] = DISTANCE_BAND,
    min_order_size: Decimal,
    margin_available: Decimal,
    margin_required: Decimal,
    margin_buffer_mult: Decimal = MARGIN_BUFFER_MULT,
    exposure_caps_ok: bool,
    open_order_count: int,
    open_order_cap: int = OPEN_ORDER_CAP,
    price_normalized_ok: bool,
    size_normalized_ok: bool,
    market_state: OperationalState,
    net_expected_edge_bps: Decimal,
    edge_floor_bps: Decimal = EDGE_FLOOR_BPS,
    policy: ArmPolicy | None,
    timeout_s: int | None,
    decision: OperatorDecision | None = None,
    decision_by: str | None = None,
    elapsed_s: int = 0,
    webhook_error: bool = False,
) -> ArmEvaluation:
    """Evaluate the §8 arm gates + generation rule + policy routing (B3).

    Order (normative): (0) ``timeout_s is None`` → BLOCKED+POLICY_ABSENT for ALL
    policies (R-TIMEOUT-FIRST); (1) ENTRY+disabled → BLOCKED+
    DISABLED_GENERATION_BLOCKS_ENTRY (STR-0180); (2) gate subset (ENTRY→all 10,
    CORRECTION→{1-8,10}) — first failure → BLOCKED+GATE_* (inv.3: before any
    approval); (3) passed: CORRECTION → ARMED (inv.1, no policy); ENTRY+AUTO → ARMED;
    ENTRY+SEMI/WEBHOOK → ``evaluate_wait``; (4) passed + ``policy is None`` →
    BLOCKED+POLICY_ABSENT. ``decision_by`` is carried for the ST-12 inv.4 record; the
    pure verdict here uses ``decision`` only.
    """
    _ = decision_by  # inv.4 record identity — attached by the ST-12 machine, not here
    # (0) R-TIMEOUT-FIRST — literal inv.5, before everything, all policies.
    if timeout_s is None:
        return ArmEvaluation(ArmOutcome.BLOCKED, ArmBlockCode.POLICY_ABSENT, {})

    is_entry = intent == IntentTag.ENTRY_INTENT
    # (1) DISABLED-generation prohibition — ENTRY only (correction exempt, STR-0180).
    if is_entry and generation_disabled:
        return ArmEvaluation(
            ArmOutcome.BLOCKED, ArmBlockCode.DISABLED_GENERATION_BLOCKS_ENTRY, {}
        )

    # (2) gate subset (numeric order); CORRECTION skips gate 9 (R-CORRECTION-SUBSET).
    required_plus_buffer = margin_required + margin_buffer_mult * margin_required
    specs: list[tuple[ArmBlockCode, bool]] = [
        (
            ArmBlockCode.GATE_1_DEPTH,
            book_depth_at_target >= min_depth_multiple * order_size,
        ),
        (
            ArmBlockCode.GATE_2_DISTANCE,
            distance_band[0] <= distance_bps <= distance_band[1],
        ),
        (ArmBlockCode.GATE_3_SIZE, order_size >= min_order_size),
        (ArmBlockCode.GATE_4_MARGIN, margin_available >= required_plus_buffer),
        (ArmBlockCode.GATE_5_EXPOSURE_CAPS, exposure_caps_ok),
        (ArmBlockCode.GATE_6_OPEN_ORDER_COUNT, open_order_count < open_order_cap),
        (ArmBlockCode.GATE_7_PRICE_NORMALIZED, price_normalized_ok),
        (ArmBlockCode.GATE_8_SIZE_NORMALIZED, size_normalized_ok),
        (ArmBlockCode.GATE_9_MARKET_STATE, market_state == OperationalState.ACTIVE),
        (ArmBlockCode.GATE_10_EDGE, net_expected_edge_bps > edge_floor_bps),
    ]
    if not is_entry:  # CORRECTION: skip gate 9 (FREEZE exemption, inv.1)
        specs = [s for s in specs if s[0] is not ArmBlockCode.GATE_9_MARKET_STATE]

    gates: dict[str, GateResult] = {}
    first_fail: ArmBlockCode | None = None
    for code, passed in specs:
        gates[code.value] = GateResult(code.value, bool(passed))
        if not passed and first_fail is None:
            first_fail = code
    if first_fail is not None:
        return ArmEvaluation(ArmOutcome.BLOCKED, first_fail, gates)

    # (3) gates passed.
    if intent == IntentTag.EXPOSURE_CORRECTION_INTENT:
        return ArmEvaluation(
            ArmOutcome.ARMED, None, gates
        )  # inv.1: no policy consulted
    if policy is None:  # (4) ENTRY + passed + no policy → fail-closed.
        return ArmEvaluation(ArmOutcome.BLOCKED, ArmBlockCode.POLICY_ABSENT, gates)
    if policy == ArmPolicy.AUTO:
        return ArmEvaluation(
            ArmOutcome.ARMED, None, gates
        )  # STR-0164 MAY-as-permission
    # ENTRY + SEMI/WEBHOOK → approval wait (inv.3: gates already passed).
    wait_outcome, wait_code = evaluate_wait(
        decision=decision,
        elapsed_s=elapsed_s,
        timeout_s=timeout_s,
        webhook_error=webhook_error,
    )
    return ArmEvaluation(wait_outcome, wait_code, gates)


__all__ = [
    "ARM_TIMEOUT_S",
    "DISTANCE_BAND",
    "EDGE_FLOOR_BPS",
    "MARGIN_BUFFER_MULT",
    "MIN_DEPTH_MULTIPLE",
    "OPEN_ORDER_CAP",
    "ArmEvaluation",
    "GateResult",
    "evaluate_arm_gates",
    "evaluate_wait",
]
