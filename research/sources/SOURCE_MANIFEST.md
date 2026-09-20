# SOURCE_MANIFEST.md

- **Purpose:** Authoritative registry of every source used to make material claims in this program, with source class, integrity hash/version, retrieval date, and role. Nothing becomes evidence until it is listed here.
- **Version:** 1.0 (Phase 0 — initial)
- **Producer:** Claude Code (Opus 4.8), Phase 0.
- **Inputs:** repository contents; `prompt.md` `<source_governance>`, `<source_precedence>`, `<mandatory_hyperliquid_sources>`, `<sdk_governance>`.
- **Source references:** see rows below.
- **Status:** IN PROGRESS (only repo-local inputs recorded; venue sources deferred to Phase 2).
- **Validation status:** Hashes computed deterministically (SHA-256). Venue rows are declared PENDING and carry no evidentiary weight yet.

---

## Source-class vocabulary (`prompt.md` `<source_governance>`)

`STRATEGY_SOURCE` · `VENUE_PRIMARY_SOURCE` · `VENUE_SECONDARY_SOURCE` · `TOOL_SOURCE` · `CODEBASE_SOURCE` · `ARCHITECTURE_SOURCE` · `OBSERVATION` · `EXPERIMENT` · `ASSUMPTION` · `HYPOTHESIS` · `OWNER_DECISION`.

## 1. Authoritative inputs already present in the repository

| ID | File | Source class | SHA-256 | Bytes | Retrieval date | Role |
|----|------|-------------|---------|-------|----------------|------|
| SRC-001 | `Strategy.md` | STRATEGY_SOURCE | `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18` | 92686 | 2026-09-20 | Canonical strategy specification (v2.3-final). Authoritative for strategy semantics. Immutable. |
| SRC-002 | `prompt.md` | TOOL_SOURCE (program protocol / process authority) | `a3db715874ca1c7e51d836c8e86269b0db02380ac4f51e43e7de5a8cb5bf5531` | 50200 | 2026-09-20 | Master Control Prompt v3.0. Governs workflow, authority order, phase gating, source governance. Not a strategy-semantics authority. |

## 2. PENDING — Hyperliquid primary sources to be retrieved in Phase 2

> These are mandated by `prompt.md` `<mandatory_hyperliquid_sources>`. **They have NOT been fetched.** No hashes, no retrieval dates, no evidentiary weight yet. Listed here only to fix the retrieval targets. Do not treat any claim about Hyperliquid as evidenced until the corresponding row is populated with content + hash/version + retrieval date in Phase 2.

| ID (reserved) | URL | Intended source class | Role |
|---------------|-----|----------------------|------|
| SRC-101 | https://hyperliquid.gitbook.io/hyperliquid-docs/ | VENUE_PRIMARY_SOURCE | Docs root / navigation. |
| SRC-102 | https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt | VENUE_PRIMARY_SOURCE | Machine-readable docs index. |
| SRC-103 | https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api | VENUE_PRIMARY_SOURCE | API overview. |
| SRC-104 | https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint | VENUE_PRIMARY_SOURCE | Exchange endpoint (order placement/cancel/modify, signing). |
| SRC-105 | https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint | VENUE_PRIMARY_SOURCE | Info endpoint (clearinghouseState, meta, userFills, orderStatus, webData2). |
| SRC-106 | https://github.com/hyperliquid-dex/hyperliquid-python-sdk | TOOL_SOURCE / IMPLEMENTATION_REFERENCE | Official Python SDK. **NOT** a venue authority. Discover current release/tag/commit and record it (do not hardcode a version in advance). |

## 3. Retrieval discipline (binding for Phase 2, from `prompt.md`)

- Prefer primary/first-party sources; never cite a secondary article when a first-party source supports the claim.
- Record retrieval time, URL, and version/commit where available.
- Preserve conflicting evidence; never fabricate citations; never treat search snippets as authoritative.
- For the SDK: record package name, version, git tag/release, commit SHA, repo URL, retrieval date. Treat as `TOOL_SOURCE` / `IMPLEMENTATION_REFERENCE`, never `VENUE_AUTHORITY`.
- On docs / SDK / observation disagreement: do NOT silently pick one — open a `research/findings/CONFLICT-*.md`.
