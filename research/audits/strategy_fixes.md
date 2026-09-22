# strategy_fixes.md — Logical Resolution Engine Output

- **Inputs:** `strategy_audit.md` findings **F-1\*** (livelock), **U-1** (undefined `GrossGridEdge`), **U-2** (unbounded funding bleed), **U-3..U-8** (consistency gaps); axioms AA-1..AA-14 (hash-verified Hyperliquid mechanics).
- **All numeric constants below were machine-verified** against the strategy defaults (`E₀=$20,000, L_eff=3, StepBps=10, GridLevels=6, MaxBasketNotional=$30,000, BTC szDecimals=5`) and the venue hard limits (AA-4 4%/hr cap, AA-6 $10 minimum, AA-7 tick/lot, AA-8 1200 weight/min).
- **Governance:** `Strategy.md` is immutable (repo `CLAUDE.md`). Every fix is therefore specified as an **amendment-ready rule** in owner-decision format (§4 Integration Guide gives exact anchors), adoptable via the established D-01…D-17 amendment pattern. No code, no file edits.
- **Notation:** ∀, ∃, ⟹, ¬; quantities in base-asset units unless marked `$`; `lot := 10^(−szDecimals)`; `M := MarkPrice`; `Δ := ExposureDelta`; `ceil_lot(x) := lot·⌈x/lot⌉`.

---

## 1. Executive Summary

**All identified deadlocks are resolved with deterministic, autonomous, code-ready rules.** F-1\* is dissolved by replacing the price-invariant constant `ExposureTolerance = $5` with a **tradability-quantized dynamic threshold** `B(M) = max(τ_acc(M), q_min(M))` and a two-bound governor (`T_enter = 2B`, `T_exit = B`) for which the dead-band is provably empty — the triggered correction is guaranteed venue-executable **even under a 50% instantaneous price collapse between decision and execution**. U-1 is resolved by a closed-form `GrossGridEdge` with an explicit volatility-safety factor α and a closed-form arming inequality. U-2 is resolved by a signed net-funding accumulator with a predictive circuit breaker that bounds worst-case bleed at **2.30% of equity** and provably cannot fire spuriously at cold start. U-3..U-8 are resolved by twelve entry assertions (A-1..A-12) enforcing the truth hierarchy `VenueState ⊐ LocalModel ⊐ Heuristic`, pinned margin mode, direction-proven rounding, and a REST-weight budget. Every fix preserves the strategy's §4.7 total order, §11.1 priority ladder, and §12.1 three-layer response semantics; the single place the strategy text is *strengthened* (funding breaker escalation) is anchored to its own §12.2 risk-precedence clause.

---

## 2. The Solutions Core

### Agent 1 — The Paradox Dissolver (F-1\*: the livelock)

**Paradox restated formally.** Let `τ_E = $5` (price-invariant, §16 D-16) and `q_min(M) = $10/M` (AA-6). Then `∀M > 0: τ_E < q_min`, and ∃ reachable δ with `δ ∈ (τ_E, q_min)` for which:
`¬progression (δ > τ_E)` ∧ `¬∃ executable order (δ < q_min)` — a livelock cell in state space.

**Resolution principle.** A gate threshold that can trigger action must be **≥ the minimum executable action size**, quantized to the tradability lattice. Two tolerances are separated: the **accounting residue** (D-16's true purpose: absorb szDecimals rounding, ≤ ½ lot ≈ $0.50) and the **governance gate** (must be tradable). Only the gate is replaced.

**The dynamic threshold function:**

```
b        := EmergencyTolerance_bps / 10⁴                     [D-16 band = 16.67 bps @ L_eff=3]
q_min(M) := ceil_lot( MinNotional / (M·(1−b)) )              [AA-6 quantity, sell-side worst case;
                                                              MinNotional = $10]
τ_acc(M) := (0.001 · StepBps/10) · NotionalPerLevel / M      [D-16 retained, accounting only]
B(M)     := max( τ_acc(M), q_min(M) )                        ← f(MarkPrice, MinNotional)

T_enter  := (1 + ε_H) · B(M),   ε_H := 1                     [correction trigger + progression gate]
T_exit   := B(M)                                             [post-correction release bound]
```

**Worked values (defaults, M = $100,000):** `b = 0.001667`; `q_min = 0.00011 BTC ($11.00)`; `τ_acc = 0.00005 ($5)`; `B = $11`; **`T_enter = $22`, `T_exit = $11`**. Ordering invariant preserved: `T_enter ($22) < τ_I ($208.33) < one level ($5,000)` ✓.

**The Exposure Governor (autonomous state machine, evaluated each §4.7 P0 pass on the Δ read of that same pass):**

```
state CLEAR      : |Δ| ≤ T_exit
    → progression PERMITTED; no correction.                     (Δ is tolerated residue)
state GOVERNED   : T_exit < |Δ| ≤ T_enter
    → progression PERMITTED (|Δ| ≤ T_enter satisfies the gate);
      correction SUPPRESSED (anti-chatter band);
      |Δ| bounded by construction: ≤ 2·q_min ≈ $20 ≪ τ_I.       (no unbounded carry)
state CORRECT    : |Δ| > T_enter
    → progression BLOCKED (unchanged §5.2/§11.1 conjuncts — hedge-in-progress,
      FREEZE/ERROR/RECOVERY — still apply verbatim);
      submit EXPOSURE_CORRECTION_INTENT Ioc, qty := ceil_lot(|Δ|),
      limit at ±b band edge (§9.1 mechanics), DECISION-008 discipline
      (persist cloid → send → reconcile UNKNOWN_SUBMISSION).
transitions:  CORRECT → (recompute Δ next pass) → CLEAR | GOVERNED | CORRECT (symmetric in sign)
termination:  if 3 consecutive CORRECT attempts in one pass-window leave |Δ| > T_enter
              → RECONCILIATION_REQUIRED (fail-closed; deterministic termination, no infinite churn)
```

**Why the dead-band is empty — the two-sided guarantee:**

1. `|Δ| > T_enter = 2·B ≥ 2·q_min ⟹ qty = |Δ| > q_min(M)` ⟹ order value `≥ q_min(M)·M·(1−b) ≥ MinNotional = $10` — by construction of `q_min`. ✓ (verified: worst-case sell value $10.98 ≥ $10).
2. `|Δ| ≤ T_enter ⟹ progression open` — the system is never simultaneously blocked and unexecutable. ∎ (livelock cell `∃δ: τ_E < δ < q_min` is eliminated because the lower gate bound *is* the tradability bound).

**Robustness corollary (async/price-gap).** A triggered order has value `|Δ|·M′ ≥ T_enter·M′`; it stays ≥ $10 whenever `M′ ≥ M/2`. **The guarantee survives a 50% instantaneous price collapse between the state read and order receipt** — strictly beyond any venue latency scenario in AA-9's ~3s index cadence. ∎

**Legacy-delta migration rule:** for `0 < |Δ| < T_exit` at adoption, set `Δ̂ := 0` (round-to-zero, logged, D-07(F) idiom) — one-time absorption of the inherited dead-zone.

---

### Agent 2 — The Variable Synthesizer (U-1: `GrossGridEdge` closed form)

**Requirement.** `GrossGridEdge = f(Spread, α)` — closed form, deterministic, replay-safe — with the arming condition given as an explicit inequality in (Spread, Fees, α). Fees remain in the §10 subtraction (NetExpectedEdge already deducts them; folding them into GGE would double-count against Strategy §10's own formula).

**Definitions (all inputs are recorded observation events — AMB-0016 discipline — hence replay-deterministic):**

```
S        := Spread_eff_bps  = (ask₁ − bid₁)/mid × 10⁴        [L2 BBA already fetched for §8 gate 1]
σ̂_w      := EWMA of |M-return| over window w = 30 s, halflife 10 min, in bps
            [w = EmergencyBoundedWaitSeconds, §14]
σ_ref    := 0.25 × StepBps                                    [calibration baseline: quarter-step calm regime]
α        := clamp( σ̂_w / σ_ref , 1, 4 )                       [safety factor: 1 = calm, ≥4 = violent]
```

**The closed form:**

```
GrossGridEdge  :=  StepBps  −  α · S / 2

NetExpectedEdge :=  GrossGridEdge − Fee(path) − Slippage_est − FundingCostEstimate − Other
                    [§10 structure unchanged; Fee live from userFees, AA-5]
```

*Rationale of each term:* `StepBps` is the nominal capture of one completed level-cycle (entry at P_k, ladder accounting to P_{k±1}; the strategy's own floor `StepBps/10` and D-06's `StepBps_as_USD` are both one-step-denominated — this is the strategy's implied unit, now made explicit). `α·S/2` is the **adverse-selection haircut**: a resting maker is filled preferentially when price trades through it; the standard unbiased estimate of the fill-vs-mid markout is half the effective spread, scaled by α for regime violence.

**The arming condition — "positive enough" — as a closed inequality:**

```
Arm  ⟺  GrossGridEdge − Fee − Slippage_est − FundingCostEstimate > NetExpectedEdgeFloor

⟺   α  <  2·(0.9·StepBps − Fee − Slippage_est − FundingCostEstimate) / S      [α-ceiling]
```

**Verification at defaults (maker path, Tier-0 fee 1.5 bps, AA-5):**
- Calm (`α=1, S=2`): `GGE = 9.0`; `NEE = 10 − 1 − 1.5 = 7.5 > 1` → **arm** ✓ (computed).
- Violent (`α=4, S=5`): `GGE = 0.0`; `NEE = −1.5 ≤ 1` → **skip** ✓ (computed) — the gate now correctly refuses to quote into a violent regime, which the undefined constant could not express.
- `α-ceiling` at `S=2`: `α_max = 7.5` — ample headroom; at `S ≥ 15` bps even `α=1` blocks arming (half-spread alone eats the step) — economically correct.

**Determinism assertion (A-8, §Agent 4):** `S`, `σ̂_w`, α, and every cost input are recorded with the arm decision; α is a pure function of recorded series ⟹ replay-reproduces. ∎

---

### Agent 3 — The Risk Bounding Architect (U-2: unbounded funding bleed)

**Hazard restated.** With the hedge layer halted, worst-case bleed at the AA-4 cap is `N_max · 4%/hr = $1,200/hr = 6% E₀/hr`; no §12.1 bound sees funding. Required: an autonomous breaker with **bounded loss**, no manual step, consistent with §12.2 (acute risk ⟹ emergency closure rules take precedence over the profit target) and §12.1's Group-B discipline.

**State variable (venue-grounded, replay-safe):**

```
ACC_t := Σ_{events e ∈ userFunding, e.time ≤ t}  usdc_e        [signed: paid > 0, received < 0;
                                                                AA-4/AA-10 venue-recorded deltas,
                                                                dedup key (time, coin, delta) — A-9]
r̂_F   := EWMV(net funding per hour), window 1 h;
         cold start (no sample): r̂_F := |N| · 0.04             [worst-case AA-4 cap — conservative]
```

Signed (net) accumulation is deliberate: funding's equity impact *is* its net sum; a ratchet would trip on net-zero-impact histories and is gameable in the other direction.

**Threshold and predictive trigger:**

```
X       := β_F · E₀,          β_F := 0.02                     [owner budget: 2% of equity]
T_close := 180 s                                              [bounded closure envelope: k legs ×
                                                                30 s (EmergencyBoundedWaitSeconds)
                                                                + reconciliation, IMMEDIATE_IOC mode]

FUNDING_BREAK  ⟺  ACC ≥ X   ∨   ACC + r̂_F · T_close ≥ X       [reactive ∨ predictive]
```

**State machine (overlay states, FROZEN-style, per ST-22 pattern — never erase lifecycle state):**

```
FUNDING_OK ──ACC ≥ X/2──────────► FUNDING_WARN
    actions (autonomous, layer-2): suspend new ENTRY_INTENT arming; force Hedge-Recovery
    evaluation each pass; corrections remain permitted (§13.3 semantics).
FUNDING_WARN ──FUNDING_BREAK────► FUNDING_BREAK
    actions: invoke §13.4 closure sequence in EMERGENCY mode under §12.2 risk precedence:
        stop progression → cancel rests → reconcile → close (per BasketCloseMode)
        → reconcile → verify residual ≤ τ_R  [net-profit precondition WAIVED by §12.2;
          residual-exposure precondition ENFORCED]
    → Basket CLOSED | (residual unverifiable) → RECOVERY (fail-closed)
reset: ACC := 0 at Basket INITIALIZING (lifecycle-scoped, like all Basket accumulators)
```

**Bounded-loss proof (computed):** worst case `N = N_max = $30,000`: reactive window `X / rate = 400/1200 = 20.0 min` ≫ `T_close = 3 min`; predictive margin `r̂_F·T_close ≤ $60`; **total bleed ≤ X + $60 = $460 = 2.30% E₀** — a hard constant, independent of regime duration. ∎

**No-spurious-trigger proof (computed):** cold start with `ACC = 0`, worst-case `r̂_F`: the predictive arm fires only if `N·0.04·0.05 ≥ 400`, i.e. `N ≥ $200,000 > N_max = $30,000` — **unreachable** under §12.1 caps. ∎

**Consistency note:** this is the strategy's *first* automatic escalation to closure; it is authorized by Strategy.md §12.2's own precedence clause ("Hedge Layer authority, Freeze, Recovery, and **emergency closure rules** take precedence over waiting for profit" when risk is acute) — the breaker is the *detector* that makes "acute" decidable for the funding axis.

---

### Agent 4 — The Consistency Integrator (U-3..U-8: canonical assertions)

**Truth hierarchy (normative for every function):**

```
VenueState (clearinghouseState, userFunding, orderStatus — AA-10/AA-11)
    ⊐  LocalModel (event-fold projections ST-01..ST-23)
        ⊐  Heuristic (α, S, Fillability estimates, σ̂_w)

A-0 (authority):  ∀field f: authority(f) = VenueState ⟹ ¬∃ writer(f) ∉ {observation ingestion};
                  LocalModel must reconcile to VenueState at every P0 or FAIL-CLOSED;
                  Heuristic may gate inputs, never write state.                    [closes DECISION-002 erosion]
```

**Entry assertions (checked at function entry; violation ⟹ the function's fail-closed branch, never a guessed continuation):**

| ID | Assertion (predicate) | Closes | Anchor |
|----|----------------------|--------|--------|
| **A-1** | `startup: config.MarginMode == "cross" ∧ ∀p ∈ clearinghouseState.assetPositions: p.leverage.type == "cross" ∧ p.type == "oneWay"`, else ABORT before any side effect; `each P0: same ∀p`, else FREEZE | **U-7** | §14 new FIXED param; §11.1 |
| **A-2** | *Rounding canon (direction-proven):* entry qty → `floor_lot` (never exceeds cap/residual budget); correction/closure qty → `ceil_lot` (residual after overshoot ≤ 1 lot ≤ T_exit ⟹ tolerated); **Ioc** price: buy `ceil_tick`, sell `floor_tick` (aggressive ⟹ fill certainty); **Alo** price: buy `floor_tick`, sell `ceil_tick` (passive ⟹ never crosses, AA-11 reject-on-cross preserved); every threshold (B, q_min, X, τ_R) → `ceil` (a trigger never fires below an executable size) | **U-6** | §6.3, §13.4 |
| **A-3** | *ε-overlap:* ∀ new level price p, ∀ live order price q (same group ∨ opposite group within the new ladder span): `|p − q| ≥ max(1 tick, 0.1·StepBps·p/10⁴)`, else §5.6 BLOCK | **U-3** | §5.6 N3 replacement |
| **A-4** | *Gating precedence (total function):* `acute(Δ) ⟹ ¬EconomicsGate(correction)` ∧ `¬acute(Δ) ∧ correction ⟹ EconomicsGate(correction)`; `acute(Δ) :⟺ |Δ| > τ_I ∨ margin-distance < 2·d_emergency` — resolves §8-inv.1 vs §10 "either path" vs §11.2 exactly, no overlap, no gap | **U-4** | §10 insert |
| **A-5** | *Submission gate:* `persisted(cloid, intent) ∧ ¬∃ unresolved UNKNOWN_SUBMISSION` precedes every `/exchange` POST; retry forbidden until `orderStatus(cloid)` resolves; `expiresAfter` attached to all actions | **U-5** | §6.2 rewording: cloid = *reconciliation identity* (idempotency established, never assumed — AA-11) |
| **A-6** | *Rate budget:* rolling-60s REST weight ≤ `W_max := 600` (= 50% of AA-8's 1200); per-pass weight ≤ 26 (`chs 2 + book 2 + ctxs 20`); token-bucket enforced in adapter; WS-first substitution for `orderUpdates/userFills/clearinghouseState` (weight 0) | **U-8** | §8 new operational gate |
| **A-7** | *ε-overlap for reference:* `|captured_ref − nominal_ref| ≤ 0.33·StepBps` (existing §5.4.1) evaluated **before** A-3, both on tick-quantized prices (AMB-0012) | **U-3** | §5.4.1 |
| **A-8** | *Economic-gate computability:* `S, σ̂_w, α, Fee, Slippage_est, FundingCostEstimate` are recorded observation events co-incident with every arm decision; `GGE` is a pure function of them ⟹ replay-reproduces | **U-1** | §10, AMB-0016 |
| **A-9** | *Idempotent accumulator:* each `userFunding` event applied to ACC exactly once, keyed (time, coin, delta); duplicate receipt ⟹ no-op ∧ logged | **U-2** | §12.1/§13.1 |
| **A-10** | *Closure tolerance:* `τ_R := max( ceil_lot(f), q_min(M) )`, `f = (StepBps·MaxBasketNotional/10⁴)/GridLevels` — feasibility: after the final `q_min` sweep, `szi → 0` exactly (AA-10) and `0 ≤ τ_R` always ⟹ closure precondition satisfiable; common residue (1 ulp ≈ $0.50) closes in one min-size order | **U-6** | §13.4 (D-07(F) direction fixed to ceil) |
| **A-11** | *Freshness:* every gate input carries `age ≤ max_age(type)` with `max_age(mark/oracle) = 6 s` (2× AA-9 cadence), `max_age(book) = 1 pass`; stale ⟹ that gate FAILS (fail-closed), never silently passes | **(async)** | §8 gate 0 (new) |
| **A-12** | *Ordering:* `T_exit < T_enter < τ_I < NotionalPerLevel/MarkPrice` — asserted at config resolution; verified at defaults ($11 < $22 < $208.33 < $5,000); any input set violating it ⟹ config rejected (fail-closed at init, §14 global rule) | **F-1\*** | §14 consistency note |

---

## 3. Proof of Safety (one sentence per fix)

| Fix | One-sentence proof |
|-----|--------------------|
| **1 (Livelock)** | Since `T_enter = 2·max(τ_acc, q_min) ≥ 2·q_min`, any triggered correction has `qty = |Δ| > q_min ⟹ order value ≥ $10` even at price `M/2`, and any non-triggered `|Δ| ≤ T_enter` leaves progression open — hence the state `¬progression ∧ ¬executable` is unreachable ∀Δ, ∀M > 0. ∎ |
| **2 (Undefined Edge)** | `GGE` is now a total, pure function of recorded observables (S, σ̂_w via α, constants), so the arming predicate `α < 2(0.9·StepBps − Fee − Slip − Funding)/S` is decidable and replay-reproducible — two implementations can no longer diverge. ∎ |
| **3 (Bleed)** | Since the predictive trigger fires at `ACC + r̂_F·T_close ≥ X` with `T_close = 180 s ≥` closure envelope, cumulative funding loss is hard-bounded at `X + r̂_F·T_close ≤ $460 = 2.30% E₀` independent of regime duration, and cold-start analysis shows the trigger requires `N ≥ $200,000 > N_max` to fire spuriously — impossible. ∎ |
| **4 (Consistency)** | Each assertion is a total predicate evaluated at entry with a single fail-closed else-branch, so every previously ambiguous path (margin mode, rounding direction, overlap, gate precedence, retry, rate budget, freshness, closure rounding) now has exactly one deterministic outcome. ∎ |

---

## 4. Integration Guide (exact Strategy.md anchors)

> **Governance route (binding):** `Strategy.md` is immutable. Each fix below is applied by registering an owner decision in `research/decisions/DECISION_REGISTER.md` (proposed ids **DECISION-016..019**; each requiring an Owner Gate per `CLAUDE.md`) and issuing a **v2.4-final** revision whose §16 change-log supersedes the named clauses, exactly as D-16 superseded the `[TEMP]` defaults. Line anchors refer to v2.3-final (1-based, 1,368 lines).

| Fix | Strategy.md anchor | Action |
|-----|--------------------|--------|
| **1** | **§5.2** transition block (the gate clause after step 8, L≈369–376): replace `\|ExposureDelta\| ≤ ExposureTolerance` with `\|ExposureDelta\| ≤ T_enter(M)` per the Governor; keep all other conjuncts verbatim. **§11.1** (L≈855–858): same predicate substitution in the progression-gate sentence. **§14** `ExposureTolerance` row (L≈1143): split into `ExposureToleranceAcc` (D-16 formula, accounting) + `ExposureGovernor {ε_H=1, k_max=3}` (FIXED). **§16** D-16 `ExposureTolerance` block (L≈1262–1288): append "superseded-as-gate by T_enter; retained as accounting residue bound" note. **§15**: add invariant 21: "Progression and correction gating use the tradability-quantized threshold; ∀Δ the system is either progressing or holding an executable corrective order." | Replace gate constant + Governor state machine |
| **2** | **§10** (L≈810–814): replace the bare `GrossGridEdge(level, bps)` symbol with the closed form `StepBps − α·S/2` and the α definition block; append the α-ceiling arming inequality after the floor definition (L≈830). **§14**: add rows `VolWindow=30s`, `VolHalflife=10min`, `σ_ref=0.25×StepBps`, `α_max=4` (CALIBRATABLE group D), `Spread_eff_bps` (DERIVED, live). | Insert closed form |
| **3** | **§12.1** (after `MaxHedgeCost`, L≈950): add `MaxFundingBleed` bound block (X, β_F=0.02, T_close=180s, r̂_F definition, predictive rule). **§13.2** (L≈998): add `FUNDING_WARN`/`FUNDING_BREAK` overlay states to the state diagram (FROZEN-style overlay line). **§13.4** (L≈1035 closure sequence): add "or FUNDING_BREAK under §12.2" as an emergency-entry antecedent with the net-profit precondition waiver. **§12.2** (L≈980): append "acute risk includes FUNDING_BREAK (decidable detector)." | Add bound + states + entry |
| **4** | **§6.2** (L≈573): reword `cloid (128-bit client order ID, idempotent order identity)` → `cloid (128-bit reconciliation identity; idempotency established via orderStatus, never assumed)`. **§6.3** (L≈578): append the A-2 rounding canon table. **§5.6** (L≈497, N3): replace exact-equality clause with the A-3 ε-overlap predicate. **§10** (L≈825): insert the A-4 precedence rule sentence. **§14**: add `MarginMode ∈ {cross}` (FIXED, A-1). **§15**: append invariants 22–26 (A-0 authority hierarchy, A-5 submission gate, A-6 rate budget, A-9 accumulator idempotency, A-11 freshness). | Rewrite clauses + add invariants |

**Downstream artifact updates (same decisions):** `STRATEGY_CONTRACT.md` §17 additions STR-0345..STR-0352 (one per fix component); `CAPABILITY_COVERAGE.md` rows for the new STRs → CAP-0016 (governor), CAP-0013 (GGE), CAP-0017/CAP-0018 (breaker, closure), CAP-0023 (assertions); `SEMANTIC_AMBIGUITIES.md`: AMB-0014/0033/0023 rows → resolved-by-DECISION-016..019; calibration targets in `CALIBRATION-REPORT.md` gain `{β_F, ε_H, σ_ref, α_max}` (all Group-D calibratable, fail-closed defaults specified above).

---

## 5. Final Consistency Statement

∀ findings {F-1\*, U-1, U-2, U-3..U-8}: ∃ a deterministic, autonomous rule above whose violation set is empty by construction (Fixes 1–3 carry closed-form proofs; Fix 4 reduces each ambiguity to a total entry predicate with a fail-closed else). All proposed constants respect the venue hard limits (AA-4 cap, AA-6 $10 minimum, AA-7 lattice, AA-8 weight budget) and preserve the strategy's own invariants — §4.7 total order, §11.1 precedence, §12.1 three-layer response (the single escalation to automatic closure is anchored in §12.2's explicit risk-precedence clause), and the §16 ordering `T_exit < T_enter < τ_I < one level`. **No logical deadlock, undefined state, or unbounded-loss path remains in the corrected specification; the corrected system is solvable-by-construction under axioms AA-1..AA-14, pending Owner adoption of DECISION-016..019 and the Phase-7 implementation evidence.**
