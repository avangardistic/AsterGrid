# ARCHITECTURE_CANDIDATES.md — Phase 4 (candidate architecture families)

- **Purpose:** Present materially different, viable architecture FAMILIES for this capability set, evaluated against the 343 STR-* / 24 CAP-* / state-ownership / failure boundaries. **This phase does NOT select a winner (Phase 5) and does NOT choose technologies (Phase 6/7).** Families are described by pattern, not product.
- **Producer:** Claude Code (Opus 4.8), Phase 4.
- **Inputs (read-only):** `STRATEGY_CONTRACT.md`, `CAPABILITY_MAP.md`, `STATE_OWNERSHIP.md`, `BOUNDARY_CANDIDATES.md`, `FAILURE_BOUNDARIES.md`, `DECISION_REGISTER.md`.
- **Ground rules from evidence:** runtime MUST be deterministic and AI-independent (`<mission>`); prefer the smallest architecture (`<anti_overengineering>`); no failure mode requires distributing the deterministic core (FAILURE_BOUNDARIES conclusion); the only justified edge boundaries are adapters/ports (venue I/O, persistence, operator input, observability) + a signing security boundary; CAP-0024 is NON_RUNTIME.

**Common to all candidates (non-negotiable, from evidence):** a deterministic domain core (CAP-0003..0018, 0020, 0023) with single-owner state (STATE_OWNERSHIP), authoritative venue reads from clearinghouseState only (DECISION-002), fail-closed guards, and edge adapters. Candidates differ in **state-ownership model, execution model, failure/recovery model, and consistency model** — not in whether the core is deterministic.

---

## CAND-A — Modular Monolith (deterministic domain core + thin adapters)

- **candidate_id:** CAND-A
- **family:** Modular monolith; single process, single deployable. Authoritative runtime state lives in in-memory domain modules; durability via an append journal + periodic state checkpoints behind a persistence port.
- **summary:** One deployable runs a synchronous deterministic pass engine (CAP-0005) over pure domain modules; edge adapters (venue read/exec, persistence, operator, observability) are thin and side-effecting. The domain core is the source of truth for domain state; the venue is the source of truth for ST-08/ST-17.
- **state ownership:** Each STATE_OWNERSHIP owner is an in-memory module owning its state; ST-08/ST-17 mirror authoritative clearinghouseState reads; persistence port journals mutations for recovery.
- **capability fit:** Core (CAP-0003..0018,0020,0023) = pure in-process modules invoked by the pass engine. Edges: CAP-0001/0002 = read adapters + background poll/subscribe tasks; CAP-0015 = exec adapter; CAP-0019 = operator port; CAP-0021 = persistence port (journal+checkpoint); CAP-0022 = observability sink. CAP-0014 signing behind a security boundary. CAP-0024 offline (not linked into the runtime).
- **failure isolation:** By fail-closed guards + precedence ordering (FM-01..11), not process separation. Adapter failures surface as "unavailable/stale" and fail-closed upstream gates.
- **reconciliation:** CAP-0002 reads clearinghouseState at P0 each pass; divergence → hedge/RECONCILIATION_REQUIRED before progression.
- **persistence:** Append journal of domain mutations + periodic checkpoints; cloid persisted before submit.
- **recovery:** Reload latest checkpoint + replay journal tail; reconcile pending cloids via orderStatus.
- **determinism preserved:** Pass engine is synchronous and total-ordered (§4.7 P0–P6); all async I/O happens at edges and only *delivers inputs* to the deterministic core; no domain decision depends on wall-clock races.
- **operator control (CAP-0019):** Approval is a gated input recorded in ST-12; the pass engine consumes an approval token; timeout→fail-closed. No runtime nondeterminism enters decisions.
- **CAP-0024 (research-only):** Separate offline harness that imports the same pure domain modules for differential testing; never imported by the runtime entrypoint.
- **strengths:** Smallest deployable; simplest state ownership; easiest determinism; lowest operational cost; strong testability of pure core.
- **weaknesses:** Recovery relies on journal+checkpoint discipline (weaker reconstructability guarantee than full event sourcing); in-memory authoritative state must be checkpointed carefully.
- **operational complexity:** LOW. **testability:** HIGH (pure core). **reversibility:** HIGH (can evolve to CAND-B by making the journal the source of truth). **does NOT solve:** full event-sourced auditability out of the box; horizontal scaling (not required).

## CAND-B — Event-Driven Single Process (event-sourced; deterministic replay)

- **candidate_id:** CAND-B
- **family:** Single process/deployable, but the **append-only event log is the source of truth**; all domain state is a deterministic fold (replay) over events. Commands→(deterministic decision)→events→state.
- **summary:** Every state change is an event appended to ST-13; domain state (ST-01..07,09..16,20..23) is derived by replay. Recovery = replay from the log. Venue reads (ST-08/ST-17) enter as observation events.
- **state ownership:** The event log owns history; each projection has a single owner that folds its slice. Authoritative venue truth still clearinghouseState (recorded as observation events).
- **capability fit:** Identical capability set to CAND-A, but each capability emits/consumes events; CAP-0021 is central (the log IS the store); CAP-0005 processes commands deterministically to produce events; edges as in CAND-A.
- **failure isolation:** Same fail-closed model; additionally, crash-safety is strong because state is never authoritative except as a fold of durable events.
- **reconciliation:** clearinghouseState observations are events; divergence handled at P0/P1 exactly as CAND-A.
- **persistence:** The event log itself (append-only, immutable) — directly satisfies STR-0315/0334 reconstructability.
- **recovery:** Deterministic replay from the log to any point; strongest reconstruction guarantee; ideal for FM-08/FM-09.
- **determinism preserved:** Replay is deterministic by construction; command handlers are pure; care required that observation/timer events are recorded (not re-derived) so replay is reproducible.
- **operator control (CAP-0019):** Approvals are events (with identity/timestamp) — naturally satisfies STR-0171 audit.
- **CAP-0024:** The reference model can consume the same event/command sequences for differential testing; still offline, not a runtime dependency.
- **strengths:** Best reconstructability/audit (matches §15 inv.19 directly); crash-safe; natural fit for "every transition reconstructable"; excellent replay/differential-testing story.
- **weaknesses:** More design discipline (event schema/versioning, snapshotting for performance); replay of external observations must be recorded to stay deterministic; higher initial complexity than CAND-A.
- **operational complexity:** MEDIUM. **testability:** HIGH (event replay + differential). **reversibility:** MEDIUM (event schema is a commitment; migrating away means log migration). **does NOT solve:** does not by itself reduce venue-integration complexity; performance needs snapshots.

## CAND-C — Layered Application with Ports & Adapters (store-as-source-of-truth; no event sourcing)

- **candidate_id:** CAND-C
- **family:** Single process; explicit domain / application / infrastructure layers. **Authoritative current state lives in a persisted store behind a repository port**; the domain loads state, decides, and saves the new current state each pass (no event log as source of truth).
- **summary:** Application layer orchestrates a pass: load current state via repository port → run pure domain decisions → persist new state + emit side effects via adapters. Infrastructure (venue, store, operator, observability) is isolated behind ports.
- **state ownership:** The store is the authoritative home of domain current-state; each aggregate has one repository owner; venue truth (ST-08/ST-17) read via venue port.
- **capability fit:** Same capabilities; domain layer = CAP-0003..0018,0020,0023 (pure); application layer = CAP-0005 orchestration; infrastructure = CAP-0001/0002/0015/0019/0021/0022 adapters. CAP-0014 signing in a guarded infra boundary.
- **failure isolation:** Same fail-closed model; store transactionality gives atomic state commits per pass (helps FM-08/FM-10).
- **reconciliation:** clearinghouseState via venue port at P0; divergence handled in domain.
- **persistence:** Current-state store (transactional) behind repository port; audit/event trail is a secondary log (CAP-0022), not the source of truth.
- **recovery:** Reload current state from the store; reconcile pending orders via orderStatus; weaker point-in-time reconstruction than CAND-B unless an audit log is also kept.
- **determinism preserved:** Domain decisions are pure; the load→decide→save cycle is deterministic given loaded state + recorded inputs; ordering per §4.7.
- **operator control (CAP-0019):** Approval via operator port; stored with identity; gated input only.
- **CAP-0024:** Offline harness reuses the pure domain layer; not a runtime dependency.
- **strengths:** Clear separation of concerns; transactional current-state commits; conventional and easy to reason about; good testability via port fakes.
- **weaknesses:** Reconstructability (§15 inv.19) requires an explicit, disciplined audit trail in addition to the current-state store; risk of the store schema drifting from domain invariants; current-state-only recovery loses the "replay any transition" property unless augmented.
- **operational complexity:** MEDIUM (depends on the store). **testability:** HIGH (ports). **reversibility:** MEDIUM. **does NOT solve:** native full-history reconstruction (needs an added audit log to fully meet STR-0315/0334).

---

## Comparison matrix (LOW / MEDIUM / HIGH + one-line rationale; NOT ranked — Phase 5 decides)

| Criterion | CAND-A Modular Monolith | CAND-B Event-Sourced | CAND-C Layered Ports/Adapters |
|-----------|--------------------------|-----------------------|-------------------------------|
| Strategy fidelity | HIGH — pure core expresses all invariants | HIGH — pure core + events express all | HIGH — pure core expresses all |
| Determinism | HIGH — synchronous pass engine | HIGH — deterministic replay (record inputs) | HIGH — load→decide→save is deterministic |
| State ownership | HIGH — single in-memory owners | HIGH — log + single-owner projections | HIGH — single repository owners |
| Failure isolation | MEDIUM — guards+ordering, in-process | MEDIUM/HIGH — crash-safe via log | MEDIUM/HIGH — transactional commits |
| Reconciliation | HIGH — P0 clearinghouseState | HIGH — observations as events | HIGH — venue port at P0 |
| Persistence | MEDIUM — journal+checkpoint | HIGH — log is persistence | MEDIUM/HIGH — transactional store |
| Recovery | MEDIUM — checkpoint+journal replay | HIGH — full replay | MEDIUM — current-state reload (+audit log to match B) |
| Observability | MEDIUM — add audit sink | HIGH — event log is the audit | MEDIUM — add audit trail |
| Security | HIGH — one process, one signing boundary | HIGH — same, events exclude secrets | HIGH — same, ports isolate infra |
| Testability | HIGH — pure core | HIGH — replay + differential | HIGH — port fakes |
| Latency | HIGH (good) — no network hops | MEDIUM/HIGH — append overhead | MEDIUM/HIGH — store round-trips |
| Operational complexity | LOW | MEDIUM — event infra/snapshots | MEDIUM — store ops |
| Deployment complexity | LOW — one deployable | LOW/MEDIUM — one deployable + log store | LOW/MEDIUM — one deployable + store |
| Developer experience | HIGH — simplest mental model | MEDIUM — event discipline | HIGH — conventional layering |
| Scalability | MEDIUM — single process (sufficient; one market/Basket) | MEDIUM — single process | MEDIUM — single process |
| Vendor/framework lock-in | LOW — no engine | LOW/MEDIUM — event-store choice later | LOW/MEDIUM — store choice later |
| Cost | LOW | MEDIUM | MEDIUM |
| Reversibility | HIGH — can grow into B | MEDIUM — log schema commitment | MEDIUM |
| Migration risk | LOW | MEDIUM | MEDIUM |

> All three keep the deterministic core identical; they differ mainly in **persistence/recovery/consistency** (CAND-B strongest reconstructability; CAND-A simplest; CAND-C conventional transactional). Scalability is "MEDIUM/sufficient" for all because the Strategy runs **one active Basket per market at a time** (STR-0005) — horizontal scale is not a requirement.

---

## PART B5 — Rejected candidate families (complexity not justified by any capability)

### CAND-D — Durable Workflow Engine (external orchestration) — **REJECTED**
- What it would add: an external orchestration/workflow engine running the transition pipeline as durable workflows.
- Capability that REQUIRES it: **none.** Durable execution/recovery (its main appeal) is already satisfied by CAND-B (event sourcing) or CAND-A (journal+checkpoint) in-process. No STR-* or CAP-* requires external orchestration.
- Why rejected: (1) introduces a heavy **runtime dependency** on an external engine, in tension with the "deterministic, self-contained, AI-independent runtime" mandate (`<mission>`, `<final_mandate>`); (2) workflow engines impose their own determinism/replay constraints and **vendor/framework lock-in** (`<technology_research>` warns against framework-first); (3) added deployment/operational cost with no correctness/state-ownership/failure-isolation gain the in-process options lack. Per `<anti_overengineering>`/`<no_predefined_subsystems>`: not adopted.

### CAND-E — Actor-Oriented Single Process (message-passing actors) — **REJECTED**
- What it would add: independent actors exchanging messages, each owning a slice of state.
- Capability that REQUIRES it: **none.** No failure mode (FAILURE_BOUNDARIES) requires actor isolation; state ownership is already single-owner without actors.
- Why rejected: the Strategy mandates a **deterministic, total-ordered transition pass** (§4.7 P0–P6, STR-0063; single Evolution in-flight per Basket). Actor concurrency introduces **nondeterministic message interleaving** that fights the required determinism and would need re-serialization to be safe — reintroducing the pass engine anyway. Adds concurrency-reasoning cost for no capability benefit. Per `<anti_overengineering>`: not adopted. (Actor *isolation* ideas, if ever useful at edges, are subsumed by adapters/background tasks in CAND-A/B/C.)

### Microservices / multi-process distribution — **REJECTED (a priori, evidence-based)**
- Capability that REQUIRES it: **none.** FAILURE_BOUNDARIES found zero failure modes requiring a service/process boundary; STATE_OWNERSHIP shows single-owner state best kept co-located; one active Basket per market means no scaling driver. Distributing the deterministic core would fragment state ownership across network boundaries — a correctness risk. Per `<no_predefined_subsystems>`/`<anti_overengineering>`: not a candidate.

---

## Capabilities that do NOT fit any candidate
**None.** All 24 capabilities fit cleanly into each of CAND-A/B/C (core = pure modules; edges = adapters/ports; CAP-0024 = offline). No capability signals a missing family. The candidate set therefore spans the viable architecture space for this evidence.

## Explicit non-decisions (reaffirmed)
No winner selected; no language/framework/database/protocol/deployment target chosen; no `ARCHITECTURE_DECISION.md` created; no `DECISION_REGISTER` architecture entry. Those are Phase 5 (decision) and Phase 6/7 (technology).

---

## Decision (Phase 5, 2026-09-21)
Selected: CAND-B.
Rejected at this phase: CAND-A, CAND-C (reasons: see ARCHITECTURE_DECISION.md §2).
Rejected at Phase 4: CAND-D, CAND-E, microservices.
Owner-selected; see DECISION_REGISTER.md DECISION-015.
