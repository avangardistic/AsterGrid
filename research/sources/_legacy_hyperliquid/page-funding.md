# Venue source page — Funding (trading)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:41Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0337 (funding hourly, 1/8 of 8h)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> The funding rate on Hyperliquid is paid every hour.
> The funding rate formula applies to 8 hour funding rate. However, **funding is paid every hour at one eighth of the computed rate for each hour**.
> `Funding Rate (F) = Average Premium Index (P) + clamp(interest rate - Premium Index (P), -0.0005, 0.0005)`. The premium is sampled every 5 seconds and averaged over the hour.
> interest rate component is predetermined at 0.01% every 8 hours, which is 0.00125% every hour …
> Funding on Hyperliquid is capped at 4%/hour … The funding cap and funding interval do not depend on the asset.
> Note that the funding payment at the end of the interval is `position_size * oracle_price * funding_rate`. In particular, the **spot oracle price** is used to convert the position size to notional value, *not the mark price*.

## Evidence status: VERIFIED

- STR-0337 (funding part) — CONFIRMED verbatim: "funding is paid every hour at one eighth of the computed rate" = Strategy's "Funding is paid hourly, at 1/8 of the 8-hour funding rate."
- Complementary nuance (not a conflict): funding notional uses the **oracle price**, whereas Strategy §16's "mark price used for margin accounting and liquidation" concerns margin/liquidation, a different mechanism. Both hold.
