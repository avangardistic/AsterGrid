"""§5.6 non-overlap N1/N2/N3 via apply_cycle (Phase 7f). Decimal-only, markers-set."""

import dataclasses
from decimal import Decimal

import pytest

from astergrid.core.fold import _empty_state
from astergrid.core.state import State
from astergrid.core.transitions import (
    CycleState,
    CycleTerminalMarkers,
    GenerationState,
    NonOverlapData,
    ReasonCode,
    StageReport,
    apply_cycle,
)

_RECON = ReasonCode.RECONCILIATION_REQUIRED.value


def _run(
    data: NonOverlapData | None, *, fallback: bool = True
) -> tuple[State, StageReport]:
    marker = CycleTerminalMarkers(
        generation_id=0,
        cycle_id=0,
        terminal_event_verified=True,
        exhausted_side_pending_cancelled=True,
        authoritative_state_reconciled=True,
        non_overlap_passed=fallback,
        ladder_gate_passed=True,
        captured_reference_price=Decimal("100010"),
        nominal_reference_price=Decimal("100000"),
        reference_price_tolerance_bps=Decimal("3.3"),
        reference_derivation="TERMINAL_EXECUTION",
        non_overlap_data=data,
    )
    state = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        st03_cycle_states=(CycleState(0, 0, "ACTIVE"),),
        cycle_terminal_markers=(marker,),
    )
    return apply_cycle(state, [])


def _data(
    *,
    old_ref: str,
    old_term: str,
    new_levels: tuple[str, ...],
    direction: str,
    live: tuple[str, ...] = (),
    step: str = "10",
    tick: str = "0.1",
) -> NonOverlapData:
    return NonOverlapData(
        old_reference_price=Decimal(old_ref),
        old_terminal_execution_price=Decimal(old_term),
        new_level_prices=tuple(Decimal(p) for p in new_levels),
        direction=direction,
        live_same_group_prices=tuple(Decimal(p) for p in live),
        step_bps=Decimal(step),
        tick_size=Decimal(tick),
    )


def test_pass_bu() -> None:
    data = _data(
        old_ref="99900",
        old_term="100000",
        new_levels=("100100", "100200"),
        direction="BU",
    )
    _, report = _run(data)
    assert _RECON not in report.reason_codes


def test_pass_sl() -> None:
    data = _data(
        old_ref="100100",
        old_term="100000",
        new_levels=("99900", "99800"),
        direction="SL",
    )
    _, report = _run(data)
    assert _RECON not in report.reason_codes


def test_fail_n1_non_monotonic() -> None:
    data = _data(
        old_ref="99900",
        old_term="100000",
        new_levels=("100200", "100100"),
        direction="BU",
    )
    _, report = _run(data)
    assert _RECON in report.reason_codes
    assert "N1" in report.notes


def test_fail_n1_equal_adjacent() -> None:
    data = _data(
        old_ref="99900",
        old_term="100000",
        new_levels=("100100", "100100"),
        direction="BU",
    )
    _, report = _run(data)
    assert _RECON in report.reason_codes
    assert "N1" in report.notes


def test_fail_n2_side() -> None:
    # BU L1 exactly at old terminal -> not strictly beyond.
    data = _data(
        old_ref="99900",
        old_term="100000",
        new_levels=("100000", "100100"),
        direction="BU",
    )
    _, report = _run(data)
    assert _RECON in report.reason_codes
    assert "N2" in report.notes


def test_fail_n2_interval_endpoint() -> None:
    # A new price exactly ON the [lo, hi] endpoint fails (inclusive interval).
    data = _data(
        old_ref="100050",
        old_term="100000",
        new_levels=("100050", "100100"),
        direction="BU",
    )
    _, report = _run(data)
    assert _RECON in report.reason_codes
    assert "N2" in report.notes


def test_fail_n3_separation() -> None:
    # tick=0.1, step=20, p_new=100100 -> eps = max(0.1, 0.1*20*100100/10000) ~ 20.02
    # live 100090 is only 10 away -> below eps -> N3 block.
    data = _data(
        old_ref="99900",
        old_term="100000",
        new_levels=("100100", "100200"),
        direction="BU",
        live=("100090",),
        step="20",
        tick="0.1",
    )
    _, report = _run(data)
    assert _RECON in report.reason_codes
    assert "N3" in report.notes


def test_pass_n3_boundary_inclusive() -> None:
    # tick=50 dominates eps; nearest live is exactly 50 away -> passes (>=).
    data = _data(
        old_ref="99900",
        old_term="100000",
        new_levels=("100100", "100200"),
        direction="BU",
        live=("100050",),
        step="1",
        tick="50",
    )
    _, report = _run(data)
    assert _RECON not in report.reason_codes


def test_pass_n3_empty_live_vacuous() -> None:
    data = _data(
        old_ref="99900",
        old_term="100000",
        new_levels=("100100", "100200"),
        direction="BU",
        live=(),
    )
    _, report = _run(data)
    assert _RECON not in report.reason_codes


def test_fallback_true_passes_false_blocks() -> None:
    _, ok = _run(None, fallback=True)
    assert _RECON not in ok.reason_codes
    _, bad = _run(None, fallback=False)
    assert _RECON in bad.reason_codes
    assert "N-fallback" in bad.notes


def test_malformed_non_overlap_data_raises() -> None:
    with pytest.raises(ValueError):  # bad direction
        _data(old_ref="1", old_term="1", new_levels=("2",), direction="XX")
    with pytest.raises(ValueError):  # empty new levels
        _data(old_ref="1", old_term="1", new_levels=(), direction="BU")
    with pytest.raises(ValueError):  # non-positive tick
        _data(old_ref="1", old_term="1", new_levels=("2",), direction="BU", tick="0")
