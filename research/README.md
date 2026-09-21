# research/ — Strategy-to-Runtime Research State

- **Purpose:** Durable, context-survivable home for all research evidence, decisions, and traceability for transforming `Strategy.md` into a deterministic, auditable Hyperliquid trading runtime. This directory (not the chat context) is the source of truth for research state.
- **Version:** 1.0 (Phase 0)
- **Producer:** Claude Code (Opus 4.8), Phase 0.
- **Inputs:** `Strategy.md` (SRC-001), `prompt.md` (SRC-002, program protocol v3.0).
- **Status:** Phase 0 COMPLETE. No blockers.
- **Validation status:** Phase 0 artifacts created deterministically; hashes recorded in `sources/SOURCE_MANIFEST.md`.

---

## Program phases (`prompt.md` `<implementation_phases>`)

| Phase | Name | State |
|-------|------|-------|
| 0 | Repository / Strategy Ingestion | **COMPLETE** (commit 51df743) |
| 1 | Strategy Forensics | **COMPLETE** — STRATEGY_CONTRACT.md (343 STR-* reqs) + STRATEGY_COVERAGE.md |
| 2 | Source & Venue Research (Hyperliquid docs + SDK) | **COMPLETE** (+2.5/2b) — 17 venue pages + SDK 0.24.0; [HC]: 15 VERIFIED, 1 PARTIAL (STR-0228), 1 CONFLICTED (STR-0337→GATE-001). Owner gates 001/002 open |
| 3 | Capability Discovery | **COMPLETE** — 24 capabilities (CAP-0001..0024); 343/343 STR-* mapped; DECISION-001/002 registered & applied |
| 4 | Architecture Research (≥3 materially different candidates) | not started |
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

**Current phase:** Phase 3 (Capability Discovery) complete. **Next:** Phase 4 (Architecture Research — ≥3 materially different candidates; boundary/topology decisions). Capability Map + coverage are the input.

## Current blocker

**None blocking.** Owner Gates 001 & 002 are **RESOLVED** (DECISION-001, DECISION-002 in `research/decisions/DECISION_REGISTER.md`). Contract [HC] fields: 15 VERIFIED, 1 PARTIALLY_VERIFIED (STR-0228, l2Book depth nuance — Phase-4 design), 1 RESOLVED_VIA_OWNER_DECISION (STR-0337). Open (non-blocking): OPEN-01 (CycleReferenceDerivation default vs "MUST be explicit"); STR-0228 depth-window design note. Phase-3 outputs: `research/architecture/CAPABILITY_MAP.md` (24 CAP-*) + `CAPABILITY_COVERAGE.md` (343/343 mapped). **No boundaries/topology/technology decided** (explicit non-decisions listed in CAPABILITY_MAP.md).

## Artifact layout (created only when a phase requires it)

```
research/
  README.md                         # this file — research state overview
  sources/
    SOURCE_MANIFEST.md              # source registry (SRC-*); venue rows PENDING
    hyperliquid/                    # (Phase 2) fetched venue evidence
  strategy/
    STRATEGY_SOURCE_RECORD.md       # canonical Strategy identity/hash/provenance
    STRATEGY_CONTRACT.md            # (Phase 1) derived STR-* requirements — CREATED (343 reqs)
    STRATEGY_COVERAGE.md            # (Phase 1) heading→STR-* coverage map — CREATED
  findings/                         # (as needed) CONFLICT-*.md, claims
  architecture/
    CAPABILITY_MAP.md               # (Phase 3) — NOT YET CREATED
    ARCHITECTURE_CANDIDATES.md      # (Phase 4)
    ARCHITECTURE_DECISION.md        # (Phase 5)
  decisions/
    DECISION_REGISTER.md            # (as needed)
    OPEN_QUESTIONS.md               # (as needed)
    REJECTED_ALTERNATIVES.md        # (as needed)
  validation/
    TRACEABILITY_MATRIX.md          # (Phase 9)
    VALIDATION_PLAN.md
    AUDIT_REPORT.md
  experiments/
    runs/
```

Per `prompt.md` `<artifact_first>` / `<artifact_structure>`: do NOT pre-create empty boilerplate. Files above without a "created" note do not yet exist.

## Authority & safety reminders (see root `CLAUDE.md`)

- `Strategy.md` is immutable. `prompt.md` governs the workflow.
- Runtime must be deterministic and AI-independent; no trading code, framework choice, agent roster, or Live activation without an explicit Owner Gate.
- Fail closed on ambiguity. The four `[DYNAMIC — CALIBRATION PENDING]` / `[DYNAMIC-CALIBRATABLE]` defaults (D-16 ×3, D-17) must remain dynamic — never frozen to arbitrary constants.
