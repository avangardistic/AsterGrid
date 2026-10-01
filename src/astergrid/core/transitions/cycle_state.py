"""Typed per-Cycle ST-* domain state + the Cycle transition markers (Phase 7f).

A LEAF module: it imports ONLY the stdlib (same rule as ``generation_state.py``).
It MUST NOT import ``core.state`` or ``core.pass_engine``.

Holds the typed ST-03 (cycle lifecycle) and ST-10 (reference prices) domain rows,
plus the §5 arbitration markers the Cycle transition reads: ``CycleTerminalMarkers``
(per old-cycle terminal-event inputs) and ``NonOverlapData`` (the real §5.6 input).
All money/price/bps values are ``Decimal`` (never float/int) and are validated at
construction (7e doctrine: malformed markers raise here; semantic failures BLOCK
in the transition). Canonical serialization keeps Decimals as Decimals — the
canonical-JSON layer tags them (R-JSON-2) at dumps time. Absent optionals are
OMITTED (R-JSON-6).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

# §5.2/§5.3 cycle lifecycle states.
_CYCLE_LIFECYCLES = frozenset({"CREATED", "ACTIVE", "TERMINAL_PENDING", "COMPLETED"})
# §5.4 reference-derivation policy names (verbatim).
_DERIVATIONS = frozenset(
    {"TERMINAL_EXECUTION", "TERMINAL_VWAP", "TERMINAL_MID", "TERMINAL_PLUS_STEP"}
)
_GROUPS = frozenset({"BU", "SL"})  # §5.6 traversal direction


def _require_id(value: int, name: str) -> None:
    if not (0 <= value <= 99):  # §3 range
        raise ValueError(f"{name} must be within 0..99: {value}")


def _require_pos_decimal(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} must be a Decimal instance")
    if value <= 0:
        raise ValueError(f"{name} must be > 0")


@dataclass(frozen=True, slots=True)
class CycleState:
    """ST-03: a Cycle's §5.2/§5.3 lifecycle state."""

    generation_id: int
    cycle_id: int
    lifecycle: str  # CREATED / ACTIVE / TERMINAL_PENDING / COMPLETED (validated)

    def __post_init__(self) -> None:
        _require_id(self.generation_id, "generation_id")
        _require_id(self.cycle_id, "cycle_id")
        if self.lifecycle not in _CYCLE_LIFECYCLES:
            raise ValueError(f"invalid cycle lifecycle: {self.lifecycle!r}")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "generation_id": self.generation_id,
            "cycle_id": self.cycle_id,
            "lifecycle": self.lifecycle,
        }


@dataclass(frozen=True, slots=True)
class ReferencePriceRecord:
    """ST-10: the immutable execution-grounded reference for a NEW cycle (§5.4)."""

    generation_id: int
    cycle_id: int  # the NEW cycle the reference was captured for
    reference: Decimal  # captured reference, full precision, > 0 (never float/int)
    derivation: str  # one of the four §5.4 policies (validated)

    def __post_init__(self) -> None:
        _require_id(self.generation_id, "generation_id")
        _require_id(self.cycle_id, "cycle_id")
        _require_pos_decimal(self.reference, "reference")
        if self.derivation not in _DERIVATIONS:
            raise ValueError(f"invalid reference derivation: {self.derivation!r}")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "generation_id": self.generation_id,
            "cycle_id": self.cycle_id,
            "reference": self.reference,  # stays Decimal; tagged at dumps time
            "derivation": self.derivation,
        }


@dataclass(frozen=True, slots=True)
class NonOverlapData:
    """The real §5.6 non-overlap input (all fields REQUIRED = complete).

    Inputs are assumed tick/lot-normalized (STR-0363); the transition does NOT
    renormalize and does NOT verify normalization.
    """

    old_reference_price: Decimal
    old_terminal_execution_price: Decimal
    new_level_prices: tuple[Decimal, ...]  # non-empty; Level-1 = index 0
    direction: str  # BU or SL (validated)
    live_same_group_prices: tuple[Decimal, ...]  # may be empty (vacuous N3)
    step_bps: Decimal  # §7.1 StepBps, input to the STR-0361 epsilon only
    tick_size: Decimal

    def __post_init__(self) -> None:
        _require_pos_decimal(self.old_reference_price, "old_reference_price")
        _require_pos_decimal(
            self.old_terminal_execution_price, "old_terminal_execution_price"
        )
        if not self.new_level_prices:
            raise ValueError("new_level_prices must be non-empty")
        for price in self.new_level_prices:
            _require_pos_decimal(price, "new_level_price")
        if self.direction not in _GROUPS:
            raise ValueError(f"direction must be BU or SL: {self.direction!r}")
        for price in self.live_same_group_prices:
            _require_pos_decimal(price, "live_same_group_price")
        _require_pos_decimal(self.step_bps, "step_bps")
        _require_pos_decimal(self.tick_size, "tick_size")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "old_reference_price": self.old_reference_price,
            "old_terminal_execution_price": self.old_terminal_execution_price,
            "new_level_prices": list(self.new_level_prices),
            "direction": self.direction,
            "live_same_group_prices": list(self.live_same_group_prices),
            "step_bps": self.step_bps,
            "tick_size": self.tick_size,
        }


@dataclass(frozen=True, slots=True)
class CycleTerminalMarkers:
    """Per old-cycle terminal-event inputs the §5.2/§5.3 transition reads.

    Keyed to the OLD cycle (generation_id, cycle_id) whose terminal event this
    row drives; S7/S8 resume stays keyed here. Set directly by tests in 7f; a real
    P0 will populate these from envelopes in a later phase.
    """

    generation_id: int
    cycle_id: int  # the OLD cycle whose terminal event this drives
    terminal_event_verified: bool = False
    exhausted_side_pending_cancelled: bool = False  # §5.2 step 2
    authoritative_state_reconciled: bool = False  # §5.2 step 3 / §5.3 D3
    non_overlap_passed: bool = False  # fallback when non_overlap_data absent
    ladder_gate_passed: bool = False  # §5.2 step 8 (pure gate in 7f)
    captured_reference_price: Decimal | None = None
    nominal_reference_price: Decimal | None = None
    reference_price_tolerance_bps: Decimal | None = None  # §14 bound, read as-is
    reference_derivation: str | None = None
    non_overlap_data: NonOverlapData | None = None  # real §5.6 input when present
    all_progression_orders_cancelled: bool = False  # §5.3 D2

    def __post_init__(self) -> None:
        _require_id(self.generation_id, "generation_id")
        _require_id(self.cycle_id, "cycle_id")
        if self.captured_reference_price is not None:
            _require_pos_decimal(
                self.captured_reference_price, "captured_reference_price"
            )
        if self.nominal_reference_price is not None:
            _require_pos_decimal(
                self.nominal_reference_price, "nominal_reference_price"
            )
        if self.reference_price_tolerance_bps is not None:
            _require_pos_decimal(
                self.reference_price_tolerance_bps, "reference_price_tolerance_bps"
            )
        if (
            self.reference_derivation is not None
            and self.reference_derivation not in _DERIVATIONS
        ):
            raise ValueError(
                f"invalid reference derivation: {self.reference_derivation!r}"
            )

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "generation_id": self.generation_id,
            "cycle_id": self.cycle_id,
            "terminal_event_verified": self.terminal_event_verified,
            "exhausted_side_pending_cancelled": self.exhausted_side_pending_cancelled,
            "authoritative_state_reconciled": self.authoritative_state_reconciled,
            "non_overlap_passed": self.non_overlap_passed,
            "ladder_gate_passed": self.ladder_gate_passed,
            "all_progression_orders_cancelled": self.all_progression_orders_cancelled,
        }
        if self.captured_reference_price is not None:
            obj["captured_reference_price"] = self.captured_reference_price
        if self.nominal_reference_price is not None:
            obj["nominal_reference_price"] = self.nominal_reference_price
        if self.reference_price_tolerance_bps is not None:
            obj["reference_price_tolerance_bps"] = self.reference_price_tolerance_bps
        if self.reference_derivation is not None:
            obj["reference_derivation"] = self.reference_derivation
        if self.non_overlap_data is not None:
            obj["non_overlap_data"] = self.non_overlap_data.to_canonical_obj()
        return obj
