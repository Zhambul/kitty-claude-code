# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test harnesses."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
)

type RegisteredHandler = tuple[str, str, str | None, list[str] | None]


def class_bases(node: standard_dependencies.ast.ClassDef) -> list[str]:
    """Read the base expressions from a class declaration.

    Returns:
        Each base expression as Python source text.

    """
    return [standard_dependencies.ast.unparse(base) for base in node.bases]


def controller_mapping(
    node: standard_dependencies.ast.stmt,
) -> tuple[str, standard_dependencies.ast.Dict] | None:
    """Read a named dictionary from an annotated assignment.

    Returns:
        The name and dictionary node, or None for another statement shape.

    """
    if not isinstance(node, standard_dependencies.ast.AnnAssign):
        return None
    if not isinstance(node.target, standard_dependencies.ast.Name):
        return None
    if not isinstance(node.value, standard_dependencies.ast.Dict):
        return None
    return (node.target.id, node.value)


def harness_controller_call(
    node: standard_dependencies.ast.AST,
) -> standard_dependencies.ast.Call | None:
    """Find a direct HarnessController constructor call.

    Returns:
        The call node, or None if the node is not that constructor call.

    """
    if not isinstance(node, standard_dependencies.ast.Call):
        return None
    if getattr(node.func, "id", None) != "HarnessController":
        return None
    return node


def resolved_controller_mapping(
    mapping: standard_dependencies.ast.expr,
    mappings: project_dependencies.Mapping[str, standard_dependencies.ast.Dict],
) -> standard_dependencies.ast.expr:
    """Resolve a controller mapping name against local dictionary assignments.

    Returns:
        The matching dictionary, or the unchanged expression if unresolved.

    """
    if not isinstance(mapping, standard_dependencies.ast.Name):
        return mapping
    return mappings.get(mapping.id, mapping)


def registration_control_name(key: standard_dependencies.ast.expr, control_name_values: dict[str, str]) -> str:
    """Read a control registration key as text.

    Returns:
        The string value, known enum value, or source text of the key.

    """
    if isinstance(key, standard_dependencies.ast.Constant) and isinstance(key.value, str):
        return key.value
    if isinstance(key, standard_dependencies.ast.Attribute):
        return control_name_values.get(key.attr, key.attr)
    return standard_dependencies.ast.unparse(key)


def registration_problem(registration: RegisteredHandler) -> str | None:
    """Check that a registration names a local class with a ControlHandler base.

    Returns:
        A failure message, or None if the handler declaration is valid.

    """
    where, control_name, handler_name, bases = registration
    if handler_name is None:
        return f"{where} {control_name!r} is not registered as a handler instance"
    if bases is None:
        return f"{where} handler {handler_name!r} is not a class in this module"
    if "ControlHandler" not in bases:
        return f"{where} {handler_name} does not declare ControlHandler (bases={bases})"
    return None


def unknown_control_problem(registration: RegisteredHandler, names: set[str]) -> str | None:
    """Check a registration against the known control names.

    Returns:
        A failure message for an unknown name, or None for a known name.

    """
    where, control_name, _handler_name, _bases = registration
    if control_name in names:
        return None
    return f"{where} registers unknown control {control_name!r}"
