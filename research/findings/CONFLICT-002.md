# CONFLICT-002 — Authoritative account-state source: "webData2" naming vs current "webData3" (frontend-aggregate)

- **conflict_id:** CONFLICT-002
- **status:** OPEN (low impact / naming)
- **claim:** Strategy repeatedly pairs "clearinghouseState/webData2" as the authoritative position/margin source (STR-0132, STR-0133, STR-0200; Strategy §6.1/§6.2/§11.1).
- **source A (STRATEGY_SOURCE):** `Strategy.md` §6.2: "clearinghouseState/webData2 (authoritative position/margin state)".
- **source B (VENUE_PRIMARY_SOURCE):** websocket/subscriptions — the current subscription is `webData3` (item 3); the data-formats section still documents `WebData2` and describes it as "**Aggregate information about a user, used primarily for the frontend**". `clearinghouseState` is a first-class REST + WS source.
- **authority_class:** VENUE_PRIMARY_SOURCE.
- **version/date:** Docs 2026-09-20; Strategy v2.3-final.
- **exact_discrepancy:** (1) `webData2` is characterized by the venue as a **frontend aggregate**, not an authoritative low-level source; (2) the live subscription name has advanced to `webData3`. Strategy treats webData2 as co-authoritative with clearinghouseState.
- **possible_reasons:** webData2 was the contemporary name when the Strategy was written; the venue has since introduced webData3; webData2/3 has always been a frontend convenience aggregate.
- **impact:** **LOW.** The authoritative source Strategy names FIRST — `clearinghouseState` — is fully verified and is the correct authority for `ActualExposure` (STR-0200) and account equity (STR-0224). The webData2 dependency is redundant/frontend and should not be treated as the authoritative delta source.
- **resolution_method:** Phase 3 should specify `clearinghouseState` (REST + WS) as THE authoritative position/margin source; treat `webData2`/`webData3` as non-authoritative UI aggregate (use only for convenience, never for POSITION_VERIFIED). Update capability/architecture docs accordingly (not Strategy.md).
- **current_status:** OPEN — surfaced to owner; no silent edit.
