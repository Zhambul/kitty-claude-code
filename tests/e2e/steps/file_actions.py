# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that name file operations from a session feed."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit import selector_operations

if TYPE_CHECKING:
    from tests.e2e.testkit.action_contexts import FileFixtureContext, WorkspaceFileContext


@when(parsers.parse('I name the {action} fixture operation in turn "{turn_name}" "{operation_name}"'))
@when(parsers.parse('I name the {action} fixture operation in work "{turn_name}" "{operation_name}"'))
def name_fixture_operation(
    file_fixture_context: FileFixtureContext,
    action: str,
    turn_name: str,
    operation_name: str,
) -> None:
    """Name one file fixture operation."""
    turn = file_fixture_context.turns.get(turn_name)
    found = selector_operations.file_operation(
        file_fixture_context.client.sessions.watch(turn.session),
        turn_reference=turn,
        path=file_fixture_context.path,
        action=action,
        timeout=file_fixture_context.wait_policy.feed,
    )
    file_fixture_context.operations.bind(operation_name, found)


@when(
    parsers.parse(
        'I name the {action} operation in turn "{turn_name}" for workspace file \'{relative_path}\' "{operation_name}"',
    ),
)
@when(
    parsers.parse(
        'I name the {action} operation in work "{turn_name}" for workspace file \'{relative_path}\' "{operation_name}"',
    ),
)
def name_workspace_file_operation(
    workspace_file_context: WorkspaceFileContext,
    action: str,
    turn_name: str,
    relative_path: str,
    operation_name: str,
) -> None:
    """Name one workspace-file operation."""
    turn = workspace_file_context.turns.get(turn_name)
    found = selector_operations.file_operation(
        workspace_file_context.client.sessions.watch(turn.session),
        turn_reference=turn,
        path=str(Path(workspace_file_context.workspace) / relative_path),
        action=action,
        timeout=workspace_file_context.wait_policy.feed,
    )
    workspace_file_context.operations.bind(operation_name, found)
