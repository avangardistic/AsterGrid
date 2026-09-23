"""The P0-P6 pass engine (Phase 7d).

``run_pass`` runs the §4.7 stages in strict P0..P6 order over one pass. Phase 7d
implements the deterministic ordering substrate only:

  P0  POSITION VERIFICATION & RECONCILIATION      — STUB (§11.1, Phase 7e)
  P1  RISK/EXPOSURE PROTECTION & HEDGE RECOVERY    — STUB (§11.1/§11.2, later)
  P2  LOCKS                                        — REAL (transitions.locks)
  P3  SAME-GENERATION CONFLICT                     — REAL (transitions.precedence)
  P4  ACROSS-GENERATION PRECEDENCE                 — REAL (transitions.precedence)
  P5  CYCLE TRANSITIONS                            — STUB (§5.2/§5.3, later)
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
    state, p4 = apply_across_generation_precedence(state, materialized)
    stages.append(p4)

    stages.append(_stub("P5"))
    stages.append(_stub("P6"))

    return state, PassReport(stages=tuple(stages))
