"""The on-the-wire envelope + tamper-evident hash chain + scenario JSON (Phase 7b).

``ObservedMeta`` carries the append-time, caller-supplied clock values (the log
never samples a clock — R-SEQ-1). ``EventEnvelope`` wraps an event with the
log-allocated ``log_sequence``/``monotonic_counter``, the DECISION-007 timing
keys, and the hash chain. ``compute_content_hash`` binds order + linkage +
timing + content, so any mutation breaks the chain. hashlib is used ONLY here
(the chain is single-sourced).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from hypergrid.core.events.codec import event_to_payload
from hypergrid.core.events.kinds import AnyEvent
from hypergrid.core.serialization import canonical_dumps, is_iso_utc_micros

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

GENESIS_PREV_HASH: str = "0" * 64
ENVELOPE_SCHEMA_VERSION: int = 1
SCENARIO_SCHEMA_VERSION: int = 1


@dataclass(frozen=True, slots=True)
class ObservedMeta:
    """Append-time clock values supplied by the caller (runtime/adapter shell).

    The log never reads a clock; every timestamp enters here. Timestamps are
    ISO-8601-Z with microsecond precision (R-JSON-5). ``venue_sequence`` is the
    per-stream venue sequence when present.
    """

    venue_sequence: int | None
    server_ts: str | None
    local_receive_ts: str

    def __post_init__(self) -> None:
        # G2-b: validate timestamps once, at construction (single-sourced). An
        # invalid ObservedMeta cannot exist, so no log can append an invalid
        # record or advance its head from one.
        if not is_iso_utc_micros(self.local_receive_ts):
            raise ValueError(
                "local_receive_ts must be an ISO-8601-Z microsecond timestamp"
            )
        if self.server_ts is not None and not is_iso_utc_micros(self.server_ts):
            raise ValueError(
                "server_ts must be an ISO-8601-Z microsecond timestamp when present"
            )


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """A recorded event with its log-allocated identity and hash-chain linkage."""

    log_sequence: int  # allocated by the log (R-SEQ-1); first is 0
    event: AnyEvent
    venue_sequence: int | None  # from ObservedMeta
    server_ts: str | None  # from ObservedMeta
    local_receive_ts: str  # from ObservedMeta
    monotonic_counter: int  # allocated by the log (== log_sequence, single-writer)
    prev_hash: str  # content_hash of the prior envelope (or genesis)
    content_hash: str  # sha256 over the canonical core object (A4)
    schema_version: int


def _core_obj(
    *,
    schema_version: int,
    log_sequence: int,
    prev_hash: str,
    event: AnyEvent,
    venue_sequence: int | None,
    server_ts: str | None,
    local_receive_ts: str,
    monotonic_counter: int,
) -> dict[str, object]:
    """The canonical object bound by the hash chain (excludes content_hash).

    Optional envelope fields (venue_sequence, server_ts) are OMITTED when absent
    (R-JSON-6).
    """
    obj: dict[str, object] = {
        "schema_version": schema_version,
        "log_sequence": log_sequence,
        "kind": event.event_kind,
        "event": event_to_payload(event),
        "local_receive_ts": local_receive_ts,
        "monotonic_counter": monotonic_counter,
        "prev_hash": prev_hash,
    }
    if venue_sequence is not None:
        obj["venue_sequence"] = venue_sequence
    if server_ts is not None:
        obj["server_ts"] = server_ts
    return obj


def content_hash_for(
    *,
    schema_version: int,
    log_sequence: int,
    prev_hash: str,
    event: AnyEvent,
    venue_sequence: int | None,
    server_ts: str | None,
    local_receive_ts: str,
    monotonic_counter: int,
) -> str:
    """sha256 (hex) over the canonical core object — the tamper-evident chain link."""
    core = _core_obj(
        schema_version=schema_version,
        log_sequence=log_sequence,
        prev_hash=prev_hash,
        event=event,
        venue_sequence=venue_sequence,
        server_ts=server_ts,
        local_receive_ts=local_receive_ts,
        monotonic_counter=monotonic_counter,
    )
    return hashlib.sha256(canonical_dumps(core).encode("utf-8")).hexdigest()


def envelope_to_obj(envelope: EventEnvelope) -> dict[str, object]:
    """Full canonical envelope object (core object + content_hash)."""
    obj = _core_obj(
        schema_version=envelope.schema_version,
        log_sequence=envelope.log_sequence,
        prev_hash=envelope.prev_hash,
        event=envelope.event,
        venue_sequence=envelope.venue_sequence,
        server_ts=envelope.server_ts,
        local_receive_ts=envelope.local_receive_ts,
        monotonic_counter=envelope.monotonic_counter,
    )
    obj["content_hash"] = envelope.content_hash
    return obj


def scenario_dumps(envelopes: Iterable[EventEnvelope]) -> str:
    """Serialize a scenario file: R-JSON-4 envelope + R-JSON-8 payload shape."""
    ordered: Sequence[EventEnvelope] = sorted(envelopes, key=lambda e: e.log_sequence)
    payload: dict[str, object] = {"events": [envelope_to_obj(env) for env in ordered]}
    return canonical_dumps(
        {"schema_version": SCENARIO_SCHEMA_VERSION, "payload": payload}
    )
