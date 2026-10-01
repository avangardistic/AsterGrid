"""Canonical event ordering (DECISION-007), pure and clock-free (Phase 7b).

The total order is: venue_sequence (when present) -> server_ts (when present) ->
local_receive_ts -> monotonic_counter -> log_sequence (the ultimate tie-break;
unique and gap-free within a log, so the order is total and ``compare`` returns
0 only for envelopes with identical order keys).

``canonical_order_key`` returns a sort key whose every position is uniformly
typed (absent optionals encode as a leading 0 flag), so it is safe to sort with.
Neither function reads any clock.
"""

from __future__ import annotations

from astergrid.core.events.envelope import EventEnvelope

_OrderKey = tuple[tuple[int, int], tuple[int, str], tuple[int, str], int, int]


def canonical_order_key(envelope: EventEnvelope) -> _OrderKey:
    """Return the DECISION-007 sort key (log_sequence appended as tie-break)."""
    vseq = envelope.venue_sequence
    sts = envelope.server_ts
    return (
        (0, 0) if vseq is None else (1, vseq),
        (0, "") if sts is None else (1, sts),
        (1, envelope.local_receive_ts),
        envelope.monotonic_counter,
        envelope.log_sequence,
    )


def _cmp_int(x: int, y: int) -> int:
    if x < y:
        return -1
    if x > y:
        return 1
    return 0


def _cmp_str(x: str, y: str) -> int:
    if x < y:
        return -1
    if x > y:
        return 1
    return 0


def _cmp_opt_int(x: int | None, y: int | None) -> int:
    if x is None and y is None:
        return 0
    if x is None:
        return -1
    if y is None:
        return 1
    return _cmp_int(x, y)


def _cmp_opt_str(x: str | None, y: str | None) -> int:
    if x is None and y is None:
        return 0
    if x is None:
        return -1
    if y is None:
        return 1
    return _cmp_str(x, y)


def compare(a: EventEnvelope, b: EventEnvelope) -> int:
    """Total order over envelopes per DECISION-007 (negative / zero / positive)."""
    for step in (
        _cmp_opt_int(a.venue_sequence, b.venue_sequence),
        _cmp_opt_str(a.server_ts, b.server_ts),
        _cmp_str(a.local_receive_ts, b.local_receive_ts),
        _cmp_int(a.monotonic_counter, b.monotonic_counter),
        _cmp_int(a.log_sequence, b.log_sequence),
    ):
        if step != 0:
            return step
    return 0
