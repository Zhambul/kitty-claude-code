# Copyright (c) 2026 Zhambyl Yermagambet
"""Find loose annotations in Python syntax trees."""

from __future__ import annotations

import ast

from tests.typing_loose_containers import contains_any_or_object, is_any_or_object, is_bare_loose_container

type LooseViolation = tuple[int, str, str]


def loose_annotation(node: ast.expr | None) -> bool:
    """Return true for a loose annotation.

    Returns:
        True for a loose annotation.

    """
    if node is None:
        return False
    if is_any_or_object(node) or is_bare_loose_container(node):
        return True
    if isinstance(node, ast.Subscript):
        return contains_any_or_object(node)
    return loose_union_member(node)


def loose_union_member(node: ast.expr) -> bool:
    """Return whether a union has a loose annotation.

    Returns:
        Whether a union has a loose annotation.

    """
    if not isinstance(node, ast.BinOp):
        return False
    if not isinstance(node.op, ast.BitOr):
        return False
    return loose_annotation(node.left) or loose_annotation(node.right)


def qualified_name(scope: list[str], name: str) -> str:
    """Return a name qualified by its current scopes.

    Returns:
        A name qualified by its current scopes.

    """
    return ".".join((*scope, name))


class LooseAnnotationVisitor(ast.NodeVisitor):
    """Collect loose annotations from one module."""

    def __init__(self) -> None:
        """Start empty scope and annotation violation records."""
        self.violations: list[LooseViolation] = []
        self.scope: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit one class scope."""
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit one function scope."""
        self.visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit one asynchronous function scope."""
        self.visit_function(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit one annotated assignment."""
        if isinstance(node.target, ast.Name):
            self.record(node.annotation, qualified_name(self.scope, node.target.id))
        self.generic_visit(node)

    def visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Record annotations from one function."""
        arguments = list(node.args.posonlyargs)
        arguments.extend(node.args.args)
        arguments.extend(node.args.kwonlyargs)
        for argument in arguments:
            if argument.arg not in {"self", "cls"}:
                name = f"{node.name}.{argument.arg}"
                self.record(argument.annotation, qualified_name(self.scope, name))
        for optional_argument in (node.args.vararg, node.args.kwarg):
            if optional_argument is not None:
                name = f"{node.name}.{optional_argument.arg}"
                self.record(optional_argument.annotation, qualified_name(self.scope, name))
        self.record(node.returns, qualified_name(self.scope, f"{node.name}.return"))
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def record(self, annotation: ast.expr | None, key: str) -> None:
        """Record one loose annotation."""
        if annotation is not None and loose_annotation(annotation):
            self.violations.append((annotation.lineno, key, ast.unparse(annotation)))
