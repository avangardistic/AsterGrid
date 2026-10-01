# SDK_RECORD.md — Hyperliquid Python SDK (SRC-106)

- **Purpose:** Record the current official Hyperliquid Python SDK release for reproducibility. Per `prompt.md` `<sdk_governance>`, the SDK is **TOOL_SOURCE / IMPLEMENTATION_REFERENCE**, NOT venue authority.
- **Producer:** Claude Code (Opus 4.8), Phase 2.
- **Source class:** TOOL_SOURCE (implementation reference only).
- **Status:** RECORDED (GitHub reachable; values from GitHub UI + GitHub REST API).

## Record

| Field | Value |
|-------|-------|
| Repository URL | https://github.com/hyperliquid-dex/hyperliquid-python-sdk |
| Latest release / tag | **0.24.0** (marked "Latest", not a prerelease, not a draft) |
| Tag → commit SHA (full) | `2fdb18f9517675ea03695a0962bd19eece9c83f0` (lightweight tag → commit; short `2fdb18f`; parent `7ee976d` = 0.23.0) |
| Target branch | `master` |
| Release published (UTC) | 2026-06-04T19:49:39Z (created 2026-06-04T19:46:55Z) |
| Release author | traderben |
| Release note | "Support multisig userSetAbstraction (#299)" — "Add support for sending user abstraction actions with a multi-sig" |
| PyPI package name | `hyperliquid-python-sdk` (documented name; PyPI page/version NOT independently fetched this run) |
| Retrieval timestamp | 2026-09-20T18:49Z |
| Retrieval method | Built-in browser: /tags, /releases/tag/0.24.0, api.github.com releases/latest + git/refs/tags/0.24.0 |

Recent tag lineage (newest→older): 0.24.0 (2fdb18f) · 0.23.0 (7ee976d) · 0.22.0 (b4d2d1b) · 0.21.0 (be7523d) · 0.20.1 (8baad66) · 0.20.0 (ea84213) · 0.19.0 (64b252e) · 0.18.0 (f19056c) · 0.17.0 (d01888e) · 0.16.0 (3ad503f).

Other SDKs referenced by the official API page (community; NOT venue authority, NOT the official SDK): Rust `github.com/infinitefield/hypersdk`; TypeScript `github.com/nktkas/hyperliquid`, `github.com/nomeida/hyperliquid`; CCXT integration.

## Governance notes (binding)

- Treat 0.24.0 as an **implementation reference**, never as the definition of venue semantics. For any `[HC]` claim, the authority is the docs/API and controlled observation; the SDK is evidence of *implementation*, not of *venue behavior*.
- Do NOT install the SDK this phase. Do NOT read its source as venue authority.
- If a specific `[HC]` claim turns on SDK behavior (e.g., duplicate-cloid handling, precision normalization), that dependency is noted in the relevant topic/finding — to be confirmed by controlled observation in a later phase, not assumed from the SDK.
