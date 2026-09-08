# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check named file operations."""

from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import file_operations as file_operation_checks

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.action_contexts import WorkspaceFileContext
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import FileOperations


@then(parsers.parse('file operation "{name}" has state {state}'))
def file_operation_has_state(
    client: BaqylauClient,
    file_operations: FileOperations,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Verify a named file operation state."""
    reference = file_operations.get(name)
    client.sessions.watch(reference.session).wait(
        f"file operation {name!r} to have state {state!r}",
        partial(file_operation_checks.has_state, reference=reference, state=state),
        timeout=wait_policy.feed,
    )


@then(parsers.parse("file operation \"{name}\" has content containing '{text}'"))
def file_operation_has_content(
    client: BaqylauClient,
    file_operations: FileOperations,
    wait_policy: WaitPolicy,
    name: str,
    text: str,
) -> None:
    """Verify named file operation content."""
    reference = file_operations.get(name)
    client.sessions.watch(reference.session).wait(
        f"file operation {name!r} content to contain {text!r}",
        partial(file_operation_checks.content_contains, reference=reference, text=text),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('file operation "{name}" has added lines'))
def file_operation_has_added_lines(
    client: BaqylauClient,
    file_operations: FileOperations,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Verify named file operation has added lines."""
    reference = file_operations.get(name)
    client.sessions.watch(reference.session).wait(
        f"file operation {name!r} to have added lines",
        partial(file_operation_checks.has_added_lines, reference=reference),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('file operation "{name}" has removed lines'))
def file_operation_has_removed_lines(
    client: BaqylauClient,
    file_operations: FileOperations,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Verify named file operation has removed lines."""
    reference = file_operations.get(name)
    client.sessions.watch(reference.session).wait(
        f"file operation {name!r} to have removed lines",
        partial(file_operation_checks.has_removed_lines, reference=reference),
        timeout=wait_policy.feed,
    )


@then(
    parsers.parse(
        "file operation \"{name}\" moved workspace file '{previous_relative_path}' "
        "to '{current_relative_path}'",
    ),
)
def file_operation_moved_workspace_file(
    workspace_file_context: WorkspaceFileContext,
    name: str,
    previous_relative_path: str,
    current_relative_path: str,
) -> None:
    """Verify one file operation moved a workspace file."""
    reference = workspace_file_context.operations.get(name)
    operation = file_operation_checks.operation(
        workspace_file_context.client.sessions.snapshot(reference.session),
        reference,
    )
    previous_path = str(Path(workspace_file_context.workspace) / previous_relative_path)
    current_path = str(Path(workspace_file_context.workspace) / current_relative_path)
    assert (operation.previous_path, operation.path) == (previous_path, current_path)
