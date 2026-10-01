# U_AMB_RECORD.md — AMB rows for verified audit findings U-1..U-8 (Phase 4.9)

- **Purpose:** durable AMB-* rows for the U findings, **without modifying** `research/strategy/SEMANTIC_AMBIGUITIES.md` (Phase 4.5 artifact). Continues numbering from AMB-0047 (F-1\*, `F1_SEMANTIC_RECORD.md`).
- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No Owner Gate opened; no DECISION created; no fix applied.**
- All eight U findings verified U_VERIFIED or U_CONDITIONAL → all get a row. No REJECTED / UNDETERMINED findings this run (subsection retained, empty).

## Verified findings (VERIFIED_BLOCKING / VERIFIED_NON_BLOCKING)

### AMB-0048 — U-1 (GrossGridEdge undefined)
- source_doc: strategy_audit.md | source_section: §1 U-1 (S-10.1)
- severity: HIGH (audit U; independently confirmed HIGH)
- summary: The binding arming edge `GrossGridEdge` has no closed-form definition anywhere in Strategy.md (single symbolic use at §10); arming is not computable as written.
- category: SEMANTIC_BLOCKING_PENDING_VERIFICATION
- mapped_to: research/findings/U1_VERIFICATION.md
- rationale: independent verification required before any Owner Gate (F-1\* pattern).
- affects_str: STR-0193, STR-0179, STR-0197, STR-0273 | affects_cap: CAP-0013, CAP-0011
- status: **VERIFIED_BLOCKING**

### AMB-0049 — U-2 (no funding-bleed bound)
- source_doc: strategy_audit.md | source_section: §1 U-2 (S-12.5)
- severity: audit HIGH; independently MEDIUM–HIGH (conditional on hedge-halt)
- summary: No risk bound rate-limits funding bleed; sole NET-drawdown bound (MaxRangeInducedDD=100%) is vacuous; catastrophic only under hedge-layer halt / stuck exposure.
- category: SEMANTIC_BLOCKING_PENDING_VERIFICATION
- mapped_to: research/findings/U2_VERIFICATION.md
- rationale: independent verification required before any Owner Gate; adding a bound + threshold is a risk-appetite decision.
- affects_str: STR-0234, STR-0235, STR-0236, STR-0246, STR-0221 | affects_cap: CAP-0017, CAP-0018, CAP-0016
- status: **VERIFIED_BLOCKING** (conditional — see U2_VERIFICATION.md §5)

### AMB-0050 — U-3 (§5.6 N3 equality-only)
- source_doc: strategy_audit.md | source_section: §1 U-3 (S-5.5)
- severity: audit ⚠️; independently MEDIUM (narrow reachability)
- summary: N3 forbids only exact same-group price equality, under-approximating the stated "no unintended overlap" invariant; opposite-group case already handled by §5.6 L503.
- category: SEMANTIC_BLOCKING_PENDING_VERIFICATION
- mapped_to: research/findings/U3_VERIFICATION.md
- rationale: independent verification required; the min-separation fix is obviously-correct/deterministic.
- affects_str: STR-0104, STR-0107, STR-0077 | affects_cap: CAP-0008, CAP-0009
- status: **VERIFIED_NON_BLOCKING**

### AMB-0051 — U-4 (correction-gating contradiction)
- source_doc: strategy_audit.md | source_section: §1 U-4 (S-8.3 / S-11.2)
- severity: audit ⚠️/U; independently HIGH (governs survival hedge in a void)
- summary: For an acute EXPOSURE_CORRECTION_INTENT with NetExpectedEdge ≤ floor, §11.2 ("unconditional") contradicts §9.1/§8-gate-10/§10 ("floor → do not attempt"); no precedence stated.
- category: SEMANTIC_BLOCKING_PENDING_VERIFICATION
- mapped_to: research/findings/U4_VERIFICATION.md
- rationale: independent verification required; the precedence choice affects survival behavior.
- affects_str: STR-0168, STR-0197, STR-0185, STR-0206, STR-0207 | affects_cap: CAP-0011, CAP-0015, CAP-0016
- status: **VERIFIED_BLOCKING**

### AMB-0052 — U-5 (cloid "idempotent" overclaim)
- source_doc: strategy_audit.md | source_section: §1 U-5 (S-6.2)
- severity: audit ⚠️/U; independently LOW (mitigated by DECISION-008)
- summary: Strategy.md §6 calls cloid "idempotent"; venue documents identity/lookup only (no dedup). Factually confirmed, but the operational path is already closed by DECISION-008; residual is immutable-text wording.
- category: SEMANTIC_BLOCKING_PENDING_VERIFICATION
- mapped_to: research/findings/U5_VERIFICATION.md
- rationale: independent verification confirms the venue fact; no new gate needed (DECISION-008 governs).
- affects_str: STR-0133, STR-0298 | affects_cap: CAP-0014, CAP-0015
- status: **VERIFIED_NON_BLOCKING**

### AMB-0053 — U-6 (closure rounding direction undefined)
- source_doc: strategy_audit.md | source_section: §1 U-6 (S-13.3)
- severity: audit ⚠️/U; independently LOW–MEDIUM (conditional)
- summary: `round_to_min_tradable_size` has no defined direction; ceil vs floor give different closure boundaries when f is not a lot-multiple; moot at the default (f = 5 lots exactly).
- category: SEMANTIC_BLOCKING_PENDING_VERIFICATION
- mapped_to: research/findings/U6_VERIFICATION.md
- rationale: independent verification required; ceil-floored-at-one-lot is the obviously-correct fix.
- affects_str: STR-0248, STR-0290, STR-0247, STR-0303 | affects_cap: CAP-0018, CAP-0013
- status: **VERIFIED_NON_BLOCKING** (conditional — see U6_VERIFICATION.md §5)

### AMB-0054 — U-7 (margin mode never pinned)
- source_doc: strategy_audit.md | source_section: §1 U-7 (R-8)
- severity: audit ⚠️/U; independently HIGH (silent risk-model invalidation)
- summary: Strategy.md never pins account margin mode; D-16 risk arithmetic assumes cross; an isolated-mode account invalidates it. Venue exposes leverage.type ∈ {cross, isolated}.
- category: SEMANTIC_BLOCKING_PENDING_VERIFICATION
- mapped_to: research/findings/U7_VERIFICATION.md
- rationale: independent verification required; which mode to pin (and asserting it) is an owner/config decision the risk model depends on.
- affects_str: STR-0223, STR-0340, STR-0225, STR-0227, STR-0337 | affects_cap: CAP-0002, CAP-0017, CAP-0020
- status: **VERIFIED_BLOCKING**

### AMB-0055 — U-8 (no REST rate budget)
- source_doc: strategy_audit.md | source_section: §1 U-8 (R-9)
- severity: audit ⚠️/U; independently MEDIUM (operational; fail-closed on staleness)
- summary: §8 gate 6 bounds only open-order count; no REST weight / pass-cadence budget exists (venue: 1200 weight/min). Operational — throttling degrades to fail-closed, not a decision divergence.
- category: SEMANTIC_BLOCKING_PENDING_VERIFICATION
- mapped_to: research/findings/U8_VERIFICATION.md
- rationale: independent verification confirms the absence; the budget is a deterministic operational policy.
- affects_str: STR-0176, STR-0133 | affects_cap: CAP-0001, CAP-0015, CAP-0002
- status: **VERIFIED_NON_BLOCKING**

## Rejected / Undetermined

*(none this run — all eight U findings verified U_VERIFIED or U_CONDITIONAL.)*
