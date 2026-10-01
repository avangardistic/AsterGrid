# Venue source page — Contract specifications (trading)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:43Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0337 (margin fractions, max leverage), STR-0175 (min/max order value), STR-0228 (impact notional)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts (Crypto Perps spec table)

> | Initial margin fraction | 1 / (leverage set by user) |
> | Maintenance margin fraction | Half of maximum initial margin fraction |
> | Mark price | See robust-price-indices |
> | Delivery / expiration | N/A (funding payments every hour) |
> | Funding impact notional | 20000 USDC for BTC and ETH; 6000 USDC for all other assets |
> | Maximum market order value | $30,000,000 for max leverage >= 25, $5,000,000 for max leverage in [20,25), $2,000,000 for [10,20), otherwise $500,000 |
> | Maximum limit order value | 10 * maximum market order value |
> USDC margining, USDT-denominated linear contracts (oracle price in USDT, collateral USDC) — technically quanto; no USDC/USDT conversion applied.

## Evidence status: VERIFIED (margin fractions) · max-leverage number CONFLICTED

- STR-0337 — CONFIRMED: "Maintenance margin fraction = Half of maximum initial margin fraction" and "Initial margin fraction = 1 / leverage". This is the venue basis for the §16 mechanics (maintenance = ½ initial at max leverage).
- STR-0337 (BTC/ETH = 40x) — this page does **not** state a fixed BTC/ETH max leverage; it is per-asset and read from live `meta.maxLeverage` (docs example shows 50). See CONFLICT-001.
- STR-0175 — CONFIRMED (support): venue enforces a **max** market/limit order value tier; the **$10 minimum order value** is on exchange-endpoint.md (`minTradeNtlRejected`).
- STR-0228 — SUPPORT: "Funding impact notional = 20000 USDC for BTC and ETH" is the venue's own book-depth notional for premium; distinct from Strategy's MarketDepth (±10×StepBps window). Note for Phase 3.
