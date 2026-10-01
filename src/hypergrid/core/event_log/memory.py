"""In-memory append-only event log (Phase 7b): tests + differential harness."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hypergrid.core.events import (
    ENVELOPE_SCHEMA_VERSION,
    GENESIS_PREV_HASH,
    EventEnvelope,
    content_hash_for,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from hypergrid.core.events import AnyEvent, ObservedMeta


class InMemoryEventLog:
    """A plain-list implementation of :class:`EventLogPort`."""

    def __init__(self) -> None:
        self._envelopes: list[EventEnvelope] = []

    def append(self, event: AnyEvent, observed: ObservedMeta) -> EventEnvelope:
        head = self.head_sequence()
        sequence = 0 if head is None else head + 1
        monotonic = sequence  # single-writer: monotonic_counter == log_sequence
        prev_hash = self.head_hash()
        content_hash = content_hash_for(
            schema_version=ENVELOPE_SCHEMA_VERSION,
            log_sequence=sequence,
            prev_hash=prev_hash,
            event=event,
            venue_sequence=observed.venue_sequence,
            server_ts=observed.server_ts,
            local_receive_ts=observed.local_receive_ts,
            monotonic_counter=monotonic,
        )
        envelope = EventEnvelope(
            log_sequence=sequence,
            event=event,
            venue_sequence=observed.venue_sequence,
            server_ts=observed.server_ts,
            local_receive_ts=observed.local_receive_ts,
            monotonic_counter=monotonic,
            prev_hash=prev_hash,
            content_hash=content_hash,
            schema_version=ENVELOPE_SCHEMA_VERSION,
        )
        self._envelopes.append(envelope)
        return envelope

    def read_all(self) -> Iterator[EventEnvelope]:
        yield from self._envelopes

    def head_hash(self) -> str:
        if not self._envelopes:
            return GENESIS_PREV_HASH
        return self._envelopes[-1].content_hash

    def head_sequence(self) -> int | None:
        if not self._envelopes:
            return None
        return self._envelopes[-1].log_sequence

    def close(self) -> None:
        return None
