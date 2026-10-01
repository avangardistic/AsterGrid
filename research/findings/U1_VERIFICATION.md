# U1_VERIFICATION.md — Independent verification of audit finding U-1 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no gate opened; no DECISION created.**
- **Primary sources:** `Strategy.md` (SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`, unmodified) §10; cached venue evidence (fees).

## 1. Finding (verbatim, SRC-204 §1)
> "`GrossGridEdge` — the variable that governs the binding economics gate — **has no closed-form definition** (single symbolic occurrence, L812). No … The gate that binds *all* arming is not computable from the strategy text."

## 2. Primary-source extraction
- **§10 (Strategy.md L810–819):** `NetExpectedEdge(path) := GrossGridEdge(level, bps) − Fee(path) − EstimatedSlippage(path) − FundingCostEstimate(holding_period) − OtherExecutionCosts(path)`.
- **§8 gate 10 (L752–754):** arming requires `NetExpectedEdge > NetExpectedEdgeFloor (approved default StepBps/10 = 1 …)`.
- **§10 floor (L827–830):** `NetExpectedEdge ≤ floor (either path) → do not arm / do not attempt`.
- `NetExpectedEdgeFloor` is defined (§14 L1143, `StepBps/10 = 1`, CALIBRATABLE). **`GrossGridEdge` is defined nowhere:** a whole-file search returns exactly one occurrence, L812 — used, never given a closed form or a §14 row.

## 3. Independent derivation
`NetExpectedEdge` is the sole binding economics quantity (gate 10, §9.1, §11.2 non-acute). It is a total function of five terms; four are defined (Fee live from userFees; EstimatedSlippage from the Fillability Analyzer §8; FundingCostEstimate; OtherExecutionCosts) but **`GrossGridEdge` is a free symbol**. Two compliant implementations could pick materially different closed forms — e.g. `GGE := StepBps` (a flat one-step capture, consistent with D-06's `StepBps_as_USD` and the `StepBps/10` floor) vs `GGE := (P_terminal − P_k)/P_terminal × 10⁴` (per-level distance-to-terminal) — yielding different per-level arming decisions. The divergence is observable at the arming gate for any level whose distance-to-terminal ≠ StepBps. This violates the document's own determinism standard (§15 inv.19 reconstructability presumes a computable decision).

## 4. Counter-example search (is it already resolved?)
Searched §10, §14, §7.1, §16 for any definition of `GrossGridEdge`, `GrossEdge`, or an equivalent one-step-capture formula. **None found.** D-06's `StepBps_as_USD = StepBps × MaxBasketNotional / 10000` (§13.4, STR-0245) *implies* a one-step economics unit but is scoped to the closure target, not the arming edge, and is never linked to `GrossGridEdge`. No §15 invariant defines it. The audit did **not** over-generalize here: the gap is a genuine absence.

## 5. Verdict
**U_VERIFIED** — the binding economics gate depends on an undefined term; two compliant implementations diverge observably at arming.

## 6. Impact
- affects_str: STR-0193 (NetExpectedEdge formula), STR-0179 (gate 10 Cost Analyzer), STR-0197 (floor either-path), STR-0273 (NetExpectedEdgeFloor).
- affects_cap: CAP-0013 (execution economics / cost analyzer), CAP-0011 (arm gating).
- severity: audit rates **U/HIGH** ("single largest indeterminacy"); independently confirmed HIGH — it gates all arming.

## 7. Recommendation (PROPOSAL, not a decision)
Give `GrossGridEdge` a closed form recorded as an owner decision — the smallest fail-closed-safe choice being `GGE := StepBps` (consistent with the existing StepBps-denominated floor and D-06), with any candidate required to satisfy `GGE − 2·fee_maker − funding_est > NetExpectedEdgeFloor` at Tier-0 fees. Justification: a binding gate must be computable and replay-deterministic; leaving the symbol free is the document's largest arming indeterminacy. **Owner-relevant (a definition choice) → treat as SEMANTIC_BLOCKING_PENDING.**
