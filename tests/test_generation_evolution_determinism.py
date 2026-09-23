"""apply_evolution determinism + frozen guarantees (Phase 7e)."""

import dataclasses

import pytest

from hypergrid.core.fold import _empty_state
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import State
from hypergrid.core.transitions import (
    EvolutionCandidateWindow,
    GenerationState,
    ReasonCode,
    apply_evolution,
)
from hypergrid.core.transitions.markers import StageReport


def _rich() -> State:
    return dataclasses.replace(
        _empty_state(),
        st02_generation_states=(
            GenerationState(0, "ACTIVE"),
            GenerationState(2, "ACTIVE"),
        ),
        st16_evolution_candidate_windows=(
            EvolutionCandidateWindow(0, "SL", (1, 2), 2, True, True, True),
            EvolutionCandidateWindow(2, "BU", (1, 2), 2, True, True, True),
        ),
    )


def test_determinism_byte_identical() -> None:
    state = _rich()
    a, _ = apply_evolution(state, [])
    b, _ = apply_evolution(state, [])
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )


def test_returned_state_is_frozen() -> None:
    state, _ = apply_evolution(_rich(), [])
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.event_count = 9  # type: ignore[misc]


def test_report_is_frozen_and_codes_valid() -> None:
    _, report = apply_evolution(_rich(), [])
    assert isinstance(report, StageReport)
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.status = "X"  # type: ignore[misc]
    valid = {m.value for m in ReasonCode}
    assert all(code in valid for code in report.reason_codes)
