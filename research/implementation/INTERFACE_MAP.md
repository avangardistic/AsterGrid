# INTERFACE_MAP.md — Conceptual interface / boundary map (Phase 6b-1)

- **Purpose:** conceptual map of the CAND-B boundaries (Core / Event Log / Adapters / Signing / Operator / Persistence), what crosses each, and the invariants enforced — plus the external observation model. **Design only — no code, no interface stubs, no language, no product.**
- **Producer:** Claude Code (Opus 4.8), Phase 6b-1. **Status:** conceptual.
- **Authoritative inputs (read-only):** `ARCHITECTURE_DECISION.md` §4/§6/§7/§8; `EVENT_MODEL.md` (this phase); `STATE_OWNERSHIP.md`; `DECISION_REGISTER.md` (DECISION-002/007/008); `VALIDATION_PLAN.md` §4.

---

## §B1 — Boundaries (conceptual)

### B1.1 Core ↔ Event Log
- **Crosses OUT (Core→Log):** new events (intent, command, timer, state-transition) — append-only.
- **Crosses IN (Log→Core):** the ordered event sequence for folding.
- **Never:** no side effect occurs inside the Core; the Core neither touches the network nor reads wall-clock/ambient state — it only folds recorded events and emits new events.
- **Invariants:** append-only + immutable (STR-0315/0334); the fold is pure and total (STR-0047..0053).

### B1.2 Core ↔ Adapters
- **Crosses OUT (Core→Adapter):** **command** events (a fully-decided, already-recorded side effect to execute).
- **Crosses IN (Adapter→Log):** **observation / acknowledgment / fill / error** events (the four externally-originating kinds).
- **Never:** the Core **never awaits an adapter synchronously to make a decision** — decisions are folds over recorded events; an adapter never decides.
- **Invariants:** persist-before-act (STR-0298); externally-originating facts enter only as recorded events (DECISION-007).

### B1.3 Adapters ↔ External Venue (REST + WS)
- **Crosses OUT (Adapter→Venue):** signed messages derived from recorded command events (via the signing boundary, B1.4).
- **Crosses IN (Venue→Adapter):** venue emissions (acks, fills, book/mark, clearinghouseState, meta, funding, errors), each **translated into a recorded event**.
- **Never:** the venue never writes to the log directly; **venue-specific field names never leak into Core state** — the adapter normalizes at the boundary.
- **Invariants:** normalization at the adapter edge; authoritative reads only from clearinghouseState (DECISION-002); freshness/gap handling (Part C, EVENT_MODEL §D).

### B1.4 Signing Boundary (adapter edge — security boundary)
- **Crosses OUT:** a **fully-decided command, already recorded as a command event, with its cloid**.
- **Crosses IN:** only the resulting **signed-message outcome** (the fact that signing/submission occurred and its result) — **NEVER secret material**.
- **Never:** no secret (API key, private key, signature-as-secret, credential) is ever present in Core state, in the Event Log, in observability output, or in any artifact (ARCHITECTURE_DECISION §7).
- **Invariants:** the signer verifies it is signing the correct, non-stale recorded intent (AMB-0029); secret isolation (STR-signing-boundary / ARCHITECTURE_DECISION §7).

### B1.5 Operator Surface (adapter edge)
- **Crosses OUT (Operator→Log):** **operator** events — arm approval/denial, freeze, resume, kill-switch, owner clearance — with operator/service identity + timestamp.
- **Crosses IN (system→Operator):** gated arm requests / status only.
- **Never:** operator input **cannot bypass §8/§10 gates** — approval only further restricts arming (STR-0168, arm-gate invariant 3); it never overrides FREEZE (STR-0168 inv.2).
- **Invariants:** timeout → fail-closed, never auto-execute (STR-0169); resume/clearance per DECISION-014; identity+timestamp recorded (STR-0171).

### B1.6 Persistence Adapter
- **Crosses OUT/IN:** event records to/from the durable event store behind a port.
- **Never:** it **reads/writes only event records; it never recomputes domain state** (folding is the Core's job).
- **Invariants:** **deterministic readback** for replay; the store is behind a port (no product chosen here).

---

## §B2 — Per-boundary summary (never / must / failure / invariant)

| Boundary | Must NEVER cross | MUST cross (normal path) | Failure behavior (fail-closed) | Enforced invariants (STR/DECISION) |
|----------|------------------|--------------------------|--------------------------------|------------------------------------|
| B1.1 Core↔Log | side effects; ambient/wall-clock reads | events out (append), event sequence in (fold) | log unavailable → no new command emitted | STR-0315/0334; STR-0047..0053 |
| B1.2 Core↔Adapters | Core awaiting adapter to decide | command out; observation/ack/fill/error in | adapter unavailable/stale → dependent gate fails closed | STR-0298; DECISION-007 |
| B1.3 Adapters↔Venue | venue writing log directly; venue field names into Core | signed msg out; normalized events in | venue error/disconnect → error event, fail-closed | DECISION-002; STR-0163 freshness |
| B1.4 Signing | secret material inward (log/Core/obs/artifacts) | decided command out; signed-outcome in | signer mismatch/stale → refuse, RECONCILIATION_REQUIRED | ARCHITECTURE_DECISION §7; AMB-0029 |
| B1.5 Operator | bypass of §8/§10 gates; auto-execute on timeout | operator events (identity+ts) | timeout → fail-closed (cancel/hold) | STR-0168/0169/0171; DECISION-014 |
| B1.6 Persistence | recomputing domain state | event records r/w; deterministic readback | store fault → replay from log; no guess | STR-0315/0334; DECISION-008 |

## §B3 — Cross-boundary invariants

1. **No side effect without a durably-recorded causal event first** (persist-before-act; STR-0298).
2. **The Core never reads a non-recorded input** (all external facts enter as recorded observation/ack/fill/error events).
3. **No secret material ever reaches the log, the Core, or observability output** (ARCHITECTURE_DECISION §7).

---

## External observation model

### §C1 — What an observation event is
An **observation event** (EVENT_MODEL §A2(e)) is an authoritative/observed venue read (clearinghouseState, meta, fee tier, funding accruals, l2Book, mark/oracle) captured with:
- **source endpoint** (which venue read);
- **read timestamp** (local receive);
- **canonical-order keys** (venue-seq if available, else server-ts, else local-ts — DECISION-007);
- **payload fingerprint** (content hash);
- **freshness window** (max-age policy per data type, §C2).
- **partial vs full:** incomplete reads are **marked partial** and **never silently treated as full** (a partial clearinghouseState / book read is recorded as partial; gates requiring completeness fail closed).

### §C2 — Freshness policy (conceptual)
- Each data type (mark/oracle, book, meta, fee, account state, fills) has a **maximum age** (a per-type max-age; concrete numbers are Phase-6c/7 — VALIDATION_PLAN §3.7/§3.17, AMB-0019).
- **Stale → the observation event is recorded as STALE**; any gate that depends on it **fails closed** (no decision on stale data).

### §C3 — Venue-emitted snapshot handling
- A venue snapshot is **marked as snapshot** (not incremental);
- **snapshot duplication is a no-op keyed by content fingerprint** (idempotent — cf. STR-0352 funding dedup);
- **WS gap → RECONCILIATION_REQUIRED** until snapshot reconciliation completes (DECISION-007; EVENT_MODEL §D).

### §C4 — Sole entry path
**Observation events are the ONLY path by which external facts enter the system.** No adapter may write to Core state directly; every external fact becomes a recorded event that the Core folds.

---

## Forward reference: CAP-0024 Reference Model governance

The CAP-0024 reference model design is the subject of **Phase 6b-2**. Per `CLAUDE.md` and the Owner-Gate policy, the **selection of a language/paradigm for CAP-0024** that differs from (or matches) the production runtime is an **Owner-Gate-scoped decision**. Phase 6b-2 will therefore:
- restate the independence requirements (VALIDATION_PLAN.md §4: **no shared code with production**, to avoid common-mode bugs; every test artifact records the versions it ran against);
- list candidate languages/paradigms;
- **NOT select one** — the selection goes through an Owner Gate.

**This section is a governance note, NOT a decision.** No DECISION-021 is created and no Owner Gate is opened in this run.
