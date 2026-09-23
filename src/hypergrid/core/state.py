"""The folded State: fold metadata + ST-* domain fields + §4.7 arbitration markers.

The State carries fold metadata (last log_sequence, head_hash, event_count,
per-kind counts), one field per ST-01..ST-23 (STATE_OWNERSHIP.md), the Phase-7d
§4.7 arbitration markers, and the Phase-7e ``effective_generation_limit`` marker.

Phase 7e types the generation-lifecycle family ST-02/14/15/16 (frozen dataclasses
in ``transitions/generation_state.py``) and enforces their ordering/coherence
invariants at construction. The remaining ST-* (ST-01, ST-03..ST-13, ST-17..ST-23)
stay ``object | None`` placeholders until their rule is implemented (Phase 7f+).
The State is frozen and validates its own invariants, so no invalid State can be
serialized.
"""

from __future__ import annotations

from dataclasses import dataclass, fields

from hypergrid.core.events import (
    AcknowledgmentEvent,
    AdministrativeEvent,
    CommandEvent,
    ErrorEvent,
    FillEvent,
    IntentEvent,
    ObservationEvent,
    OperatorEvent,
    StateTransitionEvent,
    TimerEvent,
)
from hypergrid.core.transitions.generation_state import (
    DominanceFlag,
    EvolutionCandidateWindow,
    GenerationState,
    SuccessorLock,
)
from hypergrid.core.transitions.markers import (
    P2Attempts,
    P2LocksState,
    P3CandidateMarkers,
    P4CandidateMarkers,
    P4Decision,
)

# The ten R-JSON-7 kind tags, sorted ascending — derived from the event classes
# (no duplicated hardcoded list).
_EVENT_KINDS: tuple[str, ...] = tuple(
    sorted(
        cls.event_kind
        for cls in (
            IntentEvent,
            CommandEvent,
            AcknowledgmentEvent,
            FillEvent,
            ObservationEvent,
            TimerEvent,
            ErrorEvent,
            StateTransitionEvent,
            OperatorEvent,
            AdministrativeEvent,
        )
    )
)

_HEX_CHARS = frozenset("0123456789abcdef")
_METADATA_FIELDS = frozenset(
    {"log_sequence", "head_hash", "event_count", "per_kind_count"}
)


@dataclass(frozen=True, slots=True)
class State:
    """The deterministic folded state (metadata + ST-* + §4.7 markers)."""

    # --- fold metadata (always populated) ---
    log_sequence: int | None  # last observed log_sequence; None if the log is empty
    head_hash: str  # last content_hash, or GENESIS_PREV_HASH if empty
    event_count: int  # number of envelopes folded
    per_kind_count: tuple[tuple[str, int], ...]  # sorted (kind, count) for all ten

    # --- domain fields, one per ST-* (STATE_OWNERSHIP.md) ---
    # Phase 7e types ST-02/14/15/16 (the generation lifecycle family, below).
    # ST-01/ST-03..ST-13/ST-17..ST-23 remain placeholders (object | None) and are
    # typed when their rule is implemented (Phase 7f+).
    st01_basket_lifecycle_state: object | None = None  # ST-01
    st02_generation_states: tuple[GenerationState, ...] | None = None  # ST-02 (7e)
    st03_cycle_states: object | None = None  # ST-03
    st04_level_pipeline_states: object | None = None  # ST-04
    st05_order_intents_and_outcomes: object | None = None  # ST-05
    st06_cloid_registry: object | None = None  # ST-06
    st07_expected_exposure: object | None = None  # ST-07
    st08_actual_exposure: object | None = None  # ST-08
    st09_exposure_delta: object | None = None  # ST-09
    st10_reference_prices: object | None = None  # ST-10
    st11_calibration_configuration: object | None = None  # ST-11
    st12_operator_arm_requests: object | None = None  # ST-12
    st13_event_log_audit_trail: object | None = None  # ST-13
    st14_dominance_flags: tuple[DominanceFlag, ...] | None = None  # ST-14 (7e)
    st15_successor_locks: tuple[SuccessorLock, ...] | None = None  # ST-15 (7e)
    st16_evolution_candidate_windows: (
        tuple[EvolutionCandidateWindow, ...] | None
    ) = None  # ST-16 (7e)
    st17_account_equity_capital_base: object | None = None  # ST-17
    st18_open_order_registry: object | None = None  # ST-18
    st19_market_observation_cache: object | None = None  # ST-19
    st20_risk_bound_trackers: object | None = None  # ST-20
    st21_basket_pnl_accounting_net: object | None = None  # ST-21
    st22_freeze_error_recovery_overlay: object | None = None  # ST-22
    st23_mirror_targets_hedge_intents: object | None = None  # ST-23

    # --- Phase-7d §4.7 arbitration markers (typed here; 7d-owned only) ---
    # Forward note: these p2_/p3_/p4_ fields are the §4.7 pass-arbitration markers.
    # They will be RECONCILED with (not duplicated by) the ST-* domain fields when
    # Phase 7e types those (e.g. ST-15 successor lock, ST-16 evolution candidate
    # window). Until then they stand alone and default to None.
    p2_locks: P2LocksState | None = None  # §4.7 P2 in-flight locks
    p2_attempts: P2Attempts | None = None  # §4.7 P2 per-pass attempts
    p3_candidates: P3CandidateMarkers | None = None  # §4.7 P3 candidates
    # §4.7 P3 ineligible Evolution GenerationIDs this pass (reason CYCLE_LIMIT_REACHED)
    p3_decisions: tuple[int, ...] | None = None
    p4_candidates: P4CandidateMarkers | None = None  # §4.7 P4 candidates
    p4_decisions: tuple[P4Decision, ...] | None = None  # §4.7 P4 ordered admissions

    # Phase-7e arbitration marker (NOT an ST-* field; like the p2_/p3_/p4_ markers):
    # the effective Generation limit read by the evolution transition (§4.6).
    # None ⟹ 99 (the §4.6 hard default applies now; no "unknown" state). Wiring a
    # lower config override from UserParams.max_generations is a later runtime
    # concern; the transition only ever reads this marker.
    effective_generation_limit: int | None = None

    def __post_init__(self) -> None:
        if self.event_count < 0:
            raise ValueError("event_count must be >= 0")
        if len(self.head_hash) != 64 or any(
            ch not in _HEX_CHARS for ch in self.head_hash
        ):
            raise ValueError("head_hash must be 64 lowercase hex characters")
        kinds = tuple(kind for kind, _ in self.per_kind_count)
        if kinds != _EVENT_KINDS:
            raise ValueError(
                "per_kind_count must cover exactly the ten kind tags, sorted"
            )
        if any(count < 0 for _, count in self.per_kind_count):
            raise ValueError("per_kind_count values must be >= 0")
        self._validate_generation_invariants()

    def _validate_generation_invariants(self) -> None:
        """Phase-7e ordering + coherence invariants on ST-02/14/15/16.

        Enforced: each of the four generation tuples is sorted by ``generation_id``
        ascending with NO duplicate ids; and no ``EVOLUTION_PENDING`` Generation
        carries a set ST-15 lock (a pending gen is running its window, not locked).

        NOT enforced (deliberate — documented): the "a window ⟹ lifecycle ∈
        {ACTIVE, EVOLUTION_PENDING, CREATED}" restriction. It contradicts rule (5)
        (SUCCESSOR_LOCK_ACTIVE needs a window on a SUCCESSOR_CREATED gen), rule (6)
        (GENERATION_ID_LIMIT needs a window on G99), rule (1a) (the disabled-skip
        case needs a window on a DISABLED gen) and §5.7 scenarios 11/12/19.
        Lifecycle gating for terminal states lives in the evolution transition
        (rules 1/5/6), where §4.3/§5.3 semantics belong.
        """
        for name, items in (
            ("st02_generation_states", self.st02_generation_states),
            ("st14_dominance_flags", self.st14_dominance_flags),
            ("st15_successor_locks", self.st15_successor_locks),
            ("st16_evolution_candidate_windows", self.st16_evolution_candidate_windows),
        ):
            if items is None:
                continue
            ids = [entry.generation_id for entry in items]
            if ids != sorted(ids) or len(set(ids)) != len(ids):
                raise ValueError(f"{name} must be sorted by generation_id, no dups")
        if self.st02_generation_states is not None and (
            self.st15_successor_locks is not None
        ):
            pending = {
                g.generation_id
                for g in self.st02_generation_states
                if g.lifecycle == "EVOLUTION_PENDING"
            }
            locked = {
                s.generation_id for s in self.st15_successor_locks if s.locked
            }
            if pending & locked:
                raise ValueError("EVOLUTION_PENDING generation must not be locked")

    def to_canonical_obj(self) -> dict[str, object]:
        """Canonical dict for :func:`canonical_dumps` (no None/float in output)."""
        obj: dict[str, object] = {
            "is_empty": self.log_sequence is None,
            "head_hash": self.head_hash,
            "event_count": self.event_count,
            "per_kind_count": [[kind, count] for kind, count in self.per_kind_count],
        }
        if self.log_sequence is not None:
            obj["log_sequence"] = self.log_sequence
        # Untyped ST-* placeholders are always None (Phase 7f+), so this loop emits
        # nothing yet; the typed ST-02/14/15/16 are serialized explicitly below.
        for name in _DOMAIN_FIELD_NAMES:
            value = getattr(self, name)
            if value is not None:
                obj[name] = value
        # Phase-7e typed generation state: omit when None (R-JSON-6), else recurse
        # (each already stored sorted by generation_id).
        if self.st02_generation_states is not None:
            obj["st02_generation_states"] = [
                g.to_canonical_obj() for g in self.st02_generation_states
            ]
        if self.st14_dominance_flags is not None:
            obj["st14_dominance_flags"] = [
                d.to_canonical_obj() for d in self.st14_dominance_flags
            ]
        if self.st15_successor_locks is not None:
            obj["st15_successor_locks"] = [
                s.to_canonical_obj() for s in self.st15_successor_locks
            ]
        if self.st16_evolution_candidate_windows is not None:
            obj["st16_evolution_candidate_windows"] = [
                w.to_canonical_obj() for w in self.st16_evolution_candidate_windows
            ]
        if self.effective_generation_limit is not None:
            obj["effective_generation_limit"] = self.effective_generation_limit
        # Phase-7d arbitration markers: omit when None (R-JSON-6), else recurse.
        if self.p2_locks is not None:
            obj["p2_locks"] = self.p2_locks.to_canonical_obj()
        if self.p2_attempts is not None:
            obj["p2_attempts"] = self.p2_attempts.to_canonical_obj()
        if self.p3_candidates is not None:
            obj["p3_candidates"] = self.p3_candidates.to_canonical_obj()
        if self.p3_decisions is not None:
            obj["p3_decisions"] = sorted(self.p3_decisions)
        if self.p4_candidates is not None:
            obj["p4_candidates"] = self.p4_candidates.to_canonical_obj()
        if self.p4_decisions is not None:
            obj["p4_decisions"] = [d.to_canonical_obj() for d in self.p4_decisions]
        return obj


# Fields serialized explicitly (not via the generic always-None ST-* loop): the
# Phase-7d arbitration markers, the Phase-7e typed ST-* fields, and the
# effective_generation_limit marker.
_ARBITRATION_FIELD_NAMES = frozenset(
    {
        "p2_locks",
        "p2_attempts",
        "p3_candidates",
        "p3_decisions",
        "p4_candidates",
        "p4_decisions",
        "effective_generation_limit",
    }
)
_TYPED_ST_FIELD_NAMES = frozenset(
    {
        "st02_generation_states",
        "st14_dominance_flags",
        "st15_successor_locks",
        "st16_evolution_candidate_windows",
    }
)
_DOMAIN_FIELD_NAMES: tuple[str, ...] = tuple(
    f.name
    for f in fields(State)
    if f.name not in _METADATA_FIELDS
    and f.name not in _ARBITRATION_FIELD_NAMES
    and f.name not in _TYPED_ST_FIELD_NAMES
)
