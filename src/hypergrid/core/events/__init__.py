"""hypergrid.core.events — the event model (Phase 7b).

Ten frozen event kinds, the on-the-wire envelope + hash chain, canonical order
(DECISION-007), the per-stream watermark, and the event codec. Pure, stdlib-only,
no domain logic (no fold — that is Phase 7c).
"""

from hypergrid.core.events.codec import event_from_payload, event_to_payload
from hypergrid.core.events.envelope import (
    ENVELOPE_SCHEMA_VERSION,
    GENESIS_PREV_HASH,
    SCENARIO_SCHEMA_VERSION,
    EventEnvelope,
    ObservedMeta,
    content_hash_for,
    envelope_to_obj,
    scenario_dumps,
)
from hypergrid.core.events.identity import canonical_order_key, compare
from hypergrid.core.events.kinds import (
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
)
from hypergrid.core.events.watermark import StreamWatermark, advance

__all__ = [
    "ENVELOPE_SCHEMA_VERSION",
    "GENESIS_PREV_HASH",
    "SCENARIO_SCHEMA_VERSION",
    "AcknowledgmentEvent",
    "AdministrativeEvent",
    "AnyEvent",
    "CommandEvent",
    "ErrorEvent",
    "EventEnvelope",
    "FillEvent",
    "IntentEvent",
    "ObservationEvent",
    "ObservedMeta",
    "OperatorEvent",
    "StateTransitionEvent",
    "StreamWatermark",
    "TimerEvent",
    "advance",
    "canonical_order_key",
    "compare",
    "content_hash_for",
    "envelope_to_obj",
    "event_from_payload",
    "event_to_payload",
    "scenario_dumps",
]
