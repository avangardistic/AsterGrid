"""Real P0 is clock/randomness-free (7h-1): patching time/random/os raises nothing."""

import dataclasses
import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.transitions import (
    LevelState,
    PerLevelObservation,
    apply_p0,
    extend_level_states,
    project_p1_markers,
)
from hypergrid.core.transitions.observation_state import P0ObservationMarkers

_EXTERNALS: dict[str, object] = {
    "tau_acc": Decimal("0.00005"),
    "min_notional_usd": Decimal("10"),
    "max_exposure_imbalance": Decimal("3"),
    "emergency_tolerance": Decimal("5"),
    "margin_distance": Decimal("100"),
    "normal_tolerance": Decimal("1"),
    "transient_tolerance": Decimal("3"),
}


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


def test_p0_and_part_a_functions_are_ambient_free() -> None:
    rows = (LevelState(0, 0, "BU", 1, Decimal("50000"), False),)
    obs = (
        PerLevelObservation(
            0, 0, "BU", 1, "POSITION_VERIFIED", Decimal("3.5"), True, True
        ),
    )
    markers = P0ObservationMarkers(
        observations=obs,
        net_position=Decimal("1.5"),
        mark_price=Decimal("50000"),
        **_EXTERNALS,  # type: ignore[arg-type]
    )
    state = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=rows,
        p0_observation_markers=markers,
    )
    with _no_ambient():
        run_pass(state, [])
        apply_p0(state, [])
        extended = extend_level_states(current=rows, observations=obs)
        project_p1_markers(
            level_states=extended,
            net_position=Decimal("1.5"),
            mark_price=Decimal("50000"),
            **_EXTERNALS,  # type: ignore[arg-type]
        )
