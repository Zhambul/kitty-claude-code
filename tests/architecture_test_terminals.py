# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test terminals."""

from __future__ import annotations

from tests import (
    architecture_packages,
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_declarations,
    architecture_test_paths,
    architecture_test_syntax,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
DOMAIN_PACKAGE = "domain"
REPOSITORY_PACKAGE = "repository"
CORE_PACKAGE = "core"
AUDIT_PACKAGE = "audit"
HARNESS_PACKAGE = "harness"
API_PACKAGE = "api"
APP_PACKAGE = "app"
DASHBOARD_PACKAGE = "dashboard"
ENGINE_PACKAGE = "engine"
NOTIFY_PACKAGE = "notify"
TERMINAL_PACKAGE = "terminal"
OUR_PACKAGES = architecture_packages.owned_packages()


def native_id_call_violation(
    path: project_dependencies.Path,
    node: standard_dependencies.ast.AST,
    canonical_entity_ids: set[str],
) -> str | None:
    """Check a syntax node for a direct canonical identifier constructor call.

    Returns:
        The call location and identifier type, or None for another node.

    """
    if not isinstance(node, standard_dependencies.ast.Call):
        return None
    if not isinstance(node.func, standard_dependencies.ast.Name):
        return None
    if node.func.id not in canonical_entity_ids:
        return None
    relative_path = path.relative_to(ROOT)
    line_number = node.lineno
    function_name = node.func.id
    return f"{relative_path}:{line_number} constructs {function_name}"


def imports_under(
    package: str,
) -> project_dependencies.Iterator[tuple[project_dependencies.Path, str]]:
    """Read Python imports under a package directory.

    Yields:
        Each source file path and imported module name.

    """
    for path in (ROOT / package).rglob(PYTHON_FILE_PATTERN):
        yield from architecture_test_syntax.imports_under_path(path)


def is_permitted_import(imported: str, allowed_roots: set[str], allowed_modules: frozenset[str]) -> bool:
    """Return whether one import is allowed at a package boundary.

    Returns:
        Whether one import is allowed at a package boundary.

    """
    root = imported.split(".", 1)[0]
    if root not in OUR_PACKAGES:
        return True
    if root in allowed_roots:
        return True
    return architecture_test_syntax.is_allowed_module(imported, allowed_modules)


def database_access_violation(path: project_dependencies.Path) -> str | None:
    """Check non-exempt source files for database access markers.

    Returns:
        A message with matching markers, or None for valid or exempt files.

    """
    relative = path.relative_to(ROOT).as_posix()
    if relative.startswith("repository/impl/sqlite/") or relative == "harness/impl/codex/canonical/title_store.py":
        return None
    code = architecture_test_syntax.code_only(path)
    found = [
        marker
        for marker in ("sqlite3", "SELECT ", "INSERT INTO", "UPDATE ", "DELETE FROM", "CREATE TABLE")
        if marker in code
    ]
    return architecture_test_syntax.contains_message(relative, found) if found else None


def repository_contract_violations() -> list[str]:
    """Check repository contract methods for exposed storage operations.

    Returns:
        All prohibited method and return-type messages.

    """
    violations: list[str] = []
    for path in sorted((ROOT / REPOSITORY_PACKAGE / "contract").rglob(PYTHON_FILE_PATTERN)):
        tree = architecture_test_declarations.parse_python_source(path)
        for node in standard_dependencies.ast.walk(tree):
            if isinstance(
                node,
                (
                    standard_dependencies.ast.FunctionDef,
                    standard_dependencies.ast.AsyncFunctionDef,
                ),
            ):
                violations.extend(architecture_test_paths.contract_method_violations(path, node))
    return violations


def table_columns(body: str) -> list[str]:
    """Read column names from the lines of a table declaration.

    Returns:
        The first token of each line identified as a column.

    """
    columns: list[str] = [
        line.strip().split()[0]
        for line in body.splitlines()
        if architecture_test_paths.is_table_column(line)
    ]
    return columns


def harness_boundary_violations(
    path: project_dependencies.Path,
    allowed_modules: set[str],
) -> project_dependencies.Iterator[str]:
    """Check harness imports against permitted package boundaries.

    Yields:
        A message for each prohibited application package import.

    """
    for _imported_path, imported in architecture_test_syntax.imports_under_path(path):
        imported_root = imported.split(".", 1)[0]
        if imported_root in {HARNESS_PACKAGE, DOMAIN_PACKAGE}:
            continue
        if architecture_test_syntax.is_allowed_module(imported, frozenset(allowed_modules)):
            continue
        if imported_root in {
            API_PACKAGE,
            APP_PACKAGE,
            CORE_PACKAGE,
            DASHBOARD_PACKAGE,
            AUDIT_PACKAGE,
            ENGINE_PACKAGE,
            NOTIFY_PACKAGE,
            TERMINAL_PACKAGE,
        }:
            yield f"{path.relative_to(ROOT)} imports {imported}"
