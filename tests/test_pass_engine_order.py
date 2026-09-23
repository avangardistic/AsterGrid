"""Pass engine: seven stages P0..P6 in order, stub/real split, purity (Phase 7d)."""

import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import PassReport, run_pass
from hypergrid.core.serialization import canonical_dumps

# Strategy.md §4.7 defines seven passes, P0 through P6.
_STAGES = ("P0", "P1", "P2", "P3", "P4", "P5", "P6")
_STUBBED = ("P0", "P1", "P5", "P6")
_REAL = ("P2", "P3", "P4")


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
    _, report = run_pass(_empty_state(), [])
    assert isinstance(report, PassReport)
    assert tuple(s.stage for s in report.stages) == _STAGES


def test_stub_and_real_status_split() -> None:
    # markers all None -> real stages report NO_OP, stubs report STUBBED.
    _, report = run_pass(_empty_state(), [])
    by_stage = {s.stage: s for s in report.stages}
    for stage in _STUBBED:
        assert by_stage[stage].status == "STUBBED"
    for stage in _REAL:
        assert by_stage[stage].status in ("APPLIED", "NO_OP")
        assert by_stage[stage].status == "NO_OP"  # markers None => NO_OP


def test_stubs_pass_state_through_unchanged() -> None:
    state = _empty_state()  # all P2/P3/P4 markers None
    before = canonical_dumps(state.to_canonical_obj())
    new_state, _ = run_pass(state, [])
    assert canonical_dumps(new_state.to_canonical_obj()) == before


def test_empty_envelopes_leaves_canonical_state_unchanged() -> None:
    state = _empty_state()
    before = canonical_dumps(state.to_canonical_obj())
    new_state, _ = run_pass(state, iter([]))
    assert canonical_dumps(new_state.to_canonical_obj()) == before


def test_run_pass_is_clock_and_randomness_free() -> None:
    with _no_ambient():
        state, report = run_pass(_empty_state(), [])
    assert len(report.stages) == 7
    assert state.event_count == 0


def test_report_is_canonical_serializable() -> None:
    _, report = run_pass(_empty_state(), [])
    canonical_dumps(report.to_canonical_obj())
