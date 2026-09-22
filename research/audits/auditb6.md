# auditb6.md — Multi-Agent Repository Audit: Phase 6 Readiness

- **Repository:** `hypergrid` @ commit `25ff8cb` ("phase-5: architecture decision — CAND-B event-sourced single process"), branch `arena/01a0c562-hypergrid`
- **Audit date:** 2026-09-21
- **Audit scope:** Phases 0–5 artifacts (design/research only; **no production code exists yet** — by design, per `CLAUDE.md` Owner-Gate rules)
- **Method:** Five agent passes (traceability, logic, API compliance, architecture, readiness) + **independent machine verification**: SHA-256 recomputation, programmatic range-expansion of the coverage map, exhaustive ID enumeration, status-line reconciliation, and **live re-fetch of 6 Hyperliquid documentation pages** (2026-09-21) compared against the repo's cached evidence (fetched 2026-09-20).
- **Limitation:** The sandbox has no network egress to `api.hyperliquid.xyz`, so the live API `meta.maxLeverage` value could not be probed directly; live-doc text was verified instead (see Agent 3).

---

## 1. Executive Summary

### Verdict: ⚠️ CONDITIONAL PASS — Ready to enter Phase 6 (Implementation Plan); Phase 7 (code) entry is conditional on P1 items below.

The repository is in unusually strong shape for a design-phase trading system:

- **Integrity holds end-to-end.** `Strategy.md` SHA-256 (`085044e7…a825e18`), byte size (92,686), and line count (1,368) match `STRATEGY_SOURCE_RECORD.md` exactly; the file is unmodified across all phases. All spot-checked venue evidence hashes match `SOURCE_MANIFEST.md`.
- **The blocking ledger is genuinely closed.** All **13 Owner Gates are RESOLVED** with cross-linked decision records (DECISION-001, 002, 004–014); all **11 SEMANTIC_BLOCKING** findings (+AMB-0042) carry `RESOLVED_BY_DECISION_*` statuses; all three venue conflicts (CONFLICT-001/002/003) are resolved without any silent edit to the immutable strategy.
- **Traceability is real, not decorative.** Programmatic expansion of `CAPABILITY_COVERAGE.md` covers **343/343** Phase-1 requirements with **zero gaps and zero orphaned capabilities**; all 23 states map into CAND-B's realization model (21 folded in-core + 2 venue-authoritative).
- **API compliance is verified against the live venue docs.** Every `[HC]` claim re-checked today (funding mechanics, mark-price TP/SL triggering, precision rules, rate limits, WS subscription names, clearinghouseState schema) matches the current official documentation verbatim. The one known docs-internal inconsistency (BTC/ETH `maxLeverage` example 50x vs. prose "3–40x") **persists in the live docs today** and is correctly neutralized by DECISION-001 (read `meta.maxLeverage` live; never hardcode).

**Why "conditional":** three classes of items must be addressed inside Phase 6 before Phase 7 code: (1) a **traceability artifact lag** — STR-0344 (created Phase 4.6) has no row in `CAPABILITY_COVERAGE.md` and the counts still read "343"; (2) the **verification strategy artifact** (`VALIDATION_PLAN.md`) required by `prompt.md <implementation_rule>` does not exist yet — required before implementation begins; (3) the **22 OPEN `SEMANTIC_NON_BLOCKING` findings** are binding Phase-6/7 work with fail-closed defaults until resolved, plus 2 CRITICAL findings deliberately DEFERRED to Phases 7/9/10 — these are a mandatory work queue, not optional polish. No P0 blockers were found.

---

## 2. Agent Findings Matrix

| # | Agent | Focus | Status | Critical findings | Risk level |
|---|-------|-------|--------|-------------------|------------|
| 1 | Traceability Auditor | STR→CAP→State→CAND-B lineage | **PASS with 1 gap** | STR-0344 absent from `CAPABILITY_COVERAGE.md`; counts stale at "343" (artifact lag, not a design hole — coverage is substantively documented in ARCHITECTURE_DECISION §2b/§11.4) | **Medium** (documentation integrity) |
| 2 | Logical Consistency Checker | Non-blocking findings, CONFLICT-001, state cycles | **PASS** | DECISION-001 is race-free and complete (live read + computed-once + drift fail-closed). No circular dependencies in state derivation or P0–P6 precedence. 25 NON_BLOCKING = 22 OPEN + 2 DEFERRED(CRITICAL) + 1 resolved — genuinely non-blocking *for gating*, but a mandatory Phase-6/7 queue | **Low–Medium** |
| 3 | Hyperliquid API Compliance Validator | Repo assumptions vs. official API | **PASS** | No deviation found in any `[HC]` claim (15 VERIFIED / 1 PARTIAL / 1 RESOLVED_VIA_OWNER_DECISION confirmed). **Venue drift detected**: live docs now expose `marginTables`/`marginTiers`, `marginMode`, HIP-3 builder dexes, and ~8 new WS subscriptions not in the cached extracts. Page-count bookkeeping: 16 saved files vs. "17 pages" (17 SRC IDs; SRC-101/103 share one file) | **Medium** (drift surface, not correctness) |
| 4 | Architecture Decision Validator | CAND-B + DECISION-001..015 | **PASS** | CAND-B selection is evidence-grounded (STR-0315/0334 decisive), rejection rationale for A/C/D/E/microservices is sound and documented; Pure-Core/Deterministic-Replay guarantees are architecturally enforceable, with replay fidelity explicitly conditional on the AMB-0016 event-recording discipline. Note: decision corpus is **001–015** (015 = architecture selection; 003 = classification record), not 001–014 | **Low** |
| 5 | Phase-6 Readiness Assessor | Defaults, gates, event-schema versioning | **CONDITIONAL PASS** | 13/13 gates RESOLVED (verified per file). Dynamic-defaults corpus is **4 instances** (D-16 ×3 + D-17 ×1), correctly tagged and never-freeze bound; `CALIBRATION-REPORT.md` is an explicit `NOT_YET_PRODUCED` stub with a defined method — calibration gates Live, not Phase 6. Task-input reconciliation: "17 Dynamic Defaults D-01..D-17" is a misnomer (D-01..D-17 are Owner decision IDs; D-01..D-15 resolved). `VALIDATION_PLAN.md` missing (P1). Stale status lines in contract header / README Phase-4.5 section (P2) | **Medium** |

**Cross-validation performed:** Agent 3 independently confirmed Agent 2's CONFLICT-001 resolution against live venue documentation (§4.2 below). Agent 1's STR-0344 gap was confirmed immaterial to Agent 4's architecture rationale (the invariant is load-bearing in CAND-B's justification and is properly recorded there). Agent 5's gate audit consumed Agent 2's AMB status reconciliation.

---

## 3. Detailed Analysis

### 3.1 Traceability Report (Agent 1) — Gaps in STR→CAP→State flow

**Verified by independent recomputation, not by trusting the artifacts' self-reports:**

| Claim | Repo says | Independently verified | Result |
|-------|-----------|------------------------|--------|
| Strategy immutability | SHA-256 `085044e7…a825e18`, 92,686 B, 1,368 lines | Recomputed `sha256sum`, `stat`, `wc -l` | ✅ Exact match |
| Strategy forensics | 343 STR-* (STR-0001..0343), Phase 1 | Enumerated all IDs | ✅ 343 Phase-1 + **344th** (STR-0344, Phase 4.6) appended as §17; **no numbering gaps** in 0001..0344 |
| Requirement→capability coverage | 343/343 mapped, no orphans | Parsed all `STR-a..b` ranges in `CAPABILITY_COVERAGE.md`, expanded to integer sets | ✅ Union = exactly {1..343}; missing set **empty**; all 24 CAPs referenced; "STR-\* without a CAP-\*" section empty |
| No orphaned capabilities | "Capabilities with zero STR-\* mapped: none" | Every CAP-0001..0024 lists ≥1 covered STR | ✅ Confirmed |
| State model | 23 single-owner states (ST-01..ST-23) | Enumerated | ✅ 23 states, 0 multi-owner; desired-vs-authoritative splits (ST-05, ST-18) modeled as distinct single-owner states |
| CAND-B realization | 21 states folded in-core + 2 venue-authoritative (ST-08, ST-17) = 23 | Counted ARCHITECTURE_DECISION §5 lists | ✅ 21 + 2 = 23, no state dropped |
| Derivation fidelity | Contract quotes verbatim wording | Spot-compared STR-0175, STR-0337, STR-0004 against `Strategy.md` §§8, 16, 1 | ✅ Verbatim, with venue-evidence refs and owner-decision annotations preserved |
| Strength taxonomy | 302 MUST / 36 MUST_NOT / 4 SHOULD / 1 MAY (Phase-1 set) | Grepped whole file (incl. STR-0344): 302/37/4/1 | ✅ Consistent (STR-0344 is the added MUST_NOT); the 5 non-MUST strengths are individually justified from "prefer/preferable/AUTO" wording |

**State sufficiency for the event-sourced architecture:** each of the 23 states carries owner / source-of-truth / writers / readers / persistence / versioning / consistency / recovery / reconciliation fields; ST-13 (append-only event log) is the reconstruction substrate required by STR-0315/0334. The strategy's invariant surface (identity §3, lifecycle §§4–5, pipeline §6.1, exposure §11, risk §12, basket §13) is fully represented. No missing state definition was found for any normative behavior.

**Flags (traceability):**

- **[GAP-1] STR-0344 has no coverage row.** `CAPABILITY_COVERAGE.md` still reads "STR-\* total: 343 / Mapped: 343" and contains no STR-0344 entry; `CAPABILITY_MAP.md` and `STATE_OWNERSHIP.md` headers still cite "343 STR-\*" inputs. STR-0344 *is* correctly integrated into `STRATEGY_CONTRACT.md` (§17, full field block), `ARCHITECTURE_DECISION.md` (§2b, §11.4 — mapped to the per-Level projection, i.e., CAP-0015/CAP-0003 territory), and DECISION-015. This is an **artifact-lag defect in the coverage map, not a design hole** — but the coverage map is the artifact whose contract is "guarantee no requirement is dropped," so it must be brought current. → **P1**
- **[OBS-1] Venue-sequence watermark is implicit.** DECISION-007's canonical order keys on "venue sequence when present"; no state is explicitly named as the per-stream sequence watermark (it is implicitly part of ST-13/ST-19). Phase 6 should name it in the event schema. → **P2**

### 3.2 Logic & Conflicts (Agent 2) — NON_BLOCKING items and conflict resolutions

**Re-evaluation of CONFLICT-001 (40x vs. 50x leverage) and DECISION-001:**

- *Facts:* `Strategy.md` §16 preamble asserts "BTC/ETH max leverage = 40x → 2.5%/1.25%". The docs' `meta` **example** shows `maxLeverage: 50` for BTC/ETH; the liquidations **prose** states max leverage "varies from 3-40x" with "1.25% (for 40x max leverage assets)". Agent 3 re-fetched **both live pages today (2026-09-21): the inconsistency persists verbatim in the live docs** — this is a venue-documentation defect, not a repo defect.
- *Resolution mechanics:* DECISION-001 declares the "40x" ILLUSTRATIVE/NON-BINDING; the runtime MUST read `meta.maxLeverage` live and MUST NEVER hardcode 40 or 50. Combined with D-13 (`Leverage_effective = min(Leverage_user=3, MaxLeverage_asset)`), every executed §16 formula evaluates identically whether the venue reports 40 or 50 — only the illustrative preamble changes. **Confirmed correct.**
- *Race-condition analysis:* No race exists. Leverage resolution happens once at config resolution (CAP-0020), obeys the §14 global rule ("formulas are used ONCE… then binding"), and under CAND-B the live read is recorded as an observation event (DECISION-002/007 discipline). A mid-Basket venue-side change to `maxLeverage` cannot silently mutate computed parameters; venue drift is caught by the AMB-0026 fail-closed obligation. The residual risk is documentation hygiene only — exactly as the register records it (risk: LOW runtime / MEDIUM documentation).

**Review of the 25 `SEMANTIC_NON_BLOCKING` findings (status reconciliation performed by grep, not by counting prose):**

| Status | Count | Findings |
|--------|-------|----------|
| OPEN (must be explicitly resolved in Phase 6/7) | **22** | AMB-0012..0033 except those below |
| DEFERRED (later-phase verification/validation obligations) | **2** | AMB-0034 (CRITICAL — verification obligations, Phases 7/9/10-12), AMB-0035 (HIGH — economic realism, Phase 10) |
| Resolved | **1** | AMB-0042 (OPEN-01) → RESOLVED_BY_DECISION_009 |

- *Are they truly non-blocking?* The classification method is sound and consistently applied: a finding is SEMANTIC_BLOCKING only if two compliant implementations could differ **observably** AND the resolution needs an Owner strategy-semantic decision. The borderline calls were made conservatively (AMB-0004/0007/0011 were *promoted* to BLOCKING; the uncertainty notes document the reasoning). Each NON_BLOCKING item has an "obviously-correct fail-closed/deterministic resolution" recorded with its named phase.
- *Latent risks hidden inside the set:* (1) **AMB-0034/0035 are CRITICAL-severity** — deferred, not dismissed; if the Phase 6 plan does not schedule them, they become the program's largest silent risk. (2) **AMB-0033 (numeric domain/type system)** is the most likely to produce subtle numeric defects (zero/near-zero price, StepBps boundaries, overflow) and deserves early Phase-6 treatment alongside the type-system design. (3) The label "non-blocking" is genuinely dangerous only if read as "optional" — ARCHITECTURE_DECISION §11 explicitly forecloses this by making all 25 BINDING Phase-6/7 inputs with fail-closed defaults until resolved. **Verdict: genuinely non-blocking for gate purposes; mandatory work queue; two deferred CRITICALs must be scheduled, not forgotten.**

**Circular-dependency check (state transitions):**

- The state-derivation graph is acyclic: ST-07 (ExpectedExposure) ← ST-04 (verified fills); ST-09 (ExposureDelta) ← ST-07, ST-08; ST-21 (NET PnL) ← ST-05/ST-13 + clearinghouseState; ST-20 (risk trackers) ← ST-05/ST-18/ST-21. Where two concepts appear mutually related (ST-20 risk bounds referencing PnL; PnL including costs), the event fold is layered — costs are events, PnL is a fold over them, risk trackers fold over PnL snapshots — so no cycle exists at the derivation level.
- The §4.7 precedence (P0 verification → P1 risk → P2 locks → P3 same-generation conflict → P4 across-generations → P5 cycle transitions → P6 arming) is a strict total order: risk precedes progression, arming is last, no event executes twice, unexecuted events carry forward. The one same-pass conflict (disable vs. evolution) is deterministically resolved at P3 (DISABLE wins, evolution recorded `INELIGIBLE_EVOLUTION_CANDIDATE`). The single-in-flight Evolution lock (P2) and the permanent successor lock preclude re-entrancy. DECISION-010's partial-fill semantics (partial fills count for exposure per STR-0199/0212; full terminal fill required for progression per §5.1) is internally consistent with the lifecycle rules.
- **No logical contradictions, circular dependencies, or un-owned edge cases were found.** Remaining ambiguities are enumerated, owned, and phase-assigned (22 OPEN + 2 DEFERRED above).

### 3.3 API Compliance (Agent 3) — Discrepancies with Hyperliquid docs

**Evidence integrity:** Recomputed SHA-256 of 7 saved extracts (`page-perpetuals-info`, `page-funding`, `page-margining`, `page-liquidations`, `page-order-types`, `page-rate-limits`, `page-tick-and-lot-size`) — **all match `SOURCE_MANIFEST.md`**.

**Live cross-check (fetched 2026-09-21 from hyperliquid.gitbook.io):**

| Repo claim ([HC] target) | Live docs today | Verdict |
|---|---|---|
| Mark price used for "margining, liquidations, triggering TP/SL, computing unrealized pnl" (STR-0134, CONFLICT-003 resolution) | `robust-price-indices.md`: identical wording | ✅ Confirmed |
| Funding paid hourly at 1/8 of 8h rate; interest 0.01%/8h; 4%/hr cap; funding notional uses **oracle** price (STR-0337) | `funding.md`: identical | ✅ Confirmed |
| Precision: ≤5 sig figs, ≤(6−szDecimals) decimals for perps; integer prices always valid; sizes at szDecimals; trailing-zero removal when signing (STR-0135..0138) | `tick-and-lot-size.md`: identical | ✅ Confirmed |
| `webData3` is the current subscription; `WebData2` = "aggregate information about a user, used primarily for the frontend" (CONFLICT-002 / DECISION-002) | `websocket/subscriptions.md`: item 3 is `webData3`; WebData2 description unchanged | ✅ Confirmed — clearinghouseState-as-sole-authority remains API-correct |
| `l2Book` 5 levels (fast) / 20 (slow) (STR-0228 nuance) | Confirmed | ✅ Confirmed (STR-0228 stays honestly PARTIALLY_VERIFIED: the ±10×StepBps depth-window coverage question is a design task, AMB-0013) |
| TWAP: ≥30s suborders, ≤3% per-suborder slippage, $100 min, 5min–7d (STR-0254) | Confirmed | ✅ Confirmed |
| Rate limits: 1200 weight/min per IP; open-order cap 1000 (→5000 by volume); reduce-only/trigger rejected at ≥1000 open (STR-0176) | Confirmed | ✅ Confirmed |
| clearinghouseState schema: `assetPositions[].position.szi`, `marginSummary.accountValue` (incl. unrealized PnL), `withdrawable` (STR-0200/0224, DECISION-002) | Confirmed | ✅ Confirmed |
| BTC/ETH `maxLeverage` 40x (STR-0337 / CONFLICT-001) | Docs still internally inconsistent: `meta` example = 50, liquidations prose = "3-40x" | ⚠️ As assessed — illustrative only; DECISION-001 resolution (read live) remains the correct and API-compliant answer. Live API probe impossible from this sandbox (egress blocked); the DECISION-001 optional live observation should still be logged in Phase 8/12 |

**`HC_VERIFIED` roll-up confirmed:** 17 `[HC]` requirement fields = **15 VERIFIED + 1 PARTIALLY_VERIFIED (STR-0228) + 1 RESOLVED_VIA_OWNER_DECISION (STR-0337)**; the single remaining `UNVERIFIED` string is the historical Phase-1 snapshot line (contract line 2732), not a live requirement status. ✅

**Deviations / drift found (none invalidate existing claims):**

1. **Venue schema growth since the 2026-09-20 fetch.** Live `perpetuals.md` now documents `marginTables`/`marginTiers` (lowerBound/maxLeverage), `marginMode` (`strictIsolated`/`noCross`), `isDelisted`, HIP-3 builder dexes (`xyz:*`, per-`dex` query params), `collateralToken`. Live WS page adds `twapStates`, `userTwapSliceFills`, `userTwapHistory`, `bbo`, `fastAssetCtxs`, `allDexs*`, `outcomeMetaUpdates`, `spotState` (portfolio margin). Funding adds a HIP-3 premium variant. **Implications:** (a) `marginTables` materially *supports* DECISION-006's design ("read per-asset maintenance margin from meta/margin-tiers") and should be cited when that design is written; (b) the drift surface assumed by AMB-0026 (venue-drift → fail-closed + version binding) is already real — the evidence base should be refreshed and version-pinned (commit/date, per AMB-0038) at the start of Phase 6. → **P2**
2. **Count bookkeeping:** the evidence directory holds **16 distinct saved page files**; the "17 pages" figure counts venue SRC IDs (SRC-101 and SRC-103 share `page-api-root.md`). No `[HC]` target lacks evidence — all 12 topics are covered — but the count should be reconciled to avoid audit confusion. → **P2**
3. No mismatch was found in any payload structure, order type, TIF value, nonce rule ($-based address budget, T−2d…T+1d window), minimum order value ($10), or settlement/funding logic between repo assumptions and the docs.

### 3.4 Architecture Review (Agent 4) — Validity of CAND-B and the decisions

**Re-assessment of CAND-B (event-sourced single process) against the 14 interpretation constraints and the full decision corpus:**

- **The selection is requirement-driven, not taste-driven.** The decisive grounds are mandatory, verifiable requirements: STR-0315/STR-0334 (§15 inv.19 — every transition reconstructable) makes log-as-truth structurally superior; STR-0298 (persist-before-side-effect) becomes the natural write path; STR-0325/0326 (no transition solely on intended orders) maps onto the intent-vs-outcome event distinction; §4.7 total-order determinism (STR-0047..0053) + DECISION-007's canonical order make replay faithful; STR-0344 gets an unambiguous replayable per-Level projection; DECISION-002 makes venue truth auditable as observation events. CAND-A/C would each have to bolt on exactly the same log to satisfy STR-0315/0334 — the rejection rationale (matrix ratings MEDIUM on Recovery/Persistence for A/C) is documented and consistent between Phase 4 and Phase 5 artifacts (no drift).
- **Rejections are well-reasoned:** CAND-D (external workflow engine) violates the self-contained/AI-independent mandate with no requiring capability; CAND-E (actors) fights the total-ordered pass; microservices fragment single-owner state with zero requiring failure modes (11 failure modes analyzed; none requires a service boundary; FM-08/FM-10 justify only a *store resource*). CAND-A is correctly retained as the documented migration target, and reversibility is honestly rated **MEDIUM** (the commitment is the event schema/log — migrating away is a log migration).
- **Pure Core / Deterministic Replay enforceability:** Yes, architecturally enforceable — the core is specified as total, side-effect-free fold functions with no wall-clock/randomness; adapters are side-effect-only; the canonical event order is fixed (venue-seq → server-ts → local-ts → monotonic counter); and the document honestly scopes what is *not* guaranteed (venue nondeterminism; replay of *un-recorded* observations; latency). The load-bearing condition — every decision-affecting observation/timer must be recorded — is explicitly assigned to Phase 6 as the AMB-0016 event-discipline obligation rather than hand-waved. **This is the architecture's single most failure-prone point and must be a first-class Phase-6 deliverable (event schema + versioning + snapshot policy + recording discipline).**
- **Decision register health (DECISION-001..015):** all records carry question/context/evidence/decision/alternatives/rejected-alternatives/affected-requirements/risk/reversibility/owner/date — audit-grade quality. Gate→decision cross-links verified pairwise for all 13 gates (001→D-001 Option A, 002→D-002 A, 003→D-004 C, 004→D-005 C, 005→D-006 C, 006→D-007 C, 007→D-008 B, 008→D-009 B, 009→D-010 C, 010→D-011 C, 011→D-012 A, 012→D-013 A, 013→D-014 A). **Corpus correction to the audit brief:** the register runs **DECISION-001..015** (DECISION-003 is the Phase-4.5 classification record; DECISION-015 is the Phase-5 architecture selection); "001 through 014" understates it. No unauthorized technology choice exists — ARCHITECTURE_DECISION §10's explicit non-decisions (language/framework/DB/schema/signing/deployment/observability) were verified against the artifact.
- **Flags:** none blocking. One structural caution: the Owner-selected status of CAND-B is properly recorded (owner authority per `CLAUDE.md`), but Phase 6 must keep interpretation-constraint #8 (log as durable truth) and #9 (deterministic replay) from eroding under implementation convenience — any deviation requires a new versioned decision, as the document itself mandates.

### 3.5 Readiness Checklist (Agent 5) — Dynamic Defaults and Gates

**Owner Gates — all RESOLVED (verified per file):**

| Gate | File status | Decision | Option |
|------|-------------|----------|--------|
| GATE-001 | RESOLVED 2026-09-21 | DECISION-001 | A (40x illustrative; read live) |
| GATE-002 | RESOLVED 2026-09-21 | DECISION-002 | A (clearinghouseState sole authority) |
| GATE-003..GATE-013 | RESOLVED 2026-09-21 (11 files, each carries a RESOLVED status line) | DECISION-004..014 | C, C, C, C, B, B, C, C, A, A, A |

13/13 RESOLVED. DECISION-003 (classification) and DECISION-015 (architecture) are correctly not gates. **Live activation remains explicitly NOT granted** — correct authority posture.

**Dynamic defaults — corpus reconciliation and calibration readiness:**

- The audit brief's "17 Dynamic Defaults (D-01 to D-17)" is a **misnomer to be corrected in program records**: D-01..D-17 are the *Owner decision IDs* from `Strategy.md`'s merge provenance (§14/§16). Per §16, **D-01…D-15 are resolved**; the dynamic defaults are **four instances**: D-16 ×3 (`EmergencyTolerance`, `ExposureTolerance`, `MaxExposureImbalance`, all `[DYNAMIC — CALIBRATION PENDING]`) and D-17 ×1 (`ReferencePriceToleranceBps`, `[DYNAMIC-CALIBRATABLE]`).
- **Tagging:** verified — each is tagged at every point of use (§5.2, §9.1, §12.1, §5.4.1, §14) and in the contract (STR-0338..0341) with the never-freeze rule (STR-0336: every dynamic read logged and distinguishable in the audit trail) and the §16 mutual-ordering invariant (`ExposureTolerance < MaxExposureImbalance < NotionalPerLevel/MarkPrice`, STR-0342).
- **Calibration plan:** `research/validation/CALIBRATION-REPORT.md` exists as an explicit `NOT_YET_PRODUCED` stub with a defined method (candidate input sets `Leverage_effective ∈ {2,3,5}` × `StepBps ∈ {5,10,20}`; ordering verification; owner confirmation; offline/non-runtime). Calibration correctly gates **Live readiness (Phase 13)**, not Phase 6 — but the plan is not yet scheduled into a phase plan. Additionally, per DECISION-006, the D-16 maintenance-margin model is a labelled **HYPOTHESIS** whose re-validation is a **Live prerequisite** — this is the single highest-risk open validation item in the program and must appear in the Phase-6 plan's Live-readiness dependency list.

**Event-schema versioning readiness:** Not yet designed — **by explicit decision** (ARCHITECTURE_DECISION §10 defers schema/serialization/snapshotting to Phase 6). The design inputs are ready: 23 owned states, capability-derived event kinds, DECISION-007 ordering anchor, and the recording obligations (AMB-0016 observations/timers; AMB-0027 reporting contract; AMB-0032 config/calibration versioning). **Phase 6 must deliver the event schema + versioning + snapshot policy as its core artifacts; the schema commitment is the main reversibility cost of CAND-B (MEDIUM) and deserves an RFC-grade treatment.**

**Phase-6 entry criteria (`prompt.md <implementation_rule>`):**

| Criterion | Status |
|-----------|--------|
| Strategy Forensics complete | ✅ (343+1 reqs, coverage map) |
| Strategy Contract exists | ✅ |
| Key venue sources identified | ✅ (17 venue SRCs, hash-pinned; refresh recommended) |
| Capability discovery completed | ✅ (24 CAPs, 343/343 mapped) |
| Architecture alternatives evaluated | ✅ (CAND-A/B/C + 2 rejections + microservices) |
| Architecture decision recorded | ✅ (DECISION-015 + ARCHITECTURE_DECISION.md) |
| Blocking semantic questions resolved | ✅ (11/11 gates resolved; 3 conflicts resolved) |
| **Verification strategy defined** | ⚠️ **Partial** — direction exists (CAP-0024 reference model/differential testing; AMB-0034 verification obligations), but `VALIDATION_PLAN.md` does not exist. Required before Phase 7 implementation begins. → **P1** |

**Stale documentation (found during cross-checks):** `STRATEGY_CONTRACT.md` header line 6 still says "GATE-003..GATE-013 **OPEN**" (all are RESOLVED; the rest of the file — including STR-0337's DECISION-006 status note — is current); `research/README.md`'s Phase-4.5 section still says gates are "all OPEN/pending owner decision" (superseded by its own Phase-4.6 section). Both are the exact artifact class AMB-0043 was opened for. → **P2**

---

## 4. Critical Action Items

**P0 — Blockers: none.** No finding invalidates the strategy contract, the architecture decision, the gate resolutions, or the venue-evidence base. Phase 6 may begin.

| Pri | # | Action | Rationale / evidence |
|-----|---|--------|----------------------|
| **P1** | 1 | **Update `CAPABILITY_COVERAGE.md`**: add STR-0344 row (→ CAP-0003, CAP-0015; enforcement projection in CAP-0005) and refresh the 343→344 totals and input headers in `CAPABILITY_MAP.md` / `STATE_OWNERSHIP.md` (or add a dated addendum note). | Agent 1 GAP-1: the coverage map's contract is "no requirement dropped"; it currently lags the Phase-4.6 invariant. |
| **P1** | 2 | **Produce `VALIDATION_PLAN.md`** (verification strategy: differential testing vs. CAP-0024 reference model, invariant/property tests, failure-injection, replay-determinism tests, precision tests) as an early Phase-6 deliverable — mandatory before Phase 7 code. | `prompt.md <implementation_rule>`; README lists VALIDATION_PLAN as not created. |
| **P1** | 3 | **Schedule, in the Phase-6 implementation plan, the explicit resolution of all 22 OPEN `SEMANTIC_NON_BLOCKING` findings** (fail-closed defaults until each is decided) **and carry the 2 DEFERRED findings as named later-phase obligations** (AMB-0034 → Phases 7/9/10-12; AMB-0035 → Phase 10). | Agent 2: they are binding inputs (ARCHITECTURE_DECISION §11), and the two DEFERRED are CRITICAL-severity — unscheduled, they become silent risk. |
| **P2** | 4 | **Refresh the venue evidence base** (re-fetch the 16 pages; record commit/date version pins per AMB-0038) and cite the newly documented `marginTables`/`marginTiers` in the DECISION-006 maintenance-margin design. | Agent 3: live docs already drifted (margin tiers, HIP-3 dexes, new WS subscriptions) — supports AMB-0026's fail-closed-on-drift posture. |
| **P2** | 5 | **Annotate stale status lines as historical**: `STRATEGY_CONTRACT.md` header ("GATE-003..GATE-013 OPEN") and `README.md` Phase-4.5 section ("all OPEN/pending"). | Agents 1/5: superseded in-file; stale text invites future misreads (AMB-0043 class). |
| **P2** | 6 | **Reconcile the page count** ("17 pages" = 17 venue SRC IDs vs. 16 distinct saved files; SRC-101/103 share one file) in `SOURCE_MANIFEST.md`/`README.md`. | Agent 3 bookkeeping note. |
| **P2** | 7 | **Name the venue-sequence watermark explicitly in the Phase-6 event schema** (per-stream last-sequence tracking under DECISION-007's canonical order). | Agent 1 OBS-1; folds into AMB-0016 event-discipline. |
| **P2** | 8 | In Phase 8/12, **log the optional live `meta.maxLeverage` observation** for BTC/ETH (DECISION-001, non-blocking) and keep the CALIBRATION-REPORT production plus D-16 hypothesis re-validation on the Live-readiness critical path (DECISION-006). | Agents 2/3/5. |

---

## 5. Final Conclusion

**The repository is logically sound and is ready to enter Phase 6 (Implementation Plan).** The evidence chain is intact and independently re-verified: an immutable, hash-stable strategy source; a 343(+1)-requirement contract with verbatim-provenance and zero coverage gaps; 24 capabilities with no orphans; 23 single-owner states fully realized under the selected event-sourced architecture; 13/13 Owner Gates resolved with audit-grade decision records; all 11 blocking semantic findings closed by explicit Owner decisions; and venue assumptions that — after a live re-fetch on audit day — remain verbatim-compliant with current official Hyperliquid documentation, including a correct, race-free resolution of the one genuine venue-documentation inconsistency (BTC/ETH max leverage).

The verdict is **conditional, not unconditional**, for one reason: the artifacts that make Phase 6 *safe to execute* are not all written yet. The coverage map lags the newest invariant (STR-0344); the verification strategy exists only as direction (CAP-0024 + deferred obligations), not as the required `VALIDATION_PLAN.md`; and 22 open non-blocking findings plus 2 deliberately deferred CRITICAL verification/economic-realism obligations constitute a binding work queue that the Phase-6 plan must schedule explicitly, with fail-closed defaults until each is decided. None of these is a defect in the design's logic; all are executable inside Phase 6.

Per the program's own discipline — and the independent technical inspection's warning that *coverage ≠ correctness* — this audit certifies **design readiness, not runtime correctness**. Runtime correctness remains unproven until the Phase 7/9 evidence (deterministic core, differential replay, failure injection) exists, and Live activation remains gated on calibration of the four dynamic defaults, re-validation of the D-16 margin hypothesis (DECISION-006), and an explicit Owner Live gate, none of which is granted by this document.

**Recommended next action:** enter Phase 6 and dispose of P1 items 1–3 in the plan's first increment.

---

*Audit artifacts: all verification commands (hash recomputation, coverage-range expansion, ID enumeration, status reconciliation) were executed against the repository working tree at commit `25ff8cb`; live documentation fetches were performed 2026-09-21 against hyperliquid.gitbook.io. No repository file was modified by this audit.*
