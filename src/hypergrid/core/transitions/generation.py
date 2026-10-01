"""§4.1/§4.4/§4.5/§4.6 Evolution transition (Phase 7e) — executed inside P4.

``apply_evolution`` is pure, total, clock-free and deterministic. It reads ONLY
the state's generation marker fields (ST-02/14/15/16 + the
``effective_generation_limit`` marker) plus the NARROW ``p3_decisions`` exception
in rule (2) — NEVER an envelope or event field (the Phase-7d DESIGN RULE stays in
force; ``envelopes`` is
counting-only for signature stability).

MARKER DOCTRINE
---------------
Phase-7e markers describe COMPLETED evaluations. A test-set marker asserts "the
(future) verifier already decided this". Anything not-yet-evaluated is ABSENCE
(no window; ``return_level=None``), never a guessing boolean. Multi-pass
in-progress tracking (running §4.2 confirmation windows across passes, running P0
evaluations) arrives with timers + real P0 in a later phase; until then the ONLY
"in progress" representation is lifecycle ``EVOLUTION_PENDING`` (rule (1c)). A
real P0 will populate ST-16 windows from envelopes; a real P1 will own the
``guards_passed`` verdict; timers will drive ``return_confirmation_held`` across
passes. ``apply_evolution`` itself never reads an envelope.

PHASE-7f BRIDGE (rule (2)): besides this pass's ``p3_decisions``, rule (2) also
honours a PERSISTENT per-Cycle P3 verdict — ``p3_ineligible_cycles`` keyed
(G, current-Cycle) via ``current_cycle_id_by_generation``. If G's current Cycle is
known and was recorded ineligible by P3 in any pass of this Cycle, the Evolution
stays silently bound (no code; P3 owns ``CYCLE_LIMIT_REACHED``). An unknown current
Cycle yields no opinion; all-None markers reproduce Phase-7e behaviour exactly.

DESIGN DECISION (Owner, binding): ``p2_locks.evolution_in_flight`` (§4.7 P2,
transient/per-pass/Basket-wide) and the ST-15 successor lock (§4.4,
permanent/per-Generation) are DISTINCT and never merged. This transition reads
ST-15 (rule 5); it never reads ``p2_locks``/``p2_attempts`` (rule (8) enforces
single admission via its own in-pass flag). The window-lifecycle gating for
terminal states (§4.3/§5.3) lives HERE, in rules (1)/(5)/(6), not as a
State-construction ban — so a window may coexist with SUCCESSOR_CREATED /
DISABLED_AT_CYCLE_99 (required by rules (5)/(6) and §5.7 scenarios 11/12/19).
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from hypergrid.core.transitions.generation_state import (
    DominanceFlag,
    GenerationState,
    SuccessorLock,
)
from hypergrid.core.transitions.markers import StageReport
from hypergrid.core.transitions.reason_codes import ReasonCode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from hypergrid.core.events import EventEnvelope
    from hypergrid.core.state import State

_DEFAULT_GENERATION_LIMIT = 99  # §4.6 hard default when the marker is None
# §4.3 terminal progression states: a window on one is skipped silently (rule 1a).
_SKIP_LIFECYCLES = frozenset({"DISABLED_AT_CYCLE_99", "CLOSED_ONLY_AS_PART_OF_BASKET"})


def apply_evolution(
    state: State,
    envelopes: Sequence[EventEnvelope],
) -> tuple[State, StageReport]:
    """Evaluate the §4.1 Evolution trigger over ST-16 windows; admit at most one.

    Returns (new state, P4 execution sub-report). If ST-16 is absent the sub-step
    contributes NOTHING (NO_OP, no codes, no note) — the 7d-compatibility pin.
    """
    # `envelopes` is intentionally unread: the DESIGN RULE forbids reading event
    # content; the parameter exists only for signature stability across stages.
    windows = state.st16_evolution_candidate_windows
    if windows is None:
        return state, StageReport("P4", "NO_OP", (), "")

    st02 = list(state.st02_generation_states or ())
    st14 = list(state.st14_dominance_flags or ())
    st15 = list(state.st15_successor_locks or ())
    limit = state.effective_generation_limit
    effective_limit = _DEFAULT_GENERATION_LIMIT if limit is None else limit
    p3_block = set(state.p3_decisions or ())
    # Phase-7f multi-pass P3 bridge (rule (2)): a persistent per-Cycle
    # ineligibility set, keyed (G, current-Cycle). If G's current Cycle is known
    # and (G, C) was recorded ineligible by P3 in ANY pass of this Cycle, the
    # Evolution is still bound (silent, no code — P3 owns CYCLE_LIMIT_REACHED).
    # Unknown current Cycle ⟹ no opinion. All-None ⟹ byte-identical 7e behaviour.
    current_cycle = dict(state.current_cycle_id_by_generation or ())
    ineligible_cycles = set(state.p3_ineligible_cycles or ())

    lifecycle_by_id = {g.generation_id: g.lifecycle for g in st02}
    locked_ids = {s.generation_id for s in st15 if s.locked}
    pending_ids = {g.generation_id for g in st02 if g.lifecycle == "EVOLUTION_PENDING"}

    codes: list[str] = []
    admitted = 0
    in_pass_admitted = False

    for window in sorted(windows, key=lambda w: w.generation_id):
        g = window.generation_id
        lifecycle = lifecycle_by_id.get(g)

        # (1) LIFECYCLE GATE
        if lifecycle in _SKIP_LIFECYCLES:
            continue  # (1a) candidacy already ended — silent
        if lifecycle == "EVOLUTION_PENDING" and not window.return_confirmation_held:
            continue  # (1c) window running, not failed — silent
        # (1b) ACTIVE/CREATED proceed; SUCCESSOR_CREATED falls through to rule (5).

        # (2) P3 BINDING — P3 already recorded CYCLE_LIMIT_REACHED; add no code.
        if g in p3_block:
            continue  # silent (this pass's P3 verdict)
        if g in current_cycle and (g, current_cycle[g]) in ineligible_cycles:
            continue  # silent (persistent per-Cycle P3 verdict, Phase-7f bridge)

        # (3) GUARDS — a failure is P1-real's verdict to record, not evolution's.
        if not window.guards_passed:
            continue  # silent

        # (4) RETURN
        if window.return_level is None:
            continue  # no return attempted — silent (§4.1: no apparent trigger)
        if not window.return_level_verified or not window.return_confirmation_held:
            codes.append(ReasonCode.RETURN_LEVEL_UNVERIFIED.value)  # §4.1 fail-closed
            continue

        # (5) SUCCESSOR LOCK (§4.4 item 6)
        if g in locked_ids:
            codes.append(ReasonCode.SUCCESSOR_LOCK_ACTIVE.value)
            continue

        # (6) GENERATION LIMIT (§4.6: attempt AT the limit rejected)
        if g >= effective_limit:
            codes.append(ReasonCode.GENERATION_ID_LIMIT.value)
            continue

        # (7) BASKET IN-FLIGHT (§4.3): another Generation is EVOLUTION_PENDING.
        if any(h != g for h in pending_ids):
            codes.append(ReasonCode.EVOLUTION_IN_FLIGHT_LOCKED.value)
            continue

        # (8) IN-PASS SINGLE ADMISSION (§4.7 P2 executable form)
        if in_pass_admitted:
            codes.append(ReasonCode.EVOLUTION_IN_FLIGHT_LOCKED.value)
            continue

        # (9) ADMIT — all effects atomically build the next State.
        in_pass_admitted = True
        admitted += 1
        st15.append(SuccessorLock(generation_id=g, locked=True))  # set ST-15 lock
        locked_ids.add(g)
        st02 = [
            dataclasses.replace(gs, lifecycle="SUCCESSOR_CREATED")
            if gs.generation_id == g
            else gs
            for gs in st02
        ]
        st02.append(GenerationState(generation_id=g + 1, lifecycle="CREATED"))
        st14.append(
            DominanceFlag(generation_id=g + 1, dominant_group=window.origin_group)
        )
        lifecycle_by_id[g] = "SUCCESSOR_CREATED"
        lifecycle_by_id[g + 1] = "CREATED"

    if admitted > 0:
        new_state = dataclasses.replace(
            state,
            st02_generation_states=tuple(sorted(st02, key=lambda gs: gs.generation_id)),
            st14_dominance_flags=tuple(sorted(st14, key=lambda d: d.generation_id)),
            st15_successor_locks=tuple(sorted(st15, key=lambda s: s.generation_id)),
        )
        note = f"evolution: {admitted} admitted, {len(codes)} blocked"
        return new_state, StageReport("P4", "APPLIED", tuple(codes), note)

    if codes:
        note = f"evolution: 0 admitted, {len(codes)} blocked"
        return state, StageReport("P4", "APPLIED", tuple(codes), note)

    return state, StageReport("P4", "NO_OP", (), "")
