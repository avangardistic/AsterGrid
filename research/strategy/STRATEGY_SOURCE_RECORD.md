# STRATEGY_SOURCE_RECORD.md

- **Purpose:** Record the canonical Strategy source of truth for this repository — its identity, integrity hash, version, and provenance — so every later artifact traces back to an immutable, verified anchor.
- **Version:** 1.0 (Phase 0)
- **Producer:** Claude Code (Opus 4.8), Phase 0 — Repository / Strategy Ingestion.
- **Inputs:** `Strategy.md` (root), `prompt.md` (root, authority for source governance).
- **Source references:** `prompt.md` `<strategy_authority>`, `<strategy_forensics>`, `<source_governance>`.
- **Status:** ACCEPTED (Phase 0).
- **Validation status:** Hash and byte size computed deterministically (PowerShell `Get-FileHash SHA256`); version string read verbatim from file header; repository tree confirms no competing candidate.

---

## 1. Canonical strategy file

| Field | Value |
|-------|-------|
| Canonical filename | `Strategy.md` |
| Path | `C:\Users\Avangard\Desktop\hypergrid\Strategy.md` (repo root) |
| SHA-256 | `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18` |
| Byte size | `92686` bytes |
| Line count | **1368** — see dual record below |
| Version string (verbatim) | `Version 2.3-final — Canonical Specification (base v2.2 + approved decisions D-07(F), D-09(CAL), D-12…D-15 + dynamic defaults D-16/D-17)` |
| Status string (verbatim) | `FINAL — APPROVED WITH DYNAMIC DEFAULTS (D-16/D-17; owner-overridable, calibration pending).` |
| Source class | STRATEGY_SOURCE (authoritative for strategy semantics) |
| Mutability | **IMMUTABLE** — MUST NEVER be modified, rewritten, normalized, or reinterpreted. File is currently read-only (`r--r--r--`) on disk. |
| Retrieval / verification date | 2026-09-20 |

**Line-count dual record (authoritative; Phase 1.1, owner-verified):**

```
line_count_method: (Get-Content Strategy.md).Count   # 1-based, standard
line_count: 1368
line_count_notes: |
  Phase 0 recorded 1369 via (Get-Content -Raw).Split("\n").Count, which
  appends a trailing empty element for the file's final newline. The
  standard 1-based count is 1368 (Phase 1.1, owner-verified). All
  `source_lines` fields in STRATEGY_CONTRACT.md are interpreted against
  1368 (1-based). SHA-256 unchanged; no content change.
```

Method cross-check (owner-run, 2026-09-20): (a) `(Get-Content).Count` = **1368** (authoritative, 1-based); (b) `(Get-Content -Raw).Split("`n").Count` = 1369 (adds 1 for trailing-newline empty element — source of the Phase 0 value); (c) `Measure-Object -Line` = 1090 (**DISCARD** — skips blank lines, false reading); (d) byte size = 92686 (matches Phase 0). SHA-256 unchanged → file is unmodified.

## 2. Provenance summary (as stated in the Strategy.md header, lines 3–6)

`Strategy.md` v2.3-final is a merge, with full traceability, of:

- `STRATEGY.md` v1.0 (base) and `AMEND-STRATEGY.md` (v2.0 run: 25 conflicts, resolution table, audit), producing v2.2; then
- the approved owner decision records:
  - `OWNER-DECISION-ANSWER-SHEET.md` — decisions **D-01…D-08**
  - `OWNER-DECISIONS-D09-D11.md` — **D-09, D-10, D-11** (v2.2 run)
  - `OWNER-DECISIONS-REMAINING.md` — **D-07(F), D-12, D-13, D-14, D-15**
- dynamic defaults **D-16** (three derived dynamic formulas replacing prior temporary defaults) and **D-17** (§5.4.1 reference-price tolerance), tagged `[DYNAMIC — CALIBRATION PENDING]` / `[DYNAMIC-CALIBRATABLE]`.

Every merge decision is traceable to its decision ID in Strategy.md **§14 Parameter Reference**. Superseded upstream artifacts are stated to be archived in `history/` (non-authoritative); **`history/` does not currently exist in this repository** (see §5).

> NOTE: The upstream source files listed above (`STRATEGY.md`, `AMEND-STRATEGY.md`, the three decision records) are **not present** in this repository. Only the merged canonical `Strategy.md` exists here. They are referenced by the header for provenance only and are non-authoritative relative to `Strategy.md`.

## 3. Owner decision records referenced (D-01 … D-17)

D-01 traversal-verified return level (deferred-not-cancelled) · D-02 POSITION_VERIFIED strategy fill, hedge orders ineligible · D-03 `EvolutionConfirmationSeconds = 60` · D-04 fail-closed on skipped/partial return · D-05 origin/traversed group is Dominant · D-06 `BasketNetProfitClosureTarget` formula · D-07 / D-07(F) `ResidualExposureToleranceAtClosure` derived form · D-08 `MaxGenerations = 99`, `MaxCyclesPerGeneration = 99` · D-09 Groups A–E numeric approvals · D-10 `ArmPolicy {AUTO,SEMI,WEBHOOK}` · D-11 REMOVED (`[SD]` residual-risk annotation kept) · D-12 `MaxLevelNotionalDominant` cap · D-13 `MaxBasketNotional` inputs · D-14 `MaxActiveGenerations`/`MaxActiveCycles` definitions · D-15 `TotalSystemCosts` window = lifetime-to-date · D-16 three dynamic default formulas · D-17 §5.4.1 reference-price tolerance.

## 4. Tag legend (preserve semantics EXACTLY — Strategy.md §Change-log tag legend)

| Tag | Name | Meaning (authority handling per `prompt.md` `<strategy_authority>`) |
|-----|------|--------------------------------------------------------------------|
| `[SD]` | SOURCE-DERIVED | Traceable to GridEA Path B's `STRATEGY.md`. Document-wide `[SD]` residual-risk annotation is in force (D-11): reflects *described*, not code-verified, behavior. |
| `[UR]` | USER-REQUIREMENT | Stated directly by the Strategy Owner. **Strategy-authoritative** where explicitly defined. |
| `[HC]` | HYPERLIQUID-CONSTRAINT | Venue-dependent claim; must stay traceable to current Hyperliquid evidence; may require re-verification against the live venue (Phase 2). |
| `[DD]` | DESIGN-DECISION | The document's own architectural choice. **Strategy-authoritative** where explicitly defined. |
| `[OQ]` | OPEN-QUESTION | Unresolved; implementation must not silently guess. (No `[OQ]` remains open in v2.3-final; the v1.0 §4.4 OQ is recorded closed in §16.) |
| `[TEMP]` | TEMPORARY-DEFAULT | Derived placeholder; overridable by owner; superseded by calibration + owner confirmation. Historical — replaced by D-16 dynamic formulas. |
| `[DYN]` | DYNAMIC-DEFAULT | Derived formula over already-defined parameters (no new free parameters). Tagged `[DYNAMIC — CALIBRATION PENDING]` (D-16) or `[DYNAMIC-CALIBRATABLE]` (D-17). Proposal-only; must NOT be frozen to an arbitrary constant. |

Additional rule-status tags used in the document (recorded for completeness): `[DEFINED]` (fully specified, no owner input needed) and `[DECISION_REQUIRED]` (specified but gated on a §14 entry; while gated → BLOCKED/fail-closed). Strategy.md states **no rule is currently gated**; the only non-`[DEFINED]` values are the four dynamic defaults (D-16 ×3, D-17 ×1).

## 5. Canonicity determination

- The repository tree contains exactly two non-`.git` files: `Strategy.md` and `prompt.md`.
- **No other strategy candidate file exists** in the repository (no `STRATEGY.md`, no `AMEND-STRATEGY.md`, no backups, no renamed copies, no `history/`).
- Therefore `Strategy.md` is unambiguously the canonical strategy source; no de-duplication or non-merge candidate-selection was required.

## 6. Immutable-handling obligations (from `prompt.md`)

Once canonical: read completely (done), hash (done), record version (done), **never modify**, never rewrite meaning, never silently normalize ambiguities, never let architecture convenience redefine it. This record is a *derived* artifact and is never itself the authority.

## 7. Revision log (append-only)

- **2026-09-20 — Phase 0:** initial record; line count 1369 (via `(Get-Content -Raw).Split("\n").Count`; +1 trailing-newline offset). Byte size 92686; SHA-256 `085044e7…a825e18`.
- **2026-09-20 — Phase 1.1:** line count corrected to **1368** (standard 1-based method `(Get-Content).Count`; owner-verified). Byte size and SHA-256 **unchanged** across both phases (no content change). All `source_lines` in `STRATEGY_CONTRACT.md` interpreted as 1-based against 1368; Phase 1.1 sampled 6 requirements (first STR-* of §§3,4,5,9,13,15 = STR-0016/0025/0071/0182/0234/0293) — all PASS.
