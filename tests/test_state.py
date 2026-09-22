"""State object: frozen, validated, canonical-serializable (Phase 7c)."""

import dataclasses

import pytest

from hypergrid.core.events import GENESIS_PREV_HASH
from hypergrid.core.fold import _empty_state
from hypergrid.core.serialization import canonical_dumps
from hypergrid.core.state import _EVENT_KINDS, State

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
