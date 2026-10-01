# OPEN_MIGRATION_QUESTIONS — Phase M

> Claim hygiene per `docs/prompts/PROMPT_MIGRATION_FREEBUFF.md` Part 0.10.
> Generated: 2026-10-01T12:20:34Z (UTC).
> Anything uncertain about the migration is listed here. Nothing here blocks
> the Phase-M exit criteria; items are for the Owner/Reviewer.

## Q1 — `prompt.md` merge-conflict marker (source repo)

- **Observation:** line 1 of `prompt.md` in hypergrid @ `46b42b0` is
  `<<<<<<< HEAD` (`head -c 120 prompt.md | cat -A`, 2026-10-01).
- **Action taken:** copied verbatim by the merge; NOT resolved (Part 2
  instruction).
- **Question:** does the Owner want the marker resolved in a later phase, or
  kept as historical record?
- Source class OBSERVATION; status VERIFIED (marker present, untouched).

## Q2 — OWNER_GATE files that mention Hyperliquid (none moved)

- **Observation:** `grep -ci hyperliquid` over `research/decisions/OWNER_GATE_*.md`
  → hits only in OWNER_GATE_005.md (1), OWNER_GATE_020.md (1),
  OWNER_GATE_021.md (1); zero hits in the other 18 gates.
- **Classification (read in full, 2026-10-01):**
  - GATE-005: maintenance-margin model decision — the resolution ("use the
    venue's real per-asset maintenance schedule / liquidationPx") is
    venue-generic; HL appears only as the evidence base. Strategy-semantic.
  - GATE-020: production-language choice — HL appears only as an SDK-ecosystem
    note inside a consequences bullet. Not venue-specific.
  - GATE-021: runtime/UI + logging stack — HL appears only as "official SDK is
    REFERENCE, not a runtime dependency" for the venue-client bullet. The
    decision itself is venue-agnostic.
- **Action taken:** per Step 6.2 ("If unsure whether a gate is
  venue-specific → leave it and list it"), all three STAYED in
  `research/decisions/`; `research/decisions/_legacy/` is empty.
- **Question:** confirm the classification, or mark any of the three as
  legacy in a later phase.
- Source class OBSERVATION; status VERIFIED (files read in full).

## Q3 — Renamed-class (D) strings intentionally left as `hypergrid`

- **Observation:** after Step 7d, `git grep -n -i hypergrid -- src tests
  pyproject.toml` returns exactly 2 hits (7e criterion met):
  1. `src/astergrid/__init__.py:1` — docstring: "hypergrid — deterministic,
     AI-independent Hyperliquid hedge-grid runtime."
  2. `tests/test_core_no_logging.py:33` — assert message: "expected at least
     hypergrid/core/__init__.py".
- **Classification:** prose only. Neither is hashed, serialized, written to
  the event log, used as a domain separator, or compared in a golden fixture
  (7b check). Both were left per "Rewrite only classes (A), (B), (C)".
- **Question:** should the docstring be modernized to say `astergrid` in a
  later docs pass? (Cosmetic only.)
- Source class OBSERVATION; status VERIFIED (7e re-grep output quoted in
  `RENAME_INVENTORY.md` §4).

## Q4 — Script extensions beyond the prompt's exact patterns

- **Observation:** the prompt's 7d script patterns (pat_import / pat_dotted /
  pyproject rules) miss two functional string classes in `tests/`:
  bare exact-string `"hypergrid"` in `tests/test_smoke.py:8` and
  `tests/test_core_no_logging.py:41`. Left unreplaced, the post-rename suite
  would fail (import smoke test + stdlib-guard comparison).
- **Action taken:** `research/migration/rename_package.py` adds one evidence-
  anchored extension (bare-string rewrite in `tests/` only). Both files were
  read in full before the change; both strings are import-name references,
  not domain data.
- **Question:** none open — flagged for Reviewer awareness only.
- Source class OBSERVATION + ASSUMPTION (that renaming these is the intended
  semantics of "rewrite class (C)"); status VERIFIED by 7f (544 passed,
  mypy/ruff identical, Strategy SHA unchanged).

## Q5 — Source HEAD equals expected; no divergence

- **Observation:** source HEAD `46b42b095e10f77dbac853c976527764faa9fde1`
  matches the prompt's expectation (docs-only commit over `6a854c5`; code
  identical). Recorded for completeness; no open question.
- Source class OBSERVATION; status VERIFIED.

## Q6 — Tooling

- **Observation:** no optional tool (paper-clip, Graphify, Spec-Kit) was
  needed at any step; per Part 0.11 the default NOT_APPLICABLE applies and no
  `research/tooling/TOOLING_DECISION.md` was created.
- Source class OBSERVATION; status VERIFIED.

## Q7 — Missing tools / environment

- **Observation:** none. pytest 9.1.1 / mypy 2.3.1 / ruff 0.16.6 were already
  installed; the package itself is not pip-installed (pytest runs via
  `pythonpath = ["src"]`), so no editable reinstall was needed at 7f.
- Source class OBSERVATION; status VERIFIED (`pip show hypergrid` → not
  found).
