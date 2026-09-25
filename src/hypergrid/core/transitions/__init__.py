"""hypergrid.core.transitions — §4.7 deterministic arbitration (Phase 7d).

Real P2 (locks), P3 (same-generation conflict) and P4 (across-generation
precedence) plus the shared marker/decision/report dataclasses and the
centralized reason codes. Pure, stdlib-only, no domain logic beyond §4.7
ordering; no envelope-content interpretation.
"""

from hypergrid.core.transitions.cycle import apply_cycle
from hypergrid.core.transitions.cycle_state import (
    CycleState,
    CycleTerminalMarkers,
    NonOverlapData,
    ReferencePriceRecord,
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
from hypergrid.core.transitions.level_state import LevelState
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
from hypergrid.core.transitions.precedence import (
    apply_across_generation_precedence,
    apply_same_generation_precedence,
)
from hypergrid.core.transitions.protection_lock import (
    apply_protection_unlock,
    is_protection_locked_initial,
)
from hypergrid.core.transitions.reason_codes import ReasonCode
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

__all__ = [
    "EPSILON_H",
    "ActualExposureState",
    "CycleState",
    "CycleTerminalMarkers",
    "DominanceFlag",
    "EvolutionCandidateWindow",
    "ExpectedExposureState",
    "ExposureClass",
    "ExposureDeltaState",
    "GenerationState",
    "HedgeExecution",
    "HedgeIntent",
    "IntentTag",
    "LevelFillState",
    "LevelState",
    "MarketObservationState",
    "NonOverlapData",
    "P0ObservationMarkers",
    "P1ExposureMarkers",
    "P2Attempts",
    "P2LocksState",
    "P3CandidateMarkers",
    "P4CandidateMarkers",
    "P4Decision",
    "PerLevelObservation",
    "ReasonCode",
    "ReferencePriceRecord",
    "RemainderHedgeStatus",
    "StageReport",
    "SuccessorLock",
    "apply_across_generation_precedence",
    "apply_cycle",
    "apply_evolution",
    "apply_locks",
    "apply_p0",
    "apply_p1",
    "apply_protection_unlock",
    "apply_same_generation_precedence",
    "assign_level_notionals",
    "build_exposure_singletons",
    "build_hedge_intent",
    "classify_exposure",
    "classify_remainder_hedge_status",
    "compute_actual_exposure",
    "compute_expected_exposure",
    "compute_exposure_delta",
    "compute_ladder_geometry",
    "compute_max_cycle_notional",
    "compute_max_generation_notional",
    "compute_max_level_notional",
    "compute_max_level_notional_dominant",
    "compute_q_min",
    "compute_t_enter",
    "compute_t_exit",
    "convert_notional_to_size",
    "count_active_cycles",
    "count_active_generations",
    "enforce_level_caps",
    "extend_level_states",
    "hedge_execution_for",
    "is_acute",
    "is_protection_locked_initial",
    "mirror_eligible",
    "progression_permitted",
    "project_p1_markers",
    "round_to_zero",
]
