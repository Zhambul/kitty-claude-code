# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test tables."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
PYTHON_FILE_PATTERN = "*.py"
DOMAIN_PACKAGE = "domain"
CORE_PACKAGE = "core"
AUDIT_PACKAGE = "audit"
HARNESS_PACKAGE = "harness"
APP_PACKAGE = "app"
DASHBOARD_PACKAGE = "dashboard"
ENGINE_PACKAGE = "engine"
NOTIFY_PACKAGE = "notify"
TERMINAL_PACKAGE = "terminal"
BYTECODE_CACHE_DIRECTORY = "__pycache__"
SOURCE_PACKAGES = (
    APP_PACKAGE,
    CORE_PACKAGE,
    DASHBOARD_PACKAGE,
    AUDIT_PACKAGE,
    DOMAIN_PACKAGE,
    HARNESS_PACKAGE,
    ENGINE_PACKAGE,
    NOTIFY_PACKAGE,
    TERMINAL_PACKAGE,
)


def assert_registry_is_isolated(instances: dict[object, object]) -> None:
    """Check that a new provider registry has a separate database instance."""
    injection = standard_dependencies.importlib.import_module("app.injection")
    other = injection.registry()
    database_provider = standard_dependencies.importlib.import_module("app.provider_databases").main_db
    assert injection.resolve(other, database_provider) is not injection.resolve(instances, database_provider)


def method_signatures(node: standard_dependencies.ast.ClassDef) -> dict[str, tuple[str, ...]]:
    """Read parameter names from methods declared directly in a class.

    Returns:
        Each declared method name and its positional parameter names.

    """
    return {
        member.name: (
            tuple(argument.arg for argument in member.args.args)
            + tuple(f"*{argument.arg}" for argument in member.args.kwonlyargs)
        )
        for member in node.body
        if isinstance(
            member,
            (
                standard_dependencies.ast.FunctionDef,
                standard_dependencies.ast.AsyncFunctionDef,
            ),
        )
    }


def source_python_paths() -> project_dependencies.Iterator[project_dependencies.Path]:
    """Find source files for protocol checks.

    Yields:
        Python file paths outside bytecode cache directories.

    """
    for package in SOURCE_PACKAGES:
        for path in (ROOT / package).rglob(PYTHON_FILE_PATTERN):
            if BYTECODE_CACHE_DIRECTORY not in path.parts:
                yield path


def has_generic_protocol_base(bases: list[str]) -> bool:
    """Check for a parameterized or qualified protocol base.

    Returns:
        True if a base starts with Protocol[ or typing.Protocol.

    """
    return any(base.startswith(("Protocol[", "typing.Protocol")) for base in bases)


def satisfies(members: dict, protocol: dict) -> bool:
    """Every protocol method is present with the same parameter NAMES.

    Names, not just arity: they are part of the contract because any of these
    may be called with keywords, and a renamed parameter is exactly the drift
    this test exists to catch. Matching on names is also what keeps the check
    precise -- `read(self, context)` and `read(self)` are different protocols,
    so a class does not accidentally implement one by owning a common verb.

    Returns:
        True if the protocol is not empty and all method parameters match.

    """
    if not protocol:
        return False
    return all(
        members.get(name) == arguments
        for name, arguments in protocol.items()
    )


def control_member_value(statement: standard_dependencies.ast.stmt) -> tuple[str, str] | None:
    """Read a string assigned to one named control member.

    Returns:
        The member name and value, or None for another statement shape.

    """
    if not isinstance(statement, standard_dependencies.ast.Assign):
        return None
    if len(statement.targets) != 1:
        return None
    target = statement.targets[0]
    control_value = statement.value
    if not isinstance(target, standard_dependencies.ast.Name) or not isinstance(
        control_value, standard_dependencies.ast.Constant,
    ):
        return None
    if not isinstance(control_value.value, str):
        return None
    return (target.id, control_value.value)


def control_class(
    tree: standard_dependencies.ast.Module,
) -> standard_dependencies.ast.ClassDef:
    """Find the ControlName class in a syntax tree.

    Returns:
        The ControlName class declaration.

    Raises:
        AssertionError: If the tree has no ControlName class.

    """
    for node in standard_dependencies.ast.walk(tree):
        if isinstance(node, standard_dependencies.ast.ClassDef) and node.name == "ControlName":
            return node
    message = "ControlName is missing"
    raise AssertionError(message)
