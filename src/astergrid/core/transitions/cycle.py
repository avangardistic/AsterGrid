"""§5.2/§5.3/§5.4/§5.4.1/§5.6 Cycle transition (Phase 7f) — executed as stage P5.

``apply_cycle`` is pure, total, clock-free and deterministic. It reads ONLY the
state's cycle/generation/reference markers — NEVER an envelope or event field
(the Phase-7d DESIGN RULE stays in force; ``envelopes`` is counting-only). It is
threaded as stage P5 by ``run_pass`` (after the P4 composition, before the P6
stub), so §4.7's P4-before-P5 ordering holds by construction. The seven-stage
contract is preserved: the report is always ``"P5"`` — there is no ``P5_EXEC``.

Candidate source: ST-03 rows (snapshotted at entry, ascending lexicographic).
Rows created during a pass are NEVER visited in the same pass (no C->C+1 chaining).
A marker row without a matching ST-03 row is ignored; an ST-03 row without a
marker, or with ``terminal_event_verified`` False, is skipped silently. Per
Generation, at most ONE Cycle transition is attempted per pass (§4.7 P2 executable
form, mirroring 7e rule (8)); further same-Generation terminal candidates are
skipped with ``CYCLE_TRANSITION_IN_FLIGHT_LOCKED`` (reused P2 code).

Branch (no boolean "limit reached" marker exists): for candidate (G, C) with
``effective_cycle_limit`` (None ⟹ 99), C < limit runs the §5.2 standard steps
S1-S8; C ≥ limit runs the §5.3 disable steps D1-D6. Missing gate markers fail
closed with ``RECONCILIATION_REQUIRED``; missing reference config fails closed
(DECISION-009). The §5.4.1 tolerance READS the §14 bound value from the marker and
never recomputes the coefficient-times-StepBps formula (that coefficient literal
appears nowhere in core; formulas resolve once at config time, not in the loop).

DEFERRED to a later phase (documented, not done here): §5.4.1-at-Generation-fire
(evolution has no reference plumbing yet); the §5.2 exposure/Hedge/FREEZE bullet
and §13.3 freeze block (real P0/P1); wiring P4 CYCLE admissions to P5 execution;
P2 cycle-lock lifecycle/clearing (P5 neither reads nor clears P2 cycle locks);
window-GC and ineligible-set GC. A real P0 will populate the Cycle markers from
envelopes; ``apply_cycle`` never reads an envelope.
"""

from __future__ import annotations

import dataclasses
import itertools
from decimal import Decimal
from typing import TYPE_CHECKING

from astergrid.core.transitions.cycle_state import (
    CycleState,
    NonOverlapData,
    ReferencePriceRecord,
)
from astergrid.core.transitions.generation_state import GenerationState
from astergrid.core.transitions.markers import StageReport
from astergrid.core.transitions.reason_codes import ReasonCode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from astergrid.core.events import EventEnvelope
    from astergrid.core.state import State
    from astergrid.core.transitions.cycle_state import CycleTerminalMarkers

_DEFAULT_CYCLE_LIMIT = 99  # §3 hard default when the marker is None
_SKIP_LIFECYCLES = frozenset({"DISABLED_AT_CYCLE_99", "CLOSED_ONLY_AS_PART_OF_BASKET"})
_RECON = ReasonCode.RECONCILIATION_REQUIRED.value
_CYCLE_LOCK = ReasonCode.CYCLE_TRANSITION_IN_FLIGHT_LOCKED.value
_CYCLE_LIMIT = ReasonCode.CYCLE_LIMIT_REACHED.value


def _non_overlap(data: NonOverlapData) -> tuple[bool, str]:
    """§5.6 N1->N2->N3 (first failure names the check). Pure/Decimal-only."""
    prices = data.new_level_prices
    # N1: strict monotonicity in level index along the direction.
    pairs = itertools.pairwise(prices)
    if data.direction == "BU":
        monotonic = all(a < b for a, b in pairs)
    else:  # SL
        monotonic = all(a > b for a, b in pairs)
    if not monotonic:
        return (False, "N1")
    # N2: Level-1 strictly beyond the old terminal execution price, and no new
    # price inside the closed interval spanned by old reference and old terminal.
    old_terminal = data.old_terminal_execution_price
    lo = min(data.old_reference_price, old_terminal)
    hi = max(data.old_reference_price, old_terminal)
    level_1 = prices[0]
    if data.direction == "BU":
        if not (level_1 > old_terminal):
            return (False, "N2")
    elif not (level_1 < old_terminal):
        return (False, "N2")
    if any(lo <= price <= hi for price in prices):
        return (False, "N2")
    # N3 (STR-0361, p := p_new): minimum separation from still-live same-group.
    for p_new in prices:
        epsilon = max(data.tick_size, Decimal("0.1") * data.step_bps * p_new / 10000)
        for p_live in data.live_same_group_prices:
            if abs(p_new - p_live) < epsilon:
                return (False, "N3")
    return (True, "")


def _reference_verdict(marker: CycleTerminalMarkers) -> tuple[bool, str]:
    """§5.4 + §5.4.1 gate (check order a-e). Returns (ok, note-or-check-name)."""
    nominal = marker.nominal_reference_price
    captured = marker.captured_reference_price
    tolerance = marker.reference_price_tolerance_bps
    if marker.reference_derivation is None:  # (a) DECISION-009 explicitness
        return (False, "DERIV")
    if nominal is None or nominal <= 0:  # (b)
        return (False, "DERIV")
    if captured is None:  # (c)
        return (False, "DERIV")
    if tolerance is None or tolerance <= 0:  # (d) §14 bound value missing
        return (False, "DERIV")
    deviation = abs(captured - nominal)
    allowed = tolerance / 10000 * nominal  # bound READ, never recomputed
    deviation_bps = deviation / nominal * 10000
    if deviation > allowed:  # (e) inclusive <= passes
        return (False, f"TOL dev={deviation_bps}bps")
    return (True, f"dev={deviation_bps}bps")


def _cycle_key(row: CycleState) -> tuple[int, int]:
    return (row.generation_id, row.cycle_id)


def _ref_key(row: ReferencePriceRecord) -> tuple[int, int]:
    return (row.generation_id, row.cycle_id)


def apply_cycle(
    state: State,
    envelopes: Sequence[EventEnvelope],
) -> tuple[State, StageReport]:
    """Run the §5.2/§5.3 Cycle transitions over ST-03 candidates; return (state, P5)."""
    # `envelopes` is intentionally unread (DESIGN RULE); it exists for signature
    # stability. NO_OP pin: no terminal markers or no ST-03 rows ⟹ no change.
    markers_field = state.cycle_terminal_markers
    if markers_field is None or state.st03_cycle_states is None:
        return state, StageReport("P5", "NO_OP", (), "P5: no cycle transitions")

    limit = state.effective_cycle_limit
    effective_limit = _DEFAULT_CYCLE_LIMIT if limit is None else limit

    st03 = {(r.generation_id, r.cycle_id): r for r in state.st03_cycle_states}
    st10 = {
        (r.generation_id, r.cycle_id): r for r in (state.st10_reference_prices or ())
    }
    st02 = {g.generation_id: g for g in (state.st02_generation_states or ())}
    markers = {(m.generation_id, m.cycle_id): m for m in markers_field}
    dirty = {"st03": False, "st10": False, "st02": False}
    codes: list[str] = []
    notes: list[str] = []
    attempted: set[int] = set()

    def _set_terminal_pending(gid: int, cid: int) -> None:
        row = st03[(gid, cid)]
        if row.lifecycle != "TERMINAL_PENDING":
            st03[(gid, cid)] = dataclasses.replace(row, lifecycle="TERMINAL_PENDING")
            dirty["st03"] = True

    def _set_completed(gid: int, cid: int) -> None:
        row = st03[(gid, cid)]
        if row.lifecycle != "COMPLETED":
            st03[(gid, cid)] = dataclasses.replace(row, lifecycle="COMPLETED")
            dirty["st03"] = True

    def _ensure_successor(gid: int, cid: int) -> None:
        successor = (gid, cid + 1)
        if successor not in st03:
            st03[successor] = CycleState(gid, cid + 1, "ACTIVE")
            dirty["st03"] = True

    def _set_disabled(gid: int) -> None:
        existing = st02.get(gid)
        if existing is None or existing.lifecycle != "DISABLED_AT_CYCLE_99":
            st02[gid] = GenerationState(gid, "DISABLED_AT_CYCLE_99")
            dirty["st02"] = True

    def _do_reference(marker: CycleTerminalMarkers, gid: int, cid: int) -> bool:
        ok, note = _reference_verdict(marker)
        if not ok:
            codes.append(_RECON)
            notes.append(f"G{gid}C{cid}:{note}")
            return True  # blocked
        successor = (gid, cid + 1)
        captured = marker.captured_reference_price
        derivation = marker.reference_derivation
        if successor not in st10 and captured is not None and derivation is not None:
            st10[successor] = ReferencePriceRecord(gid, cid + 1, captured, derivation)
            dirty["st10"] = True
        notes.append(f"G{gid}C{cid}:{note}")
        return False

    def _do_ladder(marker: CycleTerminalMarkers, gid: int, cid: int) -> bool:
        if not marker.ladder_gate_passed:
            codes.append(_RECON)
            notes.append(f"G{gid}C{cid}:LADDER")
            return True
        return False

    def _standard(marker: CycleTerminalMarkers, gid: int, cid: int) -> None:
        _set_terminal_pending(gid, cid)  # S1
        if not marker.exhausted_side_pending_cancelled:  # S2
            codes.append(_RECON)
            notes.append(f"G{gid}C{cid}:S2")
            return
        if not marker.authoritative_state_reconciled:  # S3
            codes.append(_RECON)
            notes.append(f"G{gid}C{cid}:S3")
            return
        if marker.non_overlap_data is not None:  # S4
            ok, check = _non_overlap(marker.non_overlap_data)
            if not ok:
                codes.append(_RECON)
                notes.append(f"G{gid}C{cid}:{check}")
                return
        elif not marker.non_overlap_passed:
            codes.append(_RECON)
            notes.append(f"G{gid}C{cid}:N-fallback")
            return
        _set_completed(gid, cid)  # S5
        _ensure_successor(gid, cid)  # S6
        if _do_reference(marker, gid, cid):  # S7
            return
        if _do_ladder(marker, gid, cid):  # S8 (pure gate; no state write)
            return
        notes.append(f"G{gid}C{cid}->COMPLETED,C{cid + 1} ACTIVE")

    def _standard_tail(marker: CycleTerminalMarkers, gid: int, cid: int) -> None:
        successor = (gid, cid + 1)
        if successor in st03 and successor in st10:
            return  # fully done — silent (idempotence)
        if successor not in st03:
            st03[successor] = CycleState(gid, cid + 1, "ACTIVE")
            dirty["st03"] = True
        if _do_reference(marker, gid, cid):
            return
        if _do_ladder(marker, gid, cid):
            return
        notes.append(f"G{gid}C{cid}:resume-done")

    def _disable(marker: CycleTerminalMarkers, gid: int, cid: int) -> None:
        _set_terminal_pending(gid, cid)  # D1
        if not marker.all_progression_orders_cancelled:  # D2
            codes.append(_RECON)
            notes.append(f"G{gid}C{cid}:D2")
            return
        if not marker.authoritative_state_reconciled:  # D3
            codes.append(_RECON)
            notes.append(f"G{gid}C{cid}:D3")
            return
        _set_completed(gid, cid)  # D4
        _set_disabled(gid)  # D5
        codes.append(_CYCLE_LIMIT)
        notes.append(f"G{gid}C{cid}:DISABLED")

    def _disable_tail(gid: int, cid: int) -> None:
        _set_disabled(gid)  # D5 (D4 already COMPLETED)
        codes.append(_CYCLE_LIMIT)
        notes.append(f"G{gid}C{cid}:resume-disable")

    for gid, cid in sorted(st03.keys()):  # snapshot: new rows not revisited
        marker = markers.get((gid, cid))
        if marker is None:
            continue
        generation = st02.get(gid)
        if generation is not None and generation.lifecycle in _SKIP_LIFECYCLES:
            continue  # disabled/closed Generation — silent (§4.3/§5.3)
        row = st03[(gid, cid)]
        if row.lifecycle == "COMPLETED":  # resume / idempotence
            if cid < effective_limit:
                _standard_tail(marker, gid, cid)
            else:
                _disable_tail(gid, cid)
            continue
        if not marker.terminal_event_verified:
            continue  # silent
        if gid in attempted:  # §4.7 P2: one Cycle transition per Generation per pass
            codes.append(_CYCLE_LOCK)
            notes.append(f"G{gid}C{cid}:locked")
            continue
        attempted.add(gid)
        if cid < effective_limit:
            _standard(marker, gid, cid)
        else:
            _disable(marker, gid, cid)

    note = "; ".join(notes) if notes else "P5: no cycle transitions"
    changed = dirty["st03"] or dirty["st10"] or dirty["st02"]
    if not changed and not codes:
        return state, StageReport("P5", "NO_OP", (), note)
    if changed:
        st03_out = (
            tuple(sorted(st03.values(), key=_cycle_key))
            if dirty["st03"]
            else state.st03_cycle_states
        )
        st10_out = (
            tuple(sorted(st10.values(), key=_ref_key))
            if dirty["st10"]
            else state.st10_reference_prices
        )
        st02_out = (
            tuple(sorted(st02.values(), key=lambda g: g.generation_id))
            if dirty["st02"]
            else state.st02_generation_states
        )
        new_state = dataclasses.replace(
            state,
            st03_cycle_states=st03_out,
            st10_reference_prices=st10_out,
            st02_generation_states=st02_out,
        )
    else:
        new_state = state
    return new_state, StageReport("P5", "APPLIED", tuple(codes), note)
