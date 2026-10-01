"""§7.3 Step 3 convert_notional_to_size — R4 round-down + cap faithfulness."""

from decimal import Decimal

import pytest

from astergrid.core.transitions import convert_notional_to_size


def test_exact_no_rounding() -> None:
    size = convert_notional_to_size(
        notional=Decimal("5000"), mark_price=Decimal("100000"), sz_decimals=5
    )
    assert size == Decimal("0.05")


def test_non_exact_floors_down() -> None:
    # true 5000/99999 = 0.05000050...; floor sz5 = 0.05000; ceiling would be 0.05001.
    size = convert_notional_to_size(
        notional=Decimal("5000"), mark_price=Decimal("99999"), sz_decimals=5
    )
    assert size == Decimal("0.05000")
    assert size == Decimal("0.05")  # numerically


def test_sz_decimals_zero_floors_to_zero_is_legal() -> None:
    size = convert_notional_to_size(
        notional=Decimal("5000"), mark_price=Decimal("99999"), sz_decimals=0
    )
    assert size == Decimal("0")  # dust-to-zero is legal output (no raise)


def test_boundary_value_not_moved() -> None:
    on_boundary = convert_notional_to_size(
        notional=Decimal("5000"), mark_price=Decimal("100000"), sz_decimals=5
    )
    assert on_boundary == Decimal("0.05")
    # a value just above a boundary floors down to it.
    just_above = convert_notional_to_size(
        notional=Decimal("5000.1"), mark_price=Decimal("100000"), sz_decimals=5
    )
    assert just_above == Decimal("0.05")  # 0.050001 -> 0.05000


def test_cap_faithfulness_property_r4() -> None:
    # The money test: size * mark_price <= notional, always (would FAIL under ceiling).
    battery = [
        (Decimal("5000"), Decimal("99999"), 5),
        (Decimal("5000"), Decimal("100000"), 5),
        (Decimal("7500"), Decimal("99991"), 4),
        (Decimal("1234.56"), Decimal("88888"), 3),
        (Decimal("10000"), Decimal("3"), 8),
        (Decimal("999"), Decimal("100003"), 6),
    ]
    for notional, mark, sz in battery:
        size = convert_notional_to_size(
            notional=notional, mark_price=mark, sz_decimals=sz
        )
        assert size * mark <= notional


def test_min_notional_check_absent() -> None:
    # $1 notional at 100000 mark, sz5 -> tiny floored size; NO MinNotional raise.
    size = convert_notional_to_size(
        notional=Decimal("1"), mark_price=Decimal("100000"), sz_decimals=5
    )
    assert size == Decimal("0.00001")


def test_validation() -> None:
    with pytest.raises(ValueError):
        convert_notional_to_size(
            notional=Decimal("0"), mark_price=Decimal("100000"), sz_decimals=5
        )
    with pytest.raises(ValueError):
        convert_notional_to_size(
            notional=Decimal("5000"), mark_price=Decimal("0"), sz_decimals=5
        )
    with pytest.raises(ValueError):
        convert_notional_to_size(
            notional=5000, mark_price=Decimal("100000"), sz_decimals=5
        )
    with pytest.raises(ValueError):
        convert_notional_to_size(
            notional=Decimal("5000"), mark_price=Decimal("100000"), sz_decimals=-1
        )
    with pytest.raises(ValueError):
        convert_notional_to_size(
            notional=Decimal("5000"), mark_price=Decimal("100000"), sz_decimals=True
        )
