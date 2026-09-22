# U5_VERIFICATION.md — Independent verification of audit finding U-5 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no gate opened; no DECISION created.**
- **Primary sources:** `Strategy.md` §6; cached venue evidence (exchange-endpoint, signing, nonces); `DECISION_REGISTER.md` DECISION-008.

## 1. Finding (verbatim, SRC-204 §1 / S-6.2)
> "venue documents cloid as *identity/lookup/cancel* only; replay protection is the **nonce set**; duplicate-cloid dedup is **not documented**. 'Idempotent' overclaims. A retry-after-timeout may execute twice …"

## 2. Primary-source extraction
- **Strategy.md §6 (L574):** "`cloid` (128-bit client order ID, **idempotent order identity**) · REST `POST /exchange` ack …".
- **Venue (`page-exchange-endpoint.md`, `page-signing.md`):** cloid = optional 128-bit client order id for lookup / cancel-by-cloid; **replay protection = per-address nonce set** (100 slots, T−2d…T+1d); **duplicate-cloid dedup is NOT documented** (recorded in SOURCE_MANIFEST SRC-119 / AA-11).

## 3. Independent derivation
The venue nowhere documents that submitting two orders with the same cloid is deduplicated. Therefore the word "idempotent" in §6 L574 asserts a property the venue does not guarantee: a retry after an ambiguous timeout could place a second live order (double execution). POSITION_VERIFIED (delta from clearinghouseState) would later detect the mismatch and fail-close — containment, not prevention. The **observation** (venue documents identity only) is factually correct.

## 4. Counter-example search (is it already resolved?)
The **operational** risk is already governed by **DECISION-008** (from OWNER_GATE_007, Option B): on ambiguous submission enter `UNKNOWN_SUBMISSION`; persist `intent+cloid` before any side effect; reconcile via `orderStatus`(by cloid)+`openOrders`+`userFills`+`clearinghouseState` **before any new side effect**; attach `expiresAfter`; **never assume cloid-based dedup**. STR-0298 (cloid persisted BEFORE network submission) supports this. So the runtime path is already closed at the decision layer — the double-execution window is reconcile-bounded, not open. What remains is only the **immutable Strategy.md wording** "idempotent," which the contract/decision layer already corrects. Audit framing ("containment, not prevention; window is real") is accurate but its residual is **already mitigated**, not an open gap.

## 5. Verdict
**U_VERIFIED** — the audit's factual claim (venue documents identity, not dedup; "idempotent" overclaims) is confirmed against primary venue evidence. **However it is NON_BLOCKING:** the operational path is already resolved by DECISION-008; the only residual is immutable-text wording, corrected downstream.

## 6. Impact
- affects_str: STR-0133 (venue mechanisms — cloid), STR-0298 (cloid persisted before submission).
- affects_cap: CAP-0014 (order construction / cloid), CAP-0015 (execution / reconciliation).
- severity: audit **⚠️/U**; independently **LOW** (mitigated by DECISION-008; residual is wording only).

## 7. Recommendation (PROPOSAL, not a decision)
No new gate needed. Record (contract/decision layer, not Strategy.md) that `cloid` is a **reconciliation identity**, idempotency **established** via `orderStatus`, never **assumed** — i.e. keep DECISION-008 as the governing rule and annotate STR-0133 in a future contract pass if desired. Justification: the semantic risk is already closed; only documentation accuracy remains → **SEMANTIC_NON_BLOCKING**.
