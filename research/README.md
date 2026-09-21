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
| 3 | Capability Discovery | not started |
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

**Current phase:** Phase 2 + 2.5 + 2b complete. **Next:** Phase 3 (Capability Discovery) — pending owner responses to OWNER_GATE_001 (max leverage / §16 calibration preamble) and OWNER_GATE_002 (clearinghouseState vs webData2/3 authority).

## Current blocker

**Two OPEN Owner Gates (non-blocking for evidence, gating for Phase-3 capability decisions):**
- **OWNER_GATE_001** — CONFLICT-001 (BTC/ETH max leverage 40x vs meta example 50x). Runtime impact LOW (Leverage_effective=3), escalated for §16 calibration-preamble integrity; STR-0337 = CONFLICTED.
- **OWNER_GATE_002** — CONFLICT-002 (webData2→webData3; authoritative source for ActualExposure). Recommend clearinghouseState as sole authority.

Other open items: OPEN-01 (Phase 1: CycleReferenceDerivation default vs "MUST be explicit"). CONFLICT-003 (trigger basis) **RESOLVED** — mark price triggers TP/SL, not last trade; STR-0134 VERIFIED. Contract [HC] fields now: 15 VERIFIED, 1 PARTIALLY_VERIFIED (STR-0228), 1 CONFLICTED (STR-0337). Evidence base: `research/sources/hyperliquid/` (17 pages + SDK_RECORD + TOPIC_EVIDENCE + _HC_TARGETS); gates in `research/decisions/`.

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
