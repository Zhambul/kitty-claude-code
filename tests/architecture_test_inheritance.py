# Copyright (c) 2026 Zhambyl Yermagambet
"""Read inherited methods for the protocol checks."""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.architecture_test_syntax import ClassDescription

ROOT = Path(__file__).resolve().parents[1]
type MethodSignatures = dict[str, tuple[str, ...]]


def resolved_contracts(
    protocols: dict[str, ClassDescription],
    classes: list[ClassDescription],
) -> tuple[dict[str, MethodSignatures], list[ClassDescription]]:
    """Resolve inherited protocol signatures and concrete implementations.

    Returns:
        Public protocol signatures and complete concrete class descriptions.

    """
    indexed = {description.name: description for description in classes}
    indexed.update({
        name: protocol_defaults(description)
        for name, description in protocols.items()
    })
    signatures = {
        name: inherited_description(description, protocols).members
        for name, description in protocols.items()
        if not name.startswith("_")
    }
    return signatures, [inherited_description(description, indexed) for description in classes]


def protocol_defaults(description: ClassDescription) -> ClassDescription:
    """Keep concrete default methods and exclude protocol stubs.

    Returns:
        The protocol defaults that a subclass can inherit.

    """
    path = ROOT / description.where.split(":", 1)[0]
    declaration = _class_declaration(path, description.name)
    implemented = {
        node.name
        for node in declaration.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _has_implementation(node)
    }
    return replace(
        description,
        members={
            name: signature
            for name, signature in description.members.items()
            if name in implemented
        },
    )


def _class_declaration(path: Path, name: str) -> ast.ClassDef:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    classes = (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    return next(node for node in classes if node.name == name)


def _has_implementation(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        not isinstance(statement, (ast.Expr, ast.Pass, ast.Raise))
        for statement in node.body
    )


def inherited_description(
    description: ClassDescription,
    classes: dict[str, ClassDescription],
) -> ClassDescription:
    """Include the methods and declarations of concrete base classes.

    Returns:
        The class with its inherited methods and protocol declarations.

    """
    members = {}
    bases = list(description.bases)
    for name in reversed(description.bases):
        base = classes.get(name)
        if base is None:
            continue
        inherited = inherited_description(base, classes)
        members.update(inherited.members)
        bases.extend(inherited.bases)
    members.update(description.members)
    return replace(description, members=members, bases=list(dict.fromkeys(bases)))
