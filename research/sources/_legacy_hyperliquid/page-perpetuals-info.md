# Venue source page — Info endpoint: Perpetuals (meta, assetCtxs, clearinghouseState, funding)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:40Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0137 (szDecimals via meta), STR-0200/0224 (clearinghouseState), STR-0134 (markPx/oraclePx), STR-0337 (maxLeverage, funding), STR-0228 (support)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> **meta** (type "meta") → `{"universe":[{"name":"BTC","szDecimals":5,"maxLeverage":50},{"name":"ETH","szDecimals":4,"maxLeverage":50},{"name":"HPOS","szDecimals":0,"maxLeverage":3,"onlyIsolated":true}, ...], "marginTables":[...]}`.

> **metaAndAssetCtxs** (type "metaAndAssetCtxs") — "includes mark price, current funding, open interest, etc." Per-asset ctx: `{"dayNtlVlm":..., "funding":"0.0000125", "impactPxs":[...], "markPx":"14.3161", "midPx":"14.314", "openInterest":"688.11", "oraclePx":"14.32", "premium":"0.00031774", "prevDayPx":"15.322"}`.

> **clearinghouseState** (type "clearinghouseState", user) — "a user's open positions and margin summary for perpetuals trading" → `{"assetPositions":[{"position":{"coin":"ETH","cumFunding":{...},"entryPx":...,"leverage":{"type":"isolated","value":20,...},"liquidationPx":...,"marginUsed":...,"maxLeverage":50,"positionValue":...,"returnOnEquity":...,"szi":"0.0335","unrealizedPnl":"-0.0134"},"type":"oneWay"}], "crossMaintenanceMarginUsed":"0.0", "crossMarginSummary":{"accountValue":"13104.514502",...}, "marginSummary":{"accountValue":"13109.482328","totalMarginUsed":"4.967826","totalNtlPos":"100.02765","totalRawUsd":"13009.454678"}, "time":..., "withdrawable":"13104.514502"}`.

> **userFunding / fundingHistory** — funding delta `{"coin":"ETH","fundingRate":"0.0000417","szi":...,"type":"funding","usdc":"-3.625312"}`; fundingHistory `{"coin":"ETH","fundingRate":"-0.00022196","premium":"-0.00052196","time":...}`.

## Evidence status: VERIFIED (clearinghouseState, mark/oracle, szDecimals) · CONFLICTED (max leverage)

- STR-0200 — CONFIRMED: net position is `assetPositions[].position.szi` (signed) from clearinghouseState; `marginSummary`/`crossMarginSummary` are authoritative.
- STR-0224 — CONFIRMED: `marginSummary.accountValue` = account equity **including unrealized PnL** (example: accountValue 13109.48 with position unrealizedPnl included; `withdrawable` also given). Matches "CapitalBase = account equity incl. unrealized PnL, from clearinghouseState accountValue".
- STR-0137 — CONFIRMED: `szDecimals` per asset in `meta.universe` (BTC 5, ETH 4).
- STR-0134 — CONFIRMED (support): `markPx` and `oraclePx` are distinct fields in assetCtxs; mark price is a live venue quantity (trigger-order basis detail cross-ref order-types/robust-price-indices).
- STR-0337 (funding) — SUPPORT: funding is delivered as periodic `funding` deltas with a per-interval `fundingRate` (example hourly-scale value 0.0000125); confirm the "hourly, 1/8 of 8h" mechanic on page-funding.md.
- **STR-0337 (max leverage) — CONFLICTED:** Strategy §16 asserts "BTC/ETH max leverage = 40x → initial margin fraction 2.5%". The docs `meta` example shows **BTC/ETH `maxLeverage: 50`** (and per-position `maxLeverage: 50`). Docs examples may be illustrative/stale and the authoritative value is the **live** `meta.maxLeverage` (per-asset, changeable). Recorded as CONFLICT-001; not resolved here. Note: max leverage is per-asset and time-varying — the runtime must read it live from `meta`, never hardcode 40 or 50.
