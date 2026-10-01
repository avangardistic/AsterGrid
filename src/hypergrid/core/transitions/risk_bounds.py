"""§12.1 range-survivability bounds + three-layer breach ladder (Phase 7h-4a).

Pure, clock-free, I/O-free. Decimal-only; ambient default context (never mutated).
A LEAF module: stdlib only. It MUST NOT import ``core.state``/``core.pass_engine``/
``core.fold``/``config``.

B1: five bound-VALUE functions (one per monitored §12.1 bound). Inputs are params;
the caller composes with State. B2: ``apply_breach_response`` — the pure three-layer
ladder (Alert → Soft Protective Action → Operator Decision) over the 8-cell table.
Every numeric literal carries its Strategy cite (D3).
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum, auto

# --------------------------- B1 — bound-value functions ---------------------------


def compute_max_range_induced_dd_pct() -> Decimal:
    """MaxRangeInducedDD = 100 (% of Basket equity; total basket loss). FIXED.

    Cite: §12.1 ("100% of Basket equity, i.e. total basket loss"); STR-0217; STR-0280.
    """
    return Decimal("100")  # §12.1 / STR-0217 / STR-0280 (FIXED, % of basket equity)


def compute_max_execution_cost_pnl_regime(
    *, basket_net_pnl: Decimal, max_basket_notional: Decimal
) -> Decimal:
    """MaxExecutionCost, two-regime (§12.1; STR-0218/STR-0281).

    ``basket_net_pnl > 0`` → 30% of BasketNetPnL; ``basket_net_pnl <= 0`` → 100 bps of
    MaxBasketNotional (the boundary ``== 0`` takes the MBN regime, per the Strategy's
    ``≤ 0``). ``max_basket_notional`` arrives as a param (STR-0284 formula is post-7h).
    """
    if not isinstance(basket_net_pnl, Decimal):
        raise ValueError("basket_net_pnl must be a Decimal instance")
    if not isinstance(max_basket_notional, Decimal):
        raise ValueError("max_basket_notional must be a Decimal instance")
    if max_basket_notional <= 0:
        raise ValueError("max_basket_notional must be > 0")
    if basket_net_pnl > 0:
        return Decimal("0.30") * basket_net_pnl  # 30% of BasketNetPnL (STR-0281)
    # 100 bps of MaxBasketNotional (STR-0281); bps → /10000.
    return max_basket_notional * Decimal("100") / Decimal("10000")


def compute_max_failed_level_rate() -> Decimal:
    """MaxFailedLevelRate = 5 (% of Levels). FIXED.

    PINNED counting rule (the runtime computes the rate): a FAILED level := an ST-04
    row at ``LEVEL_SKIPPED`` (the §9.3 per-level terminal — covers BOTH skip paths,
    since the ST-05 leg differs by path and cannot be the counter); window := ALL
    Levels of the ACTIVE Basket (not rolling).
    Cite: §12.1; STR-0220 (``SKIPPED/total ≤ 5%``); STR-0190 (§9.3); STR-0282.
    """
    return Decimal("5")  # §12.1 / STR-0220 / STR-0282 (FIXED, % of levels)


def compute_max_hedge_cost(*, max_basket_notional: Decimal) -> Decimal:
    """MaxHedgeCost = 2% of MaxBasketNotional (§12.1; STR-0221/STR-0283)."""
    if not isinstance(max_basket_notional, Decimal):
        raise ValueError("max_basket_notional must be a Decimal instance")
    if max_basket_notional <= 0:
        raise ValueError("max_basket_notional must be > 0")
    return max_basket_notional * Decimal("2") / Decimal("100")  # 2% (STR-0283)


def compute_max_exposure_imbalance_qty(
    *,
    leverage_effective: Decimal,
    notional_per_level_usd: Decimal,
    mark_price: Decimal,
) -> Decimal:
    """MaxExposureImbalance (base-asset qty). DYNAMIC formula (never a constant).

    ``(0.25 * MaintenanceMarginFraction * NotionalPerLevel) / MarkPrice`` with
    ``MaintenanceMarginFraction = 0.5 / Leverage_effective`` (§16 D-16). No
    quantization — the exact ambient-context result. STR-0279 vector: defaults at 3x
    approx 0.00208 BTC. Cite: §12.1; §16 D-16 (STR-0329..0331); STR-0223/0279/0340.
    """
    if not isinstance(leverage_effective, Decimal):
        raise ValueError("leverage_effective must be a Decimal instance")
    if not isinstance(notional_per_level_usd, Decimal):
        raise ValueError("notional_per_level_usd must be a Decimal instance")
    if not isinstance(mark_price, Decimal):
        raise ValueError("mark_price must be a Decimal instance")
    if leverage_effective <= 0:
        raise ValueError("leverage_effective must be > 0")
    if notional_per_level_usd <= 0:
        raise ValueError("notional_per_level_usd must be > 0")
    if mark_price <= 0:
        raise ValueError("mark_price must be > 0")
    mmf = Decimal("0.5") / leverage_effective  # MaintenanceMarginFraction (STR-0340)
    return (Decimal("0.25") * mmf * notional_per_level_usd) / mark_price


# --------------------------- B2 — breach ladder ---------------------------


class _NameValueStrEnum(StrEnum):
    """StrEnum base whose ``auto()`` value equals the member name (no drift)."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name


class BreachLayer(_NameValueStrEnum):
    """§12.1 three-layer breach ladder position (+ the no-breach NONE state).

    VERBATIM SNAKE mapping (§12.1 / STR-0216): "Alert" → ALERT, "Soft Protective
    Action" → SOFT_PROTECTIVE_ACTION, "Operator Decision" → OPERATOR_DECISION.
    """

    NONE = auto()  # COINED — the no-breach state (not a Strategy layer)
    ALERT = auto()  # VERBATIM §12.1/STR-0216 "Alert"
    SOFT_PROTECTIVE_ACTION = auto()  # VERBATIM §12.1/STR-0216 "Soft Protective Action"
    OPERATOR_DECISION = auto()  # VERBATIM §12.1/STR-0216 "Operator Decision"


class RiskReasonCode(_NameValueStrEnum):
    """§12.1 breach-response codes. All COINED (reason_codes.py is frozen)."""

    RISK_BOUND_ALERT = auto()  # COINED ← §12.1 layer (1) Alert
    RISK_BOUND_SOFT_ACTION = auto()  # COINED ← §12.1 layer (2) Soft Protective Action
    RISK_BOUND_OPERATOR_REQUIRED = auto()  # COINED ← §12.1 layer (3) Operator Decision


def apply_breach_response(
    *,
    current_value: Decimal,
    bound_value: Decimal,
    prior_layer: BreachLayer,
) -> tuple[BreachLayer, RiskReasonCode | None]:
    """One breach evaluation → (next layer, new code | None). 8-cell table (§12.1).

    ``breached := current_value > bound_value`` (STRICT — ``==`` is compliant; all
    five are MAX bounds, and STR-0220's ``≤ 5%`` pins the strictness). Not breached →
    cleared to NONE from any prior. Breached escalates one step per evaluation
    (NONE→ALERT→SOFT→OPERATOR), sticky at OPERATOR (no new code, no auto-terminate,
    STR-0216). The step-per-evaluation dynamics are COINED-but-anchored (STR-0216
    ``formula: NONE`` — the Strategy pins the 3 layers/order, not the triggers).
    """
    if not isinstance(current_value, Decimal):
        raise ValueError("current_value must be a Decimal instance")
    if not isinstance(bound_value, Decimal):
        raise ValueError("bound_value must be a Decimal instance")
    if not isinstance(prior_layer, BreachLayer):
        raise ValueError("prior_layer must be a BreachLayer")
    if bound_value <= 0:
        raise ValueError("bound_value must be > 0")
    if current_value < 0:
        raise ValueError("current_value must be >= 0")

    if current_value <= bound_value:  # not breached (== is compliant)
        return (BreachLayer.NONE, None)
    if prior_layer == BreachLayer.NONE:
        return (BreachLayer.ALERT, RiskReasonCode.RISK_BOUND_ALERT)
    if prior_layer == BreachLayer.ALERT:
        return (
            BreachLayer.SOFT_PROTECTIVE_ACTION,
            RiskReasonCode.RISK_BOUND_SOFT_ACTION,
        )
    if prior_layer == BreachLayer.SOFT_PROTECTIVE_ACTION:
        return (
            BreachLayer.OPERATOR_DECISION,
            RiskReasonCode.RISK_BOUND_OPERATOR_REQUIRED,
        )
    # prior_layer == OPERATOR_DECISION: sticky, no new code (never auto-terminate).
    return (BreachLayer.OPERATOR_DECISION, None)


__all__ = [
    "BreachLayer",
    "RiskReasonCode",
    "apply_breach_response",
    "compute_max_execution_cost_pnl_regime",
    "compute_max_exposure_imbalance_qty",
    "compute_max_failed_level_rate",
    "compute_max_hedge_cost",
    "compute_max_range_induced_dd_pct",
]
