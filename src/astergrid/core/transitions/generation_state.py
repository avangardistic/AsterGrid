"""Typed per-Generation ST-* domain state for Phase 7e (§4).

A LEAF module: it imports ONLY the stdlib. It MUST NOT import ``core.state`` or
``core.pass_engine`` (``state`` imports these dataclasses; nothing here imports
back), so no import cycle can form. This module holds typed ST-* DOMAIN state
(ST-02/14/15/16) — not §4.7 pass markers — hence ``generation_state``.

All dataclasses are frozen, slots-enabled and canonical-serializable via
``to_canonical_obj()`` (no ``None`` and no ``float`` at any depth; absent
optionals OMITTED per R-JSON-6). Each validates its own coherence in
``__post_init__`` and raises ``ValueError`` on an incoherent construction.
"""

from __future__ import annotations

from dataclasses import dataclass

# The six §4.3 lifecycle states (FROZEN is an overlay, never a lifecycle here).
_LIFECYCLES = frozenset(
    {
        "CREATED",
        "ACTIVE",
        "EVOLUTION_PENDING",
        "SUCCESSOR_CREATED",
        "DISABLED_AT_CYCLE_99",
        "CLOSED_ONLY_AS_PART_OF_BASKET",
    }
)
_GROUPS = frozenset({"BU", "SL"})  # §4.1 cond 2 / §4.5


@dataclass(frozen=True, slots=True)
class GenerationState:
    """ST-02: a Generation's §4.3 lifecycle state."""

    generation_id: int
    lifecycle: str  # exactly one of the six §4.3 states (validated)

    def __post_init__(self) -> None:
        if self.generation_id < 0:
            raise ValueError("generation_id must be >= 0")
        if self.lifecycle not in _LIFECYCLES:
            raise ValueError(f"invalid lifecycle: {self.lifecycle!r}")

    def to_canonical_obj(self) -> dict[str, object]:
        return {"generation_id": self.generation_id, "lifecycle": self.lifecycle}


@dataclass(frozen=True, slots=True)
class DominanceFlag:
    """ST-14: the Dominant side of a Generation (§4.5)."""

    generation_id: int
    dominant_group: str  # exactly BU or SL (validated)

    def __post_init__(self) -> None:
        if self.generation_id < 0:
            raise ValueError("generation_id must be >= 0")
        if self.dominant_group not in _GROUPS:
            raise ValueError(f"dominant_group must be BU/SL: {self.dominant_group!r}")

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "generation_id": self.generation_id,
            "dominant_group": self.dominant_group,
        }


@dataclass(frozen=True, slots=True)
class SuccessorLock:
    """ST-15: the permanent per-Generation successor lock (§4.4).

    Recorded ONLY when set: a missing tuple entry means unlocked (the evolution
    transition treats a missing entry as unlocked). ``p2_locks.evolution_in_flight``
    (§4.7 P2, transient/per-pass/Basket-wide) is a DISTINCT concept and is never
    merged with this permanent/per-Generation lock.
    """

    generation_id: int
    locked: bool  # permanent when True (§4.4)

    def __post_init__(self) -> None:
        if self.generation_id < 0:
            raise ValueError("generation_id must be >= 0")

    def to_canonical_obj(self) -> dict[str, object]:
        return {"generation_id": self.generation_id, "locked": self.locked}


@dataclass(frozen=True, slots=True)
class EvolutionCandidateWindow:
    """ST-16: a Generation's Evolution candidate window (§4.1/§4.2).

    Describes a COMPLETED evaluation of the §4.1 conditions for one Generation:
    absence (no window; ``return_level=None``) means "not yet evaluated", never a
    guessed boolean. There is deliberately NO ``is_eligible_for_evolution`` field:
    §4.4/§4.6 eligibility is evaluated DIRECTLY by the transition rules, so no
    redundant pre-evaluated flag can drift out of sync.
    """

    generation_id: int
    origin_group: str  # BU or SL (§4.1 cond 2)
    traversal_verified_levels: tuple[int, ...]  # sorted ascending (§4.1 cond 1)
    return_level: int | None  # None <=> never attempted (§4.1 cond 4)
    return_level_verified: bool  # §4.1 cond 5 verdict (meaningful iff return set)
    return_confirmation_held: bool  # §4.2 window verdict (iff verified)
    guards_passed: bool  # §4.1 cond 6 verdict (P1-owned)

    def __post_init__(self) -> None:
        if self.generation_id < 0:
            raise ValueError("generation_id must be >= 0")
        if self.origin_group not in _GROUPS:
            raise ValueError(f"origin_group must be BU or SL: {self.origin_group!r}")
        levels = self.traversal_verified_levels
        if list(levels) != sorted(levels):
            raise ValueError("traversal_verified_levels must be sorted ascending")
        if self.return_level is not None and not levels:
            raise ValueError("return_level set but no traversal levels")
        if self.return_level_verified and self.return_level is None:
            raise ValueError("return_level_verified requires a return_level")
        if self.return_confirmation_held and not self.return_level_verified:
            raise ValueError("return_confirmation_held requires return_level_verified")

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "generation_id": self.generation_id,
            "origin_group": self.origin_group,
            "traversal_verified_levels": list(self.traversal_verified_levels),
            "return_level_verified": self.return_level_verified,
            "return_confirmation_held": self.return_confirmation_held,
            "guards_passed": self.guards_passed,
        }
        if self.return_level is not None:  # R-JSON-6: omit absent optional
            obj["return_level"] = self.return_level
        return obj
