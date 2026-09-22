"""The folded State (Phase 7c): metadata + one placeholder field per ST-*.

Phase 7c is metadata-only. The State carries fold metadata (last log_sequence,
head_hash, event_count, per-kind counts) plus one placeholder field for every
ST-01..ST-23 in STATE_OWNERSHIP.md, all defaulting to ``None``. Domain typing
and semantics arrive in Phase 7d+. The State is frozen and validates its own
metadata invariants at construction, so no invalid State can be serialized.
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
    """The deterministic folded state (Phase 7c: metadata only)."""

    # --- fold metadata (always populated) ---
    log_sequence: int | None  # last observed log_sequence; None if the log is empty
    head_hash: str  # last content_hash, or GENESIS_PREV_HASH if empty
    event_count: int  # number of envelopes folded
    per_kind_count: tuple[tuple[str, int], ...]  # sorted (kind, count) for all ten

    # --- placeholder domain fields, one per ST-* (STATE_OWNERSHIP.md) ---
    st01_basket_lifecycle_state: object | None = None  # ST-01
    st02_generation_states: object | None = None  # ST-02
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
    st14_dominance_flag: object | None = None  # ST-14
    st15_successor_lock: object | None = None  # ST-15
    st16_evolution_candidate_window: object | None = None  # ST-16
    st17_account_equity_capital_base: object | None = None  # ST-17
    st18_open_order_registry: object | None = None  # ST-18
    st19_market_observation_cache: object | None = None  # ST-19
    st20_risk_bound_trackers: object | None = None  # ST-20
    st21_basket_pnl_accounting_net: object | None = None  # ST-21
    st22_freeze_error_recovery_overlay: object | None = None  # ST-22
    st23_mirror_targets_hedge_intents: object | None = None  # ST-23

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
        for name in _DOMAIN_FIELD_NAMES:
            value = getattr(self, name)
            if value is not None:
                obj[name] = value
        return obj


_DOMAIN_FIELD_NAMES: tuple[str, ...] = tuple(
    f.name for f in fields(State) if f.name not in _METADATA_FIELDS
)
