# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test databases."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
MINIMUM_PROVIDER_COUNT = 40
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
DOMAIN_PACKAGE = "domain"
CORE_PACKAGE = "core"
HARNESS_PACKAGE = "harness"
CONTRACT_FILE_NAME = "contract.py"
MODELS_DIRECTORY_NAME = "models"
API_PACKAGE = "api"
APP_PACKAGE = "app"
DASHBOARD_PACKAGE = "dashboard"
ENGINE_PACKAGE = "engine"
TERMINAL_PACKAGE = "terminal"
HARNESS_ROOT = ROOT / HARNESS_PACKAGE
DASHBOARD_ROOT = ROOT / DASHBOARD_PACKAGE
SERVICES_DIRECTORY_NAME = "services"


def canonical_harness_shared_paths() -> project_dependencies.Iterator[project_dependencies.Path]:
    """Select shared harness files and packages for canonical checks.

    Yields:
        The contract, registry, models, hooks, and services paths.

    """
    harness_root = HARNESS_ROOT
    yield (harness_root / CONTRACT_FILE_NAME)
    yield (harness_root / "registry.py")
    yield (harness_root / MODELS_DIRECTORY_NAME)
    yield (harness_root / "hooks")
    yield (harness_root / SERVICES_DIRECTORY_NAME)


def paths_under(
    shared_paths: project_dependencies.Iterator[project_dependencies.Path],
) -> project_dependencies.Iterator[project_dependencies.Path]:
    """Expand selected directories into Python source paths.

    Yields:
        Python files under each directory, or the selected file itself.

    """
    for shared_path in shared_paths:
        if shared_path.is_dir():
            yield from shared_path.rglob(PYTHON_FILE_PATTERN)
        else:
            yield shared_path


def canonical_vocabulary_top_paths() -> project_dependencies.Iterator[project_dependencies.Path]:
    """Select top-level packages for canonical vocabulary checks.

    Yields:
        The selected application and domain package paths.

    """
    yield (ROOT / API_PACKAGE)
    yield (ROOT / APP_PACKAGE)
    yield (ROOT / CORE_PACKAGE)
    yield DASHBOARD_ROOT
    yield (ROOT / DOMAIN_PACKAGE)
    yield (ROOT / ENGINE_PACKAGE)
    yield (ROOT / TERMINAL_PACKAGE)


def bare_timestamp_ordering_lines(path: project_dependencies.Path) -> list[str]:
    """Return bare event timestamp ordering from one source file.

    Returns:
        Bare event timestamp ordering from one source file.

    """
    violations: list[str] = []
    for number, line in enumerate(path.read_text(encoding=TEXT_ENCODING).splitlines(), 1):
        if "occurred_at" not in line:
            continue
        if "ORDER BY" not in line.upper():
            continue
        if "COALESCE" not in line.upper():
            violations.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    return violations


def provider_modules() -> list[project_dependencies.ModuleType]:
    """Import the application provider modules.

    Returns:
        The modules whose names start with app.provider_.

    """
    return [
        standard_dependencies.importlib.import_module(module.name)
        for module in standard_dependencies.pkgutil.iter_modules([str(ROOT / APP_PACKAGE)], "app.")
        if module.name.startswith("app.provider_")
    ]


def provider_nodes(
    modules: list[project_dependencies.ModuleType],
) -> list[tuple[project_dependencies.ModuleType, str]]:
    """Find public provider members in the supplied modules.

    Returns:
        Module and member-name pairs for objects with a build attribute.

    """
    return [
        (module, name)
        for module in modules
        for name, member in standard_dependencies.inspect.getmembers(module)
        if not name.startswith("_") and hasattr(member, "build")
    ]


def assert_provider_nodes_resolve(
    instances: dict[object, object],
    nodes: list[tuple[project_dependencies.ModuleType, str]],
) -> None:
    """Check the provider count and stable resolution within one registry."""
    injection = standard_dependencies.importlib.import_module("app.injection")
    assert len(nodes) > MINIMUM_PROVIDER_COUNT, nodes
    for module, name in nodes:
        provider = getattr(module, name)
        assert injection.resolve(instances, provider) is injection.resolve(instances, provider), name
