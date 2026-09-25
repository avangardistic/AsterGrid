"""ST-19 market observation cache — Phase 7g-3b minimal typing (own leaf).

A LEAF module: imports ONLY the stdlib. ST-19 is P0-domain market data (NOT
exposure), so it lives in its own leaf — co-locating it with the exposure/hedge
leaves would be wrong-domain.

Phase 7g-3b types ST-19 with EXACTLY one field: ``mark_price`` (M), the Fix-1
``q_min`` divisor — the only market observable the 7g-3b rule needs. Typed-but-
UNPOPULATED in 7g-3b (P0 is a stub; nothing writes ST-19 this phase — P1 takes
``mark_price`` as a marker). The 7h P0 writer populates ST-19 and a 7h projection
maps it to the P1 marker; oracle/mid/L2/funding/fee/meta join this row when their
reader lands (7h+).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MarketObservationState:
    """ST-19 (Phase 7g-3b): the mark price M (the Fix-1 q_min divisor)."""

    mark_price: Decimal  # M, > 0, Decimal instance

    def __post_init__(self) -> None:
        if not isinstance(self.mark_price, Decimal):
            raise ValueError("mark_price must be a Decimal instance")
        if self.mark_price <= 0:
            raise ValueError("mark_price must be > 0")

    def to_canonical_obj(self) -> dict[str, object]:
        return {"mark_price": self.mark_price}
