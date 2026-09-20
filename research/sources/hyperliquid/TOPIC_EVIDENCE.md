# TOPIC_EVIDENCE.md — venue evidence by topic (Phase 2)

- **Purpose:** Per-topic evidence index mapping each venue topic → the `[HC]` STR targets it serves → authoritative source page(s) (with content hash in SOURCE_MANIFEST.md) → evidence status. Verbatim excerpts live in the `page-*.md` files; this file is the index + status roll-up.
- **Producer:** Claude Code (Opus 4.8), Phase 2.
- **Note (consolidation):** the twelve "per-topic files" required by the phase are consolidated into this single indexed file for context economy; each section below is a self-contained topic record. Interpretation is deferred to Phase 3 (evidence only here).

## T1 — Order lifecycle / fills / orderStatus
- STR: STR-0129, STR-0132, STR-0133 · Sources: page-exchange-endpoint.md, page-info-endpoint.md, page-websocket-subscriptions.md
- Evidence: REST `/exchange` ack statuses `resting`/`filled`/`error`; `orderStatus` info endpoint with full status enum; WS `orderUpdates`; WS `userFills` snapshot-tagged; `userFillsByTime` "only the 10000 most recent fills are available".
- **Status: VERIFIED.**

## T2 — WebSocket semantics
- STR: STR-0129, STR-0133, STR-0200, STR-0228 · Source: page-websocket-subscriptions.md
- Evidence: `orderUpdates`, `userFills` (isSnapshot tag), `clearinghouseState`, `l2Book` (5 fast / 20 slow), `activeAssetCtx` (mark). `webData2` documented as frontend-aggregate; subscription now `webData3`.
- **Status: VERIFIED** (with webData2→webData3 naming NUANCE → CONFLICT-002).

## T3 — Precision (tick & lot)
- STR: STR-0135, STR-0136, STR-0137, STR-0138, STR-0177 · Source: page-tick-and-lot-size.md (+ exchange-endpoint, perpetuals-info)
- Evidence: ≤5 sig figs and ≤(6−szDecimals) decimals for perps; integer prices always valid; sizes rounded to szDecimals (from `meta`); signing removes trailing zeros.
- **Status: VERIFIED.**

## T4 — Account state / clearinghouseState / webData2
- STR: STR-0132, STR-0200, STR-0224 · Source: page-perpetuals-info.md (+ info-endpoint, margining)
- Evidence: `clearinghouseState` gives `assetPositions[].position.szi` (net), `marginSummary.accountValue` (equity incl. unrealized PnL), `withdrawable`; authoritative position/margin.
- **Status: VERIFIED.**

## T5 — cloid / idempotency / nonces
- STR: STR-0133 (cloid), STR-0138 · Sources: page-exchange-endpoint.md, page-nonces-and-api-wallets.md
- Evidence: cloid = optional 128-bit hex id (orderStatus lookup, cancelByCloid). Replay/idempotency of signed actions is enforced by the per-address **nonce set** (100 highest, never-reused, window T−2d…T+1d), NOT by cloid.
- **Status: VERIFIED** (nonce/replay + cloid identity). **cloid duplicate-submission de-dup: PARTIALLY_VERIFIED** (not documented; verify by observation/SDK later).

## T6 — Order types / TIF
- STR: STR-0133 (TIF), STR-0134 (trigger basis) · Sources: page-order-types.md, page-exchange-endpoint.md
- Evidence: TIF `Alo` (post-only, reject-instead-of-cross), `Ioc`, `Gtc` confirmed. Trigger schema `{isMarket,triggerPx,tpsl}`. Trailing-stop & TWAP triggers use **mark price**; stop/take UI direction relative to **mid**; `oracleRejected` shows oracle is a control.
- **Status: VERIFIED (TIF)** · **STR-0134 trigger→oracle-mark: PARTIALLY_VERIFIED** (mark confirmed for trailing/TWAP; "oracle mark for all trigger orders, not last trade" not stated verbatim in fetched pages → CONFLICT-003 note, low impact).

## T7 — Funding
- STR: STR-0337 (funding) · Source: page-funding.md
- Evidence: "funding is paid every hour at one eighth of the computed [8h] rate"; interest 0.01%/8h; capped 4%/hr; funding notional uses **oracle** price.
- **Status: VERIFIED.**

## T8 — Fees / userFees / tiers
- STR: STR-0194 · Source: page-fees.md
- Evidence: perps Tier-0 base taker 0.045% / maker 0.015%; tiered by rolling 14d volume + staking + referrals; pull live per-user fee (userFees), never hardcode.
- **Status: VERIFIED.**

## T9 — Rate limits / open-order cap
- STR: STR-0176 · Source: page-rate-limits.md
- Evidence: default **1000** open orders/user (up to 5000 by volume); at ≥1000 open, reduce-only/trigger orders rejected; IP 1200/min weighted; address-based budget.
- **Status: VERIFIED.**

## T10 — Margin mechanics
- STR: STR-0175 (margin), STR-0337 (maintenance/leverage/mark) · Sources: page-margining.md, page-contract-specifications.md
- Evidence: initial margin fraction = 1/leverage; **maintenance = ½ of initial at max leverage**; margin = position_size × mark_price / leverage; liquidation on account value (incl. unrealized pnl). Max leverage is **per-asset, read live from `meta`**.
- **Status: VERIFIED (mechanics)** · **BTC/ETH "40x" number: CONFLICTED** (docs meta example = 50) → CONFLICT-001.

## T11 — Minimum order size / value
- STR: STR-0175 · Sources: page-exchange-endpoint.md, page-contract-specifications.md
- Evidence: minimum **order value $10** (`minTradeNtlRejected`); max order value tiers by leverage; per-asset min size = $10/price at szDecimals.
- **Status: VERIFIED.**

## T12 — Native TWAP
- STR: STR-0254 · Sources: page-order-types.md, page-exchange-endpoint.md
- Evidence: native TWAP; suborders ≥30s; **≤3% per-suborder slippage**; catch-up capped at 3× normal suborder; $100 min; 5min–7day.
- **Status: VERIFIED.**

## Roll-up (17 [HC] targets)
- **VERIFIED (14):** STR-0129, 0132, 0133, 0135, 0136, 0137, 0138, 0175, 0176, 0177, 0194, 0200, 0224, 0254.
- **PARTIALLY_VERIFIED (2):** STR-0134 (trigger→oracle-mark basis), STR-0228 (l2Book depth bounded ≤20 levels/side vs ±10×StepBps window).
- **CONFLICTED (1):** STR-0337 (funding + maintenance-margin parts VERIFIED; the "BTC/ETH max leverage = 40x" sub-claim conflicts with docs meta example of 50 → CONFLICT-001).
- **SOURCE_UNAVAILABLE (0).**
- Sub-note: STR-0133's "cloid idempotent" and STR-0138's duplicate-submission behavior are PARTIALLY covered (identity yes; dedup-on-duplicate not documented).
