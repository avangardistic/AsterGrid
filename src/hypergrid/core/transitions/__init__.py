"""hypergrid.core.transitions — §4.7 deterministic arbitration (Phase 7d).

Real P2 (locks), P3 (same-generation conflict) and P4 (across-generation
precedence) plus the shared marker/decision/report dataclasses and the
centralized reason codes. Pure, stdlib-only, no domain logic beyond §4.7
ordering; no envelope-content interpretation.
"""

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
    "P2Attempts",
    "P2LocksState",
    "P3CandidateMarkers",
    "P4CandidateMarkers",
    "P4Decision",
    "ReasonCode",
    "StageReport",
    "apply_across_generation_precedence",
    "apply_locks",
    "apply_same_generation_precedence",
]
