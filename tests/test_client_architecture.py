# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify terminal client architecture and behavior."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

from tests.client_test_models import (
    PathRoute,
    RouterInclusion,
)
from tests.client_test_render_support import imported_names

if TYPE_CHECKING:
    from collections.abc import Iterator

ROOT = Path(__file__).resolve().parents[1]


CLIENT = ROOT / "client"


TEXT_ENCODING = "utf-8"


PYTHON_FILE_PATTERN = "*.py"


OUR_PACKAGES = (
    "api",
    "app",
    "core",
    "dashboard",
    "audit",
    "domain",
    "engine",
    "harness",
    "notify",
    "repository",
    "terminal",
)


def _parsed_nodes(path: Path) -> Iterator[ast.AST]:
    """Return the abstract syntax tree nodes from one source file.

    Returns:
        The abstract syntax tree nodes from one source file.

    """
    tree = ast.parse(path.read_text(encoding=TEXT_ENCODING), filename=str(path))
    return ast.walk(tree)


def _client_state_violations(
    path: Path,
    forbidden: tuple[str, ...],
    file_markers: tuple[str, ...],
) -> list[str]:
    source = path.read_text(encoding=TEXT_ENCODING)
    is_handoff_module = path.name.startswith("_handoff")
    markers = forbidden if is_handoff_module else forbidden + file_markers
    return [f"{path.name} contains {marker}" for marker in markers if marker in source]


def test_no_client_touches_store_audit_trail() -> None:
    """Verify no client touches the store the audit trail or the application.

    R5, belt to the braces of the import rule: a name that never appears
        cannot come back through a deferred import.

        Every marker below was in a client at some point. The OTLP receiver opened
        the event store; the status-line shim opened usage.db; all nine wrote an
        audit row from their `except` blocks, which is what made
        `audit/record.py` — and through it the whole sqlite layer — part of
        nine foreign processes and gave audit.db ten writers.

        The `_handoff` modules are the only client modules allowed to touch a file, and only the
        file-access markers are lifted for it — it may still not name a store, a
        repository, the audit trail or the application. It exists because both pane
        click gestures are frontend-only: the terminal launches a separate program
        for a click, that program has no model and no daemon to ask, and the text it
        needs is already on the pane's screen. So the two processes meet in the temp
        directory. Those modules are one local channel between two halves of one frontend, which
        is what this rule was never about; the rule is that a client does not reach
        OUR state, and a file of its own making is not our state.
    """
    forbidden = (
        "sqlite3",
        "repository",
        "audit",
        "app.providers",
        "build_application",
        "RawEvent",
        "main.db",
        "audit.db",
    )
    touches_files = ("open(", ".write_text(", ".write_bytes(", "os.makedirs")
    violations: list[str] = []
    for path in sorted(CLIENT.glob(PYTHON_FILE_PATTERN)):
        violations.extend(_client_state_violations(path, forbidden, touches_files))
    assert not violations


def test_no_module_of_ours_imports_a_client() -> None:
    """The coupling must not grow back in the other direction either.

    `client/` is not a package and nothing above it may reach in: the daemon
    names those files (`core/clients.py`) and runs them, and that is the entire
    relationship.
    """
    importers: list[str] = []
    for package in OUR_PACKAGES:
        for path in sorted((ROOT / package).rglob(PYTHON_FILE_PATTERN)):
            importers.extend(
                path.relative_to(ROOT).as_posix()
                for imported in imported_names(path)
                if imported.split(".")[0] in {"client", "_http", "_daemon"}
            )
    assert not importers


def code_strings(path: Path) -> list[str]:
    """Read string literals from code without its documentation strings.

    Returns:
        The string values outside module, class, and function docstrings.

    """
    tree = ast.parse(path.read_text(encoding=TEXT_ENCODING), filename=str(path))
    documentation = _documentation_values(tree)
    return [
        literal_node.value
        for literal_node in ast.walk(tree)
        if isinstance(literal_node, ast.Constant)
        and isinstance(literal_node.value, str)
        and id(literal_node) not in documentation
    ]


def _documentation_values(tree: ast.AST) -> set[int]:
    """Return the values that are module, class, or function docstrings.

    Returns:
        The values that are module, class, or function docstrings.

    """
    documentation: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                documentation.add(id(first.value))
    return documentation


def _route_paths(router: object) -> Iterator[str]:
    """Read public paths from a router and its included routers.

    Yields:
        Each route path, including paths in nested routers.

    """
    for route in getattr(router, "routes", ()):
        if isinstance(route, PathRoute):
            yield route.path
        elif isinstance(route, RouterInclusion):
            yield from _route_paths(route.original_router)
