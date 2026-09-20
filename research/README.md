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
| 2 | Source & Venue Research (Hyperliquid docs + SDK) | **COMPLETE** — 14 venue pages + SDK 0.24.0; 14/17 [HC] VERIFIED, 2 PARTIAL, 1 CONFLICTED |
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

**Current phase:** Phase 2 (Source & Venue Research) complete. **Next:** Phase 2b (fetch robust-price-indices/liquidations/signing to close STR-0134 & STR-0138 nuances) then Phase 3 (Capability Discovery). Owner review of CONFLICT-001/002/003 pending.

## Current blocker

**None blocking.** Open items: OPEN-01 (Phase 1: CycleReferenceDerivation default vs "MUST be explicit"); CONFLICT-001 (BTC/ETH max leverage 40x vs docs meta 50x — LOW impact, Leverage_effective=3 unaffected); CONFLICT-002 (webData2→webData3 naming — LOW); CONFLICT-003 (trigger→oracle-mark basis — PARTIALLY_VERIFIED). Evidence base: `research/sources/hyperliquid/` (14 pages + SDK_RECORD + TOPIC_EVIDENCE + _HC_TARGETS). Contract [HC] fields remain `venue_evidence_status: UNVERIFIED` (owner promotes to VERIFIED in a later review, per Phase-2 scope).

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
