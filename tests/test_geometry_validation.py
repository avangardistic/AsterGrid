"""§7.1 geometry input validation (7e doctrine: malformed inputs raise)."""

from decimal import Decimal

import pytest

from hypergrid.core.transitions import compute_ladder_geometry

_DEFAULTS: dict[str, object] = {
    "reference_price": Decimal("100000"),
    "direction": "BU",
    "grid_levels": 6,
    "step_bps": Decimal("10"),
    "first_level_distance_bps": Decimal("20"),
    "is_successor": False,
    "is_dominant": False,
    "gen2_distance_multiplier": Decimal("2"),
    "weak_side_first_level_multiplier": Decimal("2"),
}


def _g(**over: object) -> tuple[Decimal, ...]:
    return compute_ladder_geometry(**{**_DEFAULTS, **over})  # type: ignore[arg-type]


def test_bad_direction() -> None:
    with pytest.raises(ValueError):
        _g(direction="XX")


def test_grid_levels_out_of_range() -> None:
    with pytest.raises(ValueError):
        _g(grid_levels=0)
    with pytest.raises(ValueError):
        _g(grid_levels=13)


def test_non_positive_step() -> None:
    with pytest.raises(ValueError):
        _g(step_bps=Decimal("0"))
    with pytest.raises(ValueError):
        _g(step_bps=Decimal("-1"))


def test_non_positive_first_distance() -> None:
    with pytest.raises(ValueError):
        _g(first_level_distance_bps=Decimal("0"))


def test_non_positive_multipliers() -> None:
    with pytest.raises(ValueError):
        _g(gen2_distance_multiplier=Decimal("0"))
    with pytest.raises(ValueError):
        _g(weak_side_first_level_multiplier=Decimal("-1"))


def test_non_positive_reference() -> None:
    with pytest.raises(ValueError):
        _g(reference_price=Decimal("0"))


def test_non_decimal_params_rejected() -> None:
    with pytest.raises(ValueError):
        _g(reference_price=100000)  # int, not Decimal
    with pytest.raises(ValueError):
        _g(step_bps=10.0)  # float, not Decimal
