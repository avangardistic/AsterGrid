"""§7.1 geometry determinism + no input mutation (Phase 7g-1)."""

from decimal import Decimal

from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.transitions import compute_ladder_geometry

_KW: dict[str, object] = {
    "reference_price": Decimal("100000"),
    "direction": "BU",
    "grid_levels": 6,
    "step_bps": Decimal("10"),
    "first_level_distance_bps": Decimal("20"),
    "is_successor": True,
    "is_dominant": False,
    "gen2_distance_multiplier": Decimal("2"),
    "weak_side_first_level_multiplier": Decimal("2"),
}


def test_byte_identical_across_calls() -> None:
    before = canonical_dumps({k: str(v) for k, v in _KW.items()})
    a = compute_ladder_geometry(**_KW)  # type: ignore[arg-type]
    b = compute_ladder_geometry(**_KW)  # type: ignore[arg-type]
    assert a == b
    assert canonical_dumps(list(a)) == canonical_dumps(list(b))
    # inputs are immutable value types; serialization is unchanged after the calls.
    assert canonical_dumps({k: str(v) for k, v in _KW.items()}) == before
