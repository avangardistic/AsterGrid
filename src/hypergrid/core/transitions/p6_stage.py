"""P6-real: LEVEL ARMING / ORDER PLACEMENT (Phase 7h-4b-2, B3). Pure, clock-free.

``apply_p6`` runs the §5.2 S2->S8-mirrored sub-decisions over one pass:
  B3.1 CANCEL_SELECT   -> exhausted-traversal cancels for COMPLETED cycles (both groups)
  B3.2 ARMING_EVAL + SUBMISSION_EMIT -> §8 gate eval per INTENT_CREATED (emit if ARMED)
  B3.3 LADDER_ISSUANCE_BU/SL -> §5.2 step-8 ladders for ACTIVE cycles w/ captured ref
  B3.4 coupling        -> apply_pipeline_coupling on the post-issuance state

P6 EMITS CommandEvents (returned, never appended here - D11) and WRITES ST-04 only
(ladder rows + coupling); it NEVER writes ST-05 or ST-12 (A2/P12: the adapter advances
ST-05 via submit_order; WAITING re-evaluates next pass). Dangling inputs SKIP SILENTLY
(D15/STR-0063); ValueError only for malformed rows (ctors), dup identities (State ctor),
and B4 coupling violations.

It MUST NOT import ``core.state`` at runtime (State only for annotation;
``dataclasses.replace`` needs no class import) and MUST NOT import the log port (D11).
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from hypergrid.core.transitions.arm import evaluate_arm_gates
from hypergrid.core.transitions.arm_state import ArmOutcome
from hypergrid.core.transitions.execution_cancel import (
    CancelReasonCode,
    emit_cancel_command,
    select_exhausted_candidates,
)
from hypergrid.core.transitions.ladder_issuance import issue_fresh_ladder
from hypergrid.core.transitions.markers import StageReport
from hypergrid.core.transitions.pass_report_ext import STAGE_ORDER, SubDecisionRecord
from hypergrid.core.transitions.pipeline_coupling import apply_pipeline_coupling
from hypergrid.core.transitions.submission import emit_submission_command

if TYPE_CHECKING:
    from hypergrid.core.events import CommandEvent
    from hypergrid.core.state import State
    from hypergrid.core.transitions.level_state import LevelState

# Fixed kind order for the P6 StageReport notes (ASCII only, no RUF001 glyphs).
_KIND_ORDER = (
    "CANCEL_SELECT",
    "ARMING_EVAL",
    "SUBMISSION_EMIT",
    "LADDER_ISSUANCE_BU",
    "LADDER_ISSUANCE_SL",
)


def _level_key(lvl: LevelState) -> tuple[int, int, str, int]:
    """ST-04 canonical sort key (gen, cycle, direction, level)."""
    return (lvl.generation_id, lvl.cycle_id, lvl.direction, lvl.level_id)


def apply_p6(
    state: State,
) -> tuple[State, StageReport, tuple[SubDecisionRecord, ...], tuple[CommandEvent, ...]]:
    """Run P6 over one pass. Returns (state', report, sub_decisions, emitted)."""
    subs: list[SubDecisionRecord] = []
    emitted: list[CommandEvent] = []

    order_rows = state.st05_order_intents_and_outcomes or ()

    # --- B3.1 CANCEL_SELECT (COMPLETED cycles, both directions) ---
    cancel_by_cloid = {c.cloid: c for c in (state.p6_cancel_inputs or ())}
    for cyc in state.st03_cycle_states or ():
        if cyc.lifecycle != "COMPLETED":
            continue
        for direction in ("BU", "SL"):
            for cand in select_exhausted_candidates(
                order_rows, cyc.generation_id, cyc.cycle_id, direction
            ):
                cin = cancel_by_cloid.get(cand.cloid)
                if cin is None:  # D15 silent skip (no input yet)
                    continue
                emitted.append(
                    emit_cancel_command(
                        cloid=cin.cloid,
                        tif=cin.tif,
                        expires_after=cin.expires_after,
                        intent_log_seq=cin.intent_log_seq,
                    )
                )
                subs.append(
                    SubDecisionRecord(
                        "P6",
                        "CANCEL_SELECT",
                        cand.cloid,
                        "EMITTED",
                        (CancelReasonCode.EXHAUSTED_TRAVERSAL_CANCEL.value,),
                        notes=(
                            f"exhausted G{cyc.generation_id:02d}-C{cyc.cycle_id:02d}-"
                            f"{direction}: cancel {cand.cloid}"
                        ),
                    )
                )

    # --- B3.2 ARMING_EVAL + SUBMISSION_EMIT (INTENT_CREATED orders, cloid order) ---
    level_by_identity = {
        (lvl.generation_id, lvl.cycle_id, lvl.level_id, lvl.direction): lvl
        for lvl in (state.st04_level_pipeline_states or ())
    }
    arm_by_cloid = {a.cloid: a for a in (state.p6_arm_inputs or ())}
    for row in order_rows:
        if row.lifecycle != "INTENT_CREATED":
            continue
        lvl = level_by_identity.get(
            (
                row.intent.target_generation_id,
                row.intent.target_cycle_id,
                row.intent.target_level_id,
                row.intent.target_direction,
            )
        )
        if lvl is None:  # D15 join-miss (level may issue next pass)
            continue
        if lvl.is_protection_locked:  # B4.1 at the source
            continue
        if lvl.lifecycle not in (None, "IDLE"):  # resurrection/exclusivity guard
            continue
        ain = arm_by_cloid.get(row.cloid)
        if ain is None:  # D15 silent skip (no input yet)
            continue
        ev = evaluate_arm_gates(
            intent=row.intent.intent_tag,
            generation_disabled=ain.generation_disabled,
            book_depth_at_target=ain.book_depth_at_target,
            order_size=row.intent.requested_size,
            min_depth_multiple=ain.min_depth_multiple,
            distance_bps=ain.distance_bps,
            distance_band=ain.distance_band,
            min_order_size=ain.min_order_size,
            margin_available=ain.margin_available,
            margin_required=ain.margin_required,
            margin_buffer_mult=ain.margin_buffer_mult,
            exposure_caps_ok=ain.exposure_caps_ok,
            open_order_count=ain.open_order_count,
            open_order_cap=ain.open_order_cap,
            price_normalized_ok=ain.price_normalized_ok,
            size_normalized_ok=ain.size_normalized_ok,
            market_state=ain.market_state,
            net_expected_edge_bps=ain.net_expected_edge_bps,
            edge_floor_bps=ain.edge_floor_bps,
            policy=ain.policy,
            timeout_s=ain.timeout_s,
            decision=ain.decision,
            elapsed_s=ain.elapsed_s,
            webhook_error=ain.webhook_error,
        )
        outcome = ev.outcome.value
        codes = (ev.code.value,) if ev.code is not None else ()
        notes = f"{row.cloid}: {outcome}" + (
            f" {ev.code.value}" if ev.code is not None else ""
        )
        subs.append(
            SubDecisionRecord("P6", "ARMING_EVAL", row.cloid, outcome, codes, notes)
        )
        if ev.outcome == ArmOutcome.ARMED:
            cmd = emit_submission_command(
                order=row,
                tif=ain.tif,
                expires_after=ain.expires_after,
                intent_log_seq=ain.intent_log_seq,
            )
            emitted.append(cmd)
            subs.append(
                SubDecisionRecord(
                    "P6",
                    "SUBMISSION_EMIT",
                    row.cloid,
                    "EMITTED",
                    (),
                    notes=(
                        f"{row.cloid}: {cmd.action} tif={ain.tif} "
                        f"expires_after={ain.expires_after} seq={ain.intent_log_seq}"
                    ),
                )
            )

    # --- B3.3 LADDER_ISSUANCE_BU/SL (ACTIVE cycle + captured ref + no rows yet) ---
    ref_by_gc = {
        (r.generation_id, r.cycle_id): r for r in (state.st10_reference_prices or ())
    }
    cyc_by_gc = {
        (c.generation_id, c.cycle_id): c for c in (state.st03_cycle_states or ())
    }
    levels_present_gc = {
        (lvl.generation_id, lvl.cycle_id)
        for lvl in (state.st04_level_pipeline_states or ())
    }
    new_rows: list[LevelState] = []
    for iin in state.p6_issuance_inputs or ():
        gc = (iin.generation_id, iin.cycle_id)
        cycle_row = cyc_by_gc.get(gc)
        st10 = ref_by_gc.get(gc)
        if cycle_row is None or cycle_row.lifecycle != "ACTIVE" or st10 is None:
            continue  # D15 (cycle not ready / reference not captured)
        if gc in levels_present_gc:
            continue  # D15 (already issued)
        for group, is_dom, edge in (
            ("BU", iin.is_dominant_bu, iin.edge_clears_floor_bu),
            ("SL", iin.is_dominant_sl, iin.edge_clears_floor_sl),
        ):
            rows = issue_fresh_ladder(
                reference_price=st10.reference,
                direction=group,
                grid_levels=iin.grid_levels,
                step_bps=iin.step_bps,
                first_level_distance_bps=iin.first_level_distance_bps,
                is_dominant=is_dom,
                gen2_distance_multiplier=iin.gen2_distance_multiplier,
                weak_side_first_level_multiplier=iin.weak_side_first_level_multiplier,
                size_notional_usd=iin.size_notional_usd,
                edge_clears_floor=edge,
                current_generation_id=iin.generation_id,
                current_cycle_id=iin.cycle_id,
            )
            subject = f"G{iin.generation_id:02d}-C{iin.cycle_id:02d}-{group}"
            if rows:
                new_rows.extend(rows)
                subs.append(
                    SubDecisionRecord(
                        "P6",
                        f"LADDER_ISSUANCE_{group}",
                        subject,
                        "ISSUED",
                        (),
                        notes=f"{subject}: {len(rows)} levels",
                    )
                )
            else:
                subs.append(
                    SubDecisionRecord(
                        "P6",
                        f"LADDER_ISSUANCE_{group}",
                        subject,
                        "EMPTY",
                        (),
                        notes=f"{subject}: empty (edge below floor)",
                    )
                )
    if new_rows:
        combined = tuple(
            sorted(
                (state.st04_level_pipeline_states or ()) + tuple(new_rows),
                key=_level_key,
            )
        )
        # State ctor re-validates sorted + no-dups (dup identity raises; E2 pins).
        state = dataclasses.replace(state, st04_level_pipeline_states=combined)

    # --- B3.4 coupling on the post-issuance state (a raise is pass-atomic) ---
    state = apply_pipeline_coupling(state)

    sorted_subs = tuple(
        sorted(subs, key=lambda s: (STAGE_ORDER[s.stage], s.sub_kind, s.subject))
    )
    emitted_sorted = tuple(
        sorted(emitted, key=lambda c: (0 if c.action == "cancel" else 1, c.cloid))
    )
    report = _p6_report(sorted_subs)
    return state, report, sorted_subs, emitted_sorted


def _p6_report(subs: tuple[SubDecisionRecord, ...]) -> StageReport:
    """Build the P6 StageReport: status, first-seen code union, fixed-order notes."""
    if not subs:
        return StageReport("P6", "NO_OP", (), "P6: no sub-decisions")
    seen: list[str] = []
    seen_set: set[str] = set()
    for sub in subs:
        for code in sub.reason_codes:
            if code not in seen_set:
                seen_set.add(code)
                seen.append(code)
    counts = dict.fromkeys(_KIND_ORDER, 0)
    for sub in subs:
        counts[sub.sub_kind] += 1
    parts = [f"{counts[k]}x{k}" for k in _KIND_ORDER if counts[k]]
    return StageReport("P6", "APPLIED", tuple(seen), "P6: " + ", ".join(parts))


__all__ = ["apply_p6"]
