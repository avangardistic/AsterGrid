"""Runtime logging skeleton: JSON formatting, context fields, and redaction."""

import json
import logging

from hypergrid.runtime.logging_setup import JsonFormatter, redact, set_context


def _record(msg: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="hypergrid.runtime.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=None,
        exc_info=None,
    )


def test_formatter_emits_valid_json_with_context() -> None:
    set_context("run-1", "basket-1")
    line = JsonFormatter().format(_record("hello"))
    data = json.loads(line)
    assert data["run_id"] == "run-1"
    assert data["basket_id"] == "basket-1"
    assert data["msg"] == "hello"
    assert data["level"] == "INFO"
    assert "ts" in data and "ts_monotonic" in data


def test_run_and_basket_id_always_present() -> None:
    data = json.loads(JsonFormatter().format(_record("x")))
    assert "run_id" in data
    assert "basket_id" in data


def test_redact_removes_documented_secret_keys() -> None:
    payload = {
        "api_key": "abc",
        "signature": "deadbeef",
        "nested": {"password": "p", "ok": 1},
        "list": [{"token": "t"}, {"ok": 2}],
        "ok": 3,
    }
    redacted = redact(payload)
    assert redacted == {
        "api_key": "[REDACTED]",
        "signature": "[REDACTED]",
        "nested": {"password": "[REDACTED]", "ok": 1},
        "list": [{"token": "[REDACTED]"}, {"ok": 2}],
        "ok": 3,
    }


def test_secrets_never_appear_in_emitted_record() -> None:
    set_context("run-2", "basket-2")
    record = _record("submit")
    record.extra = {"api_key": "SECRET_VALUE", "size": "10"}  # type: ignore[attr-defined]
    line = JsonFormatter().format(record)
    assert "SECRET_VALUE" not in line
    assert "[REDACTED]" in line
