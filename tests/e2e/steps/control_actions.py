# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that request session control actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

if TYPE_CHECKING:
    from sdk import client as sdk_client
    from tests.e2e.testkit.references import Controls, Sessions
    from tests.e2e.testkit.session_contexts import SessionControlContext


@when(parsers.parse('I request backgrounding in session "{session_name}" as control "{control_name}"'))
def request_backgrounding(
    client: sdk_client.BaqylauClient,
    sessions: Sessions,
    controls: Controls,
    session_name: str,
    control_name: str,
) -> None:
    """Request backgrounding for a session."""
    controls.bind(control_name, client.sessions.background(sessions[session_name]))


@when(parsers.parse('I request interruption in session "{session_name}" as control "{control_name}"'))
def request_interruption(
    client: sdk_client.BaqylauClient,
    sessions: Sessions,
    controls: Controls,
    session_name: str,
    control_name: str,
) -> None:
    """Request interruption for a session."""
    controls.bind(control_name, client.sessions.interrupt(sessions.get(session_name)))


@when(parsers.parse('I send native command \'{command}\' to session "{session_name}" as control "{control_name}"'))
def send_native_command(
    session_control_context: SessionControlContext,
    command: str,
    session_name: str,
    control_name: str,
) -> None:
    """Send a native harness command."""
    session_control_context.controls.bind(
        control_name,
        session_control_context.prompts.client.sessions.send(
            session_control_context.prompts.sessions.get(session_name),
            command,
        ),
    )


@when(parsers.parse('I rename session "{session_name}" to \'{new_name}\' as control "{control_name}"'))
def rename_session(
    session_control_context: SessionControlContext,
    session_name: str,
    new_name: str,
    control_name: str,
) -> None:
    """Rename a session."""
    session_control_context.controls.bind(
        control_name,
        session_control_context.prompts.client.sessions.rename(
            session_control_context.prompts.sessions.get(session_name),
            new_name,
        ),
    )


@when(parsers.parse('I request an automatic name for session "{session_name}" as control "{control_name}"'))
def auto_name_session(
    client: sdk_client.BaqylauClient,
    sessions: Sessions,
    controls: Controls,
    session_name: str,
    control_name: str,
) -> None:
    """Request an automatic session name."""
    controls.bind(control_name, client.sessions.auto_name(sessions.get(session_name)))


@when(parsers.parse('I request compaction in session "{session_name}" as control "{control_name}"'))
def request_compaction(
    client: sdk_client.BaqylauClient,
    sessions: Sessions,
    controls: Controls,
    session_name: str,
    control_name: str,
) -> None:
    """Request session compaction."""
    controls.bind(control_name, client.sessions.compact(sessions.get(session_name)))


@when(parsers.parse('I close session "{session_name}" as control "{control_name}"'))
def close_session(
    client: sdk_client.BaqylauClient,
    sessions: Sessions,
    controls: Controls,
    session_name: str,
    control_name: str,
) -> None:
    """Close a session."""
    controls.bind(control_name, client.sessions.close(sessions.get(session_name)))
