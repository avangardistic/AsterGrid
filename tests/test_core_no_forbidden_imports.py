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


def _annotation_nodes(node: ast.AST) -> list[ast.expr]:
    """The annotation expressions a node introduces (AnnAssign / arg / returns)."""
    out: list[ast.expr] = []
    if isinstance(node, ast.AnnAssign) and node.annotation is not None:
        out.append(node.annotation)
    if isinstance(node, ast.arg) and node.annotation is not None:
        out.append(node.annotation)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
        node.returns is not None
    ):
        out.append(node.returns)
    return out


def _float_violations(src: str) -> list[str]:
    """Every way a ``float`` could enter core, EXCEPT ``isinstance(x, float)``.

    Rejected: float literals (``1.5``); ``float(...)`` calls; ``float`` as a
    variable/call name; ``float`` in any annotation (``x: float``, return type,
    ``arg``); ``float`` as a typing subscript arg (``list[float]``,
    ``Optional[float]``, ``Union[..., float]`` — all surface as ``Name('float')``
    inside the subscript); and the exact-string annotation ``x: "float"``.
    Allowed: ``float`` as the 2nd arg of ``isinstance(...)`` — the G1 rejection
    guard in canonical_dumps, which keeps floats OUT rather than introducing one.
    Incidental "float" inside docstrings/messages is NOT an annotation and does
    not trip the checker (only annotation positions are string-scanned).
    """
    tree = ast.parse(src)
    violations: list[str] = []

    # Whitelist the `float` Name node that is the 2nd positional arg of isinstance.
    allowed: set[int] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "isinstance"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Name)
            and node.args[1].id == "float"
        ):
            allowed.add(id(node.args[1]))

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            violations.append("float-literal")
        # A bare `float` Name covers: float() calls (func Name), variable/call
        # names, annotations (x: float), and subscript args (list[float]).
        if (
            isinstance(node, ast.Name)
            and node.id == "float"
            and id(node) not in allowed
        ):
            violations.append("float-name")

    # Exact-string annotation: x: "float".
    for node in ast.walk(tree):
        for ann in _annotation_nodes(node):
            for sub in ast.walk(ann):
                if isinstance(sub, ast.Constant) and sub.value == "float":
                    violations.append("float-string-annotation")

    return violations


def test_no_float_in_core() -> None:
    for path in _core_files():
        violations = _float_violations(path.read_text(encoding="utf-8"))
        assert not violations, f"{path} has float usage: {violations}"


def test_float_checker_rejects_and_accepts() -> None:
    # REJECT: annotation, exact-string annotation, subscript arg, call, literal.
    assert _float_violations("x: float = 1")
    assert _float_violations('x: "float" = 1')
    assert _float_violations("y: list[float] = []")
    assert _float_violations("def f() -> float: ...")
    assert _float_violations("def g(a: float) -> int: ...")
    assert _float_violations("z = float(1)")
    assert _float_violations("w = 1.5")
    # ACCEPT: the isinstance rejection guard (and float-free code).
    assert not _float_violations("isinstance(v, float)")
    assert not _float_violations("x: int = 1")


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
