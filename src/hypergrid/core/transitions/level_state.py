"""ST-04 Level pipeline state — Phase 7g-1 minimal typing (§7.1/§7.2).

A LEAF module: imports ONLY the stdlib. It MUST NOT import ``core.state`` or
``core.pass_engine``.

Phase 7g-1 types ST-04 with ONLY the fields the geometry (§7.1) and
protection-lock (§7.2) logic reads or writes: the identity quadruple, the ladder
``target_price``, and the ``is_protection_locked`` gate. Everything else is
DEFERRED (typed when the rule that uses it lands), to avoid the C2-7e error of
over-strict invariants on fields no code populates yet:

  * ``size_notional_usd`` — TYPED in Phase 7g-2 (this field), defaulted None;
    populated by the 7h arming caller. Its §7.3 sizing + hard caps live in
    ``transitions/sizing.py``.
  * lifecycle (one of the 13 §6.1 strings) — LANDED Phase 7h-1 (this field),
    observed by the real P0 (recorded, never derived). The 7g-1 forward note's
    single-source coherence rule is now enforced here as R10c:
    ``is_protection_locked ⇔ lifecycle == "LOCKED"`` (checked when observed).
  * ``filled_quantity`` (VERIFIED cumulative) — LANDED Phase 7h-1 (this field).
  * ``order_state``: SUPERSEDED. Order lifecycle is ST-05 (``order_state.py``
    ``OrderState``, Phase 7h-2 — the §6.1 pipeline minus LOCKED/IDLE); arm status is
    ST-12 (``arm_state.py``, Phase 7h-2). No AWAITING_ARM/ARMED lives on ST-04. The
    ST-04↔ST-05 coupling rule is the P6-writer phase's (7h-4).
  * order linkage (cloid, oid) — Phase 7h.

Frozen, slots, self-validating, canonical-serializable (Decimals kept as Decimals;
the canonical-JSON layer tags them at dumps time).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_GROUPS = frozenset({"BU", "SL"})  # §7.1 traversal groups
# The 13 §6.1 pipeline lifecycle strings (verbatim from Strategy.md §6.1 L561-567).
# ST-04's observed lifecycle (Phase 7h-1) is validated against this set.
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


@dataclass(frozen=True, slots=True)
class LevelState:
    """ST-04 (Phase 7g-1): ladder identity + target price + §7.2 lock gate."""

    generation_id: int  # 0..99
    cycle_id: int  # 0..99
    direction: str  # "BU" or "SL"
    level_id: int  # 1..12 (max representable ladder; config bound GridLevels)
    target_price: Decimal  # > 0, Decimal instance (§7.1 ladder price)
    is_protection_locked: bool  # §7.2 LOCKED state
    # §7.3 per-level USD notional (Phase 7g-2): typed here, populated by the 7h
    # arming caller. Appended LAST so 7g-1 positional construction keeps working.
    size_notional_usd: Decimal | None = None
    # §11.4/STR-0199 VERIFIED cumulative filled quantity (Phase 7h-1): a magnitude
    # (>= 0), NOT requested_qty; the observing P0 carries the cumulative value (no
    # in-model accumulation). Appended LAST (7g-2 positional-compat precedent).
    filled_quantity: Decimal | None = None
    # §6.1 pipeline lifecycle (Phase 7h-1): one of the 13 §6.1 strings, observed by
    # P0 (Strategy defines no transition function — it is RECORDED, never derived).
    lifecycle: str | None = None

    def __post_init__(self) -> None:
        if not (0 <= self.generation_id <= 99):
            raise ValueError("generation_id must be within 0..99")
        if not (0 <= self.cycle_id <= 99):
            raise ValueError("cycle_id must be within 0..99")
        if self.direction not in _GROUPS:
            raise ValueError(f"direction must be BU or SL: {self.direction!r}")
        if not (1 <= self.level_id <= 12):
            raise ValueError("level_id must be within 1..12")
        if not isinstance(self.target_price, Decimal):
            raise ValueError("target_price must be a Decimal instance")
        if self.target_price <= 0:
            raise ValueError("target_price must be > 0")
        if self.size_notional_usd is not None:
            if not isinstance(self.size_notional_usd, Decimal):
                raise ValueError("size_notional_usd must be a Decimal instance")
            if self.size_notional_usd <= 0:
                raise ValueError("size_notional_usd must be > 0")
        if self.filled_quantity is not None:
            if not isinstance(self.filled_quantity, Decimal):
                raise ValueError("filled_quantity must be a Decimal instance")
            if self.filled_quantity < 0:
                raise ValueError("filled_quantity must be >= 0 (magnitude)")
        if self.lifecycle is not None:
            if self.lifecycle not in _LIFECYCLES:
                raise ValueError(f"invalid lifecycle: {self.lifecycle!r}")
            # R10c LOCK COHERENCE (the 7g-1 forward note): the §7.2 gate and the §6.1
            # LOCKED pipeline position are one truth, no drift. Only checked once the
            # lifecycle is observed (non-None); pre-observation skips it.
            if self.is_protection_locked != (self.lifecycle == "LOCKED"):
                raise ValueError(
                    "lock coherence: is_protection_locked must equal "
                    '(lifecycle == "LOCKED")'
                )

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "generation_id": self.generation_id,
            "cycle_id": self.cycle_id,
            "direction": self.direction,
            "level_id": self.level_id,
            "target_price": self.target_price,  # stays Decimal; tagged at dumps
            "is_protection_locked": self.is_protection_locked,
        }
        if self.size_notional_usd is not None:  # R-JSON-6: omit absent optional
            obj["size_notional_usd"] = self.size_notional_usd
        if self.filled_quantity is not None:  # R-JSON-6
            obj["filled_quantity"] = self.filled_quantity
        if self.lifecycle is not None:  # R-JSON-6
            obj["lifecycle"] = self.lifecycle
        return obj
