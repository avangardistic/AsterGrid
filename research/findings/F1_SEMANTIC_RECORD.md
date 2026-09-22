# F1_SEMANTIC_RECORD.md — AMB-0047 (F-1\* verification record, Phase 4.7)

- **Purpose:** Record the single semantic finding arising from the independent F-1\* verification (Phase 4.7 Part C) as a durable AMB-* row, **without modifying** the Phase-4.5 artifact `research/strategy/SEMANTIC_AMBIGUITIES.md`.
- **Recording decision (fail-closed):** Phase 4.7 Part E's commit manifest does not list `SEMANTIC_AMBIGUITIES.md`, and the hard constraints forbid modifying Phase 0–5 artifacts. Therefore the AMB-0047 row is recorded here (a new Phase-4.7 findings file) rather than appended into `SEMANTIC_AMBIGUITIES.md`. A future run may fold it into the master register under an explicit instruction.
- **Producer:** Claude Code (Opus 4.8), Phase 4.7. **No Owner Gate opened; no DECISION created; no fix applied.**

---

## AMB-0047

| Field | Value |
|-------|-------|
| **finding_id** | AMB-0047 |
| **source_doc** | strategy_audit.md (SRC-204) |
| **source_section** | §1 F-1\* and §3 (S-5.3, §5.2/§11.1) |
| **severity** | CRITICAL (from audit; not re-rated) |
| **summary** | F-1\* livelock cell — `ExposureTolerance` (τ_E) may be below the venue `$10` minimum order value, creating a reachable dead-band that blocks progression yet admits no executable correction. See C.8 result. |
| **category** | SEMANTIC_BLOCKING_PENDING_VERIFICATION → (verified) SEMANTIC_BLOCKING (conditional on calibration region) |
| **mapped_to** | `research/findings/F1_VERIFICATION.md` |
| **rationale** | Independent verification required before any Owner Gate, per the Owner's decision that an audit finding ≠ an accepted strategy decision. Verification performed against `Strategy.md` (primary) and cached venue evidence; audit arithmetic reproduced exactly. |
| **affects_str** | STR-0339 (ExposureTolerance), STR-0298, STR-0315, STR-0074, STR-0077 |
| **affects_cap** | CAP-0003, CAP-0016, CAP-0023 |
| **status** | **VERIFIED_BLOCKING** — confirmed at the D-16 default scenario (τ_E=$5 < q_min=$10; reachable lot points $6/$7/$8/$9; no escape rule in the strategy text; persistent). **Conditional across the calibration grid:** present iff `StepBps · MaxBasketNotional < 600,000`; empty at `StepBps=20` with `MaxBasketNotional ≥ 30,000`. |
| **verdict** | F1_CONDITIONAL (CONFIRMED where present) — see `F1_VERIFICATION.md` §C.8 |
| **recommended_next (NOT executed)** | Open a **narrower** Owner Gate scoped to the region `StepBps · MaxBasketNotional < 600,000` to decide between a tradability-quantized gate / round-to-zero rule (audit R-1 family) vs a calibration constraint enforcing `τ_E ≥ q_min`. Owner decides; not opened in this run. |
| **date** | 2026-09-22 |

> U-1..U-8 (SRC-204) and the GA Golden Genome (SRC-206) are **not** classified in this run; they remain unverified hypotheses / an exploratory proposal (see `GA_CLASSIFICATION.md`). Only F-1\* was verified in Phase 4.7.
