"""§9 submission mechanics (Phase 7h-3, E2): real in-memory log, no fake port."""

from decimal import Decimal

import pytest

from astergrid.core.event_log import InMemoryEventLog
from astergrid.core.events import CommandEvent, ObservedMeta
from astergrid.core.transitions import (
    IntentTag,
    OrderState,
    OrderType,
    construct_order_intent,
    is_legal_order_transition,
    submit_order,
)

_TS = "2026-09-25T00:00:00.000000Z"


def _order(cloid: str = "c1", order_type: OrderType = OrderType.LIMIT) -> OrderState:
    intent = construct_order_intent(
        cloid=cloid,
        target_generation_id=0,
        target_cycle_id=0,
        target_level_id=1,
        target_direction="BU",
        order_type=order_type,
        requested_size=Decimal("1"),
        requested_price=Decimal("50000"),
        intent_tag=IntentTag.ENTRY_INTENT,
        acute=False,
    )
    return OrderState(intent=intent, lifecycle="INTENT_CREATED")


def _meta() -> ObservedMeta:
    return ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)


def test_all_order_type_action_mappings() -> None:
    expected = {
        OrderType.LIMIT: "submit",
        OrderType.MARKET: "submit",
        OrderType.STOP: "submit",
        OrderType.TAKE_PROFIT: "submit",
        OrderType.TWAP: "twap",
    }
    for order_type, action in expected.items():
        log = InMemoryEventLog()
        submit_order(
            order=_order(order_type=order_type),
            tif="Gtc",
            expires_after=60,
            intent_log_seq=0,
            port=log,
            observed=_meta(),
        )
        env = next(iter(log.read_all()))
        assert isinstance(env.event, CommandEvent)
        assert env.event.action == action, order_type


def test_exactly_once_append_and_chain() -> None:
    log = InMemoryEventLog()
    assert list(log.read_all()) == []
    receipt, advanced = submit_order(
        order=_order(),
        tif="Alo",
        expires_after=60,
        intent_log_seq=0,
        port=log,
        observed=_meta(),
    )
    envs = list(log.read_all())
    assert len(envs) == 1  # exactly one append
    assert envs[0].log_sequence == 0  # command_sequence 0-based
    assert receipt.command_sequence == 0
    assert len(receipt.content_hash) == 64  # sha256 hex
    assert receipt.content_hash == envs[0].content_hash
    assert receipt.submitted_at_ts == _TS
    assert envs[0].event.causal_predecessors == (0,)
    assert advanced.lifecycle == "ORDER_SUBMITTED"
    assert is_legal_order_transition("INTENT_CREATED", "ORDER_SUBMITTED") is True


def test_predecessors_echo_intent_seq() -> None:
    log = InMemoryEventLog()
    submit_order(
        order=_order(),
        tif="Gtc",
        expires_after=60,
        intent_log_seq=7,
        port=log,
        observed=_meta(),
    )
    assert next(iter(log.read_all())).event.causal_predecessors == (7,)


def test_double_submit_rejected() -> None:
    log = InMemoryEventLog()
    _, advanced = submit_order(
        order=_order(),
        tif="Gtc",
        expires_after=60,
        intent_log_seq=0,
        port=log,
        observed=_meta(),
    )
    # An advanced (ORDER_SUBMITTED) row can never re-enter B1.
    with pytest.raises(ValueError):
        submit_order(
            order=advanced,
            tif="Gtc",
            expires_after=60,
            intent_log_seq=0,
            port=log,
            observed=_meta(),
        )


def test_validation_failures() -> None:
    log = InMemoryEventLog()
    with pytest.raises(ValueError):  # bad tif
        submit_order(
            order=_order(),
            tif="FOK",
            expires_after=60,
            intent_log_seq=0,
            port=log,
            observed=_meta(),
        )
    with pytest.raises(ValueError):  # expires_after <= 0
        submit_order(
            order=_order(),
            tif="Gtc",
            expires_after=0,
            intent_log_seq=0,
            port=log,
            observed=_meta(),
        )
    with pytest.raises(ValueError):  # negative intent_log_seq
        submit_order(
            order=_order(),
            tif="Gtc",
            expires_after=60,
            intent_log_seq=-1,
            port=log,
            observed=_meta(),
        )
    with pytest.raises(ValueError):  # non-INTENT_CREATED row
        submit_order(
            order=OrderState(intent=_order().intent, lifecycle="ORDER_ACTIVE"),
            tif="Gtc",
            expires_after=60,
            intent_log_seq=0,
            port=log,
            observed=_meta(),
        )
    # no partial append on the last failure path either (only the guard fired).
    assert list(log.read_all()) == []
