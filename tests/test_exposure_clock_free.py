"""§11.1 exposure functions are clock/randomness free (Phase 7g-3a)."""

import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from hypergrid.core.transitions import (
    LevelFillState,
    classify_exposure,
    compute_actual_exposure,
    compute_expected_exposure,
    compute_exposure_delta,
    is_acute,
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


def test_all_exposure_functions_clock_free() -> None:
    fills = (LevelFillState(0, 0, "BU", 1, Decimal("2.5"), "POSITION_VERIFIED"),)
    with _no_ambient():
        expected = compute_expected_exposure(level_fills=fills)
        actual = compute_actual_exposure(net_position=Decimal("1"))
        delta = compute_exposure_delta(
            expected_exposure=expected, actual_exposure=actual
        )
        classify_exposure(
            exposure_delta=delta,
            normal_tolerance=Decimal("1"),
            transient_tolerance=Decimal("3"),
        )
        is_acute(
            exposure_delta=delta,
            max_exposure_imbalance=Decimal("3"),
            margin_distance=Decimal("100"),
            emergency_tolerance=Decimal("5"),
        )
