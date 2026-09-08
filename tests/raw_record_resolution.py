# Copyright (c) 2026 Zhambyl Yermagambet
"""Resolve type aliases for raw-record architecture checks."""

from __future__ import annotations

import ast

from tests.raw_record_types import SEQUENCE_TYPES, TUPLE_TYPES, ModuleTypes

VARIABLE_TUPLE_ARGUMENT_COUNT = 2


def record_imported_sequences(statement: ast.stmt, sequence_names: dict[str, str]) -> None:
    """Record sequence names from one import statement."""
    if not isinstance(statement, (ast.Import, ast.ImportFrom)):
        return
    for imported_name in statement.names:
        type_name = imported_name.name.rsplit(".", 1)[-1]
        if type_name in SEQUENCE_TYPES:
            sequence_names[imported_name.asname or imported_name.name] = type_name


def assigned_alias(statement: ast.stmt) -> tuple[str, ast.expr] | None:
    """Return a type alias from one assignment statement.

    Returns:
        A type alias from one assignment statement.

    """
    if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
        target = statement.targets[0]
        if isinstance(target, ast.Name):
            return target.id, statement.value
    if (
        isinstance(statement, ast.AnnAssign)
        and isinstance(statement.target, ast.Name)
        and statement.value is not None
    ):
        return statement.target.id, statement.value
    if isinstance(statement, ast.TypeAlias) and isinstance(statement.name, ast.Name):
        return statement.name.id, statement.value
    return None


def module_types(tree: ast.Module) -> ModuleTypes:
    """Return all type information from one module tree.

    Returns:
        All type information from one module tree.

    """
    aliases: dict[str, ast.expr] = {}
    sequence_names = {name: name for name in SEQUENCE_TYPES}
    for statement in tree.body:
        record_imported_sequences(statement, sequence_names)
        alias = assigned_alias(statement)
        if alias is not None:
            aliases[alias[0]] = alias[1]
    return ModuleTypes(aliases, sequence_names)


def type_name(node: ast.expr) -> str | None:
    """Return the simple name for one type expression.

    Returns:
        The simple name for one type expression.

    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def arguments(node: ast.Subscript) -> tuple[ast.expr, ...]:
    """Return subscript type arguments.

    Returns:
        Subscript type arguments.

    """
    if isinstance(node.slice, ast.Tuple):
        return tuple(node.slice.elts)
    return (node.slice,)


def resolved(
    node: ast.expr,
    types: ModuleTypes,
    resolving: frozenset[str],
) -> tuple[ast.expr, frozenset[str]]:
    """Resolve type aliases until a non-alias or a repeated name is reached.

    Returns:
        The resolved expression and the set of alias names visited.

    """
    if not isinstance(node, ast.Name):
        return node, resolving
    if node.id in resolving or node.id not in types.aliases:
        return node, resolving
    next_resolving = resolving | {node.id}
    return resolved(types.aliases[node.id], types, next_resolving)


def is_fixed_tuple(node: ast.expr, types: ModuleTypes, resolving: frozenset[str]) -> bool:
    """Return true for a tuple with fixed item positions.

    Returns:
        True for a tuple with fixed item positions.

    """
    resolved_node, _next_resolving = resolved(node, types, resolving)
    if not isinstance(resolved_node, ast.Subscript):
        return False
    if type_name(resolved_node.value) not in TUPLE_TYPES:
        return False
    type_arguments = arguments(resolved_node)
    if len(type_arguments) < VARIABLE_TUPLE_ARGUMENT_COUNT:
        return False
    if len(type_arguments) != VARIABLE_TUPLE_ARGUMENT_COUNT:
        return True
    second_argument = type_arguments[1]
    is_variable = isinstance(second_argument, ast.Constant) and second_argument.value is Ellipsis
    return not is_variable
