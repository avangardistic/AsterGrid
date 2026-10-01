# _HC_TARGETS.md — [HC] venue-claim target list (Phase 2)

- **Purpose:** Working list of every `[HC]` (venue-dependent) requirement in `STRATEGY_CONTRACT.md` that Phase 2 must verify against primary Hyperliquid sources. Grouped by venue topic (many claims share a page).
- **Producer:** Claude Code (Opus 4.8), Phase 2.
- **Inputs:** `STRATEGY_CONTRACT.md` (17 `[HC]` requirements), `Strategy.md` §§6,8,10,11,12,13,16.
- **Status:** working list (evidence gathered in per-topic files + SOURCE_MANIFEST.md).

**Totals:** 17 `[HC]` requirements · 12 unique venue topics.

| STR-* | topic | exact venue claim (verbatim, abridged) | Strategy § |
|-------|-------|----------------------------------------|-----------|
| STR-0129 | order-lifecycle | order state pipeline INTENT→…→FILLED→POSITION_VERIFIED (+CANCELLED/EMERGENCY/SKIPPED/ERROR) | §6.1 |
| STR-0132 | account-state | "No state reaches FILLED from a bare userFills message or REST ack alone — clearinghouseState/webData2 must confirm the delta" | §6.1 |
| STR-0133 | mechanisms/lifecycle/TIF | "cloid (128-bit …) · REST POST /exchange ack (resting/filled/error) · orderStatus · WS orderUpdates · WS userFills · REST userFills/userFillsByTime (≤10,000 retained) · clearinghouseState/webData2 · TIF Gtc/Ioc/Alo" | §6.2 |
| STR-0134 | trigger/oracle-mark | "trigger orders evaluated against oracle mark price, not last trade" | §6.2 |
| STR-0135 | precision | "Prices: ≤5 significant figures and ≤ (MAX_DECIMALS − szDecimals) decimals, MAX_DECIMALS = 6 for perps" | §6.3 |
| STR-0136 | precision | "integer prices always valid" | §6.3 |
| STR-0137 | precision | "Sizes: rounded to the asset's szDecimals (from meta)" | §6.3 |
| STR-0138 | precision | normalization before signing; venue rejects un-normalized orders | §6.3 |
| STR-0175 | min-size/margin | "Order size ≥ asset minimum … Margin available ≥ required initial margin + buffer" | §8 |
| STR-0176 | rate-limits/open-order-cap | "Open-order count has headroom below Hyperliquid's per-account cap (default ~1000 …)" | §8 |
| STR-0177 | precision | gates 7–8: price/size normalized (§6.3) | §8 |
| STR-0194 | fees | "Fee pulled live from userFees — Tier-0 base ≈ taker 0.045%, maker 0.015%, NEVER hardcoded" | §10 |
| STR-0200 | account-state | "ActualExposure := net position from clearinghouseState/webData2 ONLY" | §11.1 |
| STR-0224 | account-state | "CapitalBase = account equity incl. unrealized PnL, from clearinghouseState accountValue" | §12.1 |
| STR-0228 | market-depth/L2 | "MarketDepth = sum of USD bid+ask book depth within ±(10×StepBps) of mid" | §12.1 |
| STR-0254 | TWAP | "native TWAP (parent sliced ≥30s intervals, ≤3% per-suborder slippage)" | §13.4 |
| STR-0337 | margin-mechanics + funding | "Maintenance margin = half of initial margin at max leverage. Funding hourly at 1/8 of 8h rate. BTC/ETH max leverage 40x … Mark price used for margin/liquidation" | §16 |

## Venue topics (grouping)

- **T1 order-lifecycle-fills-orderstatus** → STR-0129, STR-0132, STR-0133 — pages: exchange-endpoint, info-endpoint, websocket/subscriptions.
- **T2 websocket-semantics** → STR-0129, STR-0133, STR-0200, STR-0228 (orderUpdates, userFills, webData2, l2Book) — page: websocket/subscriptions.
- **T3 precision-tick-lot** → STR-0135, STR-0136, STR-0137, STR-0138, STR-0177 — page: tick-and-lot-size.
- **T4 account-state-clearinghouse** → STR-0132, STR-0200, STR-0224 — page: info-endpoint (clearinghouseState).
- **T5 cloid-idempotency-nonces** → STR-0133 (cloid), STR-0138 — pages: nonces-and-api-wallets, exchange-endpoint.
- **T6 order-types-tif** → STR-0133 (TIF), STR-0134 (trigger/oracle-mark) — page: trading/order-types.
- **T7 funding** → STR-0337 (funding hourly 1/8) — page: trading/funding.
- **T8 fees** → STR-0194 — page: trading/fees (+ info userFees).
- **T9 rate-limits-openorder-cap** → STR-0176 — page: rate-limits-and-user-limits.
- **T10 margin-mechanics** → STR-0175 (margin), STR-0337 (maintenance/leverage/mark) — pages: trading/margining, contract-specifications.
- **T11 min-order-size** → STR-0175 — pages: tick-and-lot-size, contract-specifications.
- **T12 native-twap** → STR-0254 — pages: trading/order-types, exchange-endpoint.
