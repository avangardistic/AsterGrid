"""§7.1 successor geometry (G1+, all cycles — R2; direction-agnostic — R3)."""

from decimal import Decimal

from hypergrid.core.transitions import compute_ladder_geometry

_DEFAULTS: dict[str, object] = {
    "reference_price": Decimal("100000"),
    "direction": "BU",
    "grid_levels": 6,
    "step_bps": Decimal("10"),
    "first_level_distance_bps": Decimal("20"),
    "is_successor": True,
    "is_dominant": True,
    "gen2_distance_multiplier": Decimal("2"),
    "weak_side_first_level_multiplier": Decimal("2"),
}


def _g(**over: object) -> tuple[Decimal, ...]:
    return compute_ladder_geometry(**{**_DEFAULTS, **over})  # type: ignore[arg-type]


def test_successor_dominant_multiplier_2() -> None:
    # gen2_multiplier 2 * step 10 = 20 bps -> p1 = 100200 (same numbers as base).
    ladder = _g(is_dominant=True, gen2_distance_multiplier=Decimal("2"))
    assert ladder[0] == Decimal("100200")
    assert ladder[1] == Decimal("100300.2")
    assert all(ladder[i] < ladder[i + 1] for i in range(len(ladder) - 1))


def test_successor_dominant_multiplier_1_5_distinguishes() -> None:
    ladder = _g(is_dominant=True, gen2_distance_multiplier=Decimal("1.5"))
    assert ladder[0] == Decimal("100150")  # 1.5 * 10 = 15 bps


def test_successor_weak_side() -> None:
    # weak L1 distance = weak_multiplier(2) * step(10) = 20 bps; SL -> 99800.
    ladder = _g(direction="SL", is_dominant=False)
    assert ladder[0] == Decimal("99800")
    assert all(ladder[i] > ladder[i + 1] for i in range(len(ladder) - 1))


def test_base_vs_successor_differ() -> None:
    base = compute_ladder_geometry(
        **{**_DEFAULTS, "is_successor": False}  # type: ignore[arg-type]
    )
    successor = _g(is_dominant=True, gen2_distance_multiplier=Decimal("1.5"))
    assert base != successor  # base d1=20 vs dominant d1=15


def test_direction_independence_r3() -> None:
    ref = Decimal("100000")
    bu = _g(direction="BU", is_dominant=True)
    sl = _g(direction="SL", is_dominant=True)
    # R3: same distance rule, opposite side. Level 1 is exactly symmetric around
    # the reference (deeper levels compound multiplicatively per R1, so their
    # absolute distances are not additively mirrored — only the sign flips).
    assert bu[0] - ref == ref - sl[0]
    assert bu[0] > ref and sl[0] < ref
    # geometry is identical apart from the direction sign: |factor-1| matches at L1.
    assert bu[0] / ref - Decimal("1") == Decimal("1") - sl[0] / ref
