"""§5.7 Evolution scenarios (01-12, 18-19) + NEW cases as tests (Phase 7e).

All markers are set DIRECTLY on synthetic States — no envelope interpretation.
Each test asserts the returned State's fields + StageReport codes + status.
"""

import dataclasses

from astergrid.core.fold import _empty_state
from astergrid.core.serialization import canonical_dumps
from astergrid.core.state import State
from astergrid.core.transitions import (
    EvolutionCandidateWindow,
    GenerationState,
    ReasonCode,
    SuccessorLock,
    apply_evolution,
)

_RET = ReasonCode.RETURN_LEVEL_UNVERIFIED.value
_LOCK = ReasonCode.SUCCESSOR_LOCK_ACTIVE.value
_LIMIT = ReasonCode.GENERATION_ID_LIMIT.value
_INFLIGHT = ReasonCode.EVOLUTION_IN_FLIGHT_LOCKED.value


def _window(
    gid: int,
    *,
    origin: str = "SL",
    levels: tuple[int, ...] = (1, 2),
    return_level: int | None = None,
    verified: bool = False,
    held: bool = False,
    guards: bool = True,
) -> EvolutionCandidateWindow:
    return EvolutionCandidateWindow(
        generation_id=gid,
        origin_group=origin,
        traversal_verified_levels=levels,
        return_level=return_level,
        return_level_verified=verified,
        return_confirmation_held=held,
        guards_passed=guards,
    )


def _complete(gid: int, *, origin: str = "SL") -> EvolutionCandidateWindow:
    return _window(gid, origin=origin, return_level=2, verified=True, held=True)


def _state(
    *,
    st02: tuple[GenerationState, ...] | None = None,
    st15: tuple[SuccessorLock, ...] | None = None,
    st16: tuple[EvolutionCandidateWindow, ...] | None = None,
    p3_decisions: tuple[int, ...] | None = None,
    limit: int | None = None,
) -> State:
    return dataclasses.replace(
        _empty_state(),
        st02_generation_states=st02,
        st15_successor_locks=st15,
        st16_evolution_candidate_windows=st16,
        p3_decisions=p3_decisions,
        effective_generation_limit=limit,
    )


def _life(state: State, gid: int) -> str | None:
    for g in state.st02_generation_states or ():
        if g.generation_id == gid:
            return g.lifecycle
    return None


def _locked(state: State, gid: int) -> bool:
    return gid in {
        s.generation_id for s in (state.st15_successor_locks or ()) if s.locked
    }


def _dom(state: State, gid: int) -> str | None:
    for d in state.st14_dominance_flags or ():
        if d.generation_id == gid:
            return d.dominant_group
    return None


def _has_window(state: State, gid: int) -> bool:
    return gid in {
        w.generation_id for w in (state.st16_evolution_candidate_windows or ())
    }


def _gen_ids(state: State) -> list[int]:
    return [g.generation_id for g in (state.st02_generation_states or ())]


def _unchanged(before: State, after: State) -> bool:
    return canonical_dumps(before.to_canonical_obj()) == canonical_dumps(
        after.to_canonical_obj()
    )


# ------------------------------ Scenarios 01-12 ------------------------------


def test_scenario_01_no_traversal_no_generation() -> None:
    state = _state(st02=(GenerationState(0, "ACTIVE"),), st16=())
    new, report = apply_evolution(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert _unchanged(state, new)


def test_scenario_02_verified_no_return() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st16=(_window(0, origin="SL", levels=(1, 2), return_level=None),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert _unchanged(state, new)


def test_scenario_03_penetration_no_verified_return() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st16=(_window(0, origin="SL", levels=(1, 2, 3), return_level=None),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert _unchanged(state, new)


def test_scenario_04_verified_return_admits() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st16=(_complete(0, origin="SL"),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == ()
    assert _life(new, 0) == "SUCCESSOR_CREATED"
    assert _locked(new, 0) is True
    assert _life(new, 1) == "CREATED"
    assert _dom(new, 1) == "SL"
    assert not _has_window(new, 1)  # successor has no traversal yet
    assert _has_window(new, 0)  # parent window untouched
    assert _gen_ids(new) == [0, 1]


def test_scenario_05_raw_price_touch_unverified() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st16=(_window(0, return_level=2, verified=False),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_RET,)
    assert _unchanged(state, new)


def test_scenario_06_acked_delta_unverified() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st16=(_window(0, levels=(1, 2, 3), return_level=3, verified=False),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_RET,)
    assert _unchanged(state, new)


def test_scenario_07_partial_verification_window_failed() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st16=(_window(0, return_level=2, verified=True, held=False),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_RET,)
    assert _unchanged(state, new)


def test_scenario_08_terminal_no_window() -> None:
    state = _state(st02=(GenerationState(0, "ACTIVE"),), st16=())
    new, report = apply_evolution(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert _unchanged(state, new)


def test_scenario_09_terminal_pending_orders_no_window() -> None:
    state = _state(st02=(GenerationState(0, "ACTIVE"),), st16=())
    new, report = apply_evolution(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert _unchanged(state, new)


def test_scenario_10_verified_return_next_cycle_admits() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st16=(_complete(0, origin="BU"),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == ()
    assert _life(new, 0) == "SUCCESSOR_CREATED"
    assert _locked(new, 0) is True
    assert _life(new, 1) == "CREATED"
    assert _dom(new, 1) == "BU"


def test_scenario_11_second_window_blocked_by_lock() -> None:
    state = _state(
        st02=(GenerationState(0, "SUCCESSOR_CREATED"),),
        st15=(SuccessorLock(0, True),),
        st16=(_complete(0),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_LOCK,)
    assert _gen_ids(new) == [0]  # no G2
    assert _life(new, 0) == "SUCCESSOR_CREATED"
    assert _unchanged(state, new)


def test_scenario_12_later_cycle_attempt_blocked_by_lock() -> None:
    state = _state(
        st02=(GenerationState(0, "SUCCESSOR_CREATED"),),
        st15=(SuccessorLock(0, True),),
        st16=(_complete(0, origin="BU"),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_LOCK,)
    assert _gen_ids(new) == [0]
    assert _unchanged(state, new)


# ------------------------------ Scenarios 18-19 ------------------------------


def test_scenario_18_successor_creates_its_own_successor() -> None:
    state = _state(
        st02=(
            GenerationState(0, "SUCCESSOR_CREATED"),
            GenerationState(1, "ACTIVE"),
        ),
        st15=(SuccessorLock(0, True),),
        st16=(_complete(1, origin="SL"),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == ()
    assert _life(new, 1) == "SUCCESSOR_CREATED"
    assert _locked(new, 1) is True
    assert _life(new, 2) == "CREATED"
    assert _dom(new, 2) == "SL"
    assert _life(new, 0) == "SUCCESSOR_CREATED"  # G0 untouched
    assert _gen_ids(new) == [0, 1, 2]


def test_scenario_19_generation_99_limit() -> None:
    state = _state(
        st02=(GenerationState(99, "ACTIVE"),),
        st16=(_complete(99),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_LIMIT,)
    assert _gen_ids(new) == [99]  # never wraps, no G100
    assert _life(new, 99) == "ACTIVE"  # lifecycle unchanged
    assert _locked(new, 99) is False
    assert _unchanged(state, new)


# ------------------------------- NEW cases -----------------------------------


def test_new_single_admission_lowest_generation() -> None:
    # G0 and G2 both hold complete windows; only the lowest (G0) is admitted.
    state = _state(
        st02=(GenerationState(0, "ACTIVE"), GenerationState(2, "ACTIVE")),
        st16=(_complete(0), _complete(2)),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_INFLIGHT,)  # exactly one block (G2)
    assert _locked(new, 0) is True  # G0 admitted
    assert _locked(new, 2) is False  # G2 blocked
    assert _life(new, 0) == "SUCCESSOR_CREATED"
    assert _life(new, 2) == "ACTIVE"
    assert _gen_ids(new) == [0, 1, 2]  # G1 created; no G3


def test_new_p3_binding_silent_skip() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st16=(_complete(0),),
        p3_decisions=(0,),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()  # P3's CYCLE_LIMIT_REACHED stands; no dup
    assert _gen_ids(new) == [0]
    assert _unchanged(state, new)


def test_new_disabled_generation_silent_skip() -> None:
    state = _state(
        st02=(GenerationState(0, "DISABLED_AT_CYCLE_99"),),
        st16=(_complete(0),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert _unchanged(state, new)


def test_new_pending_other_blocks_in_flight() -> None:
    state = _state(
        st02=(
            GenerationState(0, "EVOLUTION_PENDING"),
            GenerationState(1, "ACTIVE"),
        ),
        st16=(
            _window(0, return_level=2, verified=True, held=False),  # running
            _complete(1),
        ),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_INFLIGHT,)  # G1 blocked by §4.3
    assert _gen_ids(new) == [0, 1]  # no admission
    assert _life(new, 0) == "EVOLUTION_PENDING"
    assert _life(new, 1) == "ACTIVE"
    assert _unchanged(state, new)


def test_new_pending_self_held_window_admits() -> None:
    state = _state(
        st02=(GenerationState(0, "EVOLUTION_PENDING"),),
        st16=(_complete(0),),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == ()
    assert _life(new, 0) == "SUCCESSOR_CREATED"
    assert _locked(new, 0) is True
    assert _life(new, 1) == "CREATED"
