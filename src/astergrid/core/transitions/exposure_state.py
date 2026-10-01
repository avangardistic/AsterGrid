"""Exposure markers + ST-07/08/09 domain state + ExposureClass (Phase 7g-3a).

A LEAF module: imports ONLY the stdlib (``dataclasses``, ``decimal``, ``enum``).
It MUST NOT import ``core.state`` or ``core.pass_engine``. Co-locates the input
marker (``LevelFillState``), the classification enum (``ExposureClass``), and the
three Basket-singleton ST rows (ST-07/08/09), mirroring the 7f precedent of
markers + ST rows + enum in one leaf.

All money/quantity values are ``Decimal`` (never float/int); everything is frozen,
slots, self-validating; canonical serialization keeps Decimals as Decimals (tagged
at dumps time) and enums as their plain string value.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum, auto

_GROUPS = frozenset({"BU", "SL"})
# The 13 §6.1 pipeline lifecycle strings (verified against Strategy.md §6.1).
_LIFECYCLES = frozenset(
    {
        "INTENT_CREATED",
        "ORDER_SUBMITTED",
        "ORDER_ACKNOWLEDGED",
        "ORDER_ACTIVE",
        "PARTIALLY_FILLED",
        "FILLED",
        "POSITION_VERIFIED",
        "CANCELLED",
        "EMERGENCY",
        "SKIPPED",
        "ERROR",
        "LOCKED",
        "IDLE",
    }
)
# Only these three contribute to ExpectedExposure (§11.1).
COUNTED_LIFECYCLES = frozenset({"PARTIALLY_FILLED", "FILLED", "POSITION_VERIFIED"})
_CLEARINGHOUSE = "clearinghouseState"  # DECISION-002 authoritative source


class ExposureClass(StrEnum):
    """§11.1 ExposureDelta classification; canonical form is its plain string."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name  # value == name (no drift), like ReasonCode

    NORMAL = auto()  # §11.1 L849 — VERBATIM label
    TRANSIENT = auto()  # §11.1 L849 — VERBATIM label
    ESCALATE = auto()  # §11.1 L849 — VERBATIM label


@dataclass(frozen=True, slots=True)
class LevelFillState:
    """Per-Level VERIFIED-fill marker (input to ExpectedExposure).

    ``filled_quantity`` is a magnitude (>= 0); per-leg sign is NEVER stored — R7
    applies the sign in the sum. For PARTIALLY_FILLED it is the verified-so-far
    quantity (DECISION-010 + §11.4), never requested_qty (STR-0199). "Verified" is
    a caller assertion in 7g-3a; a real P0 owns verification from 7h.
    """

    generation_id: int
    cycle_id: int
    direction: str
    level_id: int
    filled_quantity: Decimal  # VERIFIED magnitude, >= 0
    lifecycle: str  # one of the 13 §6.1 strings (validated)

    def __post_init__(self) -> None:
        if not (0 <= self.generation_id <= 99):
            raise ValueError("generation_id must be within 0..99")
        if not (0 <= self.cycle_id <= 99):
            raise ValueError("cycle_id must be within 0..99")
        if self.direction not in _GROUPS:
            raise ValueError(f"direction must be BU or SL: {self.direction!r}")
        if not (1 <= self.level_id <= 12):
            raise ValueError("level_id must be within 1..12")
        if not isinstance(self.filled_quantity, Decimal):
            raise ValueError("filled_quantity must be a Decimal instance")
        if self.filled_quantity < 0:
            raise ValueError("filled_quantity must be >= 0 (magnitude)")
        if self.lifecycle not in _LIFECYCLES:
            raise ValueError(f"invalid lifecycle: {self.lifecycle!r}")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "generation_id": self.generation_id,
            "cycle_id": self.cycle_id,
            "direction": self.direction,
            "level_id": self.level_id,
            "filled_quantity": self.filled_quantity,
            "lifecycle": self.lifecycle,
        }


@dataclass(frozen=True, slots=True)
class ExpectedExposureState:
    """ST-07 Basket singleton: SIGNED net expected exposure (R7; may be negative)."""

    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            raise ValueError("value must be a Decimal instance")

    def to_canonical_obj(self) -> dict[str, object]:
        return {"value": self.value}


@dataclass(frozen=True, slots=True)
class ActualExposureState:
    """ST-08 Basket singleton: signed net position from clearinghouseState only."""

    value: Decimal
    source: str  # MUST equal "clearinghouseState" (DECISION-002 / §15)

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            raise ValueError("value must be a Decimal instance")
        if self.source != _CLEARINGHOUSE:
            raise ValueError(f"source must be {_CLEARINGHOUSE!r} (DECISION-002)")

    def to_canonical_obj(self) -> dict[str, object]:
        return {"value": self.value, "source": self.source}


@dataclass(frozen=True, slots=True)
class ExposureDeltaState:
    """ST-09 Basket singleton: delta = expected - actual (exact), + class + acute.

    classification/is_acute coherence is the WRITER's contract (the 7g-3b P1 writer
    calls the Part-A functions); it CANNOT be validated here (thresholds are
    parameters, not stored).
    """

    expected_value: Decimal
    actual_value: Decimal
    delta: Decimal  # MUST equal expected_value - actual_value (exact)
    classification: ExposureClass
    is_acute: bool

    def __post_init__(self) -> None:
        if not isinstance(self.expected_value, Decimal):
            raise ValueError("expected_value must be a Decimal instance")
        if not isinstance(self.actual_value, Decimal):
            raise ValueError("actual_value must be a Decimal instance")
        if not isinstance(self.delta, Decimal):
            raise ValueError("delta must be a Decimal instance")
        if self.delta != self.expected_value - self.actual_value:
            raise ValueError("delta must equal expected_value - actual_value")
        if not isinstance(self.classification, ExposureClass):
            raise ValueError("classification must be an ExposureClass")
        if type(self.is_acute) is not bool:  # no truthy ints
            raise ValueError("is_acute must be a bool")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "delta": self.delta,
            "classification": self.classification.value,
            "is_acute": self.is_acute,
        }
