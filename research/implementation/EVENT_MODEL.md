# EVENT_MODEL.md — Conceptual event model (Phase 6b-1)

- **Purpose:** conceptual design of the log-as-truth layer's event model for the CAND-B event-sourced runtime — event KINDS, identity, invariants, the per-stream venue-sequence watermark, and the snapshot concept. **Design only — no code, no serialization format, no language, no product, no schema-as-code.**
- **Producer:** Claude Code (Opus 4.8), Phase 6b-1. **Status:** conceptual (input to Phase 6b-2 CAP-0024 design and Phase 6c/7).
- **Authoritative inputs (read-only):** `ARCHITECTURE_DECISION.md` §4 (layer model), §6 (canonical event order), §7 (signing boundary), §8 (recovery); `DECISION_REGISTER.md` (esp. DECISION-002 clearinghouseState authority; DECISION-007 canonical order; DECISION-008 recovery; DECISION-016..020); `STRATEGY_CONTRACT.md` (362 STR-*); `VALIDATION_PLAN.md`.
- **Phase-labelling:** 6b-1 (this run) = event model + interface map (conceptual); 6b-2 = CAP-0024 reference-model design; 6c = non-blocking constraint resolution. Working subdivisions of `prompt.md` Phase 6.

---

## §A1 — Design principles

- The event **log is append-only and immutable**; it is the durable source of truth (ARCHITECTURE_DECISION §4).
- Every event is **timestamped and uniquely identified** (§A3).
- Events are **folded into state deterministically**; domain state is a pure fold over the event sequence (no authoritative state exists except as a fold).
- The log is the **reconstruction substrate** — every transition is reconstructable from persisted events + recorded authoritative observations (STR-0315 / STR-0334, §15 inv.19).
- **Events record decisions; they never make them.** The pure Core makes decisions (deterministic decision functions over the fold); the log records the decision and its causal facts. Event sourcing is a means of guaranteeing reconstructability, not a license to move decisions into the log.

---

## §A2 — Event taxonomy (conceptual KINDS)

Ten conceptual event KINDS. For each: purpose · minimal conceptual content · writer · primary STR-* served. (No field types; no serialization.)

| # | Kind | Purpose | Minimal conceptual content | Writer | Primary STR-* served |
|---|------|---------|-----------------------------|--------|----------------------|
| (a) | **intent** | a decision by Core to act (open level, hedge/correct, close, arm request, mirror) | intent classification (ENTRY_INTENT / EXPOSURE_CORRECTION_INTENT), target Level/Generation/Cycle, requested size/price concept, cloid, acute/non-acute flag | Core | STR-0298, STR-0344, STR-0356/0357, STR-0208 |
| (b) | **command** | a committed side effect sent to an adapter (submit / cancel / modify / TWAP) — an intent that has crossed the signing boundary | reference to originating intent, cloid, action concept (submit/cancel/…), TIF concept, `expiresAfter` concept | Core (emits) → Signing/Venue adapter (executes) | STR-0298, STR-0133, STR-0138, STR-0254; DECISION-008 |
| (c) | **acknowledgment** | venue ack of a command (resting / filled / error) | venue oid (when present), cloid linkage, ack status concept | Venue adapter | STR-0133, STR-0132 |
| (d) | **fill** | venue fill notification (partial or full) | cloid/oid linkage, filled quantity concept, price concept, snapshot flag | Venue adapter | STR-0131, STR-0071, STR-0199, STR-0212 |
| (e) | **observation** | authoritative/observed venue read (clearinghouseState; meta; fee tier; funding accrual; l2Book; mark/oracle) | source endpoint, read timestamp, canonical-order keys, payload fingerprint, freshness window, full/partial flag | Market/Account adapter (CAP-0001/0002) | STR-0199/0200/0224 (authoritative via clearinghouseState, DECISION-002), STR-0337, STR-0352 |
| (f) | **timer** | internal time-based trigger that affects a decision (confirmation window, emergency timeout, funding-accumulator tick, arm-request timeout) | timer kind, fire timestamp, associated entity | Core (records the tick that a decision consumed) | STR-0036..0039, STR-0169 (arm timeout), STR-0353 (funding tick) |
| (g) | **error** | adapter/venue error that affects a decision (rejection, disconnect, rate-limit) | error class concept (precision/margin/rate-limit/price/risk), source, linkage to command/stream | Adapter | STR-0163, STR-0182, STR-0190; DECISION-008 |
| (h) | **state-transition** | a domain state change produced by the fold (cycle created, evolution triggered, level verified/skipped, basket frozen/closed, FUNDING_WARN/BREAK, RECONCILIATION_REQUIRED) | prior/next state concept, unique reason code, causal-chain reference | Core (from the fold) | STR-0315/0334, DECISION-013 reason codes, STR-0354 |
| (i) | **operator** | arm approval/denial, freeze, resume, kill-switch, owner clearance | operator/service identity, timestamp, action concept, target | Operator adapter | STR-0168/0171, DECISION-014 (resume/clearance) |
| (j) | **administrative** | config change, version pin, calibration applied, MarginMode pin | config/version identity, effective-time concept, provenance | Admin/Config adapter | STR-0257 (versioning), STR-0355/0358 (β_F, MarginMode), STR-0011 (calibration resolve-once) |

**Externally-originating content (only these four):** kinds **(c) acknowledgment, (d) fill, (e) observation, (g) error** are the only event kinds whose *content* originates from outside the process. All others — (a) intent, (b) command, (f) timer, (h) state-transition, (i) operator, (j) administrative — are generated by the Core or by adapters acting on Core decisions / operator input. (Operator (i) content originates from a human/service but enters through the gated Operator surface, not from the venue; it is recorded as a first-class event.)

---

## §A3 — Event identity (conceptual)

Each event carries, conceptually:
- a **monotonic local sequence number** (per log; deterministic, gap-free within the log);
- a **stable event-kind tag** (one of §A2);
- a **causal-predecessor reference** — zero or more prior event identities the event depends on (e.g. a fill references its command/intent; a state-transition references the facts that produced it);
- the **canonical-order keys** from DECISION-007: (venue sequence when present) → (server timestamp) → (local receive timestamp) → (monotonic local counter as final tie-break).

Identity is **deterministic and replay-safe**: replaying the same recorded inputs reproduces the same identities and the same order. No numeric encoding constraint is imposed here beyond determinism; concrete encoding is a Phase-6c/7 concern.

---

## §A4 — Cross-cutting invariants (conceptual)

1. **Persist-before-act:** every **command** event is preceded (in the log) by its **intent** event (STR-0298; DECISION-008). No side effect occurs without its causal event durably recorded first.
2. **Fill causality:** every **fill** event references its originating command/cloid when available; ambiguous attribution → RECONCILIATION_REQUIRED (STR-0344, DECISION-004).
3. **No uncaused transitions:** no **state-transition** event exists without a causal chain ending in recorded facts (DECISION-007 discipline; STR-0073 — price crossing / ack / isolated fill alone are insufficient).
4. **Observation provenance:** every **observation** event captures the source endpoint, the read timestamp, and the validity (freshness) window; authoritative reads (ActualExposure, CapitalBase) come only from clearinghouseState (DECISION-002).
5. **No secrets in the log:** no event ever records secret material (keys, signatures-as-secrets, credentials) — the signing boundary is never crossed inward into the log (ARCHITECTURE_DECISION §7).
6. **Single active order per Level:** intent/command events for a Level respect STR-0344 (at most one active order per Level); a second is rejected/fails-closed.
7. **Determinism:** the fold over the ordered event sequence is pure and total; identical recorded inputs → identical state and identical emitted events (STR-0047..0053 §4.7 order preserved).

---

## §A5 — Event versioning (conceptual)

The log records a **schema version per event** (conceptually — the notion that each event knows the version of the shape it was written under). **Migration policy** (how older-versioned events are folded after a schema change) is a **Phase-6c/7 concern**, not decided here. No serialization or migration mechanism is chosen in this run.

---

## Venue-sequence watermark (per-stream)

### §D1 — Streams that can carry a venue sequence

For each external stream, whether the venue provides a monotonic sequence, and the per-stream **LAST-SEQUENCE WATERMARK** (the highest sequence observed on that stream, stored as part of the log, per stream):

| Stream (concept) | Venue-provided ordering? | Watermark basis | Gap detection |
|------------------|--------------------------|-----------------|---------------|
| `orderUpdates` (WS) | Per-connection ordered stream; block/time ordering, no universal global seq field documented | last accepted (server-ts, local-ts, counter) per stream; treat as ordered-within-stream | out-of-order arrival vs recorded watermark → gap |
| `userFills` (WS) | Snapshot-tagged (`isSnapshot`), then ordered stream; fills carry time/hash | last (time, hash) fingerprint watermark | duplicate fingerprint = no-op; missing between snapshot and stream → gap |
| `userFundings` (WS) | Snapshot then hourly stream; deltas carry (time, coin, hash) | last (time, coin, hash) watermark (feeds STR-0352 accumulator dedup) | duplicate key = no-op; gap → reconcile |
| `webData3` (WS) | Frontend aggregate (non-authoritative); not a decision authority | recorded for observability only; not a decision watermark | n/a for decisions (non-authoritative, DECISION-002) |
| `clearinghouseState` (REST snapshot and/or WS) | Point-in-time authoritative read; carries `time`; no incremental seq | last read timestamp + payload fingerprint | staleness (Part C freshness), not sequence-gap |
| `meta` (REST) | Point-in-time; no seq | last read timestamp + fingerprint | staleness + drift (AMB-0026) |
| `l2Book` / mark-oracle (WS/REST) | Book snapshots on block cadence; `time` field | last (time) watermark | staleness; WS gap → reconcile |

> Where the venue exposes a genuine monotonic per-stream sequence field, the watermark is that field's highest value; where it does not, the watermark is the highest canonical-order key tuple observed on that stream (see §D2). The watermark is **stored as part of the log, per stream** (conceptually a per-stream counter/tuple in the log; **no storage technology chosen**).

### §D2 — Streams without a venue sequence

For REST reads and WS events lacking a venue sequence:
- fall back to the DECISION-007 canonical order keys: **server-ts → local-ts → monotonic local counter**;
- ordering across mixed streams is preserved by merging on the canonical-order keys (a single total order over all recorded events);
- these streams **cannot detect gaps via sequence** and therefore rely on the **freshness policy** (Part C) plus **snapshot reconciliation** (a fresh authoritative read reconciles suspected loss).

### §D3 — Cross-stream invariant (conceptual)

- **No decision may be made if any stream on which it depends has an unresolved gap or a stale watermark** — the dependent gate fails closed (RECONCILIATION_REQUIRED); no decision is made on stale state.
- The **watermark is advanced only by recorded events**, never by ambient/in-memory state — advancing the watermark is itself part of folding a recorded event.

No storage technology is chosen; the watermark is conceptually a per-stream counter/tuple held in the log.

---

## Snapshot policy

### §E1 — Status (verbatim)

**A snapshot is an OPTIMIZATION over the log — never a replacement authority.** The log remains the sole source of truth, and replay from a snapshot must produce exactly the state that replay from the log alone would produce.

### §E2 — Conceptual content of a snapshot

A snapshot captures, conceptually:
- the **per-stream watermarks** (§D);
- the **folded state** at the snapshot point;
- the **log offset** (position in the append-only sequence);
- the **schema version**.

### §E3 — Snapshot triggers (conceptual)

- **periodic** (policy-driven cadence);
- on an observed **log-size threshold**;
- **never during an active side-effect window** — a snapshot must not race with an unresolved command event (it is taken only at a consistent fold boundary).

### §E4 — Snapshot correctness invariants

- **no snapshot may be used as an authority** (only as a replay shortcut);
- a snapshot is **verifiable by replay** from the log to the same offset;
- **mismatch → discard the snapshot, replay from the log**.

### §E5 — Scope note

This section defines **concepts only**. A concrete snapshot **format, cadence, and storage** are **Phase-6c/7** concerns; none is chosen here.
