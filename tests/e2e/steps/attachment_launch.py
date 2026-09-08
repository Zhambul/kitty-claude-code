# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that launch a session with an attachment."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit.attachments import attachment_reference
from tests.e2e.testkit.launching import NamedSessionLaunch, start_named_session

if TYPE_CHECKING:
    from tests.e2e.testkit.launching import AttachmentLaunchContext


@when(
    parsers.parse(
        'I launch session "{session_name}" as turn "{turn_name}" with attachment "{attachment_name}" and prompt',
    ),
)
def launch_with_attachment(
    attachment_launch_context: AttachmentLaunchContext,
    session_name: str,
    turn_name: str,
    attachment_name: str,
    docstring: str,
) -> None:
    """Launch a session with one staged attachment."""
    staged = attachment_launch_context.staged_attachments.get(attachment_name)
    start_named_session(
        attachment_launch_context.session_launch,
        NamedSessionLaunch(session_name, turn_name, docstring.strip(), (attachment_reference(staged),)),
    )
