# Venue source page — Nonces and API wallets

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/nonces-and-api-wallets.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:47Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0133 (cloid idempotent identity), STR-0138 (pre-sign / replay)
- **Hash note:** SHA-256 in SOURCE_MANIFEST.md is of this saved extract.

## Verbatim excerpts

> On Hyperliquid, the **100 highest nonces are stored per address**. Every new transaction must have nonce larger than the smallest nonce in this set and also never have been used before. Nonces are tracked per signer …
> Nonces must be within `(T - 2 days, T + 1 day)`, where `T` is the unix millisecond timestamp on the block of the transaction.
> **Important:** … it is strongly suggested to not reuse [API wallet] addresses. Once an agent is deregistered, its used nonce state may be pruned … previously signed actions can be replayed once the nonce set is pruned.
> For each batch … fetch and increment an atomic counter that ensures a unique nonce for the address.
> (From exchange-endpoint.md) "Client Order ID (cloid) is an optional 128 bit hex string" and `cancelByCloid` exists.

## Evidence status: VERIFIED (nonce/replay, cloid exists) · PARTIALLY_VERIFIED (cloid dedup-on-duplicate-submission)

- STR-0133 (cloid = 128-bit client order id) — CONFIRMED: cloid is an optional 128-bit hex id usable for orderStatus lookup and cancelByCloid.
- STR-0138 / idempotency — CONFIRMED (replay control): replay protection is provided by the **per-address nonce set** (100 highest, never-reused, time-windowed), not by cloid. This is the venue's idempotency/replay mechanism for signed actions.
- **PARTIALLY_VERIFIED:** Strategy calls cloid "idempotent order identity". The docs confirm cloid gives a stable *identity* (query/cancel), but do **not** explicitly state that submitting the *same cloid twice* is de-duplicated/rejected. The documented dedup/replay guarantee is the nonce, not the cloid. Phase 3 must not assume duplicate-cloid submission is silently idempotent; verify by controlled observation or SDK behavior. Flagged (no conflict) — relevant to prompt.md `<idempotency>`.
