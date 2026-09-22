# PHASE6_SCHEDULE.md — Scheduling of SEMANTIC_NON_BLOCKING items (Phase 6a)

- **Producer:** Claude Code (Opus 4.8), Phase 6a. **Scheduling only — NOT decisions.** No DECISION is created here; these items have obviously-correct fail-closed/deterministic resolutions and need no Owner strategy-semantic decision.
- **Phase-labelling:** 6a = input prep (this run); 6b = event model + interface + CAP-0024 reference-model design; 6c = non-blocking constraint resolution. Working subdivisions of `prompt.md` Phase 6.
- **Source:** Phase 4.9 verifications (`research/findings/U3/U5/U6/U8_VERIFICATION.md`, `U_VERIFICATION_SUMMARY.md`, `U_AMB_RECORD.md`).

## Phase 6 scheduling — SEMANTIC_NON_BLOCKING items

**U-3 — N3 min-separation ε (STR-0361).**
Scheduled: Phase 6b (event model + interface) and Phase 6c (constraint resolution). Note on fail-closed direction: the current N3 equality-only test is NOT itself fail-closed for this gap — the strategy does not treat "possible near-overlap" as BLOCKED, so leaving N3 as equality-only silently permits near-adjacent same-group orders. Therefore STR-0361 (require `|p_new − p_live| ≥ max(1 tick, 0.1·StepBps·p/10⁴)`) is IMPLEMENTED during Phase 6c (not merely deferred to a fail-closed default). Owner: Phase 6c.

**U-5 — cloid = reconciliation identity (STR-0133 annotation; DECISION-008 governs).**
Scheduled: Phase 6c (documentation annotation only; no runtime change — DECISION-008 already closes the operational path via reconcile-before-retry / never-assume-dedup). Owner: Phase 6c.

**U-6 — closure rounding direction (annotation-level per Phase 4.10; no STR).**
Proposal: `τ_R := max(ceil_lot(f), q_min(M))` (fixes A-10) — the `q_min` floor is what preserves tradability so a final min-size sweep drives `szi → 0` exactly. Scheduled: Phase 6c (constraint resolution). Owner: Phase 6c.

**U-8 — REST rate budget (STR-0362).**
Scheduled: Phase 6c (operational policy); MAY be promoted to Phase 6b if the event model imposes cadence/refresh constraints that need the budget defined earlier. Owner: Phase 6c (or 6b, if referenced by the design).

> These four are BINDING Phase-6/7 work items with fail-closed defaults until resolved (per ARCHITECTURE_DECISION §11), but they are NOT Owner strategy-semantic decisions. No gate opened; no DECISION created.
