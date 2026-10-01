"""Canonical JSON (R-JSON-1..8), frozen for Python<->OCaml interop (Phase 7b).

Rules implemented here:
  R-JSON-1: objects are emitted with ``sort_keys=True`` (no insertion-order
    reliance).
  R-JSON-2: a ``Decimal`` is carried by its STRING value (never a float, never
    coerced to int). It is wrapped in a one-key tag object
    ``{"__decimal__": "<value>"}`` so it round-trips and OCaml can reconstruct
    it; the numeric payload itself is the string ``"<value>"``.
  R-JSON-3: ``int`` values are emitted as JSON integers (bare).
  R-JSON-4: scenario files use a top-level ``{"schema_version": <int>,
    "payload": {...}}`` envelope (see events.envelope.scenario_dumps).
  R-JSON-5: timestamps are ISO-8601 UTC strings with a ``Z`` suffix and exactly
    6 fractional digits (validated by :func:`is_iso_utc_micros`).
  R-JSON-6: absent optional fields are OMITTED (never ``null``).
  R-JSON-7: event-kind tags are the exact §A2 strings (with the hyphen in
    ``state-transition``).
  R-JSON-8: a scenario payload is ``{"events": [<envelope>, ...]}`` in ascending
    ``log_sequence`` (see events.envelope.scenario_dumps).

Floats are forbidden: emitting a float raises, and parsing a JSON float on load
raises. Only ``int``, ``str``, ``bool``, ``list``, ``dict`` and ``Decimal``
(via the tag) are valid canonical values.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal

DECIMAL_TAG = "__decimal__"

# R-JSON-5: ISO-8601 UTC, 'Z' suffix, exactly six fractional digits.
_ISO_UTC_MICROS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")


def is_iso_utc_micros(value: str) -> bool:
    """Return True iff ``value`` is an ISO-8601 UTC 'Z' timestamp with 6 μs digits."""
    return _ISO_UTC_MICROS.match(value) is not None


def _encode(value: object) -> object:
    """json ``default`` hook: wrap Decimal per R-JSON-2; reject everything else."""
    if isinstance(value, Decimal):
        return {DECIMAL_TAG: str(value)}
    raise TypeError(f"non-canonical type for JSON: {type(value).__name__}")


def _reject_forbidden(value: object) -> None:
    """Pure recursive pre-scan: forbid ``float`` and ``None`` at any depth.

    ``None`` is not a canonical value — absent optionals are OMITTED (R-JSON-6).
    ``float`` is forbidden everywhere. Accepts bool/int/str/Decimal and traverses
    dict/list/tuple. ``__decimal__`` is a RESERVED key (R-JSON-2) carrying a
    string payload; it is traversed like any dict, so a float/None smuggled
    inside the tag still raises. No clock/random/network/filesystem; no side
    effects.
    """
    if isinstance(value, bool):
        return
    if isinstance(value, float):
        raise TypeError("float is not a canonical JSON value")
    if value is None:
        raise TypeError("None is not a canonical JSON value (omit absent optionals)")
    if isinstance(value, (int, str, Decimal)):
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("canonical object keys must be strings")
            _reject_forbidden(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_forbidden(item)
        return
    raise TypeError(f"non-canonical type: {type(value).__name__}")


def canonical_dumps(value: object) -> str:
    """Serialize ``value`` to canonical JSON (R-JSON-1..3, R-JSON-6..7).

    Pre-scans with :func:`_reject_forbidden` so a ``float`` or ``None`` at any
    depth raises before serialization.
    """
    _reject_forbidden(value)
    return json.dumps(
        value,
        default=_encode,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _object_hook(obj: dict[str, object]) -> object:
    """json ``object_hook``: reconstruct Decimal from its tag object."""
    if len(obj) == 1 and DECIMAL_TAG in obj:
        raw = obj[DECIMAL_TAG]
        if not isinstance(raw, str):
            raise ValueError("decimal tag must wrap a string value")
        return Decimal(raw)
    return obj


def _reject_float(raw: str) -> object:
    """json ``parse_float``: floats are forbidden in canonical JSON."""
    raise ValueError(f"float literals are forbidden in canonical JSON: {raw!r}")


def canonical_loads(text: str) -> object:
    """Parse canonical JSON; reconstruct Decimals; reject any float literal."""
    return json.loads(text, object_hook=_object_hook, parse_float=_reject_float)
