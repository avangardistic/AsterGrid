"""§7.3 position sizing + hard caps + D-14 counting helpers (Phase 7g-2).

Pure functions only; nothing is wired into ``run_pass``. Every input is a
function argument — config values NEVER flow into ``core/`` by import, and no ST-*
field is read (the D-14 counters take typed tuples as arguments). No decimal
context is mutated anywhere (R5 depends on the ambient default context).

FIXED COMPOSITION ORDER (the 7h arming caller composes; each defined independently):
  Step 1  assign_level_notionals   — per-level USD notionals (via the Part-B caps)
  Step 2  enforce_level_caps       — per-LEVEL hard cap (reject, never clip)
  Step 3  convert_notional_to_size — USD -> base-asset size (R4 round-down)

ENFORCEMENT SPLIT: Step 2 checks PER-LEVEL notionals only. Aggregate enforcement
(a Cycle's summed notionals vs MaxCycleNotional, a Generation's vs
MaxGenerationNotional, the Basket's vs MaxBasketNotional) happens at ARMING time
over ST-04 sums (Phase 7h, §8 gate 5), NOT here. Part B provides the cap VALUES
for both enforcement points (single source).

7g-2 does NOT: compute MaxBasketNotional (§12.1/D-13 — parameter only); read any
ST-* field; persist the base-asset size (persistence = an intent, Phase 7h); check
MinNotional ($10 — §8 gate 3, Phase 7h).

PINNED READINGS (Owner rulings; OCaml parity depends on them):

R4. LEVEL-SIZING ROUNDS DOWN (toward zero). Neither §6.3/§7.3 nor STR-0382 pins a
    direction, so this is a ruling: ROUND_DOWN. RATIONALE — hard-cap faithfulness
    (STR-0154): caps are enforced on USD notionals BEFORE conversion, so conversion
    must never yield a size whose mark-value exceeds the capped notional; rounding
    up can breach a hard cap by up to one lot. The "never under-hedge" argument
    belongs to HEDGE sizing (§11, Phase 7g-3), a separate function — it does NOT
    transfer to level sizing; the closure ceiling is a tolerance upper bound,
    likewise not transferable. PINNED PROPERTY (tested): size * mark_price <=
    notional, always.

R5. DECIMAL PRECISION CONTEXT IS AMBIENT-DEFAULT AND PINNED. Non-terminating
    divisions (30000/7, 5000/99999) round per the ambient default context (28
    significant digits, ROUND_HALF_EVEN); this deterministic behaviour is pinned by
    the exact-value tests for OCaml parity. No code here mutates the context.
"""

from __future__ import annotations

from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from astergrid.core.transitions.cycle_state import CycleState
    from astergrid.core.transitions.generation_state import GenerationState

_CLOSED_LIFECYCLE = "CLOSED_ONLY_AS_PART_OF_BASKET"


def _require_pos_decimal(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} must be a Decimal instance")
    if value <= 0:
        raise ValueError(f"{name} must be > 0")


def _require_grid_levels(value: int) -> None:
    if type(value) is not int:  # bool is an int subclass — reject it
        raise ValueError("grid_levels must be an int")
    if not (1 <= value <= 12):
        raise ValueError("grid_levels must be within 1..12")


def _require_nonneg_int(value: int, name: str) -> None:
    if type(value) is not int:  # reject bool
        raise ValueError(f"{name} must be an int")
    if value < 0:
        raise ValueError(f"{name} must be >= 0")


# --------------------------- Part B: cap values ---------------------------


def compute_max_level_notional(
    *,
    max_basket_notional: Decimal,
    grid_levels: int,
) -> Decimal:
    """MaxLevelNotional (STR-0155) = max_basket_notional / grid_levels."""
    _require_pos_decimal(max_basket_notional, "max_basket_notional")
    _require_grid_levels(grid_levels)
    return max_basket_notional / grid_levels


def compute_max_level_notional_dominant(
    *,
    max_basket_notional: Decimal,
    grid_levels: int,
    gen2_size_multiplier: Decimal,
) -> Decimal:
    """MaxLevelNotionalDominant (STR-0156) = gen2 * MaxLevelNotional (single source)."""
    _require_pos_decimal(gen2_size_multiplier, "gen2_size_multiplier")
    base = compute_max_level_notional(
        max_basket_notional=max_basket_notional, grid_levels=grid_levels
    )
    return gen2_size_multiplier * base


def compute_max_cycle_notional(
    *,
    max_basket_notional: Decimal,
    active_cycle_count: int,
) -> Decimal:
    """MaxCycleNotional (STR-0157) = max_basket_notional / active_cycle_count."""
    _require_pos_decimal(max_basket_notional, "max_basket_notional")
    _require_nonneg_int(active_cycle_count, "active_cycle_count")
    if active_cycle_count == 0:
        raise ValueError("cannot compute MaxCycleNotional: active_cycle_count is 0")
    return max_basket_notional / active_cycle_count


def compute_max_generation_notional(
    *,
    max_basket_notional: Decimal,
    active_generation_count: int,
) -> Decimal:
    """MaxGenerationNotional (STR-0158) = max_basket_notional / active_gen_count."""
    _require_pos_decimal(max_basket_notional, "max_basket_notional")
    _require_nonneg_int(active_generation_count, "active_generation_count")
    if active_generation_count == 0:
        raise ValueError(
            "cannot compute MaxGenerationNotional: active_generation_count is 0"
        )
    return max_basket_notional / active_generation_count


# --------------------------- Part B: D-14 counters ---------------------------


def _is_counted_generation(generation: GenerationState) -> bool:
    """The shared D-14 'counted' predicate: not closed as part of the Basket.

    DISABLED_AT_CYCLE_99 generations COUNT (their exposure is fully live, §5.3);
    only CLOSED_ONLY_AS_PART_OF_BASKET is excluded.
    """
    return generation.lifecycle != _CLOSED_LIFECYCLE


def count_active_generations(
    generation_states: tuple[GenerationState, ...],
) -> int:
    """D-14/STR-0160: count Generations not CLOSED_ONLY_AS_PART_OF_BASKET."""
    return sum(1 for g in generation_states if _is_counted_generation(g))


def count_active_cycles(
    cycle_states: tuple[CycleState, ...],
    generation_states: tuple[GenerationState, ...],
) -> int:
    """D-14/STR-0161: count Cycles OF THE COUNTED GENERATIONS.

    7g-2 SIMPLIFIED READING: no ST-03 lifecycle is a "closed" tag yet (closure is
    §13.4, later), so every row of a counted Generation counts — INCLUDING
    COMPLETED (STR-0161) and TERMINAL_PENDING rows. FORWARD NOTE: when §13.4
    closure lands, this MUST additionally filter any future closed-Cycle tag.
    Cycles of a CLOSED Generation are EXCLUDED (STR-0161 qualifier).
    """
    counted = {g.generation_id for g in generation_states if _is_counted_generation(g)}
    return sum(1 for c in cycle_states if c.generation_id in counted)


# --------------------------- Part A: sizing ---------------------------


def assign_level_notionals(
    *,
    max_basket_notional: Decimal,
    grid_levels: int,
    gen2_size_multiplier: Decimal,
    is_successor: bool,
    is_dominant: bool,
) -> tuple[Decimal, ...]:
    """Step 1 (STR-0148): per-level USD notionals; all levels of a side are equal.

    Base (any G0 cycle) -> MaxLevelNotional per level. Successor dominant ->
    MaxLevelNotionalDominant. Successor weak -> MaxLevelNotional. Calls the Part-B
    helpers (no restated division). ``is_dominant`` ignored when not is_successor.
    """
    _require_grid_levels(grid_levels)  # validated again for a clear error here
    if is_successor and is_dominant:
        notional = compute_max_level_notional_dominant(
            max_basket_notional=max_basket_notional,
            grid_levels=grid_levels,
            gen2_size_multiplier=gen2_size_multiplier,
        )
    else:
        _require_pos_decimal(gen2_size_multiplier, "gen2_size_multiplier")
        notional = compute_max_level_notional(
            max_basket_notional=max_basket_notional, grid_levels=grid_levels
        )
    return tuple(notional for _ in range(grid_levels))


def enforce_level_caps(
    *,
    level_notionals: tuple[Decimal, ...],
    max_level_notional: Decimal,
    max_level_notional_dominant: Decimal,
    is_successor: bool,
    is_dominant: bool,
) -> tuple[Decimal, ...]:
    """Step 2 (STR-0154/0162, D-12): per-LEVEL hard cap — reject, never clip.

    CALLER CONTRACT: ``level_notionals`` holds ONE side's notionals (one cap applies
    to the whole tuple). Mixed-side tuples are a caller error, undetectable here by
    design. Returns the input unchanged on success; raises ValueError if any level
    exceeds its cap (inclusive: exactly-at passes). In the composed pipeline this
    always passes (assignment derives FROM these caps); its value is the independent
    reject-semantics check for externally-supplied notionals.
    """
    _require_pos_decimal(max_level_notional, "max_level_notional")
    _require_pos_decimal(max_level_notional_dominant, "max_level_notional_dominant")
    if not level_notionals:
        raise ValueError("level_notionals must be non-empty")
    cap = (
        max_level_notional_dominant
        if (is_successor and is_dominant)
        else max_level_notional
    )
    for notional in level_notionals:
        _require_pos_decimal(notional, "level_notional")
        if notional > cap:
            raise ValueError("level notional exceeds its hard cap (reject, never clip)")
    return level_notionals


def _round_down_to_decimals(value: Decimal, decimals: int) -> Decimal:
    """Quantize ``value`` to ``decimals`` places, ROUND_DOWN (toward zero, R4)."""
    exponent = Decimal("1").scaleb(-decimals)
    return value.quantize(exponent, rounding=ROUND_DOWN)


def convert_notional_to_size(
    *,
    notional: Decimal,
    mark_price: Decimal,
    sz_decimals: int,
) -> Decimal:
    """Step 3: base-asset size = floor(notional / mark_price, sz_decimals) (R4).

    ZERO-SIZE RULE: a conversion that rounds to 0 (dust notional) is LEGAL output,
    not an error — arming rejects it via §8 gate 3 (MinNotional) in Phase 7h.
    MinNotional is NOT checked here.
    """
    _require_pos_decimal(notional, "notional")
    _require_pos_decimal(mark_price, "mark_price")
    _require_nonneg_int(sz_decimals, "sz_decimals")
    return _round_down_to_decimals(notional / mark_price, sz_decimals)
