# RENAME_INVENTORY — hypergrid → astergrid (Step 7)

> Claim hygiene per `docs/prompts/PROMPT_MIGRATION_FREEBUFF.md` Part 0.10.
> Generated: 2026-10-01T12:20:34Z (UTC).
> Full raw hit list: `_rename_all_hits.txt` (560 hits, 143 files).

## 1. Inventory commands and counts

All counts produced in `C:/Users/Avangard/Desktop/AsterGrid` on branch
`migration/hypergrid-import`, after the Step 6 renames but **before** Step 7d
(the package directory was still `src/hypergrid` at inventory time).

| # | Count | Command |
|---|---|---|
| N1 | 560 hits / 143 files (whole repo, excluding `Strategy.md`) | `git grep -n -i "hypergrid" -- . ":(exclude)Strategy.md" > research/migration/_rename_all_hits.txt` ; `wc -l < research/migration/_rename_all_hits.txt` |
| N2 | 403 hits in `src` + `tests` + `pyproject.toml` | `git grep -c -i hypergrid -- src tests pyproject.toml \| awk -F: '{s+=$2} END {print s}'` |
| N3 | 368 import/from lines in `src`+`tests` (class A) | `git grep -nE '^[[:space:]]*(from\|import)[[:space:]]+hypergrid\b' -- src tests \| wc -l` |
| N4 | 16 string-literal hits in `src`+`tests` (class C) | `git grep -nE '"[^"]*hypergrid[^"]*"\|'"'"'[^'"'"']*hypergrid[^'"'"']*'"'"'' -- src tests \| wc -l` |
| N5 | 12 docstring hits in `src` (class D) | `git grep -n -i hypergrid -- src \| grep -vE '…import…' \| wc -l` (full command in session log) |
| N6 | 214 import/from lines in `tests` (subset of N3) | `git grep -nE '^[[:space:]]*(from\|import)[[:space:]]+hypergrid' -- tests \| wc -l` |
| N7 | 232 total hits in `tests` | `git grep -n -i hypergrid -- tests \| wc -l` |
| N8 | 5 hits in `pyproject.toml` (class B) | `git grep -n -i hypergrid -- pyproject.toml \| wc -l` |
| N9 | 0 case-variant hits (`Hypergrid`/`HYPERGRID`/`hyperGrid`) in `src`/`tests`/`pyproject.toml` | `git grep -n "Hypergrid\|HYPERGRID\|hyperGrid" -- src tests pyproject.toml` (no output) |
| N10 | 157 hits outside `src`/`tests`/`pyproject.toml`/`Strategy.md` (class D, docs/research prose; not renamed) | `git grep -n -i hypergrid -- . ":(exclude)Strategy.md" ":(exclude)src" ":(exclude)tests" ":(exclude)pyproject.toml" \| wc -l` |

Arithmetic check: 403 (N2) = 166 `src` (154 import + 12 docstring) + 232
`tests` (214 import + 18 string-literal) + 5 `pyproject.toml`.

## 2. Classification

- **(A) import/from statements — 368 lines** (N3). Rewritten by `pat_import`.
- **(B) pyproject.toml — 5 hits** (N8): line 8 `name = "hypergrid"`, line 31
  `packages = ["src/hypergrid"]`, line 56 `module = "hypergrid.config.schema"`
  (mypy strict override), plus 2 comment mentions. Rewritten by the pyproject
  rules + `pat_dotted`; comments left as-is (harmless prose).
- **(C) module-path strings in tests — 16 string-literal hits** (N4):
  `importlib.util.find_spec("hypergrid…")` in 4 files, importable-module
  tuples in `test_smoke.py`, logger name in `test_logging_format.py`,
  import-top comparison in `test_core_no_logging.py`. Rewritten by
  `pat_dotted` + the bare-string extension (§Ext).
- **(D) anything else — left untouched:**
  - 12 `src` docstring hits (N5), e.g. `src/hypergrid/__init__.py:1`.
  - 157 docs/research/prose hits (N10) — `README.md`, `CLAUDE.md`,
    `ASTERGRID_HANDOFF.md`, `docs/**`, `research/**`, `prompt.md` — historical
    records of the hypergrid project; renaming prose would falsify history.
  - 2 hits remain in `src`/`tests` after 7d (docstring + assert message) —
    see §4.

## 3. 7b STOP-condition check — NOT FIRED

The hashlib-using module (`src/hypergrid/core/events/envelope.py`, now
`src/astergrid/core/events/envelope.py`) and the serialization/identity
modules contain **only import-statement hits**:

```
git grep -n -i hypergrid -- src/hypergrid/core/events/envelope.py \
  src/hypergrid/core/events/codec.py src/hypergrid/core/events/identity.py \
  src/hypergrid/core/events/kinds.py src/hypergrid/core/serialization/canonical_json.py
```
→ 8 lines, all `from hypergrid.… import …` / `import hypergrid.…` (captured
2026-10-01). No `hypergrid` string is hashed, serialized, written to the
event log, used as an event-type/domain separator, or compared in a golden
fixture anywhere in `src/` or `tests/`. Zero (D) hits in code positions.

Additional record (Step 6.3): `src/hypergrid/operator/` contains only
`__init__.py`; `src/hypergrid/runtime/` contains `__init__.py` +
`logging_setup.py`; `grep -rni hyperliquid` over both → no matches. Neither
directory contains anything Hyperliquid-specific. Neither was edited.

## 4. Post-rename residue (7e)

```
git grep -n -i hypergrid -- src tests pyproject.toml
```
→ exactly 2 hits, both intentional class-D prose:

| File:line | Content | Reason left |
|---|---|---|
| `src/astergrid/__init__.py:1` | `"""hypergrid — deterministic, AI-independent Hyperliquid hedge-grid runtime.` | Docstring prose (historical identity line); not code, not serialized. Flagged in OPEN_MIGRATION_QUESTIONS Q3. |
| `tests/test_core_no_logging.py:33` | `assert files, "expected at least hypergrid/core/__init__.py"` | Human-facing failure-message text inside an assert; never compared or hashed. |

## 5. Extension vs the prompt's script (evidence-anchored)

The prompt's 7d patterns (`pat_import`, `pat_dotted`, pyproject rules) leave
two functional strings in `tests/` unreplaced:

| File:line (pre-rename) | Content | Why the base patterns miss it |
|---|---|---|
| `tests/test_smoke.py:8` | `"hypergrid",` (first tuple element of the importable-modules list) | bare string, no dot → `pat_dotted` misses; not an import line → `pat_import` misses |
| `tests/test_core_no_logging.py:41` | `assert top in stdlib or top == "hypergrid", (` | same |

Both were verified by reading the full files: they reference the package as
an importable module (class C), not domain data. `rename_package.py` adds
`re.sub(r'"hypergrid"', '"astergrid"', new)` for `tests/` files only (E1 in
its docstring). Without this, 7f would fail (`test_smoke` imports
`hypergrid`, which no longer exists; the no-logging stdlib guard would reject
`astergrid.*` modules as "non-stdlib"). Result: 7f green — 544 passed, mypy
119/58 identical, ruff clean, Strategy SHA unchanged.

Also recorded: the prompt's `pat_dotted` rewrites dotted references inside
docstrings/comments too (e.g. `hypergrid.core` → `astergrid.core` in module
docstrings). This is behavior-neutral prose normalization, kept as-is.

## 6. rename_package.py run output

`python research/migration/rename_package.py` → **123 files changed**
(40 src + 82 tests + 1 pyproject.toml; full file list in session log).
One fix after the first run: docstring turned into a raw string to remove a
`SyntaxWarning` (`\.` in prose); no behavioral change, script re-verified by
7f.
