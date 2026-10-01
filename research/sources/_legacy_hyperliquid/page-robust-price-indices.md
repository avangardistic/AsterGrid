# Venue source page — Robust price indices (trading)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T19:05Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0134 (trigger basis), STR-0337 (mark price for margin/liquidation), supports STR-0132/0200
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> *Oracle price* is used to compute funding rates. This weighted median of CEX prices is robust because it does not depend on hyperliquid's market data at all. Oracle prices are updated by the validators approximately once every three seconds.

> *Mark price* is the median of the following prices:
> 1. Oracle price plus a 150 second exponential moving average (EMA) of the difference between Hyperliquid's mid price and the oracle price
> 2. The median of best bid, best ask, last trade on Hyperliquid
> 3. Median of Binance, OKX, Bybit, Gate IO, MEXC perp mid prices with weights 3, 2, 2, 1, 1, respectively

> Mark price is an unbiased and robust estimate of the fair perp price, and is used for **margining, liquidations, triggering TP/SL, and computing unrealized pnl**. Mark price is updated whenever validators publish new oracle prices … approximately once every 3 seconds.

## Evidence status: VERIFIED (trigger basis = mark price, not last trade)

- STR-0134 — **RESOLVED / CONFIRMED**: trigger orders (TP/SL) are triggered by **mark price**, explicitly not by last trade alone. Terminology reconciliation: the venue distinguishes **oracle price** (funding only) from **mark price** (margining, liquidations, TP/SL triggering, uPnL). Strategy's phrase "oracle mark price" maps to the venue's **mark price**, which is a robust median that *includes* an oracle-derived component (input 1) plus book/CEX inputs. The operative claim — "evaluated against [mark], not last trade" — is unambiguously confirmed. (Note: "last trade" is only 1 of 3 medianed inputs to mark, never the sole basis.)
- STR-0337 — CONFIRMED (support): "Mark price … is used for margining, liquidations … and computing unrealized pnl" corroborates page-margining.md; oracle price (not mark) is used for funding, consistent with page-funding.md.
