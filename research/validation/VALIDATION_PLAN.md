# VALIDATION_PLAN.md — Verification strategy (Phase 6a)

- **Purpose:** the verification strategy that MUST exist before Phase 7 (implementation) begins, per `prompt.md` `<implementation_rule>`. It defines HOW correctness is established for the CAND-B event-sourced runtime — not a test checklist.
- **Producer:** Claude Code (Opus 4.8), Phase 6a. **Status:** ACCEPTED as the Phase-7 entry artifact.
- **Phase-labelling note:** 6a/6b/6c are working subdivisions of `prompt.md` Phase 6 (Implementation Plan): **6a** = input preparation (this run: validation plan, venue refresh, cleanup, scheduling); **6b** = event model + interface design + CAP-0024 reference-model design; **6c** = non-blocking constraint resolution. They are not separate official phases.
- **Inputs (read-only):** `Strategy.md` (SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`); `STRATEGY_CONTRACT.md` (362 STR-*); `ARCHITECTURE_DECISION.md` (CAND-B, §5 state realization, §6 determinism, §8 recovery); `STATE_OWNERSHIP.md`; `DECISION_REGISTER.md` (DECISION-001..020); venue evidence (SRC-1xx).

---

## §1 — Purpose and scope

This plan exists to make Phase 7 *safe to start*: it names, for every correctness claim the runtime must satisfy, the mechanism that proves or falsifies it, the oracle the expected result comes from, the evidence artifact, the failure condition, and the phase of execution.

**Covers:** the deterministic domain core, its event-sourced persistence/replay, venue-boundary reconciliation, the owner-decided mitigations (DECISION-016..020 / STR-0345..0362), and the economic/accounting claims.

**Does NOT cover:** the event schema, interface signatures, snapshot policy or implementation plan (Phase 6b); technology selection (Phase 6/7); production trading code; live activation.

**Relationship to CAP-0024 (Reference Model / Differential Testing):** CAP-0024 is the **primary oracle for the deterministic core** — an independent re-derivation of expected state/events from the normative contract over the same (command, observation) sequences. Every other mechanism either composes with CAP-0024 (differential/replay/ordering/exploration) or covers what CAP-0024 cannot (venue-boundary behavior, failure injection, precision against the live venue spec, economic realism). CAP-0024 is offline and NON_RUNTIME; it must not share code with production domain logic (§4).

---

## §2 — Oracles (where expected results come from)

Authorized oracles, in priority order:

1. **`Strategy.md`** — strategy-semantics authority (immutable).
2. **`STRATEGY_CONTRACT.md`** — derived normative requirements (STR-0001..0362).
3. **CAP-0024 Reference Model** — independent re-derivation over the same commands/events (offline, no shared code).
4. **Owner Decisions** — DECISION-001..020 (bind interpretation/architecture; never override Strategy.md).
5. **Venue evidence (SRC-1xx)** — for venue-contract tests ONLY (precision, min-value, TIF, rate limits, schema).
6. **Recorded observations (Phase 10–12)** — shadow/testnet/live evidence, for economic and venue-behavior claims.

**Hard rule:** the implementation is NEVER its own oracle. Tests passing against the current implementation do not establish correctness; every expected result must trace to an oracle above. A test whose expected result cannot be traced to an authorized oracle is not a valid test (§4).

---

## §3 — Mechanisms

Each subsection: **Claim · Oracle · Evidence · Failure · Phase.**

### 3.1 Deterministic replay
- **Claim:** folding the same event sequence reproduces the same state and the same emitted events, including the §4.7 P0–P6 pass order.
- **Oracle:** CAP-0024 + canonical event order (DECISION-007).
- **Evidence:** replay-diff artifacts (state hash + emitted-event stream per fold).
- **Failure:** any divergence not attributable to a recorded input difference.
- **Phase:** 7 (core), 9 (audit).

### 3.2 Differential testing vs CAP-0024
- **Claim:** production domain logic matches the independent reference model on the same (command, observation) sequences.
- **Oracle:** CAP-0024 only.
- **Evidence:** per-scenario diff reports.
- **Failure:** any unexplained divergence.
- **Phase:** 7, 9.

### 3.3 Invariant / property tests
- **Claim:** named invariants hold across randomized and bounded-exhaustive inputs.
- **Minimum invariant set (§15 invariants + owner-decided additions):**
  * no G100 / C100 created (GenerationID/CycleID ≤ 99)
  * each Generation ≤ one successor (permanent successor lock)
  * terminal reach alone is not Evolution (7-condition verified return)
  * POSITION_VERIFIED ⇔ fill ∧ authoritative delta (never ack/price/isolated-fill alone)
  * at most one active order per Level (STR-0344)
  * skipped instance never resurrected
  * FREEZE blocks ENTRY_INTENT but not EXPOSURE_CORRECTION_INTENT
  * ExposureDelta gate uses tradability-quantized `T_enter` (STR-0345); round-to-zero below `T_exit` (STR-0346)
  * funding-bleed breaker triggers on `ACC` (STR-0352/0353); ladder warn→suspend→closure (STR-0354)
  * `acute(Δ)` never gated by the NetExpectedEdge floor (STR-0356/0357)
  * `MarginMode` pinned → startup ABORT if absent (STR-0359) / P0 FREEZE on mismatch (STR-0360)
  * intent+cloid persisted before any side effect (STR-0298)
  * GrossGridEdge = StepBps closed form applied at the arming gate (STR-0349)
- **Oracle:** STRATEGY_CONTRACT.md + Strategy.md.
- **Evidence:** property-test reports (with the reachable-input witness for any violation).
- **Failure:** any invariant violation with a reachable input.
- **Phase:** 7, 9.

### 3.4 Exhaustive state exploration (bounded)
- **Claim:** within a small bounded domain, all interleavings of terminal / return / hedge / closure / timeout / restart produce a unique deterministic outcome.
- **Domain:** ≤ 2 Generations × ≤ 2 Cycles × ≤ 2 Levels × ≤ 2 intents.
- **Oracle:** CAP-0024.
- **Evidence:** exploration report + counter-example log.
- **Failure:** any non-deterministic branching.
- **Phase:** 7, 9.

### 3.5 Failure injection
- **Claim:** a crash/disconnect between any two atomic boundaries never produces state the recovery model cannot reconcile.
- **Boundaries:** before intent-persist, after intent-persist, before sign, after sign, before send, after send, before ack, after ack, before fill, after fill, before reconcile, after reconcile, mid-TWAP, on reconnect.
- **Oracle:** recovery model (ARCHITECTURE_DECISION §8) + clearinghouseState reconciliation (DECISION-008).
- **Evidence:** per-boundary injection logs.
- **Failure:** any state that cannot be reconciled without guessing.
- **Phase:** 9.

### 3.6 Ordering / sequencing
- **Claim:** the canonical event order (venue-seq → server-ts → local-ts → monotonic counter, DECISION-007) yields identical state regardless of arrival order.
- **Oracle:** CAP-0024.
- **Evidence:** permutation-test reports.
- **Failure:** divergence under any permutation.
- **Phase:** 7, 9.

### 3.7 Duplicate / delayed / missing events
- **Claim:** snapshot duplication, late events, WS gap detection, and REST/WS disagreement all resolve deterministically per DECISION-007 and the freshness rules.
- **Oracle:** STRATEGY_CONTRACT (freshness + gap rules) + DECISION-007.
- **Evidence:** synthetic-stream tests.
- **Failure:** any resolution that violates freshness or produces dual state.
- **Phase:** 7, 9.

### 3.8 Precision / rounding
- **Claim:** every price and size conforms to venue precision (≤5 sig figs, ≤(6−szDecimals) decimals, szDecimals lot) after normalization; the non-overlap test (N1–N3 + STR-0361 ε) holds on tick-quantized submittable prices.
- **Oracle:** venue spec (SRC-108 tick-and-lot-size) + Strategy.md §6.3.
- **Evidence:** precision-test report.
- **Failure:** any venue rejection arising from reject-and-retry patterns.
- **Phase:** 7, 9.

### 3.9 Authoritative vs derived state
- **Claim:** every state has exactly one owner; venue-authoritative states (ST-08 ActualExposure, ST-17 CapitalBase) source ONLY from clearinghouseState; no derived value is used where an authoritative value is required.
- **Oracle:** STATE_OWNERSHIP.md + DECISION-002.
- **Evidence:** ownership-audit report.
- **Failure:** any read of a derived value in a path requiring authority (e.g. webData2/3 as position/capital authority).
- **Phase:** 7, 9.

### 3.10 Exposure reconciliation
- **Claim:** ExpectedExposure and ActualExposure reconcile per STR-0199 / STR-0212; the ExposureDelta gate uses `T_enter` (STR-0345); acute vs non-acute per STR-0356/0357.
- **Oracle:** STRATEGY_CONTRACT.md.
- **Evidence:** reconciliation-test reports.
- **Failure:** any unresolved delta above `T_enter` persisting beyond the recovery window.
- **Phase:** 7, 9.

### 3.11 Economic / PnL validation
- **Claim:** NET PnL (`BasketRealized + BasketUnrealized − BasketFees + BasketFunding`) governs closure and freeze per §13.1; gross PnL never substitutes (STR-0235/0250).
- **Oracle:** STRATEGY_CONTRACT.md + CAP-0024.
- **Evidence:** PnL accounting report.
- **Failure:** any gross-for-net substitution.
- **Phase:** 9, 10.

### 3.12 Fee / funding / borrowing accounting
- **Claim:** every fee/funding event is attributed to the owning Generation/Cycle/Basket, idempotent (STR-0352 accumulator, dedup key (time,coin,delta)), and included in NET PnL.
- **Oracle:** venue evidence (userFees, userFunding) + CAP-0024.
- **Evidence:** accounting-attribution report.
- **Failure:** any unattributed or double-counted event.
- **Phase:** 9, 10.

### 3.13 Transition correctness
- **Claim:** every state transition is deterministic and reconstructable (§15 inv.19 / STR-0315/0334); reason codes unique (DECISION-013).
- **Oracle:** CAP-0024.
- **Evidence:** transition-coverage report.
- **Failure:** any non-deterministic or reason-code-ambiguous transition.
- **Phase:** 7, 9.

### 3.14 Persistence / restart recovery
- **Claim:** after crash, replay + reconciliation reconstructs state without guessing (recovery model, ARCHITECTURE_DECISION §8; DECISION-008).
- **Oracle:** ARCHITECTURE_DECISION §8 + DECISION-008.
- **Evidence:** restart-test reports.
- **Failure:** any path requiring a guess.
- **Phase:** 9.

### 3.15 Negative-EV prevention
- **Claim:** the NetExpectedEdge floor prevents uneconomic arming for ENTRY and non-acute corrections (STR-0356); GGE = StepBps closed form (STR-0349) applied; validity condition (STR-0350) enforced at config resolution.
- **Oracle:** STRATEGY_CONTRACT.md.
- **Evidence:** economics-gate report.
- **Failure:** any arming below the floor (excluding acute Hedge Recovery, correctly exempt).
- **Phase:** 7, 9, 10.

### 3.16 Hard exposure constraints
- **Claim:** MaxLevelNotional, MaxLevelNotionalDominant, MaxCycleNotional, MaxGenerationNotional, MaxBasketNotional are never exceeded; rejection (not silent clipping) is the failure mode.
- **Oracle:** STRATEGY_CONTRACT.md.
- **Evidence:** cap-enforcement report.
- **Failure:** any silent clip or override.
- **Phase:** 7, 9.

### 3.17 Venue / API behavior where observable
- **Claim:** repo assumptions about the venue match current venue behavior where directly observable.
- **Oracle:** venue evidence (SRC-1xx) + recorded observations (Phase 10–12).
- **Evidence:** controlled-observation log.
- **Failure:** any documented-vs-observed divergence not captured in a conflict record.
- **Phase:** 12 (Testnet), 13 (readiness).

---

## §4 — Test-oracle independence rules

- The CAP-0024 reference model **MUST NOT share code** with the production domain logic (avoids common-mode bugs); it re-derives expected behavior independently from the normative contract.
- Every test artifact records: `Strategy.md` SHA-256, `STRATEGY_CONTRACT.md` version, config version, reference-model version, and (where applicable) venue-evidence versions (SRC ids + snapshot dates).
- Any test whose expected result cannot be traced to an authorized oracle (§2) is not a valid test and is excluded.
- The implementation is never its own oracle (restated as a gating rule for Phase 7 review).

---

## §5 — Coverage matrix (mechanism × STR-* subset)

| Mechanism | Primary STR-* / invariant groups covered |
|-----------|-------------------------------------------|
| 3.1 Replay | §15 inv.19 (STR-0315/0334); §4.7 P0–P6 (STR-0047..0053); DECISION-007 |
| 3.2 Differential vs CAP-0024 | all domain STR (CAP-0003..0018,0020,0023); §5.7 scenarios (STR-0109..0128) |
| 3.3 Invariant/property | §15 invariants (STR-0308..0335 family); STR-0344; STR-0345/0346; STR-0352/0353/0354; STR-0356/0357; STR-0358..0360; STR-0298; STR-0349 |
| 3.4 Exhaustive (bounded) | §4 Evolution (STR-0024..0067); §5 Cycle (STR-0071..0108); closure (STR-0243..0250) |
| 3.5 Failure injection | STR-0298; STR-0132/0133/0138/0314; DECISION-008; recovery §8 |
| 3.6 Ordering | STR-0063; STR-0315/0334; DECISION-007 |
| 3.7 Dup/delayed/missing | STR-0163 (freshness); STR-0200/0228; DECISION-007 |
| 3.8 Precision | STR-0135..0138, STR-0177, STR-0093; N1–N3 (STR-0104..0108) + STR-0361 |
| 3.9 Authoritative vs derived | STR-0199/0200/0224; STATE_OWNERSHIP ST-08/ST-17; DECISION-002 |
| 3.10 Exposure reconciliation | STR-0199/0212; STR-0345; STR-0356/0357 |
| 3.11 Economic / PnL | STR-0234/0235/0236/0250; §13.1 |
| 3.12 Fee/funding accounting | STR-0246; STR-0352; STR-0194/0337 |
| 3.13 Transition correctness | STR-0315/0334; DECISION-013 reason codes (STR-0055 family) |
| 3.14 Persistence/restart | ARCHITECTURE_DECISION §8; DECISION-008; STR-0298 |
| 3.15 Negative-EV | STR-0179/0193/0197/0273; STR-0349/0350/0356 |
| 3.16 Hard exposure caps | STR-0141..0161 cap family; STR-0227 |
| 3.17 Venue/API observable | [HC] STR-0133..0138, 0175, 0176, 0228, 0254, 0337; SRC-1xx |

**Unmapped STR-\*:** none within the runtime-normative set beyond the explicitly DEFERRED obligations (AMB-0034 / AMB-0035, see below). The two Phase-4.9 non-blocking additions (STR-0361 N3 ε, STR-0362 REST budget) are covered by 3.8 and (operationally) by 3.17 respectively, and are scheduled in `PHASE6_SCHEDULE.md`. **Count of STR-* with no mechanism: 0** (all 362 map to ≥1 mechanism, directly or via the differential/exhaustive mechanisms that consume the whole contract).

---

## §6 — Entry criterion for Phase 7

Phase 7 (Deterministic Core Implementation) may begin only when:
1. This plan exists (satisfied by this artifact).
2. The §5 matrix has no unmapped STR-* beyond those explicitly DEFERRED (satisfied: 0 unmapped).
3. The CAP-0024 reference-model design is agreed (Phase 6b — NOT yet done; this is the remaining gate).

Until (3), Phase 7 does not start.

---

## §7 — Live-readiness dependency (forward reference)

The following MUST be on the Live-readiness critical path (Phase 13):
- calibration of the four dynamic defaults (`CALIBRATION-REPORT.md`);
- D-16 maintenance-margin HYPOTHESIS re-validation (DECISION-006) — now additionally evidenced by the venue `marginTables`/`marginTiers` refresh (SOURCE_MANIFEST §6);
- the funding-breaker `β_F` calibration (DECISION-018 / STR-0355);
- the Gate-018 assertions verified against a real account — startup ABORT (STR-0359) + P0 FREEZE on `leverage.type`/`position.type` mismatch (STR-0360) (DECISION-020);
- OPTIONAL live `meta.maxLeverage` observation for BTC/ETH (DECISION-001).

---

## Deferred verification obligations (named, not forgotten)

- **AMB-0034 — verification obligations** (CAP-0024 reference model, invariant/property tests, exhaustive exploration, failure injection, differential replay, precision, depth, survivability, liveness, mutation testing). → Covers Phases 7 (core), 9 (audit), 10–12 (economic and venue evidence). **THIS PLAN (Phase 6a) is the first concrete artifact satisfying AMB-0034**; the remaining artifacts (the actual reports named in §3) are produced in the named phases.
- **AMB-0035 — economic/risk realism** (gap risk, execution latency, liquidity collapse, adverse selection, funding shock). → Phase 10 (economic validation) + Phase 12 (Testnet observation). **Simulation is explicitly NOT treated as proof of economic correctness** (per the GA classification, `research/findings/GA_CLASSIFICATION.md`, Phase 4.7).

Both remain DEFERRED (traceable to `SEMANTIC_AMBIGUITIES.md` rows AMB-0034 / AMB-0035), but their phase-of-resolution is now explicit.
