# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test files."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_declarations,
    architecture_test_harnesses,
    architecture_test_layers,
    architecture_test_syntax,
    architecture_test_terminals,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
NO_ALLOWED_MODULES: frozenset[str] = frozenset()
TEXT_ENCODING = "utf-8"
DOMAIN_PACKAGE = "domain"
DOMAIN_DEPENDENCIES = ("pydantic",)
type RegisteredHandler = tuple[str, str, str | None, list[str] | None]


def controller_classes(tree: standard_dependencies.ast.Module) -> dict[str, list[str]]:
    """Read top-level class names and bases from a controller module.

    Returns:
        The declared class names and their base expressions.

    """
    classes: dict[str, list[str]] = {}
    for node in tree.body:
        if isinstance(node, standard_dependencies.ast.ClassDef):
            classes[node.name] = architecture_test_harnesses.class_bases(node)
    return classes


def controller_mappings(
    tree: standard_dependencies.ast.Module,
) -> dict[str, standard_dependencies.ast.Dict]:
    """Read annotated dictionary assignments from a controller module.

    Returns:
        Assignment names mapped to their dictionary syntax nodes.

    """
    mappings: dict[str, standard_dependencies.ast.Dict] = {}
    for node in tree.body:
        mapping = architecture_test_harnesses.controller_mapping(node)
        if mapping is not None:
            name, mapping_value = mapping
            mappings[name] = mapping_value
    return mappings


def registrations_in_mapping(
    path: project_dependencies.Path,
    mapping: standard_dependencies.ast.Dict,
    classes: dict[str, list[str]],
    control_name_values: dict[str, str],
) -> project_dependencies.Iterator[RegisteredHandler]:
    """Read control keys and handler instances from a dictionary.

    Yields:
        The source location, control name, handler name, and known bases.

    """
    for key, handler_expression in zip(mapping.keys, mapping.values, strict=False):
        if key is None:
            continue
        where = f"{path.relative_to(ROOT)}:{key.lineno}"
        handler_name = getattr(getattr(handler_expression, "func", None), "id", None)
        yield (
            where,
            architecture_test_harnesses.registration_control_name(key, control_name_values),
            handler_name,
            None if handler_name is None else classes.get(handler_name),
        )


def native_id_violations_in_path(path: project_dependencies.Path, canonical_entity_ids: set[str]) -> list[str]:
    """Find direct canonical identifier constructor calls in a source file.

    Returns:
        A failure message for each prohibited call.

    """
    tree = architecture_test_declarations.parse_python_source(path)
    violations: list[str] = []
    for node in standard_dependencies.ast.walk(tree):
        violation = architecture_test_terminals.native_id_call_violation(path, node, canonical_entity_ids)
        if violation is not None:
            violations.append(violation)
    return violations


def assert_imports(package: str, allowed_roots: set[str], allowed_modules: frozenset[str] = NO_ALLOWED_MODULES) -> None:
    """Process assert imports.

    `allowed_modules` admits named MODULES from an otherwise closed package —
        the exception the harness boundary needs: it may name the terminal CONTRACT
        (which imports nothing of ours) without opening the whole package.
    """
    bad = []
    for path, imported in architecture_test_terminals.imports_under(package):
        if not architecture_test_terminals.is_permitted_import(imported, allowed_roots, allowed_modules):
            bad.append(f"{path.relative_to(ROOT)} imports {imported}")
    assert not bad, architecture_test_layers.listed_failure_message("invalid canonical imports", bad)


def has_domain_dependency() -> bool:
    """Return true when domain imports its permitted third-party dependency.

    Returns:
        True when domain imports its permitted third-party dependency.

    """
    for _path, imported in architecture_test_terminals.imports_under(DOMAIN_PACKAGE):
        if imported.split(".", 1)[0] in DOMAIN_DEPENDENCIES:
            return True
    return False


def database_access_violations() -> list[str]:
    """Check all owned source files for database access outside permitted modules.

    Returns:
        All database access failure messages.

    """
    violations: list[str] = []
    for path in architecture_test_syntax.owned_python_paths():
        violation = architecture_test_terminals.database_access_violation(path)
        if violation is not None:
            violations.append(violation)
    return violations
