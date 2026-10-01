# U3_VERIFICATION.md — Independent verification of audit finding U-3 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no gate opened; no DECISION created.**
- **Primary sources:** `Strategy.md` §5.2, §5.6.

## 1. Finding (verbatim, SRC-204 §1 / S-5.5)
> "N3 forbids only *exact equality*. The **opposite-group** legacy ladder survives the transition … and may near-stack against the new ladder (`0 < |p_new − p_live| ≤ 1 tick` is legal). Stated invariant ('no unintended overlap') > computable test ⇒ spec–mechanization gap."

## 2. Primary-source extraction (§5.6, Strategy.md L488–511)
> "N1. Every new level price MUST be strictly monotonic in level index …
> N2. The new Level-1 price MUST lie strictly beyond the old Cycle's terminal-level execution price … no new level price may lie within the closed interval spanned by the old Cycle's reference price and the old terminal execution price.
> **N3. No new level price may equal any still-live level price of the same group within the same Generation.**
> **Cross-group overlap is not applicable** (BU prices lie above, SL prices lie below their own references by construction)."

L490: the mechanized gate implements the v1.0 invariant "Cycle transition must not create **unintended level overlap**." §5.2 step 2 cancels the exhausted traversal's pendings before the test.

## 3. Independent derivation
N3's predicate is **equality only** (`may equal`). Thus two same-group, same-Generation prices that are `1 tick` apart (`0 < |p_new − p_live| < 1 tick` is impossible on the lattice; `= 1 tick` is legal) **pass** N3 while arguably constituting the "unintended overlap" the invariant (L490) forbids. Divergence: implementation A places a new level one tick from a live same-group order (legal per N3); implementation B rejects near-adjacency as overlap. Observable → double-fill concentration at adjacent prices. The gap is spec (L490 "no unintended overlap") vs mechanization (N3 "no exact equality").

## 4. Counter-example search (audit over-generalization check)
The audit's **opposite-group** concern is **already addressed**: L503 declares "Cross-group overlap is not applicable (BU prices lie above, SL prices lie below their own references by construction)" — opposite-group ladders are reference-separated by construction, and §5.2 step 2 cancels the exhausted traversal, so the audit's "legacy opposite-group near-stack" is largely foreclosed by the strategy text. N1 (strict monotonicity) and N2 (strictly beyond the old interval) further constrain the new ladder. **The residual, genuine gap is narrower than the audit framed:** it is the SAME-group exact-equality-only predicate in N3, and its reachability is bounded by §5.2 cancellation + fixed-bps ladder construction (a live same-group same-Generation order landing exactly one tick from a new-ladder price is an edge case, not the norm).

## 5. Verdict
**U_VERIFIED** — the N3 mechanization (exact equality) under-approximates the stated no-overlap invariant for same-group prices; real but narrow, and the opposite-group part of the audit's claim is pre-addressed by L503.

## 6. Impact
- affects_str: STR-0104 (non-overlap computable gate), STR-0107 (N3 predicate), STR-0077 (§5.2 step 4 non-overlap → BLOCKED).
- affects_cap: CAP-0008 (cycle transition), CAP-0009 (grid geometry).
- severity: audit **⚠️ (bounded blast radius)**; independently **MEDIUM**, reachability narrow.

## 7. Recommendation (PROPOSAL, not a decision)
Strengthen N3 from exact-equality to a minimum separation, e.g. `|p_new − p_live| ≥ max(1 tick, 0.1 × StepBps · p/10⁴)` for still-live same-group same-Generation orders. Justification: the fail-closed-safe direction (require separation) is deterministic and makes the computable test match the stated invariant; only the ε magnitude is a Phase-6 design choice → **SEMANTIC_NON_BLOCKING**.
