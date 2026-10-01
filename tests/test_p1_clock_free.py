"""Real P1 + every Part-A/B function are clock/randomness free (7g-3b)."""

import dataclasses
import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from astergrid.core.fold import _empty_state
from astergrid.core.transitions import (
    LevelFillState,
    P1ExposureMarkers,
    apply_p1,
    build_exposure_singletons,
    build_hedge_intent,
    classify_remainder_hedge_status,
    compute_q_min,
    compute_t_enter,
    compute_t_exit,
    hedge_execution_for,
    mirror_eligible,
    progression_permitted,
    round_to_zero,
)


@contextmanager
def _no_ambient() -> Iterator[None]:
    def boom(*_a: object, **_k: object) -> object:
        raise AssertionError("clock/randomness accessed")

    saved = (time.time, time.monotonic, random.random, os.urandom)
    time.time = boom  # type: ignore[assignment]
    time.monotonic = boom  # type: ignore[assignment]
    random.random = boom  # type: ignore[assignment]
    os.urandom = boom  # type: ignore[assignment]
    try:
        yield
    finally:
        time.time, time.monotonic, random.random, os.urandom = saved


def _markers() -> P1ExposureMarkers:
    return P1ExposureMarkers(
        level_fills=(
            LevelFillState(0, 0, "BU", 1, Decimal("2.0"), "POSITION_VERIFIED"),
        ),
        net_position=Decimal("0.5"),
        tau_acc=Decimal("0.00005"),
        min_notional_usd=Decimal("10"),
        mark_price=Decimal("50000"),
        max_exposure_imbalance=Decimal("3"),
        emergency_tolerance=Decimal("5"),
        margin_distance=Decimal("100"),
        normal_tolerance=Decimal("1"),
        transient_tolerance=Decimal("3"),
    )


def test_all_p1_functions_clock_free() -> None:
    state = dataclasses.replace(_empty_state(), p1_exposure_markers=_markers())
    with _no_ambient():
        apply_p1(state, [])
        q = compute_q_min(min_notional_usd=Decimal("10"), mark_price=Decimal("50000"))
        te = compute_t_enter(tau_acc=Decimal("0.00005"), q_min=q)
        tx = compute_t_exit(tau_acc=Decimal("0.00005"), q_min=q)
        round_to_zero(exposure_delta=Decimal("1.5"), t_exit=tx)
        progression_permitted(exposure_delta=Decimal("1.5"), t_enter=te)
        hedge_execution_for(acute=True)
        build_hedge_intent(delta_hat=Decimal("1.5"), acute=False)
        mirror_eligible(lifecycle="ACTIVE")
        classify_remainder_hedge_status(within_timeout=True, skipped=False)
        build_exposure_singletons(
            level_fills=(),
            net_position=Decimal("0"),
            normal_tolerance=Decimal("1"),
            transient_tolerance=Decimal("3"),
            max_exposure_imbalance=Decimal("3"),
            margin_distance=Decimal("100"),
            emergency_tolerance=Decimal("5"),
        )
