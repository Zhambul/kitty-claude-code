# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test adapters."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
)

# Keep dependency modules separate from test helpers.
# isort: split

from tests import (
    architecture_test_controls,
    architecture_test_declarations,
    architecture_test_imports,
    architecture_test_protocols,
    architecture_test_registrations,
    architecture_test_syntax,
    architecture_test_tables,
)

# Keep inheritance resolution separate from source scanning.
# isort: split

from tests import architecture_test_inheritance

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
IMPLEMENTATION_DIRECTORY_NAME = "impl"
HARNESS_PACKAGE = "harness"
BYTECODE_CACHE_DIRECTORY = "__pycache__"
type MethodSignatures = dict[str, tuple[str, ...]]
type RegisteredHandler = tuple[str, str, str | None, list[str] | None]


def protocols_and_classes() -> tuple[dict[str, MethodSignatures], list[architecture_test_syntax.ClassDescription]]:
    """Read public protocols and concrete classes from application source files.

    Returns:
        Protocol signatures and concrete class descriptions.

    """
    declarations = tuple(
        declaration
        for path in architecture_test_tables.source_python_paths()
        for declaration in architecture_test_protocols.classes_in_path(path)
    )
    protocols = {description.name: description for is_protocol, description in declarations if is_protocol}
    classes = [description for is_protocol, description in declarations if not is_protocol]
    return architecture_test_inheritance.resolved_contracts(protocols, classes)


def protocol_divergences(
    description: architecture_test_syntax.ClassDescription, protocols: dict[str, MethodSignatures],
) -> list[str]:
    """Compare a class with the protocols declared in its bases.

    Returns:
        All method signature mismatch messages.

    """
    divergent: list[str] = []
    for protocol in description.bases:
        signature = protocols.get(protocol)
        if signature is None:
            continue
        divergent.extend(architecture_test_protocols.protocol_member_divergences(description, protocol, signature))
    return divergent


def control_names() -> set[str]:
    """Read the supported control names.

    Returns:
        The string values declared by the control enumeration.

    """
    return set(architecture_test_controls.control_name_values().values())


def _registered_handlers_in(
    path: project_dependencies.Path, control_name_values: dict[str, str],
) -> project_dependencies.Iterator[RegisteredHandler]:
    tree = architecture_test_declarations.parse_python_source(path)
    for node in standard_dependencies.ast.walk(tree):
        if not isinstance(node, standard_dependencies.ast.Call):
            continue
        if getattr(node.func, "id", None) != "HarnessController":
            continue
        for argument in node.args:
            yield from architecture_test_registrations.registrations(path, argument, control_name_values)


def outside_route_models() -> list[str]:
    """Check API routes for response models outside the API layer.

    Returns:
        All route response declaration failures.

    """
    outside: list[str] = []
    for path, node, decorators in architecture_test_imports.route_handlers():
        outside.extend(architecture_test_controls.route_model_violations(path, node, decorators))
    return outside


def dictionary_literal_violation(
    node: standard_dependencies.ast.AST,
    parents: project_dependencies.Mapping[standard_dependencies.ast.AST, standard_dependencies.ast.AST],
    allowed_registries: project_dependencies.AbstractSet[str],
) -> str | None:
    """Return a violation for one unapproved dictionary literal.

    Returns:
        A violation for one unapproved dictionary literal.

    """
    if architecture_test_controls.is_unapproved_dictionary(node, parents, allowed_registries):
        return "contains a dictionary literal"
    return None


def registered_handlers() -> project_dependencies.Iterator[RegisteredHandler]:
    """Read registered harness control handlers.

    Yields:
        Each handler's location, control name, class name, and declared bases.

    """
    control_name_values = architecture_test_controls.control_name_values()
    for path in (ROOT / HARNESS_PACKAGE / IMPLEMENTATION_DIRECTORY_NAME).rglob(PYTHON_FILE_PATTERN):
        if BYTECODE_CACHE_DIRECTORY in path.parts:
            continue
        yield from _registered_handlers_in(path, control_name_values)
