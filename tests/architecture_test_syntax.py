# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test syntax."""

from __future__ import annotations

from tests import (
    architecture_packages,
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_declarations,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
BIN_DIRECTORY_NAME = "bin"
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
type MethodSignatures = dict[str, tuple[str, ...]]


@standard_dependencies.dataclasses.dataclass(frozen=True)
class ClassDescription:
    """Describe one concrete class for protocol checks."""

    where: str
    name: str
    bases: list[str]
    members: MethodSignatures


OUR_PACKAGES = architecture_packages.owned_packages()


def contains_message(location: object, matches: list[str]) -> str:
    """Format the matching names at a source location.

    Returns:
        A message with the location and matching names.

    """
    match_text = ", ".join(matches)
    return f"{location} contains {match_text}"


def imports_under_path(
    path: project_dependencies.Path,
) -> project_dependencies.Iterator[tuple[project_dependencies.Path, str]]:
    """Read the imports in one Python file.

    Yields:
        The file path and each imported module name.

    """
    tree = architecture_test_declarations.parse_python_source(path)
    for node in standard_dependencies.ast.walk(tree):
        if isinstance(node, standard_dependencies.ast.Import):
            for alias in node.names:
                yield (path, alias.name)
        elif isinstance(node, standard_dependencies.ast.ImportFrom) and node.module:
            yield (path, node.module)


def owned_python_paths() -> project_dependencies.Iterator[project_dependencies.Path]:
    """Find Python files in the owned packages.

    Yields:
        Each Python file path, sorted within its package.

    """
    for package in OUR_PACKAGES:
        yield from sorted((ROOT / package).rglob(PYTHON_FILE_PATTERN))


def is_allowed_module(imported: str, allowed_modules: frozenset[str]) -> bool:
    """Return true when an imported name is under an allowed module.

    Returns:
        True when an imported name is under an allowed module.

    """
    for module in allowed_modules:
        if imported == module:
            return True
        if imported.startswith(f"{module}."):
            return True
    return False


def code_only(path: project_dependencies.Path) -> str:
    """Remove comments and docstrings from Python source.

    Returns:
        Source text made from the syntax tree without its docstrings.

    """
    tree = architecture_test_declarations.parse_python_source(path)
    for node in standard_dependencies.ast.walk(tree):
        if isinstance(
            node,
            (
                standard_dependencies.ast.Module,
                standard_dependencies.ast.ClassDef,
                standard_dependencies.ast.FunctionDef,
                standard_dependencies.ast.AsyncFunctionDef,
            ),
        ):
            body = node.body
            if (
                body
                and isinstance(body[0], standard_dependencies.ast.Expr)
                and isinstance(body[0].value, standard_dependencies.ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                node.body = body[1:] or [standard_dependencies.ast.Pass()]
    return standard_dependencies.ast.unparse(standard_dependencies.ast.fix_missing_locations(tree))
