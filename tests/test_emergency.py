"""§9 emergency tolerance + four-way + skip legs (Phase 7h-3, E2)."""

from decimal import Decimal

import pytest

from astergrid.core.transitions import (
    EmergencyVerdict,
    compute_emergency_tolerance_bps,
    evaluate_emergency,
)


def _eval(**over: object):  # type: ignore[no-untyped-def]
    base: dict[str, object] = {
        "wait_bound_breached": True,
        "direction": "BU",
        "target_price": Decimal("100"),
        "tolerance_bps": Decimal("50"),
        "tolerance_leverage_in": Decimal("1"),
        "fillable": True,
        "best_exec_price": Decimal("100"),
        "maker_edge_ok": False,
        "taker_edge_ok": True,
        "reprice_would_justify": False,
        "remaining_size": Decimal("1"),
        "order_cloid": "c1",
        "order_lifecycle_now": "EMERGENCY",
        "level_identity": (0, 0, "BU", 1),
        "level_lifecycle_now": "EMERGENCY",
    }
    base.update(over)
    return evaluate_emergency(**base)  # type: ignore[arg-type]


# --------------------------- tolerance formula ---------------------------


def test_tolerance_vectors() -> None:
    assert compute_emergency_tolerance_bps(Decimal("1")) == Decimal("50")
    assert compute_emergency_tolerance_bps(Decimal("2")) == Decimal("25")
    assert compute_emergency_tolerance_bps(Decimal("3")) == Decimal("17")  # 16.67→17
    assert compute_emergency_tolerance_bps(Decimal("5")) == Decimal("10")
    assert compute_emergency_tolerance_bps(Decimal("10")) == Decimal("5")


def test_tolerance_invalid_leverage() -> None:
    with pytest.raises(ValueError):
        compute_emergency_tolerance_bps(Decimal("0"))
    with pytest.raises(ValueError):
        compute_emergency_tolerance_bps(Decimal("-1"))
    with pytest.raises(ValueError):
        compute_emergency_tolerance_bps(1)  # type: ignore[arg-type]


# --------------------------- guards + band ---------------------------


def test_breach_required() -> None:
    with pytest.raises(ValueError):
        _eval(wait_bound_breached=False)


def test_band_formula_and_endpoints() -> None:
    ev = _eval()  # tol = 50/10000 = 0.005 → [99.5, 100.5]
    assert ev.band_lo == Decimal("99.500")
    assert ev.band_hi == Decimal("100.500")
    # endpoints inclusive: best at lo/hi still IOC (taker+fillable).
    assert (
        _eval(best_exec_price=Decimal("99.5")).verdict
        == EmergencyVerdict.IOC_AT_BAND_EDGE
    )
    assert (
        _eval(best_exec_price=Decimal("100.5")).verdict
        == EmergencyVerdict.IOC_AT_BAND_EDGE
    )
    # just outside → not IOC (falls through to SKIP here).
    assert (
        _eval(best_exec_price=Decimal("99.4")).verdict
        != EmergencyVerdict.IOC_AT_BAND_EDGE
    )


# --------------------------- verdicts + overlaps ---------------------------


def test_each_verdict_reachable() -> None:
    assert _eval(maker_edge_ok=True).verdict == EmergencyVerdict.WAIT_EXTEND
    assert _eval().verdict == EmergencyVerdict.IOC_AT_BAND_EDGE
    assert (
        _eval(taker_edge_ok=False, reprice_would_justify=True).verdict
        == EmergencyVerdict.REPRICE_ALO
    )
    assert (
        _eval(taker_edge_ok=False, reprice_would_justify=False).verdict
        == EmergencyVerdict.LEVEL_SKIP
    )


def test_overlap_priority() -> None:
    # maker + taker → WAIT (maker wins).
    assert _eval(maker_edge_ok=True, taker_edge_ok=True).verdict == (
        EmergencyVerdict.WAIT_EXTEND
    )
    # taker + reprice → IOC (taker before reprice).
    assert (
        _eval(reprice_would_justify=True).verdict == EmergencyVerdict.IOC_AT_BAND_EDGE
    )


# --------------------------- IOC edge + STR-0187 ---------------------------


def test_ioc_price_is_side_edge() -> None:
    bu = _eval(direction="BU")
    assert bu.ioc_limit_price == bu.band_hi
    assert bu.ioc_size == Decimal("1")
    sl = _eval(direction="SL", level_identity=(0, 0, "SL", 1))
    assert sl.ioc_limit_price == sl.band_lo


def test_str0187_fillable_in_band_but_edge_fail_never_ioc() -> None:
    # fillable=True and in-band in the baseline, but taker edge fails → never IOC.
    ev = _eval(taker_edge_ok=False, reprice_would_justify=False)
    assert ev.verdict != EmergencyVerdict.IOC_AT_BAND_EDGE
    assert ev.ioc_limit_price is None


# --------------------------- skip legs ---------------------------


def test_skip_legs_emergency_order() -> None:
    ev = _eval(taker_edge_ok=False, order_lifecycle_now="EMERGENCY")
    assert ev.verdict == EmergencyVerdict.LEVEL_SKIP
    assert (ev.skip_order_from, ev.skip_order_to) == ("EMERGENCY", "SKIPPED")
    assert ev.skip_level_to == "LEVEL_SKIPPED"


def test_skip_legs_partial_order() -> None:
    ev = _eval(
        taker_edge_ok=False,
        order_lifecycle_now="PARTIALLY_FILLED",
        level_lifecycle_now="PARTIALLY_FILLED",
    )
    assert (ev.skip_order_from, ev.skip_order_to) == ("PARTIALLY_FILLED", "CANCELLED")


def test_skip_active_order_raises() -> None:
    with pytest.raises(ValueError):
        _eval(taker_edge_ok=False, order_lifecycle_now="ORDER_ACTIVE")


def test_skip_level_leg_honors_can_level_skip() -> None:
    with pytest.raises(ValueError):
        _eval(
            taker_edge_ok=False,
            order_lifecycle_now="EMERGENCY",
            level_lifecycle_now="FILLED",  # not skippable
        )


# --------------------------- provenance ---------------------------


def test_provenance_carried() -> None:
    ev = _eval(tolerance_bps=Decimal("17"), tolerance_leverage_in=Decimal("3"))
    assert ev.tolerance_bps == Decimal("17")
    assert ev.tolerance_leverage_in == Decimal("3")
    assert ev.tolerance_formula == "STR-0276/D-16"


def test_serialization_round_trips() -> None:
    from astergrid.core.serialization import canonical_dumps

    canonical_dumps(_eval().to_canonical_obj())
    canonical_dumps(_eval(taker_edge_ok=False).to_canonical_obj())  # SKIP legs present
