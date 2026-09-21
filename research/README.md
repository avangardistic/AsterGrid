# research/ — Strategy-to-Runtime Research State

- **Purpose:** Durable, context-survivable home for all research evidence, decisions, and traceability for transforming `Strategy.md` into a deterministic, auditable Hyperliquid trading runtime. This directory (not the chat context) is the source of truth for research state.
- **Version:** 1.5 (Phase 4.5)
- **Producer:** Claude Code (Opus 4.8), Phases 0 → 4.5.
- **Inputs:** `Strategy.md` (SRC-001), `prompt.md` (SRC-002, program protocol v3.0).
- **Status:** Phases 0–4 COMPLETE. Phase 4.5 (audit reconciliation) COMPLETE — documentation cleanup + semantic classification (46 AMB-*, 11 new Owner Gates GATE-003..013, DECISION-003). Next: Phase 5.
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
| 5 | Architecture Decision | not started |
| 6 | Implementation Plan | not started |
| 7 | Deterministic Core Implementation | not started |
| 8 | Venue Integration | not started |
| 9 | Verification & Audit | not started |
| 10 | Backtest / Simulation | not started |
| 11 | Shadow | not started |
| 12 | Testnet | not started |
| 13 | Live Readiness | not started |
| 14 | Live Activation | not started (separate Owner authority; NOT granted) |

**Current phase:** Phase 4.5 (Audit reconciliation) COMPLETE. **Next:** Phase 5 (Architecture Decision — owner has indicated CAND-B; to be recorded in `ARCHITECTURE_DECISION.md` + a DECISION_REGISTER entry). Phase 5 MUST carry the 25 SEMANTIC_NON_BLOCKING findings + OPEN-01 as explicit input constraints, and the 11 OPEN Owner Gates (GATE-003..013) gate Phase-6/7 implementation of the affected areas.

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

**11 new Owner Gates opened (GATE-003..GATE-013), all OPEN/pending owner decision;** OWNER_GATE_001 & 002 remain RESOLVED. Phase 5 must carry the NON_BLOCKING findings + OPEN-01 (AMB-0042) as explicit input constraints.

## Owner decision round (Phase 4.6)

On 2026-09-21 the Owner reviewed and decided all eleven blocking gates GATE-003..GATE-013; the decisions are recorded as **DECISION-004..DECISION-014** in `research/decisions/DECISION_REGISTER.md` (each gate file carries a RESOLVED status line). Mechanical consequences applied: a new invariant **STR-0344** ("at most one active order per Level at any time", from DECISION-004); **OPEN-01 CLOSED** by DECISION-009 (CycleReferenceDerivation must be set explicitly; runtime without it fails closed) and AMB-0042 marked RESOLVED; a **dedicated-account constraint** header note added to the contract (DECISION-005/011); and the **D-16 maintenance-margin model re-labelled HYPOTHESIS** (DECISION-006 — runtime reads venue liquidationPx/maintenance as primary; re-validation is a Live prerequisite). In `SEMANTIC_AMBIGUITIES.md`, all 11 SEMANTIC_BLOCKING rows (+AMB-0042) now read `RESOLVED_BY_DECISION_0NN`. See `DECISION_REGISTER.md`.

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
    ARCHITECTURE_DECISION.md        # (Phase 5) — NOT YET CREATED
  decisions/
    DECISION_REGISTER.md            # CREATED (DECISION-001, -002)
    OWNER_GATE_001.md / OWNER_GATE_002.md  # CREATED (both RESOLVED)
  validation/
    CALIBRATION-REPORT.md           # (Phase 4.5) stub — NOT_YET_PRODUCED
    TRACEABILITY_MATRIX.md          # (Phase 9) — NOT YET CREATED
    VALIDATION_PLAN.md              # NOT YET CREATED
    AUDIT_REPORT.md                 # NOT YET CREATED
  experiments/
    runs/                           # NOT YET CREATED
```

Per `prompt.md` `<artifact_first>` / `<artifact_structure>`: do NOT pre-create empty boilerplate. Files above without a "created" note do not yet exist.

## Authority & safety reminders (see root `CLAUDE.md`)

- `Strategy.md` is immutable. `prompt.md` governs the workflow.
- Runtime must be deterministic and AI-independent; no trading code, framework choice, agent roster, or Live activation without an explicit Owner Gate.
- Fail closed on ambiguity. The four `[DYNAMIC — CALIBRATION PENDING]` / `[DYNAMIC-CALIBRATABLE]` defaults (D-16 ×3, D-17) must remain dynamic — never frozen to arbitrary constants.
