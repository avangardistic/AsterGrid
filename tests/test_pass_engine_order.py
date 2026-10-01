"""Pass engine: seven stages P0..P6 in order, stub/real split, purity (Phase 7d)."""

import dataclasses
import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager

from astergrid.core.fold import _empty_state
from astergrid.core.pass_engine import PassReport, run_pass
from astergrid.core.serialization import canonical_dumps
from astergrid.core.transitions import (
    EvolutionCandidateWindow,
    GenerationState,
    P3CandidateMarkers,
    P4CandidateMarkers,
    ReasonCode,
    apply_across_generation_precedence,
)

# Strategy.md §4.7 defines seven passes, P0 through P6.
_STAGES = ("P0", "P1", "P2", "P3", "P4", "P5", "P6")
_STUBBED: tuple[str, ...] = ()  # P0 real 7h-1; P1 7g-3b; P5 7f; P6 7h-4b-2
_REAL = ("P0", "P1", "P2", "P3", "P4", "P5", "P6")


@contextmanager
def _no_ambient() -> Iterator[None]:
    def boom(*_a: object, **_k: object) -> object:
        raise AssertionError("clock/randomness accessed")

    saved = (time.time, time.monotonic, random.random, os.urandom)
    time.time = boom  # type: ignore[assignment]
    time.monotonic = boom  # type: ignore[assignment]
    random.random = boom  # type: ignore[assignment]
    os.urandom = boom  # type: ignore[assignment]
    try:
        yield
    finally:
        time.time, time.monotonic, random.random, os.urandom = saved


def test_seven_stages_in_order() -> None:
    _, report, _ = run_pass(_empty_state(), [])
    assert isinstance(report, PassReport)
    assert tuple(s.stage for s in report.stages) == _STAGES


def test_stub_and_real_status_split() -> None:
    # markers all None -> real stages report NO_OP, stubs report STUBBED.
    _, report, _ = run_pass(_empty_state(), [])
    by_stage = {s.stage: s for s in report.stages}
    for stage in _STUBBED:
        assert by_stage[stage].status == "STUBBED"
    for stage in _REAL:
        assert by_stage[stage].status in ("APPLIED", "NO_OP")
        assert by_stage[stage].status == "NO_OP"  # markers None => NO_OP


def test_stubs_pass_state_through_unchanged() -> None:
    state = _empty_state()  # all P2/P3/P4 markers None
    before = canonical_dumps(state.to_canonical_obj())
    new_state, _, _ = run_pass(state, [])
    assert canonical_dumps(new_state.to_canonical_obj()) == before


def test_empty_envelopes_leaves_canonical_state_unchanged() -> None:
    state = _empty_state()
    before = canonical_dumps(state.to_canonical_obj())
    new_state, _, _ = run_pass(state, iter([]))
    assert canonical_dumps(new_state.to_canonical_obj()) == before


def test_run_pass_is_clock_and_randomness_free() -> None:
    with _no_ambient():
        state, report, _ = run_pass(_empty_state(), [])
    assert len(report.stages) == 7
    assert state.event_count == 0


def test_report_is_canonical_serializable() -> None:
    _, report, _ = run_pass(_empty_state(), [])
    canonical_dumps(report.to_canonical_obj())


# ---------------- Phase 7e: P4 stays one stage; evolution composes ----------------


def test_no_p4_exec_stage_name() -> None:
    _, report, _ = run_pass(_empty_state(), [])
    names = [s.stage for s in report.stages]
    assert names == list(_STAGES)  # exactly seven, P0..P6
    assert "P4_EXEC" not in names


def test_no_p5_exec_stage_name() -> None:
    _, report, _ = run_pass(_empty_state(), [])
    names = [s.stage for s in report.stages]
    assert names == list(_STAGES)  # still exactly seven; P5 is real, not renamed
    assert "P5_EXEC" not in names


def test_p5_compat_pin_markers_absent() -> None:
    # No cycle markers => P5 NO_OP and the canonical State is unchanged.
    state = _empty_state()
    before = canonical_dumps(state.to_canonical_obj())
    new_state, report, _ = run_pass(state, [])
    p5 = {s.stage: s for s in report.stages}["P5"]
    assert p5.status == "NO_OP"
    assert canonical_dumps(new_state.to_canonical_obj()) == before


def _complete_window(gid: int, origin: str = "SL") -> EvolutionCandidateWindow:
    return EvolutionCandidateWindow(gid, origin, (1, 2), 2, True, True, True)


def test_p4_7d_compat_pin_generation_markers_absent() -> None:
    # Arbitration inputs present, generation markers absent => the combined P4
    # report is byte-identical to the Phase-7d arbitration-only P4 report.
    p4c = P4CandidateMarkers(evolution_candidates=(0, 1), cycle_candidates=((0, 0),))
    state = dataclasses.replace(_empty_state(), p4_candidates=p4c)
    _, arb = apply_across_generation_precedence(state, [])
    _, full, _ = run_pass(state, [])
    p4 = {s.stage: s for s in full.stages}["P4"]
    assert p4.status == arb.status
    assert p4.reason_codes == arb.reason_codes
    assert p4.notes == arb.notes


def test_p4_combines_execution_when_markers_present() -> None:
    state = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        st16_evolution_candidate_windows=(_complete_window(0),),
    )
    _, full, _ = run_pass(state, [])
    p4 = {s.stage: s for s in full.stages}["P4"]
    assert p4.status == "APPLIED"  # execution admitted
    assert "evolution:" in p4.notes  # execution suffix present
    assert p4.reason_codes == ()  # admission emits no code


def test_p4_composition_p3_binding_through_state() -> None:
    # P3 marks G0 ineligible AND ST-16 holds G0's valid window: P3 emits
    # CYCLE_LIMIT_REACHED and evolution skips G0 silently (stages compose via state).
    state = dataclasses.replace(
        _empty_state(),
        p3_candidates=P3CandidateMarkers(
            disable_candidates=(0,), evolution_candidates=(0,)
        ),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        st16_evolution_candidate_windows=(_complete_window(0),),
    )
    new, full, _ = run_pass(state, [])
    by_stage = {s.stage: s for s in full.stages}
    assert ReasonCode.CYCLE_LIMIT_REACHED.value in by_stage["P3"].reason_codes
    assert by_stage["P4"].reason_codes == ()  # no admission, no duplicate code
    assert [g.generation_id for g in (new.st02_generation_states or ())] == [0]
