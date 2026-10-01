"""ST-04<->ST-05 coupling (Phase 7h-4b-2, B4/E2)."""

import dataclasses
from decimal import Decimal

import pytest

from astergrid.core.fold import _empty_state
from astergrid.core.serialization import canonical_dumps
from astergrid.core.state import State
from astergrid.core.transitions import (
    IntentTag,
    LevelState,
    OrderState,
    OrderType,
    apply_pipeline_coupling,
    construct_order_intent,
)


def _level(lifecycle: str | None = None, locked: bool = False) -> LevelState:
    return LevelState(
        generation_id=0,
        cycle_id=0,
        direction="BU",
        level_id=1,
        target_price=Decimal("50000"),
        is_protection_locked=locked,
        lifecycle=lifecycle,
    )


def _order(lifecycle: str, cloid: str = "c1") -> OrderState:
    intent = construct_order_intent(
        cloid=cloid,
        target_generation_id=0,
        target_cycle_id=0,
        target_level_id=1,
        target_direction="BU",
        order_type=OrderType.LIMIT,
        requested_size=Decimal("1"),
        requested_price=Decimal("50000"),
        intent_tag=IntentTag.ENTRY_INTENT,
        acute=False,
    )
    return OrderState(intent=intent, lifecycle=lifecycle)


def _state(level: LevelState | None, order: OrderState | None) -> State:
    kw: dict[str, object] = {}
    if level is not None:
        kw["st04_level_pipeline_states"] = (level,)
    if order is not None:
        kw["st05_order_intents_and_outcomes"] = (order,)
    return dataclasses.replace(_empty_state(), **kw)  # type: ignore[arg-type]


# --------------------------- passthroughs ---------------------------


def test_none_slot_passthroughs() -> None:
    s0 = _empty_state()
    assert apply_pipeline_coupling(s0) is s0  # both None
    s1 = _state(_level(), None)
    assert apply_pipeline_coupling(s1) is s1  # ST-05 None
    s2 = _state(None, _order("INTENT_CREATED"))
    assert apply_pipeline_coupling(s2) is s2  # ST-04 None


# --------------------------- B4.2 skip-cap ---------------------------


def test_skip_cap_raises() -> None:
    state = _state(_level(lifecycle="LEVEL_SKIPPED"), _order("INTENT_CREATED"))
    with pytest.raises(ValueError, match="RECONCILIATION_REQUIRED"):
        apply_pipeline_coupling(state)


def test_level_skipped_independence_matrix() -> None:
    for order_lc in (
        "ORDER_ACTIVE",
        "FILLED",
        "POSITION_VERIFIED",
        "CANCELLED",
        "SKIPPED",
        "ERROR",
    ):
        state = _state(_level(lifecycle="LEVEL_SKIPPED"), _order(order_lc))
        assert apply_pipeline_coupling(state) is state  # unchanged, no raise


# --------------------------- B4.3 PV advance ---------------------------


def test_pv_advance_writes_none_unlocked() -> None:
    state = _state(_level(lifecycle=None, locked=False), _order("POSITION_VERIFIED"))
    out = apply_pipeline_coupling(state)
    rows = out.st04_level_pipeline_states or ()
    assert rows[0].lifecycle == "POSITION_VERIFIED"


def test_pv_guards_set_lifecycle_unchanged() -> None:
    # lifecycle already set (IDLE) -> not None -> unchanged.
    state = _state(_level(lifecycle="IDLE", locked=False), _order("POSITION_VERIFIED"))
    assert apply_pipeline_coupling(state) is state


def test_pv_on_locked_level_raises() -> None:
    state = _state(_level(lifecycle="LOCKED", locked=True), _order("POSITION_VERIFIED"))
    with pytest.raises(ValueError, match="RECONCILIATION_REQUIRED"):
        apply_pipeline_coupling(state)


# --------------------------- multi-row join + determinism ---------------------


def test_multi_row_join_only_matching_changes() -> None:
    lvl_match = _level(lifecycle=None)  # (0,0,BU,1)
    lvl_other = LevelState(
        generation_id=0,
        cycle_id=0,
        direction="SL",
        level_id=1,
        target_price=Decimal("49000"),
        is_protection_locked=False,
        lifecycle=None,
    )
    order = _order("POSITION_VERIFIED", cloid="c1")  # targets (0,0,BU,1)
    state = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=(lvl_match, lvl_other),
        st05_order_intents_and_outcomes=(order,),
    )
    out = apply_pipeline_coupling(state)
    rows = {
        (r.direction, r.level_id): r for r in (out.st04_level_pipeline_states or ())
    }
    assert rows[("BU", 1)].lifecycle == "POSITION_VERIFIED"
    assert rows[("SL", 1)].lifecycle is None  # untouched


def test_determinism() -> None:
    state = _state(_level(lifecycle=None), _order("POSITION_VERIFIED"))
    a = apply_pipeline_coupling(state)
    b = apply_pipeline_coupling(state)
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )
