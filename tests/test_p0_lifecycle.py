"""§6.1 recording semantics (Phase 7h-1): lifecycle set, hard rule, lock coherence.

There are NO transitions in Strategy for the pipeline (§6.1 is a diagram of allowed
positions). P0 RECORDS an observed lifecycle; these tests pin the recording rules on
both leaves (``PerLevelObservation`` and ``LevelState``) behaviorally — no private
imports.
"""

import dataclasses
from decimal import Decimal

import pytest

from hypergrid.core.fold import _empty_state
from hypergrid.core.pass_engine import run_pass
from hypergrid.core.transitions import LevelState, PerLevelObservation
from hypergrid.core.transitions.observation_state import P0ObservationMarkers

# The 13 §6.1 + LEVEL_SKIPPED (§9.3), stated in the test (behavioral). 7h-3 added the
# 14th member to both leaves; this list tracks it (pre-authorized existing-test edit).
_ALL_LIFECYCLES = (
    "INTENT_CREATED",
    "ORDER_SUBMITTED",
    "ORDER_ACKNOWLEDGED",
    "ORDER_ACTIVE",
    "PARTIALLY_FILLED",
    "FILLED",
    "POSITION_VERIFIED",
    "CANCELLED",
    "EMERGENCY",
    "SKIPPED",
    "ERROR",
    "LOCKED",
    "IDLE",
    "LEVEL_SKIPPED",
)


def _obs(**over: object) -> PerLevelObservation:
    fields: dict[str, object] = {
        "generation_id": 0,
        "cycle_id": 0,
        "direction": "BU",
        "level_id": 1,
        "lifecycle": "ORDER_ACTIVE",
        "filled_quantity": Decimal("0"),
        "order_filled": False,
        "position_delta_verified": False,
    }
    fields.update(over)
    return PerLevelObservation(**fields)  # type: ignore[arg-type]


def _level(**over: object) -> LevelState:
    fields: dict[str, object] = {
        "generation_id": 0,
        "cycle_id": 0,
        "direction": "BU",
        "level_id": 1,
        "target_price": Decimal("50000"),
        "is_protection_locked": False,
    }
    fields.update(over)
    return LevelState(**fields)  # type: ignore[arg-type]


# --------------------------- 14-set acceptance (both leaves) ---------------------


def test_all_thirteen_accepted_on_observation() -> None:
    for lc in _ALL_LIFECYCLES:
        # FILLED needs the conjunction; the rest don't.
        obs = _obs(lifecycle=lc, order_filled=True, position_delta_verified=True)
        assert obs.lifecycle == lc


def test_all_thirteen_accepted_on_level_state() -> None:
    for lc in _ALL_LIFECYCLES:
        lvl = _level(lifecycle=lc, is_protection_locked=(lc == "LOCKED"))
        assert lvl.lifecycle == lc


def test_bogus_lifecycle_rejected_both_leaves() -> None:
    with pytest.raises(ValueError):
        _obs(lifecycle="NOT_A_STATE", order_filled=True, position_delta_verified=True)
    with pytest.raises(ValueError):
        _level(lifecycle="NOT_A_STATE")


def test_thirteen_set_drift_guard() -> None:
    # Both leaves accept exactly the same 14 and reject the same bogus token.
    for lc in _ALL_LIFECYCLES:
        assert (
            _obs(
                lifecycle=lc, order_filled=True, position_delta_verified=True
            ).lifecycle
            == lc
        )
        assert (
            _level(lifecycle=lc, is_protection_locked=(lc == "LOCKED")).lifecycle == lc
        )
    for bogus in ("", "filled", "Filled", "POSITION VERIFIED", "DONE"):
        with pytest.raises(ValueError):
            _obs(lifecycle=bogus)
        with pytest.raises(ValueError):
            _level(lifecycle=bogus)


# --------------------------- filled_quantity ---------------------------


def test_filled_quantity_nonnegative_and_decimal_only() -> None:
    assert _obs(filled_quantity=Decimal("0")).filled_quantity == Decimal("0")
    assert _obs(filled_quantity=Decimal("12.5")).filled_quantity == Decimal("12.5")
    with pytest.raises(ValueError):
        _obs(filled_quantity=Decimal("-1"))
    with pytest.raises(ValueError):
        _obs(filled_quantity=1.5)  # float rejected
    with pytest.raises(ValueError):
        _level(filled_quantity=Decimal("-1"))
    with pytest.raises(ValueError):
        _level(filled_quantity=0.5)  # float rejected


# --------------------------- §6.1 hard rule ---------------------------


def test_filled_requires_conjunction() -> None:
    # order-only, delta-only, neither: all reject.
    with pytest.raises(ValueError):
        _obs(lifecycle="FILLED", order_filled=True, position_delta_verified=False)
    with pytest.raises(ValueError):
        _obs(lifecycle="FILLED", order_filled=False, position_delta_verified=True)
    with pytest.raises(ValueError):
        _obs(lifecycle="FILLED", order_filled=False, position_delta_verified=False)


def test_filled_with_both_ok_and_nonfilled_without_ok() -> None:
    ok = _obs(lifecycle="FILLED", order_filled=True, position_delta_verified=True)
    assert ok.lifecycle == "FILLED"
    # non-FILLED with neither bit set is fine.
    assert _obs(lifecycle="ORDER_ACTIVE").lifecycle == "ORDER_ACTIVE"
    assert (
        _obs(
            lifecycle="POSITION_VERIFIED",
            order_filled=True,
            position_delta_verified=True,
        ).lifecycle
        == "POSITION_VERIFIED"
    )


def test_verification_bits_must_be_bool() -> None:
    with pytest.raises(ValueError):
        _obs(order_filled=1)  # truthy int rejected
    with pytest.raises(ValueError):
        _obs(position_delta_verified=0)


# --------------------------- R10c lock coherence (LevelState) ------------------


def test_lock_coherence_rules() -> None:
    assert _level(lifecycle="LOCKED", is_protection_locked=True).lifecycle == "LOCKED"
    assert _level(lifecycle="IDLE", is_protection_locked=False).lifecycle == "IDLE"
    assert _level(lifecycle="ORDER_ACTIVE", is_protection_locked=False).lifecycle
    with pytest.raises(ValueError):  # locked but not LOCKED
        _level(lifecycle="ORDER_ACTIVE", is_protection_locked=True)
    with pytest.raises(ValueError):  # LOCKED but not locked
        _level(lifecycle="LOCKED", is_protection_locked=False)


def test_none_lifecycle_skips_coherence() -> None:
    # Pre-observation: lifecycle None, either lock value is fine.
    assert _level(lifecycle=None, is_protection_locked=True).lifecycle is None
    assert _level(lifecycle=None, is_protection_locked=False).lifecycle is None


# --------------------------- no accumulation (P0 records the value) ------------


def test_p0_records_marker_value_exactly_no_accumulation() -> None:
    base = _level(lifecycle="ORDER_ACTIVE", filled_quantity=Decimal("2.0"))
    state = dataclasses.replace(
        _empty_state(),
        st04_level_pipeline_states=(base,),
        p0_observation_markers=P0ObservationMarkers(
            observations=(
                _obs(lifecycle="PARTIALLY_FILLED", filled_quantity=Decimal("5.0")),
            ),
            net_position=Decimal("0"),
            mark_price=Decimal("50000"),
            tau_acc=Decimal("0.00005"),
            min_notional_usd=Decimal("10"),
            max_exposure_imbalance=Decimal("3"),
            emergency_tolerance=Decimal("5"),
            margin_distance=Decimal("100"),
            normal_tolerance=Decimal("1"),
            transient_tolerance=Decimal("3"),
        ),
    )
    new_state, _ = run_pass(state, [])
    rows = new_state.st04_level_pipeline_states or ()
    assert len(rows) == 1
    # EXACTLY the marker value (5.0), not 2.0 + 5.0.
    assert rows[0].filled_quantity == Decimal("5.0")
    assert rows[0].lifecycle == "PARTIALLY_FILLED"
