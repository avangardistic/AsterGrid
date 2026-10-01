# Venue source page — Liquidations (trading)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T19:06Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0337 (maintenance margin, max leverage, mark price for liquidation), supports STR-0134
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> A liquidation event occurs when a trader's positions move against them to the point where the account equity falls below the maintenance margin. The maintenance margin is half of the initial margin at max leverage, **which varies from 3-40x**. In other words, the maintenance margin is between **1.25% (for 40x max leverage assets)** and 16.7% (for 3x max leverage assets) depending on the asset.

> Liquidations use the **mark price**, which combines external CEX prices with Hyperliquid's book state. This makes liquidations more robust than using a single instantaneous book price.

> For liquidatable positions larger than 100k USDC (10k USDC on testnet for easier testing), only 20% of the position will be sent as a market liquidation order … After a block where any position of a user is partially liquidated, there is a cooldown period of 30 seconds.

> If the account equity drops below 2/3 of the maintenance margin without successful liquidation through the book, a backstop liquidation happens through the liquidator vault.

## Evidence status: VERIFIED (maintenance/mark) · corroborates 40x

- STR-0337 — CONFIRMED: "maintenance margin is half of the initial margin at max leverage" and "Liquidations use the mark price". **Critically, the prose states max leverage "varies from 3-40x" and "1.25% (for 40x max leverage assets)"** — this directly CORROBORATES Strategy §16's "BTC/ETH max leverage = 40x → maintenance margin fraction 1.25%", and contradicts the info-endpoint `meta` *example* value of 50 (which is illustrative/stale). See CONFLICT-001 update.
- STR-0134 — SUPPORT: mark price (not last trade) governs liquidation, consistent with mark-price triggering of TP/SL (robust-price-indices).
- Extra venue facts: partial-liquidation threshold 100k USDC (10k testnet); backstop at 2/3 maintenance; 30s cooldown.
