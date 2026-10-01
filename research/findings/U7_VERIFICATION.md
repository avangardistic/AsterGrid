# U7_VERIFICATION.md — Independent verification of audit finding U-7 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no gate opened; no DECISION created.**
- **Primary sources:** `Strategy.md` §12.1, §14, §16; cached venue evidence (clearinghouseState `leverage.type`, margining).

## 1. Finding (verbatim, SRC-204 §1 / R-8)
> "Margin mode (cross/isolated) never pinned. … the entire D-16 family and `MaxSafeNotional_margin` assume cross-style account-level liquidation (AA-1); in isolated mode `margin_available` is per-position and `liq_price` depends on set leverage … ⇒ the risk model's arithmetic is invalid in the other mode."

## 2. Primary-source extraction
- **§12.1 (Strategy.md L952–956):** `MaxSafeNotional_margin = CapitalBase × Leverage_effective / 2 (D-13; the divisor 2 keeps the margin-account liquidation distance at ≈ half the 3×-leverage distance — see §16's margin mechanics)`.
- **§16 D-16 (L1298–1312):** `MaxExposureImbalance` derivation uses `0.5 / Leverage_effective = MaintenanceMarginFraction` ("maintenance margin = half of initial margin at max leverage [HC]").
- **Whole-file search for a margin-mode pin** (`cross` / `isolated` / `MarginMode` / `leverage.type` as an *account margin mode*): **none.** The only `cross`/`isolated` occurrences are "cross-group overlap" (§5.6) and "isolated fill message" (§4/§6) — unrelated to account margin mode. No §14 parameter row pins the mode; no §15 invariant references it.
- **Venue (`page-perpetuals-info.md`, AA-10):** `clearinghouseState … leverage.type ∈ {cross, isolated}` — the account/position margin mode is a first-class venue state.

## 3. Independent derivation
The risk model's liquidation-distance arithmetic (`d_liq = E₀/N − m`, and `MaxSafeNotional_margin` with divisor 2) presumes **account-level (cross) margin**: `margin_available = account_value − maintenance_margin_required` is an account-level quantity. In **isolated** mode, `margin_available` and `liquidationPx` are per-position and depend on the position's set leverage, so the same formulas yield different liquidation behavior. Strategy.md never fixes which mode the account runs. Two compliant deployments (one cross, one isolated) produce **observably different** liquidation/risk behavior from identical strategy rules. The gap is real and reachable (the venue supports both modes).

## 4. Counter-example search (is it already resolved?)
DECISION-002 pins `clearinghouseState` as the authoritative source but does **not** pin the margin **mode**. DECISION-005/011 (dedicated account) constrain *who* uses the account, not its margin mode. §16's mechanics *assume* max-leverage maintenance behavior but never assert cross vs isolated. **No rule pins the mode** — audit confirmed, not over-generalized.

## 5. Verdict
**U_VERIFIED** — margin mode is never pinned; the D-16 risk arithmetic silently assumes cross, and an isolated-mode account invalidates it. Real and reachable.

## 6. Impact
- affects_str: STR-0223 / STR-0340 (MaxExposureImbalance via maintenance fraction), STR-0225 (MaxSafeNotional_margin), STR-0227 (MaxBasketNotional), STR-0337 (maintenance/max-leverage [HC]).
- affects_cap: CAP-0002 (authoritative venue reads — `leverage.type`), CAP-0017 (risk model), CAP-0020 (config resolution).
- severity: audit **⚠️/U**; independently **HIGH** (silent risk-model invalidation across an entire margin mode).

## 7. Recommendation (PROPOSAL, not a decision)
Pin a FIXED config parameter `MarginMode` (obvious default: cross, matching the risk arithmetic) with a P0 assertion `∀ position: clearinghouseState.assetPositions[].leverage.type == MarginMode`, else FREEZE (audit R-8 family). Justification: one config bit + one assertion removes a whole class of silent model invalidation; because the correct mode is a deployment/owner choice on which the risk arithmetic depends, treat as **SEMANTIC_BLOCKING_PENDING**.
