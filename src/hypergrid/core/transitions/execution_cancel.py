"""§5.2 step-2 cancel selector (Phase 7h-3): pick the resting orders to cancel. Pure.

A transition module: stdlib + ``order_state.OrderState`` (read-only). It MUST NOT
import ``core.state``/``core.pass_engine``/``cycle`` (P5 markers are marker-gated by
the 7f design; 7h-3 neither duplicates nor touches them — A2/P5).

``select_exhausted_candidates`` implements the §5.2 step-2 SELECTOR: given the order
rows of an exhausted (gen, cycle, direction) traversal, pick the RESTING set — orders
that still hold live venue quantity — and emit a cancel candidate per row. The
``→CANCELLED`` transitions themselves are venue-ack-triggered (post-7h); the runtime/
7h-4 threads the output into P5's S2 marker.

PINNED purposive reading of §5.2 L362-363 ("Cancel all pending (not
POSITION_VERIFIED) orders"): the RESTING set, proved per excluded state — a venue
cancel is void-or-reject for each excluded state, and sending known-void cancels
violates the §6.3 reject-philosophy; safety holds because provably nothing rests
(INTENT_CREATED never sent; FILLED authoritative-done; CANCELLED/SKIPPED/ERROR/
POSITION_VERIFIED terminal). ``reason_codes.py`` is FROZEN (15 members) with no
reusable cancel code, so the code is a module-local coined enum.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto

from hypergrid.core.transitions.order_state import OrderState

# The RESTING set: order lifecycles that still hold live venue quantity (§5.2 L362-363
# resting-set reading). A cancel is meaningful only for these.
_RESTING = frozenset(
    {
        "ORDER_SUBMITTED",
        "ORDER_ACKNOWLEDGED",
        "ORDER_ACTIVE",
        "PARTIALLY_FILLED",
        "EMERGENCY",
    }
)


class _NameValueStrEnum(StrEnum):
    """StrEnum base whose ``auto()`` value equals the member name (no drift)."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name


class CancelReasonCode(_NameValueStrEnum):
    """§5.2 step-2 cancel reason. Module-local (reason_codes.py is frozen)."""

    EXHAUSTED_TRAVERSAL_CANCEL = auto()  # COINED ← §5.2 L362-363 exhausted-traversal


@dataclass(frozen=True, slots=True)
class CancelCandidate:
    """One order selected for cancellation by the §5.2 step-2 selector."""

    cloid: str
    reason_code: CancelReasonCode

    def to_canonical_obj(self) -> dict[str, object]:
        return {"cloid": self.cloid, "reason_code": self.reason_code.value}


def select_exhausted_candidates(
    order_rows: tuple[OrderState, ...],
    gen_id: int,
    cycle_id: int,
    direction: str,
) -> tuple[CancelCandidate, ...]:
    """Select the resting orders of an exhausted (gen, cycle, direction) traversal.

    Filters by traversal identity AND the resting-set lifecycle; emits one candidate
    per selected row, sorted by cloid (canonical, input-order-proof); empty → empty.
    """
    selected = [
        row
        for row in order_rows
        if row.intent.target_generation_id == gen_id
        and row.intent.target_cycle_id == cycle_id
        and row.intent.target_direction == direction
        and row.lifecycle in _RESTING
    ]
    selected.sort(key=lambda row: row.cloid)
    return tuple(
        CancelCandidate(
            cloid=row.cloid,
            reason_code=CancelReasonCode.EXHAUSTED_TRAVERSAL_CANCEL,
        )
        for row in selected
    )


__all__ = [
    "CancelCandidate",
    "CancelReasonCode",
    "select_exhausted_candidates",
]
