# Venue source page — Info endpoint (SRC-105)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:38Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0132, STR-0133, STR-0134 (support), STR-0176 (rate limit query), STR-0200/0224 (via clearinghouseState — see page-perpetuals-info.md), STR-0228 (l2Book), STR-0194 (userFees — see page-fees.md)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> ### Pagination — Responses that take a time range will only return 500 elements or distinct blocks of data.

> **allMids** — "Note that if the book is empty, the last trade price will be used as a fallback" → mids response `{ "APE":"4.33245", ... }`.

> **openOrders** (type "openOrders") → `[{coin, limitPx, oid, side, sz, timestamp}]`. **frontendOpenOrders** adds `isTrigger, triggerPx, orderType, origSz, reduceOnly, triggerCondition`.

> **userFills** (type "userFills") — "Returns at most 2000 most recent fills". Fill fields: `closedPnl, coin, crossed, dir, hash, oid, px, side, startPosition, sz, time, fee, feeToken, builderFee(optional), tid`.

> **userFillsByTime** (type "userFillsByTime", startTime required) — "Returns at most 2000 fills per response and only the 10000 most recent fills are available".

> **orderStatus** (type "orderStatus", oid = u64 or 16-byte hex cloid) → `{status:"order", order:{ order:{coin,side,limitPx,sz,oid,timestamp,triggerCondition,isTrigger,triggerPx,children,isPositionTpsl,reduceOnly,orderType,origSz,tif,cloid}, status:<status>, statusTimestamp}}` or `{status:"unknownOid"}`. Status values include: open, filled, canceled, triggered, rejected, marginCanceled, tickRejected, minTradeNtlRejected ("order notional below minimum"), perpMarginRejected, badAloPxRejected ("post-only immediate match"), iocCancelRejected, **oracleRejected ("Rejected due to price too far from oracle")**, and others.

> **userRateLimit** (type "userRateLimit") → `{cumVlm, nRequestsUsed, nRequestsCap, nRequestsSurplus}` (address-based request budget).

> **l2Book** (type "l2Book", coin, optional nSigFigs/mantissa) — "Returns at most 20 levels per side" → `{coin,time,levels:[[{px,sz,n},...],[...]]}` (n = number of orders at level).

## Evidence status: VERIFIED (lifecycle/orderStatus/userFills/l2Book) · see cross-refs

- STR-0132 — CONFIRMED (support): authoritative order state via `orderStatus` and position via clearinghouseState (perpetuals-info); userFills alone is a fill record, not position — matches "must confirm the delta".
- STR-0133 — CONFIRMED: `orderStatus` info endpoint exists; `userFills`/`userFillsByTime` exist; **"only the 10000 most recent fills are available" via userFillsByTime CONFIRMS Strategy's "≤10,000 retained"** (userFills itself returns ≤2000 most recent — a per-call limit, not a contradiction).
- STR-0176 — CONFIRMED (partial): address-based request budget queryable via `userRateLimit`; per-account **open-order cap** number (~1000) is on rate-limits-and-user-limits (see page-rate-limits.md).
- STR-0228 — CONFIRMED (with nuance): `l2Book` provides per-level px/sz; **"at most 20 levels per side"** — for tight grids ±(10×StepBps) may span more than 20 levels, so MarketDepth from l2Book is bounded to 20 levels/side. Nuance flagged (not a conflict).
- STR-0134 — SUPPORT: `oracleRejected` ("price too far from oracle") shows the oracle price is a first-class control; trigger-order price basis detail still on order-types/robust-price-indices.
- clearinghouseState (STR-0200/0224) — documented on the perpetuals info subpage; see page-perpetuals-info.md.
