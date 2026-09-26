"""§5.7 cycle-side scenarios (08/09/13-17/20) + structural cases (Phase 7f).

All markers set directly on synthetic States; Decimals string-constructed.
"""

import dataclasses
from decimal import Decimal

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import State
from hypergrid.core.transitions import (
    CycleState,
    CycleTerminalMarkers,
    EvolutionCandidateWindow,
    GenerationState,
    NonOverlapData,
    ReasonCode,
    ReferencePriceRecord,
    SuccessorLock,
    apply_cycle,
)

_RECON = ReasonCode.RECONCILIATION_REQUIRED.value
_LIMIT = ReasonCode.CYCLE_LIMIT_REACHED.value
_LOCK = ReasonCode.CYCLE_TRANSITION_IN_FLIGHT_LOCKED.value

_PASS_DATA = NonOverlapData(
    old_reference_price=Decimal("99900"),
    old_terminal_execution_price=Decimal("100000"),
    new_level_prices=(Decimal("100100"), Decimal("100200")),
    direction="BU",
    live_same_group_prices=(),
    step_bps=Decimal("10"),
    tick_size=Decimal("0.1"),
)


def _mk(gid: int, cid: int, **over: object) -> CycleTerminalMarkers:
    fields: dict[str, object] = {
        "terminal_event_verified": True,
        "exhausted_side_pending_cancelled": True,
        "authoritative_state_reconciled": True,
        "non_overlap_passed": True,
        "ladder_gate_passed": True,
        "captured_reference_price": Decimal("100010"),
        "nominal_reference_price": Decimal("100000"),
        "reference_price_tolerance_bps": Decimal("3.3"),
        "reference_derivation": "TERMINAL_EXECUTION",
        "all_progression_orders_cancelled": True,
    }
    fields.update(over)
    return CycleTerminalMarkers(gid, cid, **fields)  # type: ignore[arg-type]


def _state(
    *,
    st02: tuple[GenerationState, ...] | None = None,
    st03: tuple[CycleState, ...] | None = None,
    st15: tuple[SuccessorLock, ...] | None = None,
    st16: tuple[EvolutionCandidateWindow, ...] | None = None,
    markers: tuple[CycleTerminalMarkers, ...] | None = None,
    limit: int | None = None,
) -> State:
    return dataclasses.replace(
        _empty_state(),
        st02_generation_states=st02,
        st03_cycle_states=st03,
        st15_successor_locks=st15,
        st16_evolution_candidate_windows=st16,
        cycle_terminal_markers=markers,
        effective_cycle_limit=limit,
    )


def _clife(state: State, gid: int, cid: int) -> str | None:
    for r in state.st03_cycle_states or ():
        if (r.generation_id, r.cycle_id) == (gid, cid):
            return r.lifecycle
    return None


def _has_ref(state: State, gid: int, cid: int) -> bool:
    return (gid, cid) in {
        (r.generation_id, r.cycle_id) for r in (state.st10_reference_prices or ())
    }


def _glife(state: State, gid: int) -> str | None:
    for g in state.st02_generation_states or ():
        if g.generation_id == gid:
            return g.lifecycle
    return None


def _unchanged(before: State, after: State) -> bool:
    return canonical_dumps(before.to_canonical_obj()) == canonical_dumps(
        after.to_canonical_obj()
    )


# ------------------------------ scenarios ------------------------------


def test_scenario_08_standard_transition() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "ACTIVE"),),
        markers=(_mk(0, 0, non_overlap_data=_PASS_DATA),),
    )
    new, report = apply_cycle(state, [])
    assert report.status == "APPLIED"
    assert _RECON not in report.reason_codes
    assert _clife(new, 0, 0) == "COMPLETED"
    assert _clife(new, 0, 1) == "ACTIVE"
    assert _has_ref(new, 0, 1)
    assert _glife(new, 0) == "ACTIVE"  # no new Generation


def test_scenario_09_cancel_reconcile_path_true_proceeds() -> None:
    # Real cancel semantics arrive with ST-18 (Phase 7g+); 7f pins the true path.
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "ACTIVE"),),
        markers=(_mk(0, 0, non_overlap_data=_PASS_DATA),),
    )
    new, _ = apply_cycle(state, [])
    assert _clife(new, 0, 0) == "COMPLETED"
    assert _clife(new, 0, 1) == "ACTIVE"


def test_scenario_10_composition_evolution_and_cycle() -> None:
    window = EvolutionCandidateWindow(0, "SL", (1, 2), 2, True, True, True)
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "ACTIVE"),),
        st16=(window,),
        markers=(_mk(0, 0, non_overlap_data=_PASS_DATA),),
    )
    new, _ = run_pass(state, [])
    # P4 admitted the Evolution; P5 completed the parent Cycle — two events.
    assert _glife(new, 0) == "SUCCESSOR_CREATED"
    assert _glife(new, 1) == "CREATED"
    assert _clife(new, 0, 0) == "COMPLETED"
    assert _clife(new, 0, 1) == "ACTIVE"


def test_scenario_13_successor_created_still_cycles() -> None:
    state = _state(
        st02=(GenerationState(0, "SUCCESSOR_CREATED"),),
        st03=(CycleState(0, 50, "ACTIVE"),),
        st15=(SuccessorLock(0, True),),
        markers=(_mk(0, 50, non_overlap_data=_PASS_DATA),),
    )
    new, _ = apply_cycle(state, [])
    assert _clife(new, 0, 51) == "ACTIVE"
    assert _glife(new, 0) == "SUCCESSOR_CREATED"  # no re-evolution
    assert new.st15_successor_locks == (SuccessorLock(0, True),)  # unchanged
    assert new.st14_dominance_flags is None


def test_scenario_14_c98_creates_c99() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 98, "ACTIVE"),),
        markers=(_mk(0, 98, non_overlap_data=_PASS_DATA),),
    )
    new, _ = apply_cycle(state, [])
    assert _clife(new, 0, 98) == "COMPLETED"
    assert _clife(new, 0, 99) == "ACTIVE"


def test_scenario_15_c99_disables() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 99, "ACTIVE"),),
        markers=(_mk(0, 99),),
    )
    new, report = apply_cycle(state, [])
    assert _LIMIT in report.reason_codes
    assert _clife(new, 0, 99) == "COMPLETED"
    assert _glife(new, 0) == "DISABLED_AT_CYCLE_99"
    assert _clife(new, 0, 100) is None  # no Cycle 100


def test_scenario_16_disabled_generation_silent() -> None:
    state = _state(
        st02=(GenerationState(0, "DISABLED_AT_CYCLE_99"),),
        st03=(CycleState(0, 50, "ACTIVE"),),
        markers=(_mk(0, 50, non_overlap_data=_PASS_DATA),),
    )
    new, report = apply_cycle(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert _glife(new, 0) == "DISABLED_AT_CYCLE_99"  # open, not CLOSED
    assert _unchanged(state, new)


def test_scenario_17_disabled_generation_silent_again() -> None:
    state = _state(
        st02=(GenerationState(0, "DISABLED_AT_CYCLE_99"),),
        st03=(CycleState(0, 50, "ACTIVE"),),
        markers=(_mk(0, 50, non_overlap_data=_PASS_DATA),),
    )
    new, report = apply_cycle(state, [])
    assert report.status == "NO_OP"
    assert _unchanged(state, new)


def test_scenario_20_g99_c99_disables_no_cycle_100() -> None:
    state = _state(
        st02=(GenerationState(99, "ACTIVE"),),
        st03=(CycleState(99, 99, "ACTIVE"),),
        markers=(_mk(99, 99),),
    )
    new, report = apply_cycle(state, [])
    assert _LIMIT in report.reason_codes
    assert _glife(new, 99) == "DISABLED_AT_CYCLE_99"
    assert _clife(new, 99, 100) is None


# ------------------------------ structural ------------------------------


def test_lower_limit_disable_and_standard() -> None:
    disable = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 50, "ACTIVE"),),
        markers=(_mk(0, 50),),
        limit=50,
    )
    new, report = apply_cycle(disable, [])
    assert _LIMIT in report.reason_codes
    assert _glife(new, 0) == "DISABLED_AT_CYCLE_99"
    assert _clife(new, 0, 51) is None

    standard = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 49, "ACTIVE"),),
        markers=(_mk(0, 49, non_overlap_data=_PASS_DATA),),
        limit=50,
    )
    new2, _ = apply_cycle(standard, [])
    assert _clife(new2, 0, 50) == "ACTIVE"


def test_same_pass_same_generation_single_admission() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 5, "ACTIVE"), CycleState(0, 6, "ACTIVE")),
        markers=(
            _mk(0, 5, non_overlap_data=_PASS_DATA),
            _mk(0, 6, non_overlap_data=_PASS_DATA),
        ),
    )
    new, report = apply_cycle(state, [])
    assert _LOCK in report.reason_codes
    assert _clife(new, 0, 5) == "COMPLETED"
    assert _clife(new, 0, 7) is None  # C6 was skipped, never advanced


def test_same_pass_cross_generation_independent() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"), GenerationState(1, "ACTIVE")),
        st03=(CycleState(0, 5, "ACTIVE"), CycleState(1, 3, "ACTIVE")),
        markers=(
            _mk(0, 5, non_overlap_data=_PASS_DATA),
            _mk(1, 3, non_overlap_data=_PASS_DATA),
        ),
    )
    new, _ = apply_cycle(state, [])
    assert _clife(new, 0, 6) == "ACTIVE"
    assert _clife(new, 1, 4) == "ACTIVE"


def test_no_chaining_within_a_pass() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 50, "ACTIVE"),),
        markers=(_mk(0, 50, non_overlap_data=_PASS_DATA),),
    )
    new, _ = apply_cycle(state, [])
    assert _clife(new, 0, 51) == "ACTIVE"
    assert _clife(new, 0, 52) is None  # C51 not processed in the same pass


def test_resume_after_s4_block() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "ACTIVE"),),
        markers=(_mk(0, 0, non_overlap_passed=False),),  # no data => fallback False
    )
    blocked, r1 = apply_cycle(state, [])
    assert _RECON in r1.reason_codes
    assert _clife(blocked, 0, 0) == "TERMINAL_PENDING"
    assert _clife(blocked, 0, 1) is None
    fixed = dataclasses.replace(
        blocked, cycle_terminal_markers=(_mk(0, 0, non_overlap_data=_PASS_DATA),)
    )
    done, r2 = apply_cycle(fixed, [])
    assert _RECON not in r2.reason_codes
    assert _clife(done, 0, 0) == "COMPLETED"
    assert _clife(done, 0, 1) == "ACTIVE"
    assert _has_ref(done, 0, 1)


def test_resume_after_s7_block_writes_reference_once() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "ACTIVE"),),
        markers=(
            _mk(
                0,
                0,
                non_overlap_data=_PASS_DATA,
                captured_reference_price=Decimal("100040"),
            ),
        ),
    )
    blocked, r1 = apply_cycle(state, [])
    assert _RECON in r1.reason_codes
    assert _clife(blocked, 0, 0) == "COMPLETED"  # S5/S6 done before the S7 block
    assert _clife(blocked, 0, 1) == "ACTIVE"
    assert not _has_ref(blocked, 0, 1)
    fixed = dataclasses.replace(
        blocked, cycle_terminal_markers=(_mk(0, 0, non_overlap_data=_PASS_DATA),)
    )
    done, _ = apply_cycle(fixed, [])
    refs = [(r.generation_id, r.cycle_id) for r in (done.st10_reference_prices or ())]
    assert refs == [(0, 1)]  # written exactly once


def test_idempotence_completed_cycle() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "COMPLETED"), CycleState(0, 1, "ACTIVE")),
        markers=(_mk(0, 0, non_overlap_data=_PASS_DATA),),
    )
    state = dataclasses.replace(
        state,
        st10_reference_prices=(
            ReferencePriceRecord(0, 1, Decimal("100010"), "TERMINAL_EXECUTION"),
        ),
    )
    new, report = apply_cycle(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert _unchanged(state, new)


def test_s2_block_keeps_terminal_pending() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "ACTIVE"),),
        markers=(_mk(0, 0, exhausted_side_pending_cancelled=False),),
    )
    new, report = apply_cycle(state, [])
    assert _RECON in report.reason_codes
    assert _clife(new, 0, 0) == "TERMINAL_PENDING"


def test_s3_block_keeps_terminal_pending() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "ACTIVE"),),
        markers=(_mk(0, 0, authoritative_state_reconciled=False),),
    )
    new, report = apply_cycle(state, [])
    assert _RECON in report.reason_codes
    assert _clife(new, 0, 0) == "TERMINAL_PENDING"


def test_s8_block_keeps_completed_plus_active() -> None:
    state = _state(
        st02=(GenerationState(0, "ACTIVE"),),
        st03=(CycleState(0, 0, "ACTIVE"),),
        markers=(_mk(0, 0, non_overlap_data=_PASS_DATA, ladder_gate_passed=False),),
    )
    new, report = apply_cycle(state, [])
    assert _RECON in report.reason_codes
    assert _clife(new, 0, 0) == "COMPLETED"
    assert _clife(new, 0, 1) == "ACTIVE"
    assert _has_ref(new, 0, 1)  # S7 wrote the reference before the S8 gate
