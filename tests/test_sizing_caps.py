"""§7.3 Step 2 enforce_level_caps — reject, never clip (Phase 7g-2)."""

from decimal import Decimal

import pytest

from hypergrid.core.transitions import enforce_level_caps

_CAP = Decimal("5000")
_CAP_DOM = Decimal("7500")


def _enforce(notionals: tuple[Decimal, ...], **over: object) -> tuple[Decimal, ...]:
    kw: dict[str, object] = {
        "level_notionals": notionals,
        "max_level_notional": _CAP,
        "max_level_notional_dominant": _CAP_DOM,
        "is_successor": False,
        "is_dominant": False,
    }
    kw.update(over)
    return enforce_level_caps(**kw)  # type: ignore[arg-type]


def test_pass_through_base() -> None:
    n = tuple(Decimal("5000") for _ in range(6))
    assert _enforce(n) == n


def test_pass_through_successor_dominant() -> None:
    n = tuple(Decimal("7500") for _ in range(6))
    assert _enforce(n, is_successor=True, is_dominant=True) == n


def test_pass_through_successor_weak() -> None:
    n = tuple(Decimal("5000") for _ in range(6))
    assert _enforce(n, is_successor=True, is_dominant=False) == n


def test_reject_base_over_cap() -> None:
    with pytest.raises(ValueError):
        _enforce((Decimal("5001"),))


def test_reject_dominant_over_cap() -> None:
    with pytest.raises(ValueError):
        _enforce((Decimal("7501"),), is_successor=True, is_dominant=True)


def test_cap_selection_between_the_two() -> None:
    # 6000 is between base cap (5000) and dominant cap (7500):
    mid = (Decimal("6000"),)
    assert _enforce(mid, is_successor=True, is_dominant=True) == mid  # dominant ok
    with pytest.raises(ValueError):  # base rejects it
        _enforce(mid)


def test_boundary_exactly_at_cap_passes() -> None:
    assert _enforce((Decimal("5000"),)) == (Decimal("5000"),)


def test_validation() -> None:
    with pytest.raises(ValueError):  # empty
        _enforce(())
    with pytest.raises(ValueError):  # non-positive notional
        _enforce((Decimal("0"),))
    with pytest.raises(ValueError):  # negative cap
        _enforce((Decimal("1"),), max_level_notional=Decimal("-1"))
    with pytest.raises(ValueError):  # non-Decimal cap
        _enforce((Decimal("1"),), max_level_notional_dominant=7500)
