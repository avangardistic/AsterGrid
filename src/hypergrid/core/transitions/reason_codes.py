"""Centralized reason codes for the P0-P6 pass engine (Phase 7d).

Every member is a ``str``-valued enum: it IS a string, so it serializes to its
plain string value with no conversion (canonical form = the value). The value
equals the member name (``auto()`` + :meth:`_generate_next_value_`), so the code
string and its identifier never drift.

Each member carries a same-line provenance comment naming the RULE source (a
Strategy.md ``§``-reference, a ``STR-`` id, or a ``DECISION-`` id) and stating
whether the code string is VERBATIM from that source or COINED in Phase 7d.

Grouping by stage:
  * P2 (locks, §4.7 P2):
        EVOLUTION_IN_FLIGHT_LOCKED, CYCLE_TRANSITION_IN_FLIGHT_LOCKED
  * P3 (same-generation conflict, §4.7 P3):
        CYCLE_LIMIT_REACHED, SAME_GEN_DISABLE_BEATS_EVOLUTION
  * P4 (across-generation precedence, §4.7 P4):
        ACROSS_GEN_EVOLUTION_BEFORE_CYCLE, ACROSS_GEN_LOWER_GEN_ID_FIRST

Codes reserved for Phase 7e/7f are intentionally ABSENT (they need §4/§5 or P0
semantics not present in Phase 7d): RETURN_LEVEL_UNVERIFIED, SUCCESSOR_LOCK_ACTIVE,
GENERATION_ID_LIMIT (all DECISION-013). Do NOT add them here.
"""

from __future__ import annotations

from enum import StrEnum, auto


class ReasonCode(StrEnum):
    """A stage arbitration reason; canonical form is its plain string value."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        # auto() yields the member name, so value == name (no drift, short lines).
        return name

    # --- P2 locks (§4.7 P2) ---
    EVOLUTION_IN_FLIGHT_LOCKED = auto()  # §4.7 P2 — COINED in 7d
    CYCLE_TRANSITION_IN_FLIGHT_LOCKED = auto()  # §4.7 P2 — COINED in 7d
    # --- P3 same-generation conflict (§4.7 P3) ---
    CYCLE_LIMIT_REACHED = auto()  # §4.7 P3 + DECISION-013 — VERBATIM
    SAME_GEN_DISABLE_BEATS_EVOLUTION = auto()  # §4.7 P3 — COINED in 7d
    # --- P4 across-generation precedence (§4.7 P4) ---
    ACROSS_GEN_EVOLUTION_BEFORE_CYCLE = auto()  # §4.7 P4 — COINED in 7d
    ACROSS_GEN_LOWER_GEN_ID_FIRST = auto()  # §4.7 P4 — COINED in 7d
