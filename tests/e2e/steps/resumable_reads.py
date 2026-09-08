# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that read and search resumable sessions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.observation_contexts import ResumableSearchContext
    from tests.e2e.testkit.references import ResumableLists


@when(parsers.parse('I read resumable sessions for the workspace as "{name}"'))
def read_resumable_sessions(client: BaqylauClient, workspace: str, resumable_lists: ResumableLists, name: str) -> None:
    """Read and name the workspace resumable sessions."""
    resumable_lists.bind(name, client.insights.resumable_sessions(workspace=workspace))


@when(parsers.parse("I search resumable sessions for '{search}' as \"{name}\""))
def search_resumable_sessions(
    client: BaqylauClient,
    workspace: str,
    resumable_lists: ResumableLists,
    search: str,
    name: str,
) -> None:
    """Search and name workspace resumable sessions."""
    resumable_lists.bind(name, client.insights.resumable_sessions(workspace=workspace, search=search))


@when(parsers.parse('I search resumable sessions for session "{session_name}" ID as "{name}"'))
def search_resumable_sessions_by_id(
    resumable_search_context: ResumableSearchContext,
    session_name: str,
    name: str,
) -> None:
    """Search resumable sessions by a named session identifier."""
    resumable_search_context.resumable_lists.bind(
        name,
        resumable_search_context.client.insights.resumable_sessions(
            workspace=resumable_search_context.workspace,
            search=str(resumable_search_context.sessions.get(session_name).session_id),
        ),
    )
