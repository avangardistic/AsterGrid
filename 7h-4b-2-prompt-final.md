Phase 7h-4b-2 — FINAL PROMPT (pre-flighted v3)

Base: origin/main @ 43e3170 (post-7h-4b-1 merge + ruff-format cleanup). Scope: P6-real + ST-05↔ST-04 coupling + run_pass 3-tuple + PassReport extension + P6 input slots. Later (out of scope): venue adapter + UNKNOWN_SUBMISSION recovery + signing + UI. Post-7h TBD.

Execution rule (standing, 7-for-7): every repo-answerable question PINNED with VERBATIM evidence. Zero pre-listed STOPs (Part F). Only narrow + global abort rules.

Cite-precision discipline (D13): every STR-* claim below is quoted or flagged COINED with named anchors. No paraphrase-as-VERBATIM. No counts asserted except 382 STR / 23 DECISIONs (D14).

Read the repo. Key files: src/hypergrid/core/pass_engine.py, src/hypergrid/core/state.py, src/hypergrid/core/transitions/submission.py, src/hypergrid/core/transitions/execution_cancel.py, src/hypergrid/core/transitions/order_state.py, src/hypergrid/core/transitions/level_state.py, src/hypergrid/core/transitions/arm.py, src/hypergrid/core/transitions/arm_state.py, src/hypergrid/core/transitions/ladder_issuance.py, src/hypergrid/core/transitions/cycle.py, src/hypergrid/core/transitions/cycle_state.py, src/hypergrid/core/transitions/observation.py, src/hypergrid/core/events/kinds.py, research/strategy/STRATEGY_CONTRACT.md.
Part 0 — Six open items: PRE-FLIGHTED RESOLUTIONS (all closed, verbatim evidence)
Item 1 — run_pass unpackers: 11 files (not 2), all pinned by repo-wide grep

The draft named 2 files. The pre-flight grep (run_pass over src tests docs research at e36ff02) proves 12 test files reference run_pass, of which 11 need the mechanical 2-tuple → 3-tuple edit (site counts from the grep):
File	Unpack sites	Edit
tests/test_cycle_p3_persistence.py	5 (s1, _ = …)	add 3rd _
tests/test_cycle_transition.py	1 (new, _ =, L141)	add 3rd _
tests/test_p0_determinism.py	2 (s1, r1 = …; L59 bare call needs nothing)	add 3rd _
tests/test_p0_lifecycle.py	1 (new_state, _ =, L202)	add 3rd _
tests/test_p0_markers_projection.py	1 (new_state, report =, L123)	add 3rd _
tests/test_p0_st19_population.py	3	add 3rd _
tests/test_p0_wiring.py	6 (_, report = …; L120 bare call needs nothing)	add 3rd _ + P6 status flip (§C)
tests/test_p1_determinism.py	2 (s1, r1 = …; L43 bare call needs nothing)	add 3rd _
tests/test_p1_wiring.py	8	add 3rd _ + P6 status flip (§C)
tests/test_pass_engine_determinism.py	4	add 3rd _
tests/test_pass_engine_order.py	12	add 3rd _ + _STUBBED/_REAL flip (§C)
tests/test_p0_clock_free.py	0 (L68 is a bare run_pass(state, []))	NO EDIT

Also hit (DO NOT TOUCH): research/README.md (dated historical journal entry quoting the 7d signature); src hits are the def + docstring mentions only — zero src callers of run_pass. Any further unpacker found by your own re-grep is a narrow STOP (S-3, Part F).

E1-breakage pre-check (done for you): zero of the 12 files plants st05_order_intents_and_outcomes, so B3.2/B4 cannot fire in old tests; all canonical assertions in these files are differential (before/after, empty/full — never golden dicts), so the new PassReport key and the new None-omitted State fields are safe. Your E1 must still prove it.
Item 2 — emit-vs-refactor: VERBATIM submit_order (submission.py L67–110)

Python

def submit_order(
    *,
    order: OrderState,
    tif: str,
    expires_after: int,
    intent_log_seq: int,
    port: EventLogPort,
    observed: ObservedMeta,
) -> tuple[SubmissionResult, OrderState]:
    ...
    if order.lifecycle != "INTENT_CREATED":
        raise ValueError(
            "submit_order requires an INTENT_CREATED row (double-submit guard)"
        )
    if tif not in _TIF:
        raise ValueError(f"tif must be one of {sorted(_TIF)}: {tif!r}")
    if type(expires_after) is not int or expires_after <= 0:
        raise ValueError("expires_after must be a positive int (DECISION-008)")
    if type(intent_log_seq) is not int or intent_log_seq < 0:
        raise ValueError("intent_log_seq must be an int >= 0")

    cmd = CommandEvent(
        cloid=order.intent.cloid,
        action=_ACTION_BY_ORDER_TYPE[order.intent.order_type],   # submission.py L95
        tif=tif,
        expires_after=expires_after,
        causal_predecessors=(intent_log_seq,),                   # submission.py L98
    )
    env = port.append(cmd, observed)
    ...receipt...; drift-check...; advanced = dataclasses.replace(order, lifecycle="ORDER_SUBMITTED")
    return receipt, advanced

Resolution (emit-hybrid): new pure emit_submission_command(*, order, tif, expires_after, intent_log_seq) -> CommandEvent holding the 4 validations (messages VERBATIM-identical to the 4 strings above — 7h-3 tests match on them) + the CommandEvent(...) construction; submit_order's body calls it, then port.append + receipt + the is_legal_order_transition drift-check + advance. Signature unchanged; behavior unchanged; 7h-3 tests byte-untouched.

Correction to the draft: B1.MAP (_ACTION_BY_ORDER_TYPE) lives in submission.py L40, NOT order_state.py, and maps OrderType → {"submit","twap"} (4 types → "submit", TWAP → "twap"). "cancel" is NOT a map value; action="cancel" is valid per the frozen vocab comment in kinds.py L51 (Item 3).
Item 3 — cancel TIF: VERBATIM schema + DECISION-008 (draft's None contradicted)

VERBATIM CommandEvent (core/events/kinds.py L47–56):

Python

class CommandEvent:
    """§A2(b) command — a committed side effect. Serves STR-0298/0133/0138/0254."""

    cloid: str  # §A2(b) client order id (opaque); STR-0298
    action: str  # §A2(b) action concept: submit/cancel/modify/twap
    tif: str  # §A2(b) TIF concept (Alo/Gtc/Ioc); STR-0133
    # Originating intent is referenced via causal_predecessors (§A2(b)).
    expires_after: int | None = None  # §A2(b) expiresAfter concept; DECISION-008
    causal_predecessors: tuple[int, ...] = ()  # EVENT_MODEL §A3

tif is a non-optional str. The cancel↔TIF hunt over Strategy.md finds three cancel sentences, NONE naming a TIF: L362 ("Cancel all pending (not POSITION_VERIFIED) orders …"), L715 (SEMI timeout → "cancel, return to IDLE/PRECHECK" — an arm-request cancel), L797 (REPRICE — "cancel and re-arm"). Re-grep at execution; if a cancel↔TIF sentence exists, narrow STOP S-1.

Resolution: tif="Gtc" default is COINED (anchors: schema non-optional str; §6.2 TIF set {Gtc, Ioc, Alo} at L574 — draft's "L573" corrected; no Strategy sentence ties cancel to a TIF). No freeze exception; no schema change.

Major correction to the draft: the draft's expires_after=None for cancels contradicts DECISION-008 (research/decisions/DECISION_REGISTER.md L128, verbatim): "…persist intent+cloid BEFORE any side effect; use expiresAfter on actions; …". A cancel IS an action (action="cancel" ∈ frozen vocab). The schema's None default is permissiveness, not permission. Therefore emit_cancel_command takes REQUIRED expires_after: int (> 0, same validation/message shape as submit).
Item 4 — PassReport home: VERBATIM quotes + schema fix

VERBATIM PassReport (pass_engine.py L50–56) and StageReport (markers.py L28–35) confirmed exactly as the draft quoted. markers.py stays frozen (byte-identical). pass_engine.py is per-phase-untouched → this phase's edit is a normal pre-authorized edit, not a freeze exception.

Schema fix (draft gap): the draft's 4-field SubDecisionRecord (sub_kind/outcome/reason_codes/notes) cannot support its own specified ordering (stage_order, sub_kind, cloid) — there is no stage/cloid field, and ladder records have no cloid. Final schema (B5): 6 fields — stage, sub_kind, subject (cloid for order-kinds; G{gg:02d}-C{cc:02d}-{BU|SL} for ladder-kinds), outcome (kind-compat matrix), reason_codes, notes. All COINED with per-kind §-anchors (B5). Ordering: (stage_order, sub_kind, subject) ascending, sorted by P6 (construction-order-proof).
Item 5 — coupling direction: COINED, three VERBATIM anchors (all re-verified)

    §6.1 L570: **Hard rule:** `LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED`. … — joint invariant (also contracted as STR-0131, STRATEGY_CONTRACT.md L1097 — cite both).
    §6.1 diagram L561–568 (quoted for the level prefix the draft omitted): INTENT_CREATED → … → POSITION_VERIFIED, ↘ CANCELLED, → EMERGENCY … → SKIPPED …, → ERROR …, and Protection-locked levels additionally start: LOCKED → IDLE.
    STR-0152 (contract L1293, wording VERBATIM): "Unlocking makes the level eligible to arm, but arming still passes through the full Pending Order Architecture gate list (§8) — including the Fillability Analyzer and Cost Analyzer — before any live order is placed." (STR-0151 L1286 corroborates the unlock condition.)
    STR-0190 (contract L1607, wording VERBATIM): "LEVEL_SKIPPED is a first-class terminal state, not an error: per-level (never blocks or holds subsequent levels), no automatic retry within the same Cycle" (+ STR-0191 L1614 zero-exposure; STR-0192 L1621 never-resurrected).
    Hunt: no Strategy sentence states a gating direction (gates the order/level → zero hits). Direction ST-04 gates; ST-05 pipelines is COINED (flagged in the module docstring). If a contradicting sentence is found at execution, narrow STOP S-2.
    R10c interplay (pre-flight derived): R10c (level_state.py L107–110) enforces is_protection_locked ⟺ lifecycle == "LOCKED" whenever lifecycle is set — hence a LEVEL_SKIPPED row is ALWAYS unlocked. B4.2 needs no lock guard. Conversely P0 can never record LEVEL_SKIPPED on a locked row (ctor ValueError) — pre-existing seam, out of scope.

Item 6 — R10c first-observation: THE DRAFT'S RESOLUTION WAS FACTUALLY WRONG

The draft claimed "7h-4b-1's issue_fresh_ladder constructs LevelState rows with … lifecycle="LOCKED" … The first observation is at construction." FALSE. Verbatim ladder_issuance.py L97: # pre-observation rows: lifecycle/filled None (R10c skipped by ctor). Issuance rows carry lifecycle=None, filled_quantity=None; R10c is skipped.

The actual first observer is P0, not P6. Verbatim observation.py extend_level_states docstring: "Upsert observed fill/lifecycle onto EXISTING ST-04 rows (R10; fail-closed). P0 never CREATES geometry rows … an observation for an identity not already present is a ValueError. … Each replaced row is rebuilt via dataclasses.replace, so LevelState re-validates and the R10c lock coherence … surfaces any drift as a ValueError." Repo-wide grep: no src code sets LevelState.lifecycle except P0; try_unlock has zero in-tree callers (unlock is out of scope).

Resolution: P6 appends pre-observation rows (lifecycle=None); B4.3 writes lifecycle ONLY when None (provisional order-side observation — P0's venue recording overwrites it next pass; any disagreement trips R10c by construction). The draft's "every row carries a lifecycle / no partial rows" invariant is dropped as contrary to the merged tree.
Part A — Scope
A1. Build

    B0 — P6 input slots. New core/transitions/p6_state.py: P6ArmInput (26 fields), P6CancelInput (4), P6IssuanceInput (12) — frozen, validated, canonical. Three new State fields (None-able, sorted, no-dups, None-omitted canonical). NO STATE_OWNERSHIP.md edit: pre-flight verified it covers ST-01..ST-23 only (90 lines; p0/p1/p2/p3/p4/cycle marker slots all absent) — marker slots stay out per precedent. (Why: P6 is markers-fed per the 7d DESIGN RULE; arm/issuance/cancel params exist NOWHERE in State, and config/schema.py holds §14 file-models, not runtime state. Tests plant them — the 7d precedent: "set directly by tests". evaluate_arm_gates' 16 required params minus 2 row-derivable = 14 planted + 3 emission + 9 wait/calibratable.)
    B1 — run_pass 3-tuple (State, PassReport, tuple[CommandEvent, ...]); emitted ordering (sub_kind_order, cloid) with {"CANCEL_SELECT": 0, "SUBMISSION_EMIT": 1}; purity kept; D11 extended.
    B2 — emit_submission_command + emit_cancel_command (pure; Item 2/3); internal submit_order refactor (validations move verbatim; drift-check + receipt + advance stay).
    B3 — P6-real as apply_p6(state) in new core/transitions/p6_stage.py (P0/P1/P5 precedent: stage logic lives in its own transitions module; pass_engine.py only threads). Sub-decision order CANCEL → ARM/EVAL+EMIT → LADDER → COUPLE mirrors §5.2 S2→S8 (fresh rows arm NEXT pass).
    B4 — apply_pipeline_coupling(state) -> State in new core/transitions/pipeline_coupling.py (COINED direction, Item 5; B4.1 source-enforced, B4.2 narrow, B4.3 None-only, B4.4 passthrough).
    B5 — PassReport extension (sub_decisions, default ()) + new core/transitions/pass_report_ext.py (SubDecisionRecord, B5 schema).

A2. Non-goals (all explicit)

§10 economics / gates (consume edge_clears_floor as a planted bool — P6 NEVER calls economics.*); §12.1 bounds (consume); venue adapter / ack / fill / UNKNOWN_SUBMISSION / signing / UI (post-7h); ST-18, ST-06; reason_codes.py frozen at 15 (P6 report codes are module-local coined plain strings, the 7h-3 CancelReasonCode precedent — StageReport's 7d-era comment stays stale, markers.py byte-identical); core/events/* frozen; markers.py frozen; cycle_state.py frozen (no exhausted-side field — B3.1 breadth decision instead); prompt.md conflicted, non-authoritative. P6 NEVER writes ST-05 (the post-7h adapter advances rows via submit_order: at-least-once emission + idempotent cloid (§6.2) + harness-threading between passes; re-emission while still-resting is CORRECT). P6 NEVER writes ST-12 (WAITING re-evaluates next pass from fresh inputs; threading WAITING→ST-12 is a later phase — note as seam S-2 in the report).
Part B — Behavior specification
B0 — P6 input markers (p6_state.py, new) + State slots

All three: @dataclass(frozen=True, slots=True), to_canonical_obj, fail-closed __post_init__ (exact-bool via type(x) is bool, exact-int via type(x) is not int, Decimal-instance, ranges). Import vocab ONLY from arm_state.py (OperationalState L78, ArmPolicy L53, OperatorDecision L71) and arm.py constants (MIN_DEPTH_MULTIPLE, DISTANCE_BAND, MARGIN_BUFFER_MULT, OPEN_ORDER_CAP, EDGE_FLOOR_BPS) — never redefine a default.

    P6ArmInput (26 fields, all kw): cloid: str (non-empty, the join key); generation_disabled: bool; book_depth_at_target: Decimal (≥ 0); distance_bps: int (≥ 0); min_order_size: Decimal (> 0); margin_available: Decimal (≥ 0); margin_required: Decimal (≥ 0); exposure_caps_ok: bool; open_order_count: int (≥ 0); price_normalized_ok: bool; size_normalized_ok: bool; market_state: OperationalState (isinstance); net_expected_edge_bps: Decimal (any sign); policy: ArmPolicy | None; timeout_s: int | None (None or ≥ 0); decision: OperatorDecision | None = None; elapsed_s: int = 0 (≥ 0); webhook_error: bool = False; tif: str (∈ {Gtc,Ioc,Alo}); expires_after: int (> 0, DECISION-008); intent_log_seq: int (≥ 0); min_depth_multiple: int = MIN_DEPTH_MULTIPLE (> 0); distance_band: tuple[int, int] = DISTANCE_BAND (2 ints, lo ≤ hi); margin_buffer_mult: Decimal = MARGIN_BUFFER_MULT (≥ 0); open_order_cap: int = OPEN_ORDER_CAP (> 0); edge_floor_bps: Decimal = EDGE_FLOOR_BPS (any sign). (decision_by deliberately absent — arm.py ignores it: _ = decision_by.)
    P6CancelInput (4 fields): cloid: str (non-empty); tif: str = "Gtc" (∈ set; the Item-3 COINED default carried); expires_after: int (> 0, DECISION-008, REQUIRED); intent_log_seq: int (≥ 0, REQUIRED).
    P6IssuanceInput (12 fields): generation_id: int, cycle_id: int (exact, 0..99); grid_levels: int (exact, 1..12; E2 primarily uses 6 per STR-0262 GridLevels-FIXED); step_bps: Decimal, first_level_distance_bps: Decimal (> 0); is_dominant_bu: bool, is_dominant_sl: bool; gen2_distance_multiplier: Decimal, weak_side_first_level_multiplier: Decimal (> 0); size_notional_usd: Decimal (> 0); edge_clears_floor_bu: bool, edge_clears_floor_sl: bool.
    State (pre-authorized edit): p6_arm_inputs: tuple[P6ArmInput, ...] | None = None, p6_cancel_inputs: tuple[P6CancelInput, ...] | None = None, p6_issuance_inputs: tuple[P6IssuanceInput, ...] | None = None. Validation (same style as ST-04/ST-05): arm/cancel sorted by cloid no-dups; issuance sorted by (generation_id, cycle_id) no-dups. Canonical: omitted when None (R-JSON-6); else lists of to_canonical_obj().
    Dangling-input doctrine (D15): these are OPERATOR INTENTS, not venue reads — an input row whose target is absent/not-ready is SKIPPED SILENTLY and retried next pass (STR-0063: "any event not executed in this pass is re-evaluated in the next"). This differs from P0's loud unknown-identity ValueError PRINCIPLED: P0's observations are authoritative venue reads (unknown identity = corrupted pipeline = loud); P6's inputs may be legitimately premature (loud would false-trip). ValueError ONLY for malformed rows (ctor), dup keys (State ctor), dup issuance identities (State ctor), and coupling violations (B4.2/B4.3-incoherence). Document D15 in p6_state.py's docstring.

B1 — run_pass signature (frozen)

Python

def run_pass(
    state: State,
    envelopes: Iterable[EventEnvelope],
) -> tuple[State, PassReport, tuple[CommandEvent, ...]]:

Element 3 = P6's emitted CommandEvents, sorted by (sub_kind_order, cloid) ascending, sub_kind_order = {"CANCEL_SELECT": 0, "SUBMISSION_EMIT": 1} (ladder issuance emits no command). run_pass stays pure/total/clock-free/deterministic; input iterable still materialized once. pass_engine.py: rewrite the module docstring's P6 line (P6 … — REAL (transitions.p6_stage)) + the (state', report) sentence → 3-tuple; DELETE _stub (now unused — all seven stages real) + its call site (L122); thread apply_p6. D11: NO EventLogPort/event_log import in pass_engine.py OR p6_stage.py (structural E2 test over both files' sources).
B2 — emission helpers

B2.1 — emit_submission_command(*, order: OrderState, tif: str, expires_after: int, intent_log_seq: int) -> CommandEvent (in submission.py, additive). The 4 submit_order validations with VERBATIM-identical messages (Item 2) + the CommandEvent(cloid=order.intent.cloid, action=_ACTION_BY_ORDER_TYPE[order.intent.order_type], tif=tif, expires_after=expires_after, causal_predecessors=(intent_log_seq,)) construction. submit_order body becomes: cmd = emit_submission_command(...) → port.append → receipt → drift-check → advance. Cite: 7h-3 §B1; STR-0298; §6.2.

B2.2 — emit_cancel_command(*, cloid: str, tif: str = "Gtc", expires_after: int, intent_log_seq: int) -> CommandEvent (in execution_cancel.py, additive). Validations: cloid non-empty str; tif ∈ set; expires_after exact-int > 0 (DECISION-008, message mirrors submit's); intent_log_seq exact-int ≥ 0. Returns CommandEvent(cloid=cloid, action="cancel", tif=tif, expires_after=expires_after, causal_predecessors=(intent_log_seq,)). action="cancel" pinned literal (frozen vocab, kinds.py L51). Cite: §6.2 (TIF set); STR-0075 (step 2).
B3 — P6-real (apply_p6(state) -> tuple[State, StageReport, tuple[SubDecisionRecord, ...], tuple[CommandEvent, ...]])

Sub-decision construction order (mirrors §5.2 S2→S8): B3.1 → B3.2 → B3.3 → B3.4. Final sub_decisions sorted by (stage_order, sub_kind, subject); final emitted sorted by (sub_kind_order, cloid) — both construction-order-proof.

B3.1 — CANCEL_SELECT. For each ST-03 row with lifecycle == "COMPLETED" (tuple order), for direction in ("BU", "SL"): select_exhausted_candidates(order_rows, gid, cid, direction) over st05_order_intents_and_outcomes or (). Breadth COINED (marker names no side — CycleTerminalMarkers L134–153 has no direction field): BOTH directions of a completed cycle (anchors: STR-0075's "exhausted traversal"; STR-0080's BOTH-groups re-issuance ⇒ the whole (G,C) book is stale; §5.2 L362 "Cancel all pending"). Per candidate: look up P6CancelInput by cloid — absent ⇒ skip silently (D15). Else emit_cancel_command(...); record SubDecisionRecord("P6", "CANCEL_SELECT", cloid, "EMITTED", (EXHAUSTED_TRAVERSAL_CANCEL,), notes=f"exhausted G{gid:02d}-C{cid:02d}-{direction}: cancel {cloid}"). Idempotence: the _RESTING set excludes already-CANCELLED; harness advances lifecycles between passes. ST-03 None ⇒ no-op.

B3.2 — ARMING_EVAL + SUBMISSION_EMIT. For each ST-05 row (cloid order) with lifecycle == "INTENT_CREATED": (1) join the ST-04 row on (target_generation_id, target_cycle_id, target_level_id, target_direction) — miss ⇒ skip silently (D15/STR-0063: the level may issue next pass); (2) skip silently if lvl.is_protection_locked (B4.1 enforced at the source); (3) skip silently if lvl.lifecycle not in (None, "IDLE") (resurrection/exclusivity guard: armed/progressed/terminal instances never re-arm — LOCKED→IDLE is §6.1's unlock prefix; None = pre-observation, e.g. dominant L1, immediately armable); (4) look up P6ArmInput by cloid — absent ⇒ skip silently (D15, no record); (5) call evaluate_arm_gates with the EXPLICIT mapping: intent=row.intent.intent_tag, order_size=row.intent.requested_size, every other param ← same-named input field (decision_by never passed); (6) record ARMING_EVAL with outcome ARMED|BLOCKED|WAITING ← ArmOutcome, reason_codes=(code.value,) iff code is not None, notes=f"{cloid}: {outcome}" + (f" {code.value}" if code else ""); (7) iff ARMED: emit_submission_command(order=row, tif=in.tif, expires_after=in.expires_after, intent_log_seq=in.intent_log_seq), append to emitted, record SUBMISSION_EMIT/EMITTED with reason_codes=(), notes=f"{cloid}: {cmd.action} tif={tif} expires_after={n} seq={s}".

B3.3 — LADDER_ISSUANCE_BU/SL. For each P6IssuanceInput (slot order): preconditions — ST-03 (G,C) present with lifecycle == "ACTIVE" (P5's S6 leaves exactly this; same-pass chaining works), ST-10 record for (G,C) present (reference = the S7-captured reference for the NEW cycle — cycle_state.py L69), and NO ST-04 rows for (G,C) yet — else skip silently (D15/STR-0063: reference-not-captured or already-issued). Call issue_fresh_ladder(reference_price=st10.reference, direction="BU"/"SL", grid_levels=…, step_bps=…, first_level_distance_bps=…, is_dominant=in.is_dominant_bu/sl, gen2_distance_multiplier=…, weak_side_first_level_multiplier=…, size_notional_usd=…, edge_clears_floor=in.edge_clears_floor_bu/sl, current_generation_id=G, current_cycle_id=C). Call BU first, then SL (either may return ()). Non-atomicity COINED-normal (anchors: STR-0197 per-path do-not-arm; STR-0190 per-level independence; L1188 "A skipped level is preferable to an unsafe or economically irrational execution"; STR-0080 failure_behavior: gate failures per §8): the non-empty side's rows are appended; the empty side yields an EMPTY record with NO reason code — an economics-gate outcome is designed behavior, not a reconciliation case (deviation from the draft, reasoned here). Records: LADDER_ISSUANCE_BU/SL, subject f"G{G:02d}-C{C:02d}-{group}", outcome ISSUED (rows > 0, reason_codes=()) / EMPTY, notes f"G{G:02d}-C{C:02d}-{group}: {k} levels" / f"G{G:02d}-C{C:02d}-{group}: empty (edge below floor)". Append: sorted(existing + new) by the ST-04 key; duplicate identity ⇒ ValueError via the State ctor (fail-closed; E2 pins).

B3.4 — coupling post-pass. state = apply_pipeline_coupling(state) on the post-issuance state. A B4 raise propagates out of run_pass (pass-atomic fail-closed: the caller keeps the pre-pass state).

P6 StageReport: stage="P6"; status="APPLIED" iff sub_decisions != () else "NO_OP" (a traced evaluation IS observable work); reason_codes = first-seen union across sub_decisions (sorted order); notes = "P6: no sub-decisions" when empty, else "P6: " + ", ".join(f"{n}x{kind}") over kinds in fixed order (CANCEL_SELECT, ARMING_EVAL, SUBMISSION_EMIT, LADDER_ISSUANCE_BU, LADDER_ISSUANCE_SL) omitting zeros — ASCII only (no RUF001-ambiguous glyphs). E2 asserts exact strings.

Fail-closed cites (VERBATIM, both — no STR-0325): STR-0108 (contract L923): "the Cycle transition is BLOCKED (fail-closed, §5.2 step 4); RECONCILIATION_REQUIRED is raised; …"; STR-0098 (contract L841): "the transition is BLOCKED (fail-closed) … a RECONCILIATION_REQUIRED condition is raised; …". P6 position cite: STR-0063 (contract L565) + §4.7 L333 ("P6 LEVEL ARMING / ORDER PLACEMENT proceeds only after all transitions").
B4 — coupling (apply_pipeline_coupling(state: State) -> State; pure, total-on-valid, clock-free)

Reads ST-04 + ST-05; writes ST-04 ONLY (B4.3); raises on B4.2/B4.3-incoherence. Either slot None ⇒ return state (B4.4). Index ST-05 by (target_generation_id, target_cycle_id, target_level_id, target_direction). Tuple order PRESERVED (index-based replace, P0 precedent).

    B4.1 — locked-hold. A locked level never arms. Enforced at the B3.2 filter (source), stated here as the rule. (No post-pass scan: P6 is the only armer.)
    B4.2 — skip-cap (NARROW, sound). Iff ST-04 lifecycle == "LEVEL_SKIPPED" AND a matching ST-05 row is at INTENT_CREATED ⇒ ValueError("RECONCILIATION_REQUIRED: …") (resurrection attempt — STR-0190/0192). ALL other combinations ⇒ B4.4-independent — deliberate: _SKIPPABLE (level_state.py) PROVES skip-with-live-order is a legitimate transient, so any broader rule (e.g. the draft's "past SKIPPED" — ill-defined over branch lifecycles) would false-trip. Message MUST contain RECONCILIATION_REQUIRED.
    B4.3 — position-verified advance (None-only, unlocked-only). Iff ST-04 lifecycle is None AND not is_protection_locked AND a matching ST-05 row is at POSITION_VERIFIED ⇒ dataclasses.replace(row, lifecycle="POSITION_VERIFIED") (R10c-safe: unlocked + non-LOCKED). This is a PROVISIONAL order-side observation — P0's venue recording overwrites it next pass; disagreement trips R10c by construction (Item 6). Incoherence: locked row + matching POSITION_VERIFIED order (locked ⟹ unarmed per B4.1, yet filled) ⇒ ValueError("RECONCILIATION_REQUIRED: …").
    B4.4 — independent otherwise (including LEVEL_SKIPPED + terminal/live ST-05, IDLE + anything, set-lifecycle + anything).

Cite: STR-0131 + L570 (joint invariant); STR-0152 (unlock precedes arming); STR-0190/0191 (level-side terminal).
B5 — pass_report_ext.py (new) + PassReport extension

Python

@dataclass(frozen=True, slots=True)
class SubDecisionRecord:
    stage: str            # ∈ {"P0".."P6"} (this phase always "P6"; set-membership validated)
    sub_kind: str         # ∈ {CANCEL_SELECT, ARMING_EVAL, SUBMISSION_EMIT,
                          #    LADDER_ISSUANCE_BU, LADDER_ISSUANCE_SL}
    subject: str          # order-kinds: the cloid (non-empty); ladder-kinds:
                          # f"G{gg:02d}-C{cc:02d}-{BU|SL}" (regex-validated)
    outcome: str          # kind-compat matrix (below); else ValueError
    reason_codes: tuple[str, ...] = ()   # non-empty plain-string code values
    notes: str = ""       # deterministic (no clock/random/repr)
    def to_canonical_obj(self) -> dict[str, object]: ...  # all six keys

Kind-compat (COINED, each anchored in its field comment): CANCEL_SELECT → {EMITTED} ← STR-0075; ARMING_EVAL → {ARMED, BLOCKED, WAITING} ← §8 (STR-0173..0181); SUBMISSION_EMIT → {EMITTED} ← STR-0182; LADDER_ISSUANCE_BU/SL → {ISSUED, EMPTY} ← STR-0080. stage_order = {"P0": 0, …, "P6": 6}; P6 sorts sub_decisions by (stage_order, sub_kind, subject).

PassReport (in pass_engine.py): add sub_decisions: tuple[SubDecisionRecord, ...] = () (default preserves PassReport(stages=...) constructions); to_canonical_obj gains "sub_decisions": [r.to_canonical_obj() for r in self.sub_decisions]. Cite: STR-0063; the held traceability demand.
Part C — Code placement + pre-authorized edits (closed list)

New: core/transitions/p6_state.py (B0) · core/transitions/p6_stage.py (B3) · core/transitions/pipeline_coupling.py (B4) · core/transitions/pass_report_ext.py (B5). Additive: submission.py (+emit_submission_command, internal refactor) · execution_cancel.py (+emit_cancel_command). Pre-authorized edits: pass_engine.py (docstring + delete _stub + thread apply_p6 + PassReport field) · state.py (3 slots + validation + canonical) · transitions/__init__.py (re-exports in isort position: SubDecisionRecord, P6ArmInput, P6CancelInput, P6IssuanceInput, apply_p6, apply_pipeline_coupling, emit_submission_command, emit_cancel_command — apply_* export precedented by apply_p0/cycle/locks). New tests: test_p6_stage.py, test_pipeline_coupling.py, test_pass_report_ext.py, test_p6_inputs.py.

Pre-authorized EXISTING-test edits (11 files, NOTHING else): the mechanical unpack (x, y = run_pass(...) → x, y, _ = run_pass(...); bare calls untouched) in the 11 files of Item 1, PLUS three status flips: (i) test_pass_engine_order.py: _STUBBED = ("P6",) → _STUBBED = (), _REAL gains "P6", comment → "P0 real in 7h-1; P1 in 7g-3b; P5 in 7f; P6 in 7h-4b-2"; (ii) test_p0_wiring.py L96: by["P6"].status == "STUBBED" → "NO_OP"; (iii) test_p1_wiring.py L59–61: comment + assert → "NO_OP". No pyproject.toml / reason_codes.py / markers.py / cycle_state.py / events/* change.
Part D — Standing engineering rules

D1–D10 unchanged (Decimal-only money; exact bool/int; frozen dataclasses; total-on-valid; deterministic; canonical JSON; no clock/random/repr; module import discipline — p6_stage.py MUST NOT import core.state/event_log at runtime (TYPE_CHECKING only for State), p6_state.py imports arm_state/arm constants only; submission.py keeps its no-core.state/core.pass_engine rule).

D11 — emission-vs-append. No EventLogPort/event_log import in pass_engine.py OR p6_stage.py. Structural E2 test over both sources.
D12 — 3-tuple discipline. Only pass_engine.py + the 11 pre-authorized test files + new tests unpack three elements.
D13 — cite-precision. Every STR-* claim quoted or COINED-with-anchors. (Learned from STR-0325, STR-0262, B1.MAP-home.)
D14 — counts. 382 STR / 23 DECISIONs only. No other counts asserted.
D15 — quiet-retry for operator inputs. P6 input rows with absent/not-ready targets skip silently (STR-0063); loud ValueError only for malformed rows, dup keys/identities, and B4 violations. (Vs P0's loud venue reads — principled distinction, B0.)
Part E — Tests
E1 — Suite, types, hygiene

Full suite green at base 496 + new; mypy --strict delta-empty vs base (119 errors / 132 files — compare sorted error lists BOTH directions); ruff check + ruff format --check clean; diff touches ONLY Part-C files (verify: git status --short + git diff --stat).
E2 — Behavior matrices (every row covered; report the exact new-suite split)

test_p6_stage.py: empty state → P6 NO_OP + () emitted + "P6: no sub-decisions"; 3-tuple shape (tuple[CommandEvent, ...]); cancel emission incl. default tif="Gtc" + expires_after carried + notes exact; cancel needs input row (absent ⇒ silent, no record); cancel both-directions breadth; non-COMPLETED cycle ⇒ no cancel; already-CANCELLED rows excluded; non-RESTING excluded; arm BLOCKED (gate code in record, no emission) + ARMED (one submit/twap command, fields exact) + WAITING (SEMI no-decision, no emission); arm skips locked / non-{None,IDLE} / join-miss / input-absent rows silently; evaluate-mapping fidelity (spot: order_size ← requested_size, intent ← intent_tag); issuance ISSUED (rows appended sorted, pre-observation Nones, reference ← ST-10) + one-side-EMPTY (non-atomic append, NO RECON code, APPLIED) + both-EMPTY; issuance skips (ST-03 not ACTIVE / ST-10 missing / ST-04 present); dup issuance ⇒ ValueError; emitted ordering (kind, cloid) incl. cross-kind interleave; sub_decisions ordering (stage, kind, subject) incl. shuffled-construction; P6 notes exact ("P6: 2xCANCEL_SELECT, 1xSUBMISSION_EMIT"-shape); reason-code first-seen union; D11 structural (both files); type(x) is bool guard spot (e.g. edge_clears_floor=1 ⇒ ValueError).

test_pipeline_coupling.py: None-slot passthroughs (both/either); skip-cap raise (LEVEL_SKIPPED + INTENT_CREATED, match="RECONCILIATION_REQUIRED") + independence matrix (LEVEL_SKIPPED × {RESTING, FILLED, POSITION_VERIFIED, CANCELLED, SKIPPED, ERROR} ⇒ unchanged); B4.3 write (None + unlocked + PV ⇒ POSITION_VERIFIED, order preserved) + guards (set-lifecycle / locked ⇒ unchanged); locked + PV ⇒ raise; multi-row join correctness (wrong-level rows untouched); determinism (byte-identical canonical).

test_pass_report_ext.py: frozen/slots; field validations (bad stage / bad kind / bad subject both shapes / kind-outcome mismatch / empty code string) ⇒ ValueError; PassReport(stages=...) backward-compat (defaults ()); canonical round-trip incl. canonical_dumps; ordering map values.

test_p6_inputs.py: per-class happy-path + canonical; every validation from B0 (exact-bool/int traps, Decimal-instance, ranges, tif set, band shape); slot sorting/dup rules via State(...) construction (arm/cancel cloid order + dups ⇒ ValueError; issuance (gen,cycle) order + dups ⇒ ValueError); canonical omit-when-None (byte-compare vs pre-phase State canonical on empty state).
E3 — Pipeline, persistence

End-to-end ONE pass: ST-03 (0,5) ACTIVE + full terminal marker (S2✓ S3✓ N-fallback✓ ladder_gate_passed✓ reference✓) ⇒ P5 COMPLETED + successor ACTIVE + ST-10 (0,6); issuance inputs for (0,6) ⇒ P6 appends BU+SL rows (sorted, pre-observation); an older COMPLETED cycle + resting ST-05 + cancel inputs ⇒ cancels emitted; an unlocked idle level + INTENT_CREATED ST-05 + arm inputs (AUTO, gates pass) ⇒ submission emitted; assert the 3-tuple, sorted sub_decisions, sorted emitted, APPLIED, canonical_dumps(state) + canonical_dumps(report) stable across two runs. Unchanged-surface check: reason_codes.py, markers.py, cycle_state.py, core/events/*, Strategy.md, prompt.md, pyproject.toml, STATE_OWNERSHIP.md, and every existing test file beyond Part C — all empty diff / byte-identical.
Part F — STOPs

Zero pre-listed. Narrow function-level STOPs only: S-1 (Item 3) — a Strategy sentence tying a cancel to a TIF (re-grep; quote it). S-2 (Item 5) — a Strategy sentence contradicting the COINED direction (quote it). S-3 (Item 1) — a run_pass unpacker beyond the 11 files (re-grep src tests; research/README.md excluded — historical). S-4 (D11) — any pressure to import EventLogPort/event_log into pass_engine.py/p6_stage.py. Global abort: any E1 breakage, any edit needed outside Part C, any genuinely unresolvable question → STOP with failing artifact + citations + the exact function-level question.
Part G — Deliverables

    p6_state.py, p6_stage.py, pipeline_coupling.py, pass_report_ext.py (new); submission.py, execution_cancel.py (additive); pass_engine.py, state.py, __init__.py (pre-authorized).
    Tests: 4 new files + the 11-file pre-authorized edits (unpack + 3 status flips, NOTHING else).
    Report: true counts (new tests + suite total, exact per-file split), mypy/ruff evidence (both-direction error-list diff), coined-vocab inventory (every COINED + anchors), seam confirmations (S-1 P5→P6 same-pass chaining; S-2 ST-12 non-write; S-3 P0-wins-next-pass; S-4 adapter/ST-05), pre-authorized edits listed file-by-file, all 6 Item resolutions confirmed verbatim.

Part H — Acceptance checklist

    E1 all green (496 + new); diff touches ONLY Part-C files.
    run_pass 3-tuple; only pre-authorized unpackers.
    D11 holds over pass_engine.py + p6_stage.py (structural test).
    D13/D14/D15 hold (cite-precision; counts; quiet-retry).
    All 6 Part-0 items resolved with VERBATIM evidence (file + lines).
    E3 e2e incl. same-pass P5→P6 chaining + unchanged-surface check.

Appendix — Pinned readings (7h-4b-2)

    P1 §10/economics.py owned by 7h-4b-1. P6 consumes edge_clears_floor as a planted bool; NEVER calls economics.*.
    P2 STR-0080 (contract L697; wording "Issue a fresh ladder for BOTH groups …"). Non-atomicity COINED-normal (B3.3 anchors); NO RECON on EMPTY.
    P3 STR-0108 (L923) + STR-0098 (L841) VERBATIM fail-closed→RECON pattern. No STR-0325.
    P4 Coupling anchors: L570 + STR-0131 (L1097) + §6.1 diagram L561–568 + STR-0151/0152 (L1286/1293) + STR-0190/0191/0192 (L1607/1614/1621). Direction COINED.
    P5 STR-0063 (L565; "unexecuted → next pass") ⇒ D15 quiet-retry. P6 position: §4.7 L333.
    P6 Consumed APIs (verbatim-quoted in Part 0): evaluate_arm_gates (arm.py L99) + ARM_* vocab (arm_state.py) + constants (arm.py); select_exhausted_candidates + _RESTING + CancelReasonCode (execution_cancel.py L31/55/69); issue_fresh_ladder 12 params (ladder_issuance.py); submit_order (submission.py L67–110); ST-03/ST-10/CycleTerminalMarkers (cycle_state.py L43/65/134); P0 extend_level_states (first lifecycle observer).
    P7 reason_codes.py frozen at 15 (RECONCILIATION_REQUIRED = L64, VERBATIM).
    P8 pass_engine.py per-phase-untouched; this edit is a normal pre-authorized edit.
    P9 markers.py frozen; cycle_state.py frozen; core/events/* frozen.
    P10 Counts: 382 STR / 23 DECISIONs only (re-verified at e36ff02).
    P11 prompt.md conflicted (re-verified e36ff02): unreadable, non-authoritative.
    P12 P6 NEVER writes ST-05 (adapter owns via submit_order) nor ST-12 (future phase). At-least-once + idempotent-cloid + harness-threading (A2).

Branch: claude/7h-4b-2-p6-real (from origin/main @ 43e3170). Single commit. Report per Part G.3.

END OF 7h-4b-2 Final PROMPT (v3, pre-flighted).