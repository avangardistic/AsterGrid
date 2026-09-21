# CONFLICT-003 — Trigger-order price basis: Strategy "oracle mark price, not last trade" vs docs (mark for trailing/TWAP; mid for stop/take UI)

- **conflict_id:** CONFLICT-003
- **status:** OPEN (low impact; PARTIALLY_VERIFIED, not a proven contradiction)
- **claim:** Strategy §6.2 (STR-0134): "trigger orders evaluated against oracle mark price, not last trade."
- **source A (STRATEGY_SOURCE):** `Strategy.md` §6.2 — trigger orders use oracle mark price.
- **source B (VENUE_PRIMARY_SOURCE):** trading/order-types — Stop/Take "activated when the price reaches the selected trigger price"; long/short direction described relative to **mid price**; **Trailing Stop** and **TWAP** triggers explicitly use **mark price**. info-endpoint order status includes `oracleRejected` ("price too far from oracle"). exchange-endpoint trigger schema `{isMarket, triggerPx, tpsl}` does not state the basis.
- **authority_class:** VENUE_PRIMARY_SOURCE.
- **version/date:** Docs 2026-09-20; Strategy v2.3-final.
- **exact_discrepancy:** The fetched pages confirm **mark price** as the trigger basis for trailing-stop and TWAP, and confirm oracle is a placement control, but do **not** state verbatim that ALL stop/take trigger orders evaluate against **oracle mark price** (vs last trade). The UI direction text references **mid**. So Strategy's blanket "oracle mark price, not last trade" for trigger orders is **not fully corroborated** by these two pages (it is not contradicted either).
- **possible_reasons:** Trigger basis may be documented on robust-price-indices / liquidations pages not fetched this phase; "mark" vs "oracle mark" vs "mid" terminology overlaps; UI vs matching-engine wording.
- **impact:** **LOW–MEDIUM.** Trigger basis matters for Emergency Execution (§9.1) and stop behavior. Strategy's core intent (never trigger on raw last trade) is consistent with the venue using mark/oracle, but the precise basis for stop/take needs one more primary source.
- **resolution_method:** Phase 2b/3: fetch trading/robust-price-indices.md and trading/liquidations.md; if still unresolved, confirm by controlled observation. Do not assume "oracle mark for all trigger types" until corroborated.
- **current_status:** OPEN — surfaced to owner; STR-0134 marked PARTIALLY_VERIFIED.

## Update 2026-09-20 (Phase 2.5+2b)

- **New evidence (SRC-117, robust-price-indices.md, verbatim):** "Mark price is an unbiased and robust estimate of the fair perp price, and is used for margining, liquidations, **triggering TP/SL**, and computing unrealized pnl." Mark price is a **median** of (1) oracle price + 150s EMA of (HL mid − oracle), (2) median of best bid/ask/last-trade on HL, (3) weighted median of Binance/OKX/Bybit/Gate/MEXC perp mids. (SRC-118, liquidations.md: "Liquidations use the mark price".)
- **analysis:** The venue distinguishes **oracle price** (funding only) from **mark price** (margining, liquidations, TP/SL triggering, uPnL). Trigger orders fire on **mark price**, and "last trade" is only 1 of 3 medianed inputs — never the sole basis. Strategy's phrase "oracle mark price, not last trade" maps to the venue's **mark price** (which includes an oracle-derived component); the operative claim (triggers on mark, not raw last trade) is now **unambiguously confirmed**. The only imprecision is terminology ("oracle mark" vs "mark"), which is subsumed since mark incorporates the oracle.
- **revised impact:** **LOW** (terminology only; operative semantics confirmed).
- **updated status:** **RESOLVED.** STR-0134 promoted to VERIFIED (refs SRC-112, SRC-117, SRC-118). GATE-003 is therefore **NOT** opened (per the Part D condition).
