"""Structural guards on hypergrid.core: no forbidden imports, no float, no secrets."""

import ast
import importlib.util
from dataclasses import fields
from pathlib import Path

from hypergrid.core.events import (
    AcknowledgmentEvent,
    AdministrativeEvent,
    CommandEvent,
    ErrorEvent,
    FillEvent,
    IntentEvent,
    ObservationEvent,
    OperatorEvent,
    StateTransitionEvent,
    TimerEvent,
)
from hypergrid.runtime.logging_setup import REDACT_KEYS

_FORBIDDEN_IMPORT_TOPS = {
    "logging",
    "time",
    "datetime",
    "random",
    "os",
    "pydantic",
    "httpx",
    "websockets",
    "eth_account",
    "numpy",
    "pandas",
    "requests",
    "aiohttp",
    "asyncio",
}


def _core_root() -> Path:
    spec = importlib.util.find_spec("hypergrid.core")
    assert spec is not None
    locations = spec.submodule_search_locations
    assert locations is not None
    return Path(next(iter(locations)))


def _core_files() -> list[Path]:
    return sorted(_core_root().rglob("*.py"))


def _import_tops(node: ast.Import | ast.ImportFrom) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    if node.level and node.level > 0:
        return []
    if node.module is None:
        return []
    return [node.module.split(".")[0]]


def test_no_forbidden_imports() -> None:
    for path in _core_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for top in _import_tops(node):
                    assert top not in _FORBIDDEN_IMPORT_TOPS, (
                        f"{path} imports forbidden module {top!r}"
                    )


def test_no_float_in_core() -> None:
    for path in _core_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                assert not isinstance(node.value, float), f"{path} has a float literal"
            if isinstance(node, ast.Name):
                assert node.id != "float", f"{path} references the float builtin"


def test_hashlib_only_in_envelope() -> None:
    for path in _core_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        uses_hashlib = any(
            "hashlib" in _import_tops(node)
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        )
        if uses_hashlib:
            assert path.name == "envelope.py", (
                f"hashlib used outside envelope.py: {path}"
            )


def test_no_secret_field_names_in_events() -> None:
    kinds = [
        IntentEvent,
        CommandEvent,
        AcknowledgmentEvent,
        FillEvent,
        ObservationEvent,
        TimerEvent,
        ErrorEvent,
        StateTransitionEvent,
        OperatorEvent,
        AdministrativeEvent,
    ]
    for kind in kinds:
        for f in fields(kind):
            assert f.name.lower() not in REDACT_KEYS, (
                f"{kind.__name__}.{f.name} is a secret-bearing field name"
            )
