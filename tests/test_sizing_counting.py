"""§7.3 D-14 counters + cap-value helpers (Phase 7g-2)."""

from decimal import Decimal

import pytest

from hypergrid.core.transitions import (
    CycleState,
    GenerationState,
    compute_max_cycle_notional,
    compute_max_generation_notional,
    compute_max_level_notional,
    compute_max_level_notional_dominant,
    count_active_cycles,
    count_active_generations,
)

_MAX = Decimal("30000")


def test_count_active_generations() -> None:
    assert count_active_generations(()) == 0
    assert count_active_generations((GenerationState(0, "ACTIVE"),)) == 1
    assert count_active_generations((GenerationState(0, "DISABLED_AT_CYCLE_99"),)) == 1
    assert (
        count_active_generations((GenerationState(0, "CLOSED_ONLY_AS_PART_OF_BASKET"),))
        == 0
    )
    mixed = (
        GenerationState(0, "ACTIVE"),
        GenerationState(1, "DISABLED_AT_CYCLE_99"),
        GenerationState(2, "CLOSED_ONLY_AS_PART_OF_BASKET"),
    )
    assert count_active_generations(mixed) == 2


def test_count_active_cycles_all_lifecycles_count() -> None:
    gens = (GenerationState(0, "ACTIVE"),)
    cycles = (
        CycleState(0, 0, "COMPLETED"),
        CycleState(0, 1, "ACTIVE"),
        CycleState(0, 2, "TERMINAL_PENDING"),
        CycleState(0, 3, "CREATED"),
    )
    assert count_active_cycles(cycles, gens) == 4
    assert count_active_cycles((), gens) == 0
    assert count_active_cycles(cycles, ()) == 0


def test_count_active_cycles_excludes_closed_generation() -> None:
    gens = (
        GenerationState(0, "ACTIVE"),
        GenerationState(1, "CLOSED_ONLY_AS_PART_OF_BASKET"),
    )
    cycles = (
        CycleState(0, 0, "ACTIVE"),
        CycleState(1, 0, "ACTIVE"),  # cycle of a CLOSED gen -> excluded
        CycleState(1, 1, "COMPLETED"),  # excluded
    )
    assert count_active_cycles(cycles, gens) == 1


def test_cap_value_helpers() -> None:
    assert compute_max_level_notional(
        max_basket_notional=_MAX, grid_levels=6
    ) == Decimal("5000")
    assert compute_max_level_notional_dominant(
        max_basket_notional=_MAX, grid_levels=6, gen2_size_multiplier=Decimal("1.5")
    ) == Decimal("7500")
    assert compute_max_cycle_notional(
        max_basket_notional=_MAX, active_cycle_count=2
    ) == Decimal("15000")
    assert compute_max_generation_notional(
        max_basket_notional=_MAX, active_generation_count=3
    ) == Decimal("10000")


def test_inclusive_boundary_divide_by_one() -> None:
    assert (
        compute_max_cycle_notional(max_basket_notional=_MAX, active_cycle_count=1)
        == _MAX
    )
    assert (
        compute_max_generation_notional(
            max_basket_notional=_MAX, active_generation_count=1
        )
        == _MAX
    )


def test_fail_closed_on_zero_cycle() -> None:
    with pytest.raises(
        ValueError,
        match="cannot compute MaxCycleNotional: active_cycle_count is 0",
    ):
        compute_max_cycle_notional(max_basket_notional=_MAX, active_cycle_count=0)


def test_fail_closed_on_zero_generation() -> None:
    with pytest.raises(
        ValueError,
        match="cannot compute MaxGenerationNotional: active_generation_count is 0",
    ):
        compute_max_generation_notional(
            max_basket_notional=_MAX, active_generation_count=0
        )


def test_validation() -> None:
    with pytest.raises(ValueError):  # negative max
        compute_max_level_notional(max_basket_notional=Decimal("-1"), grid_levels=6)
    with pytest.raises(ValueError):  # negative count
        compute_max_cycle_notional(max_basket_notional=_MAX, active_cycle_count=-1)
    with pytest.raises(ValueError):  # non-Decimal max
        compute_max_generation_notional(
            max_basket_notional=30000, active_generation_count=3
        )
    with pytest.raises(ValueError):  # bool count
        compute_max_cycle_notional(max_basket_notional=_MAX, active_cycle_count=True)
