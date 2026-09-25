# STATE_OWNERSHIP.md — Phase 4 (state-ownership discovery)

- **Purpose:** For every authoritative runtime state the Strategy requires, name exactly one owner, its source of truth, writers/readers, persistence, consistency, recovery, and reconciliation trigger (per `prompt.md` `<state_ownership>`). Prerequisite input to architecture comparison. **No architecture chosen here.**
- **Producer:** Claude Code (Opus 4.8), Phase 4.
- **Inputs (read-only):** `STRATEGY_CONTRACT.md` (382 STR-*, incl. Phase 4.6/4.10/6c additions), `CAPABILITY_MAP.md` (CAP-0001..0024), `DECISION_REGISTER.md` (DECISION-002 binds ActualExposure/CapitalBase to clearinghouseState).
- **Status:** COMPLETE — 23 states; each has a single owner (zero multi-owner states).

## State-kind legend (per `prompt.md` `<state_ownership>`)
`desired_state` (what the system intends) · `local_state` (transient working memory) · `persisted_state` (durable, reconstructable) · `derived_state` (computed from other state) · `observed_venue_state` (read from venue, non-authoritative cache) · `authoritative_venue_state` (venue truth, DECISION-002: clearinghouseState).

Fields: state_id · name · kind · owner · source_of_truth · writers · readers · persistence · versioning · consistency · recovery · reconciliation_trigger · notes.

---

### ST-01 — Basket lifecycle state
- kind: persisted_state · owner: **CAP-0018** · source_of_truth: internal domain (CAP-0018) · writers: CAP-0018 (+CAP-0023 freeze/error overlay via ST-22) · readers: all runtime CAPs · persistence: YES · versioning: event-sequenced · consistency: STRONG · recovery: reconstruct from event log (ST-13) · reconciliation_trigger: §4.7 P0 each pass · notes: INITIALIZING…ACTIVE…FROZEN…CLOSED/ERROR/RECOVERY.

### ST-02 — Generation states (per Generation)
- kind: persisted_state · owner: **CAP-0006** · source_of_truth: domain state machine · writers: CAP-0006 (transitions), CAP-0007 (successor creation event) · readers: CAP-0005/0007/0008/0016/0018 · persistence: YES (immutable history) · versioning: append-only per Generation · consistency: STRONG · recovery: reconstruct from event log · reconciliation_trigger: precedence pass · notes: CREATED…SUCCESSOR_CREATED…DISABLED_AT_CYCLE_99…CLOSED_ONLY_AS_PART_OF_BASKET.

### ST-03 — Cycle states (per Cycle)
- kind: persisted_state · owner: **CAP-0008** · source_of_truth: domain state machine · writers: CAP-0008 · readers: CAP-0005/0006/0009/0016 · persistence: YES (immutable) · versioning: append-only per Cycle · consistency: STRONG · recovery: reconstruct from event log · reconciliation_trigger: terminal event + P0 · notes: TERMINAL_PENDING→COMPLETED; reconcile before COMPLETED (STR-0074/0084).

### ST-04 — Level pipeline states
- kind: persisted_state · owner: **CAP-0003** · source_of_truth: fills (venue) ∧ authoritative delta (ST-08) · writers: CAP-0003 (+CAP-0011 arm, CAP-0015 exec) · readers: CAP-0007/0008/0016/0009 · persistence: YES · versioning: per-Level event sequence · consistency: STRONG · recovery: reconcile via CAP-0002 + snapshot userFills · reconciliation_trigger: fill event / P0 · notes: INTENT…POSITION_VERIFIED/CANCELLED/EMERGENCY/SKIPPED/ERROR; LOCKED→IDLE; LEVEL_SKIPPED (§9.3).

### ST-05 — Order intents & outcomes
- kind: desired_state (intent) + persisted_state (outcome) · owner: **CAP-0015** (lifecycle) with CAP-0014 (construction) · source_of_truth: venue acks/orderStatus for outcome; local for intent · writers: CAP-0014 (create), CAP-0015 (submit/cancel/track) · readers: CAP-0003/0016/0018/0021 · persistence: YES · versioning: per-order event sequence · consistency: STRONG · recovery: reconcile via orderStatus + cloid · reconciliation_trigger: order update / P0 · notes: intent (desired) is distinct from authoritative outcome.

### ST-06 — cloid registry
- kind: persisted_state · owner: **CAP-0014** · source_of_truth: internal (client-assigned 128-bit) · writers: CAP-0014 · readers: CAP-0015 (submit/cancel-by-cloid), CAP-0003 · persistence: YES — **persisted BEFORE network submission** (STR-0298) · versioning: append-only · consistency: STRONG · recovery: cloid enables idempotent identity/lookup on restart · reconciliation_trigger: on restart with pending intents · notes: replay control is venue nonce (not cloid); duplicate-cloid dedup NOT venue-documented.

### ST-07 — ExpectedExposure
- kind: derived_state · owner: **CAP-0016** · source_of_truth: Σ VERIFIED filled qty over {PARTIALLY_FILLED,FILLED,POSITION_VERIFIED} · writers: CAP-0016 · readers: CAP-0016/0005/0018 · persistence: derivable (recompute) · versioning: recomputed · consistency: STRONG (deterministic derivation) · recovery: recompute from ST-04 · reconciliation_trigger: each pass · notes: never uses requested_qty (STR-0199).

### ST-08 — ActualExposure
- kind: authoritative_venue_state · owner: **CAP-0002** · source_of_truth: **clearinghouseState.assetPositions[].position.szi (DECISION-002)** · writers: CAP-0002 (records latest read) · readers: CAP-0016/0017/0018/0005 · persistence: snapshots persisted for audit · versioning: timestamped snapshots · consistency: authoritative point-in-time (venue) · recovery: re-read clearinghouseState · reconciliation_trigger: §4.7 P0, cycle/closure steps · notes: NEVER from local bookkeeping or webData2/3.

### ST-09 — ExposureDelta
- kind: derived_state · owner: **CAP-0016** · source_of_truth: ExpectedExposure(ST-07) − ActualExposure(ST-08) · writers: CAP-0016 · readers: CAP-0005/0016/0017 · persistence: derivable · versioning: recomputed · consistency: STRONG · recovery: recompute · reconciliation_trigger: each pass · notes: gates progression (STR-0205).

### ST-10 — Reference prices (per Cycle/Generation)
- kind: persisted_state · owner: **CAP-0008** · source_of_truth: execution-grounded capture (§5.4), tolerance-gated (§5.4.1) · writers: CAP-0008 · readers: CAP-0009 · persistence: YES (full precision) · versioning: per Cycle/Generation · consistency: STRONG · recovery: reconstruct from event log · reconciliation_trigger: at fire (tolerance check) · notes: never raw last-tick.

### ST-11 — Calibration / configuration parameters
- kind: persisted_state · owner: **CAP-0020** · source_of_truth: §14 owner-confirmed values + §16 formulas (Strategy.md authority) · writers: CAP-0020 (resolve once) · readers: all runtime CAPs · persistence: YES · versioning: config version + provenance (calibrated vs dynamic-default) · consistency: STRONG (computed once → binding, §14 global rule) · recovery: re-resolve from confirmed config · reconciliation_trigger: init / owner change · notes: fail-closed on missing; DECISION-001 (read meta.maxLeverage live).

### ST-12 — Operator arm requests / approvals
- kind: persisted_state · owner: **CAP-0019** · source_of_truth: operator/service (external input); gating deterministic · writers: CAP-0019 · readers: CAP-0011 · persistence: YES (identity + timestamp, STR-0171) · versioning: per request · consistency: STRONG · recovery: reconstruct; pending requests fail-closed on restart · reconciliation_trigger: arm request lifecycle · notes: timeout→fail-closed; never auto-approve.

### ST-13 — Event log / audit trail
- kind: persisted_state (append-only) · owner: **CAP-0021** · source_of_truth: itself (authoritative history) · writers: all runtime CAPs (via CAP-0021) · readers: CAP-0021/0022, recovery, CAP-0024 (offline) · persistence: YES (immutable) · versioning: monotonic sequence · consistency: STRONG · recovery: this is the recovery substrate · reconciliation_trigger: n/a · notes: every transition reconstructable (STR-0315/0334).

### ST-14 — Dominance flag (per successor Generation)
- kind: persisted_state · owner: **CAP-0006** (fixed at Evolution by CAP-0007) · source_of_truth: parent's recorded traversal · writers: CAP-0007 (set at fire) · readers: CAP-0009 · persistence: YES · versioning: per Generation (immutable once set) · consistency: STRONG · recovery: reconstruct · reconciliation_trigger: at Evolution · notes: never recomputed per Cycle (STR-0056).

### ST-15 — Successor lock (per Generation)
- kind: persisted_state · owner: **CAP-0006** · source_of_truth: successor-creation event · writers: CAP-0006 · readers: CAP-0007 · persistence: YES (permanent once set) · versioning: per Generation · consistency: STRONG · recovery: reconstruct · reconciliation_trigger: evolution eligibility check · notes: ≤1 successor ever (STR-0323).

### ST-16 — Evolution candidate & confirmation window
- kind: local_state (transient timer) + persisted_state (candidate/ineligible records) · owner: **CAP-0007** · source_of_truth: POSITION_VERIFIED evidence + timer · writers: CAP-0007 · readers: CAP-0005/0006 · persistence: candidates/reasons persisted; timer transient · versioning: per candidate · consistency: STRONG · recovery: deferred-candidate carry-forward; timer resets on de-verification · reconciliation_trigger: each pass over verified evidence · notes: single Evolution in-flight per Basket (lock).

### ST-17 — Account equity / CapitalBase
- kind: authoritative_venue_state · owner: **CAP-0002** · source_of_truth: **clearinghouseState.marginSummary.accountValue (incl. unrealized PnL) (DECISION-002)** · writers: CAP-0002 · readers: CAP-0010 (MaxBasketNotional), CAP-0017 · persistence: snapshots for audit · versioning: timestamped · consistency: authoritative point-in-time · recovery: re-read · reconciliation_trigger: computation time / P0 · notes: NEVER from webData2/3.; row typed 7h-4a (risk_state.py)

### ST-18 — Open-order registry (desired vs authoritative)
- kind: desired_state (local) + observed_venue_state/authoritative (venue) · owner (desired): **CAP-0015**; owner (authoritative truth): **CAP-0002** via orderStatus/openOrders · source_of_truth: venue orderStatus/openOrders for truth; local for desired · writers: CAP-0015 (desired), CAP-0002 (observed) · readers: CAP-0011 (headroom), CAP-0016 · persistence: desired YES; observed cached · versioning: per order · consistency: desired STRONG; observed EVENTUAL until reconciled · recovery: reconcile desired↔venue · reconciliation_trigger: order updates / P0 · notes: two *distinct* states (desired vs authoritative), each single-owner — not a shared-authority violation.

### ST-19 — Market observation cache
- kind: observed_venue_state · owner: **CAP-0001** · source_of_truth: venue info/WS (mark/oracle/mid/L2/funding/fee/meta) · writers: CAP-0001 · readers: CAP-0008/0009/0010/0012/0013/0016/0017 · persistence: logged for audit, not authoritative · versioning: timestamped snapshots · consistency: EVENTUAL (bounded staleness ~3s) · recovery: re-poll / WS snapshot · reconciliation_trigger: feed update · notes: stale/missing → fail-closed upstream gates.

### ST-20 — Risk-bound trackers (lifetime-to-date)
- kind: persisted_state · owner: **CAP-0017** · source_of_truth: cumulative costs/DD/failed-level counts derived from ST-05/0018/0021 · writers: CAP-0017 · readers: CAP-0017/0018 · persistence: YES (lifetime-to-date, D-15) · versioning: cumulative · consistency: STRONG · recovery: reconstruct from event log · reconciliation_trigger: continuous · notes: feeds TotalSystemCosts, MaxHedgeCost, MaxFailedLevelRate.; row typed 7h-4a (risk_state.py)

### ST-21 — Basket PnL accounting (NET)
- kind: derived_state (persisted checkpoints) · owner: **CAP-0018** · source_of_truth: realized (fills) + unrealized (clearinghouseState) − fees + funding · writers: CAP-0018 · readers: CAP-0017/0018 · persistence: checkpoints persisted · versioning: recomputed · consistency: STRONG · recovery: recompute from ST-05/0013 + clearinghouseState · reconciliation_trigger: each pass / closure · notes: NET governs all lifecycle decisions (STR-0235); unrealized input is clearinghouseState-derived.; row typed 7h-4a (risk_state.py)

### ST-22 — Freeze / Error / Recovery overlay
- kind: persisted_state · owner: **CAP-0023** (with CAP-0018 basket-state) · source_of_truth: guard/safety evaluation · writers: CAP-0023 · readers: all runtime CAPs · persistence: YES · versioning: event-sequenced · consistency: STRONG · recovery: freeze/recovery per §13.3 · reconciliation_trigger: safety-invariant breach / P1 · notes: overlay never erases underlying lifecycle state (STR-0047).; row typed 7h-4a (risk_state.py)

### ST-23 — Mirror targets / hedge intents
- kind: derived_state · owner: **CAP-0016** · source_of_truth: verified cumulative fill (symmetric recompute) · writers: CAP-0016 · readers: CAP-0011/0014 (gated correction orders) · persistence: intent records persisted · versioning: recomputed per incremental fill · consistency: STRONG · recovery: recompute from ST-04 · reconciliation_trigger: each incremental fill · notes: Basket-scoped; always re-enters §8/§10 gates.

---

## Summary
- **23 states; 0 with more than one owner.** Where a concept has both a desired and an authoritative form (ST-18 open orders; ST-05 order intent vs outcome), they are modeled as **distinct single-owner states**, not shared authority.
- **STRONG consistency:** ST-01–ST-07, ST-09–ST-17, ST-18(desired), ST-20–ST-23 (all domain/persisted/derived state).
- **EVENTUAL/point-in-time:** ST-08 & ST-17 (authoritative venue reads, point-in-time), ST-18(observed), ST-19 (observed cache).
- **Sourced from clearinghouseState (DECISION-002):** **ST-08 (ActualExposure)** and **ST-17 (CapitalBase/account equity)**; ST-21's unrealized-PnL input and ST-18's authoritative position context also derive from clearinghouseState. `webData2/webData3` is forbidden as authority anywhere.
