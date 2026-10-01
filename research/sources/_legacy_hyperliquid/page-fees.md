# Venue source page — Fees (trading)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:44Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0194 (fees / userFees / tiers)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> Fees are based on your rolling 14 day volume and are assessed at the end of each day in UTC. … Referral rewards apply for a user's first $1B in volume and referral discounts apply for a user's first $25M in volume. Maker rebates are paid out continuously …
> `(14d weighted volume) = (14d perps volume) + 2 * (14d spot volume)`. For each user, there is one fee tier across all assets.

> ### Perps fee tiers (Base rate)
> Tier 0: Taker **0.045%**, Maker **0.015%**
> Tier 1 (>5M): Taker 0.040%, Maker 0.012% · Tier 2 (>25M): 0.035% / 0.008% · Tier 3 (>100M): 0.030% / 0.004% · Tier 4 (>500M): 0.028% / 0.000% · Tier 5 (>2B): 0.026% / 0.000% · Tier 6 (>7B): 0.024% / 0.000%. (Staking "Diamond…Wood" columns give further discounts.)

## Evidence status: VERIFIED

- STR-0194 — CONFIRMED verbatim: perps **Tier-0 base = taker 0.045%, maker 0.015%**, matching Strategy §10. Fees are tier-dependent (rolling 14d volume, staking tiers, referral discounts) → confirms "moves with volume tier/staking/promotions" and the requirement to pull the live per-user fee (userFees info endpoint), NEVER hardcode. Maker rebates possible at high tiers (maker can reach 0.000% / negative via staking) — reinforces "never hardcode".
