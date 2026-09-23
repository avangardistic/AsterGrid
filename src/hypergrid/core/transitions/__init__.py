"""hypergrid.core.transitions — §4.7 deterministic arbitration (Phase 7d).

Real P2 (locks), P3 (same-generation conflict) and P4 (across-generation
precedence) plus the shared marker/decision/report dataclasses and the
centralized reason codes. Pure, stdlib-only, no domain logic beyond §4.7
ordering; no envelope-content interpretation.
"""

from hypergrid.core.transitions.generation import apply_evolution
from hypergrid.core.transitions.generation_state import (
    DominanceFlag,
    EvolutionCandidateWindow,
    GenerationState,
    SuccessorLock,
)
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
from hypergrid.core.transitions.reason_codes import ReasonCode

__all__ = [
    "DominanceFlag",
    "EvolutionCandidateWindow",
    "GenerationState",
    "P2Attempts",
    "P2LocksState",
    "P3CandidateMarkers",
    "P4CandidateMarkers",
    "P4Decision",
    "ReasonCode",
    "StageReport",
    "SuccessorLock",
    "apply_across_generation_precedence",
    "apply_evolution",
    "apply_locks",
    "apply_same_generation_precedence",
]
