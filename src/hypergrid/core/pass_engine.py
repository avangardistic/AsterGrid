"""The P0-P6 pass engine (Phase 7d).

``run_pass`` runs the §4.7 stages in strict P0..P6 order over one pass. Phase 7d
implements the deterministic ordering substrate only:

  P0  POSITION VERIFICATION & RECONCILIATION      — STUB (§11.1, Phase 7e)
  P1  RISK/EXPOSURE PROTECTION & HEDGE RECOVERY    — STUB (§11.1/§11.2, later)
  P2  LOCKS                                        — REAL (transitions.locks)
  P3  SAME-GENERATION CONFLICT                     — REAL (transitions.precedence)
  P4  ACROSS-GEN PRECEDENCE + EVOLUTION EXECUTION  — REAL (precedence + generation)
  P5  CYCLE TRANSITIONS                            — REAL (transitions.cycle)
  P6  LEVEL ARMING / ORDER PLACEMENT               — STUB (later)

Strategy.md §4.7 defines seven passes, P0 through P6; ``run_pass`` therefore
returns exactly seven StageReports (one per pass), in order. Stubs pass the state
through unchanged and report ``status="STUBBED"``; they read no event content
beyond the envelope count. The real stages read ONLY the state's marker fields
(never envelope/event content — Phase-7d DESIGN RULE).

``run_pass`` is pure, total, clock-free and deterministic: the same
``(state, envelopes)`` yields the same ``(state', report)``, and the canonical
JSON of the returned State is byte-identical across runs. The input iterable is
materialized once (``list(...)``) so it is never consumed twice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from hypergrid.core.transitions.cycle import apply_cycle
from hypergrid.core.transitions.generation import apply_evolution
from hypergrid.core.transitions.locks import apply_locks
from hypergrid.core.transitions.markers import StageReport
from hypergrid.core.transitions.precedence import (
    apply_across_generation_precedence,
    apply_same_generation_precedence,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from hypergrid.core.events import EventEnvelope
    from hypergrid.core.state import State


@dataclass(frozen=True, slots=True)
class PassReport:
    """The result of one pass: exactly seven StageReports in P0..P6 order."""

    stages: tuple[StageReport, ...]

    def to_canonical_obj(self) -> dict[str, object]:
        return {"stages": [stage.to_canonical_obj() for stage in self.stages]}


def _stub(stage: str) -> StageReport:
    """A pass-through stub stage: state unchanged, no event-content read."""
    return StageReport(
        stage=stage,
        status="STUBBED",
        reason_codes=(),
        notes=f"{stage} stub: no-op in Phase 7d",
    )


def _combine_p4(arbitration: StageReport, execution: StageReport) -> StageReport:
    """Merge the P4 arbitration (7d) and evolution-execution (7e) sub-reports.

    §4.7 P4's own text orders AND executes evolutions before Cycle transitions, so
    P4 is the home of evolution execution — no vocabulary beyond P0..P6 ever enters
    reports (OCaml compares these strings in a later phase). The combined report:
    codes = arbitration codes then execution codes; status APPLIED iff either
    sub-step applied; notes = the arbitration note plus an execution suffix ONLY
    when the execution sub-step did observable work. 7d-COMPATIBILITY PIN: when the
    generation markers are absent the execution sub-step is NO_OP with empty
    codes/note, so this returns a P4 report byte-identical to the Phase-7d one.
    """
    codes = tuple(arbitration.reason_codes) + tuple(execution.reason_codes)
    applied = arbitration.status == "APPLIED" or execution.status == "APPLIED"
    notes = arbitration.notes
    if execution.status == "APPLIED" and execution.notes:
        notes = f"{notes}; {execution.notes}"
    return StageReport("P4", "APPLIED" if applied else "NO_OP", codes, notes)


def run_pass(
    state: State,
    envelopes: Iterable[EventEnvelope],
) -> tuple[State, PassReport]:
    """Run P0..P6 over one pass; return (new state, pass report)."""
    materialized = list(envelopes)  # total-iteration guarantee: consume once

    stages: list[StageReport] = []
    stages.append(_stub("P0"))
    stages.append(_stub("P1"))

    state, p2 = apply_locks(state, materialized)
    stages.append(p2)
    state, p3 = apply_same_generation_precedence(state, materialized)
    stages.append(p3)
    # P4 is a composition over the same state thread: FIRST the 7d across-gen
    # arbitration, THEN the 7e evolution execution (§4.7 P4 executes evolutions
    # here). No new stage is introduced — the report is still named "P4".
    state, p4_arbitration = apply_across_generation_precedence(state, materialized)
    state, p4_execution = apply_evolution(state, materialized)
    stages.append(_combine_p4(p4_arbitration, p4_execution))

    # P5 is real (Phase 7f): the §5 Cycle transition, threaded after P4 so §4.7's
    # P4-before-P5 holds by construction. Still exactly stage "P5" (no P5_EXEC).
    state, p5 = apply_cycle(state, materialized)
    stages.append(p5)
    stages.append(_stub("P6"))

    return state, PassReport(stages=tuple(stages))
