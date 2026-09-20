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
| 0 | Repository / Strategy Ingestion | **COMPLETE (this run)** |
| 1 | Strategy Forensics | not started |
| 2 | Source & Venue Research (Hyperliquid docs + SDK) | not started |
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

**Current phase:** Phase 0 just completed. **Next:** Phase 1 (Strategy Forensics) — awaiting a go-ahead per the first-run scope limit.

## Current blocker

**None.** No unresolved semantic conflict, no missing required input for Phase 0.

## Artifact layout (created only when a phase requires it)

```
research/
  README.md                         # this file — research state overview
  sources/
    SOURCE_MANIFEST.md              # source registry (SRC-*); venue rows PENDING
    hyperliquid/                    # (Phase 2) fetched venue evidence
  strategy/
    STRATEGY_SOURCE_RECORD.md       # canonical Strategy identity/hash/provenance
    STRATEGY_CONTRACT.md            # (Phase 1) derived STR-* requirements — NOT YET CREATED
    STRATEGY_COVERAGE.md            # (Phase 1+)
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
