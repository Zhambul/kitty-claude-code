# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata loop entries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from audit.failures import FailureContext
from tests import (
    canonical_sessiondata_fixtures as session_fixtures,
    canonical_sessiondata_loop_support as loop_support,
    canonical_sessiondata_values as session_values,
)
from tests.canonical_sessiondata_components import domain as session_domain

if TYPE_CHECKING:
    from pathlib import Path


def test_body_carrying_entry_folded_empty_writes(tmp_path: Path) -> None:
    """Verify a body carrying entry folded empty writes one audit row.

    The last silent shape: an entry a reader expands expecting content
        lands empty, with no exception and a 200 for the fold. The row still
        applies — this only leaves a trace pointing back at the fact that made
        it, so the cause stays attributable.
    """
    loop, read_model, audit = loop_support.loop_over(
        tmp_path,
        (
            *session_fixtures.alive(),
            session_domain.event_conversation.MessageCreated(
                session_values.FIRST_MESSAGE_ID,
                session_domain.messaging.MessageRole.ASSISTANT,
                session_domain.content.TextContent(""),
                session_domain.messaging.MessagePhase.END_TURN,
                None,
            ),
        ),
    )
    loop.tick()

    entries = read_model.entries_page(session_values.SESSION, limit=10).entries
    assert ([entry.entry_type for entry in entries], loop_support.failure_locations(audit)) == (
        [session_values.MESSAGE_ENTRY_TYPE],
        ["entry fold (empty body)"],
    )
    context = audit.failures[0][1]
    assert isinstance(context, FailureContext)
    assert (
        context.entry_id,
        context.entry_type,
        context.event_type,
        context.session_id,
    ) == (entries[0].entry_id, session_values.MESSAGE_ENTRY_TYPE, "message.created", session_values.SESSION)


def test_legitimately_empty_marker_writes_no(tmp_path: Path) -> None:
    """Verify a legitimately empty marker writes no audit row.

    A turn marker carries nothing by design, so it must never trip the
        empty-body trace meant for the kinds a reader expects content in.
    """
    loop, _read_model, audit = loop_support.loop_over(
        tmp_path,
        (
            *session_fixtures.alive(),
            session_domain.event_conversation.TurnStarted(session_values.FIRST_MESSAGE_ID),
        ),
    )
    loop.tick()
    assert audit.failures == []


def test_successful_command_with_no_output_writes(tmp_path: Path) -> None:
    """Verify a successful command with no output writes no audit row."""
    loop, _read_model, audit = loop_support.loop_over(
        tmp_path,
        (
            *session_fixtures.alive(),
            session_domain.event_shell.ShellFinished(
                session_domain.ids.ShellId("quiet"),
                session_domain.outcomes.Outcome.SUCCEEDED,
                None,
                0,
            ),
        ),
    )
    loop.tick()
    assert audit.failures == []


def test_a_body_with_content_writes_no_audit_row(tmp_path: Path) -> None:
    """Verify a body with content writes no audit row."""
    loop, _read_model, audit = loop_support.loop_over(
        tmp_path,
        (
            *session_fixtures.alive(),
            session_domain.event_conversation.MessageCreated(
                session_values.FIRST_MESSAGE_ID,
                session_domain.messaging.MessageRole.ASSISTANT,
                session_domain.content.TextContent("hi"),
                session_domain.messaging.MessagePhase.END_TURN,
                None,
            ),
        ),
    )
    loop.tick()
    assert audit.failures == []


def test_rename_and_failed_file_access(tmp_path: Path) -> None:
    """Verify a rename and a failed file access are complete without content."""
    loop, _read_model, audit = loop_support.loop_over(
        tmp_path,
        (
            *session_fixtures.alive(),
            session_domain.event_resource.FileAccessed(
                "/work/after.txt",
                session_domain.outcomes.FileAction.RENAMED,
                session_domain.outcomes.Outcome.SUCCEEDED,
                previous_path="/work/before.txt",
            ),
            session_domain.event_resource.FileAccessed(
                "/work/missing.txt",
                session_domain.outcomes.FileAction.READ,
                session_domain.outcomes.Outcome.FAILED,
            ),
        ),
    )
    loop.tick()

    assert audit.failures == []
