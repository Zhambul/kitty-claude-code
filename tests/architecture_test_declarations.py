# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test declarations."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_adapters,
    architecture_test_controls,
    architecture_test_layers,
    architecture_test_routes,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"


def parse_python_source(path: project_dependencies.Path) -> standard_dependencies.ast.Module:
    """Parse one owned Python file.

    Returns:
        The syntax tree for the file.

    """
    return standard_dependencies.ast.parse(
        path.read_text(encoding=TEXT_ENCODING),
        filename=str(path),
    )


def _raw_node_violations(
    node: standard_dependencies.ast.AST,
    parents: project_dependencies.Mapping[standard_dependencies.ast.AST, standard_dependencies.ast.AST],
    allowed_registries: project_dependencies.AbstractSet[str],
) -> tuple[str, ...]:
    """Return raw dictionary violations for one syntax node.

    Returns:
        Raw dictionary violations for one syntax node.

    """
    possible_violations = (
        architecture_test_adapters.dictionary_literal_violation(node, parents, allowed_registries),
        architecture_test_routes.model_dump_violation(node),
        architecture_test_controls.dictionary_type_violation(node, parents, allowed_registries),
        architecture_test_layers.json_value_violation(node, parents),
    )
    return tuple(
        violation for violation in possible_violations if violation is not None
    ) + architecture_test_layers.import_violations(node)


def _raw_node_messages(
    node: standard_dependencies.ast.AST,
    relative_path: str,
    parents: project_dependencies.Mapping[standard_dependencies.ast.AST, standard_dependencies.ast.AST],
    allowed_registries: project_dependencies.AbstractSet[str],
) -> project_dependencies.Iterator[str]:
    for violation in _raw_node_violations(node, parents, allowed_registries):
        yield f"{relative_path}:{getattr(node, 'lineno', 1)} {violation}"


def raw_dictionary_violations(
    path: project_dependencies.Path,
    typed_registry_allowlist: project_dependencies.Mapping[str, project_dependencies.AbstractSet[str]],
) -> project_dependencies.Iterator[str]:
    """Find raw dictionary violations for one source file.

    Yields:
        Each violation with its file path and line number.

    """
    tree = parse_python_source(path)
    parents: dict[standard_dependencies.ast.AST, standard_dependencies.ast.AST] = {
        child: parent
        for parent in standard_dependencies.ast.walk(tree)
        for child in standard_dependencies.ast.iter_child_nodes(parent)
    }
    relative_path = str(path.relative_to(ROOT))
    allowed_registries = typed_registry_allowlist.get(relative_path, set())
    for node in standard_dependencies.ast.walk(tree):
        yield from _raw_node_messages(node, relative_path, parents, allowed_registries)
