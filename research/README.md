# research/ — Strategy-to-Runtime Research State

- **Purpose:** Durable, context-survivable home for all research evidence, decisions, and traceability for transforming `Strategy.md` into a deterministic, auditable Hyperliquid trading runtime. This directory (not the chat context) is the source of truth for research state.
- **Version:** 1.6 (Phase 5)
- **Producer:** Claude Code (Opus 4.8), Phases 0 → 5.
- **Inputs:** `Strategy.md` (SRC-001), `prompt.md` (SRC-002, program protocol v3.0).
- **Status:** Phases 0–4.6 COMPLETE. Phase 5 (Architecture Decision) COMPLETE — CAND-B (event-sourced single process) recorded in `architecture/ARCHITECTURE_DECISION.md` + DECISION-015. Next: Phase 6 (Implementation Plan).
- **Validation status:** Phase 0–4 artifacts created deterministically; hashes in `sources/SOURCE_MANIFEST.md`; `Strategy.md` SHA-256 unchanged across all phases.

---

## Program phases (`prompt.md` `<implementation_phases>`)

| Phase | Name | State |
|-------|------|-------|
| 0 | Repository / Strategy Ingestion | **COMPLETE** (commit 51df743) |
| 1 | Strategy Forensics | **COMPLETE** — STRATEGY_CONTRACT.md (343 STR-* reqs) + STRATEGY_COVERAGE.md |
| 2 | Source & Venue Research (Hyperliquid docs + SDK) | **COMPLETE** (+2.5/2b) — 17 venue pages + SDK 0.24.0; [HC]: 15 VERIFIED, 1 PARTIAL (STR-0228), 1 RESOLVED_VIA_OWNER_DECISION (STR-0337). Owner gates 001/002 RESOLVED (Option A, 2026-09-21) |
| 3 | Capability Discovery | **COMPLETE** — 24 capabilities (CAP-0001..0024); 343/343 STR-* mapped; DECISION-001/002 registered & applied |
| 4 | Architecture Research (≥3 materially different candidates) | **COMPLETE** — state-ownership (23 states), boundaries, failure boundaries, 3 candidates (CAND-A/B/C) + 2 rejected |
| 5 | Architecture Decision | **COMPLETE** — CAND-B event-sourced single process (DECISION-015); 14 interpretation constraints + Phase-4.5/4.6 carried constraints binding for Phase 6+ |
| 6 | Implementation Plan | not started |
| 7 | Deterministic Core Implementation | not started |
| 8 | Venue Integration | not started |
| 9 | Verification & Audit | not started |
| 10 | Backtest / Simulation | not started |
| 11 | Shadow | not started |
| 12 | Testnet | not started |
| 13 | Live Readiness | not started |
| 14 | Live Activation | not started (separate Owner authority; NOT granted) |

**Current phase:** Phase 5 (Architecture Decision) COMPLETE — CAND-B (event-driven single process / event-sourced) recorded in `architecture/ARCHITECTURE_DECISION.md` and DECISION-015; the 14 interpretation constraints (§3) and the Phase-4.5/4.6 carried constraints (§11: 25 SEMANTIC_NON_BLOCKING incl. 2 DEFERRED, D-16 hypothesis, dedicated-account, STR-0344, CycleReferenceDerivation-explicit) are BINDING inputs to Phase 6/7. **Next:** Phase 6 (Implementation Plan). All 13 Owner Gates RESOLVED (DECISION-001..014).

Phase-4 outputs: `research/architecture/STATE_OWNERSHIP.md` (23 single-owner states), `BOUNDARY_CANDIDATES.md` (smallest justified boundaries; no service/microservice justified), `FAILURE_BOUNDARIES.md` (11 failure modes; none require a service boundary), `ARCHITECTURE_CANDIDATES.md` (CAND-A modular monolith, CAND-B event-sourced, CAND-C layered ports/adapters; CAND-D workflow-engine & CAND-E actor-model rejected; microservices rejected a priori). No technology chosen.

## Current blocker

**None blocking.** Owner Gates 001 & 002 are **RESOLVED** (DECISION-001, DECISION-002 in `research/decisions/DECISION_REGISTER.md`). Contract [HC] fields: 15 VERIFIED, 1 PARTIALLY_VERIFIED (STR-0228, l2Book depth nuance — Phase-4 design), 1 RESOLVED_VIA_OWNER_DECISION (STR-0337). Open (non-blocking): OPEN-01 (CycleReferenceDerivation default vs "MUST be explicit"); STR-0228 depth-window design note. Phase-3 outputs: `research/architecture/CAPABILITY_MAP.md` (24 CAP-*) + `CAPABILITY_COVERAGE.md` (343/343 mapped). **No boundaries/topology/technology decided** (explicit non-decisions listed in CAPABILITY_MAP.md).

## Audit reconciliation (Phase 4.5)

Phase 4.5 is a bridge phase to classify the findings of three independent audit documents into `research/strategy/SEMANTIC_AMBIGUITIES.md` and to open Owner Gates for any `SEMANTIC_BLOCKING` finding.

**RESOLVED (2026-09-21):** the three audit documents were supplied under `research/audits/` (SRC-201/202/203) and classification is complete. See **`research/strategy/SEMANTIC_AMBIGUITIES.md`** (46 findings AMB-0001..0046: 11 SEMANTIC_BLOCKING → **OWNER_GATE_003..OWNER_GATE_013**, 25 NON_BLOCKING, 3 IMPLEMENTATION_DETAIL, 2 DOMAIN_CONSTRAINT, 5 ALREADY_RESOLVED) and **DECISION-003**.

| Audit document | Status | Classification output |
|----------------|--------|-----------------------|
| `philosophy.md` (SRC-201) | classified | folded into SEMANTIC_AMBIGUITIES.md (AMB-*) |
| `strategy_issues.md` (SRC-202) | classified | folded into SEMANTIC_AMBIGUITIES.md (AMB-*) |
| `phases_0_4_technical_inspection.md` (SRC-203) | classified | folded into SEMANTIC_AMBIGUITIES.md (AMB-*) |

**11 new Owner Gates opened (GATE-003..GATE-013), all OPEN/pending owner decision;** OWNER_GATE_001 & 002 remain RESOLVED. Phase 5 must carry the NON_BLOCKING findings + OPEN-01 (AMB-0042) as explicit input constraints. *(historical — Phase-4.5 status; superseded. All 18 gates GATE-001..GATE-018 are now RESOLVED as of Phase 4.10 — see the Phase-4.6 and Phase-4.10 sections above and DECISION_REGISTER.md DECISION-001..020.)*

## Owner decision round (Phase 4.6)

On 2026-09-21 the Owner reviewed and decided all eleven blocking gates GATE-003..GATE-013; the decisions are recorded as **DECISION-004..DECISION-014** in `research/decisions/DECISION_REGISTER.md` (each gate file carries a RESOLVED status line). Mechanical consequences applied: a new invariant **STR-0344** ("at most one active order per Level at any time", from DECISION-004); **OPEN-01 CLOSED** by DECISION-009 (CycleReferenceDerivation must be set explicitly; runtime without it fails closed) and AMB-0042 marked RESOLVED; a **dedicated-account constraint** header note added to the contract (DECISION-005/011); and the **D-16 maintenance-margin model re-labelled HYPOTHESIS** (DECISION-006 — runtime reads venue liquidationPx/maintenance as primary; re-validation is a Live prerequisite). In `SEMANTIC_AMBIGUITIES.md`, all 11 SEMANTIC_BLOCKING rows (+AMB-0042) now read `RESOLVED_BY_DECISION_0NN`. See `DECISION_REGISTER.md`.

## Audit ingestion + F-1\* verification (Phase 4.7)

On 2026-09-22 four secondary audit documents were registered as **non-authoritative** sources (SRC-204 `strategy_audit.md`, SRC-205 `strategy_fixes.md`, SRC-206 `genetic_calibration_report.md`, SRC-207 `ga_arena.py`+`ga_results.json`; see `sources/SOURCE_MANIFEST.md` §5). The GA study is classified exploratory-only in **`research/findings/GA_CLASSIFICATION.md`** (Golden Genome = calibration PROPOSAL, remains `[DYNAMIC — CALIBRATION PENDING]`; not a runtime dependency; CAP-0024 is the reference model). The audit's **F-1\*** livelock claim was **independently re-derived from `Strategy.md` + venue evidence** in **`research/findings/F1_VERIFICATION.md`** — verdict **F1_CONDITIONAL** (confirmed at the D-16 default scenario: τ_E=$5 < venue q_min=$10, reachable dead-band $6–$9, no escape rule; absent when `StepBps·MaxBasketNotional ≥ 600,000`); recorded as AMB-0047 in **`research/findings/F1_SEMANTIC_RECORD.md`**. **No fix applied, no DECISION-016+ created, no Owner Gate opened** — the Owner decides next steps.

## Independent verification of audit findings U-1..U-8 (Phase 4.9)

On 2026-09-22 the eight `U` findings of `strategy_audit.md` (SRC-204) were independently re-derived against `Strategy.md` + venue evidence — see **`research/findings/U_VERIFICATION_SUMMARY.md`** and per-finding **`research/findings/U1..U8_VERIFICATION.md`**; AMB-0048..0055 recorded in **`research/findings/U_AMB_RECORD.md`**. Verdicts: U-1/U-3/U-4/U-5/U-7/U-8 **U_VERIFIED**, U-2/U-6 **U_CONDITIONAL**; none rejected. Blocking-pending (need an Owner Gate before Phase 7): **U-1, U-2, U-4, U-7**. Non-blocking (Phase-6 resolution): **U-3, U-5, U-6, U-8**. Key discrepancies with the audit's framing: U-2 (conditional on hedge-halt, not always-live), U-3 (opposite-group already handled by §5.6 L503), U-5 (already mitigated by DECISION-008), U-6 (moot at the default). **No fix applied, no gate opened, no DECISION created.**

## Phase 4.10 — Owner Gate resolutions (U-1, U-2, U-4, U-7)

On 2026-09-22 the Owner resolved all four U-blocking gates (Options A) and F-1\*'s GATE-014 (Q-1=A, Q-2=B, Q-3=A). New gates **GATE-015..GATE-018** created and RESOLVED; **DECISION-016..020** recorded in `decisions/DECISION_REGISTER.md`. Mechanical consequences: new requirements **STR-0345..STR-0362** added in `strategy/STRATEGY_CONTRACT.md` §18 (no `Strategy.md` change, no existing STR renumbered); `architecture/CAPABILITY_COVERAGE.md` updated to **362/362** mapped (incl. the previously-unmapped STR-0344). Fix-1 (STR-0345..0348) and the U-1/U-2/U-4/U-7 mitigations are contract-level specifications for Phase 6/7 implementation — no code written. **U-3/U-5/U-6/U-8 remain SEMANTIC_NON_BLOCKING**, scheduled for Phase 6 (recorded as STR-0361/0362 + `findings/U_AMB_RECORD.md`); no gate opened for them.

## Phase 6a — Implementation-plan input preparation

On 2026-09-22: created **`validation/VALIDATION_PLAN.md`** (the verification strategy required before Phase 7 — 17 mechanisms, 6 prioritized oracles, coverage matrix with 0 unmapped STR-*, Phase-7 entry criteria, Live-readiness dependencies, and the AMB-0034/0035 deferred obligations). Refreshed the venue evidence base (live re-fetch 2026-09-22): the two materially-drifted pages (perpetuals, websocket subscriptions) snapshotted as `sources/hyperliquid/page-*.live-2026-09-22.md` and logged in `SOURCE_MANIFEST.md` §6 — `marginTables`/`marginTiers` **support DECISION-006**; the `meta.marginMode` field-semantics nuance (isolation qualifiers, not a literal `cross`) recorded in `findings/VENUE_DRIFT_2026-09-22.md` with **DECISION-020 unchanged**; new WS/HIP-3 capabilities logged, not adopted. Scheduled the four non-blocking items (U-3/U-5/U-6/U-8) in `decisions/PHASE6_SCHEDULE.md`. Stale Phase-4.5 gate-status prose annotated as historical (all 18 gates RESOLVED). Note: **6a/6b/6c are working subdivisions of Phase 6** (6a input prep; 6b event model + interfaces + CAP-0024 design; 6c non-blocking resolution). No event schema/interface/plan, no technology, no code, no Testnet/Live.

## Phase 6b-1 — Event model + interface map (conceptual, log-as-truth layer)

On 2026-09-22: created **`implementation/EVENT_MODEL.md`** (10 conceptual event KINDS; event identity with DECISION-007 canonical-order keys; 7 cross-cutting invariants; the per-stream venue-sequence watermark; and the snapshot concept — "an optimization over the log, never a replacement authority") and **`implementation/INTERFACE_MAP.md`** (6 boundaries: Core↔Log, Core↔Adapters, Adapters↔Venue, Signing, Operator, Persistence — each with never/must/failure/invariant; the external observation model; and a CAP-0024 governance forward-reference). Conceptual design only — no language/framework/DB/serialization/snapshot format chosen, no code, no CAP-0024 design (Phase 6b-2), no new DECISION, no gate. 6b-1/6b-2/6c are working subdivisions of Phase 6.

## Phase 6b-2 — CAP-0024 reference-model design + GATE-019

On 2026-09-22: created **`implementation/CAP0024_DESIGN.md`** — the independent reference model (primary oracle per VALIDATION_PLAN §2/§3.2/§4): purpose + independence requirements (no shared code with production), inputs/outputs, **20 behavioral obligations (B-01..B-20) each mapped to a VALIDATION_PLAN §3.x mechanism**, explicit out-of-scope (live venue access, dynamic-default values), **6 candidate languages/paradigms REF-A..F with recommendation-strength and ABSOLUTE/CONDITIONAL framing (no selection)**, and conceptual differential/exhaustive harness requirements. Opened **OWNER_GATE_019** (language/paradigm selection) and registered **DECISION-021 PENDING**. No selection made, no code, no GATE-019 resolution. Phase 6c may proceed on the finalized behavioral design without the language selection.

## GATE-019 resolution + Phase 6c — non-blocking constraints resolved

On 2026-09-22: **GATE-019 RESOLVED** — CAP-0024 reference model = **REF-D (functional), CONDITIONAL** (DECISION-021; REF-A rejected; REF-C retained as a Phase-9+ complementary note; no production-language commitment). **Phase 6c** closed the non-blocking constraint set: the 22 SEMANTIC_NON_BLOCKING findings (AMB-0012..0033) resolved as **20 new requirements STR-0363..STR-0382 (§19)** + 2 annotations (AMB-0014→STR-0345, AMB-0025→STR-0358); U-3/U-5/U-6/U-8 resolved as phase6c_note on STR-0361/0133/0290/0362; concrete numbers added as `phase6c_note` (snapshot cadence + watermark encoding in `EVENT_MODEL.md`; per-type freshness in `INTERFACE_MAP.md`); AMB-0034/0035 marked SCHEDULED in `VALIDATION_PLAN.md`. Corpus now **382 STR-***. **None escalated** (no genuinely-semantic finding). No production language chosen, no code, no new gate, no new DECISION beyond DECISION-021.

## Coverage catch-up + GATE-020 (production runtime language)

On 2026-09-22: **coverage catch-up** — STR-0363..STR-0382 (Phase 6c) mapped to existing capabilities in `architecture/CAPABILITY_COVERAGE.md` (new "Phase 6c STR additions" table; **382/382 mapped, 0 unmapped, no CAP invented**); header counts updated to 382 in CAPABILITY_COVERAGE / CAPABILITY_MAP / STATE_OWNERSHIP. **Opened OWNER_GATE_020** (production runtime language — options A Python / B Rust / C Go / D TypeScript-Node; functional-language productions rejected as a family per DECISION-021 independence + DECISION-015 non-actor CAND-B; non-binding recommendation: Python, conditional on determinism discipline) and registered **DECISION-022 PENDING**. This is the last Phase-7 blocker. No language selected, no code, no gate resolution, no new DECISION beyond DECISION-022.

## GATE-020/021 resolved + Phase 7a scaffolding

On 2026-09-22: **GATE-020 RESOLVED** — production language = **Python** with 3 mandatory conditions (int/`Decimal` in the decision path; `mypy --strict`; core single-threaded/pure) (DECISION-022; Rust/Go/TS rejected; functional family rejected). **GATE-021 RESOLVED** — runtime/UI stack + 3-log system (DECISION-023: pure-Python core, asyncio adapters, SQLite event store, Pydantic+TOML config, FastAPI+HTMX UI; domain event log + operational log + owner audit trail; core never logs). **DECISION-021 ADDENDUM** — REF-D (CAP-0024) language **PINNED to OCaml** (Dune/QCheck/Yojson; JSON scenario exchange; no shared code). Owner UI requirement recorded in `implementation/UI_REQUIREMENT.md`. **Phase 7a scaffolding** built at the repo root (`src/hypergrid/{core,adapters,runtime,operator,config}`, `tests/`): package skeleton + §14 Pydantic config schema (34 fields, strict no-float `Decimal`) + JSON logging skeleton — **no domain logic, no venue code, no secrets**. `pytest` 14/14, `mypy --strict` clean, `ruff` clean. First trading code is Phase 7b+.

## Artifact layout (created only when a phase requires it)

```
research/
  README.md                         # this file — research state overview
  sources/
    SOURCE_MANIFEST.md              # source registry (SRC-*); venue rows POPULATED (Phase 2/2b)
    hyperliquid/                    # (Phase 2) fetched venue evidence — CREATED (17 pages + SDK + evidence)
  strategy/
    STRATEGY_SOURCE_RECORD.md       # canonical Strategy identity/hash/provenance
    STRATEGY_CONTRACT.md            # (Phase 1) derived STR-* requirements — CREATED (343 reqs)
    STRATEGY_COVERAGE.md            # (Phase 1) heading→STR-* coverage map — CREATED
    SEMANTIC_AMBIGUITIES.md         # (Phase 4.5) audit classification — CREATED (46 AMB-*)
  findings/                         # CONFLICT-001/002/003 — CREATED (all RESOLVED)
  architecture/
    CAPABILITY_MAP.md               # (Phase 3) — CREATED (24 CAP-*)
    CAPABILITY_COVERAGE.md          # (Phase 3) — CREATED (343/343 mapped)
    STATE_OWNERSHIP.md              # (Phase 4) — CREATED (23 states)
    BOUNDARY_CANDIDATES.md          # (Phase 4) — CREATED
    FAILURE_BOUNDARIES.md           # (Phase 4) — CREATED (11 failure modes)
    ARCHITECTURE_CANDIDATES.md      # (Phase 4) — CREATED (CAND-A/B/C)
    ARCHITECTURE_DECISION.md        # (Phase 5) — CREATED (CAND-B; DECISION-015)
  decisions/
    DECISION_REGISTER.md            # CREATED (DECISION-001..015)
    OWNER_GATE_001.md / OWNER_GATE_002.md  # CREATED (both RESOLVED)
  validation/
    CALIBRATION-REPORT.md           # (Phase 4.5) stub — NOT_YET_PRODUCED
    TRACEABILITY_MATRIX.md          # (Phase 9) — NOT YET CREATED
    VALIDATION_PLAN.md              # (Phase 6a) — CREATED (verification strategy; Phase-7 entry artifact)
    AUDIT_REPORT.md                 # NOT YET CREATED
  experiments/
    runs/                           # NOT YET CREATED
```

Per `prompt.md` `<artifact_first>` / `<artifact_structure>`: do NOT pre-create empty boilerplate. Files above without a "created" note do not yet exist.

## Authority & safety reminders (see root `CLAUDE.md`)

- `Strategy.md` is immutable. `prompt.md` governs the workflow.
- Runtime must be deterministic and AI-independent; no trading code, framework choice, agent roster, or Live activation without an explicit Owner Gate.
- Fail closed on ambiguity. The four `[DYNAMIC — CALIBRATION PENDING]` / `[DYNAMIC-CALIBRATABLE]` defaults (D-16 ×3, D-17) must remain dynamic — never frozen to arbitrary constants.
