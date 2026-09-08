# Copyright (c) 2026 Zhambyl Yermagambet
"""Resolve source declarations across imports for architecture checks."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def declaration(path: Path, name: str) -> tuple[Path, ast.AST] | None:
    """Resolve a name to its source declaration.

    Returns:
        The source file and declaration, or None for an external name.

    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        found = _local_value(node, name)
        if found is not None:
            return path, found
        imported = _imported_value(node, name)
        if imported is not None:
            return imported
    return None


def _local_value(node: ast.AST, name: str) -> ast.AST | None:
    if isinstance(node, ast.ClassDef) and node.name == name:
        return node
    if (
        isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == name
    ):
        return node.value
    if isinstance(node, ast.Assign) and any(
        isinstance(target, ast.Name) and target.id == name
        for target in node.targets
    ):
        return node.value
    return None


def _imported_value(node: ast.AST, name: str) -> tuple[Path, ast.AST] | None:
    if not isinstance(node, ast.ImportFrom) or node.module is None:
        return None
    module = ROOT.joinpath(*node.module.split(".")).with_suffix(".py")
    if not module.is_file():
        return None
    for alias in node.names:
        if (alias.asname or alias.name) == name:
            return declaration(module, alias.name)
    return None
