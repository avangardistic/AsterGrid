# MIGRATION — hypergrid → AsterGrid, Phase M (import + rename)

> Claim hygiene per `docs/prompts/PROMPT_MIGRATION_FREEBUFF.md` Part 0.10.
> Generated: 2026-10-01T12:20:34Z (UTC).
> Detailed numbers, commands, and statuses: `SOURCE_PROVENANCE.md`,
> `RENAME_INVENTORY.md`, `OPEN_MIGRATION_QUESTIONS.md`.

## 1. Identity

| Item | Value | Source class | Status |
|---|---|---|---|
| Source repo + commit | `github.com/avangardistic/hypergrid` @ `46b42b095e10f77dbac853c976527764faa9fde1` (`main`) | OBSERVATION | VERIFIED |
| Target repo | `github.com/avangardistic/AsterGrid`, branch `migration/hypergrid-import` from `origin/arena/01a0f73c-astergrid` (`e6bf013`) | OBSERVATION | VERIFIED |
| Merge commit | `9c4989d44d6f7de23f689619e94fa412ef2ff01d` (`--allow-unrelated-histories --no-ff`, no conflicts) | OBSERVATION | VERIFIED |
| Package rename | `hypergrid` → `astergrid` (directory `src/hypergrid` → `src/astergrid` via `git mv`; imports/pyproject via `research/migration/rename_package.py`) | OWNER_DECISION (prompt Step 7) | VERIFIED |

## 2. Reason (why migrate)

Hyperliquid is one-way only: it has no hedge mode (§2 requires BU/SL both
live simultaneously), no mirroring (§11.3), and no per-side exposure
derivatives (§11.1 ExposureDelta per side). The strategy therefore cannot run
on Hyperliquid as venue. The Owner selected ASTER (DEX, hedge-native).
(Source class: OWNER_DECISION — recorded in `ASTERGRID_HANDOFF.md` and
`docs/contract/CONTRACT_DELTA_ASTER.md` §1–2; status VERIFIED as an owner
decision, engine-behavior claims inside those documents are out of Phase-M
scope.)

## 3. Decision

- Import the hypergrid repository verbatim (history preserved) into AsterGrid
  on top of the ASTER docs branch (OWNER_DECISION, prompt Steps 1–4).
- Rename the Python package `hypergrid` → `astergrid` (OWNER_DECISION, Step 7).
- Everything venue-specific that was Hyperliquid-bound is relocated, not
  deleted (Step 6): `research/sources/hyperliquid/` →
  `research/sources/_legacy_hyperliquid/` (21 files, `git mv`).
- What stays venue-agnostic: the entire deterministic core
  (`src/astergrid/core/**` — event model, append-only log, canonical JSON,
  pure fold, transitions, pass engine), the config models, the runtime
  logging shell, `adapters/` (stub only — `__init__.py`), all tests, and
  `Strategy.md` (SHA-256 unchanged: `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`).

## 4. What will change later — pointer, not re-derivation

The ASTER-specific engine/contract work is defined in:

- `docs/contract/CONTRACT_DELTA_ASTER.md` — owner decisions and the contract
  delta: two-sided exposure (G-1, amends the STR-0200 reading), source of
  truth (G-2, amends DECISION-002), startup hedge-mode gate (G-3),
  authentication V3 (G-4), §6.2/§13.4/§9 order and closure semantics under
  hedge mode. It supersedes, for the ASTER venue, the Hyperliquid-specific
  readings of STR-0200, DECISION-002, §11.1, §6.2, §6.3, §10, §13.4.
- `docs/ROADMAP.md` — phase plan; the venue port (former 7h-5a-HL, abandoned)
  is now Phase P3 "7h-5a-ASTER" (two parts), preceded by contract (P1) and
  engine delta (P2) phases; new startup assertions land with the engine
  phases.

This document intentionally does NOT re-derive those contents. (OWNER_DECISION,
prompt Step 8.2; status VERIFIED as pointers — the referenced files exist in
the working tree, checked via `test -f` in Step 4.)

## 5. Phase history (copied verbatim from the migration prompt)

| Phase | Commit | Deliverable |
|---|---|---|
| 0–6c | various | design + research (no runtime code) |
| 7a | `2e886f0` | scaffolding (pyproject, config, logging) |
| 7b | `0219b26` | event model + append-only log + canonical JSON |
| 7c | `048548f` | state + pure fold |
| 7d | `d51fb21` | P0–P6 skeleton + P2/P3/P4 (locks + precedence) |
| 7e | `141f4e1` | §4 Evolution trigger + ST-15 successor lock |
| 7f | `c2ad43f` | §5 Cycle lifecycle + reference capture + non-overlap |
| 7g-1 | `6ee967d` | §7.1 geometry + §7.2 protection locking + ST-04 |
| 7g-2 | `c916a71` | §7.3 sizing + caps + D-14 helpers |
| 7g-3a | (merged) | §11.1 exposure derivatives + ST-07/08/09 |
| 7g-3b | (merged) | §11.2/§11.3 hedge + mirroring + ST-17/19 |
| 7h-1 | (merged) | P0 real + P1 real + ST-04 completion |
| 7h-2 | `a8c2d00` | §8 arming gates + ST-05 + ST-12 |
| 7h-3 | `7489848` | §9 submission + remainder + emergency + skip + cancel selector |
| 7h-4a | `0d6748f` | §12.1 bounds + three-layer breach + ST-17/20/21/22 |
| 7h-4b-1 | `e36ff02` | §10 economics + §5.2 step-8 ladder issuance |
| cleanup ruff | `43e3170` | ruff-format on 9 pre-existing files |
| 7h-4b-2 | `6a854c5` | P6-real + coupling + 3-tuple + PassReport sub-decisions |
| 7h-5a-HL | abandoned | Hyperliquid venue port — venue is one-way only |
| 7h-5a-ASTER | later phase | see `docs/ROADMAP.md` (P3) |

### Verification of the "(merged)" rows and existing hashes (OBSERVATION, added per Step 8 instruction — the table text above is unaltered)

Verified with `git log --oneline 9c4989d^2 | cat` over the imported hypergrid
history (2026-10-01, this workspace; source class OBSERVATION; status
VERIFIED):

- 7g-3a "(merged)" → commit `0b4204e` — subject `phase-7g-3a: exposure derivatives (§11.1) + acute predicate + ST-07/08/09 typing`
- 7g-3b "(merged)" → commit `1ac0652` — subject `phase-7g-3b: P1 real wiring + Fix-1 … + §11.2 hedge urgency/intent + §11.3 mirror eligibility/intent-shape … + ST-19/ST-23 typing + first ST-07/08/09 writer`
- 7h-1 "(merged)" → commit `ebf4a1a` — subject `phase-7h-1: real P0 + ST-04 (fill/lifecycle) + ST-19 population + p1-markers projection (closes 7g-3b seam)`
- Hashes quoted in the table (`2e886f0`, `0219b26`, `048548f`, `d51fb21`, `141f4e1`, `c2ad43f`, `6ee967d`, `c916a71`, `a8c2d00`, `7489848`, `0d6748f`, `e36ff02`, `43e3170`, `6a854c5`) all resolve in the imported history with matching subjects.

## 6. Non-goals (explicit)

- No ASTER adapter, endpoint, signing, exposure, or engine work (prompt scope
  statement; OWNER_DECISION).
- No edits to `src/astergrid/operator/` or `src/astergrid/runtime/` content
  (Step 6.3: recorded only; no Hyperliquid-specific content found — see
  `RENAME_INVENTORY.md` §3).
- No edits to `Strategy.md` (Part 0.1; SHA-verified unchanged).
- No resolution of the `prompt.md` merge-conflict marker (Part 2; copied
  verbatim; recorded in `OPEN_MIGRATION_QUESTIONS.md` Q1).
- No adoption of optional tooling (Part 0.11 — `research/tooling/
  TOOLING_DECISION.md` not needed: no optional tool was even considered
  necessary during Phase M).
- No push, no merge to any main/default branch (Part 0.7).
