"""The append-only event-log port (Phase 7b).

The log is the ONLY allocator of ``log_sequence`` and ``monotonic_counter``
(R-SEQ-1): the caller supplies all clock-derived values via ``ObservedMeta``;
the log never samples a clock. ``append`` computes the tamper-evident
``content_hash`` (binding order + linkage + timing + content) and returns the
persisted envelope. The port is single-writer; concurrent appends from multiple
writers are NOT supported at this layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator

    from astergrid.core.events import AnyEvent, EventEnvelope, ObservedMeta


class EventLogPort(Protocol):
    """Append-only, single-writer event log."""

    def append(self, event: AnyEvent, observed: ObservedMeta) -> EventEnvelope:
        """Allocate the next log_sequence/monotonic_counter, hash-link, persist.

        ``observed`` supplies all clock-derived values; the log samples no clock.
        Returns the persisted envelope.
        """
        ...

    def read_all(self) -> Iterator[EventEnvelope]:
        """Yield every envelope in ascending ``log_sequence``."""
        ...

    def head_hash(self) -> str:
        """The last envelope's ``content_hash``, or the genesis hash if empty."""
        ...

    def head_sequence(self) -> int | None:
        """The last envelope's ``log_sequence``, or ``None`` if the log is empty."""
        ...

    def close(self) -> None:
        """Release resources. Idempotent."""
        ...
