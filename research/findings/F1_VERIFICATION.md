# F1_VERIFICATION.md — Independent verification of audit finding F-1\* (Phase 4.7 Part C)

- **Purpose:** Re-derive the F-1\* "livelock cell" claim from `strategy_audit.md` (SRC-204) **from first principles** against `Strategy.md` (immutable authority) and the cached venue evidence — WITHOUT trusting the audit's arithmetic. Record the verified result. **No fix is applied; no Owner Gate is opened; no DECISION is created.**
- **Producer:** Claude Code (Opus 4.8), Phase 4.7.
- **Primary sources:** `Strategy.md` (SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`, unmodified) · `research/sources/hyperliquid/page-exchange-endpoint.md` · `page-contract-specifications.md` · `page-perpetuals-info.md` · `page-tick-and-lot-size.md`.
- **Line references** are to `Strategy.md` v2.3-final (1-based).

---

## C.1 — F-1\* restated formally (verbatim scope, no interpretation)

From SRC-204 §1 and §3 (S-5.3): the D-16 `ExposureTolerance` default (`$5` notional-equivalent at defaults) is provably **below the venue's `$10` minimum order value for ∀ MarkPrice > 0**, creating a reachable dead-band `δ ∈ (τ_E, q_min)` that simultaneously **blocks grid progression** (§5.2/§11.1) and is **un-correctable by any order** (venue rejects value `< $10`) — a livelock cell in state space. "Conditional because D-16 is `[DYNAMIC — CALIBRATION PENDING]`."

Formal objects:
- `τ_E := ExposureTolerance` (D-16), unit = base-asset quantity.
- `q_min(M) := $10 / M` = minimum tradable order quantity (base-asset), `M := MarkPrice`.
- `dead-band := { δ > 0 : τ_E < δ < q_min }`.
- `livelock cell := ∃ reachable δ in dead-band such that (i) progression blocked (|Δ| > τ_E) ∧ (ii) no executable corrective order exists (|Δ| < q_min) ∧ (iii) δ persists indefinitely`.

---

## C.2 — τ_E verified from Strategy.md (primary source)

**§5.2 / §11.1 — the progression gate.** The exposure gate is stated in the §11 priority ladder (L852–862):

> "HEDGE RECOVERY … ↓ only once **|ExposureDelta| ≤ ExposureTolerance** … GRID EXECUTION → GENERATION EVOLUTION → CYCLE CREATION" (L856–861)

and reinforced (L864): *"Grid progression is **hard-gated** on exposure being within tolerance — not a soft preference."* `ExposureDelta` is defined (L846): `ExposureDelta := ExpectedExposure − ActualExposure`.

- **Gate predicate:** progression permitted ⟺ `|ExposureDelta| ≤ ExposureTolerance`; **blocked ⟺ `|ExposureDelta| > τ_E`**. Boundary is **inclusive `≤`** (equality → permitted).

**§14 Parameter Reference (L1158)** — `ExposureTolerance` row:
> "`(0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice`, NotionalPerLevel = MaxBasketNotional / GridLevels — e.g. **0.00005 BTC** at defaults | **base-asset quantity** | §5.2/§11.1 (D-09 A → D-16) | … | **[DYNAMIC — CALIBRATION PENDING]**"

**§16 D-16 block (L1267–1293)** — exact formula and unit:
> "`ExposureTolerance := (0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice` where `NotionalPerLevel := MaxBasketNotional / GridLevels`. **Unit: base-asset quantity** … Worked example (defaults): BTC at MarkPrice = 100,000 USD, StepBps = 10, MaxBasketNotional = 30,000 USD, GridLevels = 6 → NotionalPerLevel = 5,000 USD → **ExposureTolerance = 0.001 × 5,000 / 100,000 = 0.00005 BTC**."

- **Used once → binding:** §14 global rule (formulas resolved once → owner-confirmed → binding). `ExposureTolerance` carries the live `MarkPrice` input, so its base-asset value tracks price; its **notional** value (`τ_E × M`) is price-invariant.
- **Quantization / floor applied to τ_E or ExposureDelta before the gate?** Searched §5.2, §11.1, §16, §14: **none found.** `§6.3` szDecimals rounding applies to *order sizes at build time*, never to the `ExposureDelta ≤ τ_E` comparison. τ_E is emitted at full precision (0.00005 BTC), not `ceil`/`floor`-ed onto the lot grid. → "**no such rule**."

**Independent computation (audit default scenario):** StepBps = 10, NotionalPerLevel = 30,000 / 6 = 5,000, M = 100,000:
```
τ_E = (0.001 × 10/10) × 5,000 / 100,000 = 0.001 × 0.05 = 0.00005 BTC
    = $5.00 notional  (0.00005 × 100,000)
    = 5 lots  (lot = 10^-5 BTC = $1 at M=100,000)
```
**Agreement with audit:** exact (`τ_E = $5`). **Discrepancy with Strategy.md prose:** L1289–1290 calls `0.00005 BTC` "one minimum-lot equivalent" — it is in fact **5 lots** (`5 × 10^-5`). This is a wording imprecision in the immutable text (not modified here); the numeric value 0.00005 BTC is unambiguous and is what the gate uses.

---

## C.3 — q_min verified from venue evidence (primary source)

**`page-exchange-endpoint.md` L21** (order response statuses, verbatim venue error):
> `{"error":"Order must have minimum value of $10."}`

**L29:** "STR-0175 — CONFIRMED (partial): venue enforces a **minimum order value of $10** (error string). Per-asset minimum *size* derives from `$10 / price` at szDecimals." **`page-contract-specifications.md` L24:** "the **$10 minimum order value** is on exchange-endpoint.md (`minTradeNtlRejected`)."

- **Threshold:** minimum order **value = $10 USD**.
- **Scope:** the order-action schema (`page-exchange-endpoint.md` L19) is common to all order kinds; `reduceOnly` (`r`) is a flag on that same schema → the `$10` minimum applies to entry, correction, and reduce-only orders alike. No order-type exemption is documented.
- **Hard reject or soft warning:** **hard reject** — a `200 OK` body carrying `{"error": …}` (the order is not placed).
- **Reducible by tier / HIP-3 / testnet?** Not for the main perpetual dex: `$10` is the documented mainnet minimum with no tier reduction. HIP-3 *builder dexes* are separate assets (out of BTC/ETH scope). Not relied upon here.
- **szDecimals (for the lot grid):** `page-perpetuals-info.md` L11/L23 — `meta.universe` gives **BTC szDecimals = 5** (lot = 10^-5 BTC), ETH szDecimals = 4. Confirmed current in cached meta.

**Independent computation (default scenario):** `q_min(M) = $10 / M = 10 / 100,000 = 0.0001 BTC = 10 lots` at M = 100,000. **Agreement with audit:** exact.

---

## C.4 — The inequality τ_E < q_min, verified symbolically and across the grid

```
τ_E(M)   = k1 · NotionalPerLevel / M ,   k1 = 0.001 · (StepBps/10)
q_min(M) = k2 / M ,                        k2 = $10  (MIN_ORDER_VALUE)
```
Both scale as `1/M`, so `M` cancels: **the comparison is MarkPrice-invariant.**
```
τ_E < q_min  ⟺  k1 · NotionalPerLevel < k2
             ⟺  0.001 · (StepBps/10) · (MaxBasketNotional/6) < 10
             ⟺  StepBps · MaxBasketNotional < 600,000
```
**Key structural fact (independent of the audit): the D-16 τ_E formula contains NO `Leverage_effective` term.** Leverage therefore does not enter τ_E directly; it enters only through `MaxBasketNotional` (D-13, §12.1). So the grid below is parameterised by (StepBps, MaxBasketNotional); leverage is folded into MaxBasketNotional. `GridLevels = 6` (FIXED).

τ_E notional = `0.001 · (StepBps/10) · (MaxBasketNotional/6)`; q_min notional = `$10` (constant).

| StepBps | MaxBasketNotional | NotionalPerLevel | τ_E ($) | q_min ($) | τ_E < q_min? |
|--------:|------------------:|-----------------:|--------:|----------:|:-----------:|
| 5  | 30,000 | 5,000    | 2.50  | 10 | **Y** |
| 10 | 30,000 | 5,000    | 5.00  | 10 | **Y** (audit default) |
| 20 | 30,000 | 5,000    | 10.00 | 10 | **N** (τ_E = q_min → band empty) |
| 5  | 50,000 | 8,333.33 | 4.17  | 10 | **Y** |
| 10 | 50,000 | 8,333.33 | 8.33  | 10 | **Y** |
| 20 | 50,000 | 8,333.33 | 16.67 | 10 | **N** (τ_E > q_min → band empty) |

**Cases with τ_E ≥ q_min (F-1\* NOT present), as the prompt requires flagging:** `StepBps = 20, MaxBasketNotional = 30,000` (equal) and `StepBps = 20, MaxBasketNotional = 50,000` (τ_E > q_min). Therefore **F-1\* is NOT universal across the calibration grid** — it holds precisely when `StepBps · MaxBasketNotional < 600,000`.

---

## C.5 — Reachability of the dead-band

Assume `τ_E < q_min` (holds at defaults).

- **(a) Quantize ExposureDelta/ExpectedExposure to a lot before the gate?** No rule in §5.2 or §11.1 does this. `ExposureDelta` (L846) is compared directly to τ_E (L858). → **no such rule.**
- **(b) Round τ_E to a lot / min-tradable?** No. The D-16 formula (L1268) emits 0.00005 BTC at full precision; no `ceil`/`floor`. (The derivation *mentions* τ_E "tolerates the szDecimals rounding residue," L1276, but does not round τ_E.) → **no such rule.**
- **(c) "if |Δ| < min-tradable then Δ := 0"?** No such round-to-zero rule exists in the strategy text. (It exists only as the audit's *proposed* fix R-1, SRC-204 §5 — not adopted.) → **no such rule.**
- **(d) Partial-fill path (defaults; resting $5,000 limit, BTC szDecimals = 5, lot = 0.00001 BTC = $1):** venue fills are lot-multiples, so an exposure residual `|Δ|` is a lot-multiple ⇒ `|Δ| ∈ {$1,$2,…}`. The dead-band `(τ_E, q_min) = ($5, $10)` contains the reachable lot points **$6, $7, $8, $9** (0.00006–0.00009 BTC). For each:
  - **(i) reachable by partial fills** — yes; a fill/hedge-leg asymmetry (one leg fills, the mirror/correction leg over- or under-fills by 6–9 lots) leaves exactly such a residual `Δ = Expected − Actual`.
  - **(ii) blocks progression** — yes; `$6…$9 > τ_E = $5` ⇒ gate blocked (L858/L864).
  - **(iii) un-correctable** — yes; a correction order of 0.00006–0.00009 BTC has value $6–$9 `< $10` ⇒ venue rejects "Order must have minimum value of $10." (C.3).
  → **4 reachable, blocking, un-correctable lot points at the default scenario** (exact agreement with the audit's $6/$7/$8/$9).
- **(e) Other paths to the dead-band:** funding (settles in USDC; **does not change szi** — AA-4/AA-10), fees (**no szi change**), unrealized PnL (**no szi change**), position transfer (**excluded** by DECISION-005 dedicated account), liquidation (**different failure mode** — a large szi change, not a small residual). ⇒ **Only the fill/hedge-sequencing path (e, above (d)) can place `|Δ|` in the dead-band.** This sharpens the finding: F-1\* is specifically a *fill-sequencing* dead-band, not a funding/fee/PnL artefact.
- **(f) Current documented szDecimals for BTC:** **5** (`meta.universe`, C.3). (If szDecimals were smaller the lot would be coarser, but the `$10` minimum is value-based, so the dead-band in value terms is unchanged.)

---

## C.6 — Persistence of the state

Assume `|Δ| ∈ dead-band`. Exit mechanisms searched in `Strategy.md`:
- **Timer-based reset of Δ:** none declared — `Δ` is recomputed each pass from `Expected − Actual`; it does not decay.
- **Reconciliation with clearinghouseState:** re-reads authoritative `szi`; it does **not** reduce `Δ` by itself. Here `Expected` and `Actual` are each correct, stable lot-multiples differing by the dead-band residual ⇒ reconciliation confirms the *same* `Δ` ⇒ `Δ` persists. (DECISION-014 auto-resume from `RECONCILIATION_REQUIRED` fires "on successful reconciliation," but reconciliation cannot remove a residual the venue forbids trading away ⇒ no auto-clear.)
- **Operator intervention:** would require a human action outside normal correction, and even an operator cannot place a `< $10` order to flatten the residual — they would have to *add* exposure to lift `|Δ| ≥ $10` then flatten, or accept a (non-existent) round-to-zero rule. Not an autonomous exit.
- **Safety criticality:** the dead-band is **not a safe rest state** — while it holds, a *subsequent acute hedge* of small size (`|Δ| < $10`) is **also** un-executable under the same `$10` minimum, so the cell can block safety-critical exposure corrections, not merely progression.

→ **The state persists** at the default scenario; no rule in the strategy text clears it autonomously.

---

## C.7 — Independent worst-case table (D-13 §12.1 formula, primary source)

`MaxBasketNotional := min( L_eff·CapitalBase·(1−HedgeReserveRatio), CapitalBase·L_eff/2, k_liquidity·MarketDepth )` (Strategy.md L941–952; worked example L970–974). Constants per the prompt / §12.1 example: `CapitalBase E₀ = 20,000`, `HedgeReserveRatio = 0.10`, `k_liquidity = 0.10`, `MarketDepth = 500,000`, `M = 100,000`. Binding term shown in brackets.

| L_eff | MaxBasketNotional (binding term) | NPL | StepBps | τ_E ($) | q_min ($) | band = q_min−τ_E ($) | band (lots) | reachable dead-band pts | F-1\*? |
|------:|------------------:|----:|-------:|-----:|----:|-----:|----:|:--|:--:|
| 2 | 20,000 (margin ½) | 3,333.3 | 5  | 1.67 | 10 | 8.33 | 8.3 | $2…$9 (8) | **Y** |
| 2 | 20,000 | 3,333.3 | 10 | 3.33 | 10 | 6.67 | 6.7 | $4…$9 (6) | **Y** |
| 2 | 20,000 | 3,333.3 | 20 | 6.67 | 10 | 3.33 | 3.3 | $7,$8,$9 (3) | **Y** |
| 3 | 30,000 (margin ½) | 5,000   | 5  | 2.50 | 10 | 7.50 | 7.5 | $3…$9 (7) | **Y** |
| 3 | 30,000 | 5,000   | 10 | 5.00 | 10 | 5.00 | 5.0 | $6,$7,$8,$9 (4) | **Y** (audit default) |
| 3 | 30,000 | 5,000   | 20 | 10.00| 10 | 0.00 | 0.0 | none | **N** |
| 5 | 50,000 (margin ½ = depth) | 8,333.3 | 5  | 4.17 | 10 | 5.83 | 5.8 | $5…$9 (5) | **Y** |
| 5 | 50,000 | 8,333.3 | 10 | 8.33 | 10 | 1.67 | 1.7 | $9 (1) | **Y** |
| 5 | 50,000 | 8,333.3 | 20 | 16.67| 10 | −6.67| — | none | **N** |

(lot value = `M·10^-5 = $1` at M = 100,000, so band-in-lots ≈ band-in-$.) **Zero/negative-width (F-1\* absent):** the two `StepBps = 20` rows at NPL ≥ $5,000 (L_eff 3 and 5). F-1\* is present in 7 of these 9 representative sets and absent in 2.

---

## C.8 — Verdict

**Verdict: `F1_CONDITIONAL`.**

- **Confirmed where it exists:** at the audit's **default scenario** (`StepBps = 10`, `MaxBasketNotional = 30,000`, `L_eff = 3`): independently re-derived `τ_E = $5 < q_min = $10`, MarkPrice-invariant; the dead-band `($5,$10)` contains the reachable, blocking, un-correctable lot points **$6/$7/$8/$9**; and **no round-to-zero, no gate-quantization, and no min-size escape rule exists in `Strategy.md`** (C.2b/c, C.5a–c). The state **persists** (C.6). The audit's arithmetic is reproduced **exactly**, from primary sources, with zero discrepancy. Within its region the cell is a genuine, safety-relevant livelock (**blocking**).
- **Why CONDITIONAL, not universal:** per the prompt's own criterion (C.4: "if ANY combination has τ_E ≥ q_min … F-1\* is conditional, not universal"), the grid shows `τ_E ≥ q_min` at `StepBps = 20` with `MaxBasketNotional ≥ 30,000` (τ_E = $10 = q_min, then τ_E = $16.67 > q_min) ⇒ the dead-band is empty there. **Boundary condition:** F-1\* is present **iff `StepBps · MaxBasketNotional < 600,000`** (equivalently `τ_E_notional = 0.001·(StepBps/10)·(MaxBasketNotional/6) < $10`). The audit's "∀ MarkPrice > 0" universality is correct **over price** (the inequality is MarkPrice-invariant); it is **not** universal **over the (StepBps, MaxBasketNotional) calibration space**.

**Nuance vs the audit:** the audit already scoped F-1\* to the D-16 *defaults* and flagged it "Conditional because D-16 is `[DYNAMIC — CALIBRATION PENDING]`." My independent result agrees on the substance (real, reachable, persistent livelock at defaults) and adds the precise parameter boundary (`StepBps·MaxBasketNotional < 600,000`) at which the cell disappears. No contradiction with the audit's arithmetic was found.

**Recommendation (NOT executed in this run):** a **narrower Owner Gate** — scoped to the calibration region `StepBps · MaxBasketNotional < 600,000` — should be opened to decide whether to (i) add a tradability-quantized gate / round-to-zero rule (audit R-1 family), or (ii) constrain calibration so `τ_E ≥ q_min` always. **This run opens no gate, creates no DECISION, applies no fix.** The finding is recorded in [`F1_SEMANTIC_RECORD.md`](F1_SEMANTIC_RECORD.md) as AMB-0047, status VERIFIED_BLOCKING (blocking within its region, which includes the shipping default), pending an Owner decision.

---

*Verification complete. No repository file other than the Phase-4.7 findings/manifest/README was created or modified. `Strategy.md` re-verified byte-identical (SHA-256 `085044e7…a825e18`).*
