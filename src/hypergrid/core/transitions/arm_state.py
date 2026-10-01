"""§8 arm vocabulary + ST-12 arm-request machine (Phase 7h-2).

A LEAF module: imports ONLY the stdlib (``dataclasses``, ``decimal`` is unused here,
``enum``, ``re``). It MUST NOT import ``core.state``, ``core.pass_engine``, or
``arm`` (``arm`` imports THIS leaf — one-way, no cycle).

Contents:
  * Shared §8 enums — ``ArmPolicy`` (D-10 VERBATIM), ``ArmOutcome`` (WAITING coined),
    ``OperatorDecision`` (coined), ``OperationalState`` (§13.2 9-member VERBATIM),
    ``ArmBlockCode`` (16 members, each cited/coined).
  * ``ArmRequestState`` — the ST-12 row/record (CAP-0019): request identity
    ``(cloid, request_seq)`` + one of the 5 machine states + inv.4 timestamp/identity
    + the block cause when BLOCKED. Timestamps are ISO-8601-Z microsecond strings,
    validated by a module-local helper (mirrors the frozen codec's ``_req_ts``
    semantics — ``events/codec.py:82`` — without importing the private helper and
    without ``datetime``).
  * ``is_legal_arm_transition`` + ``supersede_request`` + ``expire_on_restart`` — the
    §8/ST-12 machine (B4): the 5-state graph, the re-request/policy-swap supersede
    rule (BLOCKED + ARM_SUPERSEDED, L731), and the fail-closed restart rule
    (pending → BLOCKED + ARM_TIMEOUT).

Frozen, slots, self-validating; ``to_canonical_obj`` keeps enums as their string
value and preserves the exact timestamp string.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import StrEnum, auto

# R-JSON-5: ISO-8601 UTC, 'Z' suffix, exactly six fractional digits (mirrors the
# frozen codec's timestamp contract; module-local so no frozen/private import).
_ISO_UTC_MICROS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")


def _validate_iso_ts(value: str) -> None:
    """Require an ISO-8601-Z microsecond timestamp string (inv.4; no ``datetime``)."""
    if not isinstance(value, str) or _ISO_UTC_MICROS.match(value) is None:
        raise ValueError("timestamp must be an ISO-8601-Z microsecond string")


class _NameValueStrEnum(StrEnum):
    """StrEnum base whose ``auto()`` value equals the member name (no drift)."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name


class ArmPolicy(_NameValueStrEnum):
    """§14 D-10 arm policy. VERBATIM (Strategy.md §8 L710)."""

    AUTO = auto()  # VERBATIM §8 L711 (D-10)
    SEMI = auto()  # VERBATIM §8 L713 (D-10)
    WEBHOOK = auto()  # VERBATIM §8 L716 (D-10)


class ArmOutcome(_NameValueStrEnum):
    """The arm-evaluation outcome."""

    ARMED = auto()  # VERBATIM §8 (a Level arms)
    BLOCKED = auto()  # VERBATIM §8 L757 ("Level stays IDLE/PRECHECK, logged")
    WAITING = (
        auto()
    )  # COINED — SEMI/WEBHOOK approval pending (mirrors AWAITING_APPROVAL)


class OperatorDecision(_NameValueStrEnum):
    """The §8 operator/service approval verdict input. COINED names."""

    APPROVE = auto()  # COINED — §8 "explicit operator approval" (L714)
    DENY = auto()  # COINED — STR-0165 "operator deny → BLOCKED"


class OperationalState(_NameValueStrEnum):
    """§13.2 Basket operational state. 9 members VERBATIM (Strategy.md §13.2)."""

    INITIALIZING = auto()  # VERBATIM §13.2 L1002
    ACTIVE = auto()  # VERBATIM §13.2 L1001
    FREEZE_REQUESTED = auto()  # VERBATIM §13.2 L1001
    FREEZING = auto()  # VERBATIM §13.2 L1001
    FROZEN = auto()  # VERBATIM §13.2 L1001
    RESTARTING = auto()  # VERBATIM §13.2 L1002
    ERROR = auto()  # VERBATIM §13.2 L1004
    RECOVERY = auto()  # VERBATIM §13.2 L1004
    CLOSED = auto()  # VERBATIM §13.2 L1004


class ArmBlockCode(_NameValueStrEnum):
    """The distinct cause code for a BLOCKED arm outcome (§15 inv.19).

    The 10 gate codes are COINED-but-anchored to each §8 gate sentence (L737-754);
    the workflow codes cite their Strategy line.
    """

    GATE_1_DEPTH = auto()  # COINED ← §8 gate 1 (L737-738)
    GATE_2_DISTANCE = auto()  # COINED ← §8 gate 2 (L739-741)
    GATE_3_SIZE = auto()  # COINED ← §8 gate 3 (L742)
    GATE_4_MARGIN = auto()  # COINED ← §8 gate 4 (L743-744)
    GATE_5_EXPOSURE_CAPS = auto()  # COINED ← §8 gate 5 (L745)
    GATE_6_OPEN_ORDER_COUNT = auto()  # COINED ← §8 gate 6 (L746-749)
    GATE_7_PRICE_NORMALIZED = auto()  # COINED ← §8 gate 7 (L750)
    GATE_8_SIZE_NORMALIZED = auto()  # COINED ← §8 gate 8 (L750)
    GATE_9_MARKET_STATE = auto()  # COINED ← §8 gate 9 (L751)
    GATE_10_EDGE = auto()  # COINED ← §8 gate 10 (L752-754)
    DISABLED_GENERATION_BLOCKS_ENTRY = auto()  # ← STR-0180 (§8 L758-759)
    POLICY_ABSENT = auto()  # ← inv.5 "UNSET keeps all arming BLOCKED" (§8 L734)
    ARM_TIMEOUT = auto()  # ← §8 L726 ArmRequestTimeoutSeconds elapsed / restart expiry
    ARM_DENIED = auto()  # ← STR-0165 "operator deny → BLOCKED"
    ARM_SUPERSEDED = auto()  # ← §8 L731 "a new arm request MAY supersede"
    ARM_WEBHOOK_ERROR = (
        auto()
    )  # ← STR-0166 webhook timeout/error converge (cause split)


# The 5 ST-12 machine states. IDLE/PRECHECK/ARMED/BLOCKED are §8 vocabulary
# (L713/L757); AWAITING_APPROVAL is COINED-but-consistent — it separates "evaluating
# gates" (PRECHECK) from "waiting human/service" (the only scope of timeout/expiry;
# cf. ST-12 "pending requests", STATE_OWNERSHIP.md L48-49).
_ARM_STATUSES = frozenset({"IDLE", "PRECHECK", "AWAITING_APPROVAL", "ARMED", "BLOCKED"})
_PENDING_STATUSES = frozenset({"PRECHECK", "AWAITING_APPROVAL"})

# Legal ST-12 edges (B4). ARMED is terminal per request (no outgoing edge).
_LEGAL_ARM_EDGES = frozenset(
    {
        ("IDLE", "PRECHECK"),  # request
        ("PRECHECK", "AWAITING_APPROVAL"),  # ENTRY gates pass + SEMI/WEBHOOK
        ("PRECHECK", "ARMED"),  # AUTO pass, or correction pass (inv.1)
        ("PRECHECK", "BLOCKED"),  # gate fail (+ GATE_*/entry code)
        ("AWAITING_APPROVAL", "ARMED"),  # approve
        ("AWAITING_APPROVAL", "BLOCKED"),  # deny/timeout/error (+ code)
        ("AWAITING_APPROVAL", "PRECHECK"),  # re-request (supersede prior)
        ("BLOCKED", "PRECHECK"),  # re-request (supersede prior)
    }
)


@dataclass(frozen=True, slots=True)
class ArmRequestState:
    """ST-12 row/record (CAP-0019): a per-request arm state with inv.4 provenance."""

    cloid: str  # request identity part 1 (opaque, non-empty)
    request_seq: int  # request identity part 2 (coined; >= 0)
    status: str  # one of the 5 ST-12 machine states
    timestamp: str  # inv.4 ISO-8601-Z microsecond timestamp (STR-0171/§15 inv.19)
    block_code: ArmBlockCode | None = None  # set iff status == BLOCKED
    operator_identity: str | None = None  # inv.4 identity on approve/deny/expiry

    def __post_init__(self) -> None:
        if not isinstance(self.cloid, str) or not self.cloid:
            raise ValueError("cloid must be a non-empty str")
        if type(self.request_seq) is not int or self.request_seq < 0:
            raise ValueError("request_seq must be an int >= 0")
        if self.status not in _ARM_STATUSES:
            raise ValueError(f"invalid arm status: {self.status!r}")
        _validate_iso_ts(self.timestamp)
        if self.status == "BLOCKED":
            if not isinstance(self.block_code, ArmBlockCode):
                raise ValueError("BLOCKED status requires a block_code")
        elif self.block_code is not None:
            raise ValueError("block_code is only valid for BLOCKED status")
        if self.operator_identity is not None and (
            not isinstance(self.operator_identity, str) or not self.operator_identity
        ):
            raise ValueError("operator_identity, when present, must be a non-empty str")

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "cloid": self.cloid,
            "request_seq": self.request_seq,
            "status": self.status,
            "timestamp": self.timestamp,
        }
        if self.block_code is not None:  # R-JSON-6: omit absent optionals
            obj["block_code"] = self.block_code.value
        if self.operator_identity is not None:
            obj["operator_identity"] = self.operator_identity
        return obj


def is_legal_arm_transition(from_status: str, to_status: str) -> bool:
    """Pure ST-12 edge legality over the 5 machine states (B4).

    Unknown states → ``ValueError`` (fail-closed). Known pairs → whether the edge is
    in the B4 graph (ARMED terminal, so any edge out of ARMED is ``False``).
    """
    if from_status not in _ARM_STATUSES:
        raise ValueError(f"unknown arm status: {from_status!r}")
    if to_status not in _ARM_STATUSES:
        raise ValueError(f"unknown arm status: {to_status!r}")
    return (from_status, to_status) in _LEGAL_ARM_EDGES


def supersede_request(row: ArmRequestState) -> ArmRequestState:
    """Supersede a PENDING request → BLOCKED + ARM_SUPERSEDED (L731; re-request/swap).

    Only a pending (PRECHECK/AWAITING_APPROVAL) request can be superseded; a terminal
    row (ARMED/BLOCKED) → ``ValueError`` (fail-closed). Clock-free: the record keeps
    its own timestamp (the runtime supplies fresh timestamps for new rows).
    """
    if row.status not in _PENDING_STATUSES:
        raise ValueError("only a pending request can be superseded")
    return replace(row, status="BLOCKED", block_code=ArmBlockCode.ARM_SUPERSEDED)


def expire_on_restart(row: ArmRequestState) -> ArmRequestState:
    """Restart rule (B4): a PENDING request reloads BLOCKED + ARM_TIMEOUT (fail-closed).

    Terminal rows (ARMED/BLOCKED) persist unchanged (ST-12 "pending requests
    fail-closed on restart"; STATE_OWNERSHIP.md L48-49). Clock-free: keeps the row's
    own timestamp.
    """
    if row.status not in _PENDING_STATUSES:
        return row
    return replace(row, status="BLOCKED", block_code=ArmBlockCode.ARM_TIMEOUT)


__all__ = [
    "ArmBlockCode",
    "ArmOutcome",
    "ArmPolicy",
    "ArmRequestState",
    "OperationalState",
    "OperatorDecision",
    "expire_on_restart",
    "is_legal_arm_transition",
    "supersede_request",
]
