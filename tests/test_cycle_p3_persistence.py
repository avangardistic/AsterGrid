"""Multi-pass P3 ineligibility persistence across a Cycle (Phase 7f), via run_pass.

Why pass 2 sets p3_candidates PRESENT-but-disjoint: P3 with markers None is a
NO_OP that would leave pass 1's per-pass ``p3_decisions`` stale. Resetting the
per-pass decision to () isolates the PERSISTENT ``p3_ineligible_cycles`` set as
the thing under test.
"""

import dataclasses

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.state import State
from hypergrid.core.transitions import (
    EvolutionCandidateWindow,
    GenerationState,
    P3CandidateMarkers,
)


def _glife(state: State, gid: int) -> str | None:
    for g in state.st02_generation_states or ():
        if g.generation_id == gid:
            return g.lifecycle
    return None


def _complete_window(gid: int) -> EvolutionCandidateWindow:
    return EvolutionCandidateWindow(gid, "SL", (1, 2), 2, True, True, True)


def test_persistent_ineligibility_same_cycle_binds_evolution() -> None:
    # Pass 1: P3 co-occurrence for G0 at current Cycle 7.
    pass1 = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        p3_candidates=P3CandidateMarkers(
            disable_candidates=(0,), evolution_candidates=(0,)
        ),
        current_cycle_id_by_generation=((0, 7),),
    )
    s1, _ = run_pass(pass1, [])
    assert s1.p3_ineligible_cycles == ((0, 7),)
    assert s1.p3_decisions == (0,)

    # Pass 2 (same Cycle 7): reset per-pass P3 to (), add a complete window for G0.
    pass2 = dataclasses.replace(
        s1,
        p3_candidates=P3CandidateMarkers(
            disable_candidates=(), evolution_candidates=()
        ),
        st16_evolution_candidate_windows=(_complete_window(0),),
    )
    s2, _ = run_pass(pass2, [])
    assert s2.p3_decisions == ()  # per-pass reset
    assert _glife(s2, 1) is None  # Evolution stayed bound (silent) — no G1
    assert _glife(s2, 0) == "ACTIVE"


def test_later_cycle_recandidates() -> None:
    base = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        p3_ineligible_cycles=((0, 7),),
        current_cycle_id_by_generation=((0, 8),),  # moved on to Cycle 8
        p3_candidates=P3CandidateMarkers(
            disable_candidates=(), evolution_candidates=()
        ),
        st16_evolution_candidate_windows=(_complete_window(0),),
    )
    s, _ = run_pass(base, [])
    assert _glife(s, 1) == "CREATED"  # (0,8) not ineligible -> Evolution admitted
    assert _glife(s, 0) == "SUCCESSOR_CREATED"


def test_multi_generation_union_sorted() -> None:
    pass1 = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(
            GenerationState(0, "ACTIVE"),
            GenerationState(1, "ACTIVE"),
        ),
        p3_candidates=P3CandidateMarkers(
            disable_candidates=(0, 1), evolution_candidates=(0, 1)
        ),
        current_cycle_id_by_generation=((0, 3), (1, 5)),
    )
    s, _ = run_pass(pass1, [])
    assert s.p3_ineligible_cycles == ((0, 3), (1, 5))  # sorted, no dups


def test_unknown_current_cycle_leaves_set_none() -> None:
    pass1 = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        p3_candidates=P3CandidateMarkers(
            disable_candidates=(0,), evolution_candidates=(0,)
        ),
        # no current_cycle_id_by_generation
    )
    s, _ = run_pass(pass1, [])
    assert s.p3_decisions == (0,)  # 7d per-pass decision still recorded
    assert s.p3_ineligible_cycles is None  # nothing persisted (unknown Cycle)
