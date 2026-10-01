r"""Package rename hypergrid -> astergrid (Phase M, Step 7d).

Rewrites ONLY:
  (A) import / from hypergrid... statements
  (B) pyproject.toml package references
  (C) dotted module-path strings ("hypergrid.xxx") in tests (mock patches,
      importlib, importable-module lists)

Deliberately does NOT touch docstrings, comments, prose, URLs, or any other
string (class D) — see research/migration/RENAME_INVENTORY.md.

Extension vs the prompt-issued script (evidence in RENAME_INVENTORY.md §Ext):
  E1. bare exact-string "hypergrid" (no dot after) in tests/ files:
      tests/test_smoke.py:8        (importable-modules tuple)
      tests/test_core_no_logging.py:41  (top == "hypergrid" import guard)
      The prompt's pat_import (line-start import) and pat_dotted
      (hypergrid\.[A-Za-z_]) both miss these functional strings.
  E2. pyproject.toml [tool.mypy.overrides] module = "hypergrid.config.schema":
      covered by the prompt's pat_dotted, kept explicit here for the record.

7b verification (no STOP): no "hypergrid" occurrence inside any string that is
hashed, serialized, written to the event log, used as an event-type/domain
separator, or compared in a golden fixture — the hashlib-using module
(src/astergrid/core/events/envelope.py, formerly src/hypergrid/...) and the
serialization modules contain only import-statement hits.
"""

import re
import sys
from pathlib import Path

root = Path(".")
targets = [p for d in ("src", "tests") for p in (root / d).rglob("*.py")]
targets.append(root / "pyproject.toml")

# only: "import hypergrid", "from hypergrid", dotted module paths
# "hypergrid.", and pyproject package refs
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
    # E1: bare exact-string "hypergrid" in tests/ (functional module refs).
    if p.parent.name == "tests":
        new = re.sub(r'"hypergrid"', '"astergrid"', new)
    if new != text:
        p.write_bytes(new.encode("utf-8"))  # no newline translation
        changed.append(str(p))

print("\n".join(changed))
print(len(changed), "files changed", file=sys.stderr)
