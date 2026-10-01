"""Invariant: hypergrid.core never imports `logging` and is stdlib-only.

Enforces DECISION-022 (core = no third-party deps) and DECISION-023 (core
never logs). Walks the AST of every module under `hypergrid.core`.
"""

import ast
import importlib.util
import sys
from pathlib import Path


def _core_files() -> list[Path]:
    spec = importlib.util.find_spec("hypergrid.core")
    assert spec is not None
    locations = spec.submodule_search_locations
    assert locations is not None
    root = Path(next(iter(locations)))
    return sorted(root.rglob("*.py"))


def _tops(node: ast.Import | ast.ImportFrom) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    if node.level and node.level > 0:
        return []  # relative intra-core import
    assert node.module is not None
    return [node.module.split(".")[0]]


def test_core_has_no_logging_and_is_stdlib_only() -> None:
    files = _core_files()
    assert files, "expected at least hypergrid/core/__init__.py"
    stdlib = sys.stdlib_module_names
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for top in _tops(node):
                    assert top != "logging", f"{path} imports logging"
                    assert top in stdlib or top == "hypergrid", (
                        f"{path} imports non-stdlib module {top!r}"
                    )
