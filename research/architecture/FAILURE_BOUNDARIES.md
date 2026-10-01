# FAILURE_BOUNDARIES.md — Phase 4 (failure-boundary discovery)

- **Purpose:** Identify which failures must be isolated from which capabilities/state, based on the Strategy's fail-closed rules and STATE_OWNERSHIP. Determines whether any failure *requires* a boundary beyond a single process. **No architecture chosen here.**
- **Producer:** Claude Code (Opus 4.8), Phase 4.
- **Inputs (read-only):** `STRATEGY_CONTRACT.md`, `CAPABILITY_MAP.md`, `STATE_OWNERSHIP.md`.
- **Key principle (STR-0023/0004/0131/0315/0343):** fail-closed on ambiguity; a slower verified transition beats a fast unverified one; every transition reconstructable. Isolation is achieved primarily by **fail-closed guards + single-owner state**, not by process/service separation.

Fields: failure_mode · affects (CAPs/state) · must_remain_correct (invariants) · required_isolation_boundary · recovery.

---

### FM-01 — Venue disconnection (REST/WS down or degraded)
- affects: CAP-0001 (ST-19 observations), CAP-0002 (ST-08/ST-17 reads), CAP-0015 (exec I/O).
- must_remain_correct: no state advances without authoritative confirm (STR-0132/0314); progression hard-gated (STR-0205); no unverified transition (STR-0330).
- required_isolation_boundary: **none beyond a fail-closed edge adapter.** Loss of feeds must fail-closed upstream gates (no arming/progression); it must NOT corrupt domain state. An edge adapter (in-process) that surfaces "stale/unavailable" is sufficient.
- recovery: reconnect; WS snapshot (isSnapshot) rebuild; reconcile via CAP-0002 before resuming.

### FM-02 — Partial order fill
- affects: CAP-0003, CAP-0015, CAP-0016 (ST-04/ST-05/ST-07).
- must_remain_correct: exposure = verified filled qty only (STR-0199/0212); unfilled remainder not independently hedged while working (STR-0213); remainder→Emergency/Skip on timeout (STR-0214).
- required_isolation_boundary: **none** — handled deterministically in-core; no cross-process boundary needed.
- recovery: reconcile filled qty via CAP-0002; skipped residual contributes zero.

### FM-03 — Reconciliation divergence (Expected ≠ Actual beyond tolerance)
- affects: CAP-0002, CAP-0016, CAP-0005 (ST-08/ST-09).
- must_remain_correct: Actual only from clearinghouseState (STR-0294); grid progression BLOCKED until within tolerance unless Hedge Recovery active (STR-0205); acute → unconditional hedge (STR-0206).
- required_isolation_boundary: **none** — precedence P0/P1 (CAP-0005) isolates by *ordering* (risk/reconciliation before progression), not by process. Single owner (CAP-0002) prevents split-brain.
- recovery: Hedge Recovery / RECONCILIATION_REQUIRED / freeze; resume only when reconciled.

### FM-04 — Exchange rejection (tick/minNtl/margin/oracle/ALO/IOC rejects)
- affects: CAP-0014, CAP-0015, CAP-0011.
- must_remain_correct: normalize before signing (STR-0138/0299) so rejections are avoided, not relied upon; gate failure → IDLE/PRECHECK not ERROR (STR-0163).
- required_isolation_boundary: **none** — rejection is an adapter-level outcome mapped to a domain state; no separation needed.
- recovery: re-price/re-arm (four-way re-eval) or Skip; never blind retry.

### FM-05 — Stale / out-of-tolerance reference price
- affects: CAP-0008 (ST-10), CAP-0009.
- must_remain_correct: reference within 0.33×StepBps (STR-0096/0098); else BLOCKED fail-closed, no fallback reference (STR-0098/0108); §5.6 non-overlap still authoritative.
- required_isolation_boundary: **none** — deterministic in-core gate; re-evaluate next pass after reconciliation (P0).
- recovery: RECONCILIATION_REQUIRED; re-capture on next pass.

### FM-06 — Freeze / Error / Recovery transition
- affects: CAP-0023/CAP-0018 (ST-22 overlay), all runtime CAPs.
- must_remain_correct: FREEZE blocks ENTRY_INTENT only; EXPOSURE_CORRECTION_INTENT still permitted (STR-0204/0239); overlay never erases underlying state (STR-0047).
- required_isolation_boundary: **none** — overlay is in-core state read by all capabilities; correction path must remain available even under freeze (an *ordering/gating* property, not a process boundary).
- recovery: controlled resume when safe; hedge recovery always available.

### FM-07 — Operator arm timeout / approval failure (SEMI/WEBHOOK)
- affects: CAP-0019, CAP-0011 (ST-12).
- must_remain_correct: timeout NEVER auto-executes (STR-0165); webhook failure NEVER converts to auto-approval (STR-0166); UNSET timeout → BLOCKED (STR-0172).
- required_isolation_boundary: the **external approver** is intrinsically outside the process (external-dependency); the fail-closed gate is in-core. No additional boundary needed.
- recovery: return to IDLE/PRECHECK; re-request next pass.

### FM-08 — Process restart with pending order intents
- affects: CAP-0006/0021/0015/0014 (ST-05/ST-06/ST-13).
- must_remain_correct: every transition reconstructable from persisted state + authoritative events (STR-0315/0334); cloid persisted BEFORE submission (STR-0298); never retry an external effect without establishing whether it already happened (idempotency).
- required_isolation_boundary: requires **durable persisted state** (a store resource) — the one place persistence/recovery criteria justify a separate *resource* (not a service). Reconstruction is in-core.
- recovery: on restart, reconstruct from event log (ST-13), reconcile pending cloids via orderStatus, resume fail-closed.

### FM-09 — Duplicate-submission ambiguity (timeout after send, unknown outcome)
- affects: CAP-0015, CAP-0014 (ST-05/ST-06).
- must_remain_correct: never blind-retry (idempotency, prompt `<idempotency>`); establish whether the effect happened via orderStatus/cloid before acting.
- required_isolation_boundary: **none** — resolved by cloid identity + orderStatus query in-core; venue nonce provides replay protection.
- recovery: query orderStatus by cloid; reconcile; then decide. NOTE: duplicate-cloid dedup is NOT venue-documented (deferred observation) — treat as fail-closed.

### FM-10 — Persistence unavailable (cannot durably record before a side effect)
- affects: CAP-0021, and any side-effecting CAP (CAP-0015/0014).
- must_remain_correct: cloid/intent persisted before network submission (STR-0298); if persistence is unavailable, side effects must NOT proceed (fail-closed).
- required_isolation_boundary: a **durable store resource** must be reachable; if not, halt side effects. No application-service boundary needed.
- recovery: restore store; reconstruct; resume.

### FM-11 — Invariant violation detected (safety guard trips)
- affects: CAP-0023 cross-cutting.
- must_remain_correct: never silently continue; BLOCK/RECONCILIATION_REQUIRED/INELIGIBLE/SKIP with reason (STR-0035/0343); no bypass of gates (STR-0335).
- required_isolation_boundary: **none** — cross-cutting fail-closed enforcement in-core.
- recovery: freeze/recovery; operator decision for escalation.

---

## Conclusion
- **11 failure modes documented.**
- **Failure modes that REQUIRE a boundary beyond a single process: NONE that require a separate *service/process*.** Two failure modes (FM-08, FM-10) require a **durable persisted-state resource** (a datastore), justified by the persistence/recovery criteria — this is a *resource/technology* need (Phase 6/7), not an application microservice. One class (FM-07, operator approval) has an **intrinsic external-dependency** (the human/service approver), which is outside the process by nature, not a boundary we introduce.
- Isolation is achieved by **fail-closed guards + deterministic precedence ordering + single-owner state**, consistent with `prompt.md` `<no_predefined_subsystems>`/`<anti_overengineering>`. No evidence requires distributing the deterministic core.
