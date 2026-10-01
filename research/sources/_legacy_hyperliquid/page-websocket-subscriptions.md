# Venue source page — WebSocket subscriptions

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:46Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0129 (order lifecycle), STR-0133 (orderUpdates/userFills snapshot-tag), STR-0200 (clearinghouseState WS), STR-0228 (l2Book WS)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> The subscription ack provides a snapshot of previous data for time series data (e.g. user fills). These snapshot messages are tagged with `isSnapshot: true` and can be ignored if the previous messages were already processed.
> `orderUpdates`: `{ "type": "orderUpdates", "user": "<address>" }` → `WsOrder[]` (User order updates).
> `userFills`: `{ "type": "userFills", "user": "<address>" }` → `WsUserFills` — "Fills snapshot followed by streaming fills". "the first message has `isSnapshot: true` and the following streaming updates have `isSnapshot: false`."
> `clearinghouseState`: `{ "type": "clearinghouseState", "user": "<address>", "dex": "<dex>" }` → `ClearinghouseState`.
> `webData3`: `{ "type": "webData3", "user": "<address>" }` → `WebData3`. (Data-formats section still documents `WebData2`: "Aggregate information about a user, used primarily for the frontend".)
> `l2Book`: optional `fast: boolean` — "5 levels if fast, 20 levels if slow". `WsLevel { px, sz, n }`.
> `activeAssetCtx` / `activeAssetData` (perps) give per-coin ctx incl. mark price.

## Evidence status: VERIFIED (orderUpdates, userFills snapshot-tag, clearinghouseState) · webData2 naming NUANCE

- STR-0129 — CONFIRMED (support): order lifecycle streamed via `orderUpdates` (WsOrder[]); combined with orderStatus/clearinghouseState this supports the state pipeline.
- STR-0133 — CONFIRMED: `orderUpdates` and `userFills` subscriptions exist; **userFills is snapshot-tagged (`isSnapshot: true`) on (re)subscribe** — matches Strategy's "WS userFills (fill-level, snapshot-tagged on reconnect)".
- STR-0200 — CONFIRMED (support): `clearinghouseState` available via REST and WS as the authoritative position/margin source.
- STR-0228 — CONFIRMED (nuance): WS `l2Book` gives 5 levels (fast) or 20 levels (slow); REST l2Book ≤20/side. Depth is bounded to ≤20 levels/side either way.
- **NUANCE (not a conflict):** Strategy §6.2 names "clearinghouseState/webData2". The docs now expose subscription `webData3` (and `WebData2` remains documented as **frontend-aggregate**). The authoritative position/margin source is `clearinghouseState` (Strategy also names it first); `webData2`/`webData3` is a frontend aggregate. Phase 3 should prefer `clearinghouseState` and treat webData2/3 as non-authoritative UI aggregate. Recorded as a nuance in CONFLICT-002 (low impact).
