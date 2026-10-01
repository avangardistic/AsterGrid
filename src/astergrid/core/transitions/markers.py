"""Shared arbitration dataclasses for the P2/P3/P4 stages (Phase 7d).

A LEAF module: it imports ONLY :mod:`astergrid.core.transitions.reason_codes`
and the stdlib. It MUST NOT import ``core.state`` or ``core.pass_engine`` — that
keeps the import graph acyclic (``state`` imports these markers; ``locks`` /
``precedence`` import these markers; ``pass_engine`` imports these markers).

Design rule (Phase 7d): these markers are set DIRECTLY by tests in Phase 7d.
In Phase 7e/7f the real §4/§5 transitions will populate them from folded
envelopes. NOTHING in Phase 7d infers a candidate/attempt/lock from envelope or
event content.

``StageReport`` lives here (a shared, canonical-serializable stage output used by
``locks``, ``precedence`` and ``pass_engine``) so those three never need to
import one another; ``PassReport`` (which aggregates StageReports) lives in
``pass_engine``. Each dataclass exposes ``to_canonical_obj()`` producing a dict
with no ``None`` and no ``float`` at any depth (Phase-7c canonical contract).
"""

from __future__ import annotations

from dataclasses import dataclass

from astergrid.core.transitions.reason_codes import ReasonCode


@dataclass(frozen=True, slots=True)
class StageReport:
    """One pass-engine stage's outcome (P0..P6)."""

    stage: str  # "P0" | "P1" | ... | "P6"
    status: str  # "STUBBED" | "APPLIED" | "NO_OP"
    reason_codes: tuple[str, ...] = ()  # each a ReasonCode value (plain string)
    notes: str = ""  # deterministic free-form note (no clock/random/repr)

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class P2LocksState:
    """§4.7 P2 in-flight locks (the state carried between passes)."""

    evolution_in_flight: bool = False
    # (GenerationID, cycle-in-flight) sorted by GenerationID ascending.
    cycle_in_flight_by_generation: tuple[tuple[int, bool], ...] = ()

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "evolution_in_flight": self.evolution_in_flight,
            "cycle_in_flight_by_generation": [
                [gid, flag] for gid, flag in self.cycle_in_flight_by_generation
            ],
        }


@dataclass(frozen=True, slots=True)
class P2Attempts:
    """§4.7 P2 per-pass attempt inputs (set by tests in 7d, transitions in 7e/7f)."""

    evolution_attempted: bool = False
    # (GenerationID, cycle-attempted) sorted by GenerationID ascending.
    cycle_attempted_by_generation: tuple[tuple[int, bool], ...] = ()

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "evolution_attempted": self.evolution_attempted,
            "cycle_attempted_by_generation": [
                [gid, flag] for gid, flag in self.cycle_attempted_by_generation
            ],
        }


@dataclass(frozen=True, slots=True)
class P3CandidateMarkers:
    """§4.7 P3 same-generation candidates (per pass)."""

    disable_candidates: tuple[int, ...] = ()  # GenerationIDs with a disable, sorted
    evolution_candidates: tuple[int, ...] = ()  # GenerationIDs with Evolution, sorted

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "disable_candidates": sorted(self.disable_candidates),
            "evolution_candidates": sorted(self.evolution_candidates),
        }


@dataclass(frozen=True, slots=True)
class P4CandidateMarkers:
    """§4.7 P4 across-generation candidates (per pass)."""

    evolution_candidates: tuple[int, ...] = ()  # GenerationIDs, sorted
    # (GenerationID, CycleID) sorted lexicographically.
    cycle_candidates: tuple[tuple[int, int], ...] = ()

    def to_canonical_obj(self) -> dict[str, object]:
        return {
            "evolution_candidates": sorted(self.evolution_candidates),
            "cycle_candidates": [
                [gid, cid] for gid, cid in sorted(self.cycle_candidates)
            ],
        }


@dataclass(frozen=True, slots=True)
class P4Decision:
    """One §4.7 P4 ordered admission (execution order is the tuple order)."""

    transition: str  # exactly "EVOLUTION" or "CYCLE"
    generation_id: int
    cycle_id: int | None  # the Cycle for CYCLE; None for EVOLUTION
    reason: ReasonCode  # canonical form: reason.value; membership validated below

    def __post_init__(self) -> None:
        if self.transition not in ("EVOLUTION", "CYCLE"):
            raise ValueError("transition must be 'EVOLUTION' or 'CYCLE'")
        if not isinstance(self.reason, ReasonCode):
            raise ValueError("reason must be a ReasonCode member")

    def to_canonical_obj(self) -> dict[str, object]:
        obj: dict[str, object] = {
            "transition": self.transition,
            "generation_id": self.generation_id,
            "reason": self.reason.value,
        }
        if self.cycle_id is not None:  # R-JSON-6: omit absent optional
            obj["cycle_id"] = self.cycle_id
        return obj
