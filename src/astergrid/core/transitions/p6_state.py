"""P6 input markers (Phase 7h-4b-2, B0): arm / cancel / issuance operator intents.

A LEAF module: stdlib + ``arm_state`` vocab (OperationalState/ArmPolicy/
OperatorDecision) + ``arm`` D-09 constants ONLY (never redefine a default). It MUST
NOT import ``core.state``/``core.pass_engine``.

These are the P6 stage inputs, set directly by tests (the 7d DESIGN RULE: markers are
"set directly by tests"; a later adapter sources them). They are OPERATOR INTENTS, not
venue reads.

Dangling-input doctrine (D15): a P6 input row whose target is absent/not-ready is
SKIPPED SILENTLY by the stage and retried next pass (STR-0063: "any event not executed
in this pass is re-evaluated in the next"). This differs from P0's LOUD unknown-identity
ValueError, principled: P0's observations are authoritative venue reads (unknown =
corrupted pipeline = loud); P6's inputs may be legitimately premature (loud would
false-trip). ValueError arises ONLY for malformed rows (here), dup keys / dup issuance
identities (State ctor), and coupling violations (B4).

Frozen, slots, self-validating; ``to_canonical_obj`` keeps Decimals native, enums as
``.value``, omits None optionals (R-JSON-6).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from astergrid.core.transitions.arm import (
    DISTANCE_BAND,
    EDGE_FLOOR_BPS,
    MARGIN_BUFFER_MULT,
    MIN_DEPTH_MULTIPLE,
    OPEN_ORDER_CAP,
)
from astergrid.core.transitions.arm_state import (
    ArmPolicy,
    OperationalState,
    OperatorDecision,
)

_TIF = frozenset({"Gtc", "Ioc", "Alo"})  # §6.2 TIF set


def _sbool(value: object, name: str) -> None:
    if type(value) is not bool:
        raise ValueError(f"{name} must be a bool")


def _sint(value: object, name: str) -> None:
    if type(value) is not int:  # rejects bool (int subclass) and non-ints
        raise ValueError(f"{name} must be an int")


def _dec(value: object, name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} must be a Decimal instance")


@dataclass(frozen=True, slots=True)
class P6ArmInput:
    """P6 per-order arming input (26 fields; the cloid is the ST-05 join key)."""

    cloid: str  # non-empty; join key to ST-05
    generation_disabled: bool
    book_depth_at_target: Decimal  # >= 0
    distance_bps: int  # >= 0
    min_order_size: Decimal  # > 0
    margin_available: Decimal  # >= 0
    margin_required: Decimal  # >= 0
    exposure_caps_ok: bool
    open_order_count: int  # >= 0
    price_normalized_ok: bool
    size_normalized_ok: bool
    market_state: OperationalState
    net_expected_edge_bps: Decimal  # any sign
    policy: ArmPolicy | None
    timeout_s: int | None  # None or >= 0
    tif: str  # in {Gtc,Ioc,Alo}
    expires_after: int  # > 0 (DECISION-008)
    intent_log_seq: int  # >= 0
    decision: OperatorDecision | None = None
    elapsed_s: int = 0  # >= 0
    webhook_error: bool = False
    min_depth_multiple: int = MIN_DEPTH_MULTIPLE  # > 0 (arm.py default)
    distance_band: tuple[int, int] = DISTANCE_BAND  # 2 ints, lo <= hi
    margin_buffer_mult: Decimal = MARGIN_BUFFER_MULT  # >= 0
    open_order_cap: int = OPEN_ORDER_CAP  # > 0
    edge_floor_bps: Decimal = EDGE_FLOOR_BPS  # any sign

    def __post_init__(self) -> None:
        if not isinstance(self.cloid, str) or not self.cloid:
            raise ValueError("cloid must be a non-empty str")
        _sbool(self.generation_disabled, "generation_disabled")
        _sbool(self.exposure_caps_ok, "exposure_caps_ok")
        _sbool(self.price_normalized_ok, "price_normalized_ok")
        _sbool(self.size_normalized_ok, "size_normalized_ok")
        _sbool(self.webhook_error, "webhook_error")
        _dec(self.book_depth_at_target, "book_depth_at_target")
        if self.book_depth_at_target < 0:
            raise ValueError("book_depth_at_target must be >= 0")
        _dec(self.min_order_size, "min_order_size")
        if self.min_order_size <= 0:
            raise ValueError("min_order_size must be > 0")
        _dec(self.margin_available, "margin_available")
        if self.margin_available < 0:
            raise ValueError("margin_available must be >= 0")
        _dec(self.margin_required, "margin_required")
        if self.margin_required < 0:
            raise ValueError("margin_required must be >= 0")
        _dec(self.net_expected_edge_bps, "net_expected_edge_bps")
        _dec(self.margin_buffer_mult, "margin_buffer_mult")
        if self.margin_buffer_mult < 0:
            raise ValueError("margin_buffer_mult must be >= 0")
        _dec(self.edge_floor_bps, "edge_floor_bps")
        _sint(self.distance_bps, "distance_bps")
        if self.distance_bps < 0:
            raise ValueError("distance_bps must be >= 0")
        _sint(self.open_order_count, "open_order_count")
        if self.open_order_count < 0:
            raise ValueError("open_order_count must be >= 0")
        _sint(self.expires_after, "expires_after")
        if self.expires_after <= 0:
            raise ValueError("expires_after must be a positive int (DECISION-008)")
        _sint(self.intent_log_seq, "intent_log_seq")
        if self.intent_log_seq < 0:
            raise ValueError("intent_log_seq must be an int >= 0")
        _sint(self.elapsed_s, "elapsed_s")
        if self.elapsed_s < 0:
            raise ValueError("elapsed_s must be >= 0")
        _sint(self.min_depth_multiple, "min_depth_multiple")
        if self.min_depth_multiple <= 0:
            raise ValueError("min_depth_multiple must be > 0")
        _sint(self.open_order_cap, "open_order_cap")
        if self.open_order_cap <= 0:
            raise ValueError("open_order_cap must be > 0")
        if not isinstance(self.market_state, OperationalState):
            raise ValueError("market_state must be an OperationalState")
        if self.policy is not None and not isinstance(self.policy, ArmPolicy):
            raise ValueError("policy must be an ArmPolicy or None")
        if self.decision is not None and not isinstance(
            self.decision, OperatorDecision
        ):
            raise ValueError("decision must be an OperatorDecision or None")
        if self.timeout_s is not None:
            _sint(self.timeout_s, "timeout_s")
            if self.timeout_s < 0:
                raise ValueError("timeout_s must be >= 0 or None")
        if self.tif not in _TIF:
            raise ValueError(f"tif must be one of {sorted(_TIF)}: {self.tif!r}")
        if (
            not isinstance(self.distance_band, tuple)
            or len(self.distance_band) != 2
            or type(self.distance_band[0]) is not int
            or type(self.distance_band[1]) is not int
        ):
            raise ValueError("distance_band must be a 2-tuple of ints")
        if self.distance_band[0] > self.distance_band[1]:
            raise ValueError("distance_band lo must be <= hi")

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "cloid": self.cloid,
            "generation_disabled": self.generation_disabled,
            "book_depth_at_target": self.book_depth_at_target,
            "distance_bps": self.distance_bps,
            "min_order_size": self.min_order_size,
            "margin_available": self.margin_available,
            "margin_required": self.margin_required,
            "exposure_caps_ok": self.exposure_caps_ok,
            "open_order_count": self.open_order_count,
            "price_normalized_ok": self.price_normalized_ok,
            "size_normalized_ok": self.size_normalized_ok,
            "market_state": self.market_state.value,
            "net_expected_edge_bps": self.net_expected_edge_bps,
            "tif": self.tif,
            "expires_after": self.expires_after,
            "intent_log_seq": self.intent_log_seq,
            "elapsed_s": self.elapsed_s,
            "webhook_error": self.webhook_error,
            "min_depth_multiple": self.min_depth_multiple,
            "distance_band": [self.distance_band[0], self.distance_band[1]],
            "margin_buffer_mult": self.margin_buffer_mult,
            "open_order_cap": self.open_order_cap,
            "edge_floor_bps": self.edge_floor_bps,
        }
        if self.policy is not None:  # R-JSON-6
            obj["policy"] = self.policy.value
        if self.timeout_s is not None:
            obj["timeout_s"] = self.timeout_s
        if self.decision is not None:
            obj["decision"] = self.decision.value
        return obj


@dataclass(frozen=True, slots=True)
class P6CancelInput:
    """P6 per-order cancel input (cloid join key; expires_after REQUIRED per D-008)."""

    cloid: str  # non-empty
    expires_after: int  # > 0 (DECISION-008, REQUIRED)
    intent_log_seq: int  # >= 0 (REQUIRED)
    tif: str = "Gtc"  # in {Gtc,Ioc,Alo}; Item-3 COINED default

    def __post_init__(self) -> None:
        if not isinstance(self.cloid, str) or not self.cloid:
            raise ValueError("cloid must be a non-empty str")
        _sint(self.expires_after, "expires_after")
        if self.expires_after <= 0:
            raise ValueError("expires_after must be a positive int (DECISION-008)")
        _sint(self.intent_log_seq, "intent_log_seq")
        if self.intent_log_seq < 0:
            raise ValueError("intent_log_seq must be an int >= 0")
        if self.tif not in _TIF:
            raise ValueError(f"tif must be one of {sorted(_TIF)}: {self.tif!r}")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "cloid": self.cloid,
            "tif": self.tif,
            "expires_after": self.expires_after,
            "intent_log_seq": self.intent_log_seq,
        }


@dataclass(frozen=True, slots=True)
class P6IssuanceInput:
    """P6 per-(gen,cycle) ladder-issuance input (both directions)."""

    generation_id: int  # 0..99
    cycle_id: int  # 0..99
    grid_levels: int  # 1..12 (STR-0262 GridLevels; E2 primarily uses 6)
    step_bps: Decimal  # > 0
    first_level_distance_bps: Decimal  # > 0
    is_dominant_bu: bool
    is_dominant_sl: bool
    gen2_distance_multiplier: Decimal  # > 0
    weak_side_first_level_multiplier: Decimal  # > 0
    size_notional_usd: Decimal  # > 0
    edge_clears_floor_bu: bool
    edge_clears_floor_sl: bool

    def __post_init__(self) -> None:
        _sint(self.generation_id, "generation_id")
        if not (0 <= self.generation_id <= 99):
            raise ValueError("generation_id must be within 0..99")
        _sint(self.cycle_id, "cycle_id")
        if not (0 <= self.cycle_id <= 99):
            raise ValueError("cycle_id must be within 0..99")
        _sint(self.grid_levels, "grid_levels")
        if not (1 <= self.grid_levels <= 12):
            raise ValueError("grid_levels must be within 1..12")
        _sbool(self.is_dominant_bu, "is_dominant_bu")
        _sbool(self.is_dominant_sl, "is_dominant_sl")
        _sbool(self.edge_clears_floor_bu, "edge_clears_floor_bu")
        _sbool(self.edge_clears_floor_sl, "edge_clears_floor_sl")
        for name, value in (
            ("step_bps", self.step_bps),
            ("first_level_distance_bps", self.first_level_distance_bps),
            ("gen2_distance_multiplier", self.gen2_distance_multiplier),
            ("weak_side_first_level_multiplier", self.weak_side_first_level_multiplier),
            ("size_notional_usd", self.size_notional_usd),
        ):
            _dec(value, name)
            if value <= 0:
                raise ValueError(f"{name} must be > 0")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "generation_id": self.generation_id,
            "cycle_id": self.cycle_id,
            "grid_levels": self.grid_levels,
            "step_bps": self.step_bps,
            "first_level_distance_bps": self.first_level_distance_bps,
            "is_dominant_bu": self.is_dominant_bu,
            "is_dominant_sl": self.is_dominant_sl,
            "gen2_distance_multiplier": self.gen2_distance_multiplier,
            "weak_side_first_level_multiplier": self.weak_side_first_level_multiplier,
            "size_notional_usd": self.size_notional_usd,
            "edge_clears_floor_bu": self.edge_clears_floor_bu,
            "edge_clears_floor_sl": self.edge_clears_floor_sl,
        }


__all__ = ["P6ArmInput", "P6CancelInput", "P6IssuanceInput"]
