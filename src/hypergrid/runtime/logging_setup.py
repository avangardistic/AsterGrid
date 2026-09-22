"""Logging skeleton for the runtime shell (DECISION-023).

Provides a JSON formatter, a per-run context (``run_id`` / ``basket_id`` via
``contextvars``), and a ``redact()`` helper that strips secret-bearing keys
before anything is logged. The pure ``hypergrid.core`` package never imports
this module (or ``logging`` at all).

No secret material is ever emitted. Every emitted record carries ``run_id``,
``basket_id``, a monotonic timestamp and a wall-clock timestamp.
"""

from __future__ import annotations

import contextvars
import json
import logging
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime

# Keys whose values must never appear in any log (case-insensitive match).
# Sourced from DECISION-023 logging rules.
REDACT_KEYS: frozenset[str] = frozenset(
    {
        "secret",
        "api_secret",
        "apisecret",
        "api_key",
        "apikey",
        "private_key",
        "privatekey",
        "signature",
        "sig",
        "password",
        "passwd",
        "token",
        "authorization",
        "auth",
        "mnemonic",
        "seed",
        "wallet",
    }
)

_REDACTED = "[REDACTED]"

_run_id: contextvars.ContextVar[str] = contextvars.ContextVar("run_id", default="-")
_basket_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "basket_id", default="-"
)


def set_context(run_id: str, basket_id: str) -> None:
    """Set the per-run logging context (propagated via contextvars)."""
    _run_id.set(run_id)
    _basket_id.set(basket_id)


def redact(payload: object) -> object:
    """Return a copy of ``payload`` with secret-bearing keys removed.

    Recurses into mappings and sequences. Strings/scalars pass through. Keys
    are matched case-insensitively against :data:`REDACT_KEYS`.
    """
    if isinstance(payload, Mapping):
        out: dict[str, object] = {}
        for key, value in payload.items():
            key_str = str(key)
            if key_str.lower() in REDACT_KEYS:
                out[key_str] = _REDACTED
            else:
                out[key_str] = redact(value)
        return out
    if isinstance(payload, (str, bytes)):
        return payload
    if isinstance(payload, Sequence):
        return [redact(item) for item in payload]
    return payload


class JsonFormatter(logging.Formatter):
    """Format a log record as a single JSON line (see module docstring)."""

    def format(self, record: logging.LogRecord) -> str:
        extra_obj = getattr(record, "extra", None)
        extra: dict[str, object] = {}
        if isinstance(extra_obj, Mapping):
            redacted = redact(extra_obj)
            if isinstance(redacted, dict):
                extra = redacted
        line: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "ts_monotonic": time.monotonic(),
            "run_id": _run_id.get(),
            "basket_id": _basket_id.get(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "extra": extra,
        }
        return json.dumps(line, separators=(",", ":"), sort_keys=True)
