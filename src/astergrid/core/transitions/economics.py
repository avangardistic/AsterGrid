"""§10 path economics (Phase 7h-4b-1): gross/net edge, path selection, arming validity.

Pure, clock-free, I/O-free. All edge quantities are Decimal BIPS; ambient default
context (never mutated). A LEAF module: stdlib only. It MUST NOT import ``core.state``/
``core.pass_engine``/``core.fold``/``config``.

Fee/funding/slippage VALUES arrive as parameters (STR-0194: fees are live reads, NEVER
hardcoded — no fee constant appears anywhere here). The floor arrives as a param
(STR-0273 CALIBRATABLE — never computed as StepBps/10 here). Every literal cited (D3).
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum, auto


class _NameValueStrEnum(StrEnum):
    """StrEnum base whose ``auto()`` value equals the member name (no drift)."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name


class PathEconomicsVerdict(_NameValueStrEnum):
    """§10 path-selection verdict. All COINED-but-anchored (complete 3-way)."""

    BELOW_FLOOR = auto()  # COINED ← STR-0197 "<= floor → do not arm" (either path)
    MAKER_PREFERRED = auto()  # COINED ← STR-0195 "prefer MAKER" (SHOULD → preferred)
    TAKER_REQUIRED = auto()  # COINED <- STR-0196 TAKER (MUST, emergency-only)


def compute_gross_grid_edge(*, step_bps: Decimal) -> Decimal:
    """GrossGridEdge := StepBps (DECISION-017 closed form; alpha*S/2 MUST NOT be used).

    Cite: DECISION-017 (Option A, 2026-09-22); STR-0349; STR-0351 (alpha*S/2 forbidden).
    """
    if not isinstance(step_bps, Decimal):
        raise ValueError("step_bps must be a Decimal instance")
    if step_bps <= 0:
        raise ValueError("step_bps must be > 0")
    return step_bps


def compute_net_expected_edge(
    *,
    gross_edge_bps: Decimal,
    fee_bps: Decimal,
    slippage_bps: Decimal,
    funding_bps: Decimal,
    other_bps: Decimal,
) -> Decimal:
    """NetExpectedEdge = gross - fee - slippage - funding - other (bps; STR-0193).

    ``gross_edge_bps > 0`` (GGE is StepBps by construction — anything else is a caller
    bug). fee/slippage/funding/other may be ANY sign (rebates, negative funding, price
    improvement). Cite: §10; STR-0193.
    """
    for name, value in (
        ("gross_edge_bps", gross_edge_bps),
        ("fee_bps", fee_bps),
        ("slippage_bps", slippage_bps),
        ("funding_bps", funding_bps),
        ("other_bps", other_bps),
    ):
        if not isinstance(value, Decimal):
            raise ValueError(f"{name} must be a Decimal instance")
    if gross_edge_bps <= 0:
        raise ValueError("gross_edge_bps must be > 0")
    return gross_edge_bps - fee_bps - slippage_bps - funding_bps - other_bps


def classify_path_economics(
    *,
    net_expected_edge_bps: Decimal,
    floor_bps: Decimal,
    is_emergency_or_hedge: bool,
) -> PathEconomicsVerdict:
    """§10 path selection (STR-0195/0196/0197). 3-way; boundary ``==`` is BELOW.

    ``net <= floor`` → BELOW_FLOOR (STR-0197 ``<=``, either path — failure = §9.3 Skip);
    elif emergency/hedge → TAKER_REQUIRED (STR-0196 MUST, emergency-only); else →
    MAKER_PREFERRED (STR-0195 SHOULD). Floor is a param (STR-0273).
    """
    if not isinstance(net_expected_edge_bps, Decimal):
        raise ValueError("net_expected_edge_bps must be a Decimal instance")
    if not isinstance(floor_bps, Decimal):
        raise ValueError("floor_bps must be a Decimal instance")
    if floor_bps < 0:
        raise ValueError("floor_bps must be >= 0")
    if type(is_emergency_or_hedge) is not bool:
        raise ValueError("is_emergency_or_hedge must be a bool")
    if net_expected_edge_bps <= floor_bps:
        return PathEconomicsVerdict.BELOW_FLOOR
    if is_emergency_or_hedge:
        return PathEconomicsVerdict.TAKER_REQUIRED
    return PathEconomicsVerdict.MAKER_PREFERRED


def check_arming_validity(
    *,
    gge_bps: Decimal,
    fee_maker_bps: Decimal,
    funding_est_bps: Decimal,
    floor_bps: Decimal,
) -> bool:
    """DECISION-017 validity: ``GGE - 2*fee_maker - funding_est > floor`` (STRICT).

    Boundary ``==`` is INVALID (strict ``>``). "At Tier-0 fees" is the fee BASIS; values
    arrive as params (STR-0194). Cite: DECISION-017; STR-0350 (``10 - 2*1.5 - 0 = 7``).
    """
    for name, value in (
        ("gge_bps", gge_bps),
        ("fee_maker_bps", fee_maker_bps),
        ("funding_est_bps", funding_est_bps),
        ("floor_bps", floor_bps),
    ):
        if not isinstance(value, Decimal):
            raise ValueError(f"{name} must be a Decimal instance")
    if gge_bps <= 0:
        raise ValueError("gge_bps must be > 0")
    if floor_bps < 0:
        raise ValueError("floor_bps must be >= 0")
    return gge_bps - Decimal("2") * fee_maker_bps - funding_est_bps > floor_bps


__all__ = [
    "PathEconomicsVerdict",
    "check_arming_validity",
    "classify_path_economics",
    "compute_gross_grid_edge",
    "compute_net_expected_edge",
]
