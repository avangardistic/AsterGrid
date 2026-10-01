"""No ambient state affects the model: byte-stable serialization across builds."""

from decimal import Decimal

from astergrid.core.events import (
    AcknowledgmentEvent,
    AdministrativeEvent,
    AnyEvent,
    CommandEvent,
    ErrorEvent,
    FillEvent,
    IntentEvent,
    ObservationEvent,
    OperatorEvent,
    StateTransitionEvent,
    TimerEvent,
    event_to_payload,
)
from astergrid.core.serialization import canonical_dumps

_TS = "2026-09-22T00:00:00.000000Z"


def _construct() -> list[AnyEvent]:
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


def test_equality_and_byte_stable_serialization() -> None:
    first = _construct()
    second = _construct()
    assert len(first) == 10
    for a, b in zip(first, second, strict=True):
        assert a == b
        assert canonical_dumps(event_to_payload(a)) == canonical_dumps(
            event_to_payload(b)
        )
