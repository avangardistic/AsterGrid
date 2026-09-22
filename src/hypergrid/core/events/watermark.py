"""Per-stream venue-sequence watermark (EVENT_MODEL §D / B4), pure (Phase 7b).

Tracks the highest observed position on a stream. ``advance`` is pure: it reads
no clock, does not mutate ``current``, and does not interpret the stream's
domain content (that is the adapter's job, Phase 7f+).
"""

from __future__ import annotations

from dataclasses import dataclass

from hypergrid.core.events.envelope import EventEnvelope


@dataclass(frozen=True, slots=True)
class StreamWatermark:
    """The B4 per-stream watermark tuple."""

    stream_id: str
    last_sequence_value: int | None
    last_server_ts: str | None
    last_local_ts: str | None
    last_monotonic_counter: int
    content_fingerprint: str


def advance(current: StreamWatermark, incoming: EventEnvelope) -> StreamWatermark:
    """Return the next watermark after observing ``incoming`` (no mutation)."""
    return StreamWatermark(
        stream_id=current.stream_id,
        last_sequence_value=(
            incoming.venue_sequence
            if incoming.venue_sequence is not None
            else current.last_sequence_value
        ),
        last_server_ts=(
            incoming.server_ts
            if incoming.server_ts is not None
            else current.last_server_ts
        ),
        last_local_ts=incoming.local_receive_ts,
        last_monotonic_counter=incoming.monotonic_counter,
        content_fingerprint=incoming.content_hash,
    )
