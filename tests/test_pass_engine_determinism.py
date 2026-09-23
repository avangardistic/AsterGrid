"""Pass engine determinism + frozen guarantees (Phase 7d)."""

import dataclasses

import pytest

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import State
from hypergrid.core.transitions import (
    P2Attempts,
    P2LocksState,
    P3CandidateMarkers,
    P4CandidateMarkers,
)


def _rich_state() -> State:
    return dataclasses.replace(
        _empty_state(),
        p2_locks=P2LocksState(
            evolution_in_flight=False, cycle_in_flight_by_generation=((0, True),)
        ),
        p2_attempts=P2Attempts(
            evolution_attempted=True,
            cycle_attempted_by_generation=((0, True), (1, False)),
        ),
        p3_candidates=P3CandidateMarkers(
            disable_candidates=(1,), evolution_candidates=(0, 1)
        ),
        p4_candidates=P4CandidateMarkers(
            evolution_candidates=(1, 0), cycle_candidates=((1, 0), (0, 1))
        ),
    )


def test_run_pass_byte_identical() -> None:
    state = _rich_state()
    a, _ = run_pass(state, [])
    b, _ = run_pass(state, [])
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )


def test_returned_state_is_frozen() -> None:
    state, _ = run_pass(_rich_state(), [])
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.event_count = 9  # type: ignore[misc]


def test_reports_are_frozen() -> None:
    _, report = run_pass(_rich_state(), [])
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.stages = ()  # type: ignore[misc]
    for stage in report.stages:
        with pytest.raises(dataclasses.FrozenInstanceError):
            stage.status = "X"  # type: ignore[misc]
