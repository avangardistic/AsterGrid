"""Exhaustive bounded Evolution grid vs an independent oracle (Phase 7e).

Single-candidate grid: lifecycle x return x guards x lock x G(limit boundary) x
p3-membership, pruning the one incoherent combo (EVOLUTION_PENDING + locked, which
State.__post_init__ rejects). Plus multi-generation single-admission / in-flight
blocks. All markers set directly — no envelope interpretation.
"""

import dataclasses
import itertools

from hypergrid.core.fold import _empty_state
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import State
from hypergrid.core.transitions import (
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

_LIFES = ("ACTIVE", "EVOLUTION_PENDING", "DISABLED_AT_CYCLE_99")
_RETS = ("absent", "unverified", "held")


def _win(g: int, ret: str, guards: bool) -> EvolutionCandidateWindow:
    if ret == "absent":
        return EvolutionCandidateWindow(g, "SL", (1, 2), None, False, False, guards)
    if ret == "unverified":
        return EvolutionCandidateWindow(g, "SL", (1, 2), 2, False, False, guards)
    return EvolutionCandidateWindow(g, "SL", (1, 2), 2, True, True, guards)  # held


def _life(state: State, gid: int) -> str | None:
    for g in state.st02_generation_states or ():
        if g.generation_id == gid:
            return g.lifecycle
    return None


def _locked(state: State, gid: int) -> bool:
    return gid in {
        s.generation_id for s in (state.st15_successor_locks or ()) if s.locked
    }


def _gen_ids(state: State) -> list[int]:
    return [g.generation_id for g in (state.st02_generation_states or ())]


def _unchanged(before: State, after: State) -> bool:
    return canonical_dumps(before.to_canonical_obj()) == canonical_dumps(
        after.to_canonical_obj()
    )


def _expected(
    lifecycle: str, ret: str, guards: bool, locked: bool, g: int, in_p3: bool
) -> tuple[str, str | None]:
    """Independent oracle mirroring rules (1)-(9) for a single candidate, limit=99."""
    if lifecycle == "DISABLED_AT_CYCLE_99":
        return ("silent", None)  # (1a)
    if lifecycle == "EVOLUTION_PENDING" and ret != "held":
        return ("silent", None)  # (1c) running window
    if in_p3:
        return ("silent", None)  # (2)
    if not guards:
        return ("silent", None)  # (3)
    if ret == "absent":
        return ("silent", None)  # (4) no return attempted
    if ret == "unverified":
        return ("code", _RET)  # (4) fail-closed
    if locked:
        return ("code", _LOCK)  # (5)
    if g >= 99:
        return ("code", _LIMIT)  # (6)
    return ("admit", None)  # (7 n/a single) (8 first) (9)


def test_single_candidate_exhaustive() -> None:
    count = 0
    for lifecycle, ret, guards, locked, g, in_p3 in itertools.product(
        _LIFES, _RETS, (True, False), (True, False), (98, 99), (True, False)
    ):
        if lifecycle == "EVOLUTION_PENDING" and locked:
            continue  # pruned: State invariant forbids PENDING + locked
        st15 = (SuccessorLock(g, True),) if locked else None
        p3 = (g,) if in_p3 else None
        state = dataclasses.replace(
            _empty_state(),
            st02_generation_states=(GenerationState(g, lifecycle),),
            st15_successor_locks=st15,
            st16_evolution_candidate_windows=(_win(g, ret, guards),),
            p3_decisions=p3,
            effective_generation_limit=None,
        )
        new, report = apply_evolution(state, [])
        kind, code = _expected(lifecycle, ret, guards, locked, g, in_p3)
        count += 1
        if kind == "silent":
            assert report.status == "NO_OP", (lifecycle, ret, guards, locked, g, in_p3)
            assert report.reason_codes == ()
            assert _unchanged(state, new)
        elif kind == "code":
            assert report.status == "APPLIED"
            assert report.reason_codes == (code,), (lifecycle, ret, locked, g)
            assert _unchanged(state, new)
        else:
            assert report.status == "APPLIED"
            assert report.reason_codes == ()
            assert _locked(new, g) is True
            assert _life(new, g) == "SUCCESSOR_CREATED"
            assert _life(new, g + 1) == "CREATED"
    assert count == 120  # 144 combos - 24 pruned (PENDING + locked)


def test_multi_generation_single_admission() -> None:
    for second in ("present", "absent"):
        st02 = [GenerationState(0, "ACTIVE")]
        st16 = [_win(0, "held", True)]
        if second == "present":
            st02.append(GenerationState(2, "ACTIVE"))
            st16.append(_win(2, "held", True))
        state = dataclasses.replace(
            _empty_state(),
            st02_generation_states=tuple(st02),
            st16_evolution_candidate_windows=tuple(st16),
            effective_generation_limit=None,
        )
        new, report = apply_evolution(state, [])
        assert report.status == "APPLIED"
        assert _locked(new, 0) is True
        assert _life(new, 0) == "SUCCESSOR_CREATED"
        if second == "present":
            assert report.reason_codes == (_INFLIGHT,)  # exactly one block
            assert _locked(new, 2) is False
        else:
            assert report.reason_codes == ()


def test_multi_generation_pending_blocks_in_flight() -> None:
    state = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(
            GenerationState(0, "EVOLUTION_PENDING"),
            GenerationState(1, "ACTIVE"),
        ),
        st16_evolution_candidate_windows=(
            _win(0, "unverified", True),  # running window (§4.2) — silent
            _win(1, "held", True),
        ),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "APPLIED"
    assert report.reason_codes == (_INFLIGHT,)  # §4.3 basket-in-flight
    assert _gen_ids(new) == [0, 1]  # no admission
    assert _life(new, 0) == "EVOLUTION_PENDING"


def test_exhaustive_determinism() -> None:
    state = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(
            GenerationState(0, "ACTIVE"),
            GenerationState(2, "ACTIVE"),
        ),
        st16_evolution_candidate_windows=(
            _win(0, "held", True),
            _win(2, "held", True),
        ),
    )
    a, _ = apply_evolution(state, [])
    b, _ = apply_evolution(state, [])
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )
