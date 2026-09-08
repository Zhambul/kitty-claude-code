# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test layers."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
DOMAIN_PACKAGE = "domain"
API_PACKAGE = "api"
APP_PACKAGE = "app"
ENGINE_PACKAGE = "engine"
TERMINAL_PACKAGE = "terminal"
API_ROOT = ROOT / API_PACKAGE
TYPING_DICT_NAME = "Dict"


def target_name(target: standard_dependencies.ast.expr) -> str | None:
    """Return the name of one direct assignment target.

    Returns:
        The name of one direct assignment target.

    """
    if isinstance(target, standard_dependencies.ast.Name):
        return target.id
    if isinstance(target, standard_dependencies.ast.Attribute):
        return target.attr
    return None


def is_assignment_owner(owner_name: str | None, node: standard_dependencies.ast.AST) -> bool:
    """Check whether a node can own an assignment.

    Returns:
        True for a named owner, function, class, or module.

    """
    if owner_name is not None:
        return True
    return isinstance(
        node,
        (
            standard_dependencies.ast.FunctionDef,
            standard_dependencies.ast.ClassDef,
            standard_dependencies.ast.Module,
        ),
    )


def is_model_dump(node: standard_dependencies.ast.AST) -> bool:
    """Check whether a node calls a model_dump method.

    Returns:
        True for a method call with the name model_dump.

    """
    if not isinstance(node, standard_dependencies.ast.Call):
        return False
    if not isinstance(node.func, standard_dependencies.ast.Attribute):
        return False
    return node.func.attr == "model_dump"


def json_value_violation(
    node: standard_dependencies.ast.AST,
    parents: project_dependencies.Mapping[standard_dependencies.ast.AST, standard_dependencies.ast.AST],
) -> str | None:
    """Return a violation for one unapproved JSON value type.

    Returns:
        A violation for one unapproved JSON value type.

    """
    if not isinstance(node, standard_dependencies.ast.Name) or node.id != "JsonValue":
        return None
    parent = parents.get(node)
    nested_in_dictionary = (
        isinstance(parent, standard_dependencies.ast.Subscript)
        and isinstance(parent.value, standard_dependencies.ast.Name)
        and (parent.value.id in {"dict", TYPING_DICT_NAME})
    )
    return None if nested_in_dictionary else "uses JsonValue"


def import_violations(node: standard_dependencies.ast.AST) -> tuple[str, ...]:
    """Return violations for raw dictionary imports.

    Returns:
        Violations for raw dictionary imports.

    """
    if not isinstance(node, standard_dependencies.ast.ImportFrom):
        return ()
    imported = {alias.name for alias in node.names}
    violations = []
    if "JsonValue" in imported:
        violations.append("imports JsonValue")
    if TYPING_DICT_NAME in imported:
        violations.append("imports the raw dictionary type")
    return tuple(violations)


def listed_failure_message(label: str, failures: list[str]) -> str:
    """Format a group of architecture check failures.

    Returns:
        The label followed by the indented failure messages.

    """
    failure_details = "\n  ".join(failures)
    return f"{label}:\n  {failure_details}"


def canonical_import_top_paths() -> project_dependencies.Iterator[project_dependencies.Path]:
    """Select top-level packages for canonical import checks.

    Yields:
        The API, application, domain, engine, and terminal package paths.

    """
    yield API_ROOT
    yield (ROOT / APP_PACKAGE)
    yield (ROOT / DOMAIN_PACKAGE)
    yield (ROOT / ENGINE_PACKAGE)
    yield (ROOT / TERMINAL_PACKAGE)
