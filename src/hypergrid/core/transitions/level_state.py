"""ST-04 Level pipeline state — Phase 7g-1 minimal typing (§7.1/§7.2).

A LEAF module: imports ONLY the stdlib. It MUST NOT import ``core.state`` or
``core.pass_engine``.

Phase 7g-1 types ST-04 with ONLY the fields the geometry (§7.1) and
protection-lock (§7.2) logic reads or writes: the identity quadruple, the ladder
``target_price``, and the ``is_protection_locked`` gate. Everything else is
DEFERRED (typed when the rule that uses it lands), to avoid the C2-7e error of
over-strict invariants on fields no code populates yet:

  * ``size_notional_usd`` — Phase 7g-2, WITH the §7.3 sizing + hard caps (splitting
    volume computation from cap-enforcement would create two sizing truths).
  * lifecycle (§6.1 PARTIALLY_FILLED/FILLED/POSITION_VERIFIED/CANCELLED/EMERGENCY/
    SKIPPED/ERROR, LOCKED->IDLE) — Phase 7h (real P0/P6). FORWARD NOTE: when the
    §6.1 lifecycle arrives, 7h MUST define the single-source coherence rule between
    the §7.2 ``is_protection_locked`` gate and the §6.1 LOCKED pipeline position
    (no drift).
  * ``filled_quantity`` (verified) — Phase 7h.
  * ``order_state`` (IDLE/AWAITING_ARM/ARMED/...) — Phase 7h.
  * order linkage (cloid, oid) — Phase 7h.

Frozen, slots, self-validating, canonical-serializable (Decimals kept as Decimals;
the canonical-JSON layer tags them at dumps time).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_GROUPS = frozenset({"BU", "SL"})  # §7.1 traversal groups


@dataclass(frozen=True, slots=True)
class LevelState:
    """ST-04 (Phase 7g-1): ladder identity + target price + §7.2 lock gate."""

    generation_id: int  # 0..99
    cycle_id: int  # 0..99
    direction: str  # "BU" or "SL"
    level_id: int  # 1..12 (max representable ladder; config bound GridLevels)
    target_price: Decimal  # > 0, Decimal instance (§7.1 ladder price)
    is_protection_locked: bool  # §7.2 LOCKED state

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

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "generation_id": self.generation_id,
            "cycle_id": self.cycle_id,
            "direction": self.direction,
            "level_id": self.level_id,
            "target_price": self.target_price,  # stays Decimal; tagged at dumps
            "is_protection_locked": self.is_protection_locked,
        }
