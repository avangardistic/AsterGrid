"""astergrid.core — the pure, deterministic domain.

INVARIANTS (enforced by tests/test_core_no_logging.py):
  * This package MUST NOT import `logging` (the core never logs; it returns
    decisions/events and the runtime shell logs them — DECISION-023).
  * Every import in this package MUST resolve to the Python standard library
    (no third-party dependency — DECISION-022).

Additional runtime rules (to be honored as domain logic is added in Phase 7b+):
  * Single-threaded and pure (no wall-clock reads, no randomness, no I/O).
  * No `float` in the decision/money path — `int` / `decimal.Decimal` only.

Phase 7a: intentionally empty (no domain logic yet).
"""

__all__: list[str] = []
