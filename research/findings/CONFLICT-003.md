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
