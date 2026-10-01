"""§11.4 remainder quantities (Phase 7h-3): the unfilled-size arithmetic. Pure.

A LEAF module: stdlib only. It MUST NOT import ``core.state``/``core.pass_engine``.

``track_remainder`` computes the remaining size/notional from a requested size and a
VERIFIED filled size (§11.4 L893: PARTIALLY_FILLED contributes verified-so-far; the
remainder is "not-yet-exposure" and "times out into Emergency Execution (§9.1)"; a
"skipped residual permanently contributes zero"). It takes ``reference_price`` as a
param (no ST-04 read — the ST-04↔ST-05 decoupling stands; no coupling designed, A2).

GUARD: STR-0199 (``ExpectedExposure := Σ VERIFIED``) governs the §11.1 exposure
derivation ONLY. Remainder arithmetic never treats requested AS filled, so it is
outside STR-0199's scope. Complementary to 7g-3b's
``classify_remainder_hedge_status`` (that classifies hedge status from runtime bools;
this computes quantities — no import either way).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_GROUPS = frozenset({"BU", "SL"})  # §3 direction VERBATIM


@dataclass(frozen=True, slots=True)
class RemainderState:
    """§11.4 remainder quantities for one level's order (exact Decimal arithmetic)."""

    level_identity: tuple[int, int, str, int]  # (gen, cycle, direction, level)
    requested_size: Decimal  # > 0
    verified_filled_size: Decimal  # 0 <= verified <= requested
    remaining_size: Decimal  # requested - verified (exact)
    remaining_notional_usd: Decimal  # remaining * reference_price (exact)
    is_fully_filled: bool  # remaining == 0

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "level_identity": list(self.level_identity),
            "requested_size": self.requested_size,
            "verified_filled_size": self.verified_filled_size,
            "remaining_size": self.remaining_size,
            "remaining_notional_usd": self.remaining_notional_usd,
            "is_fully_filled": self.is_fully_filled,
        }


def track_remainder(
    *,
    requested_size: Decimal,
    verified_filled_size: Decimal,
    level_identity: tuple[int, int, str, int],
    reference_price: Decimal,
) -> RemainderState:
    """Compute §11.4 remainder quantities. Fail-closed (``ValueError``) on bad input."""
    gen, cycle, direction, level = level_identity
    if type(gen) is not int or type(cycle) is not int or type(level) is not int:
        raise ValueError("level_identity gen/cycle/level must be ints")
    if direction not in _GROUPS:
        raise ValueError(f"direction must be BU or SL: {direction!r}")
    for name, value in (
        ("requested_size", requested_size),
        ("verified_filled_size", verified_filled_size),
        ("reference_price", reference_price),
    ):
        if not isinstance(value, Decimal):
            raise ValueError(f"{name} must be a Decimal instance")
    if requested_size <= 0:
        raise ValueError("requested_size must be > 0")
    if reference_price <= 0:
        raise ValueError("reference_price must be > 0")
    if not (0 <= verified_filled_size <= requested_size):
        raise ValueError("verified_filled_size must be within [0, requested_size]")

    remaining_size = requested_size - verified_filled_size
    remaining_notional_usd = remaining_size * reference_price
    return RemainderState(
        level_identity=level_identity,
        requested_size=requested_size,
        verified_filled_size=verified_filled_size,
        remaining_size=remaining_size,
        remaining_notional_usd=remaining_notional_usd,
        is_fully_filled=remaining_size == 0,
    )


__all__ = ["RemainderState", "track_remainder"]
