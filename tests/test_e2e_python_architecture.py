# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify direct Python E2E tests declare their harness limit."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from tests import e2e_feature_scenarios as feature_scenarios

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


def direct_test_functions(tree: ast.Module) -> tuple[ast.AsyncFunctionDef | ast.FunctionDef, ...]:
    """Return direct test functions in module and class containers.

    Returns:
        Direct test functions in module and class containers.

    """
    tests: list[ast.AsyncFunctionDef | ast.FunctionDef] = []
    for container in nested_test_containers(tree):
        for node in container.body:
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            if node.name.startswith("test_"):
                tests.append(node)
    return tuple(tests)


def nested_test_containers(tree: ast.Module | ast.ClassDef) -> Iterator[ast.Module | ast.ClassDef]:
    """Read a test container and its nested classes.

    Yields:
        The supplied container, followed by its nested class containers.

    """
    yield tree
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            yield from nested_test_containers(node)


def direct_test_node_violations(
    path: Path,
    source_lines: list[str],
    node: ast.AsyncFunctionDef | ast.FunctionDef,
) -> tuple[str, ...]:
    """Return harness comment violations for one direct test function.

    Returns:
        Harness comment violations for one direct test function.

    """
    first_line = first_test_line(node)
    comment = source_lines[first_line - 2] if first_line > 1 else ""
    limits = feature_scenarios.HarnessLimit.parse(comment)
    location = f"{path.relative_to(feature_scenarios.ROOT)}: {node.name}"
    violations: list[str] = []
    if len(limits) != 1:
        violations.append(f"{location} needs one '# Harness limit:' comment directly above it")
        return tuple(violations)
    if limits[0].harnesses == feature_scenarios.HARNESSES:
        violations.append(f"{location} has a stale harness limit comment")
    if not limits[0].reason.rstrip().endswith("."):
        violations.append(f"{location} has an incomplete harness limit reason")
    return tuple(violations)


def first_test_line(node: ast.AsyncFunctionDef | ast.FunctionDef) -> int:
    """Return the first decorator or definition line for a test.

    Returns:
        The first decorator or definition line for a test.

    """
    lines = [syntax_node.lineno for syntax_node in node.decorator_list]
    return min((*lines, node.lineno))


def direct_test_violations(path: Path) -> Iterator[str]:
    """Check harness comments on direct tests in a file.

    Yields:
        Each comment violation reported for a test function.

    """
    source = path.read_text(encoding=feature_scenarios.TEXT_ENCODING)
    source_lines = source.splitlines()
    for node in direct_test_functions(ast.parse(source)):
        yield from direct_test_node_violations(path, source_lines, node)


def test_direct_python_e2e_tests_declare_harness() -> None:
    """Verify direct Python E2E tests declare a harness limit."""
    e2e_root = feature_scenarios.ROOT / "tests" / "e2e"
    violations = [
        violation for path in sorted(e2e_root.rglob("test_*.py")) for violation in direct_test_violations(path)
    ]
    assert not violations
