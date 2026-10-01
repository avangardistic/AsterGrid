"""Real P0: observation recording + p1-marker projection (Phase 7h-1).

P0 is the §4.7 first pass: POSITION VERIFICATION & RECONCILIATION. In 7h-1 it
RECORDS venue-observed data (from ``P0ObservationMarkers``) into ST-04
(filled_quantity + lifecycle) and ST-19 (mark_price), and PROJECTS the
``p1_exposure_markers`` that the untouched P1 reads. It derives nothing except the
§6.1 hard rule (enforced at marker construction, not here).

RULINGS (Owner-pinned, binding — OCaml parity depends on them; each cited):
  * R9  — P0 OBSERVATION BOUNDARY. "Real P0" = record markers into ST-04/ST-19 and
    project p1-markers (pure functions + one stage entry; envelopes UNREAD). §4.7 P0
    is a single line ("feeds everything; §11.1") with NO read path, so the boundary
    is forced by architecture + the phase pins: fills/lifecycle/mark_price/
    net_position have no in-pipeline producer (P6 stub, no adapters, ``FillEvent``
    has no producer, ``fold`` writes neither ST-04 nor ST-19 and is pinned) → they
    arrive as markers (tests now; FillEvent/fold/adapter/venue later). P0 reads State
    markers + prior State ONLY; envelopes are accepted-but-UNREAD (Phase-7d DESIGN
    RULE, same as P1). P0 emits NO verdict/reason code in 7h-1 (the §6.1 hard rule is
    enforced at marker construction); reconciliation verdicts arrive with their
    consumers (ST-13/§13, later).
  * R10 — ST-04 FIELDS: exactly ``filled_quantity`` (VERIFIED cumulative, STR-0199 +
    STR-0212; the marker carries the cumulative value — P0 never accumulates) and
    ``lifecycle`` (one of the 13 §6.1 strings), plus the LOCK COHERENCE
    ``is_protection_locked ⇔ lifecycle == "LOCKED"`` enforced by ``LevelState``.
    ``order_state``/cloid/oid are §8/P6-domain (7h-2/7h-4). P0 EXTENDS existing rows
    only — it never creates geometry rows (target_price/lock are unknown to it).
  * R11 — P0-SIDE PROJECTION, P1 write-only preserved. ``p1_exposure_markers``
    becomes P0-written (single writer): ``level_fills`` from FULLY-OBSERVED ST-04
    rows, ``net_position``/``mark_price`` from p0 markers, the 7 externals carried
    verbatim (ST-11 territory). Placement is FORCED (P1 is untouchable this phase, so
    P0 must write the field P1 reads). Partial observation: a row with EITHER new
    field still None is EXCLUDED from ``level_fills`` (cannot build a ``LevelFillState``
    without both; observed-only projection).

Pure, total, clock-free, Decimal-only; no ST-* reads beyond prior ST-04; no
envelope reads. Runtime-imports the same-package leaves for construction (no cycle).
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from astergrid.core.transitions.exposure_state import LevelFillState
from astergrid.core.transitions.hedge_state import P1ExposureMarkers
from astergrid.core.transitions.level_state import LevelState
from astergrid.core.transitions.markers import StageReport
from astergrid.core.transitions.market_observation_state import MarketObservationState

if TYPE_CHECKING:
    from decimal import Decimal

    from astergrid.core.events import EventEnvelope
    from astergrid.core.state import State
    from astergrid.core.transitions.observation_state import PerLevelObservation


def extend_level_states(
    *,
    current: tuple[LevelState, ...],
    observations: tuple[PerLevelObservation, ...],
) -> tuple[LevelState, ...]:
    """Upsert observed fill/lifecycle onto EXISTING ST-04 rows (R10; fail-closed).

    P0 never CREATES geometry rows (target_price/lock are unknown to it): an
    observation for an identity not already present is a ``ValueError``. Tuple order
    is PRESERVED (in-place replace → determinism). Each replaced row is rebuilt via
    ``dataclasses.replace``, so ``LevelState`` re-validates and the R10c lock
    coherence (``is_protection_locked ⇔ lifecycle == "LOCKED"``) surfaces any drift
    as a ``ValueError``.
    """
    index_by_identity = {
        (row.generation_id, row.cycle_id, row.direction, row.level_id): i
        for i, row in enumerate(current)
    }
    rows = list(current)
    for obs in observations:
        identity = (obs.generation_id, obs.cycle_id, obs.direction, obs.level_id)
        i = index_by_identity.get(identity)
        if i is None:
            raise ValueError(
                f"P0 cannot create a level row (no geometry): {identity!r}"
            )
        rows[i] = dataclasses.replace(
            rows[i],
            filled_quantity=obs.filled_quantity,
            lifecycle=obs.lifecycle,
        )
    return tuple(rows)


def project_p1_markers(
    *,
    level_states: tuple[LevelState, ...],
    net_position: Decimal,
    mark_price: Decimal,
    tau_acc: Decimal,
    min_notional_usd: Decimal,
    max_exposure_imbalance: Decimal,
    emergency_tolerance: Decimal,
    margin_distance: Decimal,
    normal_tolerance: Decimal,
    transient_tolerance: Decimal,
) -> P1ExposureMarkers:
    """Build ``P1ExposureMarkers`` from ST-04 + p0 externals (R11; single site).

    ``level_fills`` is built from FULLY-OBSERVED rows only — a row missing either
    ``filled_quantity`` or ``lifecycle`` cannot become a ``LevelFillState`` and is
    EXCLUDED (observed-only). The rest are carried verbatim.
    """
    fills = tuple(
        LevelFillState(
            generation_id=row.generation_id,
            cycle_id=row.cycle_id,
            direction=row.direction,
            level_id=row.level_id,
            filled_quantity=row.filled_quantity,
            lifecycle=row.lifecycle,
        )
        for row in level_states
        if row.filled_quantity is not None and row.lifecycle is not None
    )
    return P1ExposureMarkers(
        level_fills=fills,
        net_position=net_position,
        tau_acc=tau_acc,
        min_notional_usd=min_notional_usd,
        mark_price=mark_price,
        max_exposure_imbalance=max_exposure_imbalance,
        emergency_tolerance=emergency_tolerance,
        margin_distance=margin_distance,
        normal_tolerance=normal_tolerance,
        transient_tolerance=transient_tolerance,
    )


def apply_p0(
    state: State,
    envelopes: list[EventEnvelope],
) -> tuple[State, StageReport]:
    """Real P0: record observations into ST-04/ST-19 + project p1-markers.

    ``envelopes`` is accepted-but-UNREAD (run_pass threading uniformity; §4.7 P0
    names no read path — R9). Markers absent → ``(state UNCHANGED, ("P0", "NO_OP",
    (), ...))`` (7d-compat pin; keeps every 7g-3b test green). Markers present → the
    write is ST-04 + ST-19 + ``p1_exposure_markers`` ONLY; P0 NEVER reads
    ST-07/08/09/ST-23 (write-only holds for P0 too), emits NO reason code, and reads
    no clock.
    """
    markers = state.p0_observation_markers
    if markers is None:
        return state, StageReport(
            "P0", "NO_OP", (), "p0 markers absent: no observation recorded"
        )

    current = state.st04_level_pipeline_states or ()
    new_st04 = extend_level_states(current=current, observations=markers.observations)
    st19 = MarketObservationState(mark_price=markers.mark_price)
    p1_markers = project_p1_markers(
        level_states=new_st04,
        net_position=markers.net_position,
        mark_price=markers.mark_price,
        tau_acc=markers.tau_acc,
        min_notional_usd=markers.min_notional_usd,
        max_exposure_imbalance=markers.max_exposure_imbalance,
        emergency_tolerance=markers.emergency_tolerance,
        margin_distance=markers.margin_distance,
        normal_tolerance=markers.normal_tolerance,
        transient_tolerance=markers.transient_tolerance,
    )
    new_state = dataclasses.replace(
        state,
        st04_level_pipeline_states=new_st04,
        st19_market_observation_cache=st19,
        p1_exposure_markers=p1_markers,
    )
    note = f"p0 levels={len(markers.observations)} st19=written p1markers=written"
    return new_state, StageReport("P0", "APPLIED", (), note)
