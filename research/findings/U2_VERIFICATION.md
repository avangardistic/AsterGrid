# U2_VERIFICATION.md — Independent verification of audit finding U-2 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no gate opened; no DECISION created.**
- **Primary sources:** `Strategy.md` §12.1, §13.1; cached venue evidence (funding, AA-4).

## 1. Finding (verbatim, SRC-204 §1 / S-12.5)
> "cumulative funding bleed is *unbounded by any risk bound* — it enters only NET PnL and the (vacuous) DD bound. At the AA-4 cap: wrong-way net N_max × 4%/hr = $1,200/hr = 6% of E₀ per hour."

## 2. Primary-source extraction
- **§12.1 risk bounds (Strategy.md L908–936):** `MaxRangeInducedDD` — "APPROVED value: 100% of Basket equity … reached only when the Basket's equity is fully consumed" (L910–912); `MaxExposureImbalance`; `MaxExecutionCost` — "cumulative **fees+slippage** bound" (L921–922); `MaxHedgeCost` — "cumulative Emergency Hedge cost … 2% of MaxBasketNotional" (L932–933); `MaxFailedLevelRate`. **No bound names funding.**
- **§13.1 (L992–996):** `BasketNetPnL = BasketRealizedPnL + BasketUnrealizedPnL − BasketFees + BasketFunding`; "NET … controls every lifecycle decision (restart target, **freeze trigger**, closure target)"; "funding is not the negligible background cost".
- **Venue (AA-4):** funding paid hourly at ⅛ of the 8h rate; **capped at 4%/hour**; notional = position_size × oracle_price × rate.

## 3. Independent derivation
Funding appears in two places: (i) `BasketNetPnL` (L993) and thence the "freeze trigger" (L996) and the closure target via `TotalSystemCosts` (STR-0246, which lists funding); (ii) nowhere as a **rate-limited protective bound**. The only NET-drawdown bound is `MaxRangeInducedDD = 100%` — which by its own text fires only at equity = 0, i.e. it is **vacuous as a trigger** (independently confirmed: `breach ⟺ equity = 0`, at which point no protective action remains). `MaxExecutionCost` is explicitly fees+slippage (L921), excluding funding. Therefore no bound limits the funding-bleed **rate**. Worst case (independent arithmetic): wrong-way net at `N_max = $30,000` × 4%/hr = **$1,200/hr = 6% of E₀ = $20,000 per hour** ⇒ ~16.7 h to full loss from funding alone. Reproduces the audit exactly.

## 4. Counter-example search (is it already resolved?)
The "freeze trigger" (L996) is NET-governed, so funding *does* feed a freeze decision — **but the trigger's numeric threshold is not defined in the text** (no NET-loss % that fires a freeze before equity = 0; the only DD bound is the vacuous 100%). Under **normal hedge liveness**, net exposure is imbalance-bounded (`|Δ| ≤ MaxExposureImbalance ≈ $208 notional`, STR-0223), so bleed ≈ $8/hr — negligible. The catastrophic path requires the **hedge layer halted / stuck long-lived exposure** (a fail-closed regime). So the gap is **conditional**, not universal: it bites only when the hedge layer cannot correct.

## 5. Verdict
**U_CONDITIONAL** — real, but reachable only under hedge-layer halt / stuck long-lived exposure; under normal hedge liveness funding bleed is imbalance-bounded. No dedicated funding circuit-breaker exists, and the sole NET-DD bound (MaxRangeInducedDD = 100%) is vacuous.

## 6. Impact
- affects_str: STR-0234 (BasketNetPnL incl. funding), STR-0235 (NET governs freeze trigger), STR-0236 (funding non-negligible), STR-0246 (TotalSystemCosts incl. funding), STR-0221/STR-0283 (MaxHedgeCost — does not cover funding).
- affects_cap: CAP-0017 (risk-bound trackers), CAP-0018 (basket lifecycle / freeze), CAP-0016 (hedge).
- severity: audit **U/HIGH**; independently **MEDIUM–HIGH** (conditional on a hedge-halt regime that is itself fail-closed).

## 7. Recommendation (PROPOSAL, not a decision)
Add a funding-bleed protective bound with an owner-chosen threshold (e.g. a rolling-window `FundingBleedRate` breaking to soft-action + escalation), OR make the NET-based freeze trigger's threshold explicit so funding bleed trips a freeze well before equity erosion. Justification: §13.1 itself declares funding "not negligible" yet no bound rate-limits it; the choice of threshold is a risk-appetite decision → **SEMANTIC_BLOCKING_PENDING**.
