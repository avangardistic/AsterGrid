"""§7.3 end-to-end composition: assign -> enforce -> convert (Phase 7g-2)."""

from decimal import Decimal

import pytest

from astergrid.core.transitions import (
    assign_level_notionals,
    compute_max_level_notional,
    compute_max_level_notional_dominant,
    convert_notional_to_size,
    enforce_level_caps,
)

_MAX = Decimal("30000")


def _caps(gen2: Decimal) -> tuple[Decimal, Decimal]:
    return (
        compute_max_level_notional(max_basket_notional=_MAX, grid_levels=6),
        compute_max_level_notional_dominant(
            max_basket_notional=_MAX, grid_levels=6, gen2_size_multiplier=gen2
        ),
    )


def test_base_pipeline() -> None:
    notionals = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=False,
        is_dominant=False,
    )
    cap, cap_dom = _caps(Decimal("1.5"))
    checked = enforce_level_caps(
        level_notionals=notionals,
        max_level_notional=cap,
        max_level_notional_dominant=cap_dom,
        is_successor=False,
        is_dominant=False,
    )
    sizes = tuple(
        convert_notional_to_size(
            notional=n, mark_price=Decimal("100000"), sz_decimals=5
        )
        for n in checked
    )
    assert sizes == tuple(Decimal("0.05") for _ in range(6))


def test_successor_dominant_pipeline() -> None:
    notionals = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=True,
        is_dominant=True,
    )
    cap, cap_dom = _caps(Decimal("1.5"))
    checked = enforce_level_caps(
        level_notionals=notionals,
        max_level_notional=cap,
        max_level_notional_dominant=cap_dom,
        is_successor=True,
        is_dominant=True,
    )
    sizes = tuple(
        convert_notional_to_size(
            notional=n, mark_price=Decimal("100000"), sz_decimals=5
        )
        for n in checked
    )
    assert sizes == tuple(Decimal("0.075") for _ in range(6))


def test_successor_weak_pipeline() -> None:
    notionals = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=True,
        is_dominant=False,
    )
    cap, cap_dom = _caps(Decimal("1.5"))
    checked = enforce_level_caps(
        level_notionals=notionals,
        max_level_notional=cap,
        max_level_notional_dominant=cap_dom,
        is_successor=True,
        is_dominant=False,
    )
    assert checked == tuple(Decimal("5000") for _ in range(6))


def test_cap_rejection_cascade_precedes_conversion() -> None:
    notionals = assign_level_notionals(
        max_basket_notional=_MAX,
        grid_levels=6,
        gen2_size_multiplier=Decimal("1.5"),
        is_successor=True,
        is_dominant=True,
    )  # 7500 each
    converted = False
    with pytest.raises(ValueError):
        checked = enforce_level_caps(
            level_notionals=notionals,
            max_level_notional=Decimal("5000"),
            max_level_notional_dominant=Decimal("7000"),  # < 7500 -> reject
            is_successor=True,
            is_dominant=True,
        )
        # unreachable: conversion must not run after the reject
        converted = True
        for n in checked:
            convert_notional_to_size(
                notional=n, mark_price=Decimal("100000"), sz_decimals=5
            )
    assert converted is False
