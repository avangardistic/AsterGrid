"""§9.3 LEVEL_SKIPPED member + can_level_skip + end-to-end (Phase 7h-3, E3)."""

from decimal import Decimal

import pytest

from hypergrid.core.event_log import InMemoryEventLog
from hypergrid.core.events import CommandEvent, ObservedMeta
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.transitions import (
    IntentTag,
    LevelState,
    OrderState,
    OrderType,
    PerLevelObservation,
    can_level_skip,
    classify_intent,
    construct_order_intent,
    evaluate_emergency,
    select_exhausted_candidates,
    submit_order,
)

_ALL_14 = (
    "INTENT_CREATED",
    "ORDER_SUBMITTED",
    "ORDER_ACKNOWLEDGED",
    "ORDER_ACTIVE",
    "PARTIALLY_FILLED",
    "FILLED",
    "POSITION_VERIFIED",
    "CANCELLED",
    "EMERGENCY",
    "SKIPPED",
    "ERROR",
    "LOCKED",
    "IDLE",
    "LEVEL_SKIPPED",
)
_SKIPPABLE = frozenset({"ORDER_ACTIVE", "EMERGENCY", "PARTIALLY_FILLED"})
_TS = "2026-09-25T00:00:00.000000Z"


def _level(lc: str) -> LevelState:
    return LevelState(
        generation_id=0,
        cycle_id=0,
        direction="BU",
        level_id=1,
        target_price=Decimal("50000"),
        is_protection_locked=(lc == "LOCKED"),
        lifecycle=lc,
    )


def _obs(lc: str) -> PerLevelObservation:
    return PerLevelObservation(
        generation_id=0,
        cycle_id=0,
        direction="BU",
        level_id=1,
        lifecycle=lc,
        filled_quantity=Decimal("0"),
        order_filled=True,  # satisfy the §6.1 FILLED hard rule across all lifecycles
        position_delta_verified=True,
    )


# --------------------------- both leaves accept LEVEL_SKIPPED ------------------


def test_level_skipped_accepted_both_leaves() -> None:
    assert _level("LEVEL_SKIPPED").lifecycle == "LEVEL_SKIPPED"
    assert _obs("LEVEL_SKIPPED").lifecycle == "LEVEL_SKIPPED"


def test_both_leaves_symmetry() -> None:
    for lc in _ALL_14:
        assert _level(lc).lifecycle == lc
        assert _obs(lc).lifecycle == lc
    for bogus in ("BOGUS", "level_skipped", "SKIP", ""):
        with pytest.raises(ValueError):
            _level(bogus)
        with pytest.raises(ValueError):
            _obs(bogus)


# --------------------------- can_level_skip matrix ---------------------------


def test_can_level_skip_matrix() -> None:
    for lc in _ALL_14:
        assert can_level_skip(lc) is (lc in _SKIPPABLE), lc
    # exactly 3 True.
    assert sum(1 for lc in _ALL_14 if can_level_skip(lc)) == 3


def test_level_skipped_is_terminal_in_skip_gate() -> None:
    # A skipped level can never be skipped again ("never resurrected", §9.3).
    assert can_level_skip("LEVEL_SKIPPED") is False


def test_can_level_skip_unknown_raises() -> None:
    with pytest.raises(ValueError):
        can_level_skip("NOPE")


def test_r10c_coherence_untouched() -> None:
    # LEVEL_SKIPPED is not LOCKED → locked=True must fail the coherence check.
    with pytest.raises(ValueError):
        LevelState(
            generation_id=0,
            cycle_id=0,
            direction="BU",
            level_id=1,
            target_price=Decimal("50000"),
            is_protection_locked=True,
            lifecycle="LEVEL_SKIPPED",
        )


# --------------------------- end-to-end + exports ---------------------------


def test_end_to_end_intent_to_submitted_to_skip() -> None:
    tag = classify_intent(Decimal("0"), Decimal("5"), False)  # flat→pos → ENTRY
    assert tag == IntentTag.ENTRY_INTENT
    intent = construct_order_intent(
        cloid="c1",
        target_generation_id=0,
        target_cycle_id=0,
        target_level_id=1,
        target_direction="BU",
        order_type=OrderType.LIMIT,
        requested_size=Decimal("1"),
        requested_price=Decimal("50000"),
        intent_tag=tag,
        acute=False,
    )
    order = OrderState(intent=intent, lifecycle="INTENT_CREATED")
    log = InMemoryEventLog()
    meta = ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)
    receipt, advanced = submit_order(
        order=order,
        tif="Gtc",
        expires_after=60,
        intent_log_seq=0,
        port=log,
        observed=meta,
    )
    assert advanced.lifecycle == "ORDER_SUBMITTED"
    env = next(iter(log.read_all()))
    assert isinstance(env.event, CommandEvent)
    # cancel selector over the resting row.
    cands = select_exhausted_candidates((advanced,), 0, 0, "BU")
    assert [c.cloid for c in cands] == ["c1"]
    # emergency LEVEL_SKIP → candidates, all serialize.
    ev = evaluate_emergency(
        wait_bound_breached=True,
        direction="BU",
        target_price=Decimal("100"),
        tolerance_bps=Decimal("50"),
        tolerance_leverage_in=Decimal("1"),
        fillable=False,
        best_exec_price=Decimal("100"),
        maker_edge_ok=False,
        taker_edge_ok=False,
        reprice_would_justify=False,
        remaining_size=Decimal("1"),
        order_cloid="c1",
        order_lifecycle_now="EMERGENCY",
        level_identity=(0, 0, "BU", 1),
        level_lifecycle_now="EMERGENCY",
    )
    assert ev.skip_level_to == "LEVEL_SKIPPED"
    for obj in (
        receipt.to_canonical_obj(),
        cands[0].to_canonical_obj(),
        ev.to_canonical_obj(),
    ):
        canonical_dumps(obj)
