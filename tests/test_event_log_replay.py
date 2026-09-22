"""Replay determinism: in-memory and SQLite logs produce byte-identical output."""

import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path

from hypergrid.core.event_log import InMemoryEventLog, SqliteEventLog
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
    scenario_dumps,
)

_TS = "2026-09-22T00:00:00.000000Z"


@contextmanager
def _no_ambient() -> Iterator[None]:
    def boom(*_a: object, **_k: object) -> object:
        raise AssertionError("clock/randomness accessed")

    with (
        mock_patch(time, "time", boom),
        mock_patch(time, "monotonic", boom),
        mock_patch(random, "random", boom),
        mock_patch(os, "urandom", boom),
    ):
        yield


@contextmanager
def mock_patch(obj: object, name: str, value: object) -> Iterator[None]:
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


def _steps() -> list[tuple[AnyEvent, ObservedMeta]]:
    meta_a = ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)
    meta_b = ObservedMeta(
        venue_sequence=100,
        server_ts="2026-09-22T00:00:01.000000Z",
        local_receive_ts=_TS,
    )
    intent = IntentEvent(
        intent_classification="ENTRY_INTENT",
        target_generation_id=0,
        target_cycle_id=0,
        target_level_id=1,
        target_direction="BU",
        requested_size=Decimal("0.001"),
        requested_price=Decimal("100000"),
        cloid="c1",
        acute=False,
    )
    command = CommandEvent(
        cloid="c1", action="submit", tif="Alo", causal_predecessors=(0,)
    )
    ack = AcknowledgmentEvent(
        cloid="c1", ack_status="resting", causal_predecessors=(1,)
    )
    fill = FillEvent(
        cloid="c1",
        filled_quantity=Decimal("0.001"),
        price=Decimal("100000"),
        is_snapshot=False,
        causal_predecessors=(1,),
    )
    obs = ObservationEvent(
        source_endpoint="clearinghouseState",
        read_timestamp=_TS,
        payload_fingerprint="abc",
        freshness_window_seconds=6,
        is_full=True,
    )
    trans = StateTransitionEvent(
        prior_state="INTENT", next_state="POSITION_VERIFIED", reason_code="VERIFIED"
    )
    pattern: list[tuple[AnyEvent, ObservedMeta]] = [
        (intent, meta_a),
        (command, meta_a),
        (ack, meta_b),
        (fill, meta_b),
        (obs, meta_b),
        (trans, meta_a),
    ]
    steps: list[tuple[AnyEvent, ObservedMeta]] = []
    while len(steps) < 20:
        steps.extend(pattern)
    return steps[:20]


def _run(tmp: Path) -> tuple[str, list[str], str]:
    tmp.mkdir(parents=True, exist_ok=True)
    mem = InMemoryEventLog()
    sqlite_log = SqliteEventLog(str(tmp / "log.db"))
    try:
        with _no_ambient():
            for event, meta in _steps():
                env_mem = mem.append(event, meta)
                env_sq = sqlite_log.append(event, meta)
                assert env_mem.content_hash == env_sq.content_hash
            mem_envs = list(mem.read_all())
            sq_envs = list(sqlite_log.read_all())
            mem_bytes = scenario_dumps(mem_envs)
            sq_bytes = scenario_dumps(sq_envs)
            assert mem_bytes == sq_bytes
            hashes = [e.content_hash for e in mem_envs]
            assert mem.head_hash() == sqlite_log.head_hash()
            seqs = [e.log_sequence for e in mem_envs]
            assert seqs == list(range(20))
            return mem_bytes, hashes, mem.head_hash()
    finally:
        sqlite_log.close()


def test_empty_log_head_is_genesis(tmp_path: Path) -> None:
    mem = InMemoryEventLog()
    assert mem.head_hash() == GENESIS_PREV_HASH
    assert mem.head_sequence() is None
    sqlite_log = SqliteEventLog(str(tmp_path / "empty.db"))
    try:
        assert sqlite_log.head_hash() == GENESIS_PREV_HASH
        assert sqlite_log.head_sequence() is None
    finally:
        sqlite_log.close()


def test_replay_is_byte_identical(tmp_path: Path) -> None:
    bytes1, hashes1, head1 = _run(tmp_path / "run1")
    bytes2, hashes2, head2 = _run(tmp_path / "run2")
    assert bytes1 == bytes2
    assert hashes1 == hashes2
    assert head1 == head2
    assert len(hashes1) == 20
