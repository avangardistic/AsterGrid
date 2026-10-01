"""§9 Emergency Execution & Level Skip (Phase 7h-3): tolerance + four-way + skip legs.

Pure, clock-free, no I/O. The runtime's 30 s timer (STR-0277,
``EMERGENCY_BOUNDED_WAIT_S``) owns the wait bound; 7h-3 takes the breach as an input
and decides. Tolerance is a FORMULA (STR-0276/D-16), never a constant. Imports the
stdlib and ``level_state.can_level_skip`` (same-package leaf). It MUST NOT import
``core.state`` or ``core.pass_engine``.

Priority (PINNED — list order + least-aggressive-first + STR-0188/0301
"never solely because of timeout"): maker_edge → WAIT_EXTEND; elif
(taker_edge ∧ fillable ∧ in_band) → IOC_AT_BAND_EDGE; elif reprice_justifies →
REPRICE_ALO; else → LEVEL_SKIP. STR-0187 by construction: IOC requires
``taker_edge_ok`` even when fillable; ``ioc_limit_price`` is the band edge
(BU→hi, SL→lo), never beyond tolerance.

Provenance (L1368 "must log their use" vs no-logging-in-core): the record carries
``tolerance_bps + tolerance_leverage_in + tolerance_formula``; the runtime logs from
it (same pattern as inv.4 identity). RECONCILIATION: the B3 ``evaluate_emergency``
signature sketch lists band/decision inputs only; carrying ``tolerance_leverage_in``
in the output (B3 prose + E2 "provenance carried") REQUIRES it as an input, so it is
accepted here as a keyword-only provenance param (flagged in the report).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum, auto

from hypergrid.core.transitions.level_state import can_level_skip

EMERGENCY_BOUNDED_WAIT_S = 30  # STR-0277, §9.1 D-09 Group A FIXED (runtime enforces)
_TOLERANCE_FORMULA = "STR-0276/D-16"  # provenance id (50 / leverage_effective, bps)
_GROUPS = frozenset({"BU", "SL"})
_BPS_DENOM = Decimal("10000")


class _NameValueStrEnum(StrEnum):
    """StrEnum base whose ``auto()`` value equals the member name (no drift)."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name


class EmergencyVerdict(_NameValueStrEnum):
    """§9.1/§9.2 emergency decision. COINED-but-anchored per member."""

    WAIT_EXTEND = auto()  # COINED ← §9.2 WAIT (maker still economic)
    IOC_AT_BAND_EDGE = auto()  # COINED ← §9.1/§9.2 Ioc at band edge (STR-0185)
    REPRICE_ALO = auto()  # COINED ← §9.2 REPRICE (repriced Alo)
    LEVEL_SKIP = auto()  # COINED ← §9.1 ELSE / §9.3 LEVEL_SKIPPED


def compute_emergency_tolerance_bps(leverage_effective: Decimal) -> Decimal:
    """D-16 tolerance: ``50 / leverage_effective`` → whole bps HALF_UP (STR-0276).

    Ambient default context (never mutated); result quantized to whole bps, so
    downstream band math (bps/10000) terminates exactly. ``leverage_effective <= 0``
    or non-Decimal → ``ValueError``. (3 → 17 pins the rounding: 16.67 → 17.)
    """
    if not isinstance(leverage_effective, Decimal):
        raise ValueError("leverage_effective must be a Decimal instance")
    if leverage_effective <= 0:
        raise ValueError("leverage_effective must be > 0")
    return (Decimal("50") / leverage_effective).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )


@dataclass(frozen=True, slots=True)
class EmergencyEvaluation:
    """§9 emergency decision record (data; legs applied runtime/7h-4-side)."""

    order_cloid: str
    level_identity: tuple[int, int, str, int]
    verdict: EmergencyVerdict
    band_lo: Decimal
    band_hi: Decimal
    tolerance_bps: Decimal
    tolerance_leverage_in: Decimal  # provenance (STR-0276 input)
    tolerance_formula: str  # provenance id "STR-0276/D-16"
    cancel_original: bool
    ioc_limit_price: Decimal | None = None  # set iff IOC_AT_BAND_EDGE (band edge)
    ioc_size: Decimal | None = None  # set iff IOC_AT_BAND_EDGE (== remaining_size)
    skip_order_from: str | None = None  # set iff LEVEL_SKIP
    skip_order_to: str | None = None  # set iff LEVEL_SKIP
    skip_level_to: str | None = None  # set iff LEVEL_SKIP ("LEVEL_SKIPPED")

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "order_cloid": self.order_cloid,
            "level_identity": list(self.level_identity),
            "verdict": self.verdict.value,
            "band_lo": self.band_lo,
            "band_hi": self.band_hi,
            "tolerance_bps": self.tolerance_bps,
            "tolerance_leverage_in": self.tolerance_leverage_in,
            "tolerance_formula": self.tolerance_formula,
            "cancel_original": self.cancel_original,
        }
        for key, value in (
            ("ioc_limit_price", self.ioc_limit_price),
            ("ioc_size", self.ioc_size),
            ("skip_order_from", self.skip_order_from),
            ("skip_order_to", self.skip_order_to),
            ("skip_level_to", self.skip_level_to),
        ):
            if value is not None:  # R-JSON-6: omit absent optionals
                obj[key] = value
        return obj


def evaluate_emergency(
    *,
    wait_bound_breached: bool,
    direction: str,
    target_price: Decimal,
    tolerance_bps: Decimal,
    tolerance_leverage_in: Decimal,
    fillable: bool,
    best_exec_price: Decimal,
    maker_edge_ok: bool,
    taker_edge_ok: bool,
    reprice_would_justify: bool,
    remaining_size: Decimal,
    order_cloid: str,
    order_lifecycle_now: str,
    level_identity: tuple[int, int, str, int],
    level_lifecycle_now: str,
) -> EmergencyEvaluation:
    """§9.1 IF/ELSE unified with the §9.2 four-way. Fail-closed on bad input."""
    if wait_bound_breached is not True:
        raise ValueError("evaluate_emergency requires wait_bound_breached is True")
    if direction not in _GROUPS:
        raise ValueError(f"direction must be BU or SL: {direction!r}")
    for name, value in (
        ("target_price", target_price),
        ("tolerance_bps", tolerance_bps),
        ("tolerance_leverage_in", tolerance_leverage_in),
        ("best_exec_price", best_exec_price),
        ("remaining_size", remaining_size),
    ):
        if not isinstance(value, Decimal):
            raise ValueError(f"{name} must be a Decimal instance")
    if target_price <= 0:
        raise ValueError("target_price must be > 0")
    if best_exec_price <= 0:
        raise ValueError("best_exec_price must be > 0")
    if tolerance_bps < 0:
        raise ValueError("tolerance_bps must be >= 0")
    if tolerance_leverage_in <= 0:
        raise ValueError("tolerance_leverage_in must be > 0")
    if remaining_size <= 0:
        raise ValueError("remaining_size must be > 0")

    tol = tolerance_bps / _BPS_DENOM
    band_lo = target_price * (Decimal("1") - tol)
    band_hi = target_price * (Decimal("1") + tol)
    in_band = band_lo <= best_exec_price <= band_hi

    ioc_limit_price: Decimal | None = None
    ioc_size: Decimal | None = None
    skip_order_from: str | None = None
    skip_order_to: str | None = None
    skip_level_to: str | None = None

    if maker_edge_ok:
        verdict = EmergencyVerdict.WAIT_EXTEND
        cancel_original = False
    elif taker_edge_ok and fillable and in_band:
        verdict = EmergencyVerdict.IOC_AT_BAND_EDGE
        cancel_original = True
        ioc_limit_price = band_hi if direction == "BU" else band_lo
        ioc_size = remaining_size
    elif reprice_would_justify:
        verdict = EmergencyVerdict.REPRICE_ALO
        cancel_original = True
    else:
        verdict = EmergencyVerdict.LEVEL_SKIP
        cancel_original = False
        # Order leg (explicit two-step; no silent chaining from ACTIVE).
        if order_lifecycle_now == "EMERGENCY":
            skip_order_from, skip_order_to = "EMERGENCY", "SKIPPED"
        elif order_lifecycle_now == "PARTIALLY_FILLED":
            # remainder abandoned, verified fills stand (§11.4 residual → zero).
            skip_order_from, skip_order_to = "PARTIALLY_FILLED", "CANCELLED"
        else:
            raise ValueError(
                "LEVEL_SKIP order leg requires EMERGENCY or PARTIALLY_FILLED "
                f"(got {order_lifecycle_now!r}); flag EMERGENCY first"
            )
        # Level leg (fail-closed via the ST-04 skip gate).
        if not can_level_skip(level_lifecycle_now):
            raise ValueError(
                f"level {level_lifecycle_now!r} cannot be skipped (can_level_skip)"
            )
        skip_level_to = "LEVEL_SKIPPED"

    return EmergencyEvaluation(
        order_cloid=order_cloid,
        level_identity=level_identity,
        verdict=verdict,
        band_lo=band_lo,
        band_hi=band_hi,
        tolerance_bps=tolerance_bps,
        tolerance_leverage_in=tolerance_leverage_in,
        tolerance_formula=_TOLERANCE_FORMULA,
        cancel_original=cancel_original,
        ioc_limit_price=ioc_limit_price,
        ioc_size=ioc_size,
        skip_order_from=skip_order_from,
        skip_order_to=skip_order_to,
        skip_level_to=skip_level_to,
    )


__all__ = [
    "EMERGENCY_BOUNDED_WAIT_S",
    "EmergencyEvaluation",
    "EmergencyVerdict",
    "compute_emergency_tolerance_bps",
    "evaluate_emergency",
]
