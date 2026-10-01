# Venue source page — Exchange endpoint (SRC-104)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:37Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0133 (ack resting/filled/error, cloid, TIF), STR-0134 (trigger schema), STR-0138 (cloid/normalize), STR-0175 (min order value), STR-0254 (twapOrder action)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> The exchange endpoint is used to interact with and trade on the Hyperliquid chain. See the Python SDK for code to generate signatures for these requests.

> For limit orders, TIF (time-in-force) sets the behavior of the order upon first hitting the book.
> ALO (add liquidity only, i.e. "post only") will be canceled instead of immediately matching.
> IOC (immediate or cancel) will have the unfilled part canceled instead of resting.
> GTC (good til canceled) orders have no special behavior.
> Client Order ID (cloid) is an optional 128 bit hex string, e.g. `0x1234567890abcdef1234567890abcdef`

> Order action schema: `"t": { "limit": { "tif": "Alo" | "Ioc" | "Gtc" } or "trigger": { "isMarket": Boolean, "triggerPx": String, "tpsl": "tp" | "sl" } }`, `"c": Cloid (optional)`; keys: a=asset, b=isBuy, p=price, s=size, r=reduceOnly, t=type, c=cloid.

> Order response statuses (200 OK): `{"resting":{"oid":...}}` · `{"filled":{"totalSz":"0.02","avgPx":"1891.4","oid":...}}` · `{"error":"Order must have minimum value of $10."}`

> Cancel-by-cloid action `{"type":"cancelByCloid","cancels":[{"asset":Number,"cloid":String}], "f":Boolean}`; cancel error: "Order was never placed, already canceled, or filled." `fast` (`f`) orders are rejected if they refer to trigger orders.

## Evidence status: VERIFIED (TIF, cloid, ack shape, min value) · PARTIALLY_VERIFIED (trigger→oracle-mark)

- STR-0133 — CONFIRMED: TIF `Alo|Ioc|Gtc` with ALO reject-instead-of-cross ("canceled instead of immediately matching"); cloid = optional 128-bit hex; REST ack statuses resting/filled/error verbatim.
- STR-0138 — CONFIRMED (support): cloid supplied by client on the order; signing/precision required client-side (see tick-and-lot-size + Signing).
- STR-0175 — CONFIRMED (partial): venue enforces a **minimum order value of $10** (error string). Per-asset minimum *size* derives from $10 / price at szDecimals (cross-check contract-specifications). Margin-availability is a client precheck, not an order-schema field.
- STR-0134 — PARTIALLY_VERIFIED: trigger schema is `{isMarket, triggerPx, tpsl}`; this page does not state the price **basis** (mark vs last). order-types.md states trailing-stop and TWAP triggers use **mark price**. "Oracle mark price for all trigger orders" remains to be confirmed on a mark/oracle page (robust-price-indices / margining) — flagged, no conflict.
- STR-0254 — supports native TWAP action exists (twapOrder); slicing/slippage confirmed on order-types.md.
