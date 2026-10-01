# Venue source page — API overview (SRC-103) + docs index (SRC-101/SRC-102)

- **URLs:**
  - SRC-101 docs root: https://hyperliquid.gitbook.io/hyperliquid-docs/
  - SRC-102 llms.txt index: https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt
  - SRC-103 API overview: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:33–18:48Z (built-in browser). The docs root renders the same navigable index as llms.txt (a Markdown list of every doc page, each with a `.md` raw variant).
- **Serves:** navigation to all [HC] target pages; confirms official SDK + base URLs (testnet).
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts (API overview)

> # API — Documentation for the Hyperliquid public API
> Python SDK: https://github.com/hyperliquid-dex/hyperliquid-python-sdk
> Rust SDK (community, Infinite Field): https://github.com/infinitefield/hypersdk
> Typescript SDKs (community): github.com/nktkas/hyperliquid ; github.com/nomeida/hyperliquid
> CCXT integrations: docs.ccxt.com/#/exchanges/hyperliquid
> All example API calls use the mainnet url (https://api.hyperliquid.xyz), but you can make the same requests against **testnet** using the corresponding url (https://api.hyperliquid-testnet.xyz)

## Key developer/API pages discovered in llms.txt (for-developers/api/*):

notation · asset-ids · **tick-and-lot-size** · **nonces-and-api-wallets** · **info-endpoint** (+ perpetuals, spot) · **exchange-endpoint** · **websocket** (subscriptions, post-requests, timeouts-and-heartbeats) · error-responses · **signing** · **rate-limits-and-user-limits** · activation-gas-fee · optimizing-latency · priority-fees · usdc.
Trading pages: **fees**, **funding**, **order-types**, **contract-specifications**, **margining**, robust-price-indices, liquidations, order-book, self-trade-prevention.

## Evidence status: VERIFIED (navigation + SDK URL + testnet base URL)

- Official Python SDK URL CONFIRMED (see SDK_RECORD.md).
- Testnet uses the same API surface at `https://api.hyperliquid-testnet.xyz` (relevant to Strategy runtime-mode/testnet handling; Phase 12).
- Community SDKs exist (Rust/TS/CCXT) — recorded for completeness; none is a venue authority.
