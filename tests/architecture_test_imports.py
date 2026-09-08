# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test imports."""

from __future__ import annotations

from tests import (
    architecture_packages,
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_declarations,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
JSON_MODULE_NAME = "json"
API_PACKAGE = "api"
API_ROOT = ROOT / API_PACKAGE
BYTECODE_CACHE_DIRECTORY = "__pycache__"
type RouteHandler = tuple[
    project_dependencies.Path,
    standard_dependencies.ast.FunctionDef | standard_dependencies.ast.AsyncFunctionDef,
    list[str],
]
OUR_PACKAGES = architecture_packages.owned_packages()


def route_handlers() -> project_dependencies.Iterator[RouteHandler]:
    """Read route handlers from the API source files.

    Yields:
        The file path, function node, and decorator texts for each route.

    """
    for path in sorted(API_ROOT.rglob(PYTHON_FILE_PATTERN)):
        tree = architecture_test_declarations.parse_python_source(path)
        for node in standard_dependencies.ast.walk(tree):
            if not isinstance(
                node,
                (
                    standard_dependencies.ast.FunctionDef,
                    standard_dependencies.ast.AsyncFunctionDef,
                ),
            ):
                continue
            decorators = [standard_dependencies.ast.unparse(decorator) for decorator in node.decorator_list]
            if any(decorator_text.startswith(("router.", "guarded.", "web.")) for decorator_text in decorators):
                yield (path, node, decorators)


def imported_binding_name(alias: standard_dependencies.ast.alias) -> str:
    """Read the local name introduced by an import.

    Returns:
        The explicit alias, or the first component of the imported name.

    """
    if alias.asname:
        return alias.asname
    return alias.name.split(".")[0]


def declared_route_names(
    node: standard_dependencies.ast.FunctionDef | standard_dependencies.ast.AsyncFunctionDef,
    decorators: list[str],
) -> set[str]:
    """Read names from a route return annotation and response model decorators.

    Returns:
        The identifier tokens in those declarations.

    """
    declared = [standard_dependencies.ast.unparse(node.returns)] if node.returns else []
    declared.extend(

            decorator_text.split("response_model=", 1)[1].split(",")[0]
            for decorator_text in decorators
            if "response_model=" in decorator_text

    )
    return {token for text in declared for token in standard_dependencies.re.findall("[A-Za-z_][A-Za-z_0-9]*", text)}


def stale_json_exemptions(exemptions: list[str]) -> list[str]:
    """Find non-test exemptions whose matching files no longer use json calls.

    Returns:
        The patterns with no json member access in their matching files.

    """
    stale_exemptions = []
    for pattern in exemptions:
        if pattern.startswith("tests/"):
            continue
        matched_paths = sorted(ROOT.glob(pattern))
        assert matched_paths, f"{pattern} matches no file"
        if not any("json." in path.read_text(encoding=TEXT_ENCODING) for path in matched_paths):
            stale_exemptions.append(pattern)
    return stale_exemptions


def imports_json(node: standard_dependencies.ast.Import) -> bool:
    """Check an import statement for the json module.

    Returns:
        True if the statement imports json.

    """
    return JSON_MODULE_NAME in {alias.name for alias in node.names}


def is_json_call(function: standard_dependencies.ast.expr) -> bool:
    """Check a call target for json.loads or json.dumps.

    Returns:
        True for either direct json module member.

    """
    if not isinstance(function, standard_dependencies.ast.Attribute):
        return False
    if function.attr not in {"dumps", "loads"}:
        return False
    return isinstance(function.value, standard_dependencies.ast.Name) and function.value.id == JSON_MODULE_NAME


def owned_python_files() -> list[project_dependencies.Path]:
    """Find owned Python files outside cache and dependency directories.

    Returns:
        The sorted source file paths.

    """
    return sorted(

            path
            for package in OUR_PACKAGES
            for path in (ROOT / package).rglob(PYTHON_FILE_PATTERN)
            if not any(part in {BYTECODE_CACHE_DIRECTORY, "node_modules"} for part in path.parts)

    )
