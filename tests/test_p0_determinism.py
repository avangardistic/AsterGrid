"""Real P0 determinism (7h-1): byte-identical outputs, no input mutation."""

import dataclasses
from decimal import Decimal

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import State
from hypergrid.core.transitions import LevelState, PerLevelObservation
from hypergrid.core.transitions.observation_state import P0ObservationMarkers


def _state() -> State:
    rows = (
        LevelState(0, 0, "BU", 1, Decimal("50000"), False),
        LevelState(0, 0, "SL", 1, Decimal("49000"), False),
    )
    markers = P0ObservationMarkers(
        observations=(
            PerLevelObservation(
                0, 0, "BU", 1, "POSITION_VERIFIED", Decimal("3.5"), True, True
            ),
            PerLevelObservation(
                0, 0, "SL", 1, "ORDER_ACTIVE", Decimal("0"), False, False
            ),
        ),
        net_position=Decimal("1.5"),
        mark_price=Decimal("50000"),
        tau_acc=Decimal("0.00005"),
        min_notional_usd=Decimal("10"),
        max_exposure_imbalance=Decimal("3"),
        emergency_tolerance=Decimal("5"),
        margin_distance=Decimal("100"),
        normal_tolerance=Decimal("1"),
        transient_tolerance=Decimal("3"),
    )
    return dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=rows,
        p0_observation_markers=markers,
    )


def test_identical_inputs_byte_identical_outputs() -> None:
    s1, r1, _ = run_pass(_state(), [])
    s2, r2, _ = run_pass(_state(), [])
    assert canonical_dumps(s1.to_canonical_obj()) == canonical_dumps(
        s2.to_canonical_obj()
    )
    assert canonical_dumps(r1.to_canonical_obj()) == canonical_dumps(
        r2.to_canonical_obj()
    )


def test_no_input_mutation() -> None:
    state = _state()
    before = canonical_dumps(state.to_canonical_obj())
    run_pass(state, [])
    after = canonical_dumps(state.to_canonical_obj())
    assert before == after
