"""P6-real stage behavior (Phase 7h-4b-2, E2)."""

import dataclasses
import inspect
from decimal import Decimal

import pytest

from astergrid.core.fold import _empty_state
from astergrid.core.pass_engine import run_pass
from astergrid.core.serialization import canonical_dumps
from astergrid.core.state import State
from astergrid.core.transitions import (
    ArmPolicy,
    CycleState,
    CycleTerminalMarkers,
    GenerationState,
    IntentTag,
    LevelState,
    NonOverlapData,
    OperationalState,
    OrderState,
    P6ArmInput,
    P6CancelInput,
    P6IssuanceInput,
    ReferencePriceRecord,
    apply_p6,
    construct_order_intent,
)


def _order(
    cloid: str,
    lifecycle: str,
    *,
    gen: int = 0,
    cyc: int = 0,
    level: int = 1,
    direction: str = "BU",
    size: str = "1",
    tag: IntentTag = IntentTag.ENTRY_INTENT,
) -> OrderState:
    from astergrid.core.transitions import OrderType

    intent = construct_order_intent(
        cloid=cloid,
        target_generation_id=gen,
        target_cycle_id=cyc,
        target_level_id=level,
        target_direction=direction,
        order_type=OrderType.LIMIT,
        requested_size=Decimal(size),
        requested_price=Decimal("50000"),
        intent_tag=tag,
        acute=False,
    )
    return OrderState(intent=intent, lifecycle=lifecycle)


def _level(
    *,
    gen: int = 0,
    cyc: int = 0,
    direction: str = "BU",
    level: int = 1,
    locked: bool = False,
    lifecycle: str | None = None,
) -> LevelState:
    return LevelState(
        generation_id=gen,
        cycle_id=cyc,
        direction=direction,
        level_id=level,
        target_price=Decimal("50000"),
        is_protection_locked=locked,
        lifecycle=lifecycle,
    )


def _arm(cloid: str, **over: object) -> P6ArmInput:
    base: dict[str, object] = {
        "cloid": cloid,
        "generation_disabled": False,
        "book_depth_at_target": Decimal("100"),
        "distance_bps": 50,
        "min_order_size": Decimal("0.1"),
        "margin_available": Decimal("100"),
        "margin_required": Decimal("10"),
        "exposure_caps_ok": True,
        "open_order_count": 0,
        "price_normalized_ok": True,
        "size_normalized_ok": True,
        "market_state": OperationalState.ACTIVE,
        "net_expected_edge_bps": Decimal("5"),
        "policy": ArmPolicy.AUTO,
        "timeout_s": 30,
        "tif": "Gtc",
        "expires_after": 60,
        "intent_log_seq": 0,
    }
    base.update(over)
    return P6ArmInput(**base)  # type: ignore[arg-type]


def _st(**kw: object) -> State:
    return dataclasses.replace(_empty_state(), **kw)  # type: ignore[arg-type]


# --------------------------- empty / shape ---------------------------


def test_empty_state_no_op() -> None:
    _, report, subs, emitted = apply_p6(_empty_state())
    assert report.stage == "P6"  # apply_p6 returns a single StageReport
    assert report.status == "NO_OP"
    assert report.notes == "P6: no sub-decisions"
    assert subs == ()
    assert emitted == ()


def test_run_pass_three_tuple_shape() -> None:
    _state, report, emitted = run_pass(_empty_state(), [])
    assert isinstance(emitted, tuple)
    assert emitted == ()
    assert {s.stage for s in report.stages} == {
        "P0",
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6",
    }


# --------------------------- B3.1 cancel ---------------------------


def _completed_cycle_state(
    order_lc: str = "ORDER_ACTIVE", with_input: bool = True
) -> State:
    kw: dict[str, object] = {
        "st03_cycle_states": (CycleState(0, 0, "COMPLETED"),),
        "st05_order_intents_and_outcomes": (_order("c1", order_lc),),
    }
    if with_input:
        kw["p6_cancel_inputs"] = (
            P6CancelInput(cloid="c1", expires_after=60, intent_log_seq=0),
        )
    return _st(**kw)


def test_cancel_emitted_with_defaults_and_notes() -> None:
    _, _report, subs, emitted = apply_p6(_completed_cycle_state())
    assert len(emitted) == 1
    assert emitted[0].action == "cancel"
    assert emitted[0].tif == "Gtc"  # Item-3 default
    assert emitted[0].expires_after == 60
    cancel = [s for s in subs if s.sub_kind == "CANCEL_SELECT"]
    assert len(cancel) == 1
    assert cancel[0].outcome == "EMITTED"
    assert cancel[0].reason_codes == ("EXHAUSTED_TRAVERSAL_CANCEL",)
    assert cancel[0].notes == "exhausted G00-C00-BU: cancel c1"


def test_cancel_needs_input_row_silent() -> None:
    _, _report, subs, emitted = apply_p6(_completed_cycle_state(with_input=False))
    assert emitted == ()
    assert subs == ()  # D15 silent, no record


def test_cancel_both_directions_breadth() -> None:
    state = _st(
        st03_cycle_states=(CycleState(0, 0, "COMPLETED"),),
        st05_order_intents_and_outcomes=(
            _order("c1", "ORDER_ACTIVE", direction="BU"),
            _order("c2", "ORDER_ACTIVE", direction="SL"),
        ),
        p6_cancel_inputs=(
            P6CancelInput(cloid="c1", expires_after=60, intent_log_seq=0),
            P6CancelInput(cloid="c2", expires_after=60, intent_log_seq=0),
        ),
    )
    _, _, _subs, emitted = apply_p6(state)
    assert {c.cloid for c in emitted} == {"c1", "c2"}


def test_cancel_non_completed_and_non_resting_excluded() -> None:
    active = _st(
        st03_cycle_states=(CycleState(0, 0, "ACTIVE"),),
        st05_order_intents_and_outcomes=(_order("c1", "ORDER_ACTIVE"),),
        p6_cancel_inputs=(
            P6CancelInput(cloid="c1", expires_after=60, intent_log_seq=0),
        ),
    )
    assert apply_p6(active)[3] == ()  # non-COMPLETED cycle -> no cancel
    # already-CANCELLED (non-resting) excluded even on a COMPLETED cycle.
    done = _completed_cycle_state(order_lc="CANCELLED")
    assert apply_p6(done)[3] == ()


# --------------------------- B3.2 arming ---------------------------


def _arm_state(
    order_lc: str = "INTENT_CREATED",
    *,
    level_kw: dict[str, object] | None = None,
    arm_over: dict[str, object] | None = None,
    with_level: bool = True,
    with_input: bool = True,
) -> State:
    kw: dict[str, object] = {
        "st05_order_intents_and_outcomes": (_order("a1", order_lc),),
    }
    if with_level:
        kw["st04_level_pipeline_states"] = (_level(**(level_kw or {})),)  # type: ignore[arg-type]
    if with_input:
        kw["p6_arm_inputs"] = (_arm("a1", **(arm_over or {})),)
    return _st(**kw)


def test_arm_armed_emits_submission() -> None:
    _, _, subs, emitted = apply_p6(_arm_state())
    arming = [s for s in subs if s.sub_kind == "ARMING_EVAL"]
    emit = [s for s in subs if s.sub_kind == "SUBMISSION_EMIT"]
    assert arming[0].outcome == "ARMED"
    assert len(emitted) == 1
    assert emitted[0].action == "submit"
    assert emit[0].notes == "a1: submit tif=Gtc expires_after=60 seq=0"


def test_arm_blocked_records_code_no_emission() -> None:
    _, _, subs, emitted = apply_p6(_arm_state(arm_over={"exposure_caps_ok": False}))
    arming = next(s for s in subs if s.sub_kind == "ARMING_EVAL")
    assert arming.outcome == "BLOCKED"
    assert arming.reason_codes == ("GATE_5_EXPOSURE_CAPS",)
    assert emitted == ()


def test_arm_waiting_no_emission() -> None:
    _, _, subs, emitted = apply_p6(
        _arm_state(arm_over={"policy": ArmPolicy.SEMI, "decision": None})
    )
    arming = next(s for s in subs if s.sub_kind == "ARMING_EVAL")
    assert arming.outcome == "WAITING"
    assert emitted == ()


def test_arm_skips_silently() -> None:
    # locked level, non-{None,IDLE} level, join-miss, input-absent -> no record.
    assert (
        apply_p6(_arm_state(level_kw={"locked": True, "lifecycle": "LOCKED"}))[2] == ()
    )
    assert apply_p6(_arm_state(level_kw={"lifecycle": "ORDER_ACTIVE"}))[2] == ()
    assert apply_p6(_arm_state(with_level=False))[2] == ()
    assert apply_p6(_arm_state(with_input=False))[2] == ()


def test_arm_idle_level_arms() -> None:
    _, _, subs, _ = apply_p6(_arm_state(level_kw={"lifecycle": "IDLE"}))
    assert next(s for s in subs if s.sub_kind == "ARMING_EVAL").outcome == "ARMED"


def test_evaluate_mapping_order_size_from_requested() -> None:
    # requested_size=20 with book_depth 100, min_depth 10 -> depth gate fails (200>100).
    state = _st(
        st04_level_pipeline_states=(_level(),),
        st05_order_intents_and_outcomes=(_order("a1", "INTENT_CREATED", size="20"),),
        p6_arm_inputs=(_arm("a1"),),
    )
    arming = next(s for s in apply_p6(state)[2] if s.sub_kind == "ARMING_EVAL")
    assert arming.outcome == "BLOCKED"
    assert arming.reason_codes == ("GATE_1_DEPTH",)


def test_evaluate_mapping_intent_from_tag() -> None:
    # a CORRECTION arms even with generation_disabled + FROZEN (skips gate 9);
    # an ENTRY would be BLOCKED -> proves intent <- intent_tag.
    state = _st(
        st04_level_pipeline_states=(_level(),),
        st05_order_intents_and_outcomes=(
            _order("a1", "INTENT_CREATED", tag=IntentTag.EXPOSURE_CORRECTION_INTENT),
        ),
        p6_arm_inputs=(
            _arm(
                "a1",
                generation_disabled=True,
                market_state=OperationalState.FROZEN,
                policy=ArmPolicy.SEMI,
            ),
        ),
    )
    arming = next(s for s in apply_p6(state)[2] if s.sub_kind == "ARMING_EVAL")
    assert arming.outcome == "ARMED"  # correction inv.1, no wait


# --------------------------- B3.3 issuance ---------------------------


def _issue_state(
    edge_bu: bool = True,
    edge_sl: bool = True,
    *,
    cyc_lc: str = "ACTIVE",
    with_ref: bool = True,
    with_existing_level: bool = False,
) -> State:
    kw: dict[str, object] = {
        "st03_cycle_states": (CycleState(0, 6, cyc_lc),),
        "p6_issuance_inputs": (
            P6IssuanceInput(
                generation_id=0,
                cycle_id=6,
                grid_levels=6,
                step_bps=Decimal("10"),
                first_level_distance_bps=Decimal("20"),
                is_dominant_bu=True,
                is_dominant_sl=False,
                gen2_distance_multiplier=Decimal("2"),
                weak_side_first_level_multiplier=Decimal("1.5"),
                size_notional_usd=Decimal("5000"),
                edge_clears_floor_bu=edge_bu,
                edge_clears_floor_sl=edge_sl,
            ),
        ),
    }
    if with_ref:
        kw["st10_reference_prices"] = (
            ReferencePriceRecord(0, 6, Decimal("100000"), "TERMINAL_EXECUTION"),
        )
    if with_existing_level:
        kw["st04_level_pipeline_states"] = (_level(gen=0, cyc=6),)
    return _st(**kw)


def test_issuance_issued_both_sides() -> None:
    state, _, subs, _ = apply_p6(_issue_state())
    rows = state.st04_level_pipeline_states or ()
    assert len(rows) == 12  # 6 BU + 6 SL
    assert all(r.lifecycle is None and r.filled_quantity is None for r in rows)
    bu = [r for r in rows if r.direction == "BU"]
    assert bu[0].target_price == Decimal("100200")  # reference <- ST-10
    kinds = {s.sub_kind: s.outcome for s in subs}
    assert kinds["LADDER_ISSUANCE_BU"] == "ISSUED"
    assert kinds["LADDER_ISSUANCE_SL"] == "ISSUED"


def test_issuance_one_side_empty_no_recon_applied() -> None:
    state, report, subs, _ = apply_p6(_issue_state(edge_sl=False))
    rows = state.st04_level_pipeline_states or ()
    assert len(rows) == 6  # BU only
    outcomes = {s.sub_kind: s for s in subs}
    assert outcomes["LADDER_ISSUANCE_SL"].outcome == "EMPTY"
    assert outcomes["LADDER_ISSUANCE_SL"].reason_codes == ()  # NO RECON code
    assert report.status == "APPLIED"


def test_issuance_both_empty() -> None:
    state, _, subs, _ = apply_p6(_issue_state(edge_bu=False, edge_sl=False))
    assert state.st04_level_pipeline_states is None
    assert {s.outcome for s in subs} == {"EMPTY"}


def test_issuance_skips() -> None:
    assert apply_p6(_issue_state(cyc_lc="CREATED"))[2] == ()  # not ACTIVE
    assert apply_p6(_issue_state(with_ref=False))[2] == ()  # no ST-10
    assert apply_p6(_issue_state(with_existing_level=True))[2] == ()  # already issued


def test_dup_issuance_input_rejected_by_state() -> None:
    dup = P6IssuanceInput(
        generation_id=0,
        cycle_id=6,
        grid_levels=6,
        step_bps=Decimal("10"),
        first_level_distance_bps=Decimal("20"),
        is_dominant_bu=True,
        is_dominant_sl=False,
        gen2_distance_multiplier=Decimal("2"),
        weak_side_first_level_multiplier=Decimal("1.5"),
        size_notional_usd=Decimal("5000"),
        edge_clears_floor_bu=True,
        edge_clears_floor_sl=True,
    )
    with pytest.raises(ValueError):
        _st(p6_issuance_inputs=(dup, dup))


# --------------------------- ordering + notes + union + D11 ---------------------


def _combined_state() -> State:
    return _st(
        st03_cycle_states=(CycleState(0, 0, "COMPLETED"),),
        st04_level_pipeline_states=(_level(gen=1, cyc=0),),
        st05_order_intents_and_outcomes=(
            _order("a1", "INTENT_CREATED", gen=1),  # arms
            _order("z1", "ORDER_ACTIVE", gen=0),  # cancels
        ),
        p6_arm_inputs=(_arm("a1"),),
        p6_cancel_inputs=(
            P6CancelInput(cloid="z1", expires_after=60, intent_log_seq=0),
        ),
    )


def test_emitted_ordering_cross_kind() -> None:
    _, _, _, emitted = apply_p6(_combined_state())
    # cancel (sub_kind_order 0) before submit (1), regardless of cloid.
    assert [(c.action, c.cloid) for c in emitted] == [
        ("cancel", "z1"),
        ("submit", "a1"),
    ]


def test_sub_decisions_sorted_and_notes_and_union() -> None:
    _, report, subs, _ = apply_p6(_combined_state())
    assert [(s.sub_kind, s.subject) for s in subs] == [
        ("ARMING_EVAL", "a1"),
        ("CANCEL_SELECT", "z1"),
        ("SUBMISSION_EMIT", "a1"),
    ]
    assert report.notes == "P6: 1xCANCEL_SELECT, 1xARMING_EVAL, 1xSUBMISSION_EMIT"
    assert report.reason_codes == ("EXHAUSTED_TRAVERSAL_CANCEL",)  # first-seen union


def test_d11_no_event_log_import() -> None:
    import astergrid.core.pass_engine as pe
    import astergrid.core.transitions.p6_stage as p6

    for mod in (pe, p6):
        src = inspect.getsource(mod)
        assert "event_log" not in src
        assert "EventLogPort" not in src


def test_bool_guard_spot() -> None:
    with pytest.raises(ValueError):
        _arm("a1", edge_floor_bps=Decimal("1"), generation_disabled=1)


# --------------------------- E3 end-to-end (P5 -> P6 same pass) ----------------

_PASS_DATA = NonOverlapData(
    old_reference_price=Decimal("99900"),
    old_terminal_execution_price=Decimal("100000"),
    new_level_prices=(Decimal("100100"), Decimal("100200")),
    direction="BU",
    live_same_group_prices=(),
    step_bps=Decimal("10"),
    tick_size=Decimal("0.1"),
)


def _e3_state() -> State:
    marker = CycleTerminalMarkers(
        0,
        5,
        terminal_event_verified=True,
        exhausted_side_pending_cancelled=True,
        authoritative_state_reconciled=True,
        non_overlap_passed=True,
        ladder_gate_passed=True,
        captured_reference_price=Decimal("100010"),
        nominal_reference_price=Decimal("100000"),
        reference_price_tolerance_bps=Decimal("3.3"),
        reference_derivation="TERMINAL_EXECUTION",
        all_progression_orders_cancelled=True,
        non_overlap_data=_PASS_DATA,
    )
    return _st(
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        st03_cycle_states=(CycleState(0, 4, "COMPLETED"), CycleState(0, 5, "ACTIVE")),
        cycle_terminal_markers=(marker,),
        st04_level_pipeline_states=(_level(gen=0, cyc=2, lifecycle="IDLE"),),
        st05_order_intents_and_outcomes=(
            _order("a1", "INTENT_CREATED", gen=0, cyc=2),
            _order("k1", "ORDER_ACTIVE", gen=0, cyc=4),
        ),
        p6_arm_inputs=(_arm("a1"),),
        p6_cancel_inputs=(
            P6CancelInput(cloid="k1", expires_after=60, intent_log_seq=0),
        ),
        p6_issuance_inputs=(
            P6IssuanceInput(
                generation_id=0,
                cycle_id=6,
                grid_levels=6,
                step_bps=Decimal("10"),
                first_level_distance_bps=Decimal("20"),
                is_dominant_bu=True,
                is_dominant_sl=False,
                gen2_distance_multiplier=Decimal("2"),
                weak_side_first_level_multiplier=Decimal("1.5"),
                size_notional_usd=Decimal("5000"),
                edge_clears_floor_bu=True,
                edge_clears_floor_sl=True,
            ),
        ),
    )


def test_e3_end_to_end_p5_then_p6_same_pass() -> None:
    state = _e3_state()
    new, report, emitted = run_pass(state, [])
    by = {s.stage: s for s in report.stages}
    # P5 completed (0,5), created (0,6) ACTIVE + ST-10 (0,6).
    cyc = {
        (c.generation_id, c.cycle_id): c.lifecycle for c in new.st03_cycle_states or ()
    }
    assert cyc[(0, 5)] == "COMPLETED"
    assert cyc[(0, 6)] == "ACTIVE"
    assert (0, 6) in {
        (r.generation_id, r.cycle_id) for r in (new.st10_reference_prices or ())
    }
    # P6 issued (0,6) BU+SL rows on top of the pre-existing (0,2) level.
    gc = [
        (lvl.generation_id, lvl.cycle_id)
        for lvl in (new.st04_level_pipeline_states or ())
    ]
    assert gc.count((0, 6)) == 12
    assert (0, 2) in gc
    # emitted: cancel k1 (0) before submit a1 (1).
    assert [(c.action, c.cloid) for c in emitted] == [
        ("cancel", "k1"),
        ("submit", "a1"),
    ]
    assert by["P6"].status == "APPLIED"
    # sub_decisions sorted by (stage, kind, subject).
    kinds = [s.sub_kind for s in report.sub_decisions]
    assert kinds == sorted(kinds, key=lambda k: k)  # ascending within P6
    # determinism across two runs.
    n2, r2, _e2 = run_pass(state, [])
    assert canonical_dumps(new.to_canonical_obj()) == canonical_dumps(
        n2.to_canonical_obj()
    )
    assert canonical_dumps(report.to_canonical_obj()) == canonical_dumps(
        r2.to_canonical_obj()
    )
