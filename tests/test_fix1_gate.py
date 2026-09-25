"""Fix-1 gate (STR-0345/0346, DECISION-016): q_min + T_enter/T_exit + gate (7g-3b)."""

import ast
import importlib.util
from decimal import Decimal, getcontext
from pathlib import Path

import pytest

from hypergrid.core.transitions import (
    compute_q_min,
    compute_t_enter,
    compute_t_exit,
    progression_permitted,
    round_to_zero,
)


def test_q_min_exact_and_context_preserved() -> None:
    prec_before = getcontext().prec
    rounding_before = getcontext().rounding
    q = compute_q_min(min_notional_usd=Decimal("10"), mark_price=Decimal("50000"))
    assert q == Decimal("0.0002")  # 10/50000 exact
    # ambient R5 context unchanged across the division (no localcontext mutation).
    assert getcontext().prec == prec_before
    assert getcontext().rounding == rounding_before


def test_t_enter_is_two_times_max_both_sides() -> None:
    # ε_H = 1 => T_enter = 2·max(τ_acc, q_min).
    assert compute_t_enter(tau_acc=Decimal("3"), q_min=Decimal("2")) == Decimal("6")
    assert compute_t_enter(tau_acc=Decimal("2"), q_min=Decimal("3")) == Decimal("6")


def test_t_exit_is_max() -> None:
    assert compute_t_exit(tau_acc=Decimal("3"), q_min=Decimal("2")) == Decimal("3")
    assert compute_t_exit(tau_acc=Decimal("2"), q_min=Decimal("3")) == Decimal("3")


def test_round_to_zero_strict_both() -> None:
    t_exit = Decimal("2")
    assert round_to_zero(exposure_delta=Decimal("1"), t_exit=t_exit) == Decimal("0")
    assert round_to_zero(exposure_delta=Decimal("-1"), t_exit=t_exit) == Decimal("0")
    assert round_to_zero(exposure_delta=Decimal("2"), t_exit=t_exit) == Decimal("2")
    assert round_to_zero(exposure_delta=Decimal("0"), t_exit=t_exit) == Decimal("0")
    assert round_to_zero(exposure_delta=Decimal("3"), t_exit=t_exit) == Decimal("3")


def test_progression_permitted_non_strict() -> None:
    t_enter = Decimal("6")
    assert progression_permitted(exposure_delta=Decimal("6"), t_enter=t_enter) is True
    assert (
        progression_permitted(exposure_delta=Decimal("6.0001"), t_enter=t_enter)
        is False
    )
    assert progression_permitted(exposure_delta=Decimal("-6"), t_enter=t_enter) is True


def test_f1star_dead_band_permits_the_unexecutable() -> None:
    # τ_acc < |Δ| < q_min: the OLD |Δ| <= ExposureTolerance gate would BLOCK; Fix-1
    # permits (T_enter = 2·q_min), and round_to_zero zeroes the sub-tradable residue.
    q_min = compute_q_min(min_notional_usd=Decimal("10"), mark_price=Decimal("50000"))
    tau_acc = Decimal("0.00005")  # < q_min (0.0002)
    delta = Decimal("0.0001")  # τ_acc < |Δ| < q_min
    t_enter = compute_t_enter(tau_acc=tau_acc, q_min=q_min)
    t_exit = compute_t_exit(tau_acc=tau_acc, q_min=q_min)
    assert progression_permitted(exposure_delta=delta, t_enter=t_enter) is True
    assert round_to_zero(exposure_delta=delta, t_exit=t_exit) == Decimal("0")


def test_pre_fix1_predicate_absent_as_live_gate() -> None:
    # 'ExposureTolerance' never appears as a live identifier in core/ (only tau_acc
    # is used); the broken F-1* |Δ| <= ExposureTolerance gate is not implemented.
    spec = importlib.util.find_spec("hypergrid.core")
    assert spec is not None and spec.submodule_search_locations is not None
    core_root = Path(next(iter(spec.submodule_search_locations)))
    for path in sorted(core_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                assert node.id != "ExposureTolerance", path
            if isinstance(node, ast.Attribute):
                assert node.attr != "ExposureTolerance", path


def test_validation() -> None:
    with pytest.raises(ValueError):
        compute_q_min(min_notional_usd=Decimal("0"), mark_price=Decimal("1"))
    with pytest.raises(ValueError):
        compute_q_min(min_notional_usd=Decimal("10"), mark_price=Decimal("0"))
    with pytest.raises(ValueError):
        compute_t_enter(tau_acc=Decimal("0"), q_min=Decimal("1"))
    with pytest.raises(ValueError):
        compute_t_exit(tau_acc=Decimal("1"), q_min=Decimal("-1"))
    with pytest.raises(ValueError):
        round_to_zero(exposure_delta=1, t_exit=Decimal("2"))  # non-Decimal
    with pytest.raises(ValueError):
        round_to_zero(exposure_delta=Decimal("1"), t_exit=Decimal("0"))
    with pytest.raises(ValueError):
        progression_permitted(exposure_delta=Decimal("1"), t_enter=Decimal("0"))
