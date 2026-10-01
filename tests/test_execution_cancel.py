"""§5.2 step-2 cancel selector (Phase 7h-3, E2)."""

from decimal import Decimal

from astergrid.core.transitions import (
    CancelReasonCode,
    IntentTag,
    OrderState,
    OrderType,
    construct_order_intent,
    select_exhausted_candidates,
)

_RESTING = (
    "ORDER_SUBMITTED",
    "ORDER_ACKNOWLEDGED",
    "ORDER_ACTIVE",
    "PARTIALLY_FILLED",
    "EMERGENCY",
)
_NON_RESTING = (
    "INTENT_CREATED",
    "FILLED",
    "CANCELLED",
    "SKIPPED",
    "ERROR",
    "POSITION_VERIFIED",
)


def _order(
    cloid: str, lifecycle: str, gen: int = 0, cycle: int = 0, direction: str = "BU"
) -> OrderState:
    intent = construct_order_intent(
        cloid=cloid,
        target_generation_id=gen,
        target_cycle_id=cycle,
        target_level_id=1,
        target_direction=direction,
        order_type=OrderType.LIMIT,
        requested_size=Decimal("1"),
        requested_price=Decimal("50000"),
        intent_tag=IntentTag.ENTRY_INTENT,
        acute=False,
    )
    return OrderState(intent=intent, lifecycle=lifecycle)


def test_all_resting_selected() -> None:
    rows = tuple(_order(f"c{i}", lc) for i, lc in enumerate(_RESTING))
    out = select_exhausted_candidates(rows, 0, 0, "BU")
    assert len(out) == len(_RESTING)
    assert all(
        c.reason_code == CancelReasonCode.EXHAUSTED_TRAVERSAL_CANCEL for c in out
    )


def test_all_non_resting_excluded() -> None:
    rows = tuple(_order(f"c{i}", lc) for i, lc in enumerate(_NON_RESTING))
    assert select_exhausted_candidates(rows, 0, 0, "BU") == ()


def test_traversal_filter() -> None:
    rows = (
        _order("a", "ORDER_ACTIVE", gen=0, cycle=0, direction="BU"),  # match
        _order("b", "ORDER_ACTIVE", gen=1, cycle=0, direction="BU"),  # wrong gen
        _order("c", "ORDER_ACTIVE", gen=0, cycle=1, direction="BU"),  # wrong cycle
        _order("d", "ORDER_ACTIVE", gen=0, cycle=0, direction="SL"),  # wrong direction
    )
    out = select_exhausted_candidates(rows, 0, 0, "BU")
    assert [c.cloid for c in out] == ["a"]


def test_output_sorted_by_cloid() -> None:
    rows = (
        _order("z", "ORDER_ACTIVE"),
        _order("a", "PARTIALLY_FILLED"),
        _order("m", "EMERGENCY"),
    )
    out = select_exhausted_candidates(rows, 0, 0, "BU")
    assert [c.cloid for c in out] == ["a", "m", "z"]


def test_empty_input_empty_output() -> None:
    assert select_exhausted_candidates((), 0, 0, "BU") == ()


def test_serialization() -> None:
    from astergrid.core.serialization import canonical_dumps

    out = select_exhausted_candidates((_order("a", "ORDER_ACTIVE"),), 0, 0, "BU")
    obj = out[0].to_canonical_obj()
    assert obj == {"cloid": "a", "reason_code": "EXHAUSTED_TRAVERSAL_CANCEL"}
    canonical_dumps(obj)
