# page-perpetuals-info — LIVE SNAPSHOT 2026-09-22 (Phase 6a venue refresh)

- **Source URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals.md
- **Fetched:** 2026-09-22 via built-in browser `.md` raw variant.
- **Role:** dated live snapshot for the Phase-6a refresh. The Phase-2 curated extract `page-perpetuals-info.md` (SRC-107) is RETAINED unchanged; this file preserves the current live evidence alongside it (append, do not lose prior evidence).
- **Scope:** decision-relevant excerpts captured verbatim (the full page is large; the excerpts below are the parts that evidence DECISION-006 / DECISION-020 and log new venue capabilities). Non-decision-relevant endpoints (perpDexs, predictedFundings, perpDeployAuctionStatus, activeAssetData, etc.) are present on the live page but omitted here.

## `meta` (universe + margin tables) — verbatim

```json
{
    "universe": [
        { "name": "BTC",  "szDecimals": 5, "maxLeverage": 50 },
        { "name": "ETH",  "szDecimals": 4, "maxLeverage": 50 },
        { "name": "HPOS", "szDecimals": 0, "maxLeverage": 3, "onlyIsolated": true },
        { "name": "LOOM", "szDecimals": 1, "maxLeverage": 3, "isDelisted": true,
          "marginMode": "strictIsolated", // "strictIsolated" means margin cannot be removed, "noCross" means only isolated margin allowed
          "onlyIsolated": true // deprecated. Means either "strictIsolated" or "noCross"
        }
    ],
    "marginTables": [
        [ 50, { "description": "", "marginTiers": [ { "lowerBound": "0.0", "maxLeverage": 50 } ] } ],
        [ 51, { "description": "tiered 10x", "marginTiers": [
                    { "lowerBound": "0.0", "maxLeverage": 10 },
                    { "lowerBound": "3000000.0", "maxLeverage": 5 } ] } ]
    ]
}
```

HIP-3 (builder dex) universe entries carry `name: "xyz:..."`, `marginTableId`, `onlyIsolated`, `marginMode: "strictIsolated"`, `growthMode`, `lastGrowthModeChangeTime`; `metaAndAssetCtxs` first-dex response includes `collateralToken: 0`.

## `clearinghouseState` — verbatim (authoritative account/position truth)

```json
{
  "assetPositions": [
    { "position": {
        "coin": "ETH",
        "cumFunding": { "allTime": "514.085417", "sinceChange": "0.0", "sinceOpen": "0.0" },
        "entryPx": "2986.3",
        "leverage": { "rawUsd": "-95.059824", "type": "isolated", "value": 20 },
        "liquidationPx": "2866.26936529",
        "marginUsed": "4.967826",
        "maxLeverage": 50,
        "positionValue": "100.02765",
        "returnOnEquity": "-0.0026789",
        "szi": "0.0335",
        "unrealizedPnl": "-0.0134"
      },
      "type": "oneWay"
    }
  ],
  "crossMaintenanceMarginUsed": "0.0",
  "crossMarginSummary": { "accountValue": "13104.514502", "totalMarginUsed": "0.0", "totalNtlPos": "0.0", "totalRawUsd": "13104.514502" },
  "marginSummary": { "accountValue": "13109.482328", "totalMarginUsed": "4.967826", "totalNtlPos": "100.02765", "totalRawUsd": "13009.454678" },
  "time": 1708622398623,
  "withdrawable": "13104.514502"
}
```

## `userFunding` delta — verbatim (supports STR-0352 accumulator)

```json
{ "delta": { "coin": "ETH", "fundingRate": "0.0000417", "szi": "49.1477", "type": "funding", "usdc": "-3.625312", "nSamples": null },
  "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8", "time": 1681222254710 }
```

## Refresh findings (Phase 6a)

- **DECISION-006 supporting evidence:** `marginTables` / `marginTiers` (`lowerBound` / `maxLeverage`) are now documented and per-position `liquidationPx` + `maxLeverage` are in `clearinghouseState`. This directly supports DECISION-006 (runtime reads venue-reported maintenance/liquidation as the primary model; §16 D-16 `0.5/Leverage_effective` is the illustrative conservative floor only).
- **DECISION-020 / marginMode nuance:** the venue `meta.marginMode` field EXISTS but its documented values are **isolation qualifiers** (`"strictIsolated"`, `"noCross"`) — there is NO literal `"cross"` value at the `meta` level. Account/position cross-vs-isolated is expressed in `clearinghouseState.assetPositions[].leverage.type ∈ {cross, isolated}` (example shows `"isolated"`), with `position.type: "oneWay"`. DECISION-020's P0 assertion (STR-0360) already keys on `leverage.type` / `position.type`, which is the correct field — see `research/findings/VENUE_DRIFT_2026-09-22.md`. DECISION-020 is NOT changed.
- **Unchanged core facts:** BTC szDecimals 5 / ETH szDecimals 4; `maxLeverage: 50` in the `meta` example (the docs-internal 40x-vs-50x inconsistency persists — DECISION-001 governs: read live, never hardcode).
