# Copyright (c) 2026 Zhambyl Yermagambet
"""Detect loose types inside container annotations."""

from __future__ import annotations

import ast


def loose_container_name(node: ast.expr) -> str | None:
    """Return a container name from one expression.

    Returns:
        A container name from one expression.

    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def is_any_or_object(node: ast.expr) -> bool:
    """Return true for Any or object.

    Returns:
        True for Any or object.

    """
    return loose_container_name(node) in {"Any", "object"}


def is_bare_loose_container(node: ast.expr) -> bool:
    """Return true for a bare loose container.

    Returns:
        True for a bare loose container.

    """
    return loose_container_name(node) in {"dict", "list", "set"}


def subscript_arguments(annotation_slice: ast.expr) -> list[ast.expr]:
    """Return type arguments from one annotation subscript.

    Returns:
        Type arguments from one annotation subscript.

    """
    if isinstance(annotation_slice, ast.Tuple):
        return list(annotation_slice.elts)
    return [annotation_slice]


def contains_any_or_object(node: ast.expr | None) -> bool:
    """Return true when a container contains Any or object.

    Returns:
        True when a container contains Any or object.

    """
    if node is None:
        return False
    if is_any_or_object(node):
        return True
    if container_has_loose_argument(node):
        return True
    return union_has_loose_member(node)


def container_has_loose_argument(node: ast.expr) -> bool:
    """Return whether a container has a loose argument.

    Returns:
        Whether a container has a loose argument.

    """
    if not isinstance(node, ast.Subscript):
        return False
    if loose_container_name(node.value) not in {"dict", "list", "tuple", "set"}:
        return False
    return any(contains_any_or_object(argument) for argument in subscript_arguments(node.slice))


def union_has_loose_member(node: ast.expr) -> bool:
    """Return whether a union has a loose member.

    Returns:
        Whether a union has a loose member.

    """
    if not isinstance(node, ast.BinOp):
        return False
    if not isinstance(node.op, ast.BitOr):
        return False
    return contains_any_or_object(node.left) or contains_any_or_object(node.right)
