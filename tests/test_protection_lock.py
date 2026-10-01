"""§7.2 protection lock: initial truth table + fillability-gated unlock (7g-1)."""

from decimal import Decimal

from astergrid.core.transitions import (
    LevelState,
    apply_protection_unlock,
    is_protection_locked_initial,
)


def test_initial_lock_truth_table() -> None:
    # base: never locked
    assert not is_protection_locked_initial(
        is_successor=False, is_dominant=False, level_id=1
    )
    assert not is_protection_locked_initial(
        is_successor=False, is_dominant=True, level_id=2
    )
    # successor dominant L1: not locked
    assert not is_protection_locked_initial(
        is_successor=True, is_dominant=True, level_id=1
    )
    # successor weak L1: LOCKED
    assert is_protection_locked_initial(
        is_successor=True, is_dominant=False, level_id=1
    )
    # successor weak L2: not locked (unlock trigger)
    assert not is_protection_locked_initial(
        is_successor=True, is_dominant=False, level_id=2
    )


def _locked() -> LevelState:
    return LevelState(0, 0, "SL", 1, Decimal("99800"), True)


def _unlocked() -> LevelState:
    return LevelState(0, 0, "SL", 1, Decimal("99800"), False)


def test_locked_not_filled_unchanged() -> None:
    level = _locked()
    result = apply_protection_unlock(level, next_level_filled=False)
    assert result is level  # unchanged (same object)


def test_locked_filled_unlocks_new_instance() -> None:
    level = _locked()
    result = apply_protection_unlock(level, next_level_filled=True)
    assert result is not level  # new instance
    assert result.is_protection_locked is False
    assert level.is_protection_locked is True  # input unmutated


def test_unlocked_either_unchanged() -> None:
    level = _unlocked()
    assert apply_protection_unlock(level, next_level_filled=True) is level
    assert apply_protection_unlock(level, next_level_filled=False) is level


def test_unlock_preserves_all_other_fields() -> None:
    level = LevelState(3, 7, "BU", 2, Decimal("100300.2"), True)
    result = apply_protection_unlock(level, next_level_filled=True)
    assert result.generation_id == 3
    assert result.cycle_id == 7
    assert result.direction == "BU"
    assert result.level_id == 2
    assert result.target_price == Decimal("100300.2")
    assert result.is_protection_locked is False
