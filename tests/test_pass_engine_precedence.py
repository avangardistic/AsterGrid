"""P3/P4 precedence: exhaustive bounded, determinism (Phase 7d).

Markers are set DIRECTLY on synthetic States — no envelope interpretation.
"""

import dataclasses
import itertools
from collections.abc import Iterable

from hypergrid.core.fold import _empty_state
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.transitions import (
    P3CandidateMarkers,
    P4CandidateMarkers,
    ReasonCode,
    apply_across_generation_precedence,
    apply_same_generation_precedence,
)

_CYCLE_LIMIT = ReasonCode.CYCLE_LIMIT_REACHED.value
_DISABLE_BEATS = ReasonCode.SAME_GEN_DISABLE_BEATS_EVOLUTION.value
_EVO_BEFORE_CYCLE = ReasonCode.ACROSS_GEN_EVOLUTION_BEFORE_CYCLE.value
_LOWER_FIRST = ReasonCode.ACROSS_GEN_LOWER_GEN_ID_FIRST.value


def _subsets(items: tuple[int, ...] | tuple[tuple[int, int], ...]) -> Iterable[tuple]:
    for r in range(len(items) + 1):
        yield from itertools.combinations(items, r)


# ----------------------------- P3 -----------------------------


def test_p3_none_markers_is_noop() -> None:
    state = _empty_state()
    new_state, report = apply_same_generation_precedence(state, [])
    assert report.status == "NO_OP"
    assert new_state.p3_decisions is None


def test_p3_exhaustive_bounded() -> None:
    gens = (0, 1)
    for disable in _subsets(gens):
        for evo in _subsets(gens):
            markers = P3CandidateMarkers(
                disable_candidates=disable, evolution_candidates=evo
            )
            state = dataclasses.replace(_empty_state(), p3_candidates=markers)
            new_state, report = apply_same_generation_precedence(state, [])
            assert report.status == "APPLIED"
            expected = tuple(sorted(set(evo) & set(disable)))
            assert new_state.p3_decisions == expected  # DISABLE wins
            if expected:
                assert _CYCLE_LIMIT in report.reason_codes
                assert _DISABLE_BEATS in report.reason_codes
            else:
                assert report.reason_codes == ()


# ----------------------------- P4 -----------------------------


def test_p4_none_markers_is_noop() -> None:
    state = _empty_state()
    new_state, report = apply_across_generation_precedence(state, [])
    assert report.status == "NO_OP"
    assert new_state.p4_decisions is None


def test_p4_exhaustive_bounded() -> None:
    gens = (0, 1)
    cycle_pool = ((0, 0), (0, 1), (1, 0), (1, 1))
    for evo in _subsets(gens):
        for cyc in _subsets(cycle_pool):
            markers = P4CandidateMarkers(evolution_candidates=evo, cycle_candidates=cyc)
            state = dataclasses.replace(_empty_state(), p4_candidates=markers)
            new_state, report = apply_across_generation_precedence(state, [])
            assert report.status == "APPLIED"
            decisions = new_state.p4_decisions
            assert decisions is not None

            evo_d = [d for d in decisions if d.transition == "EVOLUTION"]
            cyc_d = [d for d in decisions if d.transition == "CYCLE"]
            # All Evolutions before any Cycle.
            assert [d.transition for d in decisions] == (
                ["EVOLUTION"] * len(evo_d) + ["CYCLE"] * len(cyc_d)
            )
            # Lower GenerationID first among Evolutions.
            assert [d.generation_id for d in evo_d] == sorted(set(evo))
            # Cycles in lexicographic (GenID, CycleID) order.
            assert [(d.generation_id, d.cycle_id) for d in cyc_d] == sorted(set(cyc))
            for d in decisions:
                assert d.reason.value == _EVO_BEFORE_CYCLE
            if decisions:
                assert _EVO_BEFORE_CYCLE in report.reason_codes
            assert (_LOWER_FIRST in report.reason_codes) is (len(set(evo)) >= 2)


def test_precedence_determinism() -> None:
    p3 = P3CandidateMarkers(disable_candidates=(1,), evolution_candidates=(0, 1))
    p4 = P4CandidateMarkers(
        evolution_candidates=(1, 0), cycle_candidates=((1, 0), (0, 1))
    )
    state = dataclasses.replace(_empty_state(), p3_candidates=p3, p4_candidates=p4)
    a3, _ = apply_same_generation_precedence(state, [])
    b3, _ = apply_same_generation_precedence(state, [])
    a4, _ = apply_across_generation_precedence(state, [])
    b4, _ = apply_across_generation_precedence(state, [])
    assert canonical_dumps(a3.to_canonical_obj()) == canonical_dumps(
        b3.to_canonical_obj()
    )
    assert canonical_dumps(a4.to_canonical_obj()) == canonical_dumps(
        b4.to_canonical_obj()
    )
