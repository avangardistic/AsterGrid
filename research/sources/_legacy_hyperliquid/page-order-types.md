# Venue source page — Order types (trading)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-types.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:36Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0133 (TIF), STR-0134 (trigger basis), STR-0254 (TWAP)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> ### Order options
> * Good Til Cancel (GTC): An order that rests on the order book until it is filled or canceled
> * Post Only (ALO): An order that is added to the order book but doesn't execute immediately. It is only executed as a resting order
> * Immediate or Cancel (IOC): An order that will be canceled if it is not immediately filled
> * Reduce Only: An order that reduces a current position …

> * TWAP: A large order divided into smaller suborders and executed at regular intervals … Intervals are a minimum of 30 seconds. TWAP suborders have a maximum slippage of 3%
> ### TWAP details
> … Suborders are sent at a fixed interval … every 30 seconds … A suborder is constrained to have a max slippage of 3%. When suborders do not fully fill … later suborders will be larger but subject to the constraint of 3 times the normal suborder size … Running time can be set from 5 minutes to 7 days, with a $100 minimum total order size.

> * Stop Market: A market order that is activated when the price reaches the selected trigger price. For long orders, the trigger price needs to be higher than the mid price …
> * Trailing Stop: A market order that is activated when the mark price retraces from its best level …
> * TWAP … Trigger Price: The TWAP order will be activated when the mark price reaches the trigger price set

## Evidence status: VERIFIED (TIF, TWAP) · PARTIALLY_VERIFIED (trigger→oracle-mark)

- STR-0133 (TIF Gtc/Ioc/Alo) — CONFIRMED verbatim (GTC, ALO=Post Only, IOC).
- STR-0254 (native TWAP: ≥30s intervals, ≤3% per-suborder slippage) — CONFIRMED verbatim ("Intervals are a minimum of 30 seconds. TWAP suborders have a maximum slippage of 3%"). Extra venue facts: suborder cap = 3× normal suborder size; $100 min; 5min–7day; ±20% randomize option. Strategy's "remaining quantity tracked, never assumed closed" is a design rule, not contradicted by venue text.
- STR-0134 (trigger evaluated against oracle mark price, not last trade) — PARTIALLY_VERIFIED here: this page states trailing-stop and TWAP triggers use **mark price**; stop/take activation is described relative to **mid price** in the UI direction rule. The precise "oracle mark price" basis for stop/take trigger orders is to be confirmed on the exchange-endpoint page (trigger order schema). No conflict asserted yet — nuance flagged.
