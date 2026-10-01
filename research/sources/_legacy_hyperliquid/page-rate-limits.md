# Venue source page — Rate limits and user limits

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:45Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0176 (open-order cap ~1000), plus rate-limit context for STR-0129/0133 lifecycle
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> Each user has a **default open order limit of 1000** plus one additional order for every 5M USDC of volume, **capped at a total of 5000 open orders**. When an order is placed with at least 1000 other open orders by the same user, it will be **rejected if it is reduce-only or a trigger order**.

> REST requests share an aggregated weight limit of **1200 per minute** (per IP). `l2Book, allMids, clearinghouseState, orderStatus` have weight 2; most other info requests weight 20; `userFills`/`userFillsByTime` etc. have additional weight per 20 items returned.
> Address-based limits: 1 request per 1 USDC traded cumulatively since inception; initial buffer 10000 requests; when rate-limited, one request every 10 seconds; cancels have cumulative limit `min(limit+100000, limit*2)`. Applies to actions, not info.
> WebSocket: max 10 connections; 1000 subscriptions; 2000 msgs/min; 100 inflight post messages.

## Evidence status: VERIFIED

- STR-0176 — CONFIRMED verbatim: per-account open-order cap default **1000** (up to 5000 with volume); at ≥1000 open orders, **reduce-only or trigger orders are rejected**. This exactly matches Strategy §8 gate 6, incl. the rationale that exposure caps must preserve headroom for hedge (reduce-only/trigger) orders. Nuance (favorable): the cap can rise to 5000 with volume, so "~1000" is the conservative floor.
