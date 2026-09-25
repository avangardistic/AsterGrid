"""P0 observation markers (Phase 7h-1) — a leaf.

Imports ONLY the stdlib at runtime; ``LevelFillState`` / ``P1ExposureMarkers`` are
referenced ONLY under ``TYPE_CHECKING`` (the hedge_state precedent). It MUST NOT
import ``core.state`` or ``core.pass_engine``.

Holds the P0 input markers (a 7d-style marker set directly by tests in 7h-1; a
later adapter/FillEvent/fold path populates them event-sourced):

  * ``PerLevelObservation`` — one observed level: identity quadruple, the observed
    §6.1 ``lifecycle`` string, the CUMULATIVE VERIFIED ``filled_quantity`` (R10a),
    and the two verification bits. The §6.1 HARD RULE
    (``FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED``, Strategy.md §6.1 L570)
    is enforced at construction — a bare ack can never claim FILLED.
  * ``P0ObservationMarkers`` — the P0 stage input: the observations (identities
    UNIQUE), ``net_position`` (clearinghouseState, any sign; DECISION-002),
    ``mark_price`` (M, > 0), and the 7 config-resolution externals carried
    verbatim (ST-11 territory; SAME validations as ``P1ExposureMarkers``).

RULINGS (Owner-pinned, binding — OCaml parity depends on them):
  * R9  — P0 OBSERVATION BOUNDARY: fills/lifecycle/mark_price/net_position have no
    in-pipeline producer (P6 stub, no adapters, ``FillEvent`` has no producer,
    ``fold`` writes neither ST-04 nor ST-19), so they arrive as MARKERS; P0 RECORDS,
    never derives. Grounded jointly (§4.7 P0 is one line with no read path).
  * R10a — ``filled_quantity`` is the VERIFIED filled quantity (STR-0199, not
    requested_qty) and CUMULATIVE (DECISION-010/§11.4): the marker carries the
    verified-so-far value; P0 never accumulates (no accumulation rule exists).

All money/qty is Decimal; frozen, slots, self-validating; canonical serialization
keeps Decimals (tagged at dumps time).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_GROUPS = frozenset({"BU", "SL"})
# The 13 §6.1 + LEVEL_SKIPPED (§9.3, 7h-3) — kept identical to the level_state leaf
# (the symmetric "both leaves" design; the C1 cross-test guards against drift).
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
        "LEVEL_SKIPPED",  # §9.3 (7h-3): first-class per-level terminal
    }
)


@dataclass(frozen=True, slots=True)
class PerLevelObservation:
    """One observed level (P0 records; never derives) — R9/R10a."""

    generation_id: int  # 0..99
    cycle_id: int  # 0..99
    direction: str  # "BU" or "SL"
    level_id: int  # 1..12
    lifecycle: str  # one of the 13 §6.1 strings (validated)
    filled_quantity: Decimal  # CUMULATIVE VERIFIED magnitude, >= 0 (R10a)
    order_filled: bool  # venue-observed order-fill bit
    position_delta_verified: bool  # authoritative position-delta confirmation bit

    def __post_init__(self) -> None:
        if not (0 <= self.generation_id <= 99):
            raise ValueError("generation_id must be within 0..99")
        if not (0 <= self.cycle_id <= 99):
            raise ValueError("cycle_id must be within 0..99")
        if self.direction not in _GROUPS:
            raise ValueError(f"direction must be BU or SL: {self.direction!r}")
        if not (1 <= self.level_id <= 12):
            raise ValueError("level_id must be within 1..12")
        if self.lifecycle not in _LIFECYCLES:
            raise ValueError(f"invalid lifecycle: {self.lifecycle!r}")
        if not isinstance(self.filled_quantity, Decimal):
            raise ValueError("filled_quantity must be a Decimal instance")
        if self.filled_quantity < 0:
            raise ValueError("filled_quantity must be >= 0 (magnitude)")
        if type(self.order_filled) is not bool:
            raise ValueError("order_filled must be a bool")
        if type(self.position_delta_verified) is not bool:
            raise ValueError("position_delta_verified must be a bool")
        # §6.1 HARD RULE (Strategy.md §6.1 L570): LEVEL FILLED ⇔ ORDER FILLED ∧
        # POSITION DELTA VERIFIED. Enforced at construction — no state reaches
        # FILLED from a bare userFills message or REST ack alone.
        if self.lifecycle == "FILLED" and not (
            self.order_filled and self.position_delta_verified
        ):
            raise ValueError(
                "§6.1 hard rule: FILLED requires order_filled and "
                "position_delta_verified (no FILLED from a bare ack alone)"
            )

    @property
    def identity(self) -> tuple[int, int, str, int]:
        return (self.generation_id, self.cycle_id, self.direction, self.level_id)

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "generation_id": self.generation_id,
            "cycle_id": self.cycle_id,
            "direction": self.direction,
            "level_id": self.level_id,
            "lifecycle": self.lifecycle,
            "filled_quantity": self.filled_quantity,
            "order_filled": self.order_filled,
            "position_delta_verified": self.position_delta_verified,
        }


@dataclass(frozen=True, slots=True)
class P0ObservationMarkers:
    """The P0 stage input (markers set by tests; 7h projects from ST-04/venue)."""

    observations: tuple[PerLevelObservation, ...]
    net_position: Decimal  # signed net (any sign); clearinghouseState (DECISION-002)
    mark_price: Decimal  # M, the q_min divisor, > 0
    # The 7 config-resolution externals (ST-11 track) — carried verbatim into the
    # P1 markers. SAME validations as P1ExposureMarkers (single source of truth).
    tau_acc: Decimal  # D-16 ExposureTolerance residue, > 0
    min_notional_usd: Decimal  # venue minimum order value in USD, > 0
    max_exposure_imbalance: Decimal  # τ_I, > 0
    emergency_tolerance: Decimal  # d_emergency, > 0
    margin_distance: Decimal  # bps basis (matches d_emergency), >= 0
    normal_tolerance: Decimal  # > 0
    transient_tolerance: Decimal  # >= normal_tolerance

    def __post_init__(self) -> None:
        identities = [obs.identity for obs in self.observations]
        if len(set(identities)) != len(identities):
            raise ValueError("observations must have UNIQUE level identities")
        _pos(self.mark_price, "mark_price")
        _pos(self.tau_acc, "tau_acc")
        _pos(self.min_notional_usd, "min_notional_usd")
        _pos(self.max_exposure_imbalance, "max_exposure_imbalance")
        _pos(self.emergency_tolerance, "emergency_tolerance")
        _pos(self.normal_tolerance, "normal_tolerance")
        if not isinstance(self.net_position, Decimal):
            raise ValueError("net_position must be a Decimal instance")
        if not isinstance(self.margin_distance, Decimal):
            raise ValueError("margin_distance must be a Decimal instance")
        if self.margin_distance < 0:
            raise ValueError("margin_distance must be >= 0")
        if not isinstance(self.transient_tolerance, Decimal):
            raise ValueError("transient_tolerance must be a Decimal instance")
        if self.transient_tolerance < self.normal_tolerance:
            raise ValueError("transient_tolerance must be >= normal_tolerance")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "observations": [obs.to_canonical_obj() for obs in self.observations],
            "net_position": self.net_position,
            "mark_price": self.mark_price,
            "tau_acc": self.tau_acc,
            "min_notional_usd": self.min_notional_usd,
            "max_exposure_imbalance": self.max_exposure_imbalance,
            "emergency_tolerance": self.emergency_tolerance,
            "margin_distance": self.margin_distance,
            "normal_tolerance": self.normal_tolerance,
            "transient_tolerance": self.transient_tolerance,
        }


def _pos(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} must be a Decimal instance")
    if value <= 0:
        raise ValueError(f"{name} must be > 0")


# This leaf carries no field typed with ``LevelFillState``/``P1ExposureMarkers``
# (those are CONSTRUCTED in ``observation.py`` at the projection site), so — unlike
# ``hedge_state`` which types ``level_fills: tuple[LevelFillState, ...]`` — no
# TYPE_CHECKING import of them belongs here. The seam is
# ``PerLevelObservation`` -> ``observation.project_p1_markers`` -> ``LevelFillState``
# rows -> ``P1ExposureMarkers``.
__all__ = ["P0ObservationMarkers", "PerLevelObservation"]
