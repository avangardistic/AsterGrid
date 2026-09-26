"""§9 order submission mechanics (Phase 7h-3): build CommandEvent + append + advance.

A transition module: builds a frozen ``CommandEvent`` (``events/kinds.py``), appends
it via the injected ``EventLogPort`` (``event_log/port.py``), returns a receipt, and
advances the ST-05 row ``INTENT_CREATED → ORDER_SUBMITTED`` (the 7h-2-deferred trigger
edge). NO venue call, NO ST-18 write, NO ``TimerEvent`` (A2 seams).

Row-first ordering (DECISION-008 Option B): the ST-05 row provably exists before the
append, so "persist intent+cloid BEFORE any side effect" holds. The double-submit
guard is LOCAL (never venue-dedup reliance): a non-``INTENT_CREATED`` row is rejected,
so an advanced row can never re-enter B1.

Imports ``core.events`` (frozen ``CommandEvent``) at runtime and the log/envelope
types for annotation only. It MUST NOT import ``core.state`` or ``core.pass_engine``.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from hypergrid.core.events import CommandEvent
from hypergrid.core.transitions.order_state import (
    OrderState,
    OrderType,
    is_legal_order_transition,
)

if TYPE_CHECKING:
    from hypergrid.core.event_log import EventLogPort
    from hypergrid.core.events import ObservedMeta

# §6.2 VERBATIM TIF set (Gtc/Ioc/Alo).
_TIF = frozenset({"Gtc", "Ioc", "Alo"})

# B1.MAP — OrderType → CommandEvent.action. PINNED: the frozen action vocab
# {submit, cancel, modify, twap} forces it. COINED refinement: "action = what the
# exchange is asked to do; order type is a parameter of that request" (trigger/TIF/
# price params are post-7h venue concerns; type info joins via cloid → ST-05).
_ACTION_BY_ORDER_TYPE: dict[OrderType, str] = {
    OrderType.LIMIT: "submit",  # PINNED ← frozen action vocab
    OrderType.MARKET: "submit",  # PINNED
    OrderType.STOP: "submit",  # PINNED
    OrderType.TAKE_PROFIT: "submit",  # PINNED
    OrderType.TWAP: "twap",  # PINNED ← CommandEvent.action "twap"
}


@dataclasses.dataclass(frozen=True, slots=True)
class SubmissionResult:
    """B1 receipt: the append outcome, reconstructable from the log (inv.19)."""

    cloid: str  # order identity (opaque); == order.intent.cloid
    command_sequence: int  # env.log_sequence (R-SEQ-1; first is 0)
    content_hash: str  # env.content_hash (sha256 chain link)
    submitted_at_ts: str  # observed.local_receive_ts (ISO-8601-Z micros)

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "cloid": self.cloid,
            "command_sequence": self.command_sequence,
            "content_hash": self.content_hash,
            "submitted_at_ts": self.submitted_at_ts,
        }


def emit_submission_command(
    *,
    order: OrderState,
    tif: str,
    expires_after: int,
    intent_log_seq: int,
) -> CommandEvent:
    """Build the submission ``CommandEvent`` (pure; Phase 7h-4b-2 B2.1).

    Holds the four submit_order validations (messages VERBATIM-identical — 7h-3 tests
    match on them) + the ``CommandEvent`` construction. No append, no advance. P6 uses
    this to emit without a log port; ``submit_order`` calls it then appends.
    Fail-closed (``ValueError``): non-``INTENT_CREATED`` row, ``tif ∉ {Gtc,Ioc,Alo}``,
    ``expires_after <= 0`` (DECISION-008), ``intent_log_seq < 0``. Cite: STR-0298; §6.2.
    """
    if order.lifecycle != "INTENT_CREATED":
        raise ValueError(
            "submit_order requires an INTENT_CREATED row (double-submit guard)"
        )
    if tif not in _TIF:
        raise ValueError(f"tif must be one of {sorted(_TIF)}: {tif!r}")
    if type(expires_after) is not int or expires_after <= 0:
        raise ValueError("expires_after must be a positive int (DECISION-008)")
    if type(intent_log_seq) is not int or intent_log_seq < 0:
        raise ValueError("intent_log_seq must be an int >= 0")
    return CommandEvent(
        cloid=order.intent.cloid,
        action=_ACTION_BY_ORDER_TYPE[order.intent.order_type],
        tif=tif,
        expires_after=expires_after,
        causal_predecessors=(intent_log_seq,),
    )


def submit_order(
    *,
    order: OrderState,
    tif: str,
    expires_after: int,
    intent_log_seq: int,
    port: EventLogPort,
    observed: ObservedMeta,
) -> tuple[SubmissionResult, OrderState]:
    """Submit one order: build+append a CommandEvent, receipt, advance the ST-05 row.

    Fail-closed (``ValueError``): non-``INTENT_CREATED`` row (double-submit guard),
    ``tif ∉ {Gtc,Ioc,Alo}``, ``expires_after <= 0`` (DECISION-008; units opaque),
    ``intent_log_seq < 0``. Appends EXACTLY once. Returns (receipt, advanced row).
    """
    cmd = emit_submission_command(
        order=order,
        tif=tif,
        expires_after=expires_after,
        intent_log_seq=intent_log_seq,
    )
    env = port.append(cmd, observed)
    receipt = SubmissionResult(
        cloid=order.intent.cloid,
        command_sequence=env.log_sequence,
        content_hash=env.content_hash,
        submitted_at_ts=observed.local_receive_ts,
    )
    # Trigger wire: honor the ST-05 table (raises if it ever drifts), then advance.
    if not is_legal_order_transition("INTENT_CREATED", "ORDER_SUBMITTED"):
        raise ValueError("order table drift: INTENT_CREATED→ORDER_SUBMITTED not legal")
    advanced = dataclasses.replace(order, lifecycle="ORDER_SUBMITTED")
    return receipt, advanced


__all__ = ["SubmissionResult", "emit_submission_command", "submit_order"]
