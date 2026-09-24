"""State object: frozen, validated, canonical-serializable (Phase 7c)."""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.events import GENESIS_PREV_HASH
from hypergrid.core.fold import _empty_state
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import _EVENT_KINDS, State
from hypergrid.core.transitions import (
    CycleState,
    CycleTerminalMarkers,
    DominanceFlag,
    EvolutionCandidateWindow,
    GenerationState,
    LevelState,
    ReferencePriceRecord,
    SuccessorLock,
)

_FULL_COUNTS = tuple(sorted((kind, 0) for kind in _EVENT_KINDS))


def _valid_state() -> State:
    return State(
        log_sequence=0,
        head_hash="a" * 64,
        event_count=1,
        per_kind_count=_FULL_COUNTS,
    )


def test_state_is_frozen() -> None:
    state = _valid_state()
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.event_count = 5


def test_state_has_23_domain_placeholders() -> None:
    domain = [f for f in dataclasses.fields(State) if f.name.startswith("st")]
    assert len(domain) == 23


def test_to_canonical_obj_passes_canonical_dumps() -> None:
    # canonical_dumps raises on None/float, so a clean serialize proves the output
    # contains no None/float at any depth.
    canonical_dumps(_valid_state().to_canonical_obj())
    canonical_dumps(_empty_state().to_canonical_obj())


def test_identical_states_equal_and_serialize_identically() -> None:
    a = _valid_state()
    b = _valid_state()
    assert a == b
    assert canonical_dumps(a.to_canonical_obj()) == canonical_dumps(
        b.to_canonical_obj()
    )


def test_bad_per_kind_count_rejected() -> None:
    with pytest.raises(ValueError, match="per_kind_count"):
        State(
            log_sequence=0,
            head_hash="a" * 64,
            event_count=1,
            per_kind_count=(("intent", 1),),  # incomplete
        )
    unsorted = tuple(reversed(_FULL_COUNTS))
    with pytest.raises(ValueError, match="per_kind_count"):
        State(
            log_sequence=0,
            head_hash="a" * 64,
            event_count=1,
            per_kind_count=unsorted,
        )


def test_bad_head_hash_rejected() -> None:
    with pytest.raises(ValueError, match="head_hash"):
        State(
            log_sequence=0,
            head_hash="xyz",
            event_count=1,
            per_kind_count=_FULL_COUNTS,
        )


def test_empty_state_properties() -> None:
    state = _empty_state()
    assert state.event_count == 0
    assert state.head_hash == GENESIS_PREV_HASH
    assert state.log_sequence is None
    assert all(count == 0 for _, count in state.per_kind_count)
    assert len(state.per_kind_count) == 10
    for f in dataclasses.fields(State):
        if f.name.startswith("st"):
            assert getattr(state, f.name) is None
    # empty log => is_empty True, log_sequence omitted
    obj = state.to_canonical_obj()
    assert obj["is_empty"] is True
    assert "log_sequence" not in obj


# ------------------------ Phase 7e: typed ST-02/14/15/16 ------------------------


def test_typed_generation_fields_default_none() -> None:
    s = _valid_state()
    assert s.st02_generation_states is None
    assert s.st14_dominance_flags is None
    assert s.st15_successor_locks is None
    assert s.st16_evolution_candidate_windows is None
    assert s.effective_generation_limit is None


def test_typed_generation_fields_serialize_cleanly() -> None:
    s = dataclasses.replace(
        _valid_state(),
        st02_generation_states=(GenerationState(0, "ACTIVE"),),
        st14_dominance_flags=(DominanceFlag(1, "BU"),),
        st15_successor_locks=(SuccessorLock(0, True),),
        st16_evolution_candidate_windows=(
            EvolutionCandidateWindow(0, "SL", (1, 2), 2, True, True, True),
        ),
        effective_generation_limit=99,
    )
    canonical_dumps(s.to_canonical_obj())  # no None/float at any depth
    obj = s.to_canonical_obj()
    assert obj["effective_generation_limit"] == 99
    assert obj["st02_generation_states"] == [
        {"generation_id": 0, "lifecycle": "ACTIVE"}
    ]


def test_generation_ordering_invariants_rejected() -> None:
    with pytest.raises(ValueError, match="sorted"):
        dataclasses.replace(
            _valid_state(),
            st02_generation_states=(
                GenerationState(1, "ACTIVE"),
                GenerationState(0, "ACTIVE"),
            ),
        )
    with pytest.raises(ValueError, match="sorted"):
        dataclasses.replace(
            _valid_state(),
            st15_successor_locks=(SuccessorLock(0, True), SuccessorLock(0, True)),
        )


def test_pending_generation_cannot_be_locked() -> None:
    with pytest.raises(ValueError, match="locked"):
        dataclasses.replace(
            _valid_state(),
            st02_generation_states=(GenerationState(0, "EVOLUTION_PENDING"),),
            st15_successor_locks=(SuccessorLock(0, True),),
        )


def test_lifecycle_membership_validated() -> None:
    with pytest.raises(ValueError):
        GenerationState(0, "FROZEN")  # overlay, not a lifecycle


def test_window_coherence_rejected() -> None:
    with pytest.raises(ValueError):  # unsorted levels
        EvolutionCandidateWindow(0, "SL", (2, 1), None, False, False, True)
    with pytest.raises(ValueError):  # return without traversal
        EvolutionCandidateWindow(0, "SL", (), 2, False, False, True)
    with pytest.raises(ValueError):  # verified without return
        EvolutionCandidateWindow(0, "SL", (1, 2), None, True, False, True)
    with pytest.raises(ValueError):  # held without verified
        EvolutionCandidateWindow(0, "SL", (1, 2), 2, False, True, True)
    with pytest.raises(ValueError):  # bad group
        EvolutionCandidateWindow(0, "XX", (1, 2), None, False, False, True)


# ------------------------ Phase 7f: typed ST-03/10 + markers --------------------


def test_typed_cycle_fields_default_none() -> None:
    s = _valid_state()
    assert s.st03_cycle_states is None
    assert s.st10_reference_prices is None
    assert s.effective_cycle_limit is None
    assert s.current_cycle_id_by_generation is None
    assert s.p3_ineligible_cycles is None
    assert s.cycle_terminal_markers is None


def test_typed_cycle_fields_serialize_cleanly() -> None:
    s = dataclasses.replace(
        _valid_state(),
        st03_cycle_states=(CycleState(0, 0, "ACTIVE"),),
        st10_reference_prices=(
            ReferencePriceRecord(0, 1, Decimal("100000"), "TERMINAL_EXECUTION"),
        ),
        effective_cycle_limit=99,
        current_cycle_id_by_generation=((0, 3),),
        p3_ineligible_cycles=((0, 3),),
        cycle_terminal_markers=(CycleTerminalMarkers(0, 0),),
    )
    canonical_dumps(s.to_canonical_obj())  # no None/float at any depth
    obj = s.to_canonical_obj()
    assert obj["effective_cycle_limit"] == 99
    assert obj["current_cycle_id_by_generation"] == [[0, 3]]
    assert obj["st03_cycle_states"] == [
        {"generation_id": 0, "cycle_id": 0, "lifecycle": "ACTIVE"}
    ]


def test_cycle_ordering_invariants_rejected() -> None:
    with pytest.raises(ValueError, match="sorted"):
        dataclasses.replace(
            _valid_state(),
            st03_cycle_states=(CycleState(0, 1, "ACTIVE"), CycleState(0, 0, "ACTIVE")),
        )
    with pytest.raises(ValueError, match="sorted"):
        dataclasses.replace(_valid_state(), p3_ineligible_cycles=((0, 1), (0, 1)))
    with pytest.raises(ValueError, match="sorted"):
        dataclasses.replace(
            _valid_state(),
            current_cycle_id_by_generation=((1, 0), (0, 0)),
        )


def test_cycle_limit_range_and_bool_rejected() -> None:
    with pytest.raises(ValueError, match=r"0\.\.99"):
        dataclasses.replace(_valid_state(), effective_cycle_limit=100)
    with pytest.raises(ValueError, match="int"):
        dataclasses.replace(_valid_state(), effective_cycle_limit=True)


def test_cycle_id_out_of_range_rejected() -> None:
    with pytest.raises(ValueError):
        CycleState(0, 100, "ACTIVE")
    with pytest.raises(ValueError):
        dataclasses.replace(_valid_state(), p3_ineligible_cycles=((0, 100),))


def test_bad_cycle_strings_rejected() -> None:
    with pytest.raises(ValueError):  # bad lifecycle
        CycleState(0, 0, "FROZEN")
    with pytest.raises(ValueError):  # bad derivation
        ReferencePriceRecord(0, 1, Decimal("1"), "BOGUS")
    with pytest.raises(ValueError):  # reference must be Decimal, > 0
        ReferencePriceRecord(0, 1, Decimal("0"), "TERMINAL_MID")


# ------------------------ Phase 7g-1: typed ST-04 ------------------------


def test_st04_defaults_none() -> None:
    assert _valid_state().st04_level_pipeline_states is None


def test_st04_ordering_invariant_rejected() -> None:
    with pytest.raises(ValueError, match="sorted"):
        dataclasses.replace(
            _valid_state(),
            st04_level_pipeline_states=(
                LevelState(0, 0, "BU", 2, Decimal("100300.2"), False),
                LevelState(0, 0, "BU", 1, Decimal("100200"), False),
            ),
        )
    with pytest.raises(ValueError, match="sorted"):  # duplicate quadruple
        dataclasses.replace(
            _valid_state(),
            st04_level_pipeline_states=(
                LevelState(0, 0, "BU", 1, Decimal("100200"), False),
                LevelState(0, 0, "BU", 1, Decimal("100200"), False),
            ),
        )


def test_st04_bu_before_sl_ordering_accepted() -> None:
    # "BU" < "SL" lexicographically — this order is valid.
    dataclasses.replace(
        _valid_state(),
        st04_level_pipeline_states=(
            LevelState(0, 0, "BU", 1, Decimal("100200"), False),
            LevelState(0, 0, "SL", 1, Decimal("99800"), True),
        ),
    )


def test_st04_with_size_serializes_and_duplicate_identity_rejected() -> None:
    state = dataclasses.replace(
        _valid_state(),
        st04_level_pipeline_states=(
            LevelState(0, 0, "BU", 1, Decimal("100200"), False, Decimal("5000")),
            LevelState(0, 0, "BU", 2, Decimal("100300.2"), False, Decimal("5000")),
        ),
    )
    canonical_dumps(state.to_canonical_obj())  # no None/float at any depth
    # Rows with the SAME identity quadruple but different size are still duplicates.
    with pytest.raises(ValueError, match="sorted"):
        dataclasses.replace(
            _valid_state(),
            st04_level_pipeline_states=(
                LevelState(0, 0, "BU", 1, Decimal("100200"), False, Decimal("5000")),
                LevelState(0, 0, "BU", 1, Decimal("100200"), False, Decimal("7500")),
            ),
        )


def test_fully_populated_7g1_state_serializes() -> None:
    state = dataclasses.replace(
        _valid_state(),
        st03_cycle_states=(CycleState(0, 0, "ACTIVE"),),
        st04_level_pipeline_states=(
            LevelState(0, 0, "BU", 1, Decimal("100200"), False),
            LevelState(0, 0, "SL", 1, Decimal("99800"), True),
        ),
        st10_reference_prices=(
            ReferencePriceRecord(0, 1, Decimal("100000"), "TERMINAL_EXECUTION"),
        ),
    )
    canonical_dumps(state.to_canonical_obj())  # no None/float at any depth
    obj = state.to_canonical_obj()
    assert obj["st04_level_pipeline_states"] == [
        {
            "generation_id": 0,
            "cycle_id": 0,
            "direction": "BU",
            "level_id": 1,
            "target_price": Decimal("100200"),
            "is_protection_locked": False,
        },
        {
            "generation_id": 0,
            "cycle_id": 0,
            "direction": "SL",
            "level_id": 1,
            "target_price": Decimal("99800"),
            "is_protection_locked": True,
        },
    ]
