"""apply_cycle is clock/randomness free (Phase 7f)."""

import dataclasses
import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from hypergrid.core.fold import _empty_state
from hypergrid.core.transitions import (
    CycleState,
    CycleTerminalMarkers,
    GenerationState,
    NonOverlapData,
    apply_cycle,
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


def test_apply_cycle_is_clock_free() -> None:
    data = NonOverlapData(
        old_reference_price=Decimal("100000"),
        old_terminal_execution_price=Decimal("100000"),
        new_level_prices=(Decimal("100100"), Decimal("100200")),
        direction="BU",
        live_same_group_prices=(),
        step_bps=Decimal("10"),
        tick_size=Decimal("0.1"),
    )
    marker = CycleTerminalMarkers(
        generation_id=0,
        cycle_id=0,
        terminal_event_verified=True,
        exhausted_side_pending_cancelled=True,
        authoritative_state_reconciled=True,
        ladder_gate_passed=True,
        captured_reference_price=Decimal("100010"),
        nominal_reference_price=Decimal("100000"),
        reference_price_tolerance_bps=Decimal("3.3"),
        reference_derivation="TERMINAL_EXECUTION",
        non_overlap_data=data,
    )
    state = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        st03_cycle_states=(CycleState(0, 0, "ACTIVE"),),
        cycle_terminal_markers=(marker,),
    )
    with _no_ambient():
        new, report = apply_cycle(state, [])
    assert report.status == "APPLIED"
    assert new.st03_cycle_states is not None
