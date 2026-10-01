"""Event <-> canonical-obj codec (Phase 7b): pure, typed, no domain semantics.

Serialization builds a plain dict from an event; deserialization reconstructs the
correct dataclass from a payload dict (used by the SQLite log's ``read_all``).
Explicit typed extractors keep this ``Any``-free under ``mypy --strict``. This is
plumbing only — it encodes/decodes structure, never any §4-§13 rule.
"""

from __future__ import annotations

from dataclasses import fields
from decimal import Decimal

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
from hypergrid.core.serialization import is_iso_utc_micros


def event_to_payload(event: AnyEvent) -> dict[str, object]:
    """Return the event's domain fields as a canonical dict (omit absent optionals).

    Optional fields default to ``None`` and are OMITTED when unset (R-JSON-6).
    ``causal_predecessors`` is always present (empty tuple is a value, not absent).
    """
    out: dict[str, object] = {}
    for f in fields(event):
        value = getattr(event, f.name)
        if value is None:
            continue
        if isinstance(value, tuple):
            out[f.name] = list(value)
        else:
            out[f.name] = value
    return out


def _require(payload: dict[str, object], key: str) -> object:
    if key not in payload:
        raise ValueError(f"missing required field {key!r}")
    return payload[key]


def _req_str(payload: dict[str, object], key: str) -> str:
    value = _require(payload, key)
    if not isinstance(value, str):
        raise ValueError(f"field {key!r} must be a string")
    return value


def _req_int(payload: dict[str, object], key: str) -> int:
    value = _require(payload, key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"field {key!r} must be an int")
    return value


def _req_dec(payload: dict[str, object], key: str) -> Decimal:
    value = _require(payload, key)
    if not isinstance(value, Decimal):
        raise ValueError(f"field {key!r} must be a Decimal")
    return value


def _req_bool(payload: dict[str, object], key: str) -> bool:
    value = _require(payload, key)
    if not isinstance(value, bool):
        raise ValueError(f"field {key!r} must be a bool")
    return value


def _req_ts(payload: dict[str, object], key: str) -> str:
    """Require an ISO-8601-Z microsecond timestamp string (R-JSON-5)."""
    value = _req_str(payload, key)
    if not is_iso_utc_micros(value):
        raise ValueError(f"field {key!r} must be an ISO-8601-Z microsecond timestamp")
    return value


def _opt_int(payload: dict[str, object], key: str) -> int | None:
    if key not in payload:
        return None
    return _req_int(payload, key)


def _opt_str(payload: dict[str, object], key: str) -> str | None:
    if key not in payload:
        return None
    return _req_str(payload, key)


def _preds(payload: dict[str, object]) -> tuple[int, ...]:
    if "causal_predecessors" not in payload:
        return ()
    value = payload["causal_predecessors"]
    if not isinstance(value, list):
        raise ValueError("causal_predecessors must be a list")
    result: list[int] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int):
            raise ValueError("causal_predecessors entries must be ints")
        result.append(item)
    return tuple(result)


def _build_intent(p: dict[str, object]) -> IntentEvent:
    return IntentEvent(
        intent_classification=_req_str(p, "intent_classification"),
        target_generation_id=_req_int(p, "target_generation_id"),
        target_cycle_id=_req_int(p, "target_cycle_id"),
        target_level_id=_req_int(p, "target_level_id"),
        target_direction=_req_str(p, "target_direction"),
        requested_size=_req_dec(p, "requested_size"),
        requested_price=_req_dec(p, "requested_price"),
        cloid=_req_str(p, "cloid"),
        acute=_req_bool(p, "acute"),
        causal_predecessors=_preds(p),
    )


def _build_command(p: dict[str, object]) -> CommandEvent:
    return CommandEvent(
        cloid=_req_str(p, "cloid"),
        action=_req_str(p, "action"),
        tif=_req_str(p, "tif"),
        expires_after=_opt_int(p, "expires_after"),
        causal_predecessors=_preds(p),
    )


def _build_acknowledgment(p: dict[str, object]) -> AcknowledgmentEvent:
    return AcknowledgmentEvent(
        cloid=_req_str(p, "cloid"),
        ack_status=_req_str(p, "ack_status"),
        venue_oid=_opt_str(p, "venue_oid"),
        causal_predecessors=_preds(p),
    )


def _build_fill(p: dict[str, object]) -> FillEvent:
    return FillEvent(
        cloid=_req_str(p, "cloid"),
        filled_quantity=_req_dec(p, "filled_quantity"),
        price=_req_dec(p, "price"),
        is_snapshot=_req_bool(p, "is_snapshot"),
        venue_oid=_opt_str(p, "venue_oid"),
        causal_predecessors=_preds(p),
    )


def _build_observation(p: dict[str, object]) -> ObservationEvent:
    return ObservationEvent(
        source_endpoint=_req_str(p, "source_endpoint"),
        read_timestamp=_req_ts(p, "read_timestamp"),
        payload_fingerprint=_req_str(p, "payload_fingerprint"),
        freshness_window_seconds=_req_int(p, "freshness_window_seconds"),
        is_full=_req_bool(p, "is_full"),
        causal_predecessors=_preds(p),
    )


def _build_timer(p: dict[str, object]) -> TimerEvent:
    return TimerEvent(
        timer_kind=_req_str(p, "timer_kind"),
        fire_timestamp=_req_ts(p, "fire_timestamp"),
        associated_entity=_req_str(p, "associated_entity"),
        causal_predecessors=_preds(p),
    )


def _build_error(p: dict[str, object]) -> ErrorEvent:
    return ErrorEvent(
        error_class=_req_str(p, "error_class"),
        source=_req_str(p, "source"),
        linkage_cloid=_opt_str(p, "linkage_cloid"),
        causal_predecessors=_preds(p),
    )


def _build_state_transition(p: dict[str, object]) -> StateTransitionEvent:
    return StateTransitionEvent(
        prior_state=_req_str(p, "prior_state"),
        next_state=_req_str(p, "next_state"),
        reason_code=_req_str(p, "reason_code"),
        causal_predecessors=_preds(p),
    )


def _build_operator(p: dict[str, object]) -> OperatorEvent:
    return OperatorEvent(
        operator_identity=_req_str(p, "operator_identity"),
        timestamp=_req_ts(p, "timestamp"),
        action=_req_str(p, "action"),
        target=_req_str(p, "target"),
        causal_predecessors=_preds(p),
    )


def _build_administrative(p: dict[str, object]) -> AdministrativeEvent:
    return AdministrativeEvent(
        config_identity=_req_str(p, "config_identity"),
        effective_time=_req_ts(p, "effective_time"),
        provenance=_req_str(p, "provenance"),
        causal_predecessors=_preds(p),
    )


def event_from_payload(kind: str, payload: dict[str, object]) -> AnyEvent:
    """Reconstruct the event dataclass named by ``kind`` from ``payload``."""
    if kind == IntentEvent.event_kind:
        return _build_intent(payload)
    if kind == CommandEvent.event_kind:
        return _build_command(payload)
    if kind == AcknowledgmentEvent.event_kind:
        return _build_acknowledgment(payload)
    if kind == FillEvent.event_kind:
        return _build_fill(payload)
    if kind == ObservationEvent.event_kind:
        return _build_observation(payload)
    if kind == TimerEvent.event_kind:
        return _build_timer(payload)
    if kind == ErrorEvent.event_kind:
        return _build_error(payload)
    if kind == StateTransitionEvent.event_kind:
        return _build_state_transition(payload)
    if kind == OperatorEvent.event_kind:
        return _build_operator(payload)
    if kind == AdministrativeEvent.event_kind:
        return _build_administrative(payload)
    raise ValueError(f"unknown event kind: {kind!r}")
