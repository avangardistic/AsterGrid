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

from hypergrid.core.events import CommandEvent
from hypergrid.core.transitions.order_state import OrderState

_TIF = frozenset({"Gtc", "Ioc", "Alo"})  # §6.2 TIF set

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


def emit_cancel_command(
    *,
    cloid: str,
    tif: str = "Gtc",
    expires_after: int,
    intent_log_seq: int,
) -> CommandEvent:
    """Build a cancel ``CommandEvent`` (pure; Phase 7h-4b-2 B2.2).

    ``action="cancel"`` is a frozen-vocab literal (kinds.py L51). ``tif="Gtc"`` default
    is COINED (Item 3: schema requires a non-optional str; no Strategy sentence ties a
    cancel to a TIF). ``expires_after`` is REQUIRED and ``> 0`` — a cancel IS an action
    (DECISION-008 "use expiresAfter on actions"); the schema's None default is
    permissiveness, not permission. Fail-closed (``ValueError``): empty cloid,
    ``tif ∉ {Gtc,Ioc,Alo}``, ``expires_after <= 0``, ``intent_log_seq < 0``.
    Cite: §6.2 (TIF set); STR-0075 (step 2); DECISION-008.
    """
    if not isinstance(cloid, str) or not cloid:
        raise ValueError("cloid must be a non-empty str")
    if tif not in _TIF:
        raise ValueError(f"tif must be one of {sorted(_TIF)}: {tif!r}")
    if type(expires_after) is not int or expires_after <= 0:
        raise ValueError("expires_after must be a positive int (DECISION-008)")
    if type(intent_log_seq) is not int or intent_log_seq < 0:
        raise ValueError("intent_log_seq must be an int >= 0")
    return CommandEvent(
        cloid=cloid,
        action="cancel",  # frozen vocab literal (kinds.py L51)
        tif=tif,
        expires_after=expires_after,
        causal_predecessors=(intent_log_seq,),
    )


__all__ = [
    "CancelCandidate",
    "CancelReasonCode",
    "emit_cancel_command",
    "select_exhausted_candidates",
]
