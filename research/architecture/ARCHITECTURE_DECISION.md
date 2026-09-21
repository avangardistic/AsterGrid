# ARCHITECTURE_DECISION.md — Phase 5 (architecture decision)

- **Purpose:** Record the single binding architecture decision for the runtime, turning the Owner's Phase-4 candidate selection into the authoritative architecture for Phase 6 onward. This file records a decision; it does **not** select any technology (language / framework / database / protocol / library / deployment target) — those are Phase 6/7.
- **Version:** 1.0 (Phase 5).
- **Producer:** Claude Code (Opus 4.8), Phase 5.
- **Inputs (read-only):**
  - Phase 4 artifacts: `ARCHITECTURE_CANDIDATES.md` (CAND-A/B/C + rejected CAND-D/E + microservices), `STATE_OWNERSHIP.md` (23 single-owner states), `BOUNDARY_CANDIDATES.md`, `FAILURE_BOUNDARIES.md` (11 failure modes), `CAPABILITY_MAP.md` (CAP-0001..0024), `CAPABILITY_COVERAGE.md`.
  - Phase 1 contract: `STRATEGY_CONTRACT.md` (344 STR-*, incl. STR-0344).
  - Phase 4.5/4.6 audits: `SEMANTIC_AMBIGUITIES.md` (46 AMB-*), `DECISION_REGISTER.md` (DECISION-001..014).
  - Owner selection: CAND-B, recorded 2026-09-21.
- **Status:** ACCEPTED (Owner-selected 2026-09-21).
- **Validation status:** Decision recorded deterministically from Phase-4 evidence; no runtime behavior validated here (validation is Phase 9+). `Strategy.md` SHA-256 re-verified unchanged this phase (`085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`).

---

## §1 — Decision

**Selected architecture family: CAND-B — Event-Driven Single Process / Event-Sourced (deterministic replay).**

Owner-selected 2026-09-21. A single process/deployable in which an **append-only event log is the source of truth**; all domain state is a deterministic fold (replay) over recorded events. Commands → (pure deterministic decision) → events → state. The deterministic domain core is identical to that common to all Phase-4 candidates; CAND-B fixes the **persistence / recovery / reconstructability model** as event-sourced.

This decision selects an architecture **family and its interpretation constraints only**. It does not select a language, framework, database, event-store product, serialization format, snapshot policy, signing library, deployment target, or observability stack.

---

## §2 — Rationale (why B over A / C / D / E)

The Phase-4 comparison matrix rates all three viable candidates HIGH on strategy fidelity, determinism, and state ownership — they share an identical pure deterministic core. They differ materially only in **persistence / recovery / reconstructability**. CAND-B is selected because a set of **mandatory** STR-* requirements and Owner decisions make full-history reconstructability and deterministic replay a first-class correctness property, which CAND-B satisfies natively while CAND-A and CAND-C satisfy only by bolting on a disciplined audit trail.

Grounds (not generic preference):

**(a) Phase-4 comparison matrix.** CAND-B is rated **HIGH** on Recovery ("full replay"), Persistence ("log is persistence"), and Observability ("event log is the audit"); CAND-A is **MEDIUM** on Recovery/Persistence (journal+checkpoint) and CAND-C **MEDIUM** on Recovery (current-state reload) — both needing an *added* audit log to reach CAND-B's reconstructability. The matrix already notes CAND-B has "strongest reconstruction guarantee; ideal for FM-08/FM-09."

**(b) The mandatory requirements that made the difference:**
- **STR-0315 / STR-0334 (§15 invariant 19 — every transition reconstructable):** CAND-B's append-only log *is* the reconstruction substrate (ST-13); reconstructability is structural, not an add-on. This is the decisive requirement.
- **STR-0298 (persist-before-side-effect / cloid persisted before network submission):** an event-sourced write path makes "append intent+cloid event, then act" the natural and enforced ordering (ties to DECISION-008 recovery).
- **STR-0325 / STR-0326 (fail-closed; no transition solely on intended orders):** decisions are pure functions over recorded events; a transition is produced only from verified/observed events, never from an unrecorded intent — the log distinguishes intent events from authoritative-outcome events.
- **§4.7 P0–P6 total-order determinism (STR-0047..STR-0053):** the pass engine consumes events in a canonical total order and emits events deterministically; replay reproduces the exact P0–P6 ordering.
- **STR-0344 (one active order per Level — Phase 4.6 / DECISION-004):** an invariant checked against the folded per-Level projection; event sourcing gives an unambiguous, replayable per-Level order history to enforce it.
- **DECISION-002 (clearinghouseState authority):** authoritative venue truth (ST-08 ActualExposure, ST-17 CapitalBase) enters the system as **observation events** recorded when read — so replay is faithful and venue reads are auditable.
- **DECISION-007 (canonical event order; tie-break):** provides the deterministic ordering anchor that makes event replay reproducible (see §6).

**(c) Why the alternatives are not selected:**
- **CAND-A (modular monolith, journal+checkpoint):** viable and simplest, but reconstructability (STR-0315/0334) rests on checkpoint discipline and is weaker than a log-as-truth model; the matrix rates its Recovery/Persistence only MEDIUM. Retained as the documented migration target (see §9).
- **CAND-C (layered ports/adapters, store-as-truth):** conventional and transactional, but "replay any transition" (STR-0315/0334) requires an *added* disciplined audit log on top of the current-state store — i.e. it reintroduces CAND-B's log anyway to meet the same requirement.
- **CAND-D (external workflow engine) — REJECTED at Phase 4:** introduces a heavy external runtime dependency, in tension with the deterministic, self-contained, AI-independent mandate; no STR-*/CAP-* requires it.
- **CAND-E (actor model) — REJECTED at Phase 4:** nondeterministic message interleaving fights the required total-ordered §4.7 pass; would need re-serialization, reintroducing the pass engine.
- **Microservices / multi-process — REJECTED a priori:** no failure mode requires a service boundary; distributing the deterministic core fragments single-owner state across the network. One active Basket per market (STR-0005) means no scaling driver.

---

## §3 — Interpretation (binding)

The Owner's interpretation of CAND-B, recorded verbatim as architecture-level constraints. **These fourteen constraints are BINDING for Phase 6 onward.** Any Phase-6/7 design that contradicts one requires a new, versioned decision in `DECISION_REGISTER.md`.

1. Single process.
2. Single active Basket.
3. Single authoritative deterministic core.
4. No microservices.
5. No external workflow engine.
6. No actor-based strategy concurrency.
7. No Kafka-style distributed event architecture.
8. Event Log as the durable source of truth.
9. Deterministic replay.
10. Pure domain decision functions.
11. External venue access only via adapters.
12. `clearinghouseState` remains the authoritative venue truth (per DECISION-002).
13. Signing isolated as a security boundary.
14. CAP-0024 (Reference Model / Differential Testing) remains fully offline.

---

## §4 — Layer model (conceptual — no technology)

Conceptual layers only. No product, protocol, or interface signature is chosen here.

- **Core (pure domain):** the deterministic state machine, decision functions, the event fold (state = fold over events), and the deterministic pass engine implementing §4.7 P0–P6. Pure: no I/O, no wall-clock reads, no randomness; identical inputs → identical outputs/events. Hosts CAP-0003..0018, 0020, 0023.
- **Event Log (durable source of truth):** append-only, immutable, the reconstruction substrate (ST-13, CAP-0021). Deterministic replay reconstructs any state to any point. **Snapshotting strategy is a Phase-6 decision** (a performance optimization over the log, never a replacement authority).
- **Adapters (side-effect boundary):** the only place side effects occur — venue I/O (REST/WS: CAP-0001 observe, CAP-0002 authoritative reads, CAP-0015 execution), persistence I/O, signing, and the operator surface. Adapters only *deliver recorded inputs to* / *carry out committed effects from* the core; they make no domain decisions.
- **Signing Boundary:** a security boundary isolating secret material (see §7). Secrets live only here; they never cross into Core, the Event Log, decision inputs, logs, or any artifact.
- **Operator Surface:** gated input only (CAP-0019). Approvals/arm requests are recorded events with identity+timestamp (STR-0171); timeout → fail-closed; the operator surface cannot bypass the §8/§10 gates or safety precedence.
- **Research (offline):** CAP-0024 reference model / differential testing. Reuses the same pure Core over the same event/command sequences but is **never linked into the runtime entrypoint** — zero runtime dependency.

---

## §5 — State ownership under CAND-B

Each of the 23 states in `STATE_OWNERSHIP.md` is realized as exactly one of:
- **(a) in-core authoritative state derived by folding the event log** (domain/persisted/derived state), or
- **(b) authoritative venue state read from `clearinghouseState` and recorded as an observation event when observed** (venue-authoritative point-in-time truth).

No state has two owners; where a concept has a desired and an authoritative form (ST-05 intent vs outcome; ST-18 desired vs authoritative open orders) they remain **distinct single-owner states**, both realized as folds of their respective event streams.

- **(a) In-core, folded from the event log (21 states):** ST-01, ST-02, ST-03, ST-04, ST-05, ST-06, ST-07, ST-09, ST-10, ST-11, ST-12, ST-13 (the log itself), ST-14, ST-15, ST-16, ST-18 (desired), ST-19 (observation events; non-authoritative cache), ST-20, ST-21, ST-22, ST-23.
- **(b) Venue-authoritative, recorded as observation events (2 states):** **ST-08 (ActualExposure)** and **ST-17 (CapitalBase / account equity)** — sourced **ONLY** from `clearinghouseState` per DECISION-002 (`assetPositions[].position.szi`; `marginSummary.accountValue` incl. unrealized PnL). `webData2/webData3` is forbidden as authority anywhere.

Note: ST-19 (market observation cache) and ST-18 (observed) are *observed_venue_state* — non-authoritative; they enter as observation events but are never the authority for a decision. ST-21's unrealized-PnL input and ST-18's authoritative position context derive from clearinghouseState (category (b) source) even though the states themselves are folded/derived.

**Count: (a) in-core = 21; (b) venue-authoritative = 2; total 23; states with two owners = 0.**

---

## §6 — Determinism guarantees

**Guaranteed:**
- The Core is **pure**: decision/fold functions are total, side-effect-free, and reference no wall-clock, randomness, or ambient state.
- Adapters are **side-effect-only**: they deliver recorded inputs and carry out committed effects; they never decide.
- **Replay is deterministic:** folding the same event sequence reproduces the same state and the same emitted events, including the exact §4.7 P0–P6 pass ordering.
- **No AI/LLM/prompt/agent participates in any runtime decision** — the runtime is AI-independent (mandate reaffirmed). Event sourcing records decisions; it never moves decisions into the log.

**Determinism anchor — canonical event-order tie-break (DECISION-007), applied verbatim:**
> canonical event order = **(venue sequence when present) → (server timestamp) → (local receive timestamp) → (monotonic local counter as final tie-break)**. All observation/timer events that affect a decision are recorded in the event log; a WS gap → `RECONCILIATION_REQUIRED` until snapshot reconciliation.

**NOT guaranteed (by construction, out of scope for this decision):**
- Determinism of the *external venue* or network timing — hence authoritative reads are re-read and reconciled (DECISION-002/008), not assumed.
- That an *un-recorded* observation or timer is reproducible — replay fidelity requires every decision-affecting observation/timer to be recorded (a Phase-6 event-discipline obligation; see §12).
- Wall-clock real-time performance / latency bounds (a Phase-6+ concern; snapshotting addresses replay cost, not determinism).

---

## §7 — Signing boundary

The signing boundary is a security boundary at the adapter edge. **What crosses out:** a signed action (order submit/cancel/TWAP) constructed from an already-decided, already-recorded intent (cloid persisted before submission per STR-0298 / DECISION-008). **What never crosses in:** secret material of any kind.

**Explicit statement:** No secret material (API keys, private keys, signatures-as-secrets, or any credential) is present in the event log, in core state, in the decision path, in operator/observability logs, or in any research artifact. The signer verifies it is signing the correct, non-stale intent (AMB-0029) and emits only the outcome; key lifecycle (rotation/revoke/recovery, AMB-0030) is a Phase-6/7 security design.

---

## §8 — Recovery model (conceptual)

On crash/restart:
1. **Replay** the event log to reconstruct current state deterministically (the log is the source of truth; snapshots, if adopted in Phase 6, only shortcut replay).
2. **Reconcile external side effects against `clearinghouseState`** (authoritative, DECISION-002) plus `orderStatus`/`openOrders`/`userFills`, **before emitting any new intent** — any pending `UNKNOWN_SUBMISSION` is resolved first (DECISION-008).
3. **Idempotency is cloid-based with reconcile-before-act** (DECISION-008): the venue is not assumed to dedup by cloid, so identity is used for lookup/reconciliation, never as an assumption of at-most-once submission.

No detailed recovery protocol is defined here; the protocol, snapshot cadence, and reconciliation sequencing are Phase 6+.

---

## §9 — Migration / reversibility

- **To CAND-A (modular monolith):** the event log can be demoted to a journal behind a persistence port, with in-memory modules made authoritative and periodically checkpointed. **Gained:** lower operational complexity, simpler mental model. **Lost:** native full-history reconstructability (STR-0315/0334 would then rest on checkpoint+journal discipline) and free differential-replay. Feasible because the pure Core is unchanged between families (Phase-4 notes CAND-A "can evolve to CAND-B", so the reverse demotion is also mechanical).
- **To CAND-C (layered store-as-truth):** project the folded state into a current-state store behind a repository port and treat the event log as a secondary audit trail. **Gained:** transactional current-state commits, conventional layering. **Lost:** log-as-authority; reconstructability would depend on retaining the audit log (i.e. partially retaining CAND-B).
- **Reversibility rating: MEDIUM** — the pure Core carries over unchanged in every direction; the commitment being made is the **event schema / log-as-truth**, so migrating *away* means a log/schema migration. This is the cost noted in §12.

---

## §10 — What this decision does NOT decide (explicit non-decisions)

- Programming language.
- Framework / runtime library.
- Database or event-store product.
- Event schema / serialization format.
- Snapshot policy (cadence, format, retention).
- Signing library / key-management product.
- Deployment target / cloud provider / packaging.
- Observability stack (metrics/log/trace products).
- Any class name, function signature, module/file layout, or interface definition.

These are Phase 6 (Implementation Plan) and Phase 6/7 (technology) decisions.

---

## §11 — Constraints carried forward from Phase 4.5 / 4.6 (BINDING inputs to Phase 6/7)

These are **BINDING inputs to Phase 6/7, not nice-to-haves.** Any Phase-6/7 design that contradicts one requires a new DECISION in `DECISION_REGISTER.md`.

**(1) The 25 SEMANTIC_NON_BLOCKING findings** (`SEMANTIC_AMBIGUITIES.md`) — each has an obviously-correct fail-closed/deterministic resolution recordable without Owner authority, but each MUST be explicitly resolved in its named phase:
- AMB-0012 (non-overlap tested on tick/lot-normalized submittable prices), AMB-0013 (MarketDepth coverage vs l2Book ≤20 / ±10×StepBps window), AMB-0014 (ExposureTolerance below min-tradable size; quantization/round-to-zero), AMB-0015 (rounding direction / boundary equality), AMB-0016 (record dynamic-default inputs + calibration version/effective-time for replay), AMB-0017 (side-effect ordering / atomic decision boundary beyond §4.7), AMB-0018 (evidence gap ≠ continuity in confirmation window), AMB-0019 (per-data-type freshness/age policy), AMB-0020 (REST vs WS precedence/reconciliation), AMB-0021 (TWAP parent/child, remaining-qty, crash-mid-TWAP), AMB-0022 (cancellation-in-flight state), AMB-0023 (rejection taxonomy → skip/retry/recalc/freeze), AMB-0024 (market/IOC slippage propagation to reference/cost/non-overlap), AMB-0025 (account/margin/position-mode pinned; feeds GATE-005), AMB-0026 (venue drift handling + Strategy/venue version binding), AMB-0027 (output/reporting contract; no success-before-settlement), AMB-0028 (rate-limit/backoff/open-order-cap model), AMB-0029 (signer verifies correct non-stale intent; forensic trail), AMB-0030 (API-key rotation/revoke/recovery lifecycle), AMB-0031 (kill-switch / cancel-all / flatten-all semantics), AMB-0032 (owner-gate/policy/calibration versioning during an active Basket), AMB-0033 (numeric domain/type system & boundary cases), AMB-0042 (CycleReferenceDerivation — **already RESOLVED by DECISION-009**), and the two DEFERRED findings below.
  - **DEFERRED (2), carried as later-phase verification/validation obligations, not Phase-6 decisions:**
    - **AMB-0034** — verification obligations (reference model, invariant/property, exhaustive, failure-injection, differential replay, precision, depth, survivability, liveness, mutation) → Phase 7/9/10-12 (CAP-0024).
    - **AMB-0035** — economic/risk realism (gap risk, exec latency, liquidity collapse, adverse selection, funding shock) → Phase 10 (economic validation).

**(2) D-16 HYPOTHESIS labelling (DECISION-006):** the runtime reads venue-reported `liquidationPx` and per-asset maintenance margin (`clearinghouseState` / margin tiers) as the primary maintenance/liquidation model; the §16 `0.5 / Leverage_effective` formula is an illustrative conservative floor only. D-16 formulas are HYPOTHESIS; **re-validation is a Live prerequisite.**

**(3) Dedicated-account constraint (DECISION-005 / DECISION-011):** the account is dedicated to one Basket; any exposure not attributable to a strategy intent is contamination → `RECONCILIATION_REQUIRED` / `FREEZE`. Funding/fees are allocated per-position from `userFunding` / fill-fee fields; `accountValue ≈ Basket capital`.

**(4) STR-0344 (one active order per Level at any time)** (DECISION-004): the architecture must support a per-Level projection that enforces at-most-one active order per Level; ambiguity → fail-closed.

**(5) CycleReferenceDerivation-must-be-explicit (DECISION-009 / OPEN-01 closure):** `CycleReferenceDerivation` MUST be set explicitly in runtime config; the Strategy.md value is a template only; a runtime without an explicit setting fails closed (BLOCKED).

---

## §12 — Risks and open questions

- **Event schema discipline (Phase-6 cost, acknowledged; not a blocker):** event sourcing commits to an event schema and its versioning. Migrating away (§9) means a log migration. This is the price of the reconstructability guarantee CAND-B was chosen for.
- **Snapshotting strategy (Phase-6 cost, acknowledged; not a blocker):** replay cost grows with log length; a snapshot policy is needed for performance. Snapshots are an optimization over the log, never a replacement authority.
- **Replay fidelity of external inputs:** every decision-affecting observation/timer MUST be recorded (per DECISION-007), or replay diverges. This is an event-discipline obligation on Phase 6 (tracked as AMB-0016).
- **Un-decided NON_BLOCKING findings may surprise Phase 6:** any of the 25 SEMANTIC_NON_BLOCKING findings not yet decided may surface a design fork in Phase 6 and MUST be resolved there explicitly (fail-closed default until resolved). The 2 DEFERRED findings (AMB-0034/0035) are later-phase verification/validation obligations and are not resolved by architecture.
- **D-16 hypothesis (carried, §11.2):** risk remains HIGH until controlled observation confirms the maintenance/liquidation model; re-validation gates Live.

---

## Confirmations

- No technology selected (no language / framework / database / event-store / protocol / library / deployment / observability product).
- No implementation detail defined (no class name, function signature, file layout, event schema, or interface).
- No trading code written; no Testnet/Live connection; no order submitted.
- No agent/subsystem roster defined.
- No STR-* normative content changed; `Strategy.md` unmodified.
- All 13 Owner Gates remain RESOLVED (DECISION-001..014); none reopened.
