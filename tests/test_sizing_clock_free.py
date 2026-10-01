"""§7.3 sizing + Part-B helpers are clock/randomness free (Phase 7g-2)."""

import os
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from astergrid.core.transitions import (
    CycleState,
    GenerationState,
    assign_level_notionals,
    compute_max_cycle_notional,
    compute_max_generation_notional,
    compute_max_level_notional,
    compute_max_level_notional_dominant,
    convert_notional_to_size,
    count_active_cycles,
    count_active_generations,
    enforce_level_caps,
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


def test_all_sizing_functions_clock_free() -> None:
    m = Decimal("30000")
    with _no_ambient():
        notionals = assign_level_notionals(
            max_basket_notional=m,
            grid_levels=6,
            gen2_size_multiplier=Decimal("1.5"),
            is_successor=True,
            is_dominant=True,
        )
        enforce_level_caps(
            level_notionals=notionals,
            max_level_notional=Decimal("5000"),
            max_level_notional_dominant=Decimal("7500"),
            is_successor=True,
            is_dominant=True,
        )
        convert_notional_to_size(
            notional=Decimal("5000"), mark_price=Decimal("99999"), sz_decimals=5
        )
        compute_max_level_notional(max_basket_notional=m, grid_levels=6)
        compute_max_level_notional_dominant(
            max_basket_notional=m, grid_levels=6, gen2_size_multiplier=Decimal("1.5")
        )
        compute_max_cycle_notional(max_basket_notional=m, active_cycle_count=2)
        compute_max_generation_notional(
            max_basket_notional=m, active_generation_count=3
        )
        gens = (GenerationState(0, "ACTIVE"),)
        count_active_generations(gens)
        count_active_cycles((CycleState(0, 0, "ACTIVE"),), gens)
