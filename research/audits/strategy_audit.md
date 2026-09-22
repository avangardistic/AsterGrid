# strategy_audit.md — Formal Logical Autopsy of Strategy.md v2.3-final

- **Subject:** `Strategy.md` (SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`, 1,368 lines, v2.3-final) — *unmodified by this audit.*
- **Axiom sources:** Official Hyperliquid documentation as cached in `research/sources/hyperliquid/page-*.md` (hash-verified against `SOURCE_MANIFEST.md`) **plus live re-fetch of 6 pages on 2026-09-21** (perpetuals, liquidations, funding, robust-price-indices, tick-and-lot-size, websocket/subscriptions) — live text matched the cached axioms verbatim on every checked claim.
- **Method:** Axiom extraction (AA-1..AA-14) → statement-wise interrogation (Sᵢ mapped, stress-tested, async-tested) → adversarial scenario simulation → formal synthesis. Verdicts use the requested taxonomy: **F** (fatal flaw), **U** (undefined behavior), **O** (optimization gap), **Pass**.
- **Cross-reference:** `STR-xxxx` ids cite the derived contract (`research/strategy/STRATEGY_CONTRACT.md`) for traceability; the audit is independent of that contract's conclusions.

---

## 1. Executive Summary

### Verdict: **VALID — conditionally.** Confidence: **82 / 100.**

**The core claim of this audit:** `Strategy.md` contains **no fatal contradiction with the Hyperliquid liquidation, margining, funding, or execution engines** in its *approved* (owner-decided) core. The verification-first architecture (POSITION_VERIFIED, fail-closed, §4.7 total order) is **provably async-safe**: no rule assumes synchronous execution, and every state claim is anchored on a post-hoc authoritative read (AA-10), which neutralizes the venue's undocumented latency and ordering behavior by construction.

**However, the strategy is not provably *solvent as written*.** The audit exposes:

| Class | Count | Headline finding |
|---|---|---|
| **F (fatal-as-written)** | **1** | **F-1\*** — The D-16 `ExposureTolerance` default ($5 notional-equivalent) is provably **below the venue's $10 minimum order value for ∀ MarkPrice > 0**, creating a reachable dead-band `δ ∈ (τ_E, q_min)` that simultaneously **blocks grid progression** (§5.2) and is **un-correctable by any order** (venue rejects < $10). A provable livelock cell in state space. Conditional because D-16 is `[DYNAMIC — CALIBRATION PENDING]` — adopt it unmodified and the flaw is fatal. |
| **U (undefined behavior)** | **8** | `GrossGridEdge` — the variable that governs the binding economics gate — **has no closed-form definition** (single symbolic occurrence, L812). No cumulative funding-bleed bound exists. §5.6's computable non-overlap test *under-approximates* the stated invariant. Correction-order gating is contradictory between §10 and §11.2. cloid idempotency is asserted beyond what the venue documents. Closure-tolerance rounding direction undefined. Margin mode (cross/isolated) never pinned. No rate-limit budget. |
| **O (optimization gaps)** | **5** | The maintenance-margin model mis-attributes `0.5/L_eff` as "the" maintenance fraction (safe-direction error, proven). `MaxRangeInducedDD = 100%` is vacuous as protection. Closure target inflates the per-cycle edge 6×. Etc. |

**Solvency (informal, proven in §6):** under pinned cross/one-way margin and hedge-layer liveness, net notional `N ≤ 1.5·E₀` and the actual venue liquidation distance is `d_liq = E₀/N − m ≥ 65.3%` (BTC/ETH, `m = 0.5/maxLev ∈ {1.0%, 1.25%}`), versus the strategy's modeled `50%` — **the model errs conservative by ≥ 15 points**. With the hedge layer intact, net exposure is bounded by `MaxExposureImbalance` ($208 notional at defaults), making liquidation require a joint failure (hedge halt ∧ ≥ 65% adverse excursion). **Liquidation risk is therefore a liveness problem, not a margin-arithmetic problem.** The 8 U-class gaps are precisely threats to that liveness premise.

Confidence is 82, not higher, because (i) F-1/U-class items must be closed before the liveness premise is implementable, (ii) 4 of the axioms the strategy depends on are *absences* in the venue documentation (cloid dedup, matching priority, latency bounds, block finality), and absences cannot be proven against, only contained — which the strategy does, but containment is implementation-dependent (Phase 7, unproven).

---

## 2. The Axiomatic Basis (Hyperliquid Reality)

Extracted verbatim from the hash-verified primary sources; each is used later as a proof obligation.

| ID | Axiom | Formal content | Source |
|----|-------|----------------|--------|
| **AA-1** | Liquidation price (cross) | `liq_price = price − side · margin_available / position_size / (1 − l·side)`, `l = 1/MAINTENANCE_LEVERAGE`; `margin_available(cross) = account_value − maintenance_margin_required`. Backstop liquidation at account equity `< ⅔` maintenance ⇒ trader can end at **zero equity**. | liquidations.md (live-verified) |
| **AA-2** | Maintenance margin | `Maintenance fraction = ½ × maximum initial margin fraction = 0.5/maxLeverage`, i.e. a function of the **asset's max leverage and margin tier — not the user's set leverage** ("max leverage … varies from 3-40x"; 1.25% at 40x). Docs' `meta` *example* shows BTC/ETH `maxLeverage: 50` (internally inconsistent with prose; persists live today). | contract-specifications, margining, liquidations (live-verified) |
| **AA-3** | Initial margin | `Initial margin = position_size × mark_price / leverage_user`; `initial fraction = 1/leverage_user`. Cross unrealized PnL counts as margin. | margining.md |
| **AA-4** | Funding | Paid **hourly** at ⅛ of the 8h rate; `F = P + clamp(0.01% − P, ±0.05%)`; premium sampled 5s; **capped at 4%/hour**; payment `= position_size × oracle_price × rate` (**oracle spot**, not mark, converts to notional). | funding.md (live-verified) |
| **AA-5** | Fees | Perps Tier-0: **taker 0.045% (4.5 bps), maker 0.015% (1.5 bps)**; tiered by rolling 14d volume/staking; live per-user via `userFees`. | fees.md |
| **AA-6** | Order value bounds | **Minimum order value $10** (venue error: *"Order must have minimum value of $10"*); max market order value $30M at maxLev ≥ 25 (limit ×10). | exchange-endpoint.md, contract-specifications.md |
| **AA-7** | Precision | Price: ≤ 5 significant figures ∧ ≤ (6 − szDecimals) decimals; **integer prices always valid**; size at szDecimals; trailing zeros removed at signing. | tick-and-lot-size.md (live-verified) |
| **AA-8** | Rate limits | REST 1200 weight/min per IP (`l2Book/allMids/clearinghouseState/orderStatus` weight 2; most info weight 20); address budget 1 req/USDC traded; WS: 10 conns / 1000 subs / 2000 msgs/min / 100 inflight posts; **open-order cap 1000 (→5000 by volume); at ≥ 1000 open, reduce-only/trigger orders are rejected**. | rate-limits.md |
| **AA-9** | Price indices | Oracle = weighted CEX median, ~3s cadence; **mark = median(oracle+EMA-Δmid, book BBA+last, CEX mids 3:2:2:1:1)**; mark/oracle update ~3s; mark is used for **margining, liquidation, and TP/SL triggering**; funding notional uses oracle. | robust-price-indices.md (live-verified) |
| **AA-10** | Account truth | `clearinghouseState`: one **net** position per coin (`assetPositions[].position.szi`, `type: "oneWay"`), `marginSummary.accountValue` (equity incl. unrealized PnL), `withdrawable`, per-position `liquidationPx`, `leverage.type ∈ {cross, isolated}`, `cumFunding`. **No venue-side long/short pairing exists** — "hedge" orders net into one position. | perpetuals-info.md |
| **AA-11** | Execution & TIF | REST ack `resting/filled/error`; **ALO = "canceled instead of immediately matching"** (reject-on-cross); IOC cancels remainder; `orderStatus`, WS `orderUpdates`/`userFills` (snapshot-tagged); fills ≤ 10k retained; `cloid` = optional 128-bit identity for lookup/cancelByCloid; replay protection = per-address **nonce set** (100 slots, window T−2d…T+1d); **duplicate-cloid dedup is NOT documented**. | exchange-endpoint, nonces, signing |
| **AA-12** | Trigger orders | Stop/take triggered on **mark price** (median-of-medians, manipulation-hardened); "last trade" is only ⅓ of one median input. | order-types, robust-price-indices |
| **AA-13** | Native TWAP | Suborders ≥ 30s; **≤ 3% slippage per suborder**; catch-up ≤ 3× normal slice; $100 min; 5min–7d runtime. | order-types.md |
| **AA-14** | Finality/latency | **Not axiomatized.** The docs specify *no* latency bounds, *no* matching-priority algorithm, *no* block-time guarantees. Any strategy assumption on these is unverifiable ⇒ must be designed latency-agnostic. | (absence) |

**Derived venue constants used throughout (defaults: `E₀ = $20,000`, `L_user = 3`, `StepBps = 10`, `GridLevels = 6`, `MaxBasketNotional = $30,000`, `NotionalPerLevel = $5,000`, BTC `szDecimals = 5`):**

```
q_min      := $10 / MarkPrice                       (minimum tradable quantity, AA-6)
m_model    := 0.5 / L_eff = 16.67%                  (strategy's maintenance fraction, §16)
m_actual   := 0.5 / maxLevTier  ∈ {1.0%, 1.25%}     (BTC @ 50x / 40x, AA-2)
d_liq(N)   := E₀/N − m                              (adverse fractional move to liquidation, AA-1/AA-3)
N_max      := 1.5 · E₀ = $30,000                    (binding cap term, §12.1)
d_liq(N_max) = 0.6667 − m = {50.0% modeled, 65.7% actual @50x, 65.4% @40x}
```

---

## 3. Line-by-Line Critical Analysis

Legend: **Async** = robust against asynchronous venue execution. **Vol** = robust under ≥ 5σ moves / funding spikes / liquidity gaps. Verdicts: ✅ Pass · ⚠️ Conditional · ❌ Fail.

### §2–§3 — Model & Identity (L95–L184)

| Sᵢ | Claim (Strategy.md) | Axiom map | Test | Verdict |
|----|---------------------|-----------|------|---------|
| S-2.1 | "Exactly one active Basket per market" (L98) | AA-10 (one net position/coin) | Consistent: one Basket ↔ one net book. No venue conflict. | ✅ |
| S-2.2 | Basket → Generation → Cycle → Level; generations never close individually (L102) | — (internal) | Closed finite state space: `|G| ≤ 100, |C| ≤ 100/G`; all terminal. No Zeno condition (each transition consumes an ID or a verified fill). | ✅ |
| S-3.1 | IDs independent, never encoded; reject 100; no wrap/recycle (L155–L184) | — | Exhaustive-range sound: `∀n ∈ [0,99]` representable; rejection at boundary is total. Immutability ⇒ replay-safe. | ✅ |
| S-3.2 | Display string derived-only, never parsed (L176) | — | Eliminates an entire class of injection/round-trip defects. | ✅ |

### §4 — Generation Lifecycle (L185–L338)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-4.1 | Evolution = 7-condition verified return; each of {terminal reach, crossing, ack, isolated fill, unverified WS} individually insufficient (L187–L231) | AA-11, AA-12 | Negation set is complete against venue evidence types: every venue emit (ack, fill msg, price) is enumerated and disqualifed. ∀ venue evidence `e` alone: `e ⊬ Evolution`. | ✅ |
| S-4.2 | Return level = dynamic, traversal-derived (D-01); deferred-not-cancelled (L207) | — | Well-defined: return level exists ⇔ ∃ verified traversal. Deferred candidate bounded by Generation lifetime (≤ 99 Cycles) — no unbounded queue. | ✅ |
| S-4.3 | Confirmation 60s continuous + latch hysteresis (§4.2) | AA-9 (3s mark cadence) | 60s ≫ 20 mark updates ⇒ immune to index flicker; latch kills boundary flip-flop. `EvolutionConfirmationTolerance` band (L238 "extended") is under-specified in v2.3 prose — see U-4's sibling; repo AMB-0006/DECISION-009 resolves nominal reference. | ⚠️ (resolved at decision layer) |
| S-4.4 | One-successor lock; SUCCESSOR_CREATED may continue Cycles (§4.4) | — | Linear growth: `#Generations ≤ 100` — the "PASSIVE exposure explosion" failure mode of grid lineages is structurally excluded (proven by induction on the lock). | ✅ |
| S-4.5 | Dominance = origin/traversed group, fixed at Evolution (§4.5, D-05) | — | Deterministic function of recorded events; no recompute race. | ✅ |
| S-4.6 | G99 semantics; no wrap; GENERATION_ID_LIMIT reason code (§4.6) | — | Boundary total: G99 ∌ successor. | ✅ |
| S-4.7 | P0–P6 total order; no event twice; carry-forward (§4.7) | — | **Acyclicity proven:** P0 (verify) → P1 (risk) → P2 (locks) → P3 (same-gen conflict: DISABLE ≻ Evolution) → P4 (Evolution ≻ Cycle; lower GenID first) → P5 (Cycle) → P6 (arm). Strict lexicographic order ⇒ no circular wait; single-in-flight Evolution (P2) precludes re-entrancy. The one same-pass conflict (disable vs evolve) has a unique winner. | ✅ |

### §5 — Cycle Lifecycle (L339–L555)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-5.1 | TerminalEvent = terminal level POSITION_VERIFIED; fill ∧ delta (§5.1) | AA-10, AA-11 | Double-anchor on venue truth; async-safe (see §4, scenario 3). | ✅ |
| S-5.2 | Transition order: cancel pending → reconcile → non-overlap → COMPLETED → new Cycle → capture ref → fresh ladder (§5.2) | AA-11 | Step 3 (reconcile) after step 2 (cancel) means the non-overlap test runs on post-cancel venue state ⇒ in-flight cancels can only cause BLOCK + re-eval (fail-closed), never corruption. | ✅ |
| S-5.3 | **Progression gate:** `|ExposureDelta| ≤ ExposureTolerance`, τ_E = (0.001×StepBps/10)×NotionalPerLevel/MarkPrice (§5.2, §16) | **AA-6** | ❌ **F-1\***: at defaults, τ_E ≡ $5 of notional (price-invariant), while `q_min = $10/MarkPrice`. **∀p > 0: τ_E < q_min.** ∴ ∃ reachable δ with τ_E < δ < q_min: progression is blocked (`δ > τ_E`) yet every corrective order is venue-rejected (`δ < q_min`). Dead-band is reachable via partial-fill sequencing (fills quantized at $1 notional for BTC@100k). **Livelock cell proven.** Conditional: D-16 is calibration-pending (repo: AMB-0014); the strategy text itself provides no round-to-zero/min-size escape. | ❌ F-1\* |
| S-5.4 | Reference capture execution-grounded; 4 policies; tolerance 0.33×StepBps vs nominal (§5.4–5.4.1, D-17) | AA-9, AA-12 | `0.33 < 1` ⇒ captured ref cannot drift a full step ⇒ composes with §5.6 by construction: `drift < 0.33·Step ⇒ level-1 monotonicity preserved`. Fail-closed on breach, no fallback ⇒ no drift accumulation. | ✅ |
| S-5.5 | Non-overlap N1–N3: monotonic; level-1 beyond old [ref, terminal-exec]; **no new price may equal** a live same-group price (§5.6) | — | ⚠️ **U-3**: N3 forbids only *exact equality*. The **opposite-group** legacy ladder survives the transition (step 2 cancels the exhausted traversal only) and may near-stack against the new ladder (`0 < |p_new − p_live| ≤ 1 tick` is legal). Stated invariant ("no unintended overlap") > computable test ⇒ spec–mechanization gap. Blast radius bounded by caps (two levels ≈ $10–12.5k) but double-fill concentration is real. | ⚠️ U-3 |
| S-5.6 | Scenarios 01–20 (§5.7) | — | All 20 trace-checked against §§4–5 rules: no contradiction found; each borderline case has a unique outcome. | ✅ |

### §6 — Execution Assurance (L556–L580)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-6.1 | Pipeline INTENT→…→FILLED→POSITION_VERIFIED; **`FILLED ⇔ fill ∧ delta`**; never from ack/fills alone (§6.1) | AA-10, AA-11, AA-14 | The load-bearing invariant, and the correct answer to AA-14's absence of latency guarantees: every claim is established *post hoc* from `clearinghouseState`. ∀ async reorderings of venue messages, the invariant cannot produce a false FILLED (delta is a read, not an inference). | ✅ |
| S-6.2 | "cloid (128-bit client order ID, **idempotent order identity**)" (L573) | **AA-11** | ⚠️ **U-5**: venue documents cloid as *identity/lookup/cancel* only; replay protection is the **nonce set**; duplicate-cloid dedup is **not documented**. "Idempotent" overclaims. A retry-after-timeout may execute twice; POSITION_VERIFIED then detects the delta mismatch and fail-closes — containment, not prevention. Financial duplication window = one reconciliation cycle. | ⚠️ U-5 |
| S-6.3 | Precision normalization pre-sign, never reject-and-retry (§6.3) | AA-7, AA-11 | Exactly matches venue rules incl. trailing-zero signing; eliminates the documented top SDK bug class. | ✅ |

### §7 — Grid Geometry (L582–L698)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-7.1 | bps distances; Level-1 at 2×Step (20bps), spacing 10bps; ladder = [20,30,40,50,60,70]bps (§7.1) | AA-7 | Monotone; max span 70bps ≪ d_liq (50–65%) ⇒ geometry cannot self-liquidate. | ✅ |
| S-7.2 | Successor asymmetry: dominant Level-1 at 2×Step, volume ×1.5; weak Level-1 LOCKED until weak Level-2 fills (§7.1, D-09C/D-12) | — | Directional bias is deliberate; caps (`MaxLevelNotionalDominant = $7,500`) resolve the size conflict explicitly. Weak-side lock is fail-closed (no order ⇒ no exposure). | ✅ |
| S-7.3 | Sizing: USD-notional → base at live mark, szDecimals-rounded; caps level/dominant/cycle/generation/basket with D-14 divisors (§7.3) | AA-7, AA-10 | Rounding residue ≤ ½ ulp = $0.50 (BTC@100k, szDec 5) — bounded, and τ_E was designed to absorb it (see F-1 for the boundary failure). Cap lattice is consistent: `MaxLevel ×6 = MaxBasket` when single cycle/gen; divisors shrink per-cycle/gen caps as count grows ⇒ `Σ caps ≤ MaxBasket` always. | ✅ |

### §8 — Pending Order & Fillability (L700–L763)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-8.1 | Pre-arm within 50bps; gates 1–10 incl. depth ≥ 10× size, DistanceBand [5,100]bps, size ≥ asset min, margin ≥ 1.2× required, caps, open-order headroom, precision, no FREEZE, NetExpectedEdge > floor (§8) | AA-6, AA-7, AA-8, AA-3 | Gate 3 is exactly AA-6. Gate 6 matches AA-8's ≥1000-open reject quirk incl. hedge-headroom rationale. Margin gate: `1.2 × (N_max/3) = 0.6·E₀ < E₀` ∀E₀ ⇒ **no margin deadlock at max size** (closed-form). | ✅ |
| S-8.2 | ArmPolicy AUTO/SEMI/WEBHOOK; timeout → cancel, **never auto-execute**; approval only restricts (§8, D-10) | — | Approval is a pure restriction lattice: `armable_SEMI ⊆ armable_AUTO` ⇒ no bypass path. | ✅ |
| S-8.3 | **Invariant 1: the arm gate NEVER applies to EXPOSURE_CORRECTION_INTENT**; disabled-gen corrections "pass every other gate"; §10: "NetExpectedEdge ≤ floor (**either path**) → do not attempt"; §11.2 acute: hedge Ioc "**regardless of cost — unconditional**" | — | ⚠️ **U-4**: The correction path's gate set is *contradictory as written*: §8-inv.1 exempts corrections from arm-approval, the disabled-gen clause makes them pass "every other gate", §10's "either path" floors them economically, §11.2's acute branch exempts them economically. Resolvable only by an implicit precedence (acute ⇒ skip economics; else apply). The strategy never states that precedence. Two compliant implementations diverge observably. | ⚠️ U-4 |
| S-8.4 | Fillability Analyzer = L2 VWAP snapshot estimate + defense-in-depth (Ioc pricing, POSITION_VERIFIED, Skip) (§8) | AA-9, AA-14 | Correctly scoped as *estimate*: the four layers catch estimation error post hoc. No guarantee is claimed ⇒ nothing to contradict AA-14. | ✅ |

### §9 — Emergency Execution & Skip (L765–L806)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-9.1 | Emergency Ioc at tolerance-band edge (`±17bps` @3x); require fillable ∧ in-band ∧ edge-clearing; **else SKIP**; never unbounded market order (§9.1) | AA-11, AA-6 | Band-bounded taker: worst cost/fill = 17 (slippage band) + 4.5 (fee) = **21.5 bps** = $1.61 per $7,500 dominant level. Replacement for unbounded market orders — the correct response to a venue with no market-order protection. Emergency band vs AA-6: on BTC, band edge order ≥ min size for all configured level sizes ($5,000 ≫ $10). | ✅ |
| S-9.2 | Four-way re-eval (WAIT/Ioc/REPRICE/SKIP); taker never solely because maker timed out (§9.2) | AA-11 (ALO semantics) | Eliminates adverse-selection-by-timer; consistent with ALO reject-on-cross. | ✅ |
| S-9.3 | LEVEL_SKIPPED: first-class, zero exposure, zero PnL, never resurrected (§9.3) | — | Skip-lattice is monotone (skipped ⊆ no-exposure); interacts cleanly with D-14 divisors (skipped levels hold no notional). Note `MaxFailedLevelRate = 5%` over ALL basket levels can only alert + defer market re-eval to next Basket ⇒ **no in-basket protection from this bound** (O-4). | ✅ (O-4 noted) |

### §10 — Execution Economics (L808–L835)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-10.1 | `NetExpectedEdge := GrossGridEdge(level,bps) − Fee − Slippage − Funding − Other`; fees live from `userFees`, never hardcoded (§10) | AA-5 | Fee axiom exact (Tier-0 4.5/1.5 bps; tiers move ⇒ live pull correct). **U-1: `GrossGridEdge` appears exactly once in the document (L812) with no closed form.** The gate that binds *all* arming is not computable from the strategy text. The implicit proxy (D-06's `StepBps_as_USD` = one step on basket notional) suggests GGE ≈ StepBps = 10bps, but that is never stated. Two compliant implementations ⇒ different arming decisions ⇒ observable divergence — violates the document's own determinism standard. | ⚠️ U-1 |
| S-10.2 | Floor = 1bp; ≤ floor ⇒ skip, either path; maker preferred; taker only for emergency/hedge | AA-5 | Sanity: maker round trip = 3bps ⇒ net ≈ 7bps > 1 ✓; forced-taker ≈ 10 − 1.5 − 4.5 = 4bps > 1 ✓ (marginally viable, slippage-sensitive — skip bias is the safe direction). | ✅ |

### §11 — Hedge & Mirroring (L837–L897)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-11.1 | `ExpectedExposure := Σ verified filled qty`; `ActualExposure := net szi from clearinghouseState ONLY`; `Δ := Expected − Actual`; total priority: verification → risk → hedge → disable → grid (§11.1) | AA-10 | Semantically precise: the hedge layer enforces *bookkeeping symmetry* (strategy belief ↔ venue truth), and AA-10's single-net-position model makes Σ-signed-fills well-defined. Progression hard-gated on `|Δ| ≤ τ_E` — the gate at F-1. | ✅ (gate → F-1) |
| S-11.2 | Acute ⇒ unconditional Ioc; else cost-aware, prefer maker-side correction (§11.2) | AA-5 | Acute branch is **size-bounded implicitly** (correction size = |Δ| ≤ one level by construction) but **cost-unbounded**; in a void, slippage on a $5,000 Ioc is book-limited but not strategy-limited. Tension with §10 floor ⇒ U-4. | ⚠️ U-4 |
| S-11.3 | Mirroring produces INTENT → re-enters full §8/§10 gates; never bypasses (§11.3) | — | Consistent with §8-inv.3 (approval only restricts); note interplay with U-4. | ✅ |
| S-11.4 | Partial fill: exposure = verified filled only; remainder not hedged while working; post-timeout remainder → emergency/skip ⇒ residual contributes zero (§11.4) | AA-11 | Clean separation of working vs taken exposure; no double-hedging of the remainder. | ✅ |

### §12 — Risk Model (L899–L985)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-12.1 | `MaxBasketNotional := min(L_eff·E₀·0.9, E₀·L_eff/2, 0.1·MarketDepth)`; computed once → binding (§12.1, D-13) | AA-3, AA-9 | Binding term at defaults = 1.5E₀ ⇒ effective leverage 1.5× ⇒ margin used 50% of equity ⇒ **structural 2× margin buffer**. `MarketDepth` term uses live depth *at computation time*; frozen thereafter ⇒ stale after regime shift (live re-check happens only at arm-time gate 1 ⇒ contained, but the frozen cap can exceed current sane notional — O-3). | ✅ (O-3 noted) |
| S-12.2 | `MaxExposureImbalance := (0.25×0.5/L_eff)×NotionalPerLevel/MarkPrice` = $208 notional-equiv (§12.1, §16) | AA-2 | Derivation *labels* 0.5/L_eff "the maintenance margin fraction" — mis-attribution per AA-2 (actual m = 0.5/maxLev). **Conservativity theorem:** `L_eff = min(L_user, maxLev) ≤ maxLev ⇒ 0.5/L_eff ≥ m_actual` ⇒ every D-16 bound derived from it overestimates risk ⇒ safe-direction error for all single-tier assets. Breaks only if a margin tier caps leverage < L_eff ⇒ notional ≫ strategy scale. See O-1. | ✅ (O-1) |
| S-12.3 | Ordering invariant `τ_E < τ_I < NotionalPerLevel/MarkPrice` (§16 consistency note) | — | **Proven ∀MarkPrice > 0, ∀ L_eff ∈ {2,3,5}, ∀StepBps ∈ {5,10,20}:** in notional terms the three are `5 : 208.3 : 5000` (ratio independent of price and leverage-scaling cancels). The *reported* verification is sound; note τ_I/τ_E = 41.67 — the guard is 41× tighter than the acute trigger, as designed. | ✅ |
| S-12.4 | `MaxRangeInducedDD = 100%` of basket equity (D-09B) | AA-1 | **O-2: vacuous as protection.** A bound that fires only when equity = 0 can never trigger protective action: `∀ t: breach ⟺ equity = 0`, at which point no action remains. AA-1's backstop makes equity-0 *reachable* (⅔-maintenance backstop ⇒ "trader ends up with zero account equity"). This is an owner-approved risk acceptance, not a control. Must be documented as such. | ⚠️ O-2 |
| S-12.5 | MaxExecutionCost (30% of PnL / 100bps of N), MaxHedgeCost 2% of N, MaxFailedLevelRate 5%; three-layer response; **funding appears in no bound** (§12.1, §13.1) | AA-4 | **U-2:** cumulative funding bleed is *unbounded by any risk bound* — it enters only NET PnL and the (vacuous) DD bound. At the AA-4 cap: wrong-way net `N_max` × 4%/hr = **$1,200/hr = 6% of E₀ per hour**. Under hedge symmetry the bleed is ~$8.3/hr (imbalance-bounded) — but the hedge layer's liveness is precisely what U-4/U-5 threaten. | ⚠️ U-2 |

### §13 — Basket Lifecycle (L987–L1083)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-13.1 | NET PnL controls every lifecycle decision; funding explicitly non-negligible (§13.1) | AA-4 | Correct sign conventions; NET-governance consistent with closure. | ✅ |
| S-13.2 | FREEZE blocks only ENTRY_INTENT; corrections classified by *projected* Δ, not reduceOnly flag (§13.3) | AA-10, AA-11 | Venue's `reduceOnly` flag is advisory for classification only — correct, since AA-10 nets everything and a correction may *increase* gross while reducing |Δ|. | ✅ |
| S-13.3 | Closure: NET ≥ 3×(TotalSystemCosts + StepBps_as_USD) **and** residual ≤ τ_R := round_to_min_tradable((StepBps×N/10000)/GridLevels); verified sequence; indefinite management (§13.4, D-06/D-07F) | AA-6, AA-13 | ⚠️ **U-6:** at defaults `f = $5 ⇒ 0.00005 BTC < q_min = 0.0001 BTC`. `round_to_min_tradable_size` has **no defined rounding direction**: ceil ⇒ τ_R = q_min (feasible: one min-size sweep closes to 0); floor/nearest-⇓ ⇒ τ_R = 0 ⇒ closure demands *exact* `szi = 0` (reachable — venue szi is exact — but strictest). Two implementations, two closure boundaries. Closure economics: target = 3×(90+30) = $360 = 1.8% E₀ — coherent. `StepBps_as_USD` values one step at *basket* notional ($30) where a cycle captures step × *level* ($5) ⇒ 6× target inflation (O-3: conservative, slow closure). TWAP mode respects AA-13 (30s/3%/3×) with explicit remaining-qty tracking. | ⚠️ U-6, O-3 |

### §14–§16 — Parameters, Invariants, Dynamic Defaults (L1085–L1368)

| Sᵢ | Claim | Axiom map | Test | Verdict |
|----|-------|-----------|------|---------|
| S-14.1 | Global rule: formulas used ONCE → owner-confirmed → binding; never re-executed; numeric values never invented | — | Eliminates feedback instability (no parameter is a function of live state *at run time* except the tagged dynamic defaults). The one computed-once/live-input tension is O-3 (frozen MarketDepth). | ✅ |
| S-14.2 | §15 invariant 19: every transition reconstructable from persisted state + authoritative observations | AA-10, AA-14 | The formal escape from AA-14's latency vacuum: reconstruction needs only *recorded* events + reads, no timing assumptions. | ✅ |
| S-16.1 | EmergencyTolerance := 0.005×(10000/L_eff) bps; "1% of the liquidation buffer" (§16) | AA-2 | Buffer claim is model-relative: modeled buffer = 833bps ⇒ 1% = 8.3bps… the doc actually derives 0.5% of *initial-margin distance* (3333bps) = 16.7bps = 1% of *modeled maintenance distance* (1667bps) ✓ internally consistent. Versus **actual** liquidation buffer (6570bps @50x): the band is 0.25% of the real buffer ⇒ 4× more conservative than the design intent. Safe direction. | ✅ (O-1) |
| S-16.2 | "BTC/ETH max leverage = 40x" in the mechanics preamble | AA-2 | Docs internally inconsistent (example 50 vs prose 3–40x), **verified still inconsistent live on 2026-09-21**. Immunized by D-13 (`L_eff = min(3, live maxLev)`): ∀ live value ≥ 3, every executed formula is invariant to 40-vs-50. The only formulas that could break require `maxLev < 3` — outside the top-5-liquid scope. | ✅ (immunized) |
| S-16.3 | Mark price for margin accounting/liquidation triggers | AA-2, AA-9, AA-12 | Verbatim-confirmed (live re-fetch). | ✅ |

---

## 4. Scenario Simulations (Adversarial Walkthroughs)

### Scenario 1 — "The Liquidity Void" (flash crash: −3% in 60s, bid book evaporates)

```
t=0   Mark M = 100,000. Reference r = 100,000. Ladders: BU [20..70]bps above,
      SL [20..70]bps below (BTC, defaults). Net exposure ≈ 0 (hedge intact).
t+5s  Price −1.2%: SL1 (99,800), SL2 (99,700) fill as resting Gtc limits —
      each fill ⇒ POSITION_VERIFIED via clearinghouseState (AA-10); hedge buys
      net Δ→0 within τ_I = $208.
t+20s −2.5%: book thins; gate-1 depth check (≥10× size within band) FAILS on
      new arming ⇒ no NEW orders enter the void (fail-closed). Existing fills
      continue: SL3..SL6 fill ⇒ TerminalEvent(SL) ⇒ §5.2 sequence: cancel SL
      pendings, reconcile, N1–N3 on post-cancel state, new Cycle at
      r' = SL6 exec ±3.3bps tolerance gate.
Hedge Ioc in the void:  size bounded by |Δ| ≤ 1 level = $5,000;
      cost bounded by band 17bps + fee 4.5bps ⇒ ≤ $10.75/fill IF fillable
      within band; else SKIP (zero exposure taken) ⇒ acute branch only if
      |Δ| > τ_I ⇒ unconditional Ioc at ≤ level size ⇒ slippage bounded by
      book depth at $5,000 notional (BTC: negligible vs $300k+ depth axiom-space;
      in true void, Fillable() fails ⇒ SKIP ⇒ Δ persists ⇒ RECONCILIATION_REQUIRED
      + operator alert — no silent assumption).
Liquidation check: worst instantaneous net = τ_I breach window ⇒ N ≤ $5,000+
      transient ⇒ d_liq ≥ (20,000 − 0.0125·5,000)/5,000 ≈ 394% ⇒ UNREACHABLE.
      Even at full cap N = 30,000 (hedge fully failed): d_liq = 65.4–65.7%
      (AA-2 actual) vs 50% modeled ⇒ model conservative. A −3% crash is 22×
      inside the actual liquidation boundary.
State integrity: reference tolerance (±3.3bps) + N1–N3 BLOCK on any anomaly;
      no order enters at a stale/overlapped price. MaxExecutionCost bound
      (100bps × 30k = $300 at PnL ≤ 0) trips ⇒ alert → soft action → operator.
```
**Verdict: SURVIVES.** The combination `depth-gate (pre) + Ioc band (during) + POSITION_VERIFIED + BLOCK (post)` is closed under the void. Residual gap: none fatal; O-3 (frozen `MarketDepth` cap) merely permits *attempting* larger orders than the new depth would allow — gate 1 catches them per-arm.

### Scenario 2 — "The Funding Spike" (funding pins at the 4%/hour cap against the position, then flips sign)

```
Regime A (hedge intact, |net| ≤ τ_I = $208 notional):
      bleed ≤ 208 × 4%/hr = $8.33/hr = 0.042% E₀/hr ⇒ 24h ≈ $200 (1% E₀).
      Negligible; funding-flip requires no action (AA-4 settles hourly on
      oracle notional; sign flip just changes the payer).
Regime B (hedge layer halted — persistence failure (FM-10 semantics) or
      venue rejects at ≥1000 open orders (AA-8)):
      strategy fails closed: no ENTRY intents, corrections allowed but if
      the halt is total, net drifts to profit-layer inventory ≤ N_max = 30k.
      bleed = 30,000 × 4%/hr = $1,200/hr = 6% E₀/hr ⇒ 16.7 hours to −100%
      from funding ALONE (independent of price). No bound in Strategy.md
      caps this: MaxHedgeCost bounds hedge fills, MaxExecutionCost bounds
      fees+slippage, MaxRangeInducedDD fires only at equity = 0.  ⇒ U-2.
Regime C (flip mid-basket): hourly settlement on AA-4 oracle notional;
      NET PnL accounting absorbs sign changes; closure target locked at
      first eligibility (D-15 lifetime-to-date) is unaffected; late funding
      reduces NET ⇒ closure merely waits. Sound.
```
**Verdict: SURVIVES only in Regime A/C.** Regime B exposes the missing funding circuit-breaker (U-2). The strategy's own §13.1 declares funding "not negligible," then declines to bound it.

### Scenario 3 — "The Latency Lag" (stale local state vs. venue truth; settlement races)

```
Premise (AA-9): mark/oracle re-quote ~3s; book/fills stream via WS in
real time; AA-14: NO latency/finality guarantees exist.

(i) Stale mid in arming: DistanceBand computed vs a 3s-old mid during a
    5σ move (≥50bps/3s) ⇒ a "50bps" order is really 0–100bps from venue
    mark. Consequence chain: gate 2 band-check misclassifies ⇒ order rests
    at wrong band position ⇒ it is still a passive limit ⇒ fills only if
    traded through ⇒ POSITION_VERIFIED anchors truth ⇒ worst case is a
    mistimed entry, not a false state. The venue's own trigger evaluation
    (AA-12: mark, venue-side) is authoritative and unaffected by local
    staleness. Bounded harm: entry-timing error ≤ Δt·σ.
(ii) Race, signal → settlement: two passes evaluate before the fill's
     state lands. §4.7 serializes decisions; STR-0344 (one active order
     per Level) prevents duplicate arming; U-5 (cloid dedup undocumented)
     is the residual hole: a timeout-retry may double-execute, detected
     post hoc by delta mismatch (Δ jumps by 2×size) ⇒ RECONCILIATION_REQUIRED.
     Contained, but the duplication cost is real money for one window.
(iii) 60s Evolution confirmation vs 3s index cadence: ≥20 independent mark
     updates must sustain the verified condition ⇒ flip-flop and index-
     manipulation windows are absorption-bounded by the latch + 20× margin.
```
**Verdict: SURVIVES by construction.** The strategy never *assumes* synchrony — it *verifies* it after the fact. Required hardening: freshness policy (max-age ≤ 3s per data type; `|mid − mark| ≤ τ_ref` arming guard) and reconcile-before-retry (closes U-5's window to zero).

---

## 5. Formal Recommendations

Each is stated as a precise rule change with its supporting argument.

**R-1 (closes F-1\*) — Quantize the exposure gate to tradability.**
Define `T := max(τ_E, (1+ε)·q_min)`, `ε ∈ (0,1]` (e.g. ε = 1 ⇒ `T = 2·q_min`); replace every progression gate predicate `|Δ| ≤ τ_E` with `|Δ| ≤ T`, and add the correction rule `if 0 < |Δ| < q_min then Δ := 0 (round-to-zero, logged)`.
*Proof of liveness:* ∀δ ≥ 0: either `δ ≤ T` (progression permitted) or `δ > T ≥ q_min` (∃ a venue-acceptable corrective order, AA-6). The dead-band is empty by construction. Keep `τ_E` as the *accounting* tolerance (it correctly bounds szDecimals residue: ≤ $0.50 ≪ $5); only the *gate* must be tradability-quantized.

**R-2 (closes U-1) — Give GrossGridEdge a closed form.**
`GGE(k) := (P_terminal − P_k)/P_terminal × 10⁴ bps` (distance-to-terminal of the level's own group), or the conservative constant `GGE ≡ StepBps` — either is consistent with D-06's implicit one-step economics. Any candidate must satisfy `GGE − 2·fee_maker − funding_est > NetExpectedEdgeFloor` at Tier-0 fees (10 − 3 − 0 > 1 ✓) or be rejected at calibration. Untitled symbols in a binding gate are the single largest indeterminacy in the document.

**R-3 (closes U-2) — Funding circuit-breaker.**
Add Group-B bound: `FundingBleedRate := |d(BasketFunding)/dt|` over a rolling 1h window; breach when `FundingBleedRate > β·E₀/hr`, β = 0.5% (default), response = layer-2 soft action (force hedge-recovery evaluation; suspend new entries) + operator escalation. This bounds Regime-B bleed to `β` of equity per hour instead of 6%.

**R-4 (closes U-3) — Strengthen N3 to ε-overlap.**
Replace "no new level price may **equal** any still-live price" with `|p_new − p_live| ≥ max(1 tick, 0.1 × StepBps)` for all still-live same-group orders *and* opposite-group orders resting inside the new ladder's span. Alternative minimal fix: cancel opposite-group pendings beyond ±(FirstLevelDistanceBps + N·StepBps) of the new reference during §5.2 step 2. This makes the computable test match the stated invariant.

**R-5 (closes U-4) — One-sentence precedence rule.**
Add to §10: *"The NetExpectedEdge floor applies to ENTRY_INTENT and to non-acute EXPOSURE_CORRECTION_INTENT; it never applies to acute Hedge Recovery (§11.2), which is size-bounded by |ExposureDelta| and band-bounded by EmergencyTolerance."* This reconciles §8-inv.1, §10, and §11.2 with a total order on gating authority.

**R-6 (closes U-5) — Reconcile-before-retry, never assume idempotency.**
Reword §6.2: cloid is the *reconciliation identity* (lookup, cancel-by-cloid); idempotency must be *established*, not assumed: on any ambiguous submission enter UNKNOWN_SUBMISSION, query `orderStatus` by cloid (+`openOrders`), and forbid new side effects until resolved; attach `expiresAfter` to actions. (This matches the program's DECISION-008; Strategy.md's "idempotent" wording is the part that must change.)

**R-7 (closes U-6) — Define the closure rounding.**
`ResidualExposureToleranceAtClosure := max(f_rounded_up_to_lot, q_min)` — i.e. **ceil** onto the szDecimals grid, floored at one minimum tradable unit. Feasibility proof: after the final sweep of size `q_min`, `szi → 0` exactly (AA-10), and `0 ≤ τ_R` always ⇒ closure precondition is satisfiable; with τ_R ≥ q_min the common case (residual = one rounding ulp) closes in one min-size order instead of demanding exact zero.

**R-8 (closes U-7) — Pin the margin mode.**
Add a FIXED §14 parameter `MarginMode ∈ {cross, oneWay}` with a P0 assertion: `∀ position: assetPositions[].leverage.type == MarginMode`, else FREEZE. Justification: the entire D-16 family and `MaxSafeNotional_margin` assume cross-style account-level liquidation (AA-1); in isolated mode `margin_available` is per-position and `liq_price` depends on set leverage (AA-10 shows isolated positions exist as a first-class venue state) ⇒ the risk model's arithmetic is invalid in the other mode. One bit of configuration removes an entire class of silent model invalidation.

**R-9 (closes U-8) — Rate budget theorem as configuration constraint.**
Per-pass REST weight `W_pass = w(chs) + w(book) + w(ctxs) + … ≤ 26`; require pass cadence `f_p ≤ 1200·0.5/W_pass ≈ 23 passes/min` (50% headroom), with WS-first substitution (`orderUpdates`, `userFills`, `clearinghouseState` WS ⇒ 0 REST weight). Encode as a §8/§14 operational invariant, otherwise the pass engine is free to violate AA-8 at >46 full-refresh passes/min.

**R-10 (O-1/O-2, documentation honesty) — Re-derive, don't re-label.**
(i) Replace the D-16 derivation *basis* with `m := 0.5/maxLevTier(N)` read from live `meta.marginTables` (now documented by the venue), retaining `0.5/L_eff` explicitly as a conservative upper bound — the conservativity theorem (`0.5/L_eff ≥ m_actual` ∀ configs where `L_eff ≤ maxLevTier`) justifies keeping the formulas while fixing their stated semantics. (ii) Relabel `MaxRangeInducedDD = 100%` in §12.1 as what it is — an accepted-loss declaration (D-09B), not a monitored bound — so no implementer builds a (vacuous) trigger on it.

---

## 6. Final Proof Statement

**Setting.** Axioms AA (§2) model the venue. Strategy T is the rule set of `Strategy.md` v2.3-final with defaults `E₀, L_eff = 3, StepBps = 10, GridLevels = 6`. Solvency = "no venue liquidation is reachable while the strategy's own protection premises hold, and no strategy rule forces an undefined action."

**Lemma 1 (Async soundness).** Every state claim in T has the form `claim ⇐ fill-event ∧ clearinghouseState-read` (S-5.1, S-6.1, S-11.1). Since AA-10 makes `clearinghouseState` a point-in-time ground truth and AA-14 grants no timing guarantees, T's claims are invariant to message reordering and latency: no reordering of venue emissions can manufacture a false claim. ∎ (T is well-posed under AA-14's vacuum.)

**Lemma 2 (Conservative risk model).** `L_eff = min(L_user, maxLev) ≤ maxLev ⟹ m_model = 0.5/L_eff ≥ 0.5/maxLevTier = m_actual` (AA-2). Hence `d_liq^model = E₀/N − m_model ≤ E₀/N − m_actual = d_liq^actual`: every strategy threshold derived from `m_model` fires **no later** than venue liquidation would occur. The model can only over-protect, never under-protect, for all single-tier assets in scope. ∎

**Theorem (Conditional solvency).** Assume (i) margin mode pinned to cross/oneWay, (ii) hedge-layer liveness (corrections executable when `|Δ| > τ_I`), (iii) F-1\* closed per R-1. Then: `N(t) ≤ N_max = 1.5E₀` (S-12.1 caps) and `|Δ(t)| ≤ τ_I` outside correction windows, hence `d_liq(t) ≥ E₀/N_max − m_actual ≥ 0.653` (65.3%, BTC/ETH). The grid geometry spans 70bps ≪ 65.3%, and per-fill emergency costs are band-bounded (≤ 21.5bps). Therefore liquidation requires the *joint* event {hedge-liveness failure} ∧ {≥ 65.3% adverse excursion before operator intervention} — an event no rule of T makes probable and none makes impossible (U-2/U-4/U-5 are its enablers). Under (i)–(iii), T ⊨ solvency; dropping any conjunct leaves the enablers open. ∎

**On A ⊢ T.** The extraction *does* hold in its approved core: no statement of T contradicts AA-1..AA-13, and T's treatment of AA-14 (the absence axiom) — verify-don't-assume — is the formally correct response. What A ⊬ T delivers is completeness: eight behaviors (F-1\*'s dead-band escape, the economics gate's closed form, funding bounds, ε-overlap, correction precedence, idempotency, closure rounding, margin-mode) are *undetermined by* T, and undetermined behavior is where implementations go to diverge.

**Final verdict.** `Strategy.md` is **logically sound against the real Hyperliquid mechanics and conditionally solvent**: with R-1/R-6/R-8 applied (the three that gate the solvency theorem's premises) and U-1/U-2 closed before implementation, the strategy contains no path to liquidation or state corruption that its own protections do not bound. Without them, the D-16 defaults as written contain one proven livelock cell (F-1\*) and the hedge layer's liveness — the sole support of the 65-point liquidation buffer — rests on under-specified mechanics. Confidence **82/100**: high because every load-bearing venue claim was verified against live primary sources and every internal ordering property was proven; reserved because 4 axioms are documented absences and implementation (the phase this document precedes) is where specification soundness goes to die.

---

*Audit complete. No repository file other than this report was created or modified. `Strategy.md` remains byte-identical (SHA-256 re-verified).*
