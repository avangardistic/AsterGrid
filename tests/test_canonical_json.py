"""Canonical JSON rules R-JSON-1..8 (frozen for OCaml interop)."""

from decimal import Decimal

import pytest

from astergrid.core.event_log import InMemoryEventLog
from astergrid.core.events import (
    CommandEvent,
    ObservedMeta,
    StateTransitionEvent,
    scenario_dumps,
)
from astergrid.core.serialization import (
    canonical_dumps,
    canonical_loads,
    is_iso_utc_micros,
)

_TS = "2026-09-22T00:00:00.000000Z"
_META = ObservedMeta(venue_sequence=None, server_ts=None, local_receive_ts=_TS)


def test_rjson1_sort_keys() -> None:
    assert canonical_dumps({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    assert canonical_dumps({"a": 2, "b": 1}) == '{"a":2,"b":1}'


def test_rjson2_decimal_is_tagged_string() -> None:
    assert canonical_dumps(Decimal("1.10")) == '{"__decimal__":"1.10"}'
    restored = canonical_loads(canonical_dumps(Decimal("1.10")))
    assert isinstance(restored, Decimal)
    # exact preservation: "1.10" keeps its trailing zero (exponent -2), not "1.1"
    assert restored.as_tuple() == Decimal("1.10").as_tuple()
    assert restored.as_tuple() != Decimal("1.1").as_tuple()


def test_rjson3_int_is_bare_integer() -> None:
    assert canonical_dumps({"n": 7}) == '{"n":7}'
    assert canonical_loads('{"n":7}') == {"n": 7}


def test_battery_roundtrip() -> None:
    battery: list[object] = [
        "plain",
        7,
        Decimal("0.00005"),
        [1, "two", Decimal("3.3")],
        {"nested": {"x": Decimal("100000"), "y": [True, False]}},
        {"omitted_optional_absent": 1},
    ]
    for value in battery:
        assert canonical_loads(canonical_dumps(value)) == value


def test_rjson5_timestamp_format() -> None:
    assert is_iso_utc_micros("2026-09-22T00:00:00.000000Z")
    assert not is_iso_utc_micros("2026-09-22T00:00:00Z")  # no fractional digits
    assert not is_iso_utc_micros("2026-09-22T00:00:00.000Z")  # 3 not 6
    assert not is_iso_utc_micros("2026-09-22T00:00:00.000000+00:00")  # not Z


def test_float_literal_rejected_on_load() -> None:
    with pytest.raises(ValueError, match="float"):
        canonical_loads('{"x":1.5}')


def test_g1_reject_float_and_none() -> None:
    for bad in (1.5, float("nan"), float("inf"), None):
        with pytest.raises(TypeError):
            canonical_dumps(bad)
    with pytest.raises(TypeError):
        canonical_dumps({"a": None})
    with pytest.raises(TypeError):
        canonical_dumps({"a": [1, 1.5]})


def test_g1_decimal_tag_still_works_but_rejects_smuggled_float() -> None:
    assert canonical_dumps({"__decimal__": "1.10"}) == '{"__decimal__":"1.10"}'
    assert canonical_loads(canonical_dumps({"__decimal__": "1.10"})) == Decimal("1.10")
    assert canonical_dumps(Decimal("1.10")) == '{"__decimal__":"1.10"}'
    with pytest.raises(TypeError):
        canonical_dumps({"__decimal__": 1.5})


def test_rjson4_7_8_scenario_envelope() -> None:
    log = InMemoryEventLog()
    log.append(CommandEvent(cloid="c1", action="submit", tif="Alo"), _META)
    log.append(
        StateTransitionEvent(
            prior_state="INTENT", next_state="VERIFIED", reason_code="OK"
        ),
        _META,
    )
    scenario = canonical_loads(scenario_dumps(log.read_all()))
    assert isinstance(scenario, dict)
    # R-JSON-4: top-level schema_version + payload
    assert scenario["schema_version"] == 1
    payload = scenario["payload"]
    assert isinstance(payload, dict)
    events = payload["events"]
    assert isinstance(events, list)
    # R-JSON-8: ascending log_sequence
    seqs = [e["log_sequence"] for e in events if isinstance(e, dict)]
    assert seqs == [0, 1]
    # R-JSON-7: the hyphenated kind tag is preserved
    kinds = [e["kind"] for e in events if isinstance(e, dict)]
    assert "state-transition" in kinds
