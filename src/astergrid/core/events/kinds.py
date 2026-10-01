"""The ten event KINDS (EVENT_MODEL.md §A2), as frozen, slots-enabled dataclasses.

Design rules (Phase 7b):
  * Each kind is ``@dataclass(frozen=True, slots=True)`` with NO domain-semantic
    methods (no folding of §4-§13 rules).
  * ``Decimal`` for money/price/size; ``int`` for counts; ``str`` for identifiers.
  * Identifiers are OPAQUE, CALLER-SUPPLIED strings (venue cloids/oids, operator
    identities). Core never generates an identifier (no uuid, no randomness, no
    counter-derived id — the monotonic ``log_sequence`` belongs to the log,
    R-SEQ-1).
  * No event carries its own ``log_sequence`` (R-SEQ-1); it carries a uniform
    ``causal_predecessors: tuple[int, ...]`` referencing already-recorded priors
    by their ``log_sequence`` (EVENT_MODEL §A3).
  * ``event_kind`` is a ``ClassVar[str]`` matching R-JSON-7 exactly.
  * Fields are MINIMAL — each corresponds to EVENT_MODEL §A2 "minimal conceptual
    content"; provenance is cited per field. Domain timestamps that §A2 lists as
    kind content (observation read ts, timer fire ts, operator ts) are EVENT
    payload fields; DECISION-007 log-observation keys live only in the envelope.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class IntentEvent:
    """§A2(a) intent — a Core decision to act. Serves STR-0298/0344/0356/0208."""

    intent_classification: str  # §A2(a): ENTRY_INTENT / EXPOSURE_CORRECTION_INTENT
    target_generation_id: int  # §A2(a) target Generation (§3 identity)
    target_cycle_id: int  # §A2(a) target Cycle (§3 identity)
    target_level_id: int  # §A2(a) target Level (§3 identity)
    target_direction: str  # §A2(a) group/direction (§3 identity: BU/SL)
    requested_size: Decimal  # §A2(a) requested size concept
    requested_price: Decimal  # §A2(a) requested price concept
    cloid: str  # §A2(a) client order id (opaque); STR-0298
    acute: bool  # §A2(a) acute/non-acute flag; STR-0356/0357
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "intent"


@dataclass(frozen=True, slots=True)
class CommandEvent:
    """§A2(b) command — a committed side effect. Serves STR-0298/0133/0138/0254."""

    cloid: str  # §A2(b) client order id (opaque); STR-0298
    action: str  # §A2(b) action concept: submit/cancel/modify/twap
    tif: str  # §A2(b) TIF concept (Alo/Gtc/Ioc); STR-0133
    # Originating intent is referenced via causal_predecessors (§A2(b)).
    expires_after: int | None = None  # §A2(b) expiresAfter concept; DECISION-008
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "command"


@dataclass(frozen=True, slots=True)
class AcknowledgmentEvent:
    """§A2(c) acknowledgment — venue ack of a command. Serves STR-0133/0132."""

    cloid: str  # §A2(c) cloid linkage (opaque)
    ack_status: str  # §A2(c) ack status concept: resting/filled/error
    venue_oid: str | None = None  # §A2(c) venue oid when present (opaque)
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "acknowledgment"


@dataclass(frozen=True, slots=True)
class FillEvent:
    """§A2(d) fill — venue fill notification. Serves STR-0131/0071/0199/0212."""

    cloid: str  # §A2(d) cloid linkage (opaque)
    filled_quantity: Decimal  # §A2(d) filled quantity concept; STR-0199/0212
    price: Decimal  # §A2(d) price concept
    is_snapshot: bool  # §A2(d) snapshot flag
    venue_oid: str | None = None  # §A2(d) oid linkage when present (opaque)
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "fill"


@dataclass(frozen=True, slots=True)
class ObservationEvent:
    """§A2(e) observation — an authoritative/observed venue read.

    Serves STR-0199/0200/0224 (authoritative via clearinghouseState, DECISION-002),
    STR-0337, STR-0352. The DECISION-007 canonical-order keys live in the envelope,
    NOT here; ``read_timestamp`` is the §A2(e) payload read timestamp.
    """

    source_endpoint: str  # §A2(e) source endpoint
    read_timestamp: str  # §A2(e) read timestamp (ISO-8601-Z payload field)
    payload_fingerprint: str  # §A2(e) payload fingerprint (content hash, opaque)
    freshness_window_seconds: int  # §A2(e) freshness window; STR-0369
    is_full: bool  # §A2(e) full/partial flag (True=full, False=partial)
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "observation"


@dataclass(frozen=True, slots=True)
class TimerEvent:
    """§A2(f) timer — internal time-based trigger. STR-0036..0039/0169/0353."""

    timer_kind: str  # §A2(f) timer kind
    fire_timestamp: str  # §A2(f) fire timestamp (ISO-8601-Z payload field)
    associated_entity: str  # §A2(f) associated entity id (opaque)
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "timer"


@dataclass(frozen=True, slots=True)
class ErrorEvent:
    """§A2(g) error — adapter/venue error. STR-0163/0182/0190; DECISION-008."""

    error_class: str  # §A2(g) error class: precision/margin/rate-limit/price/risk
    source: str  # §A2(g) source
    linkage_cloid: str | None = None  # §A2(g) linkage to command/stream (opaque)
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "error"


@dataclass(frozen=True, slots=True)
class StateTransitionEvent:
    """§A2(h) state-transition — a domain state change from the fold.

    Serves STR-0315/0334, DECISION-013 reason codes, STR-0354. Phase 7b records
    the transition's fields only; the FOLD that produces it is Phase 7c.
    """

    prior_state: str  # §A2(h) prior state concept
    next_state: str  # §A2(h) next state concept
    reason_code: str  # §A2(h) unique reason code; DECISION-013
    causal_predecessors: tuple[int, ...] = ()  # §A2(h) causal-chain reference

    event_kind: ClassVar[str] = "state-transition"


@dataclass(frozen=True, slots=True)
class OperatorEvent:
    """§A2(i) operator — a gated operator action. Serves STR-0168/0171; DECISION-014."""

    operator_identity: str  # §A2(i) operator/service identity (opaque); STR-0171
    timestamp: str  # §A2(i) timestamp (ISO-8601-Z payload field)
    action: str  # §A2(i) action: approve/deny/freeze/resume/kill-switch/clearance
    target: str  # §A2(i) target
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "operator"


@dataclass(frozen=True, slots=True)
class AdministrativeEvent:
    """§A2(j) administrative — config/version/calibration. STR-0257/0355/0358/0011."""

    config_identity: str  # §A2(j) config/version identity (opaque)
    effective_time: str  # §A2(j) effective-time (ISO-8601-Z payload field)
    provenance: str  # §A2(j) provenance
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

    event_kind: ClassVar[str] = "administrative"


# Discriminated union of the ten kinds (used by the envelope and the log port).
AnyEvent = (
    IntentEvent
    | CommandEvent
    | AcknowledgmentEvent
    | FillEvent
    | ObservationEvent
    | TimerEvent
    | ErrorEvent
    | StateTransitionEvent
    | OperatorEvent
    | AdministrativeEvent
)
