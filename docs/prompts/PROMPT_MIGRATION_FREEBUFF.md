# Prompt for CLI agent (freebuff): Phase M — import hypergrid into AsterGrid

**You are the Executor.** Do exactly the steps below, in order. After each step, check its **Exit criterion**. If it fails, or any STOP condition fires, **stop and report** — do not improvise, do not "fix forward".

**Scope of this prompt = repository migration mechanics ONLY.**
It does NOT include any ASTER adapter, endpoint, signing, exposure, or engine work. Those are later phases (see `docs/ROADMAP.md`). Finish at Step 9 and stop.

**OS note:** the Owner works on Windows/PowerShell. Commands below are PowerShell. Where a text rewrite is needed, use the provided Python script (not `Get-Content | Set-Content`, which changes encoding/newlines).

---

## Part 0 — Binding rules

1. `Strategy.md` is **immutable**. Never edit, reformat, or re-save it. Verify its SHA-256 at the end.
2. **No `float` in `core/`** (Decimal for money, int for counts). **No `logging` in `core/`.**
3. `log_sequence` / `monotonic_counter` are allocated by the log only.
4. Canonical JSON: `sort_keys=True`; `Decimal` as `{"__decimal__": "<string>"}`; `None`/`float` rejected.
5. **Fail-closed.** Never guess, never invent defaults, never silently continue.
6. **Do not rewrite history.** No `rebase`, `reset --hard` on shared work, `commit --amend` of pushed commits, `push --force`, remote branch deletion.
7. **Do NOT push** and **do NOT merge to any main/default branch.** The Owner pushes.
8. **No count without its command.** Every number you report is accompanied by the exact command that produced it.
9. Artifacts over chat: everything material goes into files under `research/migration/`.
10. **Claim hygiene.** Each claim in an artifact carries: *source class* (`CODEBASE_SOURCE`, `OBSERVATION`, `OWNER_DECISION`, `ASSUMPTION`…), *anchor* (`file:line`, URL+timestamp, or command), *status* (`VERIFIED` / `PARTIALLY_VERIFIED` / `UNVERIFIED` / `CONFLICTED`).
11. Optional tools (paper-clip, Graphify, Spec-Kit): **do not adopt.** If you think one is needed, write `research/tooling/TOOLING_DECISION.md` (purpose, alternatives, decision, risk, reversibility) and stop for the Owner. Default = `NOT_APPLICABLE`.

## Part 1 — Multi-agent ground check (run BEFORE any git write)

Other agents may be working on the same remote. Before every git operation that writes (commit, branch, merge, checkout -b, fetch --all is fine), run and **read**:

```powershell
git status
git branch --all
git log --oneline -10 --all
git remote -v
git rev-parse HEAD
```

Never assume branch/HEAD/remote are what they were at session start. If the remote branch you are based on moved unexpectedly or a conflict appears: **stop and report; do not resolve silently.**

## Part 2 — Facts you must know (verified by the Reviewer on 2026-10-01)

- **Target repo** `github.com/avangardistic/AsterGrid` is **NOT empty**. It already contains `ASTERGRID_HANDOFF.md`, `docs/`, and `research/aster/`. Therefore **do not** "clone hypergrid and retarget the remote" (the Owner's older plan) — that would push unrelated history into a non-empty repo.
- **Source repo** `github.com/avangardistic/hypergrid` (private), branch `main`, expected HEAD `46b42b0` (docs-only over `6a854c5`; code identical). The Owner's machine has access. Record the actual hash; a different hash is not a STOP, but must be recorded.
- Expected baselines (record actuals; divergence = document, not STOP, unless the suite fails): `Strategy.md` SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18` (92,686 bytes, 1,368 lines) — **mismatch = STOP**; pytest ≈ 544 passed; mypy `--strict` errors live in `tests/`, `src/` clean; ruff clean.
- In the source repo `prompt.md` may contain a merge-conflict marker (line 1 `<<<<<<<`). **Do not "resolve" it.** Copy as-is; report it in `OPEN_MIGRATION_QUESTIONS.md`.
- In the source repo the package is `src/hypergrid/`. `adapters/` contains only `__init__.py`.
- The branch holding the Aster docs is the one that contains `docs/contract/CONTRACT_DELTA_ASTER.md`. Find it (Step 2); do not guess its name.

---

## Step 1 — Prepare two clones (siblings)

```powershell
cd C:\Users\Avangard\Desktop
git clone https://github.com/avangardistic/hypergrid.git hypergrid-src
git clone https://github.com/avangardistic/AsterGrid.git AsterGrid
```
(If either folder already exists: run Part 1 on it and reuse it — do not delete anything.)

**Exit:** both folders exist. `hypergrid-src` is on `main`.

## Step 2 — Locate the base branch in AsterGrid

```powershell
cd C:\Users\Avangard\Desktop\AsterGrid
git fetch --all --prune
git branch -r
git ls-tree -r --name-only origin/aster-migration | Select-String "CONTRACT_DELTA_ASTER"
```
Find the remote branch whose tree contains `docs/contract/CONTRACT_DELTA_ASTER.md` (check each branch with `git ls-tree -r --name-only <branch>`). Call it `BASE`. Candidates: `origin/aster-migration` or `origin/arena/01a0f73c-astergrid`.

**Exit:** exactly one `BASE` chosen and quoted, with the command that proved it. If none contains the file → **STOP**.

## Step 3 — Record source provenance (read-only on the source)

```powershell
cd C:\Users\Avangard\Desktop\hypergrid-src
git log --oneline -10
git rev-parse HEAD
Get-FileHash Strategy.md -Algorithm SHA256
(Get-Item Strategy.md).Length
python -m pytest -q
python -m mypy --strict src tests
python -m ruff check src tests
```
Quote every output. If `pip`/deps are missing, install per `pyproject.toml` dev extras and note it.

**Exit:** all values captured. `Strategy.md` SHA matches (else **STOP**).

## Step 4 — Create the migration branch in AsterGrid and import history

Run Part 1 first. Then:

```powershell
cd C:\Users\Avangard\Desktop\AsterGrid
git checkout -b migration/hypergrid-import BASE      # BASE from Step 2, e.g. origin/aster-migration
git remote add hg ..\hypergrid-src
git fetch hg
git merge --allow-unrelated-histories --no-ff hg/main -m "import: hypergrid main (verbatim, history preserved)"
```
- Do not use `--squash`, rebase, or cherry-pick.
- If the merge reports **any conflict** (e.g. same-named `README.md`, `.gitignore`, `research/`): **STOP**, `git merge --abort`, report the conflicting paths. Do not resolve.
- Afterwards `git remote remove hg`.

**Exit:** merge commit exists; `Get-FileHash Strategy.md` equals the Step 3 value; `docs/contract/CONTRACT_DELTA_ASTER.md`, `docs/ROADMAP.md`, `research/aster/SOURCE_MANIFEST.md`, `ASTERGRID_HANDOFF.md` are all still present (list them with `Test-Path`).

## Step 5 — Re-run the baseline on the imported tree (still package `hypergrid`)

```powershell
python -m pytest -q
python -m mypy --strict src tests
python -m ruff check src tests
```
**Exit:** same results as Step 3. Different → **STOP** and report (an import must not change behaviour).

## Step 6 — Strip/relocate Hyperliquid-only material (move, never delete)

1. If `research/sources/hyperliquid/` exists → `git mv research/sources/hyperliquid research/sources/_legacy_hyperliquid`.
2. For `research/decisions/OWNER_GATE_*.md`: move **only** those that are clearly Hyperliquid-endpoint-specific into `research/decisions/_legacy/` (`git mv`). Strategy-semantic gates stay. If unsure whether a gate is venue-specific → leave it and list it in `OPEN_MIGRATION_QUESTIONS.md`.
3. `src/hypergrid/adapters/` stays as-is (only `__init__.py`). `src/hypergrid/operator/` and `runtime/`: do **not** edit; just record (with `Get-ChildItem -Recurse`) whether they contain anything Hyperliquid-specific.
4. Create `research/sources/aster/` with a `README.md` stating: "Authoritative venue sources are in `research/aster/` (see `SOURCE_MANIFEST.md`)." (No other content.)

**Exit:** `git status` shows only renames + the new README; no file content changed.

## Step 7 — Rename the Python package `hypergrid` → `astergrid` (HIGH-RISK STEP, read carefully)

A naive global text replace is **forbidden**: the string `hypergrid` may occur inside serialized constants, hash-chain domain separators, event-type names, golden/fixture files, or the repo URL. Changing those would silently alter hashes or break replay.

7a. **Inventory first** (read-only), and save it to `research/migration/RENAME_INVENTORY.md`:
```powershell
git grep -n -i "hypergrid" -- . ":(exclude)Strategy.md" | Out-File research/migration/_rename_all_hits.txt -Encoding utf8
```
Classify every hit into: (A) `import`/`from hypergrid...` statements; (B) `pyproject.toml` package/discovery/entry-point; (C) module-path strings in tests (e.g. `"hypergrid.core..."` used in mock patches/`importlib`); (D) **anything else** (constants, docstrings, URLs, fixtures, docs/research prose).
Record counts **with the grep command that produced each count**.

7b. **STOP condition:** if any (D) hit is inside `src/` or `tests/` *and* is a string that is hashed, serialized, written to the event log, used as an event-type/domain separator, or compared in a golden fixture → **STOP** and report the exact `file:line`. Do not rename.

7c. Rename the directory with git: `git mv src\hypergrid src\astergrid`.

7d. Rewrite **only classes (A), (B), (C)** using this script (preserves encoding and newlines). Save as `research/migration/rename_package.py`, run it, and keep it in the repo:

```python
import re, sys, pathlib
root = pathlib.Path(".")
targets = [p for d in ("src", "tests") for p in (root / d).rglob("*.py")]
targets.append(root / "pyproject.toml")
# only: "import hypergrid", "from hypergrid", dotted module paths "hypergrid.", and pyproject package refs
pat_import = re.compile(r"(?m)^(\s*)(from|import)\s+hypergrid\b")
pat_dotted = re.compile(r"\bhypergrid(\.[A-Za-z_])")
changed = []
for p in targets:
    raw = p.read_bytes()
    text = raw.decode("utf-8")
    new = pat_import.sub(r"\1\2 astergrid", text)
    new = pat_dotted.sub(r"astergrid\1", new)
    if p.name == "pyproject.toml":
        new = re.sub(r'(?m)^(name\s*=\s*")hypergrid(")', r"\1astergrid\2", new)
        new = re.sub(r"\bsrc/hypergrid\b", "src/astergrid", new)
    if new != text:
        p.write_bytes(new.encode("utf-8"))   # no newline translation
        changed.append(str(p))
print("\n".join(changed)); print(len(changed), "files changed", file=sys.stderr)
```
7e. Re-grep: `git grep -n -i "hypergrid" -- src tests pyproject.toml`. Every remaining hit must be an intentional (D) hit already classified in 7a; list them in `RENAME_INVENTORY.md` with a one-line reason each.

7f. Reinstall the package in the environment if it was installed editable (`pip install -e .`), then:
```powershell
python -m pytest -q
python -m mypy --strict src tests
python -m ruff check src tests
```
**Exit:** pytest pass count **identical** to Step 3; mypy error count not higher; ruff clean; `Get-FileHash Strategy.md` unchanged. Any failure → **STOP**, report (do not patch tests to make them pass).

## Step 8 — Write the migration artifacts

Create (all under `research/migration/`; use the claim-hygiene format from Part 0.10):

1. **`SOURCE_PROVENANCE.md`** — Step 3 values with timestamps (UTC) and the commands; source HEAD hash; base branch (Step 2) and its hash; the merge-commit hash.
2. **`MIGRATION.md`** — source repo+commit; target repo; reason (Hyperliquid is one-way only; strategy needs hedge mode: §2 BU/SL both live, §11.3 mirroring, §11.1 per-side ExposureDelta); decision (ASTER DEX; hedge-native); rename `hypergrid`→`astergrid`; what stays venue-agnostic; what will change later (STR-0200, DECISION-002, §6.2, §6.3, STR-0224, §10, §13.4, new startup assertions) — **pointing to `docs/contract/CONTRACT_DELTA_ASTER.md` and `docs/ROADMAP.md`, not re-deriving them**; the phase-history table below (copy verbatim); explicit non-goals.
3. **`OPEN_MIGRATION_QUESTIONS.md`** — everything uncertain (prompt.md conflict marker, unsure gate files, any (D) rename hits, differing source HEAD, missing tools).
4. **`RENAME_INVENTORY.md`** (from Step 7).

Phase-history table to copy verbatim into `MIGRATION.md`:

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

If you can verify any "(merged)" or hash with `git log` in the imported history, add the verified hash next to it as `OBSERVATION` with the command; do not alter the table's original text.

## Step 9 — Commit (two commits), do NOT push, report

Run Part 1 first.

```powershell
git add -A research/sources research/decisions src tests pyproject.toml
git commit -m "migration: rename package hypergrid -> astergrid; relocate legacy HL material"
git add research/migration
git commit -m "migration: provenance, MIGRATION.md, rename inventory, open questions"
```
(If the rename and relocate changes are easier to separate into two commits, that is acceptable; keep every commit green.)

**Final checks, quote outputs:** `git status` (clean), `git log --oneline -6`, `Get-FileHash Strategy.md`, pytest/mypy/ruff results.

**Do not push. Do not merge. Stop.**

---

## Report format (final message)

1. Chosen `BASE` + proof command. 2. Source HEAD + baseline values (Step 3) vs after-rename values (Step 7f) in a table. 3. Merge commit hash; any conflicts (expected: none). 4. Rename inventory summary (A/B/C/D counts, each with its command). 5. Files moved in Step 6 (list). 6. Contents of `OPEN_MIGRATION_QUESTIONS.md`. 7. All STOPs fired (or "none"). 8. Exact commit hashes created. 9. Statement: "No push performed. `Strategy.md` SHA unchanged: <hash>."

## STOP list (summary)

`Strategy.md` SHA mismatch · no branch contains `CONTRACT_DELTA_ASTER.md` · merge conflict · suite/mypy/ruff regress at Step 5 or 7f · a hashed/serialized `hypergrid` string found (7b) · any need to edit a file not named in this prompt · any step you cannot verify. **Fail-closed. Silence is never a decision.**
