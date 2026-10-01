# BOUNDARY_CANDIDATES.md — Phase 4 (boundary discovery)

- **Purpose:** For each capability, evaluate the smallest boundary that satisfies its requirements (per `prompt.md` `<boundary_discovery>`/`<no_predefined_subsystems>`/`<anti_overengineering>`). **Default: NOT a separate process/service.** A separate boundary is justified only if it materially improves ≥1 of: correctness, state ownership, consistency, failure isolation, security isolation, latency, scaling, persistence, recovery, testability, deployment, operations. **No architecture chosen here.**
- **Producer:** Claude Code (Opus 4.8), Phase 4.
- **Inputs (read-only):** `CAPABILITY_MAP.md`, `STATE_OWNERSHIP.md`, `STRATEGY_CONTRACT.md`.
- **Boundary vocabulary:** function · pure-domain-module · adapter · library · workflow-node · background-task · independent-process · independent-service · external-dependency.

## Summary table (smallest justified boundary)

| CAP | Capability | Smallest justified boundary | Separate process/service? | One-line reason |
|-----|-----------|-----------------------------|---------------------------|-----------------|
| CAP-0001 | Market/Venue Observation | **adapter** (+ background-task for I/O) | NO (in-process async task) | I/O concurrency is a task, not a service; normalization is pure. |
| CAP-0002 | Authoritative State Reconciliation | **adapter** (+ background-task for polling) | NO | Reads clearinghouseState; single owner of ST-08/ST-17; no isolation gain from separation. |
| CAP-0003 | Execution Assurance / POSITION_VERIFIED | **pure-domain-module** | NO | Pure gate over fills ∧ delta; core determinism. |
| CAP-0004 | Identity & Lifecycle Mgmt | **pure-domain-module** | NO | Pure; owns identity registry. |
| CAP-0005 | Transition Orchestration & Precedence | **pure-domain-module** | NO | The deterministic core pass engine. |
| CAP-0006 | Generation Lifecycle | **pure-domain-module** | NO | Pure state machine. |
| CAP-0007 | Evolution Evaluation | **pure-domain-module** | NO | Pure evaluation over verified evidence. |
| CAP-0008 | Cycle Lifecycle & Reference Capture | **pure-domain-module** | NO | Pure; reference capture uses observed price as input. |
| CAP-0009 | Grid Geometry | **function/pure-domain-module** | NO | Pure computation. |
| CAP-0010 | Sizing & Cap Enforcement | **pure-domain-module** | NO | Pure; uses live mark as input. |
| CAP-0011 | Arm-Gate Evaluation | **pure-domain-module** | NO | Pure gate list; approval is a gated input (CAP-0019). |
| CAP-0012 | Fillability Analysis | **function** (pure over L2 snapshot) | NO | Pure computation over a book snapshot. |
| CAP-0013 | Execution Economics | **function/pure-domain-module** | NO | Pure computation over live fees/costs. |
| CAP-0014 | Intent Construction & Normalization | **pure-domain-module** (+ security boundary for signing) | NO (signing is a security boundary, not a service) | Normalization pure; **signing/wallet is a security boundary** (Owner-gated), not a topology decision. |
| CAP-0015 | Order Execution & Lifecycle | **adapter** (+ background-task for exec I/O) | NO | Side-effecting venue I/O; isolate as adapter, decisions stay in core. |
| CAP-0016 | Exposure & Hedge/Mirroring | **pure-domain-module** | NO | Pure over ST-07/ST-08. |
| CAP-0017 | Risk-Bound Evaluation | **pure-domain-module** | NO | Pure over trackers + observed margin. |
| CAP-0018 | Basket Lifecycle & Closure | **pure-domain-module** | NO | Pure state machine + closure verification. |
| CAP-0019 | Operator Control / Arm Approval | **adapter/port** (external input) | NO (in-process port; external actor is the dependency) | External human/service is an external-dependency; the gate is in-core. |
| CAP-0020 | Config & Calibration Resolution | **library/pure-domain-module** | NO | Deterministic resolution; fail-closed. |
| CAP-0021 | Persistence & Reconstruction | **adapter/port** (durable store behind a port) | NO (store may be a separate *resource*, not a service we build) | Recovery/reconstruction need a durable store; a store resource ≠ a microservice. |
| CAP-0022 | Observability & Audit | **adapter/library** | NO | Logging sink behind a port. |
| CAP-0023 | Fail-Closed Safety Enforcement | **cross-cutting pure-domain concern** | NO | Cross-cutting guard, not a component. |
| CAP-0024 | Reference Model & Differential Testing | **external-dependency (research-only)** | N/A — NON_RUNTIME | Offline harness; MUST NOT be a runtime dependency. |

**Result:** the deterministic strategy core (CAP-0003..0018, 0020, 0023) is best expressed as **pure in-process domain modules sharing one authoritative state owner set**; the only boundaries the evidence justifies are **adapters/ports at the edges** (venue I/O, persistence, operator input, observability) and a **security boundary** for signing. No capability requires an independent service, microservice, agent, or external orchestration engine.

---

## Detailed evaluation — the 6 flagged capabilities

### CAP-0001 — Market/Venue Observation & Normalization
- Options: adapter (venue read) + background-task (async subscription/poll).
- **Decision: in-process adapter + background task; NOT a separate service.**
- Justification: concurrency for WS/REST is an execution-model detail (task/loop), not a boundary that improves correctness or isolation; normalization is pure and belongs in-core. A separate service would add deployment/operational cost and a network hop with **no** correctness/state-ownership gain (it owns only the ephemeral observed cache ST-19, non-authoritative). Failure isolation is achieved by fail-closed gates, not by process separation.

### CAP-0002 — Authoritative State Reconciliation (clearinghouseState)
- Options: adapter (read) + background-task (poll) + reconciliation logic (pure-domain).
- **Decision: in-process adapter + pure reconciliation; NOT a separate service.**
- Justification: it is the single owner of ST-08/ST-17 (authoritative venue reads); centralizing it in-process guarantees the single-source-of-truth rule (DECISION-002) more simply than a remote service. Separation would introduce a consistency boundary between "read" and "use" with no benefit and added staleness risk.

### CAP-0015 — Order Execution & Lifecycle Tracking
- Options: adapter (exchange endpoint) + background-task (exec I/O) + pure decision logic in-core.
- **Decision: in-process adapter for side effects; NOT a separate service.**
- Justification: side-effecting I/O is isolated behind an adapter for testability and for idempotency handling (cloid/nonce), but the *decisions* (what/when to submit, bounded emergency, skip) MUST stay in the deterministic core to preserve determinism and AI-independence. A separate execution service would fragment order/exposure state ownership across a network boundary — a correctness risk, not a gain. (Latency optimization, if ever needed, is a Phase-6/7 concern.)

### CAP-0021 — Persistence & Event Reconstruction
- Options: port/adapter over a durable store (the store may be a separate *resource*).
- **Decision: a durable store behind an in-process port; NOT a service we build.**
- Justification: recovery/reconstruction (STR-0315/0334) genuinely requires durable persisted state — this is the one place a *separate resource* (a datastore) is justified by the recovery/persistence criteria. But that is a **technology/resource** choice (Phase 6/7), not an application microservice; the application accesses it through a port. No independent application service is warranted.

### CAP-0019 — Operator Control / Arm Approval
- Options: port/adapter for external approval; external actor (human/service) is the dependency.
- **Decision: in-process port; the operator/webhook service is an external-dependency.**
- Justification: the external approver is inherently outside the process (security/authority isolation is intrinsic), but the **arm gate and timeout→fail-closed logic are deterministic and belong in-core** (approval is a *gated input*, never a decision). WEBHOOK mode's external service is an external-dependency, not a component we design. This keeps runtime determinism intact (external input cannot bypass §8/§10).

### CAP-0024 — Reference Model & Differential Testing
- Options: external-dependency, research-only.
- **Decision: NON_RUNTIME research artifact; explicitly NOT a runtime boundary.**
- Justification: `prompt.md` `<reference_model>` wants a pure offline model for differential testing; it MUST NOT be a runtime dependency (the runtime must be AI-independent and self-contained). It lives entirely in the research/test tier.
