"""§7.1/§7.2 geometry + protection lock are clock/randomness free (Phase 7g-1)."""

import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from hypergrid.core.transitions import (
    LevelState,
    apply_protection_unlock,
    compute_ladder_geometry,
    is_protection_locked_initial,
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


def test_all_pure_functions_are_clock_free() -> None:
    level = LevelState(0, 0, "SL", 1, Decimal("99800"), True)
    with _no_ambient():
        ladder = compute_ladder_geometry(
            reference_price=Decimal("100000"),
            direction="BU",
            grid_levels=6,
            step_bps=Decimal("10"),
            first_level_distance_bps=Decimal("20"),
            is_successor=False,
            is_dominant=False,
            gen2_distance_multiplier=Decimal("2"),
            weak_side_first_level_multiplier=Decimal("2"),
        )
        locked = is_protection_locked_initial(
            is_successor=True, is_dominant=False, level_id=1
        )
        unlocked = apply_protection_unlock(level, next_level_filled=True)
    assert len(ladder) == 6
    assert locked is True
    assert unlocked.is_protection_locked is False
