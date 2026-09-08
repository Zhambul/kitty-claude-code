# Copyright (c) 2026 Zhambyl Yermagambet
"""Read control registrations through named and imported mappings."""

import ast
from collections.abc import Iterator
from pathlib import Path

from tests import architecture_test_harnesses, architecture_test_symbols

ROOT = Path(__file__).resolve().parents[1]
type RegisteredHandler = tuple[str, str, str | None, list[str] | None]


def registrations(path: Path, node: ast.AST, names: dict[str, str]) -> Iterator[RegisteredHandler]:
    """Read handlers from a dictionary, a mapping proxy, or an imported name.

    Yields:
        The source location, control name, handler class, and its bases.

    """
    if isinstance(node, ast.Name):
        resolved = architecture_test_symbols.declaration(path, node.id)
        if resolved is not None:
            yield from registrations(*resolved, names)
    elif isinstance(node, ast.Call):
        if getattr(node.func, "id", None) == "MappingProxyType":
            yield from registrations(path, node.args[0], names)
    elif isinstance(node, ast.Dict):
        yield from _dictionary_registrations(path, node, names)


def _dictionary_registrations(path: Path, node: ast.Dict, names: dict[str, str]) -> Iterator[RegisteredHandler]:
    for key, handler_expression in zip(node.keys, node.values, strict=True):
        if key is None:
            yield from registrations(path, handler_expression, names)
        else:
            handler_name = getattr(getattr(handler_expression, "func", None), "id", None)
            yield (
                f"{path.relative_to(ROOT)}:{key.lineno}",
                architecture_test_harnesses.registration_control_name(key, names),
                handler_name,
                _handler_bases(path, handler_name),
            )


def _handler_bases(path: Path, name: str | None) -> list[str] | None:
    if name is None:
        return None
    resolved = architecture_test_symbols.declaration(path, name)
    if resolved is None or not isinstance(resolved[1], ast.ClassDef):
        return None
    return [
        ast.unparse(base).rsplit(".", 1)[-1]
        for base in resolved[1].bases
    ]
