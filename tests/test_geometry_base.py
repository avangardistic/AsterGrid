"""§7.1 base geometry (Generation 0, all cycles — R2) (Phase 7g-1)."""

from decimal import Decimal

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

_BASE_BU = tuple(
    Decimal(x)
    for x in (
        "100200",
        "100300.2",
        "100400.5002",
        "100500.9007002",
        "100601.4016009002",
        "100702.0030025011002",
    )
)
_BASE_SL = tuple(
    Decimal(x)
    for x in (
        "99800",
        "99700.2",
        "99600.4998",
        "99500.8993002",
        "99401.3984008998",
        "99301.9970024989002",
    )
)


def _g(**over: object) -> tuple[Decimal, ...]:
    return compute_ladder_geometry(**{**_DEFAULTS, **over})  # type: ignore[arg-type]


def test_base_bu_full_tuple() -> None:
    ladder = _g(direction="BU")
    assert ladder == _BASE_BU
    assert ladder[0] == Decimal("100200")  # exact
    assert ladder[1] == Decimal("100300.2")  # compounding (R1), NOT 100300.0


def test_base_sl_full_tuple() -> None:
    ladder = _g(direction="SL")
    assert ladder == _BASE_SL
    assert ladder[0] == Decimal("99800")
    assert ladder[1] == Decimal("99700.2")


def test_monotonicity() -> None:
    bu = _g(direction="BU")
    assert all(bu[i] < bu[i + 1] for i in range(len(bu) - 1))
    sl = _g(direction="SL")
    assert all(sl[i] > sl[i + 1] for i in range(len(sl) - 1))


def test_length_equals_grid_levels() -> None:
    assert len(_g(grid_levels=6)) == 6
    assert len(_g(grid_levels=1)) == 1
    assert len(_g(grid_levels=12)) == 12


def test_base_ignores_dominance() -> None:
    with_dom = _g(is_successor=False, is_dominant=True)
    without_dom = _g(is_successor=False, is_dominant=False)
    assert with_dom == without_dom
