# ASTER DEX — Source Manifest (Phase 0 grounding, partial)

**Fetched:** 2026-10-01 (UTC session date) via GitHub contents API
**Upstream repo:** `github.com/asterdex/api-docs`, branch `master`, HEAD `eeddec8d97cd1250351f62b976973ae2a0d583c5` (commit date 2026-09-23T15:02:57Z)
**Scope:** only the facts the contract delta (`docs/contract/CONTRACT_DELTA_ASTER.md`) depends on. This is NOT the full Phase 0 deliverable (no exchangeInfo filters, funding formula, WS payloads, rate-limit table).

Verbatim docs are not vendored (≈ 0.5 MB, vendor-owned). Re-fetch and compare the SHA-256 below.

| ID | Path in upstream repo | bytes | SHA-256 |
|---|---|---|---|
| S1 | `Aster API Overview.md` | 4357 (blob `3ea38b3a…`) | not hashed locally — blob sha above is the git id |
| S2 | `V1(Legacy)/EN/aster-finance-futures-api.md` | 121054 | `76309567b82cc94cb48822cd196bbe988d6d8b7b509de24b7d3df57427e1fdbe` |
| S3 | `V3(Recommended)/EN/aster-finance-futures-api-v3.md` | 231324 | `96c6a37dea14ced0ee97d8cac2265a88df5628cad2e2721b8353cba937c2ca32` |
| S4 | `V3(Recommended)/EN/aster-finance-futures-api-testnet.md` | 175900 | `417f2f3abfed8d40202e301f442b523c674f16bcea468cd43819b1a5299a6428` |

Reproduce:
```
curl -sL -H "Accept: application/vnd.github.raw" \
  "https://api.github.com/repos/asterdex/api-docs/contents/V3(Recommended)/EN/aster-finance-futures-api-v3.md" | sha256sum
```
(Hashes drift when upstream edits; record the upstream HEAD sha with any re-check.)

## Facts used, with anchors (line numbers are in the files as fetched)

| # | Fact | Source | Anchor |
|---|---|---|---|
| F1 | V1 new API-key creation is closed: "Starting from March 25, 2026, V1 new API Key creation is no longer supported. Existing API Keys will continue to work." | S1 | l.5 |
| F2 | V1 auth = API key + HMAC SHA256, header `X-MBX-APIKEY`, `timestamp`, optional `recvWindow` | S1, S2 | S1 l.34-41 (header l.36); S2 l.192 |
| F3 | V3 auth = `user` (master wallet) + `signer` (API wallet) + `nonce` (µs) + `signature`; signature is EIP-712 signed with the signer private key | S1, S3 | S1 l.43-60; S3 l.259-266, 3097 |
| F4 | V3 is not stdlib-only (Keccak + secp256k1 signing) | S3 | follows from F3 |
| F5 | Hedge-mode switch/read exist in both: `POST/GET /fapi/v1/positionSide/dual` (V1) and `/fapi/v3/positionSide/dual` (V3); POST weight 1, GET weight 30; applies to "EVERY symbol"; `dualSidePosition` is the STRING `"true"`/`"false"` on POST and a JSON bool on GET | S2, S3 | S2 l.2177-2225; S3 l.2338-2375 |
| F6 | Order: V1 `POST /fapi/v1/order`; V3 `POST /fapi/v3/order`. `positionSide` "must be sent in Hedge Mode" (LONG/SHORT; BOTH in one-way) | S2, S3 | S2 l.2313-2340; S3 l.2537-2556 |
| F7 | `reduceOnly`: "Cannot be sent in Hedge Mode; cannot be sent with closePosition=true" | S2, S3 | S2 l.2335; S3 l.2554 |
| F8 | `closePosition=true` (STOP_MARKET/TAKE_PROFIT_MARKET): in Hedge Mode "cannot be used with BUY orders in LONG position side, and cannot be used with SELL orders in SHORT position side" | S2 | l.2387 |
| F9 | `newClientOrderId`: "A unique id among open orders. Automatically generated if not sent." regex `^[\.A-Z\:/a-z0-9_-]{1,36}$` — i.e. uniqueness among OPEN orders only, ≤ 36 chars; the docs state no post-close dedup guarantee | S2, S3 | S2 l.2337; S3 l.2556 |
| F10 | Positions: V1 `GET /fapi/v2/positionRisk` (weight 5); V3 `GET /fapi/v3/positionRisk` (weight 5). Hedge-mode response has separate `LONG` and `SHORT` rows per symbol; in the doc sample the SHORT row's `positionAmt` is **negative** (`"-10.000"`) | S2, S3 | S2 l.3276 (hedge sample l.3231-3270, SHORT `positionAmt` at l.3266); S3 l.3741 |
| F11 | Account: V1 `GET /fapi/v4/account` (weight 5) — `assets[]` per asset (`walletBalance`, `marginBalance`, `availableBalance`, …) and `positions[]` ("only LONG and SHORT positions will be returned with Hedge mode"). V3 equivalents: `GET /fapi/v3/accountWithJoinMargin`, `GET /fapi/v3/balance` | S2, S3 | S2 l.3046 (`positions[]` at l.3022); S3 l.3445, 3535 |
| F12 | Docs recommend pairing positionRisk with user-data stream `ACCOUNT_UPDATE` for timeliness | S2, S3 | S2 l.3293; S3 l.3755 |
| F13 | Testnet exists for V3 only: REST `https://fapi.asterdex-testnet.com`, WS `wss://fstream.asterdex-testnet.com`. No testnet is mentioned in the V1 doc (0 matches for "testnet") | S4, S2 | S4 l.134, 4327-4332 |
| F14 | Mainnet base `https://fapi.asterdex.com`; V3 listenKey endpoints `POST/PUT/DELETE /fapi/v3/listenKey`; key valid 60 min | S3 | l.5788-5826 |
| F15 | Rate limits are per IP (weights) and per account (orders); 429 → back off; repeated → 418 IP ban 2 min–3 days | S2 | l.162-186 |
| F16 | V3: `positionRisk` hedge sample has SHORT `positionAmt` `"-10.000"` (S3 l.3730) and per-row `marginType`, `notional` (negative for SHORT); `POST/GET /fapi/v3/multiAssetsMargin` (`"true"` Multi-Assets / `"false"` Single-Asset, "on Every symbol"); `POST /fapi/v3/marginType` (symbol, `ISOLATED`\|`CROSSED`); `GET /fapi/v3/accountWithJoinMargin` (+ non-join `GET /fapi/v3/account`) | S3 | l.3730; l.2436-2461; l.3586-3596; l.3535-3539 |

## NOT verified here (still open for Phase 0 proper)

- Whether `POST positionSide/dual` is rejected while positions/open orders exist (Binance returns an error; Aster docs examined do not say).
- Whether a flat leg's `positionRisk` row is omitted (samples show both rows).
- V3 `accountWithJoinMargin` response fields; the exact `marginType` wire value for cross; Hedge+Multi-Assets coexistence.
- `exchangeInfo` filter shapes (`tickSize`, `stepSize`, `minNotional`) — §6.3.
- Funding formula/cadence — §10.
- Margin modes (cross/isolated; Multi-Assets mode) and which asset the equity is read from.
- WS payload shapes for `ACCOUNT_UPDATE` / `ORDER_TRADE_UPDATE`.
- Fee tiers (the handoff's 0.5 / 4 bps figures are carried over, not re-checked).

## Hygiene note

The V3 docs embed an example `privateKey` / `signer` pair in sample code. They are vendor sample values — never copy them into this repo, tests or fixtures.
