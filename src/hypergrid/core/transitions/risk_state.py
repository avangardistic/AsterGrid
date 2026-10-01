"""ST-17/ST-20/ST-21/ST-22 row types (Phase 7h-4a). Frozen, slots, self-validating.

A LEAF module: stdlib (``dataclasses``, ``decimal``, ``enum`` unused-except-reuse,
``re``) + same-package ``arm_state.OperationalState`` (ST-22 reuse) and
``risk_bounds.BreachLayer`` (ST-20 ladder) ONLY. It MUST NOT import ``core.state``/
``core.pass_engine``/``core.fold``/``config``.

Timestamps are ISO-8601-Z microsecond strings, validated by a module-local helper
(arm_state pattern — no ``datetime``, no frozen/private import). ``to_canonical_obj``
keeps Decimals native, enums as ``.value``, tuples as lists, omits None (R-JSON-6).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from hypergrid.core.transitions.arm_state import OperationalState
from hypergrid.core.transitions.risk_bounds import BreachLayer

# R-JSON-5 ISO-8601-Z microseconds (module-local; mirrors arm_state — no datetime).
_ISO_UTC_MICROS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")

# The 5 VERBATIM §12.1 monitored-bound names (NOT MaxBasketNotional — computed-once,
# §14 global rule, so it has no ladder). Module-private (validated str, not an enum:
# mixed case forbids the auto()==name enum pattern).
_BOUND_IDS = frozenset(
    {
        "MaxRangeInducedDD",
        "MaxExposureImbalance",
        "MaxExecutionCost",
        "MaxFailedLevelRate",
        "MaxHedgeCost",
    }
)
_CLEARINGHOUSE = "clearinghouseState"  # DECISION-002 authority endpoint (not a path)


def _validate_iso_ts(value: str, name: str) -> None:
    if not isinstance(value, str) or _ISO_UTC_MICROS.match(value) is None:
        raise ValueError(f"{name} must be an ISO-8601-Z microsecond string")


@dataclass(frozen=True, slots=True)
class AccountEquityState:
    """ST-17: point-in-time account equity (CapitalBase), authoritative source only."""

    capital_base_usd: Decimal  # > 0
    # MUST == "clearinghouseState": DECISION-002 names the AUTHORITY endpoint (the
    # exact field is marginSummary.accountValue, SRC-107), not a JSON path — the ST-08
    # ActualExposureState.source precedent. STR-0224.
    source: str
    read_at_ts: str  # ISO-8601-Z micros (point-in-time read)

    def __post_init__(self) -> None:
        if not isinstance(self.capital_base_usd, Decimal):
            raise ValueError("capital_base_usd must be a Decimal instance")
        if self.capital_base_usd <= 0:
            raise ValueError("capital_base_usd must be > 0")
        if self.source != _CLEARINGHOUSE:
            raise ValueError(f"source must be {_CLEARINGHOUSE!r} (DECISION-002)")
        _validate_iso_ts(self.read_at_ts, "read_at_ts")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "capital_base_usd": self.capital_base_usd,
            "source": self.source,
            "read_at_ts": self.read_at_ts,
        }


@dataclass(frozen=True, slots=True)
class BoundLayerState:
    """ST-20 per-bound ladder state — the persisted §12.1 alert record.

    ``bound_id`` = identity, ``updated_at_ts`` = timestamp (§12.1 "persisted, with
    identity and timestamp"; the runtime supplies ``updated_at_ts`` at evaluation).
    """

    bound_id: str  # ∈ the 5 verbatim §12.1 names
    layer: BreachLayer
    updated_at_ts: str  # ISO-8601-Z micros

    def __post_init__(self) -> None:
        if self.bound_id not in _BOUND_IDS:
            raise ValueError(f"unknown bound_id: {self.bound_id!r}")
        if not isinstance(self.layer, BreachLayer):
            raise ValueError("layer must be a BreachLayer")
        _validate_iso_ts(self.updated_at_ts, "updated_at_ts")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "bound_id": self.bound_id,
            "layer": self.layer.value,
            "updated_at_ts": self.updated_at_ts,
        }


@dataclass(frozen=True, slots=True)
class RiskBoundTrackerState:
    """ST-20: lifetime-to-date tracked quantities + per-bound ladder states (D-15)."""

    cumulative_execution_cost_usd: Decimal  # >= 0 (lifetime-to-date)
    cumulative_hedge_cost_usd: Decimal  # >= 0 (lifetime-to-date)
    failed_level_rate_pct: Decimal  # in [0, 100] (B1.3 counting rule; runtime-fed)
    range_induced_dd_pct: Decimal  # in [0, 100]
    # Per-bound LADDER state only; the |ExposureDelta| CURRENT value lives in ST-09
    # (already typed) — ST-20 carries no duplicate quantity.
    bound_layers: tuple[BoundLayerState, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("cumulative_execution_cost_usd", self.cumulative_execution_cost_usd),
            ("cumulative_hedge_cost_usd", self.cumulative_hedge_cost_usd),
        ):
            if not isinstance(value, Decimal):
                raise ValueError(f"{name} must be a Decimal instance")
            if value < 0:
                raise ValueError(f"{name} must be >= 0")
        for name, value in (
            ("failed_level_rate_pct", self.failed_level_rate_pct),
            ("range_induced_dd_pct", self.range_induced_dd_pct),
        ):
            if not isinstance(value, Decimal):
                raise ValueError(f"{name} must be a Decimal instance")
            if not (0 <= value <= 100):
                raise ValueError(f"{name} must be within [0, 100]")
        ids = [row.bound_id for row in self.bound_layers]
        if ids != sorted(ids) or len(set(ids)) != len(ids):
            raise ValueError("bound_layers must be sorted by bound_id, no dups")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "cumulative_execution_cost_usd": self.cumulative_execution_cost_usd,
            "cumulative_hedge_cost_usd": self.cumulative_hedge_cost_usd,
            "failed_level_rate_pct": self.failed_level_rate_pct,
            "range_induced_dd_pct": self.range_induced_dd_pct,
            "bound_layers": [row.to_canonical_obj() for row in self.bound_layers],
        }


@dataclass(frozen=True, slots=True)
class BasketNetPnLState:
    """ST-21: NET PnL accounting. NET (never gross) governs every lifecycle decision."""

    realized_usd: Decimal  # any sign
    unrealized_usd: Decimal  # any sign
    fees_usd: Decimal  # any sign (rebates exist)
    funding_usd: Decimal  # any sign (negative funding exists)
    net_usd: Decimal  # == realized + unrealized - fees + funding (STR-0234)

    def __post_init__(self) -> None:
        for name, value in (
            ("realized_usd", self.realized_usd),
            ("unrealized_usd", self.unrealized_usd),
            ("fees_usd", self.fees_usd),
            ("funding_usd", self.funding_usd),
            ("net_usd", self.net_usd),
        ):
            if not isinstance(value, Decimal):
                raise ValueError(f"{name} must be a Decimal instance")
        expected = (
            self.realized_usd + self.unrealized_usd - self.fees_usd + self.funding_usd
        )
        if self.net_usd != expected:
            raise ValueError(
                "net_usd must equal realized + unrealized - fees + funding (STR-0234)"
            )

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "realized_usd": self.realized_usd,
            "unrealized_usd": self.unrealized_usd,
            "fees_usd": self.fees_usd,
            "funding_usd": self.funding_usd,
            "net_usd": self.net_usd,
        }


@dataclass(frozen=True, slots=True)
class FreezeErrorRecoveryOverlayState:
    """ST-22: the freeze/error/recovery overlay (never erases underlying state)."""

    operational_state: OperationalState  # REUSE arm_state (9 §13.2 members VERBATIM)
    since_ts: str  # ISO-8601-Z micros
    # OPEN cause vocabulary (runtime/post-7h writers across subsystems): the row
    # CARRIES provenance, it does not gate — content is not checked against a set.
    last_reason_code: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.operational_state, OperationalState):
            raise ValueError("operational_state must be an OperationalState")
        _validate_iso_ts(self.since_ts, "since_ts")
        if self.last_reason_code is not None and (
            not isinstance(self.last_reason_code, str) or not self.last_reason_code
        ):
            raise ValueError("last_reason_code, when present, must be a non-empty str")

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "operational_state": self.operational_state.value,
            "since_ts": self.since_ts,
        }
        if self.last_reason_code is not None:  # R-JSON-6
            obj["last_reason_code"] = self.last_reason_code
        return obj


__all__ = [
    "AccountEquityState",
    "BasketNetPnLState",
    "BoundLayerState",
    "FreezeErrorRecoveryOverlayState",
    "RiskBoundTrackerState",
]
