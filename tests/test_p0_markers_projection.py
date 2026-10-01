"""p1_exposure_markers projection by P0 (R11) + end-to-end P0->P1 pipeline (7h-1)."""

import dataclasses
from decimal import Decimal

from astergrid.core.fold import _empty_state
from astergrid.core.pass_engine import run_pass
from astergrid.core.transitions import (
    LevelFillState,
    LevelState,
    PerLevelObservation,
    build_exposure_singletons,
    project_p1_markers,
)
from astergrid.core.transitions.observation_state import P0ObservationMarkers

_EXTERNALS: dict[str, object] = {
    "tau_acc": Decimal("0.00005"),
    "min_notional_usd": Decimal("10"),
    "max_exposure_imbalance": Decimal("3"),
    "emergency_tolerance": Decimal("5"),
    "margin_distance": Decimal("100"),
    "normal_tolerance": Decimal("1"),
    "transient_tolerance": Decimal("3"),
}


def _level(direction: str, level_id: int, **over: object) -> LevelState:
    fields: dict[str, object] = {
        "generation_id": 0,
        "cycle_id": 0,
        "direction": direction,
        "level_id": level_id,
        "target_price": Decimal("50000"),
        "is_protection_locked": False,
    }
    fields.update(over)
    return LevelState(**fields)  # type: ignore[arg-type]


def test_projection_deterministic_same_in_same_out() -> None:
    rows = (
        _level("BU", 1, filled_quantity=Decimal("9.25"), lifecycle="POSITION_VERIFIED"),
    )
    a = project_p1_markers(
        level_states=rows,
        net_position=Decimal("2.25"),
        mark_price=Decimal("50000"),
        **_EXTERNALS,  # type: ignore[arg-type]
    )
    b = project_p1_markers(
        level_states=rows,
        net_position=Decimal("2.25"),
        mark_price=Decimal("50000"),
        **_EXTERNALS,  # type: ignore[arg-type]
    )
    assert a.to_canonical_obj() == b.to_canonical_obj()


def test_unobserved_rows_excluded() -> None:
    rows = (
        # fully observed -> included
        _level("BU", 1, filled_quantity=Decimal("4.0"), lifecycle="FILLED"),
        # lifecycle observed, quantity None -> excluded
        _level("BU", 2, lifecycle="ORDER_ACTIVE"),
        # quantity observed, lifecycle None -> excluded
        _level("SL", 1, filled_quantity=Decimal("1.0")),
        # neither -> excluded
        _level("SL", 2),
    )
    markers = project_p1_markers(
        level_states=rows,
        net_position=Decimal("0"),
        mark_price=Decimal("50000"),
        **_EXTERNALS,  # type: ignore[arg-type]
    )
    assert len(markers.level_fills) == 1
    only = markers.level_fills[0]
    assert (only.direction, only.level_id) == ("BU", 1)
    assert only.filled_quantity == Decimal("4.0")


def test_seven_externals_carried_verbatim() -> None:
    markers = project_p1_markers(
        level_states=(),
        net_position=Decimal("-2.5"),
        mark_price=Decimal("50000"),
        **_EXTERNALS,  # type: ignore[arg-type]
    )
    assert markers.level_fills == ()
    assert markers.net_position == Decimal("-2.5")
    for name, value in _EXTERNALS.items():
        assert getattr(markers, name) == value


def test_end_to_end_p0_then_p1_pipeline() -> None:
    # Distinctive values no 7g-3b test uses: expected +9.25, actual 2.25, Δ = 7.0.
    geometry = (
        _level("BU", 1),  # pre-observation row (target_price/lock known, fill None)
    )
    p0_markers = P0ObservationMarkers(
        observations=(
            PerLevelObservation(
                generation_id=0,
                cycle_id=0,
                direction="BU",
                level_id=1,
                lifecycle="POSITION_VERIFIED",
                filled_quantity=Decimal("9.25"),
                order_filled=True,
                position_delta_verified=True,
            ),
        ),
        net_position=Decimal("2.25"),
        mark_price=Decimal("50000"),
        **_EXTERNALS,  # type: ignore[arg-type]
    )
    state = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=geometry,
        p0_observation_markers=p0_markers,
    )
    new_state, report, _ = run_pass(state, [])
    by = {s.stage: s for s in report.stages}
    assert by["P0"].status == "APPLIED"
    assert by["P1"].status == "APPLIED"

    # P1 consumed P0's PROJECTION, not test-set p1 markers: the singletons match a
    # direct Part-A call on the row P0 projected (BU +9.25).
    exp, act, delta = build_exposure_singletons(
        level_fills=(
            LevelFillState(0, 0, "BU", 1, Decimal("9.25"), "POSITION_VERIFIED"),
        ),
        net_position=Decimal("2.25"),
        normal_tolerance=Decimal("1"),
        transient_tolerance=Decimal("3"),
        max_exposure_imbalance=Decimal("3"),
        margin_distance=Decimal("100"),
        emergency_tolerance=Decimal("5"),
    )
    assert new_state.st07_expected_exposure == exp
    assert new_state.st08_actual_exposure == act
    assert new_state.st09_exposure_delta == delta
    assert new_state.st09_exposure_delta.delta == Decimal("7.0")  # raw Δ
    # ST-04 row now carries the observed fill/lifecycle.
    row = (new_state.st04_level_pipeline_states or ())[0]
    assert row.filled_quantity == Decimal("9.25")
    assert row.lifecycle == "POSITION_VERIFIED"
