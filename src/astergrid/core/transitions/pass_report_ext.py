"""P6 sub-decision record for the PassReport extension (Phase 7h-4b-2, B5).

A LEAF module: stdlib only (``dataclasses``, ``re``). It MUST NOT import
``core.state``/``core.pass_engine``. ``SubDecisionRecord`` is one traced P6
sub-decision; ``PassReport.sub_decisions`` carries a tuple of them (default ``()``).

Vocabulary (all COINED, anchored per field/kind): the five ``sub_kind`` values name
P6's sub-steps; the kind-compat matrix pins each kind's legal ``outcome`` set. Ordering
uses ``STAGE_ORDER`` (P0..P6); P6 sorts records by (stage_order, sub_kind, subject).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

STAGE_ORDER: dict[str, int] = {f"P{i}": i for i in range(7)}  # P0..P6

# Sub-kind vocabulary (COINED). Order-kinds carry a cloid subject; ladder-kinds carry
# a G..-C..-{BU|SL} subject.
_ORDER_KINDS = frozenset({"CANCEL_SELECT", "ARMING_EVAL", "SUBMISSION_EMIT"})
_LADDER_KINDS = frozenset({"LADDER_ISSUANCE_BU", "LADDER_ISSUANCE_SL"})
_SUB_KINDS = _ORDER_KINDS | _LADDER_KINDS

# Kind-compat matrix (COINED, each kind anchored to its Strategy step):
#   CANCEL_SELECT   -> {EMITTED}          (STR-0075 step-2 cancel)
#   ARMING_EVAL     -> {ARMED,BLOCKED,WAITING} (§8 arm gates, STR-0173..0181)
#   SUBMISSION_EMIT -> {EMITTED}          (STR-0182 submission)
#   LADDER_ISSUANCE_BU/SL -> {ISSUED,EMPTY} (STR-0080 both-groups issuance)
_OUTCOMES_BY_KIND: dict[str, frozenset[str]] = {
    "CANCEL_SELECT": frozenset({"EMITTED"}),
    "ARMING_EVAL": frozenset({"ARMED", "BLOCKED", "WAITING"}),
    "SUBMISSION_EMIT": frozenset({"EMITTED"}),
    "LADDER_ISSUANCE_BU": frozenset({"ISSUED", "EMPTY"}),
    "LADDER_ISSUANCE_SL": frozenset({"ISSUED", "EMPTY"}),
}

# Ladder subject shape: G{gg:02d}-C{cc:02d}-{BU|SL}.
_LADDER_SUBJECT = re.compile(r"^G\d{2}-C\d{2}-(BU|SL)$")


@dataclass(frozen=True, slots=True)
class SubDecisionRecord:
    """One traced P6 sub-decision (data; six canonical keys)."""

    stage: str  # in {"P0".."P6"} (this phase always "P6")
    sub_kind: str  # one of the five sub-kinds
    subject: str  # cloid (order-kinds) or G..-C..-{BU|SL} (ladder-kinds)
    outcome: str  # per the kind-compat matrix
    reason_codes: tuple[str, ...] = ()  # non-empty plain-string code values
    notes: str = ""  # deterministic (no clock/random/repr)

    def __post_init__(self) -> None:
        if self.stage not in STAGE_ORDER:
            raise ValueError(f"invalid stage: {self.stage!r}")
        if self.sub_kind not in _SUB_KINDS:
            raise ValueError(f"invalid sub_kind: {self.sub_kind!r}")
        if self.outcome not in _OUTCOMES_BY_KIND[self.sub_kind]:
            raise ValueError(
                f"outcome {self.outcome!r} invalid for sub_kind {self.sub_kind!r}"
            )
        if self.sub_kind in _LADDER_KINDS:
            if _LADDER_SUBJECT.match(self.subject) is None:
                raise ValueError(f"bad ladder subject: {self.subject!r}")
        elif not isinstance(self.subject, str) or not self.subject:
            raise ValueError("order-kind subject (cloid) must be a non-empty str")
        for code in self.reason_codes:
            if not isinstance(code, str) or not code:
                raise ValueError("reason_codes must be non-empty strings")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "sub_kind": self.sub_kind,
            "subject": self.subject,
            "outcome": self.outcome,
            "reason_codes": list(self.reason_codes),
            "notes": self.notes,
        }


__all__ = ["STAGE_ORDER", "SubDecisionRecord"]
