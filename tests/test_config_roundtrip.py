"""§14 config schema: validation, TOML round-trip, float/DERIVED/domain rules."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from hypergrid.config.schema import (
    ExposureRiskParams,
    GridGeometryParams,
    UserParams,
    from_toml,
    to_toml,
    user_params_json_schema,
)


def test_defaults_validate() -> None:
    params = UserParams()
    assert params.grid.grid_levels == 6
    assert params.grid.step_bps == Decimal("10")


def test_toml_roundtrip_is_lossless_for_defaults() -> None:
    params = UserParams()
    assert from_toml(to_toml(params)) == params


def test_toml_roundtrip_is_lossless_for_custom_values() -> None:
    params = UserParams.model_validate(
        {
            "grid": {"step_bps": "12.5", "grid_levels": 8},
            "arming": {"distance_band_bps": ["6.25", "125"]},
            "exposure": {"exposure_tolerance": "0.00006"},
        }
    )
    restored = from_toml(to_toml(params))
    assert restored == params
    assert restored.grid.step_bps == Decimal("12.5")
    assert restored.arming.distance_band_bps == (Decimal("6.25"), Decimal("125"))


def test_derived_field_cannot_be_set_by_user() -> None:
    with pytest.raises(ValidationError):
        ExposureRiskParams.model_validate({"max_basket_notional": "30000"})


def test_grid_levels_out_of_range_fails() -> None:
    with pytest.raises(ValidationError):
        GridGeometryParams.model_validate({"grid_levels": 13})
    with pytest.raises(ValidationError):
        GridGeometryParams.model_validate({"grid_levels": 0})


def test_float_where_decimal_required_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GridGeometryParams.model_validate({"step_bps": 10.0})


def test_int_and_str_accepted_for_decimal_fields() -> None:
    from_int = GridGeometryParams.model_validate({"step_bps": 10})
    from_str = GridGeometryParams.model_validate({"step_bps": "10"})
    assert from_int.step_bps == from_str.step_bps == Decimal("10")


def test_json_schema_exports_metadata() -> None:
    schema = user_params_json_schema()
    assert isinstance(schema, dict)
    assert "properties" in schema
