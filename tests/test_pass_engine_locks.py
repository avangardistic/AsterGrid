"""P2 locks: exhaustive bounded over <=2 generations, determinism (Phase 7d).

Markers are set DIRECTLY on synthetic States — no envelope interpretation.
"""

import dataclasses
import itertools
import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager

from astergrid.core.fold import _empty_state
from astergrid.core.serialization import canonical_dumps
from astergrid.core.state import State
from astergrid.core.transitions import (
    P2Attempts,
    P2LocksState,
    ReasonCode,
    apply_locks,
)

_EVO_LOCK = ReasonCode.EVOLUTION_IN_FLIGHT_LOCKED.value
_CYC_LOCK = ReasonCode.CYCLE_TRANSITION_IN_FLIGHT_LOCKED.value


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


def _state_with(locks: P2LocksState, attempts: P2Attempts) -> State:
    return dataclasses.replace(_empty_state(), p2_locks=locks, p2_attempts=attempts)


def test_p2_none_markers_is_noop() -> None:
    state = _empty_state()
    new_state, report = apply_locks(state, [])
    assert report.status == "NO_OP"
    assert canonical_dumps(new_state.to_canonical_obj()) == canonical_dumps(
        state.to_canonical_obj()
    )


def test_p2_exhaustive_bounded() -> None:
    bools = (False, True)
    for evo_flight, evo_attempt in itertools.product(bools, bools):
        for c0f, c0a, c1f, c1a in itertools.product(bools, repeat=4):
            locks = P2LocksState(
                evolution_in_flight=evo_flight,
                cycle_in_flight_by_generation=((0, c0f), (1, c1f)),
            )
            attempts = P2Attempts(
                evolution_attempted=evo_attempt,
                cycle_attempted_by_generation=((0, c0a), (1, c1a)),
            )
            new_state, report = apply_locks(_state_with(locks, attempts), [])
            assert report.status == "APPLIED"
            codes = report.reason_codes
            new_locks = new_state.p2_locks
            assert new_locks is not None

            # Evolution lock: attempt while in-flight -> blocked; else admitted.
            if evo_attempt and evo_flight:
                assert _EVO_LOCK in codes
                assert new_locks.evolution_in_flight is True
            elif evo_attempt and not evo_flight:
                assert _EVO_LOCK not in codes
                assert new_locks.evolution_in_flight is True  # admitted
            else:
                assert _EVO_LOCK not in codes
                assert new_locks.evolution_in_flight is evo_flight  # unchanged

            # Cycle lock per generation.
            cyc = dict(new_locks.cycle_in_flight_by_generation)
            for gid, flight, attempt in ((0, c0f, c0a), (1, c1f, c1a)):
                if attempt and not flight:
                    assert cyc[gid] is True  # admitted
                else:
                    assert cyc[gid] is flight  # blocked (stays True) or untouched

            blocked_cycle = (c0a and c0f) or (c1a and c1f)
            assert (_CYC_LOCK in codes) is blocked_cycle


def test_p2_determinism() -> None:
    locks = P2LocksState(
        evolution_in_flight=False, cycle_in_flight_by_generation=((0, True),)
    )
    attempts = P2Attempts(
        evolution_attempted=True, cycle_attempted_by_generation=((0, True),)
    )
    state = _state_with(locks, attempts)
    a, _ = apply_locks(state, [])
    b, _ = apply_locks(state, [])
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )


def test_p2_is_clock_free() -> None:
    with _no_ambient():
        apply_locks(_state_with(P2LocksState(), P2Attempts()), [])
