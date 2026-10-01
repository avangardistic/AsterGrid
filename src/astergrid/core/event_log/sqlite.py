"""SQLite-backed append-only event log (Phase 7b), stdlib ``sqlite3`` only.

The ledger favours durability over throughput (WAL + synchronous=FULL); append
cadence is second-scale. It stores the domain EVENT payload as canonical JSON
plus the envelope metadata columns; it is a generic event store — it does not
fold or interpret domain events beyond ``kind`` + payload. ``log_sequence`` and
``content_hash`` are allocated/computed atomically per append (single transaction).
This module is inside ``core/`` and imports no ``logging`` and no clock.
"""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from astergrid.core.events import (
    ENVELOPE_SCHEMA_VERSION,
    GENESIS_PREV_HASH,
    EventEnvelope,
    content_hash_for,
    event_from_payload,
    event_to_payload,
)
from astergrid.core.serialization import canonical_dumps, canonical_loads

if TYPE_CHECKING:
    from collections.abc import Iterator

    from astergrid.core.events import AnyEvent, ObservedMeta

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS event_log (
    log_sequence INTEGER PRIMARY KEY,
    kind TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    venue_sequence INTEGER NULL,
    server_ts TEXT NULL,
    local_receive_ts TEXT NOT NULL,
    monotonic_counter INTEGER NOT NULL,
    prev_hash TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    schema_version INTEGER NOT NULL
)
"""


class SqliteEventLog:
    """A ``sqlite3`` implementation of :class:`EventLogPort`."""

    def __init__(self, path: str) -> None:
        self._path = path
        self._closed = False
        self._conn = sqlite3.connect(path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=FULL")
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

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
        payload_json = canonical_dumps(event_to_payload(event))
        with self._conn:  # single transaction: sequence + content_hash are atomic
            self._conn.execute(
                "INSERT INTO event_log (log_sequence, kind, payload_json, "
                "venue_sequence, server_ts, local_receive_ts, monotonic_counter, "
                "prev_hash, content_hash, schema_version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    sequence,
                    event.event_kind,
                    payload_json,
                    observed.venue_sequence,
                    observed.server_ts,
                    observed.local_receive_ts,
                    monotonic,
                    prev_hash,
                    content_hash,
                    ENVELOPE_SCHEMA_VERSION,
                ),
            )
        return EventEnvelope(
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

    def read_all(self) -> Iterator[EventEnvelope]:
        cursor = self._conn.execute(
            "SELECT log_sequence, kind, payload_json, venue_sequence, server_ts, "
            "local_receive_ts, monotonic_counter, prev_hash, content_hash, "
            "schema_version FROM event_log ORDER BY log_sequence ASC"
        )
        for row in cursor.fetchall():
            yield _row_to_envelope(row)

    def head_hash(self) -> str:
        cursor = self._conn.execute(
            "SELECT content_hash FROM event_log ORDER BY log_sequence DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row is None:
            return GENESIS_PREV_HASH
        value = row[0]
        if not isinstance(value, str):
            raise ValueError("content_hash column must be text")
        return value

    def head_sequence(self) -> int | None:
        cursor = self._conn.execute(
            "SELECT log_sequence FROM event_log ORDER BY log_sequence DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row is None:
            return None
        value = row[0]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("log_sequence column must be an integer")
        return value

    def close(self) -> None:
        if self._closed:
            return
        self._conn.close()
        self._closed = True


def _as_int(value: object, column: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"column {column} must be an integer")
    return value


def _as_str(value: object, column: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"column {column} must be text")
    return value


def _as_opt_int(value: object, column: str) -> int | None:
    if value is None:
        return None
    return _as_int(value, column)


def _as_opt_str(value: object, column: str) -> str | None:
    if value is None:
        return None
    return _as_str(value, column)


def _row_to_envelope(row: object) -> EventEnvelope:
    if not isinstance(row, (tuple, list)) or len(row) != 10:
        raise ValueError("unexpected event_log row shape")
    kind = _as_str(row[1], "kind")
    payload_obj = canonical_loads(_as_str(row[2], "payload_json"))
    if not isinstance(payload_obj, dict):
        raise ValueError("payload_json must decode to an object")
    return EventEnvelope(
        log_sequence=_as_int(row[0], "log_sequence"),
        event=event_from_payload(kind, payload_obj),
        venue_sequence=_as_opt_int(row[3], "venue_sequence"),
        server_ts=_as_opt_str(row[4], "server_ts"),
        local_receive_ts=_as_str(row[5], "local_receive_ts"),
        monotonic_counter=_as_int(row[6], "monotonic_counter"),
        prev_hash=_as_str(row[7], "prev_hash"),
        content_hash=_as_str(row[8], "content_hash"),
        schema_version=_as_int(row[9], "schema_version"),
    )
