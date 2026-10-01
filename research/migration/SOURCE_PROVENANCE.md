# SOURCE_PROVENANCE — Phase M (hypergrid → AsterGrid import)

> Claim hygiene per `docs/prompts/PROMPT_MIGRATION_FREEBUFF.md` Part 0.10.
> Every claim carries source class, anchor (command or file), and status.
> Generated: 2026-10-01T12:20:34Z (UTC, `date -u '+%Y-%m-%dT%H:%M:%SZ'`).

## 1. Source repo (hypergrid)

| Item | Value | Source class | Anchor | Status |
|---|---|---|---|---|
| URL | `https://github.com/avangardistic/hypergrid` (private) | CODEBASE_SOURCE | `git remote -v` in `../hypergrid-src` | VERIFIED |
| Branch | `main` | CODEBASE_SOURCE | `git branch --all` | VERIFIED |
| HEAD | `46b42b095e10f77dbac853c976527764faa9fde1` | OBSERVATION | `git rev-parse HEAD` → `46b42b095e10f77dbac853c976527764faa9fde1` | VERIFIED |
| HEAD subject | `docs: merge-gate protocol (standing roles + verdict rule)` (2026-09-27T08:30:26+03:30) | OBSERVATION | `git log -1 --format='%H %cI %s'` | VERIFIED |
| Expected HEAD per prompt | `46b42b0` — matches actual | OWNER_DECISION (expected) vs OBSERVATION (actual) | Part 2 of the prompt; `git rev-parse HEAD` | VERIFIED |
| Clone location | `C:/Users/Avangard/Desktop/hypergrid-src` (sibling of AsterGrid) | OBSERVATION | `git clone` executed 2026-10-01, fresh clone | VERIFIED |

## 2. Strategy.md immutability anchor

| Item | Value | Source class | Anchor | Status |
|---|---|---|---|---|
| SHA-256 | `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18` | OBSERVATION | `sha256sum Strategy.md` (hypergrid-src, pre-merge; and AsterGrid, post-merge and post-rename) — identical | VERIFIED |
| Expected SHA per prompt | `085044e7…` — matches | OWNER_DECISION | Part 2 of the prompt | VERIFIED |
| Size / lines | 92,686 bytes / 1,368 lines | OBSERVATION | `stat -c '%s' Strategy.md`; `wc -l < Strategy.md` | VERIFIED |
| Edits to Strategy.md | none | OBSERVATION | SHA identical across Steps 3/4/5/7f; `git grep -i hypergrid -- Strategy.md` not run (file excluded from inventory by instruction; file itself untouched by all steps) | VERIFIED |

## 3. Step 3 baselines (source tree, `../hypergrid-src`, Python 3.14.7)

| Check | Result | Anchor (exact command) | Status |
|---|---|---|---|
| pytest | `544 passed in 7.19s` | `python -m pytest -q` | VERIFIED |
| mypy `--strict src` | `Success: no issues found in 58 source files` | `python -m mypy --strict src` | VERIFIED |
| mypy `--strict src tests` | `Found 119 errors in 17 files (checked 140 source files)` (all in `tests/`) | `python -m mypy --strict src tests` | VERIFIED |
| ruff | `All checks passed!` | `python -m ruff check src tests` | VERIFIED |
| Tool versions | pytest 9.1.1, mypy 2.3.1, ruff 0.16.6 | `python -m pytest --version` etc. | VERIFIED |
| deps install | none required — all tools already present | `pip show hypergrid` → not installed; tools preinstalled | VERIFIED |

## 4. Step 2 — base branch in AsterGrid

| Item | Value | Source class | Anchor | Status |
|---|---|---|---|---|
| BASE | `origin/arena/01a0f73c-astergrid` | OBSERVATION | `git fetch --all --prune`; `git ls-tree -r --name-only origin/arena/01a0f73c-astergrid` lists `docs/contract/CONTRACT_DELTA_ASTER.md`; the same `git ls-tree` on `origin/aster-migration` and `origin/main` lists only `ASTERGRID_HANDOFF.md` (1 file each) | VERIFIED |
| BASE hash | `e6bf013668ef0d619ac4f836aad0a77471c0bf65` | OBSERVATION | `git rev-parse origin/arena/01a0f73c-astergrid` | VERIFIED |
| Candidate `origin/aster-migration` | does NOT contain the contract file (1 file: `ASTERGRID_HANDOFF.md`) | OBSERVATION | `git ls-tree -r --name-only origin/aster-migration` | VERIFIED |

## 5. Step 4 — merge

| Item | Value | Source class | Anchor | Status |
|---|---|---|---|---|
| Branch | `migration/hypergrid-import` from `origin/arena/01a0f73c-astergrid` | OBSERVATION | `git checkout -b migration/hypergrid-import origin/arena/01a0f73c-astergrid` | VERIFIED |
| Merge commit | `9c4989d44d6f7de23f689619e94fa412ef2ff01d` | OBSERVATION | `git rev-parse HEAD` after `git merge --allow-unrelated-histories --no-ff hg/main -m "import: hypergrid main (verbatim, history preserved)"` | VERIFIED |
| Conflicts | none (`Merge made by the 'ort' strategy.`, 239 files changed, 38,400 insertions, exit 0) | OBSERVATION | merge output captured in session log | VERIFIED |
| `hg` remote | added `../hypergrid-src`, fetched, then `git remote remove hg` — only `origin` remains | OBSERVATION | `git remote -v` after removal | VERIFIED |
| Post-merge Strategy.md SHA | `085044e7…` (unchanged) | OBSERVATION | `sha256sum Strategy.md` | VERIFIED |
| Anchor files present | `docs/contract/CONTRACT_DELTA_ASTER.md`, `docs/ROADMAP.md`, `research/aster/SOURCE_MANIFEST.md`, `ASTERGRID_HANDOFF.md` | OBSERVATION | `test -f` loop printed PRESENT for all four | VERIFIED |

## 6. Step 5 / 7f — baselines on imported tree (pre- and post-rename)

| Check | Step 5 (imported, still `hypergrid`) | Step 7f (renamed to `astergrid`) | Status |
|---|---|---|---|
| pytest | `544 passed in 6.17s` | `544 passed in 9.22s` | VERIFIED — pass count identical |
| mypy `--strict src` | `Success: no issues found in 58 source files` | `Success: no issues found in 58 source files` | VERIFIED — identical |
| mypy `--strict src tests` | `Found 119 errors in 17 files (checked 140 source files)` | `Found 119 errors in 17 files (checked 140 source files)` | VERIFIED — identical |
| ruff | `All checks passed!` | `All checks passed!` | VERIFIED — identical |
| Strategy.md SHA | `085044e7…` | `085044e7…` | VERIFIED — unchanged |

Commands for the Step 7f column: `python -m pytest -q`; `python -m mypy --strict src`; `python -m mypy --strict src tests`; `python -m ruff check src tests`; `sha256sum Strategy.md`.

## 7. Step 9 — commits created (this branch, not pushed)

| Item | Value | Source class | Anchor | Status |
|---|---|---|---|---|
| Merge commit | `9c4989d44d6f7de23f689619e94fa412ef2ff01d` | OBSERVATION | `git rev-parse HEAD` (see §5) | VERIFIED |
| Commit 1 (relocate + rename) | see final session report / `git log --oneline -6` | OBSERVATION | recorded after Step 9 execution | VERIFIED at commit time |
| Commit 2 (artifacts) | see final session report / `git log --oneline -6` | OBSERVATION | recorded after Step 9 execution | VERIFIED at commit time |
| Push status | NOT pushed; no merge to any main/default branch; Owner pushes | OWNER_DECISION | Part 0.7 of the prompt | VERIFIED (no push command executed) |
