"""astergrid.core.serialization — pure, stdlib-only canonical JSON (Phase 7b).

The canonical JSON format is FROZEN here as the shared contract between the
Python production runtime and the OCaml CAP-0024 reference model (Phase 7k+).
See `canonical_json` for the R-JSON-1..8 rules. This subpackage is pure: it
never imports `logging`, reads no clock, and uses only the standard library.
"""

from astergrid.core.serialization.canonical_json import (
    DECIMAL_TAG,
    canonical_dumps,
    canonical_loads,
    is_iso_utc_micros,
)

__all__ = [
    "DECIMAL_TAG",
    "canonical_dumps",
    "canonical_loads",
    "is_iso_utc_micros",
]
