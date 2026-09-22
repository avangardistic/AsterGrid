# CAPABILITY_MAP.md — Phase 3 Capability Discovery

- **Purpose:** Enumerate every behavior the Strategy materially requires, as **capabilities** (required behaviors), derived from evidence. Per `prompt.md` `<capability_discovery>`/`<boundary_discovery>`: **a capability is NOT a subsystem, service, module, process, or agent.** No boundaries, topology, or technology are decided here (that is Phase 4/5).
- **Producer:** Claude Code (Opus 4.8), Phase 3.
- **Inputs (evidence):** (a) 362 STR-* in `STRATEGY_CONTRACT.md` (343 Phase 1 + STR-0344 Phase 4.6 + STR-0345..0362 Phase 4.10; mappings for the additions are in `CAPABILITY_COVERAGE.md`); (b) venue evidence base (`TOPIC_EVIDENCE.md`, `SDK_RECORD.md`, `SOURCE_MANIFEST.md`); (c) `DECISION_REGISTER.md` (DECISION-001, DECISION-002).
- **Status:** COMPLETE for Phase 3 (24 capabilities; full STR-*→CAP-* coverage in `CAPABILITY_COVERAGE.md`).

---

## Explicit non-decisions (this phase decides NONE of these)

- **No subsystem boundaries** — capabilities are not modules/services.
- **No process model** — nothing about threads/processes/loops is decided.
- **No service topology** — no client/server/microservice layout.
- **No framework or language selection** — Python-first is only a `prompt.md` preference, not chosen here.
- **No persistence technology choice** — "persistence required" states a need, not a DB.
- **No agent design** — no runtime agents; the final runtime is AI-independent.
- **No deployment model** — no containers/cloud/hosting decisions.

Field key per capability: purpose · strategy_requirements_covered · inputs · outputs · state_required · source_of_truth · consistency · timing · security · persistence · failure_behavior · recovery · test_requirements · external_dependencies · deterministic_implementation_sufficient · independent_execution_necessary · notes.

---

### CAP-0001 — Market/Venue Observation & Normalization
- purpose: Observe venue market data (mark/oracle/mid price, L2 book depth, funding rate, live user fees, asset meta/szDecimals/maxLeverage) and normalize into deterministic domain inputs.
- strategy_requirements_covered: STR-0091, STR-0092, STR-0133 (market feeds), STR-0134, STR-0194, STR-0228, STR-0236, STR-0337 (funding/mark/maxLeverage read live), STR-0261-context.
- inputs: venue info/WS feeds (allMids, l2Book, metaAndAssetCtxs, userFees, meta).
- outputs: normalized MarkPrice, OraclePrice, MidPrice, L2 depth (≤20 levels/side), FundingRate, live Fee tier, szDecimals, maxLeverage.
- state_required: latest observed snapshots (ephemeral cache).
- source_of_truth: venue (info/WS); NOT authoritative for position (that is CAP-0002).
- consistency: read-your-writes not required; staleness bounded by venue update cadence (~3s mark/oracle).
- timing: near-real-time; funding hourly; fees per-tier.
- security: read-only; no secrets.
- persistence: observations logged for audit (CAP-0022) but not authoritative state.
- failure_behavior: on missing/stale feed → fail-closed upstream gates (no arming without fresh depth/price).
- recovery: re-subscribe/re-poll; WS snapshot (isSnapshot) on reconnect.
- test_requirements: normalization unit tests; snapshot/stale-feed handling.
- external_dependencies: Hyperliquid info + WS (SRC-105/107/109/112/114/117).
- deterministic_implementation_sufficient: YES (normalization is pure given inputs).
- independent_execution_necessary: MAYBE (I/O-bound; concurrency is a Phase-4/5 boundary decision, not required semantically).
- notes: l2Book bounded to ≤20 levels/side (STR-0228 PARTIALLY_VERIFIED) — MarketDepth window ±10×StepBps may exceed it; open design note for Phase 4.

### CAP-0002 — Authoritative State Reconciliation (clearinghouseState)
- purpose: Read the authoritative position/margin/account state and compute ActualExposure and CapitalBase; detect divergence from expected.
- strategy_requirements_covered: STR-0004, STR-0076, STR-0132, STR-0200, STR-0224, STR-0294, STR-0327, STR-0334(recon), plus reconciliation steps in STR-0074/0084/0249.
- inputs: clearinghouseState (REST + WS): assetPositions[].position.szi, marginSummary.accountValue, withdrawable, cumFunding.
- outputs: ActualExposure (net szi), CapitalBase (equity incl. unrealized PnL), reconciliation verdicts.
- state_required: last authoritative snapshot + reconciliation status.
- source_of_truth: **clearinghouseState ONLY (DECISION-002)**; webData2/webData3 forbidden as authority.
- consistency: authoritative; never overwritten by local bookkeeping (STR-0294).
- timing: polled/subscribed; reconciliation triggered per §4.7 P0 and cycle/closure steps.
- security: read-only account data; address (not agent) used.
- persistence: authoritative snapshots + reconciliation events persisted (reconstructability).
- failure_behavior: if authoritative state cannot be established → fail-closed (BLOCKED / RECONCILIATION_REQUIRED).
- recovery: re-read authoritative state; freeze on unresolved divergence.
- test_requirements: reconciliation tests; divergence/fail-closed tests.
- external_dependencies: Hyperliquid info clearinghouseState (SRC-107), WS (SRC-109).
- deterministic_implementation_sufficient: YES (compute is deterministic given authoritative reads).
- independent_execution_necessary: MAYBE (I/O polling cadence is a Phase-4/5 concern).
- notes: DECISION-002 binds this capability's source of truth.

### CAP-0003 — Execution Assurance & POSITION_VERIFIED
- purpose: Combine verified exchange fill AND authoritative position delta into POSITION_VERIFIED; drive the order/level state pipeline; never derive FILLED from ack/fill alone.
- strategy_requirements_covered: STR-0004, STR-0071, STR-0072, STR-0073, STR-0129, STR-0130, STR-0131, STR-0132, STR-0293, STR-0312, STR-0314, STR-0330(inv15).
- inputs: order fills (userFills/orderUpdates), authoritative delta (CAP-0002).
- outputs: POSITION_VERIFIED events; pipeline state (INTENT…POSITION_VERIFIED/CANCELLED/EMERGENCY/SKIPPED/ERROR).
- state_required: per-order/level pipeline state.
- source_of_truth: fill events (venue) ∧ CAP-0002 delta.
- consistency: LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED.
- timing: event-driven; verification may lag fills.
- security: n/a beyond venue reads.
- persistence: pipeline transitions persisted (reconstructable).
- failure_behavior: no state advances to FILLED/POSITION_VERIFIED without authoritative confirm; fail-closed otherwise.
- recovery: reconcile via CAP-0002; snapshot-tagged userFills on reconnect.
- test_requirements: partial-fill, duplicate-event, ack-without-delta, timeout tests.
- external_dependencies: venue fills + clearinghouseState.
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: cornerstone invariant of the whole system.

### CAP-0004 — Identity & Lifecycle Management
- purpose: Assign and persist canonical Generation/Cycle/Level identities; enforce ranges, immutability, non-recycle; derive display strings.
- strategy_requirements_covered: STR-0003, STR-0016..0024, STR-0103, STR-0306, STR-0313, STR-0316, STR-0317, STR-0318, STR-0319, STR-0331, STR-0332.
- inputs: lifecycle events (create Generation/Cycle/Level).
- outputs: LevelIdentity{GenerationID,CycleID,Direction,LevelID}; display strings (derived only).
- state_required: identity registry (immutable history).
- source_of_truth: internal identity registry.
- consistency: independent fields; never encoded together; never wrap/overwrite/recycle.
- timing: synchronous with lifecycle transitions.
- security: n/a.
- persistence: immutable historical identities (STR-0023, STR-0332).
- failure_behavior: reject ID=100 / wrap / recycle (fail-closed).
- recovery: reconstruct from persisted identities.
- test_requirements: boundary (0/99/100), immutability, display-format tests.
- external_dependencies: none.
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: —

### CAP-0005 — Deterministic Transition Orchestration & Precedence
- purpose: Evaluate all state transitions in deterministic passes with the total precedence order (P0–P6; §11.1 ordering); enforce locks; no event twice; carry-forward unexecuted.
- strategy_requirements_covered: STR-0063..0070, STR-0040(lock), STR-0203, STR-0205, STR-0335.
- inputs: verified state (CAP-0002/0003), candidate transitions from CAP-0006/0007/0008.
- outputs: ordered, executed transitions per pass.
- state_required: pass state; in-flight locks (Evolution single-in-flight per Basket).
- source_of_truth: deterministic domain state machine.
- consistency: total deterministic ordering; risk precedence over progression.
- timing: pass-based; arming only after all transitions complete (P6).
- security: n/a.
- persistence: transition log (reconstructable).
- failure_behavior: unexecuted → next pass; risk/exposure may block/divert everything below.
- recovery: deterministic re-evaluation from persisted state.
- test_requirements: precedence/conflict tests (P3 disable-vs-evolution; P4 ordering); replay.
- external_dependencies: none (pure domain).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: the deterministic core; must be AI-independent.

### CAP-0006 — Generation Lifecycle Management
- purpose: Manage Generation states (CREATED→ACTIVE→EVOLUTION_PENDING→SUCCESSOR_CREATED→DISABLED_AT_CYCLE_99→CLOSED_ONLY_AS_PART_OF_BASKET; FROZEN overlay), one-successor lock, Gen-99 handling, dominance fixation.
- strategy_requirements_covered: STR-0006, STR-0011, STR-0013, STR-0014, STR-0041..0062, STR-0101, STR-0119, STR-0120, STR-0121, STR-0122, STR-0123, STR-0126, STR-0127, STR-0321, STR-0322(part), STR-0323, STR-0324, STR-0325, STR-0326, STR-0333.
- inputs: verified evolution/terminal/limit events.
- outputs: Generation state transitions; successor creation; dominance flag.
- state_required: per-Generation state + successor lock + dominance.
- source_of_truth: deterministic domain state machine.
- consistency: ≤1 successor per Generation (permanent lock); disabled≠closed.
- timing: within precedence passes (CAP-0005).
- security: n/a.
- persistence: generation states + locks (immutable history).
- failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE (SUCCESSOR_LOCK_ACTIVE / GENERATION_ID_LIMIT / CYCLE_LIMIT_REACHED).
- recovery: reconstruct from persisted events.
- test_requirements: scenarios 11–19; one-successor, disable, gen-99 tests.
- external_dependencies: none.
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: —

### CAP-0007 — Evolution Evaluation (path-dependent return)
- purpose: Evaluate the ordered 7-condition evolution trigger (verified traversal, recorded origin, reversal, return level, POSITION_VERIFIED strategy-order return, guards, eligibility) with confirmation window + hysteresis; deferral-not-cancel; fail-closed on unverified return.
- strategy_requirements_covered: STR-0011, STR-0025..0040, STR-0055..0057, STR-0101, STR-0109..0115, STR-0118, STR-0304, STR-0322.
- inputs: POSITION_VERIFIED events, recorded traversal, return-level derivation, confirmation timer.
- outputs: EvolutionTriggered (new Generation) or INELIGIBLE_EVOLUTION_CANDIDATE + reason.
- state_required: recorded traversal, return-level latch, confirmation window, deferred-candidate carry-forward.
- source_of_truth: deterministic domain evaluation over POSITION_VERIFIED evidence.
- consistency: hedge orders ineligible; only verified return; single Evolution in flight per Basket.
- timing: EvolutionConfirmationSeconds=60 continuous; de-verification resets window.
- security: n/a.
- persistence: candidates + reasons persisted (never silently discarded).
- failure_behavior: fail-closed (RETURN_LEVEL_UNVERIFIED); deferred to later Cycle.
- recovery: re-candidate on future complete re-formation.
- test_requirements: scenarios 01–07,10,18; hysteresis/latch; ineligible-reason tests.
- external_dependencies: none (consumes CAP-0003 output).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: return level is dynamic/traversal-derived, never configured.

### CAP-0008 — Cycle Lifecycle & Reference-Price Capture
- purpose: Detect terminal events, execute standard cycle transition and cycle-99 disable in strict order; capture execution-grounded reference price gated by §5.4.1 tolerance; enforce ladder non-overlap.
- strategy_requirements_covered: STR-0008, STR-0012, STR-0071..0090, STR-0091..0100, STR-0102, STR-0104..0108, STR-0116, STR-0117, STR-0122, STR-0123, STR-0320.
- inputs: terminal POSITION_VERIFIED, reference derivation policy, StepBps.
- outputs: new Cycle; captured reference; fresh ladder request; or BLOCKED + RECONCILIATION_REQUIRED.
- state_required: cycle states, reference price (full precision), ladder geometry.
- source_of_truth: deterministic domain + execution-grounded fills.
- consistency: reference within 0.33×StepBps of nominal; non-overlap N1–N3; both must pass.
- timing: within precedence passes; reconcile before COMPLETED.
- security: n/a.
- persistence: cycle transitions + reference + deviation logs.
- failure_behavior: fail-closed BLOCKED (tolerance/non-overlap); no fallback reference.
- recovery: re-evaluate next pass after reconciliation (P0).
- test_requirements: reference-tolerance, non-overlap, terminal/disable transition tests.
- external_dependencies: none.
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: ReferencePriceToleranceBps is [DYN] (STR-0341) — resolved by CAP-0020.

### CAP-0009 — Grid Geometry Computation
- purpose: Compute level prices in bps→absolute→tick-rounded; first-level distances; successor-Generation asymmetry (dominant/weak, protection locking → fillability-gated unlock).
- strategy_requirements_covered: STR-0007, STR-0009, STR-0010, STR-0139..0152.
- inputs: reference price, StepBps, FirstLevelDistanceBps, Gen2DistanceMultiplier, WeakSideFirstLevelMultiplier, dominance.
- outputs: level price ladder (both groups); locked/ready/unlock flags.
- state_required: per-level geometry + lock/unlock state.
- source_of_truth: deterministic computation from parameters + reference.
- consistency: monotonic; composes from anchors; tick-round at build.
- timing: at ladder issuance (P6) subject to §8/§10 gates.
- security: n/a.
- persistence: geometry per cycle (reconstructable).
- failure_behavior: config error surfaced at validation if derivation can't satisfy §5.6.
- recovery: recompute deterministically.
- test_requirements: geometry unit tests; asymmetry; unlock-trigger tests.
- external_dependencies: szDecimals/tick (CAP-0001).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: —

### CAP-0010 — Position Sizing & Exposure-Cap Enforcement
- purpose: Convert USD notional-per-level to base-asset size (live mark, szDecimals); enforce hard notional caps (level/dominant/cycle/generation/basket) by rejection.
- strategy_requirements_covered: STR-0002, STR-0153..0162, STR-0227(MaxBasketNotional), STR-0285..0288, STR-0309.
- inputs: MaxBasketNotional, GridLevels, multipliers, live mark, active counts.
- outputs: order size; accept/reject vs caps.
- state_required: active generation/cycle counts; cap values.
- source_of_truth: deterministic computation; MaxBasketNotional computed once then binding (§14 global rule).
- consistency: hard caps, reject not clip; PASSIVE exposure counted.
- timing: at order build.
- security: n/a.
- persistence: cap config + computed values.
- failure_behavior: reject over-cap (fail-closed).
- recovery: recompute counts from persisted state.
- test_requirements: cap-breach, dominant-vs-level (D-12), divisor-count tests.
- external_dependencies: live mark (CAP-0001), CapitalBase (CAP-0002) for MaxBasketNotional inputs.
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: —

### CAP-0011 — Pending-Order Arm-Gate Evaluation
- purpose: Evaluate the full §8 arm-gate list (depth, distance band, min size, margin+buffer, exposure caps, open-order headroom, normalization, freeze/error/recovery, cost floor) plus ArmPolicy mode; DISABLED-generation arming rule.
- strategy_requirements_covered: STR-0152, STR-0163..0180 (excl. 0181), STR-0335.
- inputs: level candidate, market depth, margin, caps, ArmPolicy, NetExpectedEdge, generation state.
- outputs: arm / AWAITING_ARM / IDLE-PRECHECK (logged).
- state_required: per-level arm state; arm-request records.
- source_of_truth: deterministic gate evaluation.
- consistency: all gates mandatory; approval only restricts, never bypasses; EXPOSURE_CORRECTION exempt from gate-9/progression only.
- timing: PendingArmDistance pre-arm; ArmRequestTimeoutSeconds for SEMI/WEBHOOK.
- security: arm approvals carry identity; persisted.
- persistence: every arm request/approval/denial/expiry with identity+timestamp.
- failure_behavior: gate fail → IDLE/PRECHECK (not error); UNSET timeout → BLOCKED.
- recovery: re-evaluate on next pass.
- test_requirements: gate-by-gate, arm-policy AUTO/SEMI/WEBHOOK, timeout-never-auto-execute tests.
- external_dependencies: CAP-0001 (depth), CAP-0002 (margin), CAP-0012 (fillability), CAP-0013 (economics), CAP-0019 (approval).
- deterministic_implementation_sufficient: YES (given inputs; approval input handled by CAP-0019).
- independent_execution_necessary: NO.
- notes: —

### CAP-0012 — Fillability Analysis
- purpose: Walk live L2 book to estimate VWAP-execution-price slippage for an order size (snapshot estimate, defense-in-depth).
- strategy_requirements_covered: STR-0181, STR-0185(fillable), STR-0189(support).
- inputs: L2 book snapshot, order size/side.
- outputs: estimated slippage; fillable/unfillable verdict.
- state_required: none (pure over snapshot).
- source_of_truth: venue L2 book (CAP-0001).
- consistency: explicitly a snapshot estimate, not a guarantee.
- timing: at arming/emergency.
- security: n/a.
- persistence: estimates logged for audit.
- failure_behavior: unfillable → Skip fallback; backstopped by POSITION_VERIFIED.
- recovery: re-estimate on fresh snapshot.
- test_requirements: VWAP-walk tests; thin-book/Skip tests.
- external_dependencies: l2Book (≤20 levels/side).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: bounded by l2Book depth (STR-0228 nuance).

### CAP-0013 — Execution Economics Evaluation
- purpose: Compute NetExpectedEdge (gross − fee − slippage − funding − other), select maker/taker path, enforce NetExpectedEdgeFloor; four-way maker→taker re-eval.
- strategy_requirements_covered: STR-0179, STR-0188, STR-0189, STR-0193..0198, STR-0207, STR-0300, STR-0301, STR-0311.
- inputs: gross grid edge, live fee, slippage estimate, funding estimate, floor.
- outputs: NetExpectedEdge; path decision (maker/taker); WAIT/Ioc/REPRICE/SKIP.
- state_required: none (pure).
- source_of_truth: deterministic computation over live fees/costs.
- consistency: net governs; taker never solely from maker timeout.
- timing: at arming and at emergency/timeout re-eval.
- security: n/a.
- persistence: economics decisions logged.
- failure_behavior: ≤ floor → do not arm / Skip.
- recovery: recompute on fresh inputs.
- test_requirements: economic-path, floor, four-way-branch tests.
- external_dependencies: live userFees (CAP-0001), fillability (CAP-0012), funding (CAP-0001).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: —

### CAP-0014 — Order Intent Construction & Precision Normalization
- purpose: Build signed-order intents with correct precision (≤5 sig figs, ≤(6−szDecimals) decimals, size at szDecimals), assign cloid, set TIF, tag ENTRY_INTENT vs EXPOSURE_CORRECTION_INTENT; persist cloid before submission.
- strategy_requirements_covered: STR-0135, STR-0136, STR-0137, STR-0138, STR-0177, STR-0240, STR-0241, STR-0242, STR-0298, STR-0299.
- inputs: target price/size, szDecimals, intent classification, cloid generator.
- outputs: normalized, signed-ready order intent with cloid + intent tag.
- state_required: cloid registry (persisted before network submission).
- source_of_truth: deterministic normalization; precision rules from venue.
- consistency: normalize before signing; cloid persisted first; intent classified by projected ExposureDelta.
- timing: pre-submission.
- security: signing material handled outside artifacts; never logged.
- persistence: cloid + intent persisted before submit.
- failure_behavior: fail-closed on invalid precision (do not rely on exchange rejection).
- recovery: cloid enables idempotent identity/lookup (dedup-on-resubmit NOT venue-documented — observe later).
- test_requirements: precision, cloid-persist-before-submit, intent-classification tests.
- external_dependencies: venue precision rules (SRC-108), signing (SRC-119).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: signing itself is a security boundary (Owner-gated wallet authority; not this phase).

### CAP-0015 — Order Execution & Lifecycle Tracking
- purpose: Submit/cancel/modify orders; track lifecycle via orderUpdates/orderStatus; bounded emergency execution (Ioc within tolerance) and Level Skip; never unbounded market order.
- strategy_requirements_covered: STR-0075, STR-0085, STR-0129, STR-0130, STR-0133(exec), STR-0182..0187, STR-0190, STR-0191, STR-0192, STR-0214, STR-0254(TWAP close legs), STR-0297.
- inputs: order intents (CAP-0014), venue exchange endpoint, tolerance band.
- outputs: order acks (resting/filled/error), cancellations, EMERGENCY/SKIPPED outcomes.
- state_required: open-order registry; emergency timers.
- source_of_truth: venue acks + CAP-0003 verification.
- consistency: never chase beyond EmergencyTolerance; never accept uneconomic fill.
- timing: EmergencyBoundedWaitSeconds=30; TWAP suborders ≥30s.
- security: signed submissions (wallet authority Owner-gated).
- persistence: submissions/acks/cancels persisted.
- failure_behavior: bounded Ioc or LEVEL_SKIPPED; fail-closed on ambiguity.
- recovery: reconcile via CAP-0002/0003; idempotency via cloid/nonce.
- test_requirements: emergency-band, skip, partial-fill, timeout, duplicate-submission tests.
- external_dependencies: exchange endpoint (SRC-104), order-types (SRC-112), nonces (SRC-110).
- deterministic_implementation_sufficient: YES (decision logic; venue latency is external).
- independent_execution_necessary: MAYBE (execution I/O loop; boundary decision Phase 4/5).
- notes: retry only after establishing whether the effect already happened (idempotency).

### CAP-0016 — Exposure Computation & Hedge/Mirroring Evaluation
- purpose: Compute ExpectedExposure/ActualExposure/ExposureDelta; classify; drive Hedge Recovery (acute unconditional Ioc; else cost-aware); evaluate Mirroring intents (Basket-scoped, verified-fill-driven) through normal gates.
- strategy_requirements_covered: STR-0001, STR-0199, STR-0201, STR-0202, STR-0204, STR-0206, STR-0207, STR-0208..0214, STR-0223(MaxExposureImbalance), STR-0231, STR-0295, STR-0296, STR-0302, STR-0308, STR-0329.
- inputs: verified filled quantities, ActualExposure (CAP-0002), MaxExposureImbalance, mark price.
- outputs: ExposureDelta; hedge/mirror intents (EXPOSURE_CORRECTION_INTENT).
- state_required: exposure model; mirror targets.
- source_of_truth: ExpectedExposure (verified fills) vs ActualExposure (clearinghouseState).
- consistency: Expected never treated as Actual; progression hard-gated on tolerance.
- timing: continuous; acute branch immediate.
- security: n/a.
- persistence: exposure/hedge decisions persisted.
- failure_behavior: acute → unconditional Ioc hedge; else cost-aware; corrections allowed under FREEZE.
- recovery: hedge recovery permitted even under FREEZE / for DISABLED generations.
- test_requirements: exposure-delta classification, acute-hedge, mirroring-through-gates, partial-fill tests.
- external_dependencies: CAP-0002, CAP-0001 (mark), CAP-0011/0013/0014 (gated correction orders).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: MaxExposureImbalance is [DYN] (STR-0340) via CAP-0020.

### CAP-0017 — Risk-Bound Evaluation & Three-Layer Breach Response
- purpose: Continuously monitor Basket-scoped risk bounds (DD, execution cost, failed-level rate, hedge cost, exposure imbalance) and apply the three-layer response (Alert → Soft Protective Action → Operator Decision); risk precedence over profit target; margin/liquidation-distance awareness.
- strategy_requirements_covered: STR-0215..0223, STR-0225..0230, STR-0232, STR-0233, STR-0307, STR-0309, STR-0337(margin awareness).
- inputs: BasketNetPnL, exposure, costs, bounds, mark price, maintenance-margin fraction.
- outputs: breach alerts; soft protective actions; escalation signals.
- state_required: cumulative cost/DD trackers; bound values.
- source_of_truth: deterministic evaluation over authoritative PnL/exposure/margin.
- consistency: never auto-terminate on Group-B breach; risk precedence over closure.
- timing: continuous.
- security: n/a.
- persistence: breach alerts persisted with identity/timestamp.
- failure_behavior: soft protective action (hedge/cancel/arming-suspend); operator decision for escalation.
- recovery: resume when within bounds.
- test_requirements: bound-breach, three-layer, risk-precedence tests.
- external_dependencies: CAP-0001 (mark/margin), CAP-0002 (equity), CAP-0016 (exposure).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: max leverage read live (DECISION-001); Leverage_effective=3.

### CAP-0018 — Basket Lifecycle & Closure Verification
- purpose: Manage Basket states (INITIALIZING…CLOSED/ERROR/RECOVERY), NET-PnL accounting, FREEZE semantics, and the verified closure sequence (both net-profit and residual-exposure preconditions).
- strategy_requirements_covered: STR-0005, STR-0234..0256, STR-0303, STR-0310, STR-0328.
- inputs: BasketNetPnL, closure target, residual exposure, close mode.
- outputs: Basket state transitions; CLOSED only after all conditions pass.
- state_required: Basket state; PnL accumulators; closure progress.
- source_of_truth: NET PnL (§13.1) + authoritative residual exposure (CAP-0002).
- consistency: CLOSED requires both preconditions; gross never substitutes; indefinite management if unmet.
- timing: closure is a verified state machine, not "order submitted".
- security: n/a.
- persistence: basket lifecycle + closure verification persisted.
- failure_behavior: fail-closed; not CLOSED until verified.
- recovery: reconcile; hedge recovery permitted during indefinite management.
- test_requirements: closure-precondition, residual-tolerance, indefinite-management, TWAP-close tests.
- external_dependencies: CAP-0002, CAP-0015 (close legs), CAP-0012 (fillability).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: BasketNetProfitClosureTarget & ResidualExposureToleranceAtClosure derived (CAP-0020).

### CAP-0019 — Operator Control Surface / Arm Approval
- purpose: Provide the human/service approval channel for SEMI/WEBHOOK arm policy; capture operator/service identity; enforce timeout→fail-closed (never auto-approve).
- strategy_requirements_covered: STR-0165, STR-0166, STR-0167, STR-0170, STR-0171, STR-0172.
- inputs: arm requests (from CAP-0011); operator/service approvals.
- outputs: approve/deny/expire decisions with identity.
- state_required: pending arm requests + outcomes.
- source_of_truth: operator/external service (input), gating logic deterministic.
- consistency: approval only restricts; timeout never auto-executes; failure never auto-approves.
- timing: ArmRequestTimeoutSeconds=30.
- security: identity recorded per request; approvals authenticated.
- persistence: request/approval/denial/expiry persisted with identity+timestamp.
- failure_behavior: timeout/error → IDLE/PRECHECK (fail-closed).
- recovery: re-request on next pass.
- test_requirements: SEMI/WEBHOOK approval, timeout, identity-recording tests.
- external_dependencies: operator UI / external webhook service (Live default SEMI).
- deterministic_implementation_sufficient: PARTIAL — the gating/timeout logic is deterministic, but the approval decision is an external human/service input (non-deterministic by nature; treated as a gated input, never bypassing §8/§10).
- independent_execution_necessary: MAYBE (external approval channel; boundary decision Phase 4/5).
- notes: Live activation and wallet authority remain separate Owner boundaries.

### CAP-0020 — Configuration & Calibration Parameter Resolution
- purpose: Resolve all §14 parameters and §16 dynamic defaults deterministically (formulas over defined params; computed once → binding per §14 global rule); fail-closed on any missing required value; never invent values.
- strategy_requirements_covered: STR-0024(limits), STR-0036(EvoConfSec), STR-0083, STR-0091(policy), STR-0096, STR-0100, STR-0140..0143, STR-0148..0150, STR-0155..0161, STR-0227, STR-0245, STR-0248, STR-0257..0292, STR-0336, STR-0338, STR-0339, STR-0340, STR-0341, STR-0342, STR-0343.
- inputs: §14 confirmed values; §16 dynamic-default formulas; live inputs (StepBps, MaxBasketNotional, Leverage_effective, MarkPrice, GridLevels).
- outputs: resolved parameter values; dynamic-default values (tagged, logged).
- state_required: confirmed parameter set; calibration status.
- source_of_truth: §14 (owner-confirmed) + §16 formulas; Strategy.md is authority.
- consistency: formula used once then binding; dynamic defaults must remain dynamic (never frozen); mutual ordering (§16 consistency note) must hold or be reported.
- timing: at init / on owner change; dynamic defaults evaluated as used (logged).
- security: n/a.
- persistence: parameter set + calibration provenance persisted; dynamic reads distinguishable in audit.
- failure_behavior: UNSET required value → fail-closed (BLOCKED); no invented default.
- recovery: re-resolve from confirmed config.
- test_requirements: formula-once, dynamic-default, mutual-ordering, fail-closed-on-missing tests.
- external_dependencies: live inputs (CAP-0001/0002) for dynamic formulas.
- deterministic_implementation_sufficient: YES (runtime resolution is deterministic; offline *calibration research* is NON_RUNTIME — see CAP-0024).
- independent_execution_necessary: NO.
- notes: DECISION-001 (max leverage read live) applies here.

### CAP-0021 — Persistence & Event Reconstruction
- purpose: Persist all authoritative state, events, decisions, and identities such that every transition is reconstructable from persisted state + authoritative exchange observations.
- strategy_requirements_covered: STR-0023, STR-0171, STR-0315, STR-0334, plus persistence needs referenced across CAP-0002..0020.
- inputs: domain events, authoritative observations, decisions, arm workflow.
- outputs: durable event log / state store enabling reconstruction.
- state_required: the durable store itself.
- source_of_truth: append-only event history (immutable for historical objects).
- consistency: reconstructability; no transition depends solely on intended orders.
- timing: synchronous with state changes (persist before side effects where required, e.g., cloid).
- security: no secrets persisted.
- persistence: this IS the persistence capability.
- failure_behavior: if persistence unavailable → fail-closed for side-effecting actions.
- recovery: full state reconstruction from persisted history.
- test_requirements: replay/reconstruction, crash-recovery tests.
- external_dependencies: none (technology TBD Phase 4/5).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: MAYBE (durable store may be a separate resource; boundary decision Phase 4/5).
- notes: persistence *technology* is explicitly NOT chosen here.

### CAP-0022 — Observability & Audit Trail
- purpose: Emit and retain audit-grade logs: dynamic-default reads (tagged, distinguishable from calibrated runs), breach alerts, deviation magnitudes, ineligible-candidate reasons, arm workflow.
- strategy_requirements_covered: STR-0035(reason logging), STR-0054, STR-0097(deviation log), STR-0184, STR-0216, STR-0336, STR-0342.
- inputs: runtime events, dynamic-default usage, alerts.
- outputs: audit trail / structured logs.
- state_required: log store (may overlap CAP-0021).
- source_of_truth: runtime emissions.
- consistency: a run using dynamic defaults is distinguishable in the audit trail.
- timing: continuous.
- security: no secrets in logs.
- persistence: audit logs retained.
- failure_behavior: logging failure should not silently drop safety-relevant events.
- recovery: n/a.
- test_requirements: audit-completeness, dynamic-default-tagging tests.
- external_dependencies: none.
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: —

### CAP-0023 — Fail-Closed Safety Enforcement (cross-cutting)
- purpose: Enforce fail-closed behavior wherever the Strategy requires it (ambiguous state/config/environment/identity, inconsistent state, unestablished authoritative position, missing evidence, failed reconciliation, violated invariant, unresolved calibration/owner decision) via BLOCKED / RECONCILIATION_REQUIRED / INELIGIBLE / SKIPPED.
- strategy_requirements_covered: STR-0035, STR-0077, STR-0087, STR-0090, STR-0098, STR-0108, STR-0172, STR-0343, plus every MUST_NOT/guard invariant (e.g., STR-0021, STR-0022, STR-0033, STR-0057, STR-0058, STR-0073, STR-0081, STR-0192, STR-0213, STR-0250, STR-0330, STR-0335) as their fail-closed enforcement.
- inputs: guard/gate outcomes from all capabilities.
- outputs: fail-closed state (block/skip/ineligible/reconcile) + reason.
- state_required: safety/error/recovery state overlay.
- source_of_truth: deterministic guard evaluation.
- consistency: never guess; never silently continue; a slower verified transition beats a fast unverified one.
- timing: cross-cutting, every pass.
- security: n/a.
- persistence: fail-closed events persisted with reasons.
- failure_behavior: this IS the fail-closed capability.
- recovery: freeze/recovery per §13.3; resume only when safe.
- test_requirements: failure-injection, freeze/recovery, fail-closed-path tests.
- external_dependencies: none.
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: cross-cutting concern; not a subsystem.

### CAP-0024 — Reference Model & Differential Testing (RESEARCH-ONLY / NON_RUNTIME)
- purpose: A pure/deterministic reference model of core strategy semantics for differential testing against production domain logic; consumes canonical scenarios (§5.7). **Not part of the trading runtime.**
- strategy_requirements_covered: STR-0109..0128 (as differential-test scenarios; also covered at runtime by CAP-0006/0007/0008), plus verification of all deterministic capabilities.
- inputs: canonical scenario sequences; STR contract.
- outputs: expected states/transitions/decisions for differential comparison.
- state_required: model state (offline).
- source_of_truth: Strategy.md + STRATEGY_CONTRACT.md (never production code).
- consistency: expected results derived from Strategy, not implementation.
- timing: offline.
- security: no network/secrets.
- persistence: test fixtures.
- failure_behavior: divergence = defect or blocking ambiguity.
- recovery: n/a.
- test_requirements: differential harness itself.
- external_dependencies: none (no network, no AI at runtime).
- deterministic_implementation_sufficient: YES.
- independent_execution_necessary: NO.
- notes: **NON_RUNTIME** — research/verification only; must not become a runtime dependency.
