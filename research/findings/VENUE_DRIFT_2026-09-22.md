# VENUE_DRIFT_2026-09-22.md — Phase 6a venue-refresh findings

- **Producer:** Claude Code (Opus 4.8), Phase 6a. **No DECISION changed; no fix applied; no gate opened.** This file records venue-evidence observations from the 2026-09-22 live refresh. Per Step 2.3, a genuine conflict is recorded here and STOPPED for that finding — decisions are NOT changed.

## DRIFT-1 — `meta.marginMode` field semantics vs DECISION-020's pinned `MarginMode = cross` (NON-BLOCKING clarification)

- **Observed (live 2026-09-22, `perpetuals.md`):** the venue `meta.universe[]` entries may carry `marginMode` with values `"strictIsolated"` ("margin cannot be removed") or `"noCross"` ("only isolated margin allowed"); `onlyIsolated` is deprecated and means either. There is **NO literal `"cross"` value** for `meta.marginMode` — it is an **asset-level isolation qualifier**, present only on isolated-restricted assets.
- **Where "cross" actually lives:** `clearinghouseState.assetPositions[].leverage.type ∈ {cross, isolated}` (per-position), with `position.type ∈ {oneWay, ...}`. The live example shows `leverage.type: "isolated"`, `type: "oneWay"`.
- **Assessment:** this is a **field-semantics nuance, not a contradiction**. DECISION-020 pins `MarginMode = cross` and its P0 assertion (STR-0360) already keys on `clearinghouseState.assetPositions[].leverage.type == MarginMode` AND `position.type == oneWay` — i.e. it reads the correct authoritative field. `meta.marginMode` is a separate, asset-level restriction that would additionally prevent selecting cross on isolation-restricted assets (e.g. HIP-3 `xyz:*`, delisted, `onlyIsolated` assets).
- **Consequence (recorded, not actioned):** Phase 6b/6c should, when implementing STR-0358..0360, (a) assert on `leverage.type`/`position.type` (already specified), and (b) additionally reject trading an asset whose `meta.marginMode`/`onlyIsolated` forbids cross (BTC/ETH are not so restricted). This is an implementation detail for the pinned-mode check, not a change to DECISION-020.
- **Status:** NON-BLOCKING clarification. **DECISION-020 UNCHANGED.** No gate opened.

## DRIFT-2 — new venue capabilities (logged, not adopted)

- **`meta` / `metaAndAssetCtxs`:** `marginTables` / `marginTiers` (`lowerBound`/`maxLeverage`), `collateralToken`, `isDelisted`, HIP-3 builder dexes (`xyz:*`, `marginTableId`, `growthMode`). `marginTables` **supports DECISION-006** (venue-reported maintenance/leverage tiers as the primary model).
- **WebSocket:** new subscriptions `twapStates`, `userTwapSliceFills`, `userTwapHistory`, `bbo`, `fastAssetCtxs`, `allDexsClearinghouseState`, `allDexsAssetCtxs`, `outcomeMetaUpdates`, `spotState`; `webData3` is current.
- **Status:** logged as available venue capabilities in SOURCE_MANIFEST.md §6. **NOT adopted in any design** (Phase 6b decides). No conflict with any decision.

## No decision-contradicting conflict found

The refresh found **no evidence that contradicts** any DECISION-001..020. DRIFT-1 is a field-semantics clarification consistent with DECISION-020; DRIFT-2 is additive capability. The docs-internal BTC/ETH 40x-vs-50x inconsistency persists (DECISION-001 governs). Therefore no decision is stopped or changed.
