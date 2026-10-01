"""Phase-7e rule (1a): a CLOSED Generation with a window never evolves (Phase 7f).

Proof that Phase-7e option A was right: a window on CLOSED_ONLY_AS_PART_OF_BASKET
is constructible, and the transition skips it silently.
"""

import dataclasses

from hypergrid.core.fold import _empty_state
from hypergrid.core.transitions import (
    EvolutionCandidateWindow,
    GenerationState,
    apply_evolution,
)


def test_closed_generation_window_is_silent() -> None:
    state = dataclasses.replace(
        _empty_state(),
        st02_generation_states=(GenerationState(0, "CLOSED_ONLY_AS_PART_OF_BASKET"),),
        st16_evolution_candidate_windows=(
            EvolutionCandidateWindow(0, "SL", (1, 2), 2, True, True, True),
        ),
    )
    new, report = apply_evolution(state, [])
    assert report.status == "NO_OP"
    assert report.reason_codes == ()
    assert new is state
