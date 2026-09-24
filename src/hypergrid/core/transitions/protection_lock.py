"""§7.2 Protection Level Locking -> fillability-gated unlock (Phase 7g-1).

Separate module mirroring the §7.1/§7.2 split. Pure, total, clock-free. Runtime
imports: stdlib only (``dataclasses``); ``LevelState`` is imported ONLY under
``TYPE_CHECKING`` for annotations (``dataclasses.replace`` needs no runtime import).

§7.2 unlock condition (unchanged from GridEA): the next level fills -> the
protection level unlocks. Unlocking only makes the level ELIGIBLE to arm; arming
still passes the full §8 gate list (Fillability + Cost analyzers) — NONE of which
is implemented here (§8 is Phase 7h).

``next_level_filled`` is the pre-computed conjunction "the next level (k+1, same
direction) reached POSITION_VERIFIED". CITATION: §7.2 says "fills" and
§7.1/STR-0146 says POSITION_VERIFIED — identical by the §6.1 hard rule (LEVEL
FILLED <=> ORDER FILLED AND DELTA VERIFIED). Phase 7g-1 tests set it directly; a
real P0 populates it from envelopes in Phase 7h.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hypergrid.core.transitions.level_state import LevelState


def is_protection_locked_initial(
    *,
    is_successor: bool,
    is_dominant: bool,
    level_id: int,
) -> bool:
    """Initial §7.2 lock: only the successor weak side's Level 1 is LOCKED.

    locked <=> is_successor AND (NOT is_dominant) AND level_id == 1 (STR-0146,
    re-applied per Cycle ladder). The re-application rhythm lives with the ladder
    owner (the 7h arming caller), not here.
    """
    return is_successor and not is_dominant and level_id == 1


def apply_protection_unlock(
    level: LevelState,
    *,
    next_level_filled: bool,
) -> LevelState:
    """Unlock a LOCKED level once its next same-direction level is verified.

    Pure: returns a NEW LevelState only when it actually unlocks; otherwise returns
    the input unchanged. Unlocked-in / either -> unchanged; Locked + not filled ->
    unchanged; Locked + filled -> is_protection_locked=False.
    """
    if not level.is_protection_locked:
        return level
    if next_level_filled:
        return dataclasses.replace(level, is_protection_locked=False)
    return level
