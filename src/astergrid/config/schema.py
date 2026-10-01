"""Pydantic v2 config models derived from `Strategy.md` §14 (Phase 7a).

One model per §14 parameter group. Every field carries metadata (STR-* id,
unit, calibration status, defining §) in ``json_schema_extra`` so the future
UI (DECISION-023 / UI_REQUIREMENT.md) can render labelled forms and so JSON
schema export is self-describing.

STRICT FLOAT POLICY (no choice): money and any value that interacts with money
uses ``decimal.Decimal`` — never ``float``. A ``float`` passed where a
``Decimal`` is required is a VALIDATION ERROR. We NEVER convert ``float`` ->
``Decimal`` (``Decimal(<float>)`` inherits the binary-representation error).
Accept only ``int``, ``str`` or ``Decimal`` for Decimal fields. Pure counts
and durations use ``int``.

§14 global rule (STR-0257): values/formulas are proposal-only; a DERIVED value
is never user-set — DERIVED parameters live in ``DerivedParams`` (runtime-
populated in Phase 7b), never in the user-facing group models. Phase 7a defines
structure only; no trading/domain logic is computed here.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from decimal import Decimal
from typing import Annotated, Literal

import tomli_w
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _reject_float(value: object) -> object:
    """Reject ``float`` for Decimal fields; pass int/str/Decimal through."""
    if isinstance(value, float):
        raise ValueError(
            "float is forbidden for a money/Decimal field; pass int, str, or Decimal"
        )
    return value


# Strict Decimal: floats are rejected before pydantic's Decimal coercion.
Dec = Annotated[Decimal, BeforeValidator(_reject_float)]

_MODEL_CONFIG = ConfigDict(frozen=True, extra="forbid")


class LifecycleEvolutionParams(BaseModel):
    """§14 group: Lifecycle & evolution."""

    model_config = _MODEL_CONFIG

    evolution_confirmation_seconds: int = Field(
        default=60,
        gt=0,
        json_schema_extra={
            "str_id": "STR-0258",
            "unit": "s",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§4.2 (D-03)",
        },
    )
    max_generations: int = Field(
        default=99,
        json_schema_extra={
            "str_id": "STR-0259",
            "unit": "count",
            "calibration_status": "FIXED",
            "defined_in": "§3 (D-08)",
        },
    )
    max_cycles_per_generation: int = Field(
        default=99,
        json_schema_extra={
            "str_id": "STR-0260",
            "unit": "count",
            "calibration_status": "FIXED",
            "defined_in": "§3 (D-08)",
        },
    )


class GridGeometryParams(BaseModel):
    """§14 group: Grid geometry (§7)."""

    model_config = _MODEL_CONFIG

    step_bps: Dec = Field(
        default=Decimal("10"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0261",
            "unit": "bps",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§7.1 (D-09 C)",
        },
    )
    grid_levels: int = Field(
        default=6,
        ge=1,
        le=12,
        json_schema_extra={
            "str_id": "STR-0262",
            "unit": "count",
            "calibration_status": "FIXED",
            "defined_in": "§7.1 (D-09 C)",
        },
    )
    first_level_distance_bps: Dec = Field(
        default=Decimal("20"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0263",
            "unit": "bps",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§7.1 (D-09 C); default = 2 x StepBps",
        },
    )
    reference_price_tolerance_bps: Dec = Field(
        default=Decimal("3.3"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0264",
            "unit": "bps",
            "calibration_status": "[DYNAMIC-CALIBRATABLE]",
            "defined_in": "§5.4.1 (D-17); default = 0.33 x StepBps",
        },
    )
    gen2_distance_multiplier: Dec = Field(
        default=Decimal("2"),
        ge=Decimal("1.1"),
        le=Decimal("2.0"),
        json_schema_extra={
            "str_id": "STR-0265",
            "unit": "ratio",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§7.1 (D-09 C); range 1.1-2.0",
        },
    )
    weak_side_first_level_multiplier: Dec = Field(
        default=Decimal("2"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0266",
            "unit": "ratio",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§7.1 (D-09 C)",
        },
    )
    gen2_size_multiplier: Dec = Field(
        default=Decimal("1.5"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0267",
            "unit": "ratio",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§7.1 (D-09 C)",
        },
    )
    cycle_reference_derivation: str = Field(
        default="TERMINAL_EXECUTION",
        json_schema_extra={
            "str_id": "STR-0268",
            "unit": "policy",
            "calibration_status": "FIXED",
            "defined_in": "§5.4 (one of the four §5.4 options; DECISION-009: "
            "MUST be set explicitly in runtime config)",
        },
    )


class ArmingOrderGateParams(BaseModel):
    """§14 group: Arming & order gates (§8)."""

    model_config = _MODEL_CONFIG

    pending_arm_distance_bps: Dec = Field(
        default=Decimal("50"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0269",
            "unit": "bps",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§8 (D-09 D); default = 5 x StepBps",
        },
    )
    min_depth_multiple: Dec = Field(
        default=Decimal("10"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0270",
            "unit": "ratio",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§8 (D-09 D)",
        },
    )
    distance_band_bps: tuple[Dec, Dec] = Field(
        default=(Decimal("5"), Decimal("100")),
        json_schema_extra={
            "str_id": "STR-0271",
            "unit": "bps",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§8 (D-09 D); [StepBps/2, 10 x StepBps]",
        },
    )
    margin_safety_buffer: Dec = Field(
        default=Decimal("0.20"),
        ge=0,
        json_schema_extra={
            "str_id": "STR-0272",
            "unit": "fraction",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§8 (D-09 D); x required initial margin",
        },
    )
    net_expected_edge_floor_bps: Dec = Field(
        default=Decimal("1"),
        json_schema_extra={
            "str_id": "STR-0273",
            "unit": "bps",
            "calibration_status": "CALIBRATABLE",
            "defined_in": "§8/§10 (D-09 D); default = StepBps/10",
        },
    )
    arm_policy: Literal["AUTO", "SEMI", "WEBHOOK"] = Field(
        default="SEMI",
        json_schema_extra={
            "str_id": "STR-0274",
            "unit": "policy",
            "calibration_status": "FIXED",
            "defined_in": "§8 (D-10); Testnet=AUTO, Live=SEMI",
        },
    )
    arm_request_timeout_seconds: int = Field(
        default=30,
        gt=0,
        json_schema_extra={
            "str_id": "STR-0275",
            "unit": "s",
            "calibration_status": "FIXED",
            "defined_in": "§8 (D-10); required for SEMI/WEBHOOK",
        },
    )


class ExecutionEmergencyParams(BaseModel):
    """§14 group: Execution & emergency (§9, §10)."""

    model_config = _MODEL_CONFIG

    emergency_tolerance_bps: Dec = Field(
        default=Decimal("17"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0276",
            "unit": "bps",
            "calibration_status": "[DYNAMIC — CALIBRATION PENDING]",
            "defined_in": "§9.1 (D-16); 0.005 x (10000/Leverage_effective); "
            "default shown at L_eff=3 (example, dynamic — calibrate)",
        },
    )
    emergency_bounded_wait_seconds: int = Field(
        default=30,
        gt=0,
        json_schema_extra={
            "str_id": "STR-0277",
            "unit": "s",
            "calibration_status": "FIXED",
            "defined_in": "§9.1 (D-09 A)",
        },
    )


class TwoRegimeCost(BaseModel):
    """MaxExecutionCost two-regime form (§12.1, STR-0281)."""

    model_config = _MODEL_CONFIG

    profit_regime_fraction: Dec = Field(
        default=Decimal("0.30"),
        ge=0,
        json_schema_extra={"unit": "fraction", "when": "BasketNetPnL > 0"},
    )
    loss_regime_bps: Dec = Field(
        default=Decimal("100"),
        ge=0,
        json_schema_extra={"unit": "bps", "when": "BasketNetPnL <= 0"},
    )


class ExposureRiskParams(BaseModel):
    """§14 group: Exposure & risk bounds (§7.3, §11, §12.1).

    User-settable subset only; DERIVED notional caps live in ``DerivedParams``.
    """

    model_config = _MODEL_CONFIG

    exposure_tolerance: Dec = Field(
        default=Decimal("0.00005"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0278",
            "unit": "base-asset quantity",
            "calibration_status": "[DYNAMIC — CALIBRATION PENDING]",
            "defined_in": "§5.2/§11.1 (D-16); example default (dynamic — calibrate)",
        },
    )
    max_exposure_imbalance: Dec = Field(
        default=Decimal("0.00208"),
        gt=0,
        json_schema_extra={
            "str_id": "STR-0279",
            "unit": "base-asset quantity",
            "calibration_status": "[DYNAMIC — CALIBRATION PENDING]",
            "defined_in": "§11.2/§12.1 (D-16); example default at 3x (calibrate)",
        },
    )
    max_range_induced_dd_pct: Dec = Field(
        default=Decimal("100"),
        json_schema_extra={
            "str_id": "STR-0280",
            "unit": "% of equity",
            "calibration_status": "FIXED",
            "defined_in": "§12.1 (D-09 B)",
        },
    )
    max_execution_cost: TwoRegimeCost = Field(
        default_factory=TwoRegimeCost,
        json_schema_extra={
            "str_id": "STR-0281",
            "unit": "two-regime (fraction / bps)",
            "calibration_status": "FIXED",
            "defined_in": "§12.1 (D-09 B)",
        },
    )
    max_failed_level_rate_pct: Dec = Field(
        default=Decimal("5"),
        ge=0,
        json_schema_extra={
            "str_id": "STR-0282",
            "unit": "% of Levels",
            "calibration_status": "FIXED",
            "defined_in": "§12.1 (D-09 B); window = ALL Levels of ACTIVE Basket",
        },
    )
    max_hedge_cost_pct: Dec = Field(
        default=Decimal("2"),
        ge=0,
        json_schema_extra={
            "str_id": "STR-0283",
            "unit": "% of USD notional",
            "calibration_status": "FIXED",
            "defined_in": "§12.1 (D-09 B); of MaxBasketNotional",
        },
    )


class BasketClosureEconomicsParams(BaseModel):
    """§14 group: Basket closure & economics (§13).

    User-settable subset only; DERIVED targets live in ``DerivedParams``.
    """

    model_config = _MODEL_CONFIG

    basket_close_mode: str = Field(
        default="HYBRID",
        json_schema_extra={
            "str_id": "STR-0291",
            "unit": "policy",
            "calibration_status": "FIXED",
            "defined_in": "§13.4 (one of the three §13.4 options)",
        },
    )


class UserParams(BaseModel):
    """The complete user-settable §14 configuration (six groups).

    ``extra='forbid'`` guarantees a DERIVED parameter name (e.g.
    ``MaxBasketNotional``) cannot be set by the user here — DERIVED values are
    computed by the runtime into ``DerivedParams`` (Phase 7b).
    """

    model_config = _MODEL_CONFIG

    lifecycle: LifecycleEvolutionParams = Field(
        default_factory=LifecycleEvolutionParams
    )
    grid: GridGeometryParams = Field(default_factory=GridGeometryParams)
    arming: ArmingOrderGateParams = Field(default_factory=ArmingOrderGateParams)
    execution: ExecutionEmergencyParams = Field(
        default_factory=ExecutionEmergencyParams
    )
    exposure: ExposureRiskParams = Field(default_factory=ExposureRiskParams)
    closure: BasketClosureEconomicsParams = Field(
        default_factory=BasketClosureEconomicsParams
    )


class DerivedParams(BaseModel):
    """DERIVED §14 parameters (STR-0284..0290) — NOT user-settable.

    These are computed by the runtime from `UserParams` + authoritative venue
    reads (Phase 7b); Phase 7a leaves them unset (``None``). Never configured
    by the user (§14 global rule, STR-0257).
    """

    model_config = _MODEL_CONFIG

    max_basket_notional: Dec | None = Field(
        default=None, json_schema_extra={"str_id": "STR-0284", "unit": "USD notional"}
    )
    max_level_notional: Dec | None = Field(
        default=None, json_schema_extra={"str_id": "STR-0285", "unit": "USD notional"}
    )
    max_level_notional_dominant: Dec | None = Field(
        default=None, json_schema_extra={"str_id": "STR-0286", "unit": "USD notional"}
    )
    max_cycle_notional: Dec | None = Field(
        default=None, json_schema_extra={"str_id": "STR-0287", "unit": "USD notional"}
    )
    max_generation_notional: Dec | None = Field(
        default=None, json_schema_extra={"str_id": "STR-0288", "unit": "USD notional"}
    )
    basket_net_profit_closure_target: Dec | None = Field(
        default=None, json_schema_extra={"str_id": "STR-0289", "unit": "USD"}
    )
    residual_exposure_tolerance_at_closure: Dec | None = Field(
        default=None,
        json_schema_extra={"str_id": "STR-0290", "unit": "base-asset size"},
    )


def _pythonify(value: object) -> object:
    """Convert Decimals to str and tuples to lists for TOML serialization."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Mapping):
        return {str(k): _pythonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_pythonify(item) for item in value]
    return value


def to_toml(params: UserParams) -> str:
    """Serialize `UserParams` to TOML (Decimals as strings; lossless)."""
    converted = _pythonify(params.model_dump(mode="python"))
    if not isinstance(converted, dict):
        raise TypeError("expected a mapping at the top level")
    return tomli_w.dumps(converted)


def from_toml(text: str) -> UserParams:
    """Parse TOML back into `UserParams` (str -> Decimal via the strict type)."""
    return UserParams.model_validate(tomllib.loads(text))


def user_params_json_schema() -> dict[str, object]:
    """JSON schema for `UserParams` (for UI form generation, Phase 7b+)."""
    return UserParams.model_json_schema()
