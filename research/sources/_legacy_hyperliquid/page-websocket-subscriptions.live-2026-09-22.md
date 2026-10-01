# page-websocket-subscriptions — LIVE SNAPSHOT 2026-09-22 (Phase 6a venue refresh)

- **Source URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions.md
- **Fetched:** 2026-09-22 via built-in browser `.md` raw variant.
- **Role:** dated live snapshot for the Phase-6a refresh. The Phase-2 curated extract `page-websocket-subscriptions.md` (SRC-109) is RETAINED unchanged; this file preserves current live evidence alongside it.

## Available WebSocket subscriptions (verbatim list, 2026-09-22)

1. `allMids` (has `dex` param) · 2. `notification` · 3. **`webData3`** (current; WebData2 = frontend aggregate, retained in data-format list) · 4. **`twapStates`** · 5. `clearinghouseState` · 6. `openOrders` · 7. `candle` · 8. `l2Book` (`nSigFigs`,`mantissa`,`fast`; **5 levels if fast, 20 if slow**) · 9. `trades` · 10. `orderUpdates` · 11. `userEvents` (channel name `"user"`; includes fills / funding / liquidation / nonUserCancel) · 12. `userFills` (`aggregateByTime`) · 13. `userFundings` · 14. `userNonFundingLedgerUpdates` · 15. `activeAssetCtx` · 16. `activeAssetData` (Perps only) · 17. **`userTwapSliceFills`** · 18. **`userTwapHistory`** · 19. **`bbo`** · 20. **`spotState`** (`isPortfolioMargin`) · 21. **`allDexsClearinghouseState`** · 22. **`allDexsAssetCtxs`** · 23. **`outcomeMetaUpdates`** · 24. **`fastAssetCtxs`** (base64 + raw DEFLATE/RFC1951 compressed).

## Refresh findings (Phase 6a)

- **New venue capabilities logged (NOT adopted in any design — Phase 6b decides):** `twapStates`, `userTwapSliceFills`, `userTwapHistory`, `bbo`, `fastAssetCtxs`, `allDexsClearinghouseState`, `allDexsAssetCtxs`, `outcomeMetaUpdates`, `spotState`.
- **Snapshot / gap semantics unchanged:** subscription ack provides a snapshot tagged `isSnapshot: true`; streaming user endpoints (`WsUserFills`, `WsUserFundings`) send `isSnapshot: true` first, then `isSnapshot: false` — consistent with DECISION-007 (record decision-affecting events; WS gap → RECONCILIATION_REQUIRED).
- **Authority unchanged:** `WebData2`/`webData3` remain "aggregate information … used primarily for the frontend"; `clearinghouseState` remains the authoritative account/position feed (DECISION-002 intact).
