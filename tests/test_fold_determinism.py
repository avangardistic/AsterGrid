"""fold() determinism across runs and across log implementations (Phase 7c)."""

from decimal import Decimal
from pathlib import Path

from hypergrid.core.event_log import InMemoryEventLog, SqliteEventLog
from hypergrid.core.event_log.port import EventLogPort
from hypergrid.core.events import (
    GENESIS_PREV_HASH,
    AcknowledgmentEvent,
    AnyEvent,
    CommandEvent,
    FillEvent,
    IntentEvent,
    ObservationEvent,
    ObservedMeta,
    StateTransitionEvent,
)
from hypergrid.core.fold import fold
from hypergrid.core.serialization import canonical_dumps

_TS = "2026-09-22T00:00:00.000000Z"
_META_A = ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)
_META_B = ObservedMeta(
    venue_sequence=100, server_ts="2026-09-22T00:00:01.000000Z", local_receive_ts=_TS
)


def _events() -> list[tuple[AnyEvent, ObservedMeta]]:
    pattern: list[tuple[AnyEvent, ObservedMeta]] = [
        (
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
            _META_A,
        ),
        (CommandEvent(cloid="c1", action="submit", tif="Alo"), _META_A),
        (AcknowledgmentEvent(cloid="c1", ack_status="resting"), _META_B),
        (
            FillEvent(
                cloid="c1",
                filled_quantity=Decimal("0.001"),
                price=Decimal("100000"),
                is_snapshot=False,
            ),
            _META_B,
        ),
        (
            ObservationEvent(
                source_endpoint="clearinghouseState",
                read_timestamp=_TS,
                payload_fingerprint="abc",
                freshness_window_seconds=6,
                is_full=True,
            ),
            _META_B,
        ),
        (
            StateTransitionEvent(
                prior_state="INTENT", next_state="VERIFIED", reason_code="OK"
            ),
            _META_A,
        ),
    ]
    steps: list[tuple[AnyEvent, ObservedMeta]] = []
    while len(steps) < 20:
        steps.extend(pattern)
    return steps[:20]


def _populate(log: EventLogPort) -> None:
    for event, meta in _events():
        log.append(event, meta)


def test_fold_same_list_twice_byte_identical() -> None:
    log = InMemoryEventLog()
    _populate(log)
    envelopes = list(log.read_all())
    assert canonical_dumps(fold(envelopes).to_canonical_obj()) == canonical_dumps(
        fold(envelopes).to_canonical_obj()
    )


def test_fold_two_independent_inmemory_logs_identical() -> None:
    log_a = InMemoryEventLog()
    log_b = InMemoryEventLog()
    _populate(log_a)
    _populate(log_b)
    state_a = fold(log_a.read_all())
    state_b = fold(log_b.read_all())
    assert canonical_dumps(state_a.to_canonical_obj()) == canonical_dumps(
        state_b.to_canonical_obj()
    )


def test_fold_sqlite_matches_inmemory(tmp_path: Path) -> None:
    mem = InMemoryEventLog()
    _populate(mem)
    sqlite_log = SqliteEventLog(str(tmp_path / "log.db"))
    try:
        _populate(sqlite_log)
        mem_state = fold(mem.read_all())
        sq_state = fold(sqlite_log.read_all())
        assert canonical_dumps(mem_state.to_canonical_obj()) == canonical_dumps(
            sq_state.to_canonical_obj()
        )
        assert mem_state.head_hash == sq_state.head_hash
        assert mem_state.event_count == 20
    finally:
        sqlite_log.close()


def test_fold_head_hash_matches_last_envelope() -> None:
    log = InMemoryEventLog()
    _populate(log)
    envelopes = list(log.read_all())
    state = fold(envelopes)
    assert state.head_hash == envelopes[-1].content_hash
    assert state.event_count == 20
    empty = fold([])
    assert empty.head_hash == GENESIS_PREV_HASH
