# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test architecture adapters."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_controls,
    architecture_test_declarations,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
IMPLEMENTATION_DIRECTORY_NAME = "impl"
HARNESS_PACKAGE = "harness"
CLAUDE_CODE_PACKAGE = "claude_code"
CODEX_PACKAGE = "codex"
IDS_FILE_NAME = "ids.py"


def test_adapter_identity_types_are_owned() -> None:
    """Verify adapter identity types are owned and prefixed by their adapter."""
    for adapter, prefix in ((CLAUDE_CODE_PACKAGE, "ClaudeCode"), (CODEX_PACKAGE, "Codex")):
        directory = ROOT / HARNESS_PACKAGE / IMPLEMENTATION_DIRECTORY_NAME / adapter
        declared = [
            name
            for path in directory.glob("id*_types.py")
            for name in _identity_types(path)
        ]
        assert declared
        assert all(name.startswith(prefix) for name in declared)


def _identity_types(path: project_dependencies.Path) -> list[str]:
    tree = architecture_test_declarations.parse_python_source(path)
    assignments = (
        node for node in tree.body
        if isinstance(node, standard_dependencies.ast.Assign)
        and isinstance(node.value, standard_dependencies.ast.Call)
        and getattr(node.value.func, "id", None) == "NewType"
    )
    return [
        target.id for node in assignments for target in node.targets
        if isinstance(target, standard_dependencies.ast.Name)
    ]


def test_adapters_map_native_entity_ids_only() -> None:
    """Verify adapters map native entity identifiers only in their identifier module."""
    canonical_entity_ids = {
        "ActorId",
        "AssignmentId",
        "AttentionId",
        "MessageId",
        "QuestionId",
        "ReasoningId",
        "SessionId",
        "ShellId",
        "SkillId",
        "TaskId",
        "TaskListId",
        "TurnId",
    }
    native_identifier_violations: list[str] = []
    for adapter in (CLAUDE_CODE_PACKAGE, CODEX_PACKAGE):
        native_identifier_violations.extend(
            architecture_test_controls.native_id_violations(adapter, canonical_entity_ids),
        )
    assert not native_identifier_violations
