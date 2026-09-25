"""Real P0 wiring into run_pass (7h-1): seven stages, upserts, write-only, envelopes."""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.event_log import InMemoryEventLog
from hypergrid.core.events import CommandEvent, ObservedMeta
from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import State
from hypergrid.core.transitions import (
    ActualExposureState,
    ExpectedExposureState,
    ExposureClass,
    ExposureDeltaState,
    HedgeExecution,
    HedgeIntent,
    IntentTag,
    LevelState,
    PerLevelObservation,
    apply_p0,
)
from hypergrid.core.transitions.observation_state import P0ObservationMarkers

_STAGES = ("P0", "P1", "P2", "P3", "P4", "P5", "P6")
_TS = "2026-09-25T00:00:00.000000Z"
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


def _obs(direction: str, level_id: int, **over: object) -> PerLevelObservation:
    fields: dict[str, object] = {
        "generation_id": 0,
        "cycle_id": 0,
        "direction": direction,
        "level_id": level_id,
        "lifecycle": "ORDER_ACTIVE",
        "filled_quantity": Decimal("1.0"),
        "order_filled": False,
        "position_delta_verified": False,
    }
    fields.update(over)
    return PerLevelObservation(**fields)  # type: ignore[arg-type]


def _markers(**over: object) -> P0ObservationMarkers:
    fields: dict[str, object] = {
        "observations": (),
        "net_position": Decimal("0"),
        "mark_price": Decimal("50000"),
        **_EXTERNALS,
    }
    fields.update(over)
    return P0ObservationMarkers(**fields)  # type: ignore[arg-type]


# --------------------------- seven stages ---------------------------


def test_seven_stages_p0_first_applied_with_markers() -> None:
    rows = (_level("BU", 1),)
    state = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=rows,
        p0_observation_markers=_markers(observations=(_obs("BU", 1),)),
    )
    _, report = run_pass(state, [])
    names = [s.stage for s in report.stages]
    assert names == list(_STAGES)
    assert "P5_EXEC" not in names
    by = {s.stage: s for s in report.stages}
    assert by["P0"].status == "APPLIED"
    assert by["P6"].status == "STUBBED"


def test_p0_no_op_without_markers() -> None:
    state = _empty_state()
    before = canonical_dumps(state.to_canonical_obj())
    new_state, report = run_pass(state, [])
    p0 = {s.stage: s for s in report.stages}["P0"]
    assert p0.status == "NO_OP"
    assert p0.reason_codes == ()
    assert p0.notes == "p0 markers absent: no observation recorded"
    assert canonical_dumps(new_state.to_canonical_obj()) == before


# --------------------------- upsert rules ---------------------------


def test_unknown_identity_fails_closed() -> None:
    state = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=(_level("BU", 1),),
        p0_observation_markers=_markers(observations=(_obs("SL", 5),)),
    )
    with pytest.raises(ValueError):
        run_pass(state, [])


def test_duplicate_identities_rejected_at_construction() -> None:
    with pytest.raises(ValueError):
        _markers(observations=(_obs("BU", 1), _obs("BU", 1)))


def test_upsert_preserves_order_and_touches_only_target() -> None:
    rows = (_level("BU", 1), _level("BU", 2), _level("SL", 1))
    state = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=rows,
        p0_observation_markers=_markers(
            observations=(
                _obs(
                    "BU", 2, lifecycle="PARTIALLY_FILLED", filled_quantity=Decimal("7")
                ),
            )
        ),
    )
    new_state, _ = run_pass(state, [])
    out = new_state.st04_level_pipeline_states or ()
    keys = [(r.direction, r.level_id) for r in out]
    assert keys == [("BU", 1), ("BU", 2), ("SL", 1)]  # order preserved
    assert out[0].filled_quantity is None and out[2].filled_quantity is None
    assert out[1].filled_quantity == Decimal("7")
    assert out[1].lifecycle == "PARTIALLY_FILLED"


# --------------------------- write-only (junk independence) ---------------------


def _junk_state(base: State) -> State:
    return dataclasses.replace(
        base,
        st07_expected_exposure=ExpectedExposureState(Decimal("99")),
        st08_actual_exposure=ActualExposureState(Decimal("88"), "clearinghouseState"),
        st09_exposure_delta=ExposureDeltaState(
            expected_value=Decimal("99"),
            actual_value=Decimal("88"),
            delta=Decimal("11"),
            classification=ExposureClass.ESCALATE,
            is_acute=True,
        ),
        st23_mirror_targets_hedge_intents=HedgeIntent(
            IntentTag.EXPOSURE_CORRECTION_INTENT,
            Decimal("11"),
            True,
            HedgeExecution.IOC,
        ),
    )


def test_p0_is_write_only_ignores_st07_08_09_23() -> None:
    rows = (_level("BU", 1),)
    clean = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=rows,
        p0_observation_markers=_markers(observations=(_obs("BU", 1),)),
    )
    junky = _junk_state(clean)
    clean_out, clean_rep = apply_p0(clean, [])
    junk_out, junk_rep = apply_p0(junky, [])
    # P0's report is identical (P0 emits no verdict, reads nothing from st07-23).
    assert clean_rep.to_canonical_obj() == junk_rep.to_canonical_obj()
    # The fields P0 WRITES are identical regardless of the junk it did not read.
    assert clean_out.st04_level_pipeline_states == junk_out.st04_level_pipeline_states
    assert clean_out.st19_market_observation_cache == (
        junk_out.st19_market_observation_cache
    )
    assert clean_out.p1_exposure_markers == junk_out.p1_exposure_markers


# --------------------------- envelope independence ---------------------


def test_envelope_independence() -> None:
    rows = (_level("BU", 1),)
    state = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=rows,
        p0_observation_markers=_markers(observations=(_obs("BU", 1),)),
    )
    log = InMemoryEventLog()
    meta = ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)
    for i in range(3):
        log.append(CommandEvent(cloid=f"c{i}", action="submit", tif="Alo"), meta)
    envelopes = list(log.read_all())
    s_empty, r_empty = run_pass(state, [])
    s_full, r_full = run_pass(state, envelopes)
    by_empty = {s.stage: s for s in r_empty.stages}["P0"]
    by_full = {s.stage: s for s in r_full.stages}["P0"]
    assert by_empty.to_canonical_obj() == by_full.to_canonical_obj()
    assert canonical_dumps(s_empty.to_canonical_obj()) == canonical_dumps(
        s_full.to_canonical_obj()
    )
