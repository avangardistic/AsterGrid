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
from hypergrid.core.transitions.generation import apply_evolution
from hypergrid.core.transitions.generation_state import (
    DominanceFlag,
    EvolutionCandidateWindow,
    GenerationState,
    SuccessorLock,
)
from hypergrid.core.transitions.geometry import compute_ladder_geometry
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
    "CycleState",
    "CycleTerminalMarkers",
    "DominanceFlag",
    "EvolutionCandidateWindow",
    "GenerationState",
    "LevelState",
    "NonOverlapData",
    "P2Attempts",
    "P2LocksState",
    "P3CandidateMarkers",
    "P4CandidateMarkers",
    "P4Decision",
    "ReasonCode",
    "ReferencePriceRecord",
    "StageReport",
    "SuccessorLock",
    "apply_across_generation_precedence",
    "apply_cycle",
    "apply_evolution",
    "apply_locks",
    "apply_protection_unlock",
    "apply_same_generation_precedence",
    "assign_level_notionals",
    "compute_ladder_geometry",
    "compute_max_cycle_notional",
    "compute_max_generation_notional",
    "compute_max_level_notional",
    "compute_max_level_notional_dominant",
    "convert_notional_to_size",
    "count_active_cycles",
    "count_active_generations",
    "enforce_level_caps",
    "is_protection_locked_initial",
]
