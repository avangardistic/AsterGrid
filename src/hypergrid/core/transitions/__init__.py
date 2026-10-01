"""hypergrid.core.transitions — §4.7 deterministic arbitration (Phase 7d).

Real P2 (locks), P3 (same-generation conflict) and P4 (across-generation
precedence) plus the shared marker/decision/report dataclasses and the
centralized reason codes. Pure, stdlib-only, no domain logic beyond §4.7
ordering; no envelope-content interpretation.
"""

from hypergrid.core.transitions.arm import (
    ARM_TIMEOUT_S,
    DISTANCE_BAND,
    EDGE_FLOOR_BPS,
    MARGIN_BUFFER_MULT,
    MIN_DEPTH_MULTIPLE,
    OPEN_ORDER_CAP,
    ArmEvaluation,
    GateResult,
    evaluate_arm_gates,
    evaluate_wait,
)
from hypergrid.core.transitions.arm_state import (
    ArmBlockCode,
    ArmOutcome,
    ArmPolicy,
    ArmRequestState,
    OperationalState,
    OperatorDecision,
    expire_on_restart,
    is_legal_arm_transition,
    supersede_request,
)
from hypergrid.core.transitions.cycle import apply_cycle
from hypergrid.core.transitions.cycle_state import (
    CycleState,
    CycleTerminalMarkers,
    NonOverlapData,
    ReferencePriceRecord,
)
from hypergrid.core.transitions.economics import (
    PathEconomicsVerdict,
    check_arming_validity,
    classify_path_economics,
    compute_gross_grid_edge,
    compute_net_expected_edge,
)
from hypergrid.core.transitions.emergency import (
    EMERGENCY_BOUNDED_WAIT_S,
    EmergencyEvaluation,
    EmergencyVerdict,
    compute_emergency_tolerance_bps,
    evaluate_emergency,
)
from hypergrid.core.transitions.execution_cancel import (
    CancelCandidate,
    CancelReasonCode,
    emit_cancel_command,
    select_exhausted_candidates,
)
from hypergrid.core.transitions.exposure import (
    classify_exposure,
    compute_actual_exposure,
    compute_expected_exposure,
    compute_exposure_delta,
    is_acute,
)
from hypergrid.core.transitions.exposure_state import (
    ActualExposureState,
    ExpectedExposureState,
    ExposureClass,
    ExposureDeltaState,
    LevelFillState,
)
from hypergrid.core.transitions.generation import apply_evolution
from hypergrid.core.transitions.generation_state import (
    DominanceFlag,
    EvolutionCandidateWindow,
    GenerationState,
    SuccessorLock,
)
from hypergrid.core.transitions.geometry import compute_ladder_geometry
from hypergrid.core.transitions.hedge import (
    apply_p1,
    build_exposure_singletons,
    build_hedge_intent,
    classify_remainder_hedge_status,
    compute_q_min,
    compute_t_enter,
    compute_t_exit,
    hedge_execution_for,
    mirror_eligible,
    progression_permitted,
    round_to_zero,
)
from hypergrid.core.transitions.hedge_state import (
    EPSILON_H,
    HedgeExecution,
    HedgeIntent,
    IntentTag,
    P1ExposureMarkers,
    RemainderHedgeStatus,
)
from hypergrid.core.transitions.ladder_issuance import issue_fresh_ladder
from hypergrid.core.transitions.level_state import LevelState, can_level_skip
from hypergrid.core.transitions.locks import apply_locks
from hypergrid.core.transitions.markers import (
    P2Attempts,
    P2LocksState,
    P3CandidateMarkers,
    P4CandidateMarkers,
    P4Decision,
    StageReport,
)
from hypergrid.core.transitions.market_observation_state import (
    MarketObservationState,
)
from hypergrid.core.transitions.observation import (
    apply_p0,
    extend_level_states,
    project_p1_markers,
)
from hypergrid.core.transitions.observation_state import (
    P0ObservationMarkers,
    PerLevelObservation,
)
from hypergrid.core.transitions.order_state import (
    OrderIntent,
    OrderState,
    OrderType,
    classify_intent,
    construct_order_intent,
    is_legal_order_transition,
)
from hypergrid.core.transitions.p6_stage import apply_p6
from hypergrid.core.transitions.p6_state import (
    P6ArmInput,
    P6CancelInput,
    P6IssuanceInput,
)
from hypergrid.core.transitions.pass_report_ext import SubDecisionRecord
from hypergrid.core.transitions.pipeline_coupling import apply_pipeline_coupling
from hypergrid.core.transitions.precedence import (
    apply_across_generation_precedence,
    apply_same_generation_precedence,
)
from hypergrid.core.transitions.protection_lock import (
    apply_protection_unlock,
    is_protection_locked_initial,
)
from hypergrid.core.transitions.reason_codes import ReasonCode
from hypergrid.core.transitions.remainder import RemainderState, track_remainder
from hypergrid.core.transitions.risk_bounds import (
    BreachLayer,
    RiskReasonCode,
    apply_breach_response,
    compute_max_execution_cost_pnl_regime,
    compute_max_exposure_imbalance_qty,
    compute_max_failed_level_rate,
    compute_max_hedge_cost,
    compute_max_range_induced_dd_pct,
)
from hypergrid.core.transitions.risk_state import (
    AccountEquityState,
    BasketNetPnLState,
    BoundLayerState,
    FreezeErrorRecoveryOverlayState,
    RiskBoundTrackerState,
)
from hypergrid.core.transitions.sizing import (
    assign_level_notionals,
    compute_max_cycle_notional,
    compute_max_generation_notional,
    compute_max_level_notional,
    compute_max_level_notional_dominant,
    convert_notional_to_size,
    count_active_cycles,
    count_active_generations,
    enforce_level_caps,
)
from hypergrid.core.transitions.submission import (
    SubmissionResult,
    emit_submission_command,
    submit_order,
)

__all__ = [
    "ARM_TIMEOUT_S",
    "DISTANCE_BAND",
    "EDGE_FLOOR_BPS",
    "EMERGENCY_BOUNDED_WAIT_S",
    "EPSILON_H",
    "MARGIN_BUFFER_MULT",
    "MIN_DEPTH_MULTIPLE",
    "OPEN_ORDER_CAP",
    "AccountEquityState",
    "ActualExposureState",
    "ArmBlockCode",
    "ArmEvaluation",
    "ArmOutcome",
    "ArmPolicy",
    "ArmRequestState",
    "BasketNetPnLState",
    "BoundLayerState",
    "BreachLayer",
    "CancelCandidate",
    "CancelReasonCode",
    "CycleState",
    "CycleTerminalMarkers",
    "DominanceFlag",
    "EmergencyEvaluation",
    "EmergencyVerdict",
    "EvolutionCandidateWindow",
    "ExpectedExposureState",
    "ExposureClass",
    "ExposureDeltaState",
    "FreezeErrorRecoveryOverlayState",
    "GateResult",
    "GenerationState",
    "HedgeExecution",
    "HedgeIntent",
    "IntentTag",
    "LevelFillState",
    "LevelState",
    "MarketObservationState",
    "NonOverlapData",
    "OperationalState",
    "OperatorDecision",
    "OrderIntent",
    "OrderState",
    "OrderType",
    "P0ObservationMarkers",
    "P1ExposureMarkers",
    "P2Attempts",
    "P2LocksState",
    "P3CandidateMarkers",
    "P4CandidateMarkers",
    "P4Decision",
    "P6ArmInput",
    "P6CancelInput",
    "P6IssuanceInput",
    "PathEconomicsVerdict",
    "PerLevelObservation",
    "ReasonCode",
    "ReferencePriceRecord",
    "RemainderHedgeStatus",
    "RemainderState",
    "RiskBoundTrackerState",
    "RiskReasonCode",
    "StageReport",
    "SubDecisionRecord",
    "SubmissionResult",
    "SuccessorLock",
    "apply_across_generation_precedence",
    "apply_breach_response",
    "apply_cycle",
    "apply_evolution",
    "apply_locks",
    "apply_p0",
    "apply_p1",
    "apply_p6",
    "apply_pipeline_coupling",
    "apply_protection_unlock",
    "apply_same_generation_precedence",
    "assign_level_notionals",
    "build_exposure_singletons",
    "build_hedge_intent",
    "can_level_skip",
    "check_arming_validity",
    "classify_exposure",
    "classify_intent",
    "classify_path_economics",
    "classify_remainder_hedge_status",
    "compute_actual_exposure",
    "compute_emergency_tolerance_bps",
    "compute_expected_exposure",
    "compute_exposure_delta",
    "compute_gross_grid_edge",
    "compute_ladder_geometry",
    "compute_max_cycle_notional",
    "compute_max_execution_cost_pnl_regime",
    "compute_max_exposure_imbalance_qty",
    "compute_max_failed_level_rate",
    "compute_max_generation_notional",
    "compute_max_hedge_cost",
    "compute_max_level_notional",
    "compute_max_level_notional_dominant",
    "compute_max_range_induced_dd_pct",
    "compute_net_expected_edge",
    "compute_q_min",
    "compute_t_enter",
    "compute_t_exit",
    "construct_order_intent",
    "convert_notional_to_size",
    "count_active_cycles",
    "count_active_generations",
    "emit_cancel_command",
    "emit_submission_command",
    "enforce_level_caps",
    "evaluate_arm_gates",
    "evaluate_emergency",
    "evaluate_wait",
    "expire_on_restart",
    "extend_level_states",
    "hedge_execution_for",
    "is_acute",
    "is_legal_arm_transition",
    "is_legal_order_transition",
    "is_protection_locked_initial",
    "issue_fresh_ladder",
    "mirror_eligible",
    "progression_permitted",
    "project_p1_markers",
    "round_to_zero",
    "select_exhausted_candidates",
    "submit_order",
    "supersede_request",
    "track_remainder",
]
