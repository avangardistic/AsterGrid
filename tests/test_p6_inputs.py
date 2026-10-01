"""P6 input markers + State slot wiring (Phase 7h-4b-2, E2)."""

import dataclasses
from decimal import Decimal

import pytest

from astergrid.core.fold import _empty_state
from astergrid.core.serialization import canonical_dumps
from astergrid.core.transitions import (
    ArmPolicy,
    OperationalState,
    OperatorDecision,
    P6ArmInput,
    P6CancelInput,
    P6IssuanceInput,
)


def _arm(**over: object) -> P6ArmInput:
    base: dict[str, object] = {
        "cloid": "c1",
        "generation_disabled": False,
        "book_depth_at_target": Decimal("100"),
        "distance_bps": 50,
        "min_order_size": Decimal("0.1"),
        "margin_available": Decimal("100"),
        "margin_required": Decimal("10"),
        "exposure_caps_ok": True,
        "open_order_count": 0,
        "price_normalized_ok": True,
        "size_normalized_ok": True,
        "market_state": OperationalState.ACTIVE,
        "net_expected_edge_bps": Decimal("5"),
        "policy": ArmPolicy.AUTO,
        "timeout_s": 30,
        "tif": "Gtc",
        "expires_after": 60,
        "intent_log_seq": 0,
    }
    base.update(over)
    return P6ArmInput(**base)  # type: ignore[arg-type]


def _cancel(**over: object) -> P6CancelInput:
    base: dict[str, object] = {"cloid": "c1", "expires_after": 60, "intent_log_seq": 0}
    base.update(over)
    return P6CancelInput(**base)  # type: ignore[arg-type]


def _issue(**over: object) -> P6IssuanceInput:
    base: dict[str, object] = {
        "generation_id": 0,
        "cycle_id": 6,
        "grid_levels": 6,
        "step_bps": Decimal("10"),
        "first_level_distance_bps": Decimal("20"),
        "is_dominant_bu": True,
        "is_dominant_sl": False,
        "gen2_distance_multiplier": Decimal("2"),
        "weak_side_first_level_multiplier": Decimal("1.5"),
        "size_notional_usd": Decimal("5000"),
        "edge_clears_floor_bu": True,
        "edge_clears_floor_sl": True,
    }
    base.update(over)
    return P6IssuanceInput(**base)  # type: ignore[arg-type]


# --------------------------- happy paths + canonical ---------------------------


def test_happy_paths_and_canonical() -> None:
    for row in (_arm(), _cancel(), _issue()):
        canonical_dumps(row.to_canonical_obj())
    assert _cancel().tif == "Gtc"  # Item-3 COINED default
    # optional None fields omitted (arm with no policy/timeout/decision).
    obj = _arm(policy=None, timeout_s=None, decision=None).to_canonical_obj()
    assert "policy" not in obj and "timeout_s" not in obj and "decision" not in obj
    obj2 = _arm(
        policy=ArmPolicy.SEMI, timeout_s=30, decision=OperatorDecision.APPROVE
    ).to_canonical_obj()
    assert obj2["policy"] == "SEMI" and obj2["decision"] == "APPROVE"


# --------------------------- P6ArmInput validation ---------------------------


def test_arm_bool_and_int_traps() -> None:
    with pytest.raises(ValueError):
        _arm(generation_disabled=1)  # truthy int, not bool
    with pytest.raises(ValueError):
        _arm(distance_bps=True)  # bool, not int
    with pytest.raises(ValueError):
        _arm(open_order_count=-1)
    with pytest.raises(ValueError):
        _arm(expires_after=0)
    with pytest.raises(ValueError):
        _arm(intent_log_seq=-1)


def test_arm_decimal_and_enum_and_tif() -> None:
    with pytest.raises(ValueError):
        _arm(book_depth_at_target=1.0)  # float
    with pytest.raises(ValueError):
        _arm(min_order_size=Decimal("0"))
    with pytest.raises(ValueError):
        _arm(market_state="ACTIVE")  # not the enum
    with pytest.raises(ValueError):
        _arm(tif="FOK")
    with pytest.raises(ValueError):
        _arm(cloid="")
    with pytest.raises(ValueError):
        _arm(timeout_s=-1)


def test_arm_distance_band_shape() -> None:
    assert _arm(distance_band=(5, 100)).distance_band == (5, 100)
    with pytest.raises(ValueError):
        _arm(distance_band=(5, 100, 1))
    with pytest.raises(ValueError):
        _arm(distance_band=(100, 5))  # lo > hi
    with pytest.raises(ValueError):
        _arm(distance_band=(5, True))  # bool member


# --------------------------- P6CancelInput / P6IssuanceInput validation -------


def test_cancel_validation() -> None:
    with pytest.raises(ValueError):
        _cancel(cloid="")
    with pytest.raises(ValueError):
        _cancel(expires_after=0)
    with pytest.raises(ValueError):
        _cancel(intent_log_seq=-1)
    with pytest.raises(ValueError):
        _cancel(tif="FOK")


def test_issuance_validation() -> None:
    with pytest.raises(ValueError):
        _issue(generation_id=100)
    with pytest.raises(ValueError):
        _issue(grid_levels=0)
    with pytest.raises(ValueError):
        _issue(grid_levels=13)
    with pytest.raises(ValueError):
        _issue(grid_levels=True)  # bool trap
    with pytest.raises(ValueError):
        _issue(step_bps=Decimal("0"))
    with pytest.raises(ValueError):
        _issue(is_dominant_bu=1)  # bool trap


# --------------------------- State slot sorting / dup rules --------------------


def test_state_arm_cancel_sorted_no_dup() -> None:
    ok = dataclasses.replace(
        _empty_state(),
        p6_arm_inputs=(_arm(cloid="a"), _arm(cloid="b")),
        p6_cancel_inputs=(_cancel(cloid="a"), _cancel(cloid="b")),
    )
    canonical_dumps(ok.to_canonical_obj())
    with pytest.raises(ValueError):  # arm unsorted
        dataclasses.replace(
            _empty_state(), p6_arm_inputs=(_arm(cloid="b"), _arm(cloid="a"))
        )
    with pytest.raises(ValueError):  # cancel dup cloid
        dataclasses.replace(
            _empty_state(), p6_cancel_inputs=(_cancel(cloid="a"), _cancel(cloid="a"))
        )


def test_state_issuance_sorted_no_dup() -> None:
    ok = dataclasses.replace(
        _empty_state(),
        p6_issuance_inputs=(_issue(generation_id=0, cycle_id=5), _issue(cycle_id=6)),
    )
    canonical_dumps(ok.to_canonical_obj())
    with pytest.raises(ValueError):  # unsorted by (gen, cycle)
        dataclasses.replace(
            _empty_state(),
            p6_issuance_inputs=(_issue(cycle_id=6), _issue(cycle_id=5)),
        )
    with pytest.raises(ValueError):  # dup (gen, cycle)
        dataclasses.replace(
            _empty_state(),
            p6_issuance_inputs=(_issue(cycle_id=6), _issue(cycle_id=6)),
        )


def test_empty_state_omits_p6_slots() -> None:
    obj = _empty_state().to_canonical_obj()
    assert "p6_arm_inputs" not in obj
    assert "p6_cancel_inputs" not in obj
    assert "p6_issuance_inputs" not in obj
