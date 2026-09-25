"""Real P1 wiring into run_pass (7g-3b): seven stages, write-only, envelopes unread."""

import dataclasses
from decimal import Decimal

from hypergrid.core.event_log import InMemoryEventLog
from hypergrid.core.events import CommandEvent, ObservedMeta
from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import State
from hypergrid.core.transitions import (
    ExposureClass,
    HedgeExecution,
    IntentTag,
    LevelFillState,
    P1ExposureMarkers,
    build_exposure_singletons,
)

_STAGES = ("P0", "P1", "P2", "P3", "P4", "P5", "P6")
_TS = "2026-09-25T00:00:00.000000Z"


def _markers(**over: object) -> P1ExposureMarkers:
    fields: dict[str, object] = {
        "level_fills": (
            LevelFillState(0, 0, "BU", 1, Decimal("2.0"), "POSITION_VERIFIED"),
        ),
        "net_position": Decimal("0.5"),
        "tau_acc": Decimal("0.00005"),
        "min_notional_usd": Decimal("10"),
        "mark_price": Decimal("50000"),
        "max_exposure_imbalance": Decimal("3"),
        "emergency_tolerance": Decimal("5"),
        "margin_distance": Decimal("100"),
        "normal_tolerance": Decimal("1"),
        "transient_tolerance": Decimal("3"),
    }
    fields.update(over)
    return P1ExposureMarkers(**fields)  # type: ignore[arg-type]


def _with(markers: P1ExposureMarkers) -> State:
    return dataclasses.replace(_empty_state(), p1_exposure_markers=markers)


def _p1(report_stages: tuple) -> object:
    return {s.stage: s for s in report_stages}["P1"]


def test_seven_stages_p1_second() -> None:
    _, report = run_pass(_with(_markers()), [])
    names = [s.stage for s in report.stages]
    assert names == list(_STAGES)
    assert "P5_EXEC" not in names
    by = {s.stage: s for s in report.stages}
    assert by["P0"].status == "STUBBED"
    assert by["P6"].status == "STUBBED"
    assert by["P1"].status == "APPLIED"


def test_markers_absent_no_op_unchanged() -> None:
    state = _empty_state()
    before = canonical_dumps(state.to_canonical_obj())
    new_state, report = run_pass(state, [])
    p1 = _p1(report.stages)
    assert p1.status == "NO_OP"
    assert p1.reason_codes == ()
    assert p1.notes == "p1 markers absent: no exposure evaluation"
    assert canonical_dumps(new_state.to_canonical_obj()) == before


def test_markers_present_writes_and_coheres() -> None:
    markers = _markers()
    new_state, report = run_pass(_with(markers), [])
    p1 = _p1(report.stages)
    # exposure singletons match a DIRECT writer call on the same inputs.
    exp, act, delta = build_exposure_singletons(
        level_fills=markers.level_fills,
        net_position=markers.net_position,
        normal_tolerance=markers.normal_tolerance,
        transient_tolerance=markers.transient_tolerance,
        max_exposure_imbalance=markers.max_exposure_imbalance,
        margin_distance=markers.margin_distance,
        emergency_tolerance=markers.emergency_tolerance,
    )
    assert new_state.st07_expected_exposure == exp
    assert new_state.st08_actual_exposure == act
    assert new_state.st09_exposure_delta == delta
    assert new_state.st09_exposure_delta.delta == Decimal("1.5")  # raw Δ, never Δ̂
    assert new_state.st09_exposure_delta.classification == ExposureClass.TRANSIENT
    assert new_state.st09_exposure_delta.is_acute is False
    # ST-23 hedge intent
    intent = new_state.st23_mirror_targets_hedge_intents
    assert intent is not None
    assert intent.amount == Decimal("1.5")  # Δ̂ == Δ here (above T_exit)
    assert intent.intent_tag == IntentTag.EXPOSURE_CORRECTION_INTENT
    assert intent.execution == HedgeExecution.PREFER_MAKER
    # codes exact + order: gate, (zeroed?), urgency
    assert p1.reason_codes == ("PROGRESSION_BLOCKED", "HEDGE_DEFERRED_TO_SECTION_10")
    assert p1.notes == "p1 gate=BLOCKED zeroed=false urgency=DEFERRED_10"


def test_acute_and_zeroed_paths() -> None:
    # acute path: margin_distance < 2·d_emergency -> IMMEDIATE_IOC.
    acute_markers = _markers(margin_distance=Decimal("0"))
    new_state, report = run_pass(_with(acute_markers), [])
    intent = new_state.st23_mirror_targets_hedge_intents
    assert intent is not None
    assert intent.execution == HedgeExecution.IOC
    assert "HEDGE_IMMEDIATE_IOC" in _p1(report.stages).reason_codes
    # zeroed path: sub-tradable residual -> FIX1_RESIDUAL_ZEROED + Δ̂ == 0.
    zero_markers = _markers(
        level_fills=(LevelFillState(0, 0, "BU", 1, Decimal("0.0001"), "FILLED"),),
        net_position=Decimal("0"),
    )
    z_state, z_report = run_pass(_with(zero_markers), [])
    z_intent = z_state.st23_mirror_targets_hedge_intents
    assert z_intent is not None
    assert z_intent.amount == Decimal("0")  # zeroed
    assert z_state.st09_exposure_delta.delta == Decimal("0.0001")  # raw Δ preserved
    assert "FIX1_RESIDUAL_ZEROED" in _p1(z_report.stages).reason_codes


def test_only_target_fields_change() -> None:
    markers = _markers()
    new_state, _ = run_pass(_with(markers), [])
    # every field except the four P1 writes (+ the markers input) is unchanged.
    written = {
        "st07_expected_exposure",
        "st08_actual_exposure",
        "st09_exposure_delta",
        "st23_mirror_targets_hedge_intents",
    }
    base = _with(markers)
    for f in dataclasses.fields(State):
        if f.name in written:
            continue
        assert getattr(new_state, f.name) == getattr(base, f.name), f.name


def test_envelopes_unread() -> None:
    markers = _markers()
    log = InMemoryEventLog()
    meta = ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)
    for i in range(3):
        log.append(CommandEvent(cloid=f"c{i}", action="submit", tif="Alo"), meta)
    envelopes = list(log.read_all())
    _, empty_report = run_pass(_with(markers), [])
    _, full_report = run_pass(_with(markers), envelopes)
    p1_empty = _p1(empty_report.stages)
    p1_full = _p1(full_report.stages)
    assert p1_empty.to_canonical_obj() == p1_full.to_canonical_obj()
