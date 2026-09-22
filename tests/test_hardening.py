"""Phase 7b hardening (G2): timestamp validation in codec + ObservedMeta + append."""

import pytest

from hypergrid.core.event_log import InMemoryEventLog, SqliteEventLog
from hypergrid.core.events import CommandEvent, ObservedMeta
from hypergrid.core.events.codec import event_from_payload

_GOOD = "2026-09-22T00:00:00.000000Z"
_BAD = "2026-09-22T00:00:00Z"  # no microseconds


def test_codec_rejects_bad_read_timestamp() -> None:
    with pytest.raises(ValueError, match="timestamp"):
        event_from_payload(
            "observation",
            {
                "source_endpoint": "clearinghouseState",
                "read_timestamp": _BAD,
                "payload_fingerprint": "abc",
                "freshness_window_seconds": 6,
                "is_full": True,
            },
        )


def test_codec_rejects_bad_fire_timestamp() -> None:
    with pytest.raises(ValueError, match="timestamp"):
        event_from_payload(
            "timer",
            {
                "timer_kind": "confirmation",
                "fire_timestamp": _BAD,
                "associated_entity": "e",
            },
        )


def test_codec_rejects_bad_operator_timestamp() -> None:
    with pytest.raises(ValueError, match="timestamp"):
        event_from_payload(
            "operator",
            {
                "operator_identity": "op1",
                "timestamp": _BAD,
                "action": "approve",
                "target": "a",
            },
        )


def test_codec_rejects_bad_effective_time() -> None:
    with pytest.raises(ValueError, match="timestamp"):
        event_from_payload(
            "administrative",
            {"config_identity": "cfg", "effective_time": _BAD, "provenance": "owner"},
        )


def test_observed_meta_validates_timestamps() -> None:
    ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_GOOD)
    ObservedMeta(venue_sequence=1, server_ts=_GOOD, local_receive_ts=_GOOD)
    with pytest.raises(ValueError, match="local_receive_ts"):
        ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_BAD)
    with pytest.raises(ValueError, match="server_ts"):
        ObservedMeta(venue_sequence=None, server_ts=_BAD, local_receive_ts=_GOOD)


def _command() -> CommandEvent:
    return CommandEvent(cloid="c1", action="submit", tif="Alo")


def test_append_does_not_advance_head_on_bad_meta_empty() -> None:
    log = InMemoryEventLog()
    with pytest.raises(ValueError):
        log.append(
            _command(),
            ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_BAD),
        )
    assert log.head_sequence() is None


def test_append_does_not_advance_head_on_bad_meta_nonempty(tmp_path: object) -> None:
    path = f"{tmp_path}/log.db"
    log = SqliteEventLog(path)
    try:
        log.append(
            _command(),
            ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_GOOD),
        )
        before = log.head_sequence()
        with pytest.raises(ValueError):
            log.append(
                CommandEvent(
                    cloid="c2", action="submit", tif="Alo"
                ),
                ObservedMeta(
                    venue_sequence=None, server_ts=None, local_receive_ts=_BAD
                ),
            )
        assert log.head_sequence() == before
    finally:
        log.close()


def test_valid_append_still_works() -> None:
    log = InMemoryEventLog()
    env = log.append(
        _command(),
        ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_GOOD),
    )
    assert env.log_sequence == 0
