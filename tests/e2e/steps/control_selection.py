# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that change session model settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

if TYPE_CHECKING:
    from tests.e2e.testkit.session_contexts import SessionControlContext


@when(parsers.parse('I select model {model} in session "{session_name}" as control "{control_name}"'))
def select_model(
    session_control_context: SessionControlContext,
    session_name: str,
    model: str,
    control_name: str,
) -> None:
    """Select a session model."""
    session_control_context.controls.bind(
        control_name,
        session_control_context.prompts.client.sessions.select_model(
            session_control_context.prompts.sessions.get(session_name),
            model,
        ),
    )


@when(parsers.parse('I select {effort} effort in session "{session_name}" as control "{control_name}"'))
def select_effort(
    session_control_context: SessionControlContext,
    session_name: str,
    effort: str,
    control_name: str,
) -> None:
    """Select a session effort level."""
    session_control_context.controls.bind(
        control_name,
        session_control_context.prompts.client.sessions.select_effort(
            session_control_context.prompts.sessions.get(session_name),
            effort,
        ),
    )
