# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that launch sessions and send session prompts."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit import launching, references as refs, session_contexts

if TYPE_CHECKING:
    from sdk.client import ActionReceipt


def _send_prompt(
    context: session_contexts.SessionPromptContext, request: session_contexts.PromptRequest,
) -> ActionReceipt:
    session = context.sessions.get(request.session_name)
    lead = context.client.sessions.snapshot(session).lead()
    receipt = context.client.sessions.send(session, request.prompt)
    if receipt.status_code != HTTPStatus.OK or receipt.outcome.status not in {"sent", "queued"}:
        message = f"send action {receipt.request_id!r} was not accepted: {receipt.outcome}"
        raise AssertionError(message)
    context.turns.bind(
        request.turn_name,
        refs.TurnRef(
            session, request.prompt, receipt.cursor_before, lead.statistics.prompt_count + 1, actor_id=lead.actor_id,
        ),
    )
    return receipt


@when(parsers.parse('I launch session "{session_name}" as turn "{turn_name}" with prompt'))
def launch_session(
    session_launch_context: launching.SessionLaunchContext,
    session_name: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Launch one session."""
    launching.start_named_session(
        session_launch_context,
        launching.NamedSessionLaunch(session_name, turn_name, docstring.strip()),
    )


@when(parsers.parse('I send prompt to session "{session_name}" as turn "{turn_name}"'))
def send_prompt(
    session_prompt_context: session_contexts.SessionPromptContext,
    session_name: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Send one prompt."""
    _send_prompt(
        session_prompt_context,
        session_contexts.PromptRequest(session_name, turn_name, docstring.strip()),
    )


@when(parsers.parse('I send prompt to session "{session_name}" as turn "{turn_name}" and control "{control_name}"'))
def send_prompt_as_control(
    session_control_context: session_contexts.SessionControlContext,
    session_name: str,
    turn_name: str,
    control_name: str,
    docstring: str,
) -> None:
    """Send one prompt and name its control."""
    request = session_contexts.PromptRequest(session_name, turn_name, docstring.strip())
    session_control_context.controls.bind(
        control_name,
        _send_prompt(session_control_context.prompts, request),
    )
