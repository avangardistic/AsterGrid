"""ST-04 LevelState: frozen, validated, canonical (Phase 7g-1)."""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.serialization import canonical_dumps, canonical_loads
from hypergrid.core.transitions import LevelState


def _valid() -> LevelState:
    return LevelState(0, 0, "BU", 1, Decimal("100200"), False)


def test_frozen() -> None:
    level = _valid()
    with pytest.raises(dataclasses.FrozenInstanceError):
        level.level_id = 2  # type: ignore[misc]


def test_bad_direction() -> None:
    with pytest.raises(ValueError):
        LevelState(0, 0, "XX", 1, Decimal("100200"), False)


def test_out_of_range_ids() -> None:
    with pytest.raises(ValueError):
        LevelState(100, 0, "BU", 1, Decimal("1"), False)
    with pytest.raises(ValueError):
        LevelState(0, 100, "BU", 1, Decimal("1"), False)
    with pytest.raises(ValueError):
        LevelState(0, 0, "BU", 0, Decimal("1"), False)
    with pytest.raises(ValueError):
        LevelState(0, 0, "BU", 13, Decimal("1"), False)


def test_non_positive_price() -> None:
    with pytest.raises(ValueError):
        LevelState(0, 0, "BU", 1, Decimal("0"), False)


def test_non_decimal_price() -> None:
    with pytest.raises(ValueError):
        LevelState(0, 0, "BU", 1, 100200, False)  # type: ignore[arg-type]


def test_to_canonical_obj_serializes() -> None:
    canonical_dumps(_valid().to_canonical_obj())


def test_equal_instances_serialize_identically() -> None:
    a = _valid()
    b = _valid()
    assert a == b
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )


# ------------------------ Phase 7g-2: size_notional_usd ------------------------


def test_size_default_none_and_omitted() -> None:
    level = _valid()  # 7g-1 positional construction still valid
    assert level.size_notional_usd is None
    assert "size_notional_usd" not in level.to_canonical_obj()


def test_sizeless_state_golden() -> None:
    # canonical form of a size-less state is byte-identical to the 7g-1 golden.
    golden = (
        '{"cycle_id":0,"direction":"BU","generation_id":0,'
        '"is_protection_locked":false,"level_id":1,'
        '"target_price":{"__decimal__":"100200"}}'
    )
    assert canonical_dumps(_valid().to_canonical_obj()) == golden


def test_size_present_serializes_and_round_trips() -> None:
    level = LevelState(0, 0, "BU", 1, Decimal("100200"), False, Decimal("5000"))
    assert level.size_notional_usd == Decimal("5000")
    text = canonical_dumps(level.to_canonical_obj())
    assert '"size_notional_usd":{"__decimal__":"5000"}' in text
    restored = canonical_loads(text)
    assert isinstance(restored, dict)
    assert restored["size_notional_usd"] == Decimal("5000")


def test_size_validation() -> None:
    with pytest.raises(ValueError):
        LevelState(0, 0, "BU", 1, Decimal("100200"), False, Decimal("0"))
    with pytest.raises(ValueError):
        LevelState(0, 0, "BU", 1, Decimal("100200"), False, 5000)  # type: ignore[arg-type]
