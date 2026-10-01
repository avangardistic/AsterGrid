"""ST-05 order intents & outcomes (Phase 7h-2): inlet + classifier + lifecycle.

A LEAF module: imports ONLY the stdlib plus ``hedge_state.IntentTag`` (same package,
no cycle — CAP-0014/CAP-0015 reuse the §11.1 intent vocabulary). It MUST NOT import
``core.state`` or ``core.pass_engine``.

Contents:
  * ``OrderType`` — COINED inlet vocabulary StrEnum (B1).
  * ``OrderIntent`` + ``construct_order_intent`` — the ST-05 **intent half** (B1,
    CAP-0014 greenfield construction). Malformed input → ``ValueError`` (no row);
    there is NO inlet→SKIPPED path (SKIPPED = tolerance/economics fail, §6.1).
  * ``classify_intent`` — §13.3 ENTRY vs EXPOSURE_CORRECTION by projected
    ``ExposureDelta`` before/after, IGNORING ``reduce_only`` (STR-0240/0241/0242, B2).
  * ``OrderState`` + ``is_legal_order_transition`` — the ST-05 **outcome half**: the
    §6.1 order pipeline of 11 states (§6.1 minus LOCKED/IDLE, which are ST-04's —
    STATE_OWNERSHIP.md single-owner rule L87), with a data transition table
    (CAP-0015 lifecycle). Edges are table-defined now; their triggers
    (ORDER_SUBMITTED entry, fill/ack/cancel/error) are 7h-3/venue's.

All money/qty is Decimal; frozen, slots, self-validating; canonical serialization
keeps Decimals (tagged at dumps) and enums as their plain string value.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum, auto

from astergrid.core.transitions.hedge_state import IntentTag

_GROUPS = frozenset({"BU", "SL"})  # §3 identity direction vocabulary (IntentEvent)


class _NameValueStrEnum(StrEnum):
    """StrEnum base whose ``auto()`` value equals the member name (no drift)."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name


class OrderType(_NameValueStrEnum):
    """Inlet order type. Every member COINED (no §/STR vocabulary for order types).

    ``TWAP`` is consistent with the frozen ``CommandEvent.action`` vocab
    (submit/cancel/modify/twap, ``events/kinds.py:51``); 7h-3 maps these to submit
    actions. The plain string value equals the member name.
    """

    LIMIT = auto()  # COINED — resting limit order (§8 Alo/Gtc pre-arm precedent)
    MARKET = auto()  # COINED — immediate market order
    STOP = auto()  # COINED — stop / trigger order (§6.2 trigger orders)
    TAKE_PROFIT = auto()  # COINED — take-profit trigger order
    TWAP = auto()  # COINED — TWAP (cf. CommandEvent.action "twap", kinds.py:51)


# The 11 §6.1 order-pipeline lifecycle states (Strategy.md §6.1 L561-570) MINUS
# LOCKED/IDLE — those are ST-04 LevelState.lifecycle members (level_state.py L48-49;
# the §6.1 "Protection-locked levels" sentence's subject is *levels*; single-owner
# rule STATE_OWNERSHIP.md L87). No AWAITING_ARM/ARMED here (arm status is ST-12's).
_ORDER_LIFECYCLES = frozenset(
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
    }
)

# Legal §6.1 order-pipeline edges (Strategy.md §6.1 diagram L561-565). Branch points
# read from the diagram's arrow layout; each edge cited. Reversals and stage-skips
# are absent by construction, so ``is_legal_order_transition`` rejects them.
_LEGAL_ORDER_EDGES = frozenset(
    {
        # linear chain (L561-562)
        ("INTENT_CREATED", "ORDER_SUBMITTED"),
        ("ORDER_SUBMITTED", "ORDER_ACKNOWLEDGED"),
        ("ORDER_ACKNOWLEDGED", "ORDER_ACTIVE"),
        ("ORDER_ACTIVE", "PARTIALLY_FILLED"),
        ("PARTIALLY_FILLED", "FILLED"),
        ("FILLED", "POSITION_VERIFIED"),
        # cancellation branch (L563 "↘ CANCELLED") — a resting/working order
        ("ORDER_ACKNOWLEDGED", "CANCELLED"),
        ("ORDER_ACTIVE", "CANCELLED"),
        ("PARTIALLY_FILLED", "CANCELLED"),
        # emergency: trigger-without-fill (L564) — from a resting/active order
        ("ORDER_ACTIVE", "EMERGENCY"),
        # skipped: tolerance/economics fail (L564) — post-emergency skip
        ("EMERGENCY", "SKIPPED"),
        # error: unrecoverable exchange error (L565) — from submission/active states
        ("ORDER_SUBMITTED", "ERROR"),
        ("ORDER_ACKNOWLEDGED", "ERROR"),
        ("ORDER_ACTIVE", "ERROR"),
    }
)


@dataclass(frozen=True, slots=True)
class OrderIntent:
    """ST-05 intent half (B1): a Core decision to place one order (CAP-0014)."""

    cloid: str  # own order identity (opaque, non-empty); STR-0298, §6.2 cloid
    target_generation_id: int  # §3 identity (cf. IntentEvent)
    target_cycle_id: int  # §3 identity
    target_level_id: int  # §3 identity
    target_direction: str  # "BU"/"SL" VERBATIM (IntentEvent.target_direction, §3)
    order_type: OrderType  # COINED inlet vocabulary (this module)
    requested_size: Decimal  # exact, > 0 (cf. IntentEvent; no rounding this phase)
    requested_price: Decimal  # exact, > 0 (cf. IntentEvent)
    intent_tag: IntentTag  # from classify_intent (B2); reused hedge_state.IntentTag
    acute: bool  # cf. IntentEvent.acute (STR-0356/0357); carried, no 7h-2 branching

    def __post_init__(self) -> None:
        if not isinstance(self.cloid, str) or not self.cloid:
            raise ValueError("cloid must be a non-empty str")
        for name in ("target_generation_id", "target_cycle_id", "target_level_id"):
            value = getattr(self, name)
            if type(value) is not int:  # reject bool (int subclass) and non-ints
                raise ValueError(f"{name} must be an int")
        if self.target_direction not in _GROUPS:
            raise ValueError(
                f"target_direction must be BU or SL: {self.target_direction!r}"
            )
        if not isinstance(self.order_type, OrderType):
            raise ValueError("order_type must be an OrderType")
        if not isinstance(self.requested_size, Decimal):
            raise ValueError("requested_size must be a Decimal instance")
        if self.requested_size <= 0:
            raise ValueError("requested_size must be > 0")
        if not isinstance(self.requested_price, Decimal):
            raise ValueError("requested_price must be a Decimal instance")
        if self.requested_price <= 0:
            raise ValueError("requested_price must be > 0")
        if not isinstance(self.intent_tag, IntentTag):
            raise ValueError("intent_tag must be an IntentTag")
        if type(self.acute) is not bool:
            raise ValueError("acute must be a bool")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "cloid": self.cloid,
            "target_generation_id": self.target_generation_id,
            "target_cycle_id": self.target_cycle_id,
            "target_level_id": self.target_level_id,
            "target_direction": self.target_direction,
            "order_type": self.order_type.value,
            "requested_size": self.requested_size,
            "requested_price": self.requested_price,
            "intent_tag": self.intent_tag.value,
            "acute": self.acute,
        }


def construct_order_intent(
    *,
    cloid: str,
    target_generation_id: int,
    target_cycle_id: int,
    target_level_id: int,
    target_direction: str,
    order_type: OrderType,
    requested_size: Decimal,
    requested_price: Decimal,
    intent_tag: IntentTag,
    acute: bool,
) -> OrderIntent:
    """The B1 inlet (CAP-0014): validate + build an ``OrderIntent`` (no rounding).

    Malformed input → ``ValueError`` (via ``OrderIntent.__post_init__``); no row is
    created. There is no inlet→SKIPPED path (SKIPPED = §6.1 tolerance/economics fail).
    """
    return OrderIntent(
        cloid=cloid,
        target_generation_id=target_generation_id,
        target_cycle_id=target_cycle_id,
        target_level_id=target_level_id,
        target_direction=target_direction,
        order_type=order_type,
        requested_size=requested_size,
        requested_price=requested_price,
        intent_tag=intent_tag,
        acute=acute,
    )


def classify_intent(
    exposure_before: Decimal,
    exposure_after: Decimal,
    reduce_only: bool,
) -> IntentTag:
    """§13.3 classification by projected ExposureDelta (B2; STR-0240/0241/0242).

    Classified by projected delta, NOT by ``reduce_only`` (accepted and IGNORED —
    an opposite-direction hedge is a correction even with ``reduce_only=False``,
    STR-0241). ``|after| < |before|`` → EXPOSURE_CORRECTION_INTENT; otherwise
    (``|after| >= |before|``, incl. flat→position and the equality tie) →
    ENTRY_INTENT (the tie breaks toward ENTRY, fail-closed).
    """
    _ = reduce_only  # STR-0241: deliberately ignored (classification is delta-based)
    if abs(exposure_after) < abs(exposure_before):
        return IntentTag.EXPOSURE_CORRECTION_INTENT
    return IntentTag.ENTRY_INTENT


def is_legal_order_transition(from_state: str, to_state: str) -> bool:
    """Pure §6.1 edge legality over the 11 order-pipeline states (B4).

    Unknown states → ``ValueError`` (fail-closed on garbage). Known pairs → whether
    the edge is in the §6.1 table; reversals and stage-skips are not, so they
    return ``False``.
    """
    if from_state not in _ORDER_LIFECYCLES:
        raise ValueError(f"unknown order state: {from_state!r}")
    if to_state not in _ORDER_LIFECYCLES:
        raise ValueError(f"unknown order state: {to_state!r}")
    return (from_state, to_state) in _LEGAL_ORDER_EDGES


@dataclass(frozen=True, slots=True)
class OrderState:
    """ST-05 row: the intent half (``OrderIntent``) + the §6.1 outcome ``lifecycle``.

    Standalone (A2): no ST-04 coupling this phase. ``lifecycle`` is one of the 11
    §6.1 order-pipeline states; ``INTENT_CREATED`` is the B1 entry.
    """

    intent: OrderIntent  # ST-05 intent half (B1)
    lifecycle: str  # ST-05 outcome half: one of the 11 §6.1 order-pipeline states

    def __post_init__(self) -> None:
        if not isinstance(self.intent, OrderIntent):
            raise ValueError("intent must be an OrderIntent")
        if self.lifecycle not in _ORDER_LIFECYCLES:
            raise ValueError(f"invalid order lifecycle: {self.lifecycle!r}")

    @property
    def cloid(self) -> str:
        return self.intent.cloid

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "intent": self.intent.to_canonical_obj(),
            "lifecycle": self.lifecycle,
        }


__all__ = [
    "OrderIntent",
    "OrderState",
    "OrderType",
    "classify_intent",
    "construct_order_intent",
    "is_legal_order_transition",
]
