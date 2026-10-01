"""ST-04<->ST-05 pipeline coupling (Phase 7h-4b-2, B4). Pure, total-on-valid.

Reads ST-04 + ST-05; writes ST-04 ONLY (B4.3); raises on B4.2/B4.3 incoherence. The
gating DIRECTION is COINED (Item 5): ST-04 (the level/protection side) gates; ST-05
(the order pipeline) advances the level. No Strategy sentence states a direction; the
anchors are §6.1 L570 / STR-0131 (joint FILLED invariant), STR-0151/0152 (unlock
precedes arming), STR-0190/0191/0192 (LEVEL_SKIPPED first-class terminal, never
resurrected). If a contradicting sentence is found, that is narrow STOP S-2.

It MUST NOT import ``core.state`` at runtime (State only for annotation);
``dataclasses.replace`` needs no class import. Tuple order is PRESERVED (index-based
replace, the P0 precedent).
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hypergrid.core.state import State


def apply_pipeline_coupling(state: State) -> State:
    """Advance ST-04 rows from their matching ST-05 order (B4). Fail-closed on RECON.

    Either slot None -> return state unchanged (B4.4). Index ST-05 by the level
    identity (target_generation_id, target_cycle_id, target_level_id, target_direction).
    Per ST-04 row with a matching order:
      B4.2 skip-cap: LEVEL_SKIPPED level + INTENT_CREATED order -> ValueError
        ("RECONCILIATION_REQUIRED": resurrection attempt, STR-0190/0192).
      B4.3 PV advance: order POSITION_VERIFIED + level lifecycle None + unlocked ->
        write level lifecycle="POSITION_VERIFIED" (provisional order-side observation;
        P0's venue read overwrites it next pass; R10c-safe since unlocked). Locked
        level + POSITION_VERIFIED order -> ValueError ("RECONCILIATION_REQUIRED":
        locked implies unarmed yet filled).
      B4.4 independent otherwise (unchanged).
    """
    orders = state.st05_order_intents_and_outcomes
    levels = state.st04_level_pipeline_states
    if orders is None or levels is None:  # B4.4 short-circuit
        return state

    order_by_identity = {
        (
            o.intent.target_generation_id,
            o.intent.target_cycle_id,
            o.intent.target_level_id,
            o.intent.target_direction,
        ): o
        for o in orders
    }

    new_levels = list(levels)
    changed = False
    for i, lvl in enumerate(new_levels):
        order = order_by_identity.get(
            (lvl.generation_id, lvl.cycle_id, lvl.level_id, lvl.direction)
        )
        if order is None:
            continue
        if order.lifecycle == "INTENT_CREATED" and lvl.lifecycle == "LEVEL_SKIPPED":
            raise ValueError(
                "RECONCILIATION_REQUIRED: INTENT_CREATED order on a LEVEL_SKIPPED "
                f"level (resurrection): {lvl.generation_id}/{lvl.cycle_id}/"
                f"{lvl.direction}/{lvl.level_id}"
            )
        if order.lifecycle == "POSITION_VERIFIED":
            if lvl.is_protection_locked:
                raise ValueError(
                    "RECONCILIATION_REQUIRED: POSITION_VERIFIED order on a locked "
                    f"level: {lvl.generation_id}/{lvl.cycle_id}/{lvl.direction}/"
                    f"{lvl.level_id}"
                )
            if lvl.lifecycle is None:
                new_levels[i] = dataclasses.replace(lvl, lifecycle="POSITION_VERIFIED")
                changed = True
    if not changed:
        return state
    return dataclasses.replace(state, st04_level_pipeline_states=tuple(new_levels))


__all__ = ["apply_pipeline_coupling"]
