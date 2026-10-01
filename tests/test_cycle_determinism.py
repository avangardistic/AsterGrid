"""apply_cycle determinism + frozen guarantees (Phase 7f)."""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.fold import _empty_state
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import State
from hypergrid.core.transitions import (
    CycleState,
    CycleTerminalMarkers,
    GenerationState,
    NonOverlapData,
    apply_cycle,
)


def _rich() -> State:
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
    return dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        st03_cycle_states=(CycleState(0, 0, "ACTIVE"),),
        cycle_terminal_markers=(marker,),
    )


def test_apply_cycle_byte_identical() -> None:
    state = _rich()
    a, ra = apply_cycle(state, [])
    b, rb = apply_cycle(state, [])
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )
    assert ra.to_canonical_obj() == rb.to_canonical_obj()


def test_returned_state_is_frozen() -> None:
    state, _ = apply_cycle(_rich(), [])
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.event_count = 9  # type: ignore[misc]


def test_report_is_frozen() -> None:
    _, report = apply_cycle(_rich(), [])
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.status = "X"  # type: ignore[misc]
