"""P1 real: Fix-1 gate + §11.2 hedge urgency/intent + §11.3/§11.4 helpers (7g-3b).

Real P1 (second pass stage). Pure/total/clock-free/Decimal-only; reads State
markers ONLY (envelopes accepted-but-UNREAD); no ST-* reads inside the pure
functions; write-only on ST-07/08/09/ST-23 in ``apply_p1``. No dynamic default is
computed (τ_I, d_emergency, τ_acc are marker parameters); no decimal context is
mutated (the ``q_min`` division runs under the ambient R5 context — 7g-2 precedent).

PINNED READINGS (documented; OCaml parity):

R6 (7g-3a). Classification magnitude bands (independent of is_acute).
R7 (7g-3a). Exposure is direction-signed net (BU +, SL -); only |Δ| enters predicates.
R8 (RULED, deferred). NO ROUNDING SITE in 7g-3b: §11 gives no hedge quantity formula
    (STR-0206/0207 formula: NONE) and orders normalization BEFORE SIGNING (STR-0299,
    adapter, post-7h). The hedge amount is the EXACT residual Δ̂ ∈ {0, Δ} — nothing
    to round. The rounding-DIRECTION question is deferred to order-construction/
    signing; evidence preserved there (round-to-zero STR-0346 + size-bounded-by-|Δ|
    §18/GATE-017 both point toward-zero), not ruled now.

Fix-1 (STR-0345/0346, DECISION-016): the PRE-Fix-1 predicate (|Δ| <= ExposureTolerance)
is the known-broken F-1* dead-band gate and is NEVER implemented as a live gate;
ExposureTolerance survives only as τ_acc INPUT to T_enter/T_exit. STR-0345's T_enter
form governs (STR-0083/0296's tolerance conjunct is read THROUGH Fix-1).

STRICTNESS TABLE:
  round_to_zero:           0 < |Δ| < T_exit  (STRICT both) -> Δ̂ = 0; else Δ exact
  progression_permitted:   |Δ| <= T_enter    (NON-strict, STR-0345 ⟺ / §11.1 diagram)
  is_acute (7g-3a):        |Δ| > τ_I  OR  margin_distance < 2·d_emergency (STRICT both)

Δ̂ HAZARD RULE: is_acute, classify_exposure and progression_permitted ALL take the
RAW Δ. Δ̂ flows ONLY to the ST-23 amount + the P1 audit codes — NEVER into a
predicate, NEVER into ST-09.delta (which is always the raw expected-actual).

§11.3 STOP-ITEM (B2b): the "symmetric formula" (§11.3 L883, STR-0209) is a NAME, not
a formula — a Strategy-wide search of every "symmetric"/"mirror" occurrence found no
formula (only L879/L883/L981 prose). It is NOT invented here; ST-23 mirror-target
fields + the P1 mirror call site arrive WITH that formula in a later phase.
``mirror_eligible`` (the pure §11.3 eligibility predicate) IS implemented, with no
call site in 7g-3b.
"""

from __future__ import annotations

import dataclasses
from decimal import Decimal
from typing import TYPE_CHECKING

from astergrid.core.transitions.exposure import (
    classify_exposure,
    compute_actual_exposure,
    compute_expected_exposure,
    compute_exposure_delta,
    is_acute,
)
from astergrid.core.transitions.exposure_state import (
    ActualExposureState,
    ExpectedExposureState,
    ExposureDeltaState,
)
from astergrid.core.transitions.hedge_state import (
    EPSILON_H,
    HedgeExecution,
    HedgeIntent,
    IntentTag,
    RemainderHedgeStatus,
)
from astergrid.core.transitions.markers import StageReport
from astergrid.core.transitions.reason_codes import ReasonCode

if TYPE_CHECKING:
    from astergrid.core.events import EventEnvelope
    from astergrid.core.state import State
    from astergrid.core.transitions.exposure_state import LevelFillState

_ONE = Decimal("1")
_MIRROR_ELIGIBLE = frozenset({"ACTIVE", "SUCCESSOR_CREATED", "DISABLED_AT_CYCLE_99"})


def _pos(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} must be a Decimal instance")
    if value <= 0:
        raise ValueError(f"{name} must be > 0")


# --------------------------- Fix-1 (STR-0345/0346) ---------------------------


def compute_q_min(*, min_notional_usd: Decimal, mark_price: Decimal) -> Decimal:
    """STR-0345: q_min(M) = MinNotional / M (ambient R5 context; per-market scalar)."""
    _pos(min_notional_usd, "min_notional_usd")
    _pos(mark_price, "mark_price")
    return min_notional_usd / mark_price


def compute_t_enter(*, tau_acc: Decimal, q_min: Decimal) -> Decimal:
    """STR-0345: T_enter = (1 + ε_H) · max(τ_acc, q_min)."""
    _pos(tau_acc, "tau_acc")
    _pos(q_min, "q_min")
    return (_ONE + EPSILON_H) * max(tau_acc, q_min)


def compute_t_exit(*, tau_acc: Decimal, q_min: Decimal) -> Decimal:
    """STR-0345: T_exit = max(τ_acc, q_min)."""
    _pos(tau_acc, "tau_acc")
    _pos(q_min, "q_min")
    return max(tau_acc, q_min)


def round_to_zero(*, exposure_delta: Decimal, t_exit: Decimal) -> Decimal:
    """STR-0346: Δ̂ = 0 iff 0 < |Δ| < T_exit (strict both); else Δ exactly."""
    if not isinstance(exposure_delta, Decimal):
        raise ValueError("exposure_delta must be a Decimal instance")
    _pos(t_exit, "t_exit")
    magnitude = abs(exposure_delta)
    if 0 < magnitude < t_exit:
        return Decimal("0")
    return exposure_delta


def progression_permitted(*, exposure_delta: Decimal, t_enter: Decimal) -> bool:
    """STR-0345: progression permitted ⟺ |Δ| <= T_enter (non-strict)."""
    if not isinstance(exposure_delta, Decimal):
        raise ValueError("exposure_delta must be a Decimal instance")
    _pos(t_enter, "t_enter")
    return abs(exposure_delta) <= t_enter


# --------------------------- §11.2 hedge urgency/intent ---------------------------


def hedge_execution_for(*, acute: bool) -> HedgeExecution:
    """§11.2: acute -> Ioc (STR-0206 unconditional); else -> maker (STR-0207)."""
    if type(acute) is not bool:
        raise ValueError("acute must be a bool")
    return HedgeExecution.IOC if acute else HedgeExecution.PREFER_MAKER


def build_hedge_intent(*, delta_hat: Decimal, acute: bool) -> HedgeIntent:
    """The single HedgeIntent construction site; built even when delta_hat == 0."""
    if not isinstance(delta_hat, Decimal):
        raise ValueError("delta_hat must be a Decimal instance")
    execution = hedge_execution_for(acute=acute)
    return HedgeIntent(
        intent_tag=IntentTag.EXPOSURE_CORRECTION_INTENT,
        amount=delta_hat,
        acute=acute,
        execution=execution,
    )


# --------------------------- §11.3 mirror eligibility ---------------------------


def mirror_eligible(*, lifecycle: str) -> bool:
    """§11.3 (STR-0211): mirroring available for ACTIVE/SUCCESSOR_CREATED/DISABLED.

    Unknown lifecycles -> False (fail-closed). The symmetric trigger/target price
    recomputation is the B2b STOP-item (no formula in Strategy); this predicate has
    no P1 call site in 7g-3b.
    """
    return lifecycle in _MIRROR_ELIGIBLE


# --------------------------- §11.4 remainder tri-state ---------------------------


def classify_remainder_hedge_status(
    *,
    within_timeout: bool,
    skipped: bool,
) -> RemainderHedgeStatus:
    """§11.4: skipped (terminal) -> SKIPPED_RESIDUAL_ZERO; else working/pending."""
    if type(within_timeout) is not bool:
        raise ValueError("within_timeout must be a bool")
    if type(skipped) is not bool:
        raise ValueError("skipped must be a bool")
    if skipped:
        return RemainderHedgeStatus.SKIPPED_RESIDUAL_ZERO
    if within_timeout:
        return RemainderHedgeStatus.WORKING_NOT_YET_EXPOSURE
    return RemainderHedgeStatus.PENDING_EMERGENCY_EXECUTION


# --------------------------- ST-07/08/09 writer (D1) ---------------------------


def build_exposure_singletons(
    *,
    level_fills: tuple[LevelFillState, ...],
    net_position: Decimal,
    normal_tolerance: Decimal,
    transient_tolerance: Decimal,
    max_exposure_imbalance: Decimal,
    margin_distance: Decimal,
    emergency_tolerance: Decimal,
) -> tuple[ExpectedExposureState, ActualExposureState, ExposureDeltaState]:
    """First ST-07/08/09 writer: owns the classification/is_acute coherence contract.

    ST-09.delta is ALWAYS the raw expected-actual (7g-3a coherence is inviolable);
    Δ̂ NEVER enters ST-09. classification == classify_exposure(raw Δ, ...) and
    is_acute == is_acute(raw Δ, ...) by this single site.
    """
    expected = compute_expected_exposure(level_fills=level_fills)
    actual = compute_actual_exposure(net_position=net_position)
    delta = compute_exposure_delta(expected_exposure=expected, actual_exposure=actual)
    classification = classify_exposure(
        exposure_delta=delta,
        normal_tolerance=normal_tolerance,
        transient_tolerance=transient_tolerance,
    )
    acute = is_acute(
        exposure_delta=delta,
        max_exposure_imbalance=max_exposure_imbalance,
        margin_distance=margin_distance,
        emergency_tolerance=emergency_tolerance,
    )
    return (
        ExpectedExposureState(expected),
        ActualExposureState(actual, "clearinghouseState"),
        ExposureDeltaState(
            expected_value=expected,
            actual_value=actual,
            delta=delta,
            classification=classification,
            is_acute=acute,
        ),
    )


# --------------------------- P1 stage (A2) ---------------------------


def apply_p1(
    state: State,
    envelopes: list[EventEnvelope],
) -> tuple[State, StageReport]:
    """Real P1: Fix-1 gate + exposure singletons + HedgeIntent (write-only on state).

    ``envelopes`` is accepted-but-unread (run_pass threading uniformity). Markers
    absent -> NO_OP, state unchanged (7d-compat pin). P1 never reads
    ST-07/08/09/ST-19/ST-02/ST-17; it writes ST-07/08/09/ST-23 only.
    """
    markers = state.p1_exposure_markers
    if markers is None:
        return state, StageReport(
            "P1", "NO_OP", (), "p1 markers absent: no exposure evaluation"
        )

    expected_state, actual_state, delta_state = build_exposure_singletons(
        level_fills=markers.level_fills,
        net_position=markers.net_position,
        normal_tolerance=markers.normal_tolerance,
        transient_tolerance=markers.transient_tolerance,
        max_exposure_imbalance=markers.max_exposure_imbalance,
        margin_distance=markers.margin_distance,
        emergency_tolerance=markers.emergency_tolerance,
    )
    raw_delta = delta_state.delta  # raw Δ — never Δ̂

    q_min = compute_q_min(
        min_notional_usd=markers.min_notional_usd, mark_price=markers.mark_price
    )
    t_enter = compute_t_enter(tau_acc=markers.tau_acc, q_min=q_min)
    t_exit = compute_t_exit(tau_acc=markers.tau_acc, q_min=q_min)
    permitted = progression_permitted(exposure_delta=raw_delta, t_enter=t_enter)
    delta_hat = round_to_zero(exposure_delta=raw_delta, t_exit=t_exit)
    acute = delta_state.is_acute
    intent = build_hedge_intent(delta_hat=delta_hat, acute=acute)

    zeroed = delta_hat == 0 and raw_delta != 0
    codes: list[str] = [
        (
            ReasonCode.PROGRESSION_PERMITTED.value
            if permitted
            else ReasonCode.PROGRESSION_BLOCKED.value
        )
    ]
    if zeroed:
        codes.append(ReasonCode.FIX1_RESIDUAL_ZEROED.value)
    codes.append(
        ReasonCode.HEDGE_IMMEDIATE_IOC.value
        if acute
        else ReasonCode.HEDGE_DEFERRED_TO_SECTION_10.value
    )

    note = (
        f"p1 gate={'PERMITTED' if permitted else 'BLOCKED'} "
        f"zeroed={'true' if zeroed else 'false'} "
        f"urgency={'IMMEDIATE_IOC' if acute else 'DEFERRED_10'}"
    )
    new_state = dataclasses.replace(
        state,
        st07_expected_exposure=expected_state,
        st08_actual_exposure=actual_state,
        st09_exposure_delta=delta_state,
        st23_mirror_targets_hedge_intents=intent,
    )
    return new_state, StageReport("P1", "APPLIED", tuple(codes), note)
