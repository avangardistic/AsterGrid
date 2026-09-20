# SOURCE_MANIFEST.md

- **Purpose:** Authoritative registry of every source used to make material claims in this program, with source class, integrity hash/version, retrieval date, and role. Nothing becomes evidence until it is listed here.
- **Version:** 2.0 (Phase 2 — venue sources + SDK populated)
- **Producer:** Claude Code (Opus 4.8), Phase 0 (rows 1) + Phase 2 (rows 101–113, SDK).
- **Inputs:** repository contents; `prompt.md` `<source_governance>`, `<source_precedence>`, `<mandatory_hyperliquid_sources>`, `<sdk_governance>`.
- **Source references:** see rows below.
- **Status:** IN PROGRESS (repo inputs + mandatory Hyperliquid docs + SDK recorded; a few secondary pages remain for Phase 2b — see §4).
- **Validation status:** Hashes computed deterministically (SHA-256). **Hash scope:** for venue pages, the SHA-256 is of the locally saved faithful extract file (`research/sources/hyperliquid/page-*.md`), captured from the page's `.md` raw variant via the built-in browser on 2026-09-20 — not of an upstream byte stream (GitBook serves no stable byte artifact). URL + retrieval timestamp + saved-file hash together make each fetch reproducible.

---

## Source-class vocabulary (`prompt.md` `<source_governance>`)

`STRATEGY_SOURCE` · `VENUE_PRIMARY_SOURCE` · `VENUE_SECONDARY_SOURCE` · `TOOL_SOURCE` · `CODEBASE_SOURCE` · `ARCHITECTURE_SOURCE` · `OBSERVATION` · `EXPERIMENT` · `ASSUMPTION` · `HYPOTHESIS` · `OWNER_DECISION`.

## 1. Authoritative inputs already present in the repository

| ID | File | Source class | SHA-256 | Bytes | Retrieval date | Role |
|----|------|-------------|---------|-------|----------------|------|
| SRC-001 | `Strategy.md` | STRATEGY_SOURCE | `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18` | 92686 | 2026-09-20 | Canonical strategy specification (v2.3-final). Authoritative for strategy semantics. Immutable. |
| SRC-002 | `prompt.md` | TOOL_SOURCE (program protocol / process authority) | `a3db715874ca1c7e51d836c8e86269b0db02380ac4f51e43e7de5a8cb5bf5531` | 50200 | 2026-09-20 | Master Control Prompt v3.0. Governs workflow, authority order, phase gating, source governance. Not a strategy-semantics authority. |

## 2. Hyperliquid primary sources — FETCHED (Phase 2, 2026-09-20)

All fetched via the built-in browser using each page's `.md` raw variant. SHA-256 is of the saved extract file (see §hash-scope above). Retrieval date 2026-09-20 for all rows.

| ID | URL | Class | Saved file | SHA-256 (of extract) | Bytes | [HC] targets addressed |
|----|-----|-------|-----------|----------------------|-------|------------------------|
| SRC-101/102 | https://hyperliquid.gitbook.io/hyperliquid-docs/ ; /llms.txt | VENUE_PRIMARY_SOURCE | page-api-root.md | `f4218008a63e8d50110b78404eea02eb14212589dbff3161b770fda06b26131a` | 2311 | docs index/navigation; SDK URL; testnet base URL |
| SRC-103 | .../for-developers/api.md | VENUE_PRIMARY_SOURCE | page-api-root.md | (same as above) | 2311 | API overview; official SDK; mainnet/testnet URLs |
| SRC-104 | .../for-developers/api/exchange-endpoint.md | VENUE_PRIMARY_SOURCE | page-exchange-endpoint.md | `342e5e9caabac52d09ae4bf8dca050078ce7fbd69e4976062137beaa37aa26d1` | 3034 | STR-0133, 0134, 0138, 0175, 0254 |
| SRC-105 | .../for-developers/api/info-endpoint.md | VENUE_PRIMARY_SOURCE | page-info-endpoint.md | `9302c6c1dc76d56421839b6e2a18bce314f0d0c5c0a46a416a2a7d1979fba817` | 3745 | STR-0132, 0133, 0134, 0176, 0228 |
| SRC-107 | .../for-developers/api/info-endpoint/perpetuals.md | VENUE_PRIMARY_SOURCE | page-perpetuals-info.md | `b06c30e94c8e589c3c64009f3bc7731dd904bcaeb3e53d8c858ea8f091d10c2c` | 3663 | STR-0137, 0200, 0224, 0134, 0337 |
| SRC-108 | .../for-developers/api/tick-and-lot-size.md | VENUE_PRIMARY_SOURCE | page-tick-and-lot-size.md | `491e2921e3b401c0f5304c8b8c044717f1770430ba45aadaa23d09cfbd794b8e` | 2417 | STR-0135, 0136, 0137, 0138, 0177 |
| SRC-109 | .../for-developers/api/websocket/subscriptions.md | VENUE_PRIMARY_SOURCE | page-websocket-subscriptions.md | `37129be15214ad0214b8f7ba693ed897bf75b22e9899582acee373e3a7abeb77` | 2885 | STR-0129, 0133, 0200, 0228 |
| SRC-110 | .../for-developers/api/nonces-and-api-wallets.md | VENUE_PRIMARY_SOURCE | page-nonces-and-api-wallets.md | `7adc4b891d3e0c3e9e2804fa5f88d67a8738469bae7b9b15e9cf67c006dd1471` | 2253 | STR-0133 (cloid), 0138 |
| SRC-111 | .../for-developers/api/rate-limits-and-user-limits.md | VENUE_PRIMARY_SOURCE | page-rate-limits.md | `f084a9eb153b5bc0dfa992b903bd23086c348366d853e9504819a3131f3916f5` | 1835 | STR-0176 |
| SRC-112 | .../trading/order-types.md | VENUE_PRIMARY_SOURCE | page-order-types.md | `46a9fd59d66f84e95137065850556775ffb9c0f2d5020d017043bec91d9177fb` | 2779 | STR-0133 (TIF), 0134, 0254 |
| SRC-113 | .../trading/funding.md | VENUE_PRIMARY_SOURCE | page-funding.md | `ff7dcd1a0638fc639473cfa2e3c0508ea1d158558fb20b1a0a1c5614e0d5eb2a` | 1657 | STR-0337 (funding) |
| SRC-114 | .../trading/fees.md | VENUE_PRIMARY_SOURCE | page-fees.md | `4e432e4bec1564e397e839cb2ba8d267774fe093159333a46a751e25411ac9ac` | 1612 | STR-0194 |
| SRC-115 | .../trading/margining.md | VENUE_PRIMARY_SOURCE | page-margining.md | `2e34e652a453a1722e3fd33c01846c5301e788a2ad18a366ab7789cd140b15f2` | 2021 | STR-0175, 0224, 0337 |
| SRC-116 | .../trading/contract-specifications.md | VENUE_PRIMARY_SOURCE | page-contract-specifications.md | `8664798caa50cba3b47446fdec1902c0ef2b795c3c59853d26547128b825a857` | 2105 | STR-0175, 0228, 0337 |

**Working/index artifacts (not venue sources):** `_HC_TARGETS.md` (`189635c3c162602352f44bfdbfebd67115104fe22c2d97f7a0bd94636f373b02`), `TOPIC_EVIDENCE.md` (roll-up).

## 2a. SDK (SRC-106) — FETCHED (Phase 2)

| ID | URL | Class | Record file | SHA-256 (record) | Version / commit | Retrieved |
|----|-----|-------|-------------|------------------|------------------|-----------|
| SRC-106 | https://github.com/hyperliquid-dex/hyperliquid-python-sdk | TOOL_SOURCE / IMPLEMENTATION_REFERENCE (NOT venue authority) | SDK_RECORD.md | `5072f79424ef713a3b2a6868e9357755d6a106b89d5a2b7c82cde71155f34a76` | tag **0.24.0**, commit `2fdb18f9517675ea03695a0962bd19eece9c83f0`, published 2026-06-04 | 2026-09-20 |

## 2b. PENDING — secondary pages for Phase 2b (not yet fetched)

> Needed to fully resolve the two PARTIALLY_VERIFIED items; no evidentiary weight until fetched.

| URL | Purpose |
|-----|---------|
| .../trading/robust-price-indices.md | Mark/oracle price basis for trigger orders (CONFLICT-003 / STR-0134). |
| .../trading/liquidations.md | Trigger/liquidation price basis (STR-0134 corroboration). |
| .../for-developers/api/signing.md | Signing details (supports STR-0138 normalization). |

## 3. Retrieval discipline (binding, from `prompt.md`)

- Prefer primary/first-party sources; never cite a secondary article when a first-party source supports the claim.
- Record retrieval time, URL, and version/commit where available.
- Preserve conflicting evidence; never fabricate citations; never treat search snippets as authoritative.
- For the SDK: record package name, version, git tag/release, commit SHA, repo URL, retrieval date. Treat as `TOOL_SOURCE` / `IMPLEMENTATION_REFERENCE`, never `VENUE_AUTHORITY`.
- On docs / SDK / observation disagreement: do NOT silently pick one — open a `research/findings/CONFLICT-*.md`.
