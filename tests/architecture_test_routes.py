# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test routes."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_declarations,
    architecture_test_imports,
    architecture_test_layers,
    architecture_test_syntax,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
JSON_MODULE_NAME = "json"


def terminal_name_violation(
    path: project_dependencies.Path,
    implementation: project_dependencies.Path,
    registry: project_dependencies.Path,
) -> str | None:
    """Check terminal names outside the implementation and registry.

    Returns:
        A message with forbidden names, or None for valid or exempt files.

    """
    if implementation in path.parents or path == registry:
        return None
    lowered = path.read_text(encoding=TEXT_ENCODING).lower()
    words = [word for word in ("kitty", "kitten") if word in lowered]
    return architecture_test_syntax.contains_message(path.relative_to(ROOT), words) if words else None


def import_bindings(node: standard_dependencies.ast.AST) -> dict[str, str]:
    """Return bindings introduced by one import node.

    Returns:
        Bindings introduced by one import node.

    """
    if isinstance(node, standard_dependencies.ast.ImportFrom):
        if node.module is None:
            return {}
        return {alias.asname or alias.name: node.module for alias in node.names}
    if isinstance(node, standard_dependencies.ast.Import):
        return {architecture_test_imports.imported_binding_name(alias): alias.name for alias in node.names}
    return {}


def response_encoder_import_offenders(
    path: project_dependencies.Path, node: standard_dependencies.ast.AST,
) -> list[str]:
    """Return response-encoder imports from one syntax node.

    Returns:
        Response-encoder imports from one syntax node.

    """
    relative_path = path.relative_to(ROOT)
    if isinstance(node, standard_dependencies.ast.Import):
        if architecture_test_imports.imports_json(node):
            return [f"{relative_path} imports json"]
        return []
    if not isinstance(node, standard_dependencies.ast.ImportFrom):
        return []
    if node.module not in {JSON_MODULE_NAME, "fastapi.responses", "starlette.responses"}:
        return []
    return [
        f"{relative_path} imports {alias.name}"
        for alias in node.names
        if node.module == JSON_MODULE_NAME or alias.name == "JSONResponse"
    ]


def calls_json(path: project_dependencies.Path) -> bool:
    """Check the syntax tree for a JSON function call.

    Returns:
        True if the file calls a JSON function. Comments do not count.

    """
    tree = architecture_test_declarations.parse_python_source(path)
    for node in standard_dependencies.ast.walk(tree):
        if not isinstance(node, standard_dependencies.ast.Call):
            continue
        function = node.func
        if architecture_test_imports.is_json_call(function):
            return True
    return False


def owner_name(node: standard_dependencies.ast.AST) -> str | None:
    """Return the direct name that one parent syntax node owns.

    Returns:
        The direct name that one parent syntax node owns.

    """
    if isinstance(node, (
        standard_dependencies.ast.arg,
        standard_dependencies.ast.FunctionDef,
        standard_dependencies.ast.AsyncFunctionDef,
    )):
        return node.arg if isinstance(node, standard_dependencies.ast.arg) else node.name
    if isinstance(node, standard_dependencies.ast.AnnAssign):
        return architecture_test_layers.target_name(node.target)
    if (
        isinstance(node, standard_dependencies.ast.TypeAlias)
        and isinstance(node.name, standard_dependencies.ast.Name)
    ):
        return node.name.id
    if isinstance(node, standard_dependencies.ast.Assign) and len(node.targets) == 1:
        return architecture_test_layers.target_name(node.targets[0])
    return None


def model_dump_violation(node: standard_dependencies.ast.AST) -> str | None:
    """Return a violation for one model dump to a dictionary.

    Returns:
        A violation for one model dump to a dictionary.

    """
    if architecture_test_layers.is_model_dump(node):
        return "materializes model_dump() as a dictionary"
    return None


def raw_json_import_violations(path: project_dependencies.Path, node: standard_dependencies.ast.AST) -> list[str]:
    """Return raw JSON codec imports from one syntax node.

    Returns:
        Raw JSON codec imports from one syntax node.

    """
    if isinstance(node, standard_dependencies.ast.Import):
        if architecture_test_imports.imports_json(node):
            return [f"{path.relative_to(ROOT)}:{node.lineno} imports json"]
        return []
    if isinstance(node, standard_dependencies.ast.ImportFrom) and node.module == JSON_MODULE_NAME:
        return [f"{path.relative_to(ROOT)}:{node.lineno} imports from json"]
    return []
