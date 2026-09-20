# STRATEGY_COVERAGE.md

- **Purpose:** Heading-by-heading coverage backbone for `Strategy.md` v2.3-final. Every heading maps to ≥1 `STR-*` requirement in `STRATEGY_CONTRACT.md`, or is explicitly marked NON_NORMATIVE. Guarantees no section is silently dropped during forensics.
- **Version:** 1.1 (Phase 1 — STEP-4 reconciled to actual emitted IDs)
- **Producer:** Claude Code (Opus 4.8), Phase 1 — Strategy Forensics.
- **Inputs:** `Strategy.md` (SRC-001, SHA-256 `085044e7…a825e18`, 1369 lines).
- **Status:** IN PROGRESS (mapping filled during STEP 4).
- **Validation status:** Heading list extracted deterministically (`grep '^#{1,3} '`); line ranges computed to full 1369-line coverage.

---

## Coverage arithmetic

- Headings found: **52** (1 H1 title + 15 H2 numbered sections §1–§16 [note: no standalone "§6"→ all present] + 36 H3 subsections).
- Line span: **L1–L1369** contiguous, no gaps (each heading's range = its line to the line before the next heading; last heading to EOF L1369).

## Heading → line range → coverage

| Heading | Lines | Coverage status | STR-* IDs |
|---------|-------|-----------------|-----------|
| (title) Strategy.md — Hyperliquid Perpetual Hedge Grid Bot | L1–L81 | NON_NORMATIVE | front-matter: version/provenance/change-logs/tag-legend (identity captured in STRATEGY_SOURCE_RECORD.md) |
| §1 Executive Summary | L82–L94 | COVERED | STR-0001..STR-0004 |
| §2 Strategy Model — Formal Definitions | L95–L148 | COVERED | STR-0005..STR-0014 |
| §2.1 Naming: Soft Reset → Evolution | L149–L154 | COVERED | STR-0015 |
| §3 Canonical Identity Model | L155–L184 | COVERED | STR-0016..STR-0024 |
| §4 Generation Lifecycle | L185–L186 | NON_NORMATIVE (section header only) | — |
| §4.1 Evolution trigger — path-dependent return | L187–L231 | COVERED | STR-0025..STR-0035 |
| §4.2 Evolution Confirmation Tolerance | L232–L249 | COVERED | STR-0036..STR-0040 |
| §4.3 Generation states | L250–L271 | COVERED | STR-0041..STR-0048 |
| §4.4 One-Successor Constraint & Successor Lock | L272–L280 | COVERED | STR-0049..STR-0054 |
| §4.5 Post-Evolution Dominance | L281–L299 | COVERED | STR-0055..STR-0057 |
| §4.6 Generation 99 | L300–L307 | COVERED | STR-0058..STR-0062 |
| §4.7 Deterministic precedence (simultaneous G/C events) | L308–L338 | COVERED | STR-0063..STR-0070 |
| §5 Cycle Lifecycle | L339–L340 | NON_NORMATIVE (section header only) | — |
| §5.1 Terminal Event | L341–L355 | COVERED | STR-0071..STR-0073 |
| §5.2 Standard Cycle Transition | L356–L385 | COVERED | STR-0074..STR-0083 |
| §5.3 Cycle-Limit Disable Transition | L386–L407 | COVERED | STR-0084..STR-0090 |
| §5.4 Cycle Reference Price | L408–L427 | COVERED | STR-0091..STR-0095 |
| §5.4.1 Reference-Price Tolerance at Cycle/Generation Fire | L428–L471 | COVERED | STR-0096..STR-0100 |
| §5.5 Generation vs. Cycle — formal distinction | L472–L487 | COVERED | STR-0101..STR-0103 |
| §5.6 Ladder Non-Overlap Test | L488–L512 | COVERED | STR-0104..STR-0108 |
| §5.7 Normative Generation/Cycle scenarios | L513–L555 | COVERED | STR-0109..STR-0128 (Scenarios 01–20) |
| §6 Execution Assurance | L556–L557 | NON_NORMATIVE (section header only) | — |
| §6.1 State pipeline | L558–L571 | COVERED | STR-0129..STR-0132 |
| §6.2 Hyperliquid mechanisms relied on | L572–L575 | COVERED | STR-0133..STR-0134 |
| §6.3 Precision | L576–L581 | COVERED | STR-0135..STR-0138 |
| §7 Grid Geometry | L582–L583 | NON_NORMATIVE (section header only) | — |
| §7.1 Distance model | L584–L650 | COVERED | STR-0139..STR-0150 |
| §7.2 Protection Level Locking → Fillability-Gated Unlock | L651–L654 | COVERED | STR-0151..STR-0152 |
| §7.3 Position sizing | L655–L699 | COVERED | STR-0153..STR-0162 |
| §8 Pending Order & Fillability Architecture | L700–L764 | COVERED | STR-0163..STR-0181 |
| §9 Emergency Execution & Level Skip | L765–L766 | NON_NORMATIVE (section header only) | — |
| §9.1 Emergency Execution | L767–L788 | COVERED | STR-0182..STR-0187 |
| §9.2 Maker→Taker re-evaluation | L789–L801 | COVERED | STR-0188..STR-0189 |
| §9.3 Level Skip Model | L802–L806 | COVERED | STR-0190..STR-0192 |
| §10 Execution Economics | L808–L836 | COVERED | STR-0193..STR-0198 |
| §11 Hedge & Mirroring | L837–L838 | NON_NORMATIVE (section header only) | — |
| §11.1 Expected vs. Actual Exposure | L839–L865 | COVERED | STR-0199..STR-0205 |
| §11.2 Hedge cost-awareness | L866–L876 | COVERED | STR-0206..STR-0207 |
| §11.3 Mirroring | L877–L892 | COVERED | STR-0208..STR-0211 |
| §11.4 Partial fill ↔ hedge interaction | L893–L898 | COVERED | STR-0212..STR-0214 |
| §12 Risk Model | L899–L900 | NON_NORMATIVE (section header only) | — |
| §12.1 Range Survivability | L901–L978 | COVERED | STR-0215..STR-0230 |
| §12.2 Two-Layer framing (restated) | L979–L986 | COVERED | STR-0231..STR-0233 |
| §13 Basket Lifecycle | L987–L988 | NON_NORMATIVE (section header only) | — |
| §13.1 PnL | L989–L997 | COVERED | STR-0234..STR-0236 |
| §13.2 States | L998–L1006 | COVERED | STR-0237..STR-0238 |
| §13.3 Freeze | L1007–L1010 | COVERED | STR-0239..STR-0242 |
| §13.4 Closure | L1011–L1084 | COVERED | STR-0243..STR-0256 |
| §14 Parameter Reference | L1085–L1183 | COVERED | STR-0257 (global rule) + STR-0258..STR-0292 (all param rows + allowlist) |
| §15 State Machine Invariants | L1184–L1214 | COVERED | STR-0293..STR-0315 (23 base invariants) + STR-0316..STR-0335 (amendment 1–20) |
| §16 Dynamic Defaults Pending Calibration | L1215–L1369 | COVERED | STR-0336..STR-0343 |

> The STR-* ID ranges are the authoritative binding in `STRATEGY_CONTRACT.md`.

## STEP-4 reconciliation (actual vs. planned)

- **Total emitted:** 343 requirements (STR-0001 … STR-0343), contiguous, no duplicates, no gaps (verified by script).
- **Every COVERED heading maps to ≥1 STR-* id; every other heading is explicitly NON_NORMATIVE.** Zero headings have empty coverage; no coverage was invented.
- **Deviations from the initial planned ranges:** §1–§13 emitted exactly as planned. Only the tail three sections were renumbered to their final contiguous IDs (§14 → STR-0257..0292, §15 → STR-0293..0335, §16 → STR-0336..0343), because §14 holds 34 parameter rows + global rule + allowlist (36 entries) and §15 holds 23 base + 20 amendment invariants (43 entries) — larger than the first estimate. Twenty forward-references written before renumbering were corrected (see STRATEGY_CONTRACT.md STEP 5).
- **NON_NORMATIVE headings:** the title/front-matter block (L1–L81) and the bare section headers §4, §5, §6, §7, §9, §11, §12, §13 (heading-only; their normative content lives in numbered subsections).
