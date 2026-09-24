"""§7.3 sizing determinism + no input mutation (Phase 7g-2)."""

from decimal import Decimal

from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.transitions import (
    assign_level_notionals,
    convert_notional_to_size,
)

_KW: dict[str, object] = {
    "max_basket_notional": Decimal("30000"),
    "grid_levels": 7,
    "gen2_size_multiplier": Decimal("1.5"),
    "is_successor": True,
    "is_dominant": True,
}


def test_assign_byte_identical() -> None:
    before = canonical_dumps({k: str(v) for k, v in _KW.items()})
    a = assign_level_notionals(**_KW)  # type: ignore[arg-type]
    b = assign_level_notionals(**_KW)  # type: ignore[arg-type]
    assert a == b
    assert canonical_dumps(list(a)) == canonical_dumps(list(b))
    assert canonical_dumps({k: str(v) for k, v in _KW.items()}) == before


def test_convert_byte_identical() -> None:
    a = convert_notional_to_size(
        notional=Decimal("5000"), mark_price=Decimal("99999"), sz_decimals=5
    )
    b = convert_notional_to_size(
        notional=Decimal("5000"), mark_price=Decimal("99999"), sz_decimals=5
    )
    assert canonical_dumps([a]) == canonical_dumps([b])
