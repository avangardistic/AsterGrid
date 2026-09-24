"""ST-04 LevelState: frozen, validated, canonical (Phase 7g-1)."""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.serialization import canonical_dumps
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
