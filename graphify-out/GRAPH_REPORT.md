# Graph Report - AsterGrid  (2026-10-01)

## Corpus Check
- 256 files · ~269,572 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1569 nodes · 4139 edges · 80 communities (69 shown, 10 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 800 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78

## God Nodes (most connected - your core abstractions)
1. `State` - 100 edges
2. `canonical_dumps()` - 84 edges
3. `GenerationState` - 81 edges
4. `_empty_state()` - 80 edges
5. `run_pass()` - 59 edges
6. `CycleState` - 50 edges
7. `LevelState` - 45 edges
8. `apply_evolution()` - 40 edges
9. `EventEnvelope` - 38 edges
10. `apply_cycle()` - 38 edges

## Surprising Connections (you probably didn't know these)
- `test_state_has_23_domain_placeholders()` --uses--> `State`  [INFERRED]
  tests/test_state.py → src/astergrid/core/state.py
- `test_evaluate_wait_direct()` --calls--> `evaluate_wait()`  [INFERRED]
  tests/test_arm_gates.py → src/astergrid/core/transitions/arm.py
- `test_bogus_policy_string_raises()` --calls--> `ArmPolicy`  [INFERRED]
  tests/test_arm_gates.py → src/astergrid/core/transitions/arm_state.py
- `test_actual_exposure_identity()` --calls--> `compute_actual_exposure()`  [INFERRED]
  tests/test_exposure_derivatives.py → src/astergrid/core/transitions/exposure.py
- `test_exposure_delta()` --calls--> `compute_exposure_delta()`  [INFERRED]
  tests/test_exposure_derivatives.py → src/astergrid/core/transitions/exposure.py

## Import Cycles
- None detected.

## Communities (80 total, 10 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (86): apply_cycle(), _cycle_key(), _non_overlap(), Run the §5.2/§5.3 Cycle transitions over ST-03 candidates; return (state, P5)., §5.6 N1->N2->N3 (first failure names the check). Pure/Decimal-only., _ref_key(), CycleState, CycleTerminalMarkers (+78 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (58): apply_evolution(), Evaluate the §4.1 Evolution trigger over ST-16 windows; admit at most one.…, EvolutionCandidateWindow, ST-15: the permanent per-Generation successor lock (§4.4). Recorded ONLY when…, ST-16: a Generation's Evolution candidate window (§4.1/§4.2). Describes a…, SuccessorLock, _no_ambient(), apply_evolution is clock/randomness free (Phase 7e). (+50 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (58): LevelState, ST-04 (Phase 7g-1): ladder identity + target price + §7.2 lock gate., apply_protection_unlock(), Unlock a LOCKED level once its next same-direction level is verified. Pure:…, ST-04 LevelState: frozen, validated, canonical (Phase 7g-1)., test_bad_direction(), test_equal_instances_serialize_identically(), test_frozen() (+50 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (57): assign_level_notionals(), compute_max_cycle_notional(), compute_max_generation_notional(), compute_max_level_notional(), compute_max_level_notional_dominant(), convert_notional_to_size(), count_active_generations(), enforce_level_caps() (+49 more)

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (48): _build_acknowledgment(), _build_administrative(), _build_command(), _build_error(), _build_fill(), _build_intent(), _build_observation(), _build_operator() (+40 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (39): AST, expr, JsonFormatter, LogRecord, Logging skeleton for the runtime shell (DECISION-023). Provides a JSON…, Set the per-run logging context (propagated via contextvars)., Return a copy of ``payload`` with secret-bearing keys removed. Recurses into…, Format a log record as a single JSON line (see module docstring). (+31 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (40): compute_emergency_tolerance_bps(), EmergencyEvaluation, EmergencyVerdict, evaluate_emergency(), _NameValueStrEnum, Decimal, StrEnum, §9 Emergency Execution & Level Skip (Phase 7h-3): tolerance + four-way + skip… (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (41): apply_p6(), _level_key(), _p6_report(), Build the P6 StageReport: status, first-seen code union, fixed-order notes., ST-04 canonical sort key (gen, cycle, direction, level)., Run P6 over one pass. Returns (state', report, sub_decisions, emitted)., P6CancelInput, P6IssuanceInput (+33 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (38): apply_breach_response(), BreachLayer, compute_max_execution_cost_pnl_regime(), compute_max_exposure_imbalance_qty(), compute_max_failed_level_rate(), compute_max_hedge_cost(), compute_max_range_induced_dd_pct(), _NameValueStrEnum (+30 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (39): BaseModel, ArmingOrderGateParams, BasketClosureEconomicsParams, DerivedParams, ExecutionEmergencyParams, ExposureRiskParams, from_toml(), GridGeometryParams (+31 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (27): OperationalState, §13.2 Basket operational state. 9 members VERBATIM (Strategy.md §13.2)., AccountEquityState, BasketNetPnLState, BoundLayerState, FreezeErrorRecoveryOverlayState, ST-17/ST-20/ST-21/ST-22 row types (Phase 7h-4a). Frozen, slots, self-…, ST-20: lifetime-to-date tracked quantities + per-bound ladder states (D-15). (+19 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (36): check_arming_validity(), classify_path_economics(), compute_gross_grid_edge(), compute_net_expected_edge(), _NameValueStrEnum, PathEconomicsVerdict, Decimal, StrEnum (+28 more)

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (28): ArmEvaluation, evaluate_arm_gates(), evaluate_wait(), GateResult, Decimal, §8 arm-gate evaluation (Phase 7h-2): the 10 gates + generation rule + policy…, Evaluate the §8 arm gates + generation rule + policy routing (B3). Order…, One §8 gate's outcome. (+20 more)

### Community 13 - "Community 13"
Cohesion: 0.10
Nodes (28): canonical_dumps(), canonical_loads(), _encode(), _object_hook(), Canonical JSON (R-JSON-1..8), frozen for Python<->OCaml interop (Phase 7b).…, json ``parse_float``: floats are forbidden in canonical JSON., Parse canonical JSON; reconstruct Decimals; reject any float literal., json ``default`` hook: wrap Decimal per R-JSON-2; reject everything else. (+20 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (29): ArmRequestState, expire_on_restart(), is_legal_arm_transition(), ST-12 row/record (CAP-0019): a per-request arm state with inv.4 provenance., Pure ST-12 edge legality over the 5 machine states (B4). Unknown states →…, Supersede a PENDING request → BLOCKED + ARM_SUPERSEDED (L731; re-request/swap).…, Restart rule (B4): a PENDING request reloads BLOCKED + ARM_TIMEOUT (fail-…, Require an ISO-8601-Z microsecond timestamp string (inv.4; no ``datetime``). (+21 more)

### Community 15 - "Community 15"
Cohesion: 0.14
Nodes (27): apply_p1(), compute_q_min(), compute_t_enter(), compute_t_exit(), _pos(), progression_permitted(), Decimal, P1 real: Fix-1 gate + §11.2 hedge urgency/intent + §11.3/§11.4 helpers (7g-3b).… (+19 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (29): _gates(), _intent(), §8 arm gates + policy wait + B1 inlet + B2 classifier (Phase 7h-2, E2). All…, evaluate_arm_gates with an all-passing ENTRY+AUTO baseline, overridden by kw., test_approval_never_bypasses_failed_gate(), test_auto_pass_arms(), test_bogus_policy_string_raises(), test_correction_mechanical_gates_still_apply() (+21 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (17): ActualExposureState, ExpectedExposureState, ExposureDeltaState, LevelFillState, Exposure markers + ST-07/08/09 domain state + ExposureClass (Phase 7g-3a). A…, ST-07 Basket singleton: SIGNED net expected exposure (R7; may be negative)., ST-08 Basket singleton: signed net position from clearinghouseState only., ST-09 Basket singleton: delta = expected - actual (exact), + class + acute.… (+9 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (17): Protocol, astergrid.core.event_log — the append-only log (Phase 7b). The log-as-truth…, In-memory append-only event log (Phase 7b): tests + differential harness., EventLogPort, AnyEvent, The append-only event-log port (Phase 7b). The log is the ONLY allocator of…, Append-only, single-writer event log., Allocate the next log_sequence/monotonic_counter, hash-link, persist.… (+9 more)

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (21): _OrderKey, canonical_order_key(), _cmp_int(), _cmp_opt_int(), _cmp_opt_str(), _cmp_str(), compare(), Canonical event ordering (DECISION-007), pure and clock-free (Phase 7b). The… (+13 more)

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (24): _empty_state(), The State of an empty log: metadata defaults, all domain fields None., Run P0..P6 over one pass; return (new state, pass report, emitted commands)., run_pass(), test_multi_generation_union_sorted(), test_unknown_current_cycle_leaves_set_none(), test_st19_unwritten_when_p0_markers_absent(), test_p0_no_op_without_markers() (+16 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (17): §5.2/§5.3/§5.4/§5.4.1/§5.6 Cycle transition (Phase 7f) — executed as stage P5.…, §5.4 + §5.4.1 gate (check order a-e). Returns (ok, note-or-check-name)., _reference_verdict(), P4Decision, Shared arbitration dataclasses for the P2/P3/P4 stages (Phase 7d). A LEAF…, One §4.7 P4 ordered admission (execution order is the tuple order)., §4.7 P3 + P4 — precedence (Phase 7d, real logic). Both functions are pure,…, StrEnum (+9 more)

### Community 22 - "Community 22"
Cohesion: 0.12
Nodes (18): compute_ladder_geometry(), Decimal, §7.1 grid geometry as a pure function (Phase 7g-1). ``compute_ladder_geometry``…, Return exactly ``grid_levels`` ladder prices, in traversal order (§7.1). Base…, _require_pos_decimal(), issue_fresh_ladder(), Decimal, §5.2 step-8 one-direction ladder issuance (Phase 7h-4b-1). Pure. Composes 7g-1… (+10 more)

### Community 23 - "Community 23"
Cohesion: 0.11
Nodes (19): event_to_payload(), AnyEvent, Return the event's domain fields as a canonical dict (omit absent optionals).…, content_hash_for(), _core_obj(), envelope_to_obj(), AnyEvent, The on-the-wire envelope + tamper-evident hash chain + scenario JSON (Phase… (+11 more)

### Community 24 - "Community 24"
Cohesion: 0.18
Nodes (19): fold(), The pure fold (Phase 7c): envelopes -> State, metadata ONLY. ``fold`` is pure,…, Fold envelopes into a State (metadata only; pure, total, deterministic)., _populate(), Path, fold() determinism across runs and across log implementations (Phase 7c)., test_fold_head_hash_matches_last_envelope(), test_fold_same_list_twice_byte_identical() (+11 more)

### Community 25 - "Community 25"
Cohesion: 0.12
Nodes (17): classify_intent(), construct_order_intent(), _NameValueStrEnum, OrderIntent, OrderType, Decimal, StrEnum, ST-05 order intents & outcomes (Phase 7h-2): inlet + classifier + lifecycle. A… (+9 more)

### Community 26 - "Community 26"
Cohesion: 0.21
Nodes (13): InMemoryEventLog, AnyEvent, A plain-list implementation of :class:`EventLogPort`., Submit one order: build+append a CommandEvent, receipt, advance the ST-05 row.…, submit_order(), _meta(), _order(), §9 submission mechanics (Phase 7h-3, E2): real in-memory log, no fake port. (+5 more)

### Community 27 - "Community 27"
Cohesion: 0.16
Nodes (16): is_legal_order_transition(), OrderState, Pure §6.1 edge legality over the 11 order-pipeline states (B4). Unknown states…, ST-05 row: the intent half (``OrderIntent``) + the §6.1 outcome ``lifecycle``.…, _intent(), ST-05 order lifecycle table + slot wiring (Phase 7h-2, E3). The §6.1 order…, test_all_eleven_states_accepted(), test_all_legal_edges_pass() (+8 more)

### Community 28 - "Community 28"
Cohesion: 0.21
Nodes (17): classify_exposure(), compute_actual_exposure(), compute_exposure_delta(), is_acute(), Decimal, §11.1 exposure derivatives + acute predicate + classification (Phase 7g-3a).…, STR-0357: acute(Δ) = |Δ| > τ_I OR margin_distance < 2·d_emergency (strict).…, §11.1 (R6): magnitude bands on |Δ| (inclusive lowers; zero -> NORMAL). (+9 more)

### Community 29 - "Community 29"
Cohesion: 0.19
Nodes (11): _as_int(), _as_opt_int(), _as_opt_str(), _as_str(), AnyEvent, SQLite-backed append-only event log (Phase 7b), stdlib ``sqlite3`` only. The…, A ``sqlite3`` implementation of :class:`EventLogPort`., _row_to_envelope() (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.15
Nodes (11): _combine_p4(), PassReport, The P0-P6 pass engine (Phase 7d). ``run_pass`` runs the §4.7 stages in strict…, One pass: seven StageReports (P0..P6) + P6's traced sub-decisions., Merge the P4 arbitration (7d) and evolution-execution (7e) sub-reports. §4.7…, §4.7 P2 — locks (Phase 7d, real logic). P2 enforces two independent locks,…, One pass-engine stage's outcome (P0..P6)., StageReport (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.21
Nodes (15): compute_expected_exposure(), §11.1 + R7: signed net over counted-lifecycle fills (BU +, SL -)., _fill(), §11.1 exposure derivatives + R7 signs (Phase 7g-3a)., test_actual_exposure_identity(), test_counted_lifecycles_contribute(), test_empty_is_zero(), test_excluded_lifecycles_contribute_zero() (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (12): build_hedge_intent(), hedge_execution_for(), §11.2: acute -> Ioc (STR-0206 unconditional); else -> maker (STR-0207)., The single HedgeIntent construction site; built even when delta_hat == 0., HedgeIntent, ST-23 content: the §11.2 corrective hedge intent (amount is the exact Δ̂).…, §11.2 hedge urgency + HedgeIntent (no quantity formula; R8) (7g-3b)., test_amount_bounded_by_delta_property() (+4 more)

### Community 33 - "Community 33"
Cohesion: 0.18
Nodes (14): Decimal, §11.4 remainder quantities (Phase 7h-3): the unfilled-size arithmetic. Pure. A…, §11.4 remainder quantities for one level's order (exact Decimal arithmetic)., Compute §11.4 remainder quantities. Fail-closed (``ValueError``) on bad input., RemainderState, track_remainder(), _r(), §11.4 remainder quantities (Phase 7h-3, E2). (+6 more)

### Community 34 - "Community 34"
Cohesion: 0.18
Nodes (13): P1ExposureMarkers, The 10-field P1 input (markers set by tests; 7h projects from ST-04/venue)., apply_p0(), extend_level_states(), project_p1_markers(), Decimal, Real P0: observation recording + p1-marker projection (Phase 7h-1). P0 is the…, Build ``P1ExposureMarkers`` from ST-04 + p0 externals (R11; single site).… (+5 more)

### Community 35 - "Community 35"
Cohesion: 0.24
Nodes (13): apply_locks(), Apply the §4.7 P2 in-flight locks; return (new state, stage report)., P2Attempts, P2LocksState, §4.7 P2 in-flight locks (the state carried between passes)., §4.7 P2 per-pass attempt inputs (set by tests in 7d, transitions in 7e/7f)., _no_ambient(), P2 locks: exhaustive bounded over <=2 generations, determinism (Phase 7d).… (+5 more)

### Community 36 - "Community 36"
Cohesion: 0.20
Nodes (14): ObservedMeta, Append-time clock values supplied by the caller (runtime/adapter shell). The…, CommandEvent, §A2(b) command — a committed side effect. Serves STR-0298/0133/0138/0254., _command(), Phase 7b hardening (G2): timestamp validation in codec + ObservedMeta + append., test_append_does_not_advance_head_on_bad_meta_empty(), test_append_does_not_advance_head_on_bad_meta_nonempty() (+6 more)

### Community 37 - "Community 37"
Cohesion: 0.16
Nodes (8): The folded State: fold metadata + ST-* domain fields + §4.7 arbitration…, §4.1/§4.4/§4.5/§4.6 Evolution transition (Phase 7e) — executed inside P4.…, DominanceFlag, Typed per-Generation ST-* domain state for Phase 7e (§4). A LEAF module: it…, ST-14: the Dominant side of a Generation (§4.5)., P4CandidateMarkers, §4.7 P4 across-generation candidates (per pass)., ST-04<->ST-05 pipeline coupling (Phase 7h-4b-2, B4). Pure, total-on-valid.…

### Community 38 - "Community 38"
Cohesion: 0.18
Nodes (8): The deterministic folded state (metadata + ST-* + §4.7 markers)., Phase-7e ordering + coherence invariants on ST-02/14/15/16. Enforced: each of…, Phase-7f ordering + range invariants on ST-03/10 and the cycle markers.…, Phase-7g-1 ordering + range invariant on ST-04 (LevelState). Enforced: ST-04…, Phase-7h-2 ordering + no-dup invariants on ST-05 and ST-12. Enforced: ST-05…, Phase-7h-4b-2 ordering + no-dup invariants on the P6 input marker slots.…, Canonical dict for :func:`canonical_dumps` (no None/float in output)., State

### Community 39 - "Community 39"
Cohesion: 0.42
Nodes (14): apply_pipeline_coupling(), Advance ST-04 rows from their matching ST-05 order (B4). Fail-closed on RECON.…, _level(), _order(), ST-04<->ST-05 coupling (Phase 7h-4b-2, B4/E2)., _state(), test_determinism(), test_level_skipped_independence_matrix() (+6 more)

### Community 40 - "Community 40"
Cohesion: 0.28
Nodes (14): _level(), _obs(), §6.1 recording semantics (Phase 7h-1): lifecycle set, hard rule, lock…, test_all_thirteen_accepted_on_level_state(), test_all_thirteen_accepted_on_observation(), test_bogus_lifecycle_rejected_both_leaves(), test_filled_quantity_nonnegative_and_decimal_only(), test_filled_requires_conjunction() (+6 more)

### Community 41 - "Community 41"
Cohesion: 0.26
Nodes (13): _arm(), _cancel(), _issue(), P6 input markers + State slot wiring (Phase 7h-4b-2, E2)., test_arm_bool_and_int_traps(), test_arm_decimal_and_enum_and_tif(), test_arm_distance_band_shape(), test_cancel_validation() (+5 more)

### Community 42 - "Community 42"
Cohesion: 0.17
Nodes (10): CancelCandidate, CancelReasonCode, emit_cancel_command(), _NameValueStrEnum, StrEnum, §5.2 step-2 cancel selector (Phase 7h-3): pick the resting orders to cancel.…, Build a cancel ``CommandEvent`` (pure; Phase 7h-4b-2 B2.2). ``action="cancel"``…, StrEnum base whose ``auto()`` value equals the member name (no drift). (+2 more)

### Community 43 - "Community 43"
Cohesion: 0.22
Nodes (10): ExposureClass, StrEnum, §11.1 ExposureDelta classification; canonical form is its plain string., _c(), §11.1 classification bands R6 + ExposureClass enum (Phase 7g-3a)., test_band_boundaries(), test_degenerate_two_class(), test_mid_bands() (+2 more)

### Community 44 - "Community 44"
Cohesion: 0.19
Nodes (10): HedgeExecution, _NameValueStrEnum, _pos(), Decimal, StrEnum, P1 markers + hedge intent + enums (Phase 7g-3b) — a leaf. Imports ONLY the…, StrEnum base whose ``auto()`` value equals the member name (no drift)., §11.2 execution mode; canonical form is the plain string value. (+2 more)

### Community 45 - "Community 45"
Cohesion: 0.23
Nodes (8): MarketObservationState, ST-19 market observation cache — Phase 7g-3b minimal typing (own leaf). A LEAF…, ST-19 (Phase 7g-3b): the mark price M (the Fix-1 q_min divisor)., _markers(), ST-19 population by the real P0 (Phase 7h-1)., test_mark_price_carried_exactly(), test_mark_price_nonpositive_or_nondecimal_rejected(), test_st19_absent_before_present_after()

### Community 46 - "Community 46"
Cohesion: 0.26
Nodes (11): apply_across_generation_precedence(), apply_same_generation_precedence(), Apply the §4.7 P3 same-generation conflict rule (DISABLE beats Evolution)., Apply the §4.7 P4 across-generation ordering (Evolution before Cycle)., P3/P4 precedence: exhaustive bounded, determinism (Phase 7d). Markers are set…, _subsets(), test_p3_exhaustive_bounded(), test_p3_none_markers_is_noop() (+3 more)

### Community 47 - "Community 47"
Cohesion: 0.30
Nodes (11): _acute(), STR-0357 acute predicate (strict on both disjuncts) (Phase 7g-3a)., test_both(), test_boundary_imbalance_equal_false(), test_boundary_margin_equal_false(), test_imbalance_alone(), test_just_inside_both_false(), test_margin_alone() (+3 more)

### Community 48 - "Community 48"
Cohesion: 0.44
Nodes (11): _junk_state(), _level(), _markers(), _obs(), Real P0 wiring into run_pass (7h-1): seven stages, upserts, write-only,…, test_duplicate_identities_rejected_at_construction(), test_envelope_independence(), test_p0_is_write_only_ignores_st07_08_09_23() (+3 more)

### Community 49 - "Community 49"
Cohesion: 0.30
Nodes (11): _enforce(), Decimal, §7.3 Step 2 enforce_level_caps — reject, never clip (Phase 7g-2)., test_boundary_exactly_at_cap_passes(), test_cap_selection_between_the_two(), test_pass_through_base(), test_pass_through_successor_dominant(), test_pass_through_successor_weak() (+3 more)

### Community 50 - "Community 50"
Cohesion: 0.36
Nodes (10): Select the resting orders of an exhausted (gen, cycle, direction) traversal.…, select_exhausted_candidates(), _order(), §5.2 step-2 cancel selector (Phase 7h-3, E2)., test_all_non_resting_excluded(), test_all_resting_selected(), test_empty_input_empty_output(), test_output_sorted_by_cloid() (+2 more)

### Community 51 - "Community 51"
Cohesion: 0.33
Nodes (10): _g(), Decimal, §7.1 geometry input validation (7e doctrine: malformed inputs raise)., test_bad_direction(), test_grid_levels_out_of_range(), test_non_decimal_params_rejected(), test_non_positive_first_distance(), test_non_positive_multipliers() (+2 more)

### Community 52 - "Community 52"
Cohesion: 0.44
Nodes (10): _markers(), _p1(), Real P1 wiring into run_pass (7g-3b): seven stages, write-only, envelopes…, test_acute_and_zeroed_paths(), test_envelopes_unread(), test_markers_absent_no_op_unchanged(), test_markers_present_writes_and_coheres(), test_only_target_fields_change() (+2 more)

### Community 53 - "Community 53"
Cohesion: 0.33
Nodes (7): batchF(), evaluate(), hard_violation(), lhs(), Mean fitness of genome row-set G averaged over several CRN streams (batch 24…, run_ga(), stream_mean()

### Community 54 - "Community 54"
Cohesion: 0.33
Nodes (9): mock_patch(), _no_ambient(), AnyEvent, Path, Replay determinism: in-memory and SQLite logs produce byte-identical output., _run(), _steps(), test_empty_log_head_is_genesis() (+1 more)

### Community 55 - "Community 55"
Cohesion: 0.33
Nodes (8): SubDecisionRecord + PassReport extension (Phase 7h-4b-2, E2)., _rec(), test_bad_stage_and_kind(), test_canonical_round_trip(), test_empty_reason_code_rejected(), test_frozen(), test_kind_outcome_mismatch(), test_subject_shapes()

### Community 56 - "Community 56"
Cohesion: 0.36
Nodes (7): P3CandidateMarkers, §4.7 P3 same-generation candidates (per pass)., _complete_window(), _glife(), Multi-pass P3 ineligibility persistence across a Cycle (Phase 7f), via…, test_later_cycle_recandidates(), test_persistent_ineligibility_same_cycle_binds_evolution()

### Community 57 - "Community 57"
Cohesion: 0.39
Nodes (8): _g(), Decimal, §7.1 base geometry (Generation 0, all cycles — R2) (Phase 7g-1)., test_base_bu_full_tuple(), test_base_ignores_dominance(), test_base_sl_full_tuple(), test_length_equals_grid_levels(), test_monotonicity()

### Community 58 - "Community 58"
Cohesion: 0.39
Nodes (8): _g(), Decimal, §7.1 successor geometry (G1+, all cycles — R2; direction-agnostic — R3)., test_base_vs_successor_differ(), test_direction_independence_r3(), test_successor_dominant_multiplier_1_5_distinguishes(), test_successor_dominant_multiplier_2(), test_successor_weak_side()

### Community 59 - "Community 59"
Cohesion: 0.32
Nodes (7): classify_remainder_hedge_status(), §11.4: skipped (terminal) -> SKIPPED_RESIDUAL_ZERO; else working/pending., §11.4 remainder tri-state (7g-3b) + 7g-3a cross-test., test_skipped_level_contributes_zero_cross_test(), test_skipped_wins_precedence(), test_truthy_int_rejected(), test_working_and_pending()

### Community 60 - "Community 60"
Cohesion: 0.32
Nodes (5): P0ObservationMarkers, _pos(), Decimal, P0 observation markers (Phase 7h-1) — a leaf. Imports ONLY the stdlib at…, The P0 stage input (markers set by tests; 7h projects from ST-04/venue).

### Community 61 - "Community 61"
Cohesion: 0.32
Nodes (6): _markers(), P1 leaf types + EPSILON_H single-source (7g-3b)., test_all_to_canonical_pass_canonical_dumps(), test_hedge_intent_frozen_and_serializes(), test_markers_frozen_and_validated(), test_market_observation_state()

### Community 62 - "Community 62"
Cohesion: 0.38
Nodes (6): mirror_eligible(), §11.3 (STR-0211): mirroring available for ACTIVE/SUCCESSOR_CREATED/DISABLED.…, §11.3 mirror eligibility (pure predicate; price formula = B2b STOP-item)…, test_eligible_lifecycles(), test_entry_intent_never_constructed(), test_ineligible_lifecycles_fail_closed()

### Community 63 - "Community 63"
Cohesion: 0.29
Nodes (5): emit_submission_command(), §9 order submission mechanics (Phase 7h-3): build CommandEvent + append +…, B1 receipt: the append outcome, reconstructable from the log (inv.19)., Build the submission ``CommandEvent`` (pure; Phase 7h-4b-2 B2.1). Holds the…, SubmissionResult

### Community 64 - "Community 64"
Cohesion: 0.43
Nodes (6): _level(), p1_exposure_markers projection by P0 (R11) + end-to-end P0->P1 pipeline (7h-1)., test_end_to_end_p0_then_p1_pipeline(), test_projection_deterministic_same_in_same_out(), test_seven_externals_carried_verbatim(), test_unobserved_rows_excluded()

### Community 65 - "Community 65"
Cohesion: 0.47
Nodes (3): _dec(), _sbool(), _sint()

### Community 66 - "Community 66"
Cohesion: 0.53
Nodes (5): Pass engine determinism + frozen guarantees (Phase 7d)., _rich_state(), test_reports_are_frozen(), test_returned_state_is_frozen(), test_run_pass_byte_identical()

### Community 68 - "Community 68"
Cohesion: 0.60
Nodes (4): Real P0 determinism (7h-1): byte-identical outputs, no input mutation., _state(), test_identical_inputs_byte_identical_outputs(), test_no_input_mutation()

### Community 69 - "Community 69"
Cohesion: 0.60
Nodes (4): _markers(), Real P1 determinism + no input mutation (7g-3b)., test_byte_identical_state_and_report(), test_no_input_mutation()

## Knowledge Gaps
- **1 isolated node(s):** `astergrid`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 473 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `canonical_dumps()` connect `Community 13` to `Community 0`, `Community 1`, `Community 2`, `Community 6`, `Community 7`, `Community 10`, `Community 11`, `Community 14`, `Community 17`, `Community 20`, `Community 23`, `Community 24`, `Community 25`, `Community 27`, `Community 28`, `Community 29`, `Community 30`, `Community 31`, `Community 33`, `Community 35`, `Community 39`, `Community 41`, `Community 46`, `Community 48`, `Community 50`, `Community 52`, `Community 55`, `Community 61`, `Community 66`, `Community 68`, `Community 69`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `State` connect `Community 38` to `Community 0`, `Community 1`, `Community 2`, `Community 7`, `Community 10`, `Community 12`, `Community 14`, `Community 15`, `Community 17`, `Community 20`, `Community 21`, `Community 22`, `Community 24`, `Community 27`, `Community 30`, `Community 32`, `Community 34`, `Community 35`, `Community 37`, `Community 39`, `Community 45`, `Community 46`, `Community 48`, `Community 52`, `Community 56`, `Community 60`, `Community 66`, `Community 68`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `EventEnvelope` connect `Community 29` to `Community 0`, `Community 1`, `Community 34`, `Community 35`, `Community 37`, `Community 46`, `Community 15`, `Community 18`, `Community 19`, `Community 20`, `Community 21`, `Community 23`, `Community 24`, `Community 26`, `Community 30`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 76 inferred relationships involving `State` (e.g. with `run_pass()` and `ArmRequestState`) actually correct?**
  _`State` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 75 inferred relationships involving `canonical_dumps()` (e.g. with `_encode()` and `test_st12_slot_accepts_sorted_and_serializes()`) actually correct?**
  _`canonical_dumps()` has 75 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `GenerationState` (e.g. with `State` and `count_active_cycles()`) actually correct?**
  _`GenerationState` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `run_pass()` (e.g. with `State` and `StageReport`) actually correct?**
  _`run_pass()` has 2 INFERRED edges - model-reasoned connections that need verification._