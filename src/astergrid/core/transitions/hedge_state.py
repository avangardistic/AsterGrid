"""P1 markers + hedge intent + enums (Phase 7g-3b) — a leaf.

Imports ONLY the stdlib at runtime; ``LevelFillState`` is referenced ONLY under
``TYPE_CHECKING`` (the marker carries a tuple of them but never constructs or
isinstance-checks them — they are built and validated by tests / 7g-3a). It MUST
NOT import ``core.state`` or ``core.pass_engine``.

Holds: ``EPSILON_H`` (DECISION-016 ε_H, the single source of truth — ``hedge.py``
imports it, never redefines it); ``P1ExposureMarkers`` (the 10-field P1 input, a
7d-style marker set directly by tests, projected from ST-04/venue in 7h);
``HedgeExecution`` / ``IntentTag`` / ``RemainderHedgeStatus`` enums; and
``HedgeIntent`` (the ST-23 content). All money/qty is Decimal; frozen, slots,
self-validating; canonical serialization keeps Decimals and emits enums as their
plain string value.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from astergrid.core.transitions.exposure_state import LevelFillState

# DECISION-016 ε_H (owner-pinned constant, not a dynamic default). Single source:
# hedge.py imports this; redefining it there is forbidden.
EPSILON_H = Decimal("1")

_EXPOSURE_CORRECTION_INTENT = "EXPOSURE_CORRECTION_INTENT"


class _NameValueStrEnum(StrEnum):
    """StrEnum base whose ``auto()`` value equals the member name (no drift)."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name


class HedgeExecution(_NameValueStrEnum):
    """§11.2 execution mode; canonical form is the plain string value."""

    IOC = "Ioc"  # §11.2 L871 / §6.2 L574 TIF — VERBATIM (explicit, not auto())
    PREFER_MAKER = auto()  # STR-0207 maker-side preference — COINED


class IntentTag(_NameValueStrEnum):
    """Intent classification; canonical form is the plain string value."""

    EXPOSURE_CORRECTION_INTENT = auto()  # §11.1 priority diagram — VERBATIM
    ENTRY_INTENT = auto()  # §11.3 eligibility — VERBATIM (never built in 7g-3b)


class RemainderHedgeStatus(_NameValueStrEnum):
    """§11.4 partial-fill remainder tri-state; canonical form is the string value."""

    WORKING_NOT_YET_EXPOSURE = auto()  # §11.4 (STR-0213) — COINED
    PENDING_EMERGENCY_EXECUTION = auto()  # §11.4 -> §9.1 (STR-0214) — COINED
    SKIPPED_RESIDUAL_ZERO = auto()  # §11.4 skipped residual zero (STR-0214) — COINED


@dataclass(frozen=True, slots=True)
class P1ExposureMarkers:
    """The 10-field P1 input (markers set by tests; 7h projects from ST-04/venue)."""

    level_fills: tuple[LevelFillState, ...]
    net_position: Decimal  # signed net (any sign)
    tau_acc: Decimal  # D-16 ExposureTolerance as accounting residue, > 0
    min_notional_usd: Decimal  # venue minimum order value in USD, > 0
    mark_price: Decimal  # M, the q_min divisor, > 0
    max_exposure_imbalance: Decimal  # τ_I, > 0
    emergency_tolerance: Decimal  # d_emergency, > 0
    margin_distance: Decimal  # bps basis (matches d_emergency), >= 0
    normal_tolerance: Decimal  # > 0
    transient_tolerance: Decimal  # >= normal_tolerance

    def __post_init__(self) -> None:
        _pos(self.tau_acc, "tau_acc")
        _pos(self.min_notional_usd, "min_notional_usd")
        _pos(self.mark_price, "mark_price")
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
            "level_fills": [f.to_canonical_obj() for f in self.level_fills],
            "net_position": self.net_position,
            "tau_acc": self.tau_acc,
            "min_notional_usd": self.min_notional_usd,
            "mark_price": self.mark_price,
            "max_exposure_imbalance": self.max_exposure_imbalance,
            "emergency_tolerance": self.emergency_tolerance,
            "margin_distance": self.margin_distance,
            "normal_tolerance": self.normal_tolerance,
            "transient_tolerance": self.transient_tolerance,
        }


@dataclass(frozen=True, slots=True)
class HedgeIntent:
    """ST-23 content: the §11.2 corrective hedge intent (amount is the exact Δ̂).

    ``amount == Δ̂`` verbatim (signed; positive = buy-side correction, Δ>0 =
    under-exposed); side/qty mapping into venue buy/sell is order construction (7h+).
    ``|amount| <= |Δ|`` holds BY CONSTRUCTION (Δ̂ ∈ {0, Δ}; §18/GATE-017 no-over-
    hedge). The zero-amount intent is the explicit no-correction record.
    """

    intent_tag: IntentTag
    amount: Decimal  # signed Δ̂ (may be 0)
    acute: bool
    execution: HedgeExecution

    def __post_init__(self) -> None:
        if self.intent_tag != IntentTag.EXPOSURE_CORRECTION_INTENT:
            raise ValueError("intent_tag must be EXPOSURE_CORRECTION_INTENT")
        if not isinstance(self.amount, Decimal):
            raise ValueError("amount must be a Decimal instance")
        if type(self.acute) is not bool:
            raise ValueError("acute must be a bool")
        if not isinstance(self.execution, HedgeExecution):
            raise ValueError("execution must be a HedgeExecution")
        if self.acute != (self.execution == HedgeExecution.IOC):
            raise ValueError("coherence: acute <=> execution == IOC")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "intent_tag": self.intent_tag.value,
            "amount": self.amount,
            "acute": self.acute,
            "execution": self.execution.value,
        }


def _pos(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} must be a Decimal instance")
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
