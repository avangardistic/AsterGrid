"""§4.7 P2 — locks (Phase 7d, real logic).

P2 enforces two independent locks, evaluated together in one pass:
  * at most one Evolution transition in flight per Basket (§4.2);
  * at most one Cycle transition per Generation per pass.

``apply_locks`` is pure, total, clock-free and deterministic. It reads ONLY the
state's marker fields (``p2_locks`` + ``p2_attempts``) — NEVER envelope or event
content (Phase-7d DESIGN RULE). The ``envelopes`` parameter exists for signature
stability (Phase 7e/7f will populate the markers from folded envelopes) and is
used here ONLY for counting in the deterministic note.

If either marker field is ``None`` the stage is a NO_OP (state returned
unchanged). Otherwise, for the attempts recorded in ``p2_attempts``:
  * an attempted Evolution is ADMITTED iff none is already in flight (the
    in-flight flag is set); else BLOCKED with EVOLUTION_IN_FLIGHT_LOCKED;
  * an attempted Cycle for Generation G is ADMITTED iff none is already in
    flight for G; else BLOCKED with CYCLE_TRANSITION_IN_FLIGHT_LOCKED.
The returned State is new (never mutated); its lock flags reflect the admissions.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from hypergrid.core.transitions.markers import P2LocksState, StageReport
from hypergrid.core.transitions.reason_codes import ReasonCode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from hypergrid.core.events import EventEnvelope
    from hypergrid.core.state import State


def apply_locks(
    state: State,
    envelopes: Sequence[EventEnvelope],
) -> tuple[State, StageReport]:
    """Apply the §4.7 P2 in-flight locks; return (new state, stage report)."""
    count = len(envelopes)
    locks = state.p2_locks
    attempts = state.p2_attempts
    if locks is None or attempts is None:
        note = f"P2 no-op: no lock markers ({count} envelopes)"
        return state, StageReport("P2", "NO_OP", (), note)

    reason_codes: list[str] = []

    evolution_in_flight = locks.evolution_in_flight
    if attempts.evolution_attempted:
        if evolution_in_flight:
            reason_codes.append(ReasonCode.EVOLUTION_IN_FLIGHT_LOCKED.value)
        else:
            evolution_in_flight = True  # admit the single Evolution

    cycle_map: dict[int, bool] = dict(locks.cycle_in_flight_by_generation)
    for gid, attempted in attempts.cycle_attempted_by_generation:
        if not attempted:
            continue
        if cycle_map.get(gid, False):
            reason_codes.append(ReasonCode.CYCLE_TRANSITION_IN_FLIGHT_LOCKED.value)
        else:
            cycle_map[gid] = True  # admit the single Cycle for this Generation

    new_locks = P2LocksState(
        evolution_in_flight=evolution_in_flight,
        cycle_in_flight_by_generation=tuple(sorted(cycle_map.items())),
    )
    new_state = dataclasses.replace(state, p2_locks=new_locks)
    note = f"P2 locks applied ({count} envelopes)"
    return new_state, StageReport("P2", "APPLIED", tuple(reason_codes), note)
