# ASTER API Research Roadmap (Phase 0 / P0b grounding plan)

**Status:** DRAFT for Owner ACCEPT · 2026-10-01 · document-only
**Inputs:** `research/aster/SOURCE_MANIFEST.md` (S1–S4, F1–F16), `docs/contract/CONTRACT_DELTA_ASTER.md` (rev 2, ASTR-001..013), `docs/ROADMAP.md` (P0b), `ASTERGRID_HANDOFF.md`
**Claim hygiene:** every produced evidence file must carry SOURCE class (`VENDOR_DOC`, `TESTNET_OBSERVATION`, `OWNER_DECISION`, `ASSUMPTION`), anchor (URL/upstream path + line + fetch timestamp), and status (`VERIFIED` / `PARTIALLY_VERIFIED` / `UNVERIFIED` / `CONFLICTED`).
**Rule:** `Strategy.md` is immutable; all venue deltas stay in the overlay/contract layer. No code in this phase.

## 0. Goal

Close every "NOT verified" item in `SOURCE_MANIFEST.md` and every OPEN item in
the contract delta that can be closed **from documentation or testnet
observation** — so that Phase P2 (engine delta) and P3 (adapter) build on
verified wire facts, not handoff assumptions.

## 1. Workstreams (each → one evidence file under `research/aster/`)

### W1 — `exchangeInfo` and precision (→ `EXCHANGE_INFO.md`) — closes §6.3 / OPEN-6a
1. Fetch `GET /fapi/v3/exchangeInfo` (testnet first, then mainnet) for all
   configured symbols.
2. Record verbatim per symbol: `tickSize` (price filter), `stepSize` +
   `minQty` (lot size), `minNotional` (notional filter), `pricePrecision`,
   `quantityPrecision`, contract type, `baseAssetPrecision`.
3. Map to strategy: §6.3's "≤5 significant figures / MAX_DECIMALS=6" is
   **Hyperliquid** — the AsterGrid equivalent is the filter set above; the
   overlay must state the replacement rule (round-before-send, never
   reject-and-retry).
4. Also capture `rateLimits[]` from the same response (feeds W5).
**Accept:** table per symbol with URL + fetch timestamp + verbatim JSON excerpt; a paragraph stating which strategy constant each field binds.

### W2 — Funding economics (→ `FUNDING_EVIDENCE.md`) — closes §10 / OPEN-6b
1. Funding formula, cap/floor, interval (e.g. 8h vs 1h), and the exact
   premium-index inputs, from the V3 doc section on funding.
2. `GET /fapi/v3/premiumIndex` and `GET /fapi/v3/fundingRate` shapes; mark
   price vs last price vs index price — which is authoritative for trigger
   orders (HL used oracle mark; ASTR side needs the explicit statement).
3. Historical funding for the configured symbol(s): min/mean/max over a
   meaningful window (testnet values are not meaningful; use mainnet public
   endpoints, read-only, no auth).
**Accept:** formula quoted verbatim; a worked example in Decimal; a comparison row vs the §10 `FundingCostEstimate(holding_period)` slot.

### W3 — User-data stream shapes (→ `WS_PAYLOADS.md`) — closes MANIFEST "WS payload shapes"
1. `ACCOUNT_UPDATE`, `ORDER_TRADE_UPDATE`, `MARGIN_CALL`, mark-price and depth
   streams: full sample payloads, field-by-field, from the V3 doc.
2. For `ORDER_TRADE_UPDATE`: the exact `positionSide` values in fills (must be
   LONG/SHORT in hedge mode), order states, and the fill fields the
   `FillEvent.position_side` engine change (P2d) will map from.
3. listenKey lifecycle specifics beyond F14 (keepalive interval, expiry
   behavior mid-stream, reconnect semantics).
**Accept:** one annotated sample payload per event type; mapping table "wire field → engine field (or: adapter-only)".

### W4 — Account and margin surface (→ `ACCOUNT_FIELDS.md`) — closes OPEN-7, OPEN-9
1. `GET /fapi/v3/accountWithJoinMargin` full response schema (the doc samples
   seen so far are V1-shaped); enumerate `assets[]` and `positions[]` fields.
2. Candidate CapitalBase fields under Multi-Assets cross: `totalMarginBalance`
   (USD), `totalWalletBalance`, per-asset `marginBalance` — present all with
   units, propose one, **decide via Owner gate** (do not decide here).
3. `marginType` wire value for cross in `positionRisk` rows (doc samples show
   only `"isolated"`; POST enum is `ISOLATED|CROSSED`).
4. Whether Multi-Assets mode changes positionRisk/account field semantics
   (units, USD-value fields).
**Accept:** field inventory + the OPEN-7 proposal (not decision) + OPEN-9 answer.

### W5 — Rate limits and error taxonomy (→ `RATE_LIMITS_ERRORS.md`) — extends F15
1. Full `rateLimits[]` table per endpoint class (request weights: confirmed
   GET dual=30, positionRisk=5; enumerate the rest from exchangeInfo + docs).
2. Order-rate limits per account; 429/418 handling; ban durations.
3. Error-code table relevant to the engine: `-4225 Nonce Expired`, position-side
   errors (the ASTR-008 trigger class), `-2019 margin insufficient`, filter
   failures, duplicate `newClientOrderId` behavior.
**Accept:** table (code → meaning → engine reaction class: resync / abort / local-reject / backoff).

### W6 — Testnet behavioral probes (→ `TESTNET_PROBES.md`) — closes OPEN-1, OPEN-4, OPEN-8 (+ confirms OPEN-9)
**Needs from Owner:** one testnet API wallet (private key never enters the repo).
Probes (each a scripted, logged, minimal-impact sequence):
1. **OPEN-4:** with one small open position, attempt `POST positionSide/dual`
   flip — record exact error or acceptance. (Repeat with an open order.)
2. **OPEN-1:** flatten one leg, re-read `positionRisk` — is the flat leg's row
   omitted or zero-filled?
3. **OPEN-8:** enable hedge mode + Multi-Assets mode together; confirm both
   reads report on; flip each back; document any interference.
4. **OPEN-9:** set cross on a symbol, read `positionRisk.marginType` — record
   the exact wire string.
5. `closePosition=true` on STOP_MARKET in hedge mode — confirm the F8
   restriction empirically (contract does not use it; record for the record).
**Accept:** one probe = one section: setup, script (committed), raw request/response, verdict, OPEN-item status flip.

## 2. Sequencing & dependencies

```
W1, W2, W3, W5  → doc-only, can start immediately (public/read endpoints)
W4              → doc-only; needs the V3 account schema section
W6              → blocked on Owner testnet API wallet
```
All Wx outputs feed P1 ACCEPT (contract overlay) and unblock P2a–P2f /
P3a–P3b evidence requirements per `docs/ROADMAP.md` §3.

## 3. Explicit non-goals

No engine code, no adapter code, no key material in the repo, no mainnet
writes (W6 is testnet-only), no decision on OPEN-7/OPEN-10 (Owner gates),
no edits to `Strategy.md`.

## 4. Tooling

Research agent prompt: `docs/prompts/PROMPT_RESEARCH_ASTER_API.md`.
Vendor docs live upstream (`asterdex/api-docs`); re-fetch and re-hash per the
manifest's reproduce block — never vendor the 0.5 MB of vendor markdown into
this repo.
