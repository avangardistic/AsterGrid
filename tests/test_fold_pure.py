"""fold(): purity, no-mutation, clock-free, totality, metadata correctness."""

import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from astergrid.core.event_log import InMemoryEventLog
from astergrid.core.events import (
    GENESIS_PREV_HASH,
    CommandEvent,
    FillEvent,
    IntentEvent,
    ObservedMeta,
)
from astergrid.core.fold import _empty_state, fold
from astergrid.core.serialization import canonical_dumps

_TS = "2026-09-22T00:00:00.000000Z"
_META = ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)


@contextmanager
def _no_ambient() -> Iterator[None]:
    def boom(*_a: object, **_k: object) -> object:
        raise AssertionError("clock/randomness accessed")

    saved = (time.time, time.monotonic, random.random, os.urandom)
    time.time = boom  # type: ignore[assignment]
    time.monotonic = boom  # type: ignore[assignment]
    random.random = boom  # type: ignore[assignment]
    os.urandom = boom  # type: ignore[assignment]
    try:
        yield
    finally:
        time.time, time.monotonic, random.random, os.urandom = saved


def _small_log() -> InMemoryEventLog:
    log = InMemoryEventLog()
    log.append(
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
        _META,
    )
    log.append(CommandEvent(cloid="c1", action="submit", tif="Alo"), _META)
    log.append(
        FillEvent(
            cloid="c1",
            filled_quantity=Decimal("0.001"),
            price=Decimal("100000"),
            is_snapshot=False,
        ),
        _META,
    )
    return log


def test_fold_is_pure() -> None:
    envelopes = list(_small_log().read_all())
    a = fold(envelopes)
    b = fold(envelopes)
    assert a == b
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )


def test_fold_does_not_mutate_input() -> None:
    envelopes = list(_small_log().read_all())
    snapshot = list(envelopes)
    fold(envelopes)
    assert envelopes == snapshot
    assert len(envelopes) == 3


def test_fold_is_clock_free() -> None:
    envelopes = list(_small_log().read_all())
    with _no_ambient():
        state = fold(envelopes)
    assert state.event_count == 3


def test_fold_is_total() -> None:
    assert fold([]) == _empty_state()
    assert fold(iter([])) == _empty_state()
    envelopes = list(_small_log().read_all())
    assert fold(iter(envelopes)) == fold(envelopes)


def test_fold_metadata_matches_expectation() -> None:
    envelopes = list(_small_log().read_all())
    state = fold(envelopes)
    assert state.event_count == 3
    assert state.log_sequence == 2
    assert state.head_hash == envelopes[-1].content_hash
    counts = dict(state.per_kind_count)
    assert counts["intent"] == 1
    assert counts["command"] == 1
    assert counts["fill"] == 1
    assert counts["observation"] == 0
    assert sum(counts.values()) == 3


def test_empty_fold_head_is_genesis() -> None:
    state = fold([])
    assert state.head_hash == GENESIS_PREV_HASH
    assert state.log_sequence is None
