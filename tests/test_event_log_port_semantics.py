"""Both event-log implementations satisfy the port's semantic contract."""

from decimal import Decimal
from pathlib import Path

from hypergrid.core.event_log import InMemoryEventLog, SqliteEventLog
from hypergrid.core.event_log.port import EventLogPort
from hypergrid.core.events import (
    ENVELOPE_SCHEMA_VERSION,
    CommandEvent,
    FillEvent,
    ObservedMeta,
    content_hash_for,
)

_TS = "2026-09-22T00:00:00.000000Z"
_META = ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)


def _check_log(log: EventLogPort) -> None:
    assert log.head_sequence() is None
    assert log.head_hash() == "0" * 64

    env0 = log.append(CommandEvent(cloid="c1", action="submit", tif="Alo"), _META)
    assert env0.log_sequence == 0
    assert env0.monotonic_counter == 0

    env1 = log.append(
        FillEvent(
            cloid="c1",
            filled_quantity=Decimal("0.001"),
            price=Decimal("100000"),
            is_snapshot=False,
        ),
        _META,
    )
    assert env1.log_sequence == 1
    assert log.head_sequence() == 1
    assert log.head_hash() == env1.content_hash

    # content_hash recomputation matches (envelope minus content_hash, per A4).
    recomputed = content_hash_for(
        schema_version=ENVELOPE_SCHEMA_VERSION,
        log_sequence=env1.log_sequence,
        prev_hash=env1.prev_hash,
        event=env1.event,
        venue_sequence=env1.venue_sequence,
        server_ts=env1.server_ts,
        local_receive_ts=env1.local_receive_ts,
        monotonic_counter=env1.monotonic_counter,
    )
    assert recomputed == env1.content_hash
    assert env1.prev_hash == env0.content_hash

    seqs = [e.log_sequence for e in log.read_all()]
    assert seqs == [0, 1]

    log.close()
    log.close()  # idempotent


def test_in_memory_log_satisfies_port() -> None:
    _check_log(InMemoryEventLog())


def test_sqlite_log_satisfies_port(tmp_path: Path) -> None:
    _check_log(SqliteEventLog(str(tmp_path / "log.db")))
