"""The P0-P6 pass engine (Phase 7d).

``run_pass`` runs the §4.7 stages in strict P0..P6 order over one pass. Phase 7d
implements the deterministic ordering substrate only:

  P0  POSITION VERIFICATION & RECONCILIATION      — REAL (§6.1 + ST-04/ST-19, 7h-1)
  P1  RISK/EXPOSURE PROTECTION & HEDGE RECOVERY    — REAL (§11.1/§11.2, hedge)
  P2  LOCKS                                        — REAL (transitions.locks)
  P3  SAME-GENERATION CONFLICT                     — REAL (transitions.precedence)
  P4  ACROSS-GEN PRECEDENCE + EVOLUTION EXECUTION  — REAL (precedence + generation)
  P5  CYCLE TRANSITIONS                            — REAL (transitions.cycle)
  P6  LEVEL ARMING / ORDER PLACEMENT               — REAL (transitions.p6_stage)

Strategy.md §4.7 defines seven passes, P0 through P6; ``run_pass`` therefore
returns exactly seven StageReports (one per pass), in order. All seven stages are
real; the real stages read ONLY the state's marker fields (never envelope/event
content — Phase-7d DESIGN RULE).

``run_pass`` is pure, total, clock-free and deterministic: the same
``(state, envelopes)`` yields the same ``(state', report, emitted)``, and the
canonical JSON of the returned State is byte-identical across runs. The input
iterable is materialized once (``list(...)``) so it is never consumed twice. The
third element is P6's emitted CommandEvents (sorted by (sub_kind_order, cloid);
CANCEL_SELECT=0, SUBMISSION_EMIT=1) — no log-port import lives here (D11).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from astergrid.core.transitions.cycle import apply_cycle
from astergrid.core.transitions.generation import apply_evolution
from astergrid.core.transitions.hedge import apply_p1
from astergrid.core.transitions.locks import apply_locks
from astergrid.core.transitions.markers import StageReport
from astergrid.core.transitions.observation import apply_p0
from astergrid.core.transitions.p6_stage import apply_p6
from astergrid.core.transitions.pass_report_ext import SubDecisionRecord
from astergrid.core.transitions.precedence import (
    apply_across_generation_precedence,
    apply_same_generation_precedence,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from astergrid.core.events import CommandEvent, EventEnvelope
    from astergrid.core.state import State


@dataclass(frozen=True, slots=True)
class PassReport:
    """One pass: seven StageReports (P0..P6) + P6's traced sub-decisions."""

    stages: tuple[StageReport, ...]
    sub_decisions: tuple[SubDecisionRecord, ...] = ()

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "stages": [stage.to_canonical_obj() for stage in self.stages],
            "sub_decisions": [r.to_canonical_obj() for r in self.sub_decisions],
        }


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
) -> tuple[State, PassReport, tuple[CommandEvent, ...]]:
    """Run P0..P6 over one pass; return (new state, pass report, emitted commands)."""
    materialized = list(envelopes)  # total-iteration guarantee: consume once

    stages: list[StageReport] = []
    # P0 is real (Phase 7h-1): §6.1 observation recording into ST-04 (fill/lifecycle)
    # + ST-19, and projection of p1_exposure_markers for P1. Markers-fed, envelopes
    # unread, write-only. Still exactly stage "P0" in first position.
    state, p0 = apply_p0(state, materialized)
    stages.append(p0)
    # P1 is real (Phase 7g-3b): §11.1 exposure gate (Fix-1) + §11.2 hedge urgency,
    # markers-fed, write-only on ST-07/08/09/ST-23. Still exactly stage "P1".
    state, p1 = apply_p1(state, materialized)
    stages.append(p1)

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

    # P6 is real (Phase 7h-4b-2): §5.2 arming/placement — cancel-select, arm eval +
    # submission emit, ladder issuance, ST-04<->ST-05 coupling. Markers-fed; it emits
    # CommandEvents (returned, never appended here — D11) and writes ST-04 only.
    state, p6, sub_decisions, emitted = apply_p6(state)
    stages.append(p6)

    return state, PassReport(stages=tuple(stages), sub_decisions=sub_decisions), emitted
