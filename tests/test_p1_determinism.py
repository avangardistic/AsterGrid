"""Real P1 determinism + no input mutation (7g-3b)."""

import dataclasses
from decimal import Decimal

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.transitions import LevelFillState, P1ExposureMarkers


def _markers() -> P1ExposureMarkers:
    return P1ExposureMarkers(
        level_fills=(
            LevelFillState(0, 0, "BU", 1, Decimal("2.0"), "POSITION_VERIFIED"),
        ),
        net_position=Decimal("0.5"),
        tau_acc=Decimal("0.00005"),
        min_notional_usd=Decimal("10"),
        mark_price=Decimal("50000"),
        max_exposure_imbalance=Decimal("3"),
        emergency_tolerance=Decimal("5"),
        margin_distance=Decimal("100"),
        normal_tolerance=Decimal("1"),
        transient_tolerance=Decimal("3"),
    )


def test_byte_identical_state_and_report() -> None:
    state = dataclasses.replace(_empty_state(), p1_exposure_markers=_markers())
    s1, r1 = run_pass(state, [])
    s2, r2 = run_pass(state, [])
    assert canonical_dumps(s1.to_canonical_obj()) == canonical_dumps(
        s2.to_canonical_obj()
    )
    assert r1.to_canonical_obj() == r2.to_canonical_obj()


def test_no_input_mutation() -> None:
    markers = _markers()
    state = dataclasses.replace(_empty_state(), p1_exposure_markers=markers)
    before = canonical_dumps(state.to_canonical_obj())
    run_pass(state, [])
    assert canonical_dumps(state.to_canonical_obj()) == before
