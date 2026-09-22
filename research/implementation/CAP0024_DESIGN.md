# CAP0024_DESIGN.md — Reference Model conceptual design (Phase 6b-2)

- **Purpose:** conceptual design of CAP-0024, the independent reference model used as the **primary oracle** for the deterministic domain core (VALIDATION_PLAN §2, §3.2, §4). **Design only — no code, no language/paradigm selection (that is GATE-019).**
- **Producer:** Claude Code (Opus 4.8), Phase 6b-2. **Status:** conceptual; behavioral design (Part B) is final as specified; language/paradigm selection is OPEN (GATE-019 / DECISION-021).
- **Authoritative inputs (read-only):** `VALIDATION_PLAN.md` (§2 oracles, §3 mechanisms, §4 independence); `EVENT_MODEL.md` (10 event kinds, identity, watermark, snapshot); `INTERFACE_MAP.md` (boundaries, observation model); `ARCHITECTURE_DECISION.md` §4 (Research layer offline), §6 (canonical order); `STRATEGY_CONTRACT.md` (362 STR-*); `DECISION_REGISTER.md` (DECISION-002/007/008/013/016..020).
- **Phase-labelling:** 6b-2 (this run) = CAP-0024 design + GATE-019; consumes Phase-6b-1 as input. Working subdivision of `prompt.md` Phase 6.

---

## Part A — Purpose and independence requirements

### §A1 Purpose
CAP-0024 is the **independent reference model**: it re-derives the expected state and expected emitted events from the **normative contract** (`Strategy.md` → `STRATEGY_CONTRACT.md`) over the **same (command, observation) sequences** that production consumes, and is the primary oracle for the deterministic core (VALIDATION_PLAN §2 priority 3, §3.2). It is **offline and NON_RUNTIME** — it must **never be linked into the runtime entrypoint** (ARCHITECTURE_DECISION §4 Research layer).

### §A2 Independence requirements (from VALIDATION_PLAN §4)
- CAP-0024 **MUST NOT share code** with production domain logic — **no shared module, library, or file in any case** (this holds whether GATE-019 picks a different language or the same language with strict structural separation).
- Whether CAP-0024 uses a **different language/paradigm** or the **same language with strict structural separation** is the subject of **GATE-019** (Part C/E). This section fixes only the independence **properties** the choice must satisfy; it does not choose.
- Every CAP-0024 test artifact **records:** `Strategy.md` SHA-256, `STRATEGY_CONTRACT.md` version, config version, reference-model version, and (where applicable) venue-evidence versions (SRC ids + snapshot dates).
- CAP-0024 is **itself versioned**; **production must not depend on any CAP-0024 artifact at runtime.**

### §A3 Inputs CAP-0024 consumes (conceptual, from Phase 6b-1)
- the **ordered event sequence** (all 10 event kinds, EVENT_MODEL §A2);
- the **canonical-order rules** (DECISION-007; EVENT_MODEL §A3);
- the **per-stream watermarks** (EVENT_MODEL §D);
- the **observation model** (freshness, partial reads, snapshot handling; INTERFACE_MAP "External observation model");
- the **config** (calibration parameters, dynamic-default *formulas*, contract version).

### §A4 Outputs CAP-0024 produces (conceptual)
- a **folded state**, identical in shape to production domain state;
- a set of **emitted events**, identical in shape to production-emitted events;
- for each emitted event, a **reason code** (DECISION-013 family);
- for each folded state, an **invariant-result vector** (which §15 invariants hold / fail).

---

## Part B — Behavioral obligations

### §B1 / §B2 — Behaviors CAP-0024 MUST reproduce, with the exercising mechanism

Bidirectional mapping (**behavior ↔ VALIDATION_PLAN §3.x mechanism**). **20 behavioral obligations (B-01..B-20).**

| # | Behavior CAP-0024 must reproduce | STR / DECISION basis | VALIDATION_PLAN mechanism |
|---|----------------------------------|----------------------|---------------------------|
| B-01 | §4 Generation lifecycle transitions (evolution trigger, one-successor lock, dominance, G99) | STR-0024..0067 | §3.2, §3.4, §3.13 |
| B-02 | §5 Cycle lifecycle (terminal event, transition sequence, reference capture, non-overlap N1–N3) | STR-0071..0108 | §3.2, §3.4, §3.8, §3.13 |
| B-03 | §6 execution assurance (POSITION_VERIFIED ⇔ fill ∧ authoritative delta) | STR-0129..0138 | §3.2, §3.9 |
| B-04 | §11 exposure (Expected/Actual/Delta; tradability-quantized gate) | STR-0199/0212; STR-0345/0346 | §3.10, §3.3 |
| B-05 | §12 risk model (caps; MaxExposureImbalance; MaxBasketNotional) | STR-0221..0227; STR-0340 | §3.16, §3.3 |
| B-06 | §13 Basket lifecycle (freeze, closure preconditions, states) | STR-0234..0250 | §3.11, §3.4 |
| B-07 | §15 invariants + STR-0344..0360 hold/fail vector | §15; STR-0344..0360 | §3.3 |
| B-08 | Economics: NetExpectedEdge with GGE = StepBps closed form | STR-0193/0349/0350 | §3.15 |
| B-09 | Funding accumulator + two-leg breaker (ACC; FUNDING_WARN/BREAK) | STR-0352..0355 | §3.3, §3.12 |
| B-10 | NET PnL governance (never gross) | STR-0234/0235/0250 | §3.11 |
| B-11 | Reason codes unique per transition | DECISION-013 | §3.13 |
| B-12 | Fail-closed behaviors: RECONCILIATION_REQUIRED, LEVEL_SKIPPED, FUNDING_BREAK, BLOCKED, FREEZE, RESUME | STR-0077/0035; DECISION-014 | §3.3, §3.5, §3.7 |
| B-13 | Ordering outcomes identical under DECISION-007 permutation | STR-0063/0315/0334; DECISION-007 | §3.1, §3.6 |
| B-14 | Precision/rounding outcomes (§6.3; tick/lot; N-overlap on submittable prices) | STR-0135..0138; STR-0361 | §3.8 |
| B-15 | Acute vs non-acute distinction | STR-0356/0357 | §3.10, §3.15 |
| B-16 | MarginMode assertion outcomes (startup ABORT / P0 FREEZE) | STR-0358..0360 | §3.3, §3.9 |
| B-17 | Duplicate/delayed/missing-event resolution (snapshot dedup, gap → reconcile) | DECISION-007; EVENT_MODEL §C3/§D | §3.7 |
| B-18 | Authoritative vs derived state ownership (clearinghouseState only for ST-08/ST-17) | DECISION-002; STATE_OWNERSHIP | §3.9 |
| B-19 | Persistence/replay: fold reproduces state + emitted events from log | STR-0315/0334; §8 | §3.1, §3.14 |
| B-20 | Hard exposure caps: reject (not silent clip) on breach | STR-0141..0161; STR-0227 | §3.16 |

Every VALIDATION_PLAN mechanism §3.1–§3.16 is exercised by ≥1 obligation above (§3.5 failure-injection and §3.14 restart also consume CAP-0024 as the expected-state oracle; §3.17 venue/API observation is out of scope, §B3).

### §B3 — Explicitly OUT OF SCOPE for CAP-0024
- Any behavior requiring **live venue access** — rate-limit observation, real fills, real funding accruals, real liquidation, real order acks (VALIDATION_PLAN §3.17). Those are **Phase 10–12** (recorded observations).
- Any behavior that depends on the **actual value** of a dynamic-default — only the **formula** is in scope for CAP-0024; the calibrated **value** is resolved separately (CALIBRATION-REPORT.md, Phase 13). CAP-0024 checks formula-consistency and ordering, not the specific calibrated number.
- Technology/latency/performance behavior (throughput, snapshot cadence) — those are Phase 6c/7 operational concerns, not reference-model obligations.

---

## Part C — Candidate languages/paradigms (NO selection)

### §C0 Dependency note (binding framing)
The **production runtime language is itself NOT yet selected** (a separate future Owner Gate, required before Phase 7). Therefore each candidate is framed as either **ABSOLUTE** (a concrete choice regardless of production) or **EXPLICITLY CONDITIONAL** on the production choice (e.g. "a different paradigm family from whatever production uses, concrete language pinned once production's is chosen"). GATE-019 states this dependency so the Owner may answer **absolutely, conditionally, or by deferring** the relative options. **Candidates are labelled REF-A..F** (NOT CAND-*, which denote the Phase-4/5 architecture families).

### §C1 / §C2 — Candidate table

| Ref | Family | Independence from production (common-mode-bug resistance) | Expressiveness (event-fold + invariant checks) | Testability (differential / property / exhaustive) | Dev cost (owner effort) | Framing | Recommendation strength |
|-----|--------|-----------------------------------------------------------|------------------------------------------------|------------------------------------------------------|-------------------------|---------|-------------------------|
| **REF-A** | Same language as production, separate codebase, no shared modules | **Weak–Moderate** — same language/stdlib/idioms ⇒ correlated bugs (numeric, ordering) can recur | High (mirrors production's expressiveness) | High (easy to run the same sequences) | Low | **CONDITIONAL** on production selection | **Weak** — least independence; correlated failure modes undercut CAP-0024's purpose |
| **REF-B** | Different general-purpose language, chosen for structural separation | **Moderate–Strong** — different stdlib/numeric/idioms reduce common-mode bugs | High | High | Medium | **ABSOLUTE**, or CONDITIONAL if framed "different from production" | **Moderate** — good independence at moderate cost; concrete pin needs production known if framed relatively |
| **REF-C** | Formal/specification language or property tool (TLA+, Alloy, or similar) | **Strong** — different computational model ⇒ strongest independence; excels at invariants/exhaustive | Moderate (excellent for invariants/state exploration; less natural for full economic arithmetic/event-shape parity) | Very high for invariants/exhaustive (§3.3/§3.4/§3.6); weaker for full emitted-event parity (§3.2) | Medium–High (specialist skill) | **ABSOLUTE** | **Moderate–Strong** for the invariant/exploration slice; may need pairing with REF-B/D for full emitted-event differential |
| **REF-D** | Reference implementation in a functional language | **Moderate–Strong** — pure-fold paradigm fits event-sourcing; different paradigm from a likely-imperative production | High (fold + algebraic state is natural) | High (deterministic replay + property tests) | Medium | **ABSOLUTE**, or CONDITIONAL as REF-B | **Moderate–Strong** — paradigm fit for the fold; strong independence if production is imperative |
| **REF-E** | Declarative rule-based / constraint-based model | **Strong** — very different execution model | Moderate (rules/constraints express invariants and transitions well; economic arithmetic and event-shape parity less direct) | High for invariants/transitions; medium for emitted-event parity | Medium–High | **ABSOLUTE** | **Moderate** — strong independence, but parity on emitted-event shape/economics needs care |
| **REF-F** | Designer-proposed hybrid: a functional/formal reference for the domain fold + a thin differential-comparator (see Part D), keeping the reference paradigm-distinct from production | **Strong** — combines paradigm distinctness (fold) with formal invariant checks | High overall (covers fold parity + invariants) | Very high (covers §3.1/3.2/3.3/3.4/3.6) | Medium–High | **ABSOLUTE** or CONDITIONAL (pin the fold language once production known) | **Moderate–Strong** — most complete coverage; highest design effort |

### §C3 — No selection
This design does **NOT** select a candidate. The selection is the subject of **GATE-019 / DECISION-021**.

---

## Part D — Test-harness requirements (conceptual)

### §D1 Differential-testing harness (VALIDATION_PLAN §3.2)
Requires:
- a **deterministic input generator** (commands + observations) producing ordered event sequences;
- **both CAP-0024 and production** consuming the **same ordered event sequence**;
- a **comparator** flagging any **state / emitted-event / reason-code / invariant** divergence not attributable to a recorded input difference;
- a **coverage tracker** mapping run scenarios to VALIDATION_PLAN mechanisms (§3.x).

### §D2 Independence rules for the harness
- the **harness must not share code with production**;
- the harness must be **runnable offline**;
- the harness's **results are artifacts, not authority** — only the authorized oracles (VALIDATION_PLAN §2) are authority.

### §D3 Exhaustive-exploration support (VALIDATION_PLAN §3.4)
- CAP-0024 must run under a **bounded exhaustive enumerator** over the domain **≤ 2 Generations × ≤ 2 Cycles × ≤ 2 Levels × ≤ 2 intents**;
- the enumerator's output must be **deterministic** given the same input set.

---

## Status

Behavioral design (Part B, 20 obligations) is **final as specified** and Phase 6c (non-blocking constraint resolution) may proceed on it — **6c does not need the language selection**. The **reference-model implementation and the differential harness (Phase 7)** cannot be built until **GATE-019** selects the language/paradigm (**RESOLVED 2026-09-22 — see below**).

## Forward note (GATE-019 resolution, 2026-09-22)

Selected: **REF-D** (functional reference), CONDITIONAL. **REF-C (formal/spec) is retained as a possible complementary slice in Phase 9+ for invariant/exhaustive verification** — NOT a second CAP-0024 language, and NOT selected in this Gate. No production runtime language commitment is made. (DECISION-021; OWNER_GATE_019.)
