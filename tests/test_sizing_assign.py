"""§7.3 Step 1 assign_level_notionals (Phase 7g-2)."""

from decimal import Decimal

import pytest

from astergrid.core.transitions import (
    assign_level_notionals,
    compute_max_level_notional,
    compute_max_level_notional_dominant,
)

_MAX = Decimal("30000")


def test_base_all_equal_5000() -> None:
    result = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=False,
        is_dominant=False,
    )
    assert result == tuple(Decimal("5000") for _ in range(6))


def test_successor_dominant_all_equal_7500() -> None:
    result = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=True,
        is_dominant=True,
    )
    assert result == tuple(Decimal("7500") for _ in range(6))


def test_successor_weak_all_equal_5000() -> None:
    result = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=True,
        is_dominant=False,
    )
    assert result == tuple(Decimal("5000") for _ in range(6))


def test_base_ignores_dominance() -> None:
    kw = {
        "max_basket_notional": _MAX,
        "grid_levels": 6,
        "gen2_size_multiplier": Decimal("1.5"),
        "is_successor": False,
    }
    assert assign_level_notionals(**kw, is_dominant=True) == assign_level_notionals(
        **kw, is_dominant=False
    )


def test_non_terminating_division_pin_r5() -> None:
    result = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=7,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=False,
        is_dominant=False,
    )
    expected = Decimal("4285.714285714285714285714286")  # CPython default ctx (R5)
    assert result == tuple(expected for _ in range(7))


def test_single_source_matches_cap_helpers() -> None:
    base = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=False,
        is_dominant=False,
    )
    assert base[0] == compute_max_level_notional(
        max_basket_notional=_MAX, grid_levels=6
    )
    dom = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=True,
        is_dominant=True,
    )
    assert dom[0] == compute_max_level_notional_dominant(
        max_basket_notional=_MAX, grid_levels=6, gen2_size_multiplier=Decimal("1.5")
    )


def test_length_equals_grid_levels() -> None:
    for levels in (1, 6, 12):
        result = assign_level_notionals(
            max_basket_notional=_MAX,
            grid_levels=levels,
            gen2_size_multiplier=Decimal("1.5"),
            is_successor=False,
            is_dominant=False,
        )
        assert len(result) == levels


def test_validation() -> None:
    good = {
        "max_basket_notional": _MAX,
        "grid_levels": 6,
        "gen2_size_multiplier": Decimal("1.5"),
        "is_successor": True,
        "is_dominant": True,
    }
    with pytest.raises(ValueError):
        assign_level_notionals(**{**good, "max_basket_notional": Decimal("0")})
    with pytest.raises(ValueError):
        assign_level_notionals(**{**good, "grid_levels": 0})
    with pytest.raises(ValueError):
        assign_level_notionals(**{**good, "grid_levels": 13})
    with pytest.raises(ValueError):
        assign_level_notionals(**{**good, "grid_levels": True})  # bool
    with pytest.raises(ValueError):
        assign_level_notionals(**{**good, "gen2_size_multiplier": Decimal("0")})
    with pytest.raises(ValueError):
        assign_level_notionals(**{**good, "max_basket_notional": 30000})  # int
