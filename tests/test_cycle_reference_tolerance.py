"""§5.4 / §5.4.1 reference capture + tolerance via apply_cycle (Phase 7f)."""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.fold import _empty_state
from hypergrid.core.serialization import canonical_dumps, canonical_loads
from hypergrid.core.state import State
from hypergrid.core.transitions import (
    CycleState,
    CycleTerminalMarkers,
    GenerationState,
    ReasonCode,
    StageReport,
    apply_cycle,
)

_RECON = ReasonCode.RECONCILIATION_REQUIRED.value


def _run(
    *,
    captured: Decimal | None,
    nominal: Decimal | None,
    tol: Decimal | None,
    derivation: str | None,
) -> tuple[State, StageReport]:
    marker = CycleTerminalMarkers(
        generation_id=0,
        cycle_id=0,
        terminal_event_verified=True,
        exhausted_side_pending_cancelled=True,
        authoritative_state_reconciled=True,
        non_overlap_passed=True,  # S4 via fallback; isolate S7
        ladder_gate_passed=True,
        captured_reference_price=captured,
        nominal_reference_price=nominal,
        reference_price_tolerance_bps=tol,
        reference_derivation=derivation,
        non_overlap_data=None,
    )
    state = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        st03_cycle_states=(CycleState(0, 0, "ACTIVE"),),
        cycle_terminal_markers=(marker,),
    )
    return apply_cycle(state, [])


def test_worked_example_within_tolerance_proceeds() -> None:
    # StepBps 10 -> tol 3.3 bps; nominal 100000 -> band +/- 33 USD.
    new, report = _run(
        captured=Decimal("100010"),
        nominal=Decimal("100000"),
        tol=Decimal("3.3"),
        derivation="TERMINAL_EXECUTION",
    )
    assert _RECON not in report.reason_codes
    assert "dev=" in report.notes  # deviation magnitude logged (STR-0097)
    rows = new.st10_reference_prices or ()
    assert [(r.generation_id, r.cycle_id) for r in rows] == [(0, 1)]
    assert rows[0].reference == Decimal("100010")
    assert rows[0].derivation == "TERMINAL_EXECUTION"
    # __decimal__ round-trips through canonical JSON.
    restored = canonical_loads(canonical_dumps(new.to_canonical_obj()))
    assert isinstance(restored, dict)


def test_worked_example_outside_tolerance_blocks() -> None:
    new, report = _run(
        captured=Decimal("100040"),  # dev 40 > 33 allowed
        nominal=Decimal("100000"),
        tol=Decimal("3.3"),
        derivation="TERMINAL_EXECUTION",
    )
    assert _RECON in report.reason_codes
    assert "TOL" in report.notes
    assert (new.st10_reference_prices or ()) == ()  # no reference written


def test_exactly_at_tolerance_proceeds() -> None:
    _, report = _run(
        captured=Decimal("100033"),  # dev 33 == allowed 33
        nominal=Decimal("100000"),
        tol=Decimal("3.3"),
        derivation="TERMINAL_EXECUTION",
    )
    assert _RECON not in report.reason_codes


def test_missing_nominal_blocks() -> None:
    _, report = _run(
        captured=Decimal("100010"),
        nominal=None,
        tol=Decimal("3.3"),
        derivation="TERMINAL_EXECUTION",
    )
    assert _RECON in report.reason_codes


def test_missing_captured_blocks() -> None:
    _, report = _run(
        captured=None,
        nominal=Decimal("100000"),
        tol=Decimal("3.3"),
        derivation="TERMINAL_EXECUTION",
    )
    assert _RECON in report.reason_codes


def test_missing_tolerance_blocks() -> None:
    _, report = _run(
        captured=Decimal("100010"),
        nominal=Decimal("100000"),
        tol=None,
        derivation="TERMINAL_EXECUTION",
    )
    assert _RECON in report.reason_codes


def test_missing_derivation_blocks() -> None:
    _, report = _run(
        captured=Decimal("100010"),
        nominal=Decimal("100000"),
        tol=Decimal("3.3"),
        derivation=None,
    )
    assert _RECON in report.reason_codes


def test_bad_derivation_raises_at_construction() -> None:
    with pytest.raises(ValueError):
        CycleTerminalMarkers(0, 0, reference_derivation="BOGUS")
