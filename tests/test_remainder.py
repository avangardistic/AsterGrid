"""§11.4 remainder quantities (Phase 7h-3, E2)."""

from decimal import Decimal

import pytest

from astergrid.core.transitions import track_remainder

_ID = (0, 0, "BU", 1)


def _r(requested: str, verified: str, price: str = "50000", identity=_ID):  # type: ignore[no-untyped-def]
    return track_remainder(
        requested_size=Decimal(requested),
        verified_filled_size=Decimal(verified),
        level_identity=identity,
        reference_price=Decimal(price),
    )


def test_full_fill() -> None:
    r = _r("2", "2")
    assert r.remaining_size == Decimal("0")
    assert r.is_fully_filled is True
    assert r.remaining_notional_usd == Decimal("0")


def test_partial_fill_exact_difference_and_notional() -> None:
    r = _r("2.5", "1.5", price="40000")
    assert r.remaining_size == Decimal("1.0")
    assert r.remaining_notional_usd == Decimal("40000.0")
    assert r.is_fully_filled is False


def test_zero_verified() -> None:
    r = _r("3", "0")
    assert r.remaining_size == Decimal("3")
    assert r.is_fully_filled is False


def test_identity_tuple_order_and_direction() -> None:
    r = _r("1", "0", identity=(2, 5, "SL", 12))
    assert r.level_identity == (2, 5, "SL", 12)
    with pytest.raises(ValueError):
        _r("1", "0", identity=(0, 0, "LONG", 1))


def test_validation_errors() -> None:
    with pytest.raises(ValueError):  # verified > requested
        _r("1", "2")
    with pytest.raises(ValueError):  # negative verified
        _r("1", "-1")
    with pytest.raises(ValueError):  # requested not > 0
        _r("0", "0")
    with pytest.raises(ValueError):  # reference_price not > 0
        _r("1", "0", price="0")
    with pytest.raises(ValueError):  # non-Decimal
        track_remainder(
            requested_size=1.0,  # type: ignore[arg-type]
            verified_filled_size=Decimal("0"),
            level_identity=_ID,
            reference_price=Decimal("50000"),
        )


def test_serialization_round_trips() -> None:
    from astergrid.core.serialization import canonical_dumps

    obj = _r("2", "1").to_canonical_obj()
    assert obj["level_identity"] == [0, 0, "BU", 1]
    canonical_dumps(obj)
