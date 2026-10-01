# U_VERIFICATION_SUMMARY.md — Independent verification of audit findings U-1..U-8 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no Owner Gate opened; no DECISION created.**
- **Method:** each U-N re-derived from `Strategy.md` (SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`, unmodified) + cached venue evidence, per-file in `U<N>_VERIFICATION.md`. The F-1\* precedent showed the audit can over-generalize, so each claim was checked for an already-resolving rule.

## Results table

| U | Topic | Verdict | Severity (indep.) | Affected STR-* | Affected CAP-* | One-line conclusion |
|---|-------|---------|-------------------|----------------|----------------|---------------------|
| U-1 | `GrossGridEdge` undefined | **U_VERIFIED** | HIGH | STR-0193, 0179, 0197, 0273 | CAP-0013, 0011 | Binding arming edge depends on an undefined term; no closed form anywhere. |
| U-2 | No funding-bleed bound | **U_CONDITIONAL** | MED–HIGH | STR-0234, 0235, 0236, 0246, 0221 | CAP-0017, 0018, 0016 | Real only under hedge-halt/stuck exposure; sole NET-DD bound (100%) is vacuous. |
| U-3 | §5.6 N3 equality-only | **U_VERIFIED** | MEDIUM | STR-0104, 0107, 0077 | CAP-0008, 0009 | Same-group exact-equality under-approximates "no overlap"; opposite-group already handled by L503. |
| U-4 | Correction-gating contradiction | **U_VERIFIED** | HIGH | STR-0168, 0197, 0185, 0206, 0207 | CAP-0011, 0015, 0016 | Acute correction: §11.2 "unconditional" vs §9.1/§10 floor — no precedence stated. |
| U-5 | cloid "idempotent" overclaim | **U_VERIFIED** (NON_BLOCKING) | LOW | STR-0133, 0298 | CAP-0014, 0015 | Venue fact confirmed; operational path already closed by DECISION-008; wording-only residual. |
| U-6 | Closure rounding direction | **U_CONDITIONAL** | LOW–MED | STR-0248, 0290, 0247, 0303 | CAP-0018, 0013 | Direction undefined; moot at default (f = 5 lots exactly); bites when f ≠ lot-multiple. |
| U-7 | Margin mode never pinned | **U_VERIFIED** | HIGH | STR-0223/0340, 0225, 0227, 0337 | CAP-0002, 0017, 0020 | Risk arithmetic assumes cross; isolated mode invalidates it; never pinned. |
| U-8 | No REST rate budget | **U_VERIFIED** (NON_BLOCKING) | MEDIUM | STR-0176, 0133 | CAP-0001, 0015, 0002 | Gate 6 covers open-order count only; operational (throttle → fail-closed), not a decision divergence. |

## Blocking classification

- **SEMANTIC_BLOCKING_PENDING (needs an Owner Gate before Phase 7 — two compliant implementations differ observably AND resolution needs an owner/semantic choice):** **U-1** (define GrossGridEdge — arming determinism), **U-2** (whether/what funding-bleed bound — risk appetite), **U-4** (acute-correction economics precedence — survival behavior), **U-7** (pin margin mode — risk-model validity).
- **SEMANTIC_NON_BLOCKING (eligible for Phase-6 resolution with an obviously-correct fail-closed rule):** **U-3** (min-separation ε in N3), **U-5** (cloid = reconciliation identity — already governed by DECISION-008; documentation-accuracy residual), **U-6** (ceil rounding direction), **U-8** (operational REST rate budget).
- **REJECTED:** none.
- **UNDETERMINED:** none.

## Discrepancies with the audit's implicit framing (KEY deliverable)

The audit (SRC-204) frames U-1..U-8 uniformly as "undefined behavior (U)" gaps of comparable standing. Independent verification differs materially on four of them:

1. **U-2 — less severe / conditional.** The audit headline implies a broadly-unbounded funding hazard. Independently it is **CONDITIONAL**: funding *does* enter `BasketNetPnL`, the freeze trigger (STR-0235) and `TotalSystemCosts`/closure target (STR-0246); the catastrophic 6%-E₀/hr path requires a **hedge-layer halt / stuck exposure**. Under normal hedge liveness bleed is imbalance-bounded (~$8/hr). The real defect is the **absence of a funding-rate bound** plus the **vacuous 100% DD bound**, not an always-live drain.

2. **U-3 — narrower than framed.** The audit stresses **opposite-group** near-stacking. Strategy.md L503 already declares cross-group overlap "not applicable … by construction," and §5.2 step 2 cancels the exhausted traversal. The genuine residual is the **same-group exact-equality-only** N3 predicate, with **narrow reachability** — smaller than the audit's blast-radius framing.

3. **U-5 — already mitigated, NON_BLOCKING.** The audit presents an open double-execution risk ("containment, not prevention"). The venue fact is confirmed, but the **operational path is already closed by DECISION-008** (UNKNOWN_SUBMISSION + reconcile-before-retry + never assume dedup). The only residual is the immutable Strategy.md wording "idempotent," corrected at the contract/decision layer — **not an open gap**.

4. **U-6 — conditional, moot at default.** The audit says "two implementations, two closure boundaries" as if universal. At the D-16 default `f = $5 = exactly 5 lots`, so the direction is **moot**; the divergence appears **only when `f` is not an exact lot-multiple**.

For **U-1, U-4, U-7, U-8** the independent verdict **confirms** the audit's substance (all U_VERIFIED). Note: **U-8** is confirmed as an absence but reclassified as an **operational (NON_BLOCKING)** concern rather than a strategy-semantic divergence, since its consequence (throttling) is caught by the existing fail-closed freshness posture.

## Notes
- Nothing here is decided or fixed. Findings requiring an owner choice (U-1, U-2, U-4, U-7) are recorded as `SEMANTIC_BLOCKING_PENDING_VERIFICATION → VERIFIED_BLOCKING` in `U_AMB_RECORD.md` (AMB-0048..0055); each awaits a future Owner Gate, opened only under explicit instruction (per the F-1\* / OWNER_GATE_014 pattern).
- `SEMANTIC_AMBIGUITIES.md` (Phase 4.5) is untouched; all Phase-4.9 records live under `research/findings/`.
