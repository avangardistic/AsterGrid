# CONFLICT-001 — BTC/ETH max leverage: Strategy "40x" vs docs meta example "50x"

- **conflict_id:** CONFLICT-001
- **status:** OPEN (not resolved in Phase 2)
- **claim:** The max leverage of BTC and ETH perps (used in Strategy §16 to derive "initial margin fraction 2.5%, maintenance margin fraction 1.25%").
- **source A (STRATEGY_SOURCE):** `Strategy.md` §16 (STR-0337): "BTC/ETH max leverage = 40x → initial margin fraction 2.5%, maintenance margin fraction 1.25%." Tag `[HC]`.
- **source B (VENUE_PRIMARY_SOURCE):** Hyperliquid docs — info-endpoint/perpetuals `meta` example shows `{"name":"BTC","szDecimals":5,"maxLeverage":50}` and `{"name":"ETH",...,"maxLeverage":50}` (also per-position `maxLeverage:50` in clearinghouseState example). contract-specifications states max leverage is per-asset (no fixed 40/50 in prose).
- **authority_class:** For venue semantics, VENUE_PRIMARY_SOURCE (docs/live `meta`) outranks the Strategy's `[HC]` assumption (`prompt.md` `<source_precedence>`). BUT docs `meta` values in the page are **illustrative examples**, and the true value is the **live** `meta.maxLeverage` at runtime.
- **version/date:** Docs retrieved 2026-09-20; Strategy v2.3-final (SHA 085044e7…).
- **exact_discrepancy:** Strategy asserts 40x for BTC/ETH; docs example shows 50x. Neither the margining nor contract-specifications page fixes a numeric BTC/ETH max leverage — it is per-asset and time-varying.
- **possible_reasons:** (1) Strategy captured a point-in-time value (BTC/ETH max leverage has changed historically, e.g., 50x↔40x); (2) docs example is stale/illustrative; (3) value legitimately differs by date/asset.
- **impact:** **LOW for the runtime formulas.** The §16 dynamic defaults use `Leverage_effective = min(Leverage_user=3, MaxLeverage_asset)`. Since `Leverage_user = 3 < {40,50}`, `Leverage_effective = 3` regardless, so `EmergencyTolerance`, `MaxExposureImbalance`, and margin-distance derivations are UNAFFECTED by 40-vs-50. The "2.5%/1.25%" figures in §16 are illustrative derivation context only. Impact is **documentation/assumption hygiene**, not a computed-value error. Would become material only if `Leverage_user` were raised at/above the asset max.
- **resolution_method:** Read `meta.maxLeverage` **live** at runtime per asset (never hardcode 40 or 50); treat the §16 "40x" as illustrative. Confirm current BTC/ETH value from live `meta` in Phase 8/12. Owner may note the illustrative figure is non-binding.
- **current_status:** OPEN — surfaced to owner; no silent edit to Strategy.md or contract. STR-0337 remains `venue_evidence_status: UNVERIFIED` (funding + maintenance-margin components are verified; the max-leverage number is the open item).
