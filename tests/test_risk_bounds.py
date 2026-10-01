"""§12.1 bound-value functions (Phase 7h-4a, E2). Exact Decimal vectors."""

from decimal import Decimal

import pytest

from astergrid.core.transitions import (
    compute_max_execution_cost_pnl_regime,
    compute_max_exposure_imbalance_qty,
    compute_max_failed_level_rate,
    compute_max_hedge_cost,
    compute_max_range_induced_dd_pct,
)


def test_max_range_induced_dd_is_100() -> None:
    assert compute_max_range_induced_dd_pct() == Decimal("100")


def test_max_failed_level_rate_is_5() -> None:
    assert compute_max_failed_level_rate() == Decimal("5")


def test_exec_cost_pnl_positive_regime() -> None:
    assert compute_max_execution_cost_pnl_regime(
        basket_net_pnl=Decimal("1000"), max_basket_notional=Decimal("30000")
    ) == Decimal("300.00")  # 30% of 1000


def test_exec_cost_zero_and_negative_take_mbn_regime() -> None:
    # PnL == 0 → MBN regime (100 bps of 30000 = 300).
    assert compute_max_execution_cost_pnl_regime(
        basket_net_pnl=Decimal("0"), max_basket_notional=Decimal("30000")
    ) == Decimal("300")
    # PnL < 0 → MBN regime.
    assert compute_max_execution_cost_pnl_regime(
        basket_net_pnl=Decimal("-500"), max_basket_notional=Decimal("30000")
    ) == Decimal("300")


def test_hedge_cost_is_2pct_of_mbn() -> None:
    assert compute_max_hedge_cost(max_basket_notional=Decimal("30000")) == Decimal(
        "600"
    )


def test_exposure_imbalance_terminating_vector_exact() -> None:
    # lev 2, NPL 5000, PX 100000 → (0.25 * 0.25 * 5000)/100000 = 0.003125 EXACT.
    assert compute_max_exposure_imbalance_qty(
        leverage_effective=Decimal("2"),
        notional_per_level_usd=Decimal("5000"),
        mark_price=Decimal("100000"),
    ) == Decimal("0.003125")


def test_exposure_imbalance_str0279_defaults_vector() -> None:
    # lev 3 defaults → ~0.00208 BTC (STR-0279), quantized to 5dp.
    result = compute_max_exposure_imbalance_qty(
        leverage_effective=Decimal("3"),
        notional_per_level_usd=Decimal("5000"),
        mark_price=Decimal("100000"),
    )
    assert result.quantize(Decimal("0.00001")) == Decimal("0.00208")


def test_validation_errors() -> None:
    with pytest.raises(ValueError):
        compute_max_execution_cost_pnl_regime(
            basket_net_pnl=Decimal("1"), max_basket_notional=Decimal("0")
        )
    with pytest.raises(ValueError):
        compute_max_execution_cost_pnl_regime(
            basket_net_pnl=1.0,  # type: ignore[arg-type]
            max_basket_notional=Decimal("30000"),
        )
    with pytest.raises(ValueError):
        compute_max_hedge_cost(max_basket_notional=Decimal("-1"))
    for bad in (
        {"leverage_effective": Decimal("0")},
        {"notional_per_level_usd": Decimal("0")},
        {"mark_price": Decimal("0")},
    ):
        kwargs = {
            "leverage_effective": Decimal("3"),
            "notional_per_level_usd": Decimal("5000"),
            "mark_price": Decimal("100000"),
        }
        kwargs.update(bad)
        with pytest.raises(ValueError):
            compute_max_exposure_imbalance_qty(**kwargs)
    with pytest.raises(ValueError):
        compute_max_exposure_imbalance_qty(
            leverage_effective=3,  # type: ignore[arg-type]
            notional_per_level_usd=Decimal("5000"),
            mark_price=Decimal("100000"),
        )
