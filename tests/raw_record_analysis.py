# Copyright (c) 2026 Zhambyl Yermagambet
"""Find raw records in Python type annotations."""

from __future__ import annotations

import ast

from tests.raw_record_resolution import arguments, is_fixed_tuple, module_types, resolved, type_name
from tests.raw_record_types import EMPTY_RESOLUTION_PATH, SEQUENCE_TYPES, ModuleTypes, Violation


def contains_raw_record(
    node: ast.expr | None,
    types: ModuleTypes,
    resolving: frozenset[str] = EMPTY_RESOLUTION_PATH,
) -> bool:
    """Return true when a type contains an unnamed fixed tuple.

    Returns:
        True when a type contains an unnamed fixed tuple.

    """
    if node is None:
        return False
    resolved_node, next_resolving = resolved(node, types, resolving)
    if not isinstance(resolved_node, ast.Subscript):
        return False
    type_arguments = arguments(resolved_node)
    sequence_name = types.sequence_names.get(type_name(resolved_node.value) or "")
    if sequence_name in SEQUENCE_TYPES:
        item_arguments = type_arguments[:1]
        if any(is_fixed_tuple(argument, types, next_resolving) for argument in item_arguments):
            return True
    return any(contains_raw_record(argument, types, next_resolving) for argument in type_arguments)


class RawRecordVisitor(ast.NodeVisitor):
    """Collect raw-record violations from one module."""

    def __init__(self, types: ModuleTypes) -> None:
        """Store module types and start empty scope and violation records."""
        self.types = types
        self.violations: list[Violation] = []
        self.scope: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit one class scope."""
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit one function scope."""
        visit_function(self, node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit one asynchronous function scope."""
        visit_function(self, node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit one annotated assignment."""
        if isinstance(node.target, ast.Name):
            key = qualified_name(self.scope, node.target.id)
            record_annotation(self, node.annotation, key)
            if node.value is not None:
                record_alias(self, node.value, key)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit one module assignment."""
        if not self.scope and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                record_alias(self, node.value, target.id)
        self.generic_visit(node)

    def visit_TypeAlias(self, node: ast.TypeAlias) -> None:
        """Visit one explicit type alias."""
        if isinstance(node.name, ast.Name):
            record_alias(self, node.value, node.name.id)
        self.generic_visit(node)


def qualified_name(scope: list[str], name: str) -> str:
    """Return a name qualified by its current scopes.

    Returns:
        A name qualified by its current scopes.

    """
    return ".".join((*scope, name))


def visit_function(visitor: RawRecordVisitor, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
    """Record annotations from one function."""
    arguments = list(node.args.posonlyargs)
    arguments.extend(node.args.args)
    arguments.extend(node.args.kwonlyargs)
    for argument in arguments:
        if argument.arg not in {"self", "cls"}:
            key = qualified_name(visitor.scope, f"{node.name}.{argument.arg}")
            record_annotation(visitor, argument.annotation, key)
    for optional_argument in (node.args.vararg, node.args.kwarg):
        if optional_argument is not None:
            key = qualified_name(visitor.scope, f"{node.name}.{optional_argument.arg}")
            record_annotation(visitor, optional_argument.annotation, key)
    return_key = qualified_name(visitor.scope, f"{node.name}.return")
    record_annotation(visitor, node.returns, return_key)
    visitor.scope.append(node.name)
    visitor.generic_visit(node)
    visitor.scope.pop()


def record_alias(visitor: RawRecordVisitor, annotation: ast.expr, key: str) -> None:
    """Record one alias violation."""
    if is_fixed_tuple(annotation, visitor.types, frozenset()):
        visitor.violations.append((annotation.lineno, key, ast.unparse(annotation)))
        return
    record_annotation(visitor, annotation, key)


def record_annotation(visitor: RawRecordVisitor, annotation: ast.expr | None, key: str) -> None:
    """Record one annotation violation."""
    if annotation is not None and contains_raw_record(annotation, visitor.types):
        visitor.violations.append((annotation.lineno, key, ast.unparse(annotation)))


def source_violations(source: str) -> list[Violation]:
    """Return raw-record violations from Python source.

    Returns:
        Raw-record violations from Python source.

    """
    tree = ast.parse(source)
    visitor = RawRecordVisitor(module_types(tree))
    visitor.visit(tree)
    return visitor.violations
