# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test paths."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
BIN_DIRECTORY_NAME = "bin"
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
DOMAIN_PACKAGE = "domain"
CORE_PACKAGE = "core"
AUDIT_PACKAGE = "audit"
HARNESS_PACKAGE = "harness"
API_PACKAGE = "api"
APP_PACKAGE = "app"
DASHBOARD_PACKAGE = "dashboard"
ENGINE_PACKAGE = "engine"
NOTIFY_PACKAGE = "notify"
TERMINAL_PACKAGE = "terminal"
HARNESS_ROOT = ROOT / HARNESS_PACKAGE
API_ROOT = ROOT / API_PACKAGE
DASHBOARD_ROOT = ROOT / DASHBOARD_PACKAGE


def contract_method_violations(
    path: project_dependencies.Path,
    node: standard_dependencies.ast.FunctionDef | standard_dependencies.ast.AsyncFunctionDef,
) -> list[str]:
    """Check a repository contract method for exposed database operations.

    Returns:
        Failure messages for forbidden method names and return types.

    """
    forbidden_names = {"connect", "connection", "cursor", "transaction", "unit_of_work", "begin", "commit", "rollback"}
    forbidden_returns = ("Connection", "Cursor", "AbstractContextManager", "Iterator", "Generator")
    where = f"{path.relative_to(ROOT)}:{node.lineno}"
    violations = [f"{where} exposes {node.name}()"] if node.name in forbidden_names else []
    returns = standard_dependencies.ast.unparse(node.returns) if node.returns else ""
    violations.extend(f"{where} returns {returns}" for forbidden in forbidden_returns if forbidden in returns)
    return violations


def is_table_column(line: str) -> bool:
    """Check whether a schema line can contain a table column.

    Returns:
        False for empty lines, comments, and table constraints.

    """
    stripped = line.strip()
    if not stripped:
        return False
    return not stripped.startswith(("PRIMARY", "FOREIGN", "UNIQUE", "--"))


def is_key_value_table(columns: list[str]) -> bool:
    """Check for a generic key-value table column pair.

    Returns:
        True for one of the prohibited generic column pairs.

    """
    key_value_columns = ({"key", "val"}, {"key", "value"}, {"name", "value"})
    return set(columns) in key_value_columns


def is_foreign_terminal_import(imported_module: str) -> bool:
    """Check an import against the terminal contract package boundary.

    Returns:
        True for imports outside terminal and the permitted standard modules.

    """
    imported_root = imported_module.split(".", 1)[0]
    standard_roots = {"collections", "dataclasses", "enum", "typing", "__future__"}
    return imported_root != TERMINAL_PACKAGE and imported_root not in standard_roots


def terminal_vocabulary_paths() -> project_dependencies.Iterator[project_dependencies.Path]:
    """Find source files covered by terminal vocabulary checks.

    Yields:
        Python file paths sorted within each selected package.

    """
    scanned = (
        API_ROOT,
        ROOT / APP_PACKAGE,
        ROOT / CORE_PACKAGE,
        DASHBOARD_ROOT,
        ROOT / AUDIT_PACKAGE,
        ROOT / DOMAIN_PACKAGE,
        HARNESS_ROOT,
        ROOT / ENGINE_PACKAGE,
        ROOT / NOTIFY_PACKAGE,
        ROOT / TERMINAL_PACKAGE,
    )
    for directory in scanned:
        yield from sorted(directory.rglob(PYTHON_FILE_PATTERN))


def terminal_asset_violations() -> list[str]:
    """Check dashboard JavaScript assets for terminal-specific names.

    Returns:
        A failure message for each asset that contains kitty.

    """
    return [
        f"dashboard/static/{asset_path.name} contains kitty"
        for asset_path in sorted((DASHBOARD_ROOT / "static").glob("*.js"))
        if "kitty" in asset_path.read_text(encoding=TEXT_ENCODING).lower()
    ]


def claude_bin_entries() -> set[str]:
    """Find Claude-specific entries in the bin directory.

    Returns:
        Entry names that start with claude-.

    """
    bin_path = ROOT / BIN_DIRECTORY_NAME
    return {path.name for path in bin_path.iterdir() if path.name.startswith("claude-")}
