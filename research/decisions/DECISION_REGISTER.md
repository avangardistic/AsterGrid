# DECISION_REGISTER.md

- **Purpose:** Authoritative register of material Owner decisions made during this program (per `prompt.md` `<decision_register>`). Each decision is traceable and supersedes nothing in `Strategy.md` (which is immutable); decisions bind interpretation/architecture layers only.
- **Producer:** Claude Code (Opus 4.8), Phase 3.
- **Status:** ACTIVE. Newest decisions appended.

---

## DECISION-001 — BTC/ETH max leverage figure in §16 (from OWNER_GATE_001 / CONFLICT-001)

- **decision_id:** DECISION-001
- **question:** Is the "BTC/ETH max leverage = 40x" figure in `Strategy.md` §16 binding, given the docs are internally inconsistent (liquidations prose 40x vs info `meta` example 50x) and the runtime clamps `Leverage_effective = min(Leverage_user=3, MaxLeverage_asset) = 3`?
- **context:** §16 uses "40x" only in the mechanics *preamble* to illustrate "initial margin fraction 2.5%, maintenance margin fraction 1.25%". All executed D-16 formulas take `Leverage_effective`, which is 3 regardless of 40 vs 50. D-13 defines `Leverage_effective = min(Leverage_user, MaxLeverage_asset)`, with `MaxLeverage_asset` read from `meta`.
- **evidence:** SRC-118 liquidations.md ("max leverage … varies from 3-40x … 1.25% for 40x max leverage assets") corroborates 40x; SRC-107 info-endpoint/perpetuals `meta` example shows `maxLeverage: 50` (illustrative/stale); SRC-115/116 margining + contract-specifications confirm maintenance = ½ initial at max leverage and per-asset max leverage.
- **decision:** **Option A** — the "40x" figure in §16 is **ILLUSTRATIVE / NON-BINDING**. Runtime MUST read `meta.maxLeverage` live (per D-13) and MUST NEVER hardcode 40 or 50. Live verification of the current BTC/ETH value is OPTIONAL and non-blocking (may be logged as an observation in Phase 8/12, never as a prerequisite).
- **alternatives:** B (mandatory live verification as a prerequisite); C (owner-specified other value).
- **rejected_alternatives:** B (rejected as *mandatory*/blocking — reduced to optional observation); C (no alternative proposed).
- **affected_strategy_requirements:** STR-0337 (venue-evidence-status change only; no normative content change).
- **risk:** LOW at runtime (Leverage_effective clamps to 3); MEDIUM as a documentation artifact (docs-internal inconsistency in the §16 preamble).
- **reversibility:** HIGH (interpretation only; `Strategy.md` unchanged).
- **owner_required:** YES.
- **owner_decision:** **Option A** (recorded 2026-09-21).
- **date:** 2026-09-21.
- **supersedes:** none (first resolution of CONFLICT-001 / GATE-001).

---

## DECISION-002 — Authoritative source for ActualExposure and CapitalBase (from OWNER_GATE_002 / CONFLICT-002)

- **decision_id:** DECISION-002
- **question:** Given `Strategy.md` pairs "clearinghouseState/webData2" but the venue documents `webData2` as a frontend aggregate (now `webData3`), which endpoint is the authoritative source for `ActualExposure` (STR-0200) and `CapitalBase` (STR-0224) per §11.1?
- **context:** §15 invariant: "Actual Exposure only from authoritative exchange state." Venue docs: `clearinghouseState` (REST + WS) is the authoritative position/margin source; `webData2`/`webData3` is "used primarily for the frontend".
- **evidence:** SRC-107 clearinghouseState schema (`assetPositions[].position.szi`, `marginSummary.accountValue` incl. unrealized PnL, `withdrawable`); SRC-109 websocket subscriptions (webData3 current; WebData2 described as frontend aggregate); margining/liquidations use mark price + account value from clearinghouse.
- **decision:** **Option A** — `clearinghouseState` (REST + WS) is the **SOLE authoritative source** for `ActualExposure` and `CapitalBase`. `webData2`/`webData3` MUST NEVER be used as the basis of `POSITION_VERIFIED`, `ActualExposure`, or `CapitalBase`, and MUST NOT drive any decision (arming, closure, evolution, hedge, reconciliation). They MAY be used later for display/observability only.
- **alternatives:** B (combined use with final reconciliation via clearinghouseState); C (owner-specified other).
- **rejected_alternatives:** B, C (owner chose A).
- **affected_strategy_requirements:** STR-0200, STR-0224 (annotation only); STR-0133 (order-lifecycle state authority must also never source from webData3).
- **risk:** LOW (aligns with §15 invariant "Actual Exposure only from authoritative exchange state").
- **reversibility:** HIGH.
- **owner_required:** YES.
- **owner_decision:** **Option A** (recorded 2026-09-21).
- **date:** 2026-09-21.
- **supersedes:** none (first resolution of CONFLICT-002 / GATE-002).

---

## DECISION-003 — Phase 4.5 semantic classification

- **decision_id:** DECISION-003
- **question:** How are the audit findings classified, and which require Owner Gates?
- **context:** pointer to `research/strategy/SEMANTIC_AMBIGUITIES.md` (46 consolidated findings `AMB-0001..AMB-0046`).
- **evidence:** SRC-201 (`philosophy.md`), SRC-202 (`strategy_issues.md`), SRC-203 (`phases_0_4_technical_inspection.md`).
- **decision:** "Classified per SEMANTIC_AMBIGUITIES.md; **11** findings are SEMANTIC_BLOCKING and produce Owner Gates **GATE-003..GATE-013**; **25** findings are SEMANTIC_NON_BLOCKING and will be listed as Phase-5 constraints (2 of them DEFERRED as later-phase verification/validation obligations); 3 IMPLEMENTATION_DETAIL, 2 DOMAIN_CONSTRAINT, 5 ALREADY_RESOLVED."
- **alternatives:** N/A (classification, not a design decision).
- **rejected_alternatives:** N/A.
- **affected_strategy_requirements:** union of STR-* referenced by any AMB-* row — incl. STR-0004, 0025, 0029, 0034, 0035, 0055, 0063, 0071, 0072, 0074, 0077, 0091, 0094, 0096–0098, 0129, 0131–0138, 0159, 0176, 0199, 0200, 0201, 0206, 0212, 0223, 0224, 0227, 0228, 0234, 0239, 0240, 0242, 0245, 0246, 0248, 0254, 0256, 0257, 0268, 0293, 0294, 0298, 0314, 0315, 0334, 0336–0343 (full per-row lists in SEMANTIC_AMBIGUITIES.md).
- **risk:** LOW (this phase only classifies; it does not decide semantics).
- **reversibility:** HIGH (reclassifiable).
- **owner_required:** PARTIALLY (only for the blocking gates GATE-003..GATE-013).
- **owner_decision:** pending for the blocking gates.
- **date:** 2026-09-21.
- **supersedes:** NONE.

> Note: GATE-001 and GATE-002 remain RESOLVED (Option A) and were not reopened. Audit findings that touched them were recorded as new adjacent findings where distinct (e.g., AMB-0003 maintenance-margin model is distinct from GATE-001's max-leverage number). OPEN-01 (CycleReferenceDerivation) is carried as AMB-0042 (SEMANTIC_NON_BLOCKING) and was NOT turned into a new gate, per the Phase-4.5 B3 rule.

---

## DECISION-004 — Unique-attribution rule for POSITION_VERIFIED (from GATE-003 / AMB-0001)

- **decision_id:** DECISION-004
- **question:** How is a fill/delta uniquely attributed to one intent/Level for POSITION_VERIFIED?
- **context:** GATE-003 / AMB-0001; `research/strategy/SEMANTIC_AMBIGUITIES.md`.
- **evidence:** SRC-201 §4.1, SRC-202 A-003/B-001/D-001/D-010/K-003, SRC-203 §3.5/NC-04; venue cloid/orderStatus/clearinghouseState (SRC-104/105/107).
- **decision:** **Option C** — attribution uses `cloid` + `oid` (mapped via `orderStatus`) + authoritative delta from `clearinghouseState`, AND a new strategy-level invariant: "At most one active order per Level at any time." On ambiguity: fail-closed (`RECONCILIATION_REQUIRED`; Level not verified).
- **alternatives:** A (cloid-only), B (reconciliation-window matching without cloid), D (other).
- **rejected_alternatives:** A, B, D.
- **affected_strategy_requirements:** STR-0071, STR-0072, STR-0129, STR-0131, STR-0199, STR-0293; new invariant STR-0344 (Part B1).
- **risk:** LOW-MEDIUM (design constraint; aligned with fail-closed).
- **reversibility:** MEDIUM (grid design constraint).
- **owner_required:** YES. **owner_decision:** Option C (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-005 — External position-change handling (from GATE-004 / AMB-0002)

- **decision_id:** DECISION-005
- **question:** How are external position changes classified/handled, and is the account dedicated?
- **context:** GATE-004 / AMB-0002.
- **evidence:** SRC-202 B-002/D-011/D-012/D-013/G-010/H-008/J-004, SRC-201 §4.10, N#11.
- **decision:** **Option C** — dedicated-account domain constraint + explicit event class for external position changes (liquidation / funding / transfer). Any exposure not attributable to a strategy intent → contamination → `RECONCILIATION_REQUIRED` / `FREEZE`.
- **alternatives:** A (freeze-on-any-external-activity), B (shared-account allocation), D.
- **rejected_alternatives:** A, B.
- **affected_strategy_requirements:** STR-0200, STR-0201, STR-0294, STR-0239.
- **risk:** MEDIUM (operational; depends on account discipline).
- **reversibility:** MEDIUM.
- **owner_required:** YES. **owner_decision:** Option C (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-006 — Maintenance/liquidation model (from GATE-005 / AMB-0003)

- **decision_id:** DECISION-006
- **question:** What is the valid maintenance-margin/liquidation model for risk thresholds; is `0.5/Leverage_effective` authoritative?
- **context:** GATE-005 / AMB-0003 (distinct from GATE-001).
- **evidence:** SRC-115 margining, SRC-116 contract-specs, SRC-118 liquidations; SRC-202 C-001/C-002/H-001/K-007, SRC-201 §4.2, N#2.
- **decision:** **Option C** — runtime reads venue-reported `liquidationPx` and per-asset maintenance margin from `meta`/margin-tiers (`clearinghouseState`) as the primary maintenance/liquidation model. The §16 D-16 formula `0.5 / Leverage_effective` is retained ONLY as an illustrative, conservative floor for initial sizing. D-16 formulas are explicitly re-labelled HYPOTHESIS pending controlled observation in Phase 8/12; re-validation is a Live prerequisite.
- **alternatives:** A (schedule-only, no §16 floor), B (hypothesis-only without venue ground truth), D.
- **rejected_alternatives:** A, B.
- **affected_strategy_requirements:** STR-0223, STR-0337, STR-0340, STR-0206.
- **risk:** HIGH until controlled observation; LOW after (D-16 no longer authority).
- **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option C (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-007 — Event ordering & clock model (from GATE-006 / AMB-0004)

- **decision_id:** DECISION-007
- **question:** What is the canonical event-ordering/clock model for deterministic replay?
- **context:** GATE-006 / AMB-0004.
- **evidence:** SRC-202 B-004/E-001/D-009/L-009, SRC-201 §4.7, SRC-203 NC-03; SRC-110 nonces.
- **decision:** **Option C** — canonical event order = (venue sequence when present) → (server timestamp) → (local receive timestamp) → (monotonic local counter as tie-break). All observation/timer events that affect a decision are recorded in the event log. WS gap → `RECONCILIATION_REQUIRED` until snapshot reconciliation.
- **alternatives:** A (local ingestion order only), B (venue-seq only; no logical-clock fallback), D.
- **rejected_alternatives:** A, B.
- **affected_strategy_requirements:** STR-0063, STR-0315, STR-0334.
- **risk:** LOW (deterministic foundation for CAND-B).
- **reversibility:** MEDIUM (tie-break details in Phase 6).
- **owner_required:** YES. **owner_decision:** Option C (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-008 — UNKNOWN_SUBMISSION recovery (from GATE-007 / AMB-0005)

- **decision_id:** DECISION-008
- **question:** What is the recovery model for ambiguous submission / atomicity / idempotency?
- **context:** GATE-007 / AMB-0005; FM-08/09/10.
- **evidence:** SRC-202 B-013/B-014/E-002/E-003/G-002/G-003/G-005, SRC-201 §4.11, SRC-203 §3.5, N#6; SRC-104 exchange-endpoint (`expiresAfter`), SRC-110 nonces.
- **decision:** **Option B** — on ambiguous submission (timeout, crash mid-send), enter explicit state `UNKNOWN_SUBMISSION`; persist `intent+cloid` BEFORE any side effect; use `expiresAfter` on actions; reconcile with `orderStatus` (by cloid) + `openOrders` + `userFills` + `clearinghouseState` BEFORE any new side effect. Never assume cloid-based dedup in venue.
- **alternatives:** A (without `expiresAfter`), C (other).
- **rejected_alternatives:** A, C.
- **affected_strategy_requirements:** STR-0004, STR-0132, STR-0298, STR-0314, STR-0133, STR-0138.
- **risk:** MEDIUM (rate-limit cost of `expiresAfter`; mitigated by disciplined reconciliation).
- **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option B (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-009 — Nominal reference price + CycleReferenceDerivation explicitness (from GATE-008 / AMB-0006; CLOSES OPEN-01 / AMB-0042)

- **decision_id:** DECISION-009
- **question:** How is `nominal expected reference price` (§5.4.1) defined; and is CycleReferenceDerivation defaulted or explicit?
- **context:** GATE-008 / AMB-0006; OPEN-01 / AMB-0042.
- **evidence:** SRC-201 §4.4, N#4; Strategy §5.4/§5.4.1/§7.1.
- **decision:** **Option B** — `nominal expected reference price` = (previous Cycle's reference price) + (nominal distance to the terminal level, per §7.1 geometry for the same Generation). Captured reference remains per §5.4; §5.4.1 compares captured vs nominal. Additionally: `CycleReferenceDerivation` MUST be set explicitly in runtime config; the Strategy.md default is only a template — runtime without an explicit setting fails closed (BLOCKED). **This CLOSES OPEN-01 and resolves AMB-0042.**
- **alternatives:** A (equivalent phrasing), C (mid/mark at POSITION_VERIFIED), D.
- **rejected_alternatives:** A, C.
- **affected_strategy_requirements:** STR-0091, STR-0096, STR-0097, STR-0098.
- **risk:** LOW. **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option B (2026-09-21).
- **date:** 2026-09-21. **supersedes:** closes OPEN-01.

## DECISION-010 — Partial-fill transition semantics (from GATE-009 / AMB-0007)

- **decision_id:** DECISION-010
- **question:** When does a Level advance under partial fill?
- **context:** GATE-009 / AMB-0007.
- **evidence:** SRC-202 B-003/B-008/F-009; Strategy §5.1/§11.4.
- **decision:** **Option C** — exposure accounting uses verified cumulative filled quantity (partial fills count immediately, per STR-0199/0212), BUT terminal reach / Cycle progression requires full-fill of the terminal level (per §5.1). Remaining unfilled quantity is managed per §9.1/§9.3 (Emergency / Skip).
- **alternatives:** A (full-fill for exposure too), B (cumulative threshold = full), D.
- **rejected_alternatives:** A, B.
- **affected_strategy_requirements:** STR-0071, STR-0074, STR-0199, STR-0212.
- **risk:** LOW. **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option C (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-011 — Basket-vs-account accounting scope (from GATE-010 / AMB-0008)

- **decision_id:** DECISION-011
- **question:** How are PnL/funding/fees/residual attributed from account to Basket?
- **context:** GATE-010 / AMB-0008; depends on DECISION-005.
- **evidence:** SRC-202 A-002/A-004/D-013/F-005/H-009/I-002/I-003/I-006/I-007, SRC-201 §4.10, N#7; venue `userFunding`/fill fee (SRC-105/107).
- **decision:** **Option C** — dedicated account (per DECISION-005), with explicit per-position accounting of funding and fee sourced from `userFunding` and fill-level fee fields, so `BasketNetPnL`, `MaxBasketNotional`, closure target, and residual exposure are attributable to the Basket. accountValue ≈ Basket capital; any deviation is contamination per DECISION-005.
- **alternatives:** A (accountValue = Basket capital w/o explicit allocation), B (shared-account allocation), D.
- **rejected_alternatives:** A, B.
- **affected_strategy_requirements:** STR-0224, STR-0234, STR-0248, STR-0159.
- **risk:** LOW-MEDIUM. **reversibility:** MEDIUM.
- **owner_required:** YES. **owner_decision:** Option C (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-012 — Closure target cost-timing (from GATE-011 / AMB-0009)

- **decision_id:** DECISION-012
- **question:** When is `TotalSystemCosts` snapshot/locked; effect of late costs & corrections?
- **context:** GATE-011 / AMB-0009.
- **evidence:** SRC-202 A-006/E-009/G-014/I-004/I-005/I-008, SRC-201 §4.9, N#10; §14 global rule.
- **decision:** **Option A** — `BasketNetProfitClosureTarget` is locked at first eligibility using TotalSystemCosts accumulated to that instant. Costs incurred after locking do NOT change the target, but DO enter `BasketNetPnL`; closure condition remains "NET ≥ target". Corrections arriving after verified closure are recorded historically only; closure is not reopened.
- **alternatives:** B (recompute-until-close; violates §14 global rule), C (safety buffer), D.
- **rejected_alternatives:** B, C.
- **affected_strategy_requirements:** STR-0243, STR-0245, STR-0246, STR-0256.
- **risk:** LOW. **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option A (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-013 — Evolution complex-path semantics (from GATE-012 / AMB-0010)

- **decision_id:** DECISION-013
- **question:** How do the five Evolution border cases resolve?
- **context:** GATE-012 / AMB-0010.
- **evidence:** SRC-202 B-007/B-009/B-010/E-008/E-011, SRC-201 §4.8; Strategy §4.1/§4.4/§4.5/§4.7.
- **decision:** **Option A** — strict/verified-only Evolution semantics for all five border cases: origin = first verified group in the current Cycle; return requires return to the established return level (STR-0034); no candidate after `INELIGIBLE_EVOLUTION_CANDIDATE` within the same Cycle; only a full re-formation in a later Cycle re-candidates; disable precedes Evolution (§4.7 P3). Every border case gets a unique reason code (`RETURN_LEVEL_UNVERIFIED`, `SUCCESSOR_LOCK_ACTIVE`, `CYCLE_LIMIT_REACHED`, `GENERATION_ID_LIMIT`, …); reason-code enumeration formalized in Phase 6.
- **alternatives:** B (permissive; double-evolution/starvation risk), D.
- **rejected_alternatives:** B.
- **affected_strategy_requirements:** STR-0025, STR-0029, STR-0034, STR-0035, STR-0055.
- **risk:** LOW (aligns with single-in-flight / single-successor).
- **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option A (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-014 — Liveness / exit conditions (from GATE-013 / AMB-0011)

- **decision_id:** DECISION-014
- **question:** What are the exit conditions from fail-closed states?
- **context:** GATE-013 / AMB-0011.
- **evidence:** SRC-202 B-015/K-012/J-005, N#13; Strategy §13.3.
- **decision:** **Option A** — auto-resume on successful reconciliation for transient states (`RECONCILIATION_REQUIRED`, `BLOCKED`); explicit Owner clearance required to exit `FREEZE`, `RECOVERY`, and any kill-switch state. Every resume is recorded with identity/timestamp/evidence. §13.3 already permits EXPOSURE_CORRECTION under FREEZE, so hedge/correction remains live while ENTRY_INTENT is blocked.
- **alternatives:** B (Owner clearance for all), C (auto-resume for all), D.
- **rejected_alternatives:** B, C.
- **affected_strategy_requirements:** STR-0077, STR-0098, STR-0239, STR-0242.
- **risk:** LOW. **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option A (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-015 — Runtime architecture family selection (Phase 5)

- **decision_id:** DECISION-015
- **question:** "Which architecture family is selected for the runtime?"
- **context:** Phase-4 candidate set (`research/architecture/ARCHITECTURE_CANDIDATES.md`: CAND-A/B/C viable + CAND-D/E + microservices rejected) and the full rationale in `research/architecture/ARCHITECTURE_DECISION.md`.
- **evidence:** Phase-4 comparison matrix (CAND-B rated HIGH on Recovery/Persistence/Observability; A/C only MEDIUM and needing an added audit log) plus the mandatory requirements that made the difference: STR-0315 / STR-0334 (§15 inv.19 reconstructability), STR-0298 (persist-before-side-effect), STR-0325 / STR-0326 (fail-closed; no transition solely on intended orders), §4.7 P0–P6 total-order determinism (STR-0047..STR-0053), STR-0344 (one active order per Level), DECISION-002 (clearinghouseState authority), DECISION-007 (canonical event order / tie-break).
- **decision:** "**CAND-B — Event-Driven Single Process / Event-Sourced**, with the 14 interpretation constraints from ARCHITECTURE_DECISION.md §3 and the Phase-4.5/4.6 carried constraints from §11."
- **alternatives:** CAND-A (modular monolith), CAND-C (layered ports/adapters), CAND-D (durable workflow engine), CAND-E (actor model), microservices / multi-process distribution.
- **rejected_alternatives:** CAND-A (reconstructability rests on checkpoint discipline — weaker than log-as-truth; retained as migration target); CAND-C (needs an added disciplined audit log to meet STR-0315/0334 — reintroduces CAND-B's log); CAND-D (heavy external runtime dependency vs AI-independent mandate; nothing requires it); CAND-E (nondeterministic interleaving fights §4.7 total order); microservices (no failure mode requires a service boundary; fragments single-owner state; no scaling driver — one Basket per market, STR-0005).
- **affected_strategy_requirements:** STR-0315, STR-0334 (reconstructability); STR-0047..STR-0053 (§4.7 total-order determinism); STR-0298 (persist-before-side-effect); STR-0325, STR-0326 (fail-closed); STR-0344 (one active order per Level).
- **risk:** **LOW for correctness** (the append-only event log preserves full history, so every transition is reconstructable per STR-0315/0334 by construction); **MEDIUM for Phase-6 cost** (event-schema discipline + versioning, and a snapshotting strategy for replay performance, are required — both acknowledged as Phase-6 work, neither a blocker).
- **reversibility:** MEDIUM (the pure Core carries over unchanged to CAND-A or CAND-C; the commitment is the event schema / log-as-truth, so migrating away means a log/schema migration — see ARCHITECTURE_DECISION.md §9).
- **owner_required:** YES. **owner_decision:** CAND-B (2026-09-21).
- **date:** 2026-09-21. **supersedes:** NONE.

## DECISION-016 — F-1* livelock cell resolution (from OWNER_GATE_014 / AMB-0047) — RESOLVED

- **decision_id:** DECISION-016
- **question:** "Should the F-1* livelock cell be resolved by adopting Fix-1 (tradability-quantized exposure gate), by a calibration constraint (StepBps × MaxBasketNotional ≥ 600,000), or both?"
- **context:** `research/findings/F1_VERIFICATION.md` (independent verification, verdict F1_CONDITIONAL); `research/decisions/OWNER_GATE_014.md` (Q-1 Fix-1 adoption; Q-2 calibration constraint; Q-3 contract annotation).
- **evidence:** SRC-204 (`strategy_audit.md` §1 F-1*/§3), SRC-202 (`strategy_issues.md` category C), SRC-104 (`page-exchange-endpoint.md` — venue $10 minimum order value, hard reject), `Strategy.md` §5.2 / §11.1 (gate predicate `|ExposureDelta| ≤ ExposureTolerance`) / §16 D-16 (τ_E formula).
- **decision:** "Option A (Q-1) + B (Q-2) + A (Q-3): **Q-1=A** — Adopt Fix-1: tradability-quantized exposure gate `T_enter(M) = (1+ε_H) · max(τ_acc(M), q_min(M))` with `ε_H = 1`, plus round-to-zero for `0 < |Δ| < T_exit`. **Q-2=B** — Calibration constraint `StepBps × MaxBasketNotional ≥ 600,000` enforced ONLY as a logged warning (not init-time abort), with τ_E/q_min margin reported in CALIBRATION-REPORT.md. Rationale: a hard constraint would reject current defaults (10 × 30,000 = 300,000 < 600,000) at init. **Q-3=A** — Annotation only on STR-0339; D-16 formula unchanged."
- **alternatives:** the option sets in OWNER_GATE_014 — Q-1 {A adopt Fix-1 / B keep τ_E, rely on calibration / C other}; Q-2 {A hard config invariant / B warn-only / C other}; Q-3 {A annotation only, D-16 unchanged / B leave contract as-is / C other}.
- **rejected_alternatives:** Q-1=B/C, Q-2=A (init-abort would reject current defaults), Q-3=B/C.
- **affected_strategy_requirements:** STR-0339, STR-0298, STR-0315, STR-0074, STR-0077 (+ new STR-0345..STR-0348 — see §18 of STRATEGY_CONTRACT.md).
- **risk:** LOW after resolution: Fix-1 removes the dead-band structurally; the calibration constraint remains as a warning + tracked metric.
- **reversibility:** HIGH.
- **owner_required:** YES.
- **owner_decision:** Q-1=A, Q-2=B, Q-3=A (2026-09-22).
- **date:** 2026-09-22.
- **supersedes:** NONE.

## DECISION-017 — GrossGridEdge closed form (from OWNER_GATE_015 / AMB-0048 / U-1)

- **decision_id:** DECISION-017
- **question:** "How is `GrossGridEdge` defined as a closed form so the §8 gate-10 arming decision is computable and replay-deterministic?"
- **context:** `research/findings/U1_VERIFICATION.md`; `research/decisions/OWNER_GATE_015.md`.
- **evidence:** SRC-204 (§1 U-1 / S-10.1), `Strategy.md` §10 (L810–819, single symbolic `GrossGridEdge` use) / §8 gate 10 (L752–754) / §10 floor (L827–830).
- **decision:** "Option A — `GrossGridEdge := StepBps` (constant, deterministic). Validity condition `GGE − 2·fee_maker − funding_est > NetExpectedEdgeFloor` at Tier-0 fees. The `α·S/2` (adverse-selection) form is recorded as a future calibration proposal only, not adopted."
- **alternatives:** A (`GGE := StepBps`); B (per-level distance-to-terminal `(P_terminal − P_k)/P_terminal × 10⁴`); C (owner alternative).
- **rejected_alternatives:** B (introduces a level-dependent variable absent from the current gate design), C.
- **affected_strategy_requirements:** STR-0193, STR-0179, STR-0197, STR-0273 (+ new STR-0349..STR-0351 — see §18).
- **risk:** LOW (deterministic; matches the StepBps-denominated floor and D-06's StepBps_as_USD).
- **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option A (2026-09-22).
- **date:** 2026-09-22. **supersedes:** NONE.

## DECISION-018 — Funding circuit-breaker (from OWNER_GATE_016 / AMB-0049 / U-2)

- **decision_id:** DECISION-018
- **question:** "What funding-bleed protective bound (threshold + response) should be added, given no §12.1 bound rate-limits funding and the sole NET-DD bound is vacuous?"
- **context:** `research/findings/U2_VERIFICATION.md`; `research/decisions/OWNER_GATE_016.md`.
- **evidence:** SRC-204 (§1 U-2 / S-12.5), `Strategy.md` §12.1 (bounds, no funding entry) / §13.1 (funding non-negligible, enters NET) / §12.2 (risk precedence over closure); venue AA-4 (4%/hr cap, `userFunding`).
- **decision:** "Option A — two-leg funding breaker: a signed-net accumulator `ACC` over `userFunding` events (idempotent dedup keyed (time,coin,delta)); reactive trigger `ACC ≥ X` and predictive trigger `ACC + r̂_F·T_close ≥ X`; response ladder warn → suspend new ENTRY_INTENT → emergency Basket closure under §12.2 (net-profit precondition WAIVED; residual-exposure precondition KEPT). `β_F = 0.02` CALIBRATABLE (fail-closed default); `X = β_F·E₀`; `T_close = 180 s`."
- **alternatives:** A (two-leg breaker); B (make the NET-based freeze trigger threshold explicit, no dedicated breaker); C (owner alternative).
- **rejected_alternatives:** B, C.
- **affected_strategy_requirements:** STR-0234, STR-0235, STR-0236, STR-0246, STR-0221 (+ new STR-0352..STR-0355 — see §18).
- **risk:** LOW–MEDIUM (first automatic escalation to closure; worst-case bleed bounded by `X + r̂_F·T_close`).
- **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option A (2026-09-22).
- **date:** 2026-09-22. **supersedes:** NONE.

## DECISION-019 — Acute-correction precedence (from OWNER_GATE_017 / AMB-0051 / U-4)

- **decision_id:** DECISION-019
- **question:** "What is the precedence between §11.2 acute Hedge Recovery ('unconditional') and the §9.1/§10 economics floor for an acute EXPOSURE_CORRECTION_INTENT?"
- **context:** `research/findings/U4_VERIFICATION.md`; `research/decisions/OWNER_GATE_017.md`.
- **evidence:** SRC-204 (§1 U-4 / S-8.3, S-11.2), `Strategy.md` §8 inv.1 (L730) / §8 L759 / §9.1 (L781–784) / §10 (L827–830) / §11.2 (L869–874).
- **decision:** "Option A — precedence rule: the NetExpectedEdge floor applies to `ENTRY_INTENT` and to non-acute `EXPOSURE_CORRECTION_INTENT`; it never applies to acute Hedge Recovery (§11.2), which is size-bounded by |ExposureDelta| and band-bounded by EmergencyTolerance. Pin `acute(Δ) := |Δ| > τ_I ∨ margin_distance < 2·d_emergency` (τ_I from MaxExposureImbalance §12.1; d_emergency from EmergencyTolerance §9.1)."
- **alternatives:** A (precedence rule + acute() pin); B (leave precedence implicit); C (owner alternative).
- **rejected_alternatives:** B, C.
- **affected_strategy_requirements:** STR-0168, STR-0197, STR-0185, STR-0206, STR-0207 (+ new STR-0356..STR-0357 — see §18).
- **risk:** LOW (resolves an ambiguity deterministically; makes gating a total order).
- **reversibility:** HIGH.
- **owner_required:** YES. **owner_decision:** Option A (2026-09-22).
- **date:** 2026-09-22. **supersedes:** NONE.

## DECISION-020 — MarginMode pinning (from OWNER_GATE_018 / AMB-0054 / U-7)

- **decision_id:** DECISION-020
- **question:** "Should the account margin mode be pinned, given the D-16 risk arithmetic silently assumes cross while the venue supports isolated?"
- **context:** `research/findings/U7_VERIFICATION.md`; `research/decisions/OWNER_GATE_018.md`.
- **evidence:** SRC-204 (§1 U-7 / R-8), `Strategy.md` §12.1 (MaxSafeNotional_margin) / §16 D-16 (maintenance fraction); venue `clearinghouseState.assetPositions[].leverage.type ∈ {cross, isolated}` and `position.type oneWay` (SRC-107); whole-file search: no `MarginMode` parameter exists in Strategy.md.
- **decision:** "Option A — FIXED config parameter `MarginMode` = cross (with oneWay and account-level semantics; corresponding venue fields `marginMode` / `leverage.type` / `position.type`); owner-overridable only via an explicit Owner Gate. Config-resolution check: if `MarginMode` absent → ABORT before any side effect. Per-pass P0 assertion: every `clearinghouseState.assetPositions[].leverage.type == MarginMode` AND `position.type == oneWay`; mismatch → FREEZE."
- **alternatives:** A (pin cross + assert); B (no pin); C (owner-specified mode).
- **rejected_alternatives:** B, C.
- **affected_strategy_requirements:** STR-0223, STR-0340, STR-0225, STR-0227, STR-0337 (+ new STR-0358..STR-0360 — see §18).
- **risk:** LOW (removes silent risk-model invalidation across margin modes).
- **reversibility:** HIGH (config value).
- **owner_required:** YES. **owner_decision:** Option A (2026-09-22).
- **date:** 2026-09-22. **supersedes:** NONE.

## DECISION-021 — CAP-0024 reference-model language/paradigm (from OWNER_GATE_019) — RESOLVED

- **decision_id:** DECISION-021
- **question:** "Which language/paradigm should CAP-0024 (the reference model) be implemented in, to satisfy VALIDATION_PLAN §4's independence requirement (no shared code with production)?"
- **context:** `research/implementation/CAP0024_DESIGN.md`; `research/decisions/OWNER_GATE_019.md`. Note: the production runtime language is itself not yet selected (a separate future Owner Gate), so the answer may be ABSOLUTE, CONDITIONAL on the production choice, or DEFER (see GATE-019 §3).
- **evidence:** VALIDATION_PLAN §4 (independence); ARCHITECTURE_DECISION §4 (Research layer, offline/NON_RUNTIME); candidate list in CAP0024_DESIGN.md Part C (REF-A..F).
- **decision:** "REF-D (functional reference), CONDITIONAL. Framing (verbatim): 'CAP-0024 in a functional language, paradigm-distinct from whatever the production runtime uses; concrete language pinned when the production language is chosen (separate future Gate).' REF-A REJECTED (common-mode risk). REF-C recorded as a FORWARD NOTE only — a formal/spec slice complementing the differential harness may be considered in Phase 9+; NOT a second selection in this Gate. No commitment is made in this decision on the production runtime language."
- **alternatives:** the option set from GATE-019 — REF-A (same lang, separate codebase), REF-B (different general-purpose lang), REF-C (formal/spec tool), REF-D (functional reference), REF-E (declarative/constraint), REF-F (hybrid functional/formal + comparator).
- **rejected_alternatives:** REF-A (common-mode bug risk); all other REFs not selected; REF-C retained as a forward note only.
- **affected_strategy_requirements:** none directly (verification-layer decision).
- **risk:** LOW after resolution: REF-D is paradigm-distinct from any likely imperative production, structurally independent, and suited to the pure event fold.
- **reversibility:** MEDIUM (the reference model is not shipped; changing it requires re-running the differential suite).
- **owner_required:** YES.
- **owner_decision:** REF-D, CONDITIONAL (2026-09-22).
- **date:** 2026-09-22.
- **supersedes:** NONE.
