"""§11.1 exposure derivatives + acute predicate + classification (Phase 7g-3a).

Pure functions only; nothing is wired into ``run_pass`` (P1 stays a stub). Every
input is a parameter or a marker tuple — no ST-* field is read, no envelope is
read, no other transition is called, no decimal context is mutated. Runtime-imports
the ``exposure_state`` leaf for ``LevelFillState``/``ExposureClass`` (7f precedent:
``cycle.py`` runtime-imports ``cycle_state``; the leaf imports only stdlib, so no
cycle forms).

§11.1 formulas (exact):
  ExpectedExposure(Basket) = Σ over Levels in {PARTIALLY_FILLED, FILLED,
      POSITION_VERIFIED} of (+filled_quantity if BU else -filled_quantity)  [R7]
  ActualExposure(Basket)   = net position (signed) from clearinghouseState only
  ExposureDelta            = ExpectedExposure - ActualExposure

PINNED READINGS (Owner rulings; OCaml parity depends on them):

R6. CLASSIFICATION IS PARAMETERIZED MAGNITUDE BANDS. Strategy names the classes
    (normal/transient/escalate, §11.1 L849 — the only occurrence) but gives no
    numeric criteria. Ruling: severity-ordered bands on |Δ| with caller thresholds —
    |Δ| <= normal -> NORMAL; normal < |Δ| <= transient -> TRANSIENT; |Δ| > transient
    -> ESCALATE. Zero -> NORMAL (total; extends "nonzero delta" by the only coherent
    completion). Thresholds: 0 < normal <= transient (equality = degenerate 2-class;
    inversion -> ValueError). Independent of is_acute (STR-0357) — both are
    implemented as written.

R7. EXPOSURE IS DIRECTION-SIGNED NET (BU +, SL -). ActualExposure is venue net
    position and szi is SIGNED (STR-0200); Delta = Expected - Actual is coherent only
    on the same signed-net basis (a flat BU-1.0/SL-1.0 book must read Δ=0, not 2.0);
    BU long +, SL short - (§2 glossary + universal venue convention). Per-leg marker
    quantities stay >= 0 magnitudes; the SUM applies signs. Expected and Delta are
    SIGNED; only |Δ| enters predicates.

7g-3a does NOT: compute MaxExposureImbalance (τ_I), EmergencyTolerance
(d_emergency), or margin_distance (all §16 [DYN]/venue — parameters); decide
staleness (a 7h feed behaviour); enforce any gate (the §11.1 tolerance gate + Fix-1
are P1, Phase 7g-3b).
"""

from __future__ import annotations

from decimal import Decimal

from astergrid.core.transitions.exposure_state import (
    COUNTED_LIFECYCLES,
    ExposureClass,
    LevelFillState,
)


def _require_decimal(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} must be a Decimal instance")


def compute_expected_exposure(
    *,
    level_fills: tuple[LevelFillState, ...],
) -> Decimal:
    """§11.1 + R7: signed net over counted-lifecycle fills (BU +, SL -)."""
    total = Decimal("0")
    for fill in level_fills:
        if fill.lifecycle not in COUNTED_LIFECYCLES:
            continue
        if fill.direction == "BU":
            total += fill.filled_quantity
        else:  # SL
            total -= fill.filled_quantity
    return total


def compute_actual_exposure(*, net_position: Decimal) -> Decimal:
    """§11.1: signed net position from clearinghouseState (DECISION-002).

    In 7g-3a ``net_position`` is a parameter; the caller asserts venue origin (a bare
    Decimal cannot be origin-checked). Any sign (including zero) is valid.
    """
    _require_decimal(net_position, "net_position")
    return net_position


def compute_exposure_delta(
    *,
    expected_exposure: Decimal,
    actual_exposure: Decimal,
) -> Decimal:
    """§11.1: ExposureDelta = ExpectedExposure - ActualExposure (any sign)."""
    _require_decimal(expected_exposure, "expected_exposure")
    _require_decimal(actual_exposure, "actual_exposure")
    return expected_exposure - actual_exposure


def is_acute(
    *,
    exposure_delta: Decimal,
    max_exposure_imbalance: Decimal,
    margin_distance: Decimal,
    emergency_tolerance: Decimal,
) -> bool:
    """STR-0357: acute(Δ) = |Δ| > τ_I OR margin_distance < 2·d_emergency (strict).

    BASIS SEAM: ``margin_distance`` MUST share ``emergency_tolerance``'s bps basis
    (they are compared directly); the 7h producer owns the basis. τ_I and
    d_emergency are §16 [DYN] parameters — never computed here.
    """
    _require_decimal(exposure_delta, "exposure_delta")
    _require_decimal(max_exposure_imbalance, "max_exposure_imbalance")
    _require_decimal(margin_distance, "margin_distance")
    _require_decimal(emergency_tolerance, "emergency_tolerance")
    if max_exposure_imbalance <= 0:
        raise ValueError("max_exposure_imbalance must be > 0")
    if emergency_tolerance <= 0:
        raise ValueError("emergency_tolerance must be > 0")
    if margin_distance < 0:
        raise ValueError("margin_distance must be >= 0")
    return (
        abs(exposure_delta) > max_exposure_imbalance
        or margin_distance < 2 * emergency_tolerance
    )


def classify_exposure(
    *,
    exposure_delta: Decimal,
    normal_tolerance: Decimal,
    transient_tolerance: Decimal,
) -> ExposureClass:
    """§11.1 (R6): magnitude bands on |Δ| (inclusive lowers; zero -> NORMAL)."""
    _require_decimal(exposure_delta, "exposure_delta")
    _require_decimal(normal_tolerance, "normal_tolerance")
    _require_decimal(transient_tolerance, "transient_tolerance")
    if normal_tolerance <= 0:
        raise ValueError("normal_tolerance must be > 0")
    if transient_tolerance < normal_tolerance:
        raise ValueError("transient_tolerance must be >= normal_tolerance")
    magnitude = abs(exposure_delta)
    if magnitude <= normal_tolerance:
        return ExposureClass.NORMAL
    if magnitude <= transient_tolerance:
        return ExposureClass.TRANSIENT
    return ExposureClass.ESCALATE
