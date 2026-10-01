"""Event kinds are frozen and pure (no clock/fs/net/randomness on construction)."""

import dataclasses
import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal
from unittest import mock

import pytest

from astergrid.core.events import (
    AcknowledgmentEvent,
    AdministrativeEvent,
    CommandEvent,
    ErrorEvent,
    EventEnvelope,
    FillEvent,
    IntentEvent,
    ObservationEvent,
    OperatorEvent,
    StateTransitionEvent,
    TimerEvent,
    canonical_order_key,
    compare,
)

_TS = "2026-09-22T00:00:00.000000Z"


@contextmanager
def _no_ambient() -> Iterator[None]:
    def boom(*_a: object, **_k: object) -> object:
        raise AssertionError("clock/randomness accessed")

    with (
        mock.patch.object(time, "time", boom),
        mock.patch.object(time, "monotonic", boom),
        mock.patch.object(random, "random", boom),
        mock.patch.object(os, "urandom", boom),
    ):
        yield


def _one_of_each() -> list[object]:
    return [
        IntentEvent(
            intent_classification="ENTRY_INTENT",
            target_generation_id=0,
            target_cycle_id=0,
            target_level_id=1,
            target_direction="BU",
            requested_size=Decimal("0.001"),
            requested_price=Decimal("100000"),
            cloid="c1",
            acute=False,
        ),
        CommandEvent(cloid="c1", action="submit", tif="Alo"),
        AcknowledgmentEvent(cloid="c1", ack_status="resting"),
        FillEvent(
            cloid="c1",
            filled_quantity=Decimal("0.001"),
            price=Decimal("100000"),
            is_snapshot=False,
        ),
        ObservationEvent(
            source_endpoint="clearinghouseState",
            read_timestamp=_TS,
            payload_fingerprint="abc",
            freshness_window_seconds=6,
            is_full=True,
        ),
        TimerEvent(
            timer_kind="confirmation", fire_timestamp=_TS, associated_entity="G00-C00"
        ),
        ErrorEvent(error_class="rate-limit", source="venue"),
        StateTransitionEvent(
            prior_state="INTENT", next_state="POSITION_VERIFIED", reason_code="VERIFIED"
        ),
        OperatorEvent(
            operator_identity="op1", timestamp=_TS, action="approve", target="arm:1"
        ),
        AdministrativeEvent(
            config_identity="cfg-v1", effective_time=_TS, provenance="owner"
        ),
    ]


def test_all_kinds_are_frozen() -> None:
    for event in _one_of_each():
        with pytest.raises(dataclasses.FrozenInstanceError):
            event.causal_predecessors = (1,)


def test_construction_touches_no_ambient_state() -> None:
    with _no_ambient():
        events = _one_of_each()
    assert len(events) == 10


def test_canonical_order_key_is_pure_and_total() -> None:
    a = EventEnvelope(
        log_sequence=0,
        event=CommandEvent(cloid="c1", action="submit", tif="Alo"),
        venue_sequence=None,
        server_ts=None,
        local_receive_ts=_TS,
        monotonic_counter=0,
        prev_hash="0" * 64,
        content_hash="a" * 64,
        schema_version=1,
    )
    b = dataclasses.replace(a, log_sequence=1, monotonic_counter=1)
    assert canonical_order_key(a) == canonical_order_key(a)
    assert compare(a, a) == 0
    assert compare(a, b) == -1
    assert compare(b, a) == 1
