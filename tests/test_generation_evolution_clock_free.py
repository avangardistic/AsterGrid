"""apply_evolution is clock/randomness free (Phase 7e)."""

import dataclasses
import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager

from hypergrid.core.fold import _empty_state
from hypergrid.core.transitions import (
    EvolutionCandidateWindow,
    GenerationState,
    SuccessorLock,
    apply_evolution,
)


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


def test_apply_evolution_is_clock_free() -> None:
    state = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(
            GenerationState(0, "ACTIVE"),
            GenerationState(5, "SUCCESSOR_CREATED"),
        ),
        st15_successor_locks=(SuccessorLock(5, True),),
        st16_evolution_candidate_windows=(
            EvolutionCandidateWindow(0, "SL", (1, 2), 2, True, True, True),
            EvolutionCandidateWindow(5, "BU", (1, 2), 2, True, True, True),
        ),
    )
    with _no_ambient():
        new, report = apply_evolution(state, [])
    # G0 admits (creates G1); G5 blocked by its permanent lock. We only assert the
    # call touches no clock/randomness and produces a valid State.
    assert report.status == "APPLIED"
    assert new.st02_generation_states is not None
