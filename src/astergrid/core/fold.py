"""The pure fold (Phase 7c): envelopes -> State, metadata ONLY.

``fold`` is pure, total, clock-free and deterministic. It accumulates only
metadata: the highest ``log_sequence``, the last ``content_hash`` (head_hash),
the envelope count, and per-kind counts for all ten kinds. It performs NO domain
logic — it dispatches on ``event_kind`` solely to increment a counter, reads only
``log_sequence`` and ``content_hash`` from each envelope, and leaves every ST-*
domain field ``None``. Real §4-§13 rules arrive in Phase 7d.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from astergrid.core.events import GENESIS_PREV_HASH
from astergrid.core.state import _EVENT_KINDS, State

if TYPE_CHECKING:
    from collections.abc import Iterable

    from astergrid.core.events import EventEnvelope


def _empty_state() -> State:
    """The State of an empty log: metadata defaults, all domain fields None."""
    return State(
        log_sequence=None,
        head_hash=GENESIS_PREV_HASH,
        event_count=0,
        per_kind_count=tuple(sorted((kind, 0) for kind in _EVENT_KINDS)),
    )


def fold(envelopes: Iterable[EventEnvelope]) -> State:
    """Fold envelopes into a State (metadata only; pure, total, deterministic)."""
    counts: dict[str, int] = {kind: 0 for kind in _EVENT_KINDS}
    last_sequence: int | None = None
    last_hash = GENESIS_PREV_HASH
    event_count = 0
    for envelope in envelopes:
        event_count += 1
        last_sequence = envelope.log_sequence
        last_hash = envelope.content_hash
        counts[envelope.event.event_kind] += 1  # only kind dispatch: a counter
    if event_count == 0:
        return _empty_state()
    return State(
        log_sequence=last_sequence,
        head_hash=last_hash,
        event_count=event_count,
        per_kind_count=tuple(sorted(counts.items())),
    )
