# U6_VERIFICATION.md — Independent verification of audit finding U-6 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no gate opened; no DECISION created.**
- **Primary sources:** `Strategy.md` §13.4, §6.3; cached venue evidence (min value, szDecimals).

## 1. Finding (verbatim, SRC-204 §1 / S-13.3)
> "`round_to_min_tradable_size` has **no defined rounding direction**: ceil ⇒ τ_R = q_min (feasible …); floor/nearest-⇓ ⇒ τ_R = 0 ⇒ closure demands *exact* szi = 0 … Two implementations, two closure boundaries."

## 2. Primary-source extraction (§13.4, Strategy.md L1034–1048)
> "(b) residual ActualExposure ≤ `ResidualExposureToleranceAtClosure`. Approved form (§14 D-07): `ResidualExposureToleranceAtClosure := round_to_min_tradable_size( f(StepBps, MaxBasketNotional) )`. Functional form (D-07(F)): `f := (StepBps × MaxBasketNotional / 10000) / GridLevels` … resolved onto the asset's minimum-tradable-size grid (szDecimals, §6.3). **Exact zero may be unreachable given szDecimals rounding**; this derivation is the motivation for a small non-zero tolerance. Worked example (defaults; BTC at 100,000, szDecimals = 5): `f = (10 × 30,000 / 10000)/6 = 5 USD → 0.00005 BTC`."

`round_to_min_tradable_size` direction (ceil / floor / nearest) is **not specified** here, in §6.3 (L578, "Sizes: rounded to the asset's szDecimals" — no direction for this tolerance), or in §14 (STR-0248 / STR-0290 restate the formula, no direction).

## 3. Independent derivation
`f` need not be an exact multiple of the lot. If `f` falls below one lot or between lot multiples:
- **ceil** ⇒ `τ_R ≥ 1 lot` ⇒ after a final min-size sweep `szi → 0` exactly (venue szi is exact) ⇒ closure feasible in one order;
- **floor / nearest-down** where `f < 1 lot` ⇒ `τ_R = 0` ⇒ closure precondition demands **exact `szi = 0`** (strictest).
Two compliant implementations pick different closure boundaries ⇒ observable difference in when a Basket may CLOSE. Confirmed.

## 4. Counter-example search (audit over-generalization check)
**At the DEFAULT scenario the gap is MOOT:** `f = $5 = 0.00005 BTC = exactly 5 lots` (lot = 10⁻⁵ BTC), so any reasonable rounding returns 0.00005 exactly — ceil = floor = nearest. The direction only matters when `f` is **not an exact lot-multiple** (e.g. StepBps = 7, MaxBasketNotional = 30,000 → `f = 21/6 = $3.50 = 3.5 lots` → 3 vs 4 lots by direction). So the audit's "two implementations, two boundaries" is **conditional**, not universal — it does not bite at the shipping default.

## 5. Verdict
**U_CONDITIONAL** — real when `f` is not an exact multiple of the lot; moot at the D-16 default (`f = 5 lots` exactly). Rounding direction genuinely undefined.

## 6. Impact
- affects_str: STR-0248 / STR-0290 (ResidualExposureToleranceAtClosure = round_to_min_tradable_size(f)), STR-0247 (precondition b), STR-0303 (Basket CLOSED requires verified residual within tolerance).
- affects_cap: CAP-0018 (basket closure), CAP-0013 (precision / rounding).
- severity: audit **⚠️/U**; independently **LOW–MEDIUM** (conditional; safe-direction fix is obvious).

## 7. Recommendation (PROPOSAL, not a decision)
Fix the direction to **ceil**, floored at one lot: `τ_R := max(ceil_lot(f), 1 lot)` (audit R-7 family). Justification: ceil guarantees the closure precondition is satisfiable (a final min-size sweep drives szi to exact 0) and avoids demanding unreachable exact zero; the direction is an obviously-correct deterministic choice recordable without owner authority → **SEMANTIC_NON_BLOCKING**.
