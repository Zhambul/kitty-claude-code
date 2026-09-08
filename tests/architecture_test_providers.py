# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test providers."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
)

# Keep dependency modules separate from test helpers.
# isort: split

from tests import (
    architecture_test_databases,
    architecture_test_declarations,
    architecture_test_json,
    architecture_test_layers,
    architecture_test_paths,
    architecture_test_routes,
    architecture_test_syntax,
    architecture_test_terminals,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
JSON_MODULE_NAME = "json"


def table_column_violations(table: str, body: str, allowed_opaque: set[str]) -> list[str]:
    """Check table columns for generic storage and undeclared opaque fields.

    Returns:
        A failure message for each prohibited column or table shape.

    """
    columns = architecture_test_terminals.table_columns(body)
    violations: list[str] = []
    for column in columns:
        if column in {"val", "value", JSON_MODULE_NAME, "data", "blob"}:
            violations.append(f"{table}.{column} is a key-value column")
        if column == "payload" and f"{table}.payload" not in allowed_opaque:
            violations.append(f"{table}.payload is an undeclared opaque column")
        if column == "content" and f"{table}.content" not in allowed_opaque:
            violations.append(f"{table}.content is an undeclared opaque column")
    if architecture_test_paths.is_key_value_table(columns):
        violations.append(f"{table} is a key-value table")
    return violations


def terminal_implementation_importers(package: str) -> project_dependencies.Iterator[str]:
    """Find terminal implementation imports outside that implementation.

    Yields:
        The relative path of each file with a prohibited import.

    """
    for path, imported_module in architecture_test_terminals.imports_under(package):
        relative_path = path.relative_to(ROOT).as_posix()
        if relative_path.startswith("terminal/impl/"):
            continue
        if imported_module == "terminal.impl" or imported_module.startswith("terminal.impl."):
            yield relative_path


def binding_modules(path: project_dependencies.Path) -> dict[str, str]:
    """Find the module for each imported name.

    Returns:
        A mapping from local names to imported modules.

    """
    bindings = {}
    tree = architecture_test_declarations.parse_python_source(path)
    for node in standard_dependencies.ast.walk(tree):
        bindings.update(architecture_test_routes.import_bindings(node))
    return bindings


def response_encoder_offenders(path: project_dependencies.Path) -> list[str]:
    """Return response-encoder imports from one API source file.

    Returns:
        Response-encoder imports from one API source file.

    """
    tree = architecture_test_declarations.parse_python_source(path)
    return [
        offender
        for node in standard_dependencies.ast.walk(tree)
        for offender in architecture_test_routes.response_encoder_import_offenders(path, node)
    ]


def assigned_name(
    node: standard_dependencies.ast.AST,
    parents: project_dependencies.Mapping[standard_dependencies.ast.AST, standard_dependencies.ast.AST],
) -> str | None:
    """Return the name that owns one syntax node.

    Returns:
        The name that owns one syntax node.

    """
    current = node
    while current in parents:
        current = parents[current]
        owner_name = architecture_test_routes.owner_name(current)
        if architecture_test_layers.is_assignment_owner(owner_name, current):
            return owner_name
    return None


def raw_json_violations(path: project_dependencies.Path) -> list[str]:
    """Return raw JSON codec imports from one harness source file.

    Returns:
        Raw JSON codec imports from one harness source file.

    """
    tree = architecture_test_declarations.parse_python_source(path)
    return [
        violation
        for node in standard_dependencies.ast.walk(tree)
        for violation in architecture_test_routes.raw_json_import_violations(path, node)
    ]


def concrete_harness_importers() -> list[str]:
    """Find concrete harness imports in shared application code.

    Returns:
        Messages with each importing path and concrete harness module.

    """
    importers: list[str] = []
    for path in architecture_test_databases.paths_under(architecture_test_json.canonical_import_paths()):
        for imported_path, imported in architecture_test_syntax.imports_under_path(path):
            if imported.startswith(("harness.impl.claude_code", "harness.impl.codex")):
                importers.append(f"{imported_path.relative_to(ROOT)} imports {imported}")
    return importers
