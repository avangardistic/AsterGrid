# Venue source page — Margining (trading)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:42Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0337 (maintenance=½ initial; mark price), STR-0175 (initial margin), STR-0224 (unrealized pnl as margin / accountValue)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> ### Initial Margin and Leverage
> Leverage can be set by a user to any integer between 1 and the max leverage. **Max leverage depends on the asset.**
> The margin required to open a position is `position_size * mark_price / leverage`.
> Unrealized pnl for cross margin positions will automatically be available as initial margin for new positions …

> ### Maintenance Margin and Liquidations
> Cross positions are liquidated when the account value (including unrealized pnl) is less than the *maintenance margin* times the total open notional position. **The maintenance margin is currently set to half of the initial margin at max leverage.**

## Evidence status: VERIFIED (maintenance=½ initial; mark price) · max-leverage number CONFLICTED (see CONFLICT-001)

- STR-0337 (maintenance = ½ initial at max leverage) — CONFIRMED verbatim.
- STR-0337 (mark price used for margin/liquidation) — CONFIRMED: "margin required … = position_size * mark_price / leverage"; liquidation uses account value incl. unrealized pnl vs maintenance margin.
- STR-0175 (margin) — CONFIRMED (support): initial margin = position_size × mark_price / leverage; buffer is a client-side design addition.
- STR-0224 — CONFIRMED (support): unrealized pnl counts toward cross-account value/margin (consistent with accountValue incl. unrealized pnl).
- STR-0337 (BTC/ETH = 40x) — the number is per-asset and time-varying ("Max leverage depends on the asset"); docs `meta` example shows 50; see CONFLICT-001. Runtime must read live `meta.maxLeverage`.
