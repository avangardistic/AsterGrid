# U8_VERIFICATION.md — Independent verification of audit finding U-8 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no gate opened; no DECISION created.**
- **Primary sources:** `Strategy.md` §8, §14; cached venue evidence (rate limits, AA-8).

## 1. Finding (verbatim, SRC-204 §1 / R-9)
> "No rate-limit budget. … the pass engine is free to violate AA-8 at >46 full-refresh passes/min."

## 2. Primary-source extraction
- **§8 gate 6 (Strategy.md L746–749):** "Open-order count has headroom below Hyperliquid's per-account cap (`[HC]` default ~1000; reduce-only/trigger orders rejected above that threshold …)". This bounds the **open-order count**, not REST request weight.
- **Whole-file search for a REST weight / request-rate budget** (`1200`, `weight/min`, `rate limit`, pass-cadence budget): **none** in §8 or §14. `EmergencyBoundedWaitSeconds` (§9.1) and `ArmRequestTimeoutSeconds` (§8) are timeouts, not request budgets.
- **Venue (AA-8, `page-rate-limits.md`):** REST 1200 weight/min per IP (`l2Book/allMids/clearinghouseState/orderStatus` weight 2, most info weight 20); WS 10 conns / 1000 subs / 2000 msgs/min / 100 inflight; open-order cap 1000 (→5000 by volume).

## 3. Independent derivation
The strategy specifies no cap on REST request weight per unit time and no pass-cadence bound. A pass that refreshes `clearinghouseState` + `l2Book` + asset contexts costs a fixed weight; at high pass frequency the engine could exceed 1200 weight/min and be throttled by the venue. Two compliant implementations could poll at different cadences (the strategy constrains neither), so one could violate AA-8 while both remain "compliant" with the strategy text. The gap (absence of a budget) is real.

## 4. Counter-example search (is it a semantic gap?)
Gate 6 (open-order cap) is the *only* venue-limit-aware gate; it does **not** cover REST weight. No §15 invariant addresses request rate. However, exceeding the venue limit produces **throttling → stale/missing data**, which the strategy's fail-closed freshness posture (stale gate inputs → gate fails, §8 / STR-0163 depth/freshness) already turns into a safe (blocked) outcome rather than a corruption. So the consequence is degraded liveness, not a strategy-semantic divergence in *decisions*. This is an **operational** rule, resolvable in Phase 6 without an owner semantic decision.

## 5. Verdict
**U_VERIFIED** — no REST rate/weight budget exists (gate 6 covers only open-order count). Real, but an operational concern (throttling → fail-closed), not a strategy-semantic divergence.

## 6. Impact
- affects_str: STR-0176 (gate 6 open-order cap — closest existing), STR-0133 (venue mechanisms relied on).
- affects_cap: CAP-0001 (market observation / polling & subscriptions), CAP-0015 (execution / submission), CAP-0002 (authoritative reads).
- severity: audit **⚠️/U**; independently **MEDIUM** (liveness/operational; fail-closed on staleness limits harm).

## 7. Recommendation (PROPOSAL, not a decision)
Add an operational rate-budget rule (audit R-9 family): per-pass REST weight bounded, pass cadence `≤ 1200·headroom / W_pass`, WS-first substitution for `orderUpdates`/`userFills`/`clearinghouseState` (weight 0). Justification: a deterministic operational policy recordable in Phase 6 with a fail-closed default; no owner strategy-semantic choice required → **SEMANTIC_NON_BLOCKING**.
