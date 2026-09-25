"""ST-05 order lifecycle table + slot wiring (Phase 7h-2, E3).

The §6.1 order pipeline is 11 states (minus LOCKED/IDLE, which are ST-04's). All
inputs literal; no clock.
"""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.fold import _empty_state
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.transitions import (
    IntentTag,
    OrderIntent,
    OrderState,
    OrderType,
    construct_order_intent,
    is_legal_order_transition,
)

_ELEVEN = (
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
)
_LEGAL = (
    ("INTENT_CREATED", "ORDER_SUBMITTED"),
    ("ORDER_SUBMITTED", "ORDER_ACKNOWLEDGED"),
    ("ORDER_ACKNOWLEDGED", "ORDER_ACTIVE"),
    ("ORDER_ACTIVE", "PARTIALLY_FILLED"),
    ("PARTIALLY_FILLED", "FILLED"),
    ("FILLED", "POSITION_VERIFIED"),
    ("ORDER_ACKNOWLEDGED", "CANCELLED"),
    ("ORDER_ACTIVE", "CANCELLED"),
    ("PARTIALLY_FILLED", "CANCELLED"),
    ("ORDER_ACTIVE", "EMERGENCY"),
    ("EMERGENCY", "SKIPPED"),
    ("ORDER_SUBMITTED", "ERROR"),
    ("ORDER_ACKNOWLEDGED", "ERROR"),
    ("ORDER_ACTIVE", "ERROR"),
)
_ILLEGAL = (
    ("ORDER_ACTIVE", "ORDER_SUBMITTED"),  # reversal
    ("INTENT_CREATED", "ORDER_ACTIVE"),  # stage skip
    ("INTENT_CREATED", "CANCELLED"),  # not a working order yet
    ("FILLED", "CANCELLED"),  # already filled
    ("POSITION_VERIFIED", "FILLED"),  # terminal
    ("CANCELLED", "ORDER_ACTIVE"),  # terminal
    ("SKIPPED", "ORDER_ACTIVE"),  # terminal
    ("ERROR", "ORDER_ACTIVE"),  # terminal
)


def _intent(cloid: str = "c1") -> OrderIntent:
    return construct_order_intent(
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


# --------------------------- transition table ---------------------------


def test_all_legal_edges_pass() -> None:
    for frm, to in _LEGAL:
        assert is_legal_order_transition(frm, to) is True, (frm, to)


def test_illegal_edges_rejected() -> None:
    for frm, to in _ILLEGAL:
        assert is_legal_order_transition(frm, to) is False, (frm, to)


def test_terminals_have_no_outgoing_edges() -> None:
    for terminal in ("POSITION_VERIFIED", "CANCELLED", "SKIPPED", "ERROR"):
        for to in _ELEVEN:
            assert is_legal_order_transition(terminal, to) is False, (terminal, to)


def test_locked_idle_awaiting_arm_not_order_states() -> None:
    for alien in ("LOCKED", "IDLE", "AWAITING_ARM", "ARMED"):
        with pytest.raises(ValueError):
            is_legal_order_transition(alien, "ORDER_ACTIVE")
        with pytest.raises(ValueError):
            is_legal_order_transition("ORDER_ACTIVE", alien)


# --------------------------- OrderState row ---------------------------


def test_all_eleven_states_accepted() -> None:
    for lc in _ELEVEN:
        row = OrderState(intent=_intent(), lifecycle=lc)
        assert row.lifecycle == lc


def test_order_state_rejects_alien_lifecycle() -> None:
    for alien in ("LOCKED", "IDLE", "AWAITING_ARM", "BOGUS"):
        with pytest.raises(ValueError):
            OrderState(intent=_intent(), lifecycle=alien)


def test_order_state_serializes() -> None:
    row = OrderState(intent=_intent(), lifecycle="ORDER_ACTIVE")
    obj = row.to_canonical_obj()
    assert obj["lifecycle"] == "ORDER_ACTIVE"
    assert obj["intent"]["cloid"] == "c1"
    canonical_dumps(obj)


# --------------------------- slot wiring / persistence ---------------------


def test_st05_slot_accepts_sorted_and_serializes() -> None:
    rows = (
        OrderState(intent=_intent("a"), lifecycle="INTENT_CREATED"),
        OrderState(intent=_intent("b"), lifecycle="ORDER_ACTIVE"),
    )
    state = dataclasses.replace(_empty_state(), st05_order_intents_and_outcomes=rows)
    obj = state.to_canonical_obj()
    canonical_dumps(obj)
    assert obj["st05_order_intents_and_outcomes"][0]["intent"]["cloid"] == "a"
    assert obj["st05_order_intents_and_outcomes"][1]["lifecycle"] == "ORDER_ACTIVE"


def test_st05_unsorted_and_duplicate_rejected() -> None:
    unsorted = (
        OrderState(intent=_intent("b"), lifecycle="INTENT_CREATED"),
        OrderState(intent=_intent("a"), lifecycle="INTENT_CREATED"),
    )
    with pytest.raises(ValueError):
        dataclasses.replace(_empty_state(), st05_order_intents_and_outcomes=unsorted)
    dup = (
        OrderState(intent=_intent("a"), lifecycle="INTENT_CREATED"),
        OrderState(intent=_intent("a"), lifecycle="ORDER_ACTIVE"),
    )
    with pytest.raises(ValueError):
        dataclasses.replace(_empty_state(), st05_order_intents_and_outcomes=dup)


def test_domain_placeholder_count_preserved() -> None:
    # D6: wiring types (not adds) st fields — still 23 st* domain fields.
    domain = [f for f in dataclasses.fields(_empty_state()) if f.name.startswith("st")]
    assert len(domain) == 23
