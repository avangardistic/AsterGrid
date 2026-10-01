"""§4.7 P3 + P4 — precedence (Phase 7d, real logic).

Both functions are pure, total, clock-free and deterministic. Each reads ONLY the
state's candidate marker fields — NEVER envelope or event content (Phase-7d
DESIGN RULE). The ``envelopes`` parameter exists for signature stability
(Phase 7e/7f will populate the markers from folded envelopes) and is used here
ONLY for counting in the deterministic note.

P3 (§4.7 P3) — SAME-GENERATION CONFLICT:
  For the same Generation G, if both a Cycle-limit disable candidate and an
  Evolution candidate are present in one pass, the DISABLE wins and the Evolution
  candidate is recorded INELIGIBLE with reason CYCLE_LIMIT_REACHED (verbatim
  §4.7 P3). Output ``p3_decisions`` = the ineligible Evolution GenerationIDs for
  THIS pass, sorted ascending.
  BOUNDARY: Cycle-scoped persistence of ineligibility ("no candidate after
  INELIGIBLE within the same Cycle", DECISION-013) is Phase-7f semantics (needs
  ST-03 cycle identity); Phase 7d records the per-pass decision only.

P4 (§4.7 P4) — ACROSS-GENERATION PRECEDENCE:
  Evolution transitions execute BEFORE Cycle transitions
  (ACROSS_GEN_EVOLUTION_BEFORE_CYCLE). Among Evolutions the LOWER GenerationID
  executes first (ACROSS_GEN_LOWER_GEN_ID_FIRST) — impossible under the P2
  single-in-flight lock, but stated for determinism (verbatim §4.7 P4). Output
  ``p4_decisions`` is the ordered admission list (execution order = tuple order).
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from astergrid.core.transitions.markers import P4Decision, StageReport
from astergrid.core.transitions.reason_codes import ReasonCode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from astergrid.core.events import EventEnvelope
    from astergrid.core.state import State


def apply_same_generation_precedence(
    state: State,
    envelopes: Sequence[EventEnvelope],
) -> tuple[State, StageReport]:
    """Apply the §4.7 P3 same-generation conflict rule (DISABLE beats Evolution)."""
    count = len(envelopes)
    markers = state.p3_candidates
    if markers is None:
        note = f"P3 no-op: no candidate markers ({count} envelopes)"
        return state, StageReport("P3", "NO_OP", (), note)

    disable = set(markers.disable_candidates)
    evolution = set(markers.evolution_candidates)
    ineligible = tuple(sorted(g for g in evolution if g in disable))

    reason_codes: list[str] = []
    if ineligible:
        reason_codes.append(ReasonCode.SAME_GEN_DISABLE_BEATS_EVOLUTION.value)
        reason_codes.append(ReasonCode.CYCLE_LIMIT_REACHED.value)

    # Phase-7f multi-pass bridge (added, not replacing the per-pass decision): for
    # each ineligible G whose CURRENT Cycle is known, persist (G, C) so a later
    # pass in the SAME Cycle still binds Evolution (DECISION-013 per-Cycle
    # persistence). Unknown current Cycle ⟹ add nothing. All markers None ⟹ the
    # persistent set is left untouched, so 7d behaviour is byte-identical. Pruning
    # stale (completed-cycle) entries is a later-phase GC note, not done here.
    current = dict(state.current_cycle_id_by_generation or ())
    added = {(g, current[g]) for g in ineligible if g in current}
    if added:
        existing = set(state.p3_ineligible_cycles or ())
        new_ineligible: tuple[tuple[int, int], ...] | None = tuple(
            sorted(existing | added)
        )
    else:
        new_ineligible = state.p3_ineligible_cycles

    new_state = dataclasses.replace(
        state, p3_decisions=ineligible, p3_ineligible_cycles=new_ineligible
    )
    note = (
        f"P3 same-gen: {len(ineligible)} evolution candidate(s) ineligible "
        f"({count} envelopes)"
    )
    return new_state, StageReport("P3", "APPLIED", tuple(reason_codes), note)


def apply_across_generation_precedence(
    state: State,
    envelopes: Sequence[EventEnvelope],
) -> tuple[State, StageReport]:
    """Apply the §4.7 P4 across-generation ordering (Evolution before Cycle)."""
    count = len(envelopes)
    markers = state.p4_candidates
    if markers is None:
        note = f"P4 no-op: no candidate markers ({count} envelopes)"
        return state, StageReport("P4", "NO_OP", (), note)

    evolutions = sorted(set(markers.evolution_candidates))  # lower GenID first
    cycles = sorted(set(markers.cycle_candidates))  # (GenID, CycleID) lexicographic

    decisions: list[P4Decision] = []
    for gid in evolutions:  # all Evolutions first
        decisions.append(
            P4Decision(
                transition="EVOLUTION",
                generation_id=gid,
                cycle_id=None,
                reason=ReasonCode.ACROSS_GEN_EVOLUTION_BEFORE_CYCLE,
            )
        )
    for gid, cid in cycles:  # then all Cycles
        decisions.append(
            P4Decision(
                transition="CYCLE",
                generation_id=gid,
                cycle_id=cid,
                reason=ReasonCode.ACROSS_GEN_EVOLUTION_BEFORE_CYCLE,
            )
        )

    reason_codes: list[str] = []
    if decisions:
        reason_codes.append(ReasonCode.ACROSS_GEN_EVOLUTION_BEFORE_CYCLE.value)
    if len(evolutions) >= 2:
        reason_codes.append(ReasonCode.ACROSS_GEN_LOWER_GEN_ID_FIRST.value)

    new_state = dataclasses.replace(state, p4_decisions=tuple(decisions))
    note = (
        f"P4 across-gen: {len(evolutions)} evolution then {len(cycles)} cycle "
        f"({count} envelopes)"
    )
    return new_state, StageReport("P4", "APPLIED", tuple(reason_codes), note)
