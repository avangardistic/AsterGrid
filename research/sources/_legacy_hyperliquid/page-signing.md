# Venue source page — Signing (for-developers/api)

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/signing.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T19:07Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0138 (pre-sign normalization), STR-0133 (cloid — dedup NOT documented)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> It is recommended to use an existing SDK instead of manually generating signatures. … An incorrect signature results in recovering a different signer …
> Some common errors:
> 1. Not realizing that there are two signing schemes (`sign_l1_action` vs `sign_user_signed_action`).
> 2. Not realizing that the order of fields matter for msgpack.
> 3. Issues with **trailing zeroes on numbers**.
> 4. Issues with upper case characters in address fields. … lowercase any address before signing …
> 5. Believing that the signature must be correct because calling recover signer locally results in the correct address …

## Evidence status: VERIFIED (pre-sign normalization) · cloid dedup NOT DOCUMENTED

- STR-0138 — CONFIRMED (support): correct signing requires client-side normalization — **trailing zeroes on numbers** and lowercased addresses matter; combined with tick-and-lot-size precision rules, this confirms the Strategy's "normalize before every signed order" requirement. (The "most common third-party-SDK bug class" phrasing is commentary; the venue-verifiable normalization requirement is confirmed.)
- STR-0133 (cloid "idempotent order identity") — signing.md does **not** address duplicate-cloid submission behavior. Across all fetched pages, the venue documents replay/idempotency via the **nonce set** (nonces-and-api-wallets), and cloid as a stable *identity* for orderStatus/cancelByCloid. Whether re-submitting the same cloid is de-duplicated is **NOT documented** → remains a deferred observation item (not a blocking conflict); does not affect the enumerated mechanisms of STR-0133.
