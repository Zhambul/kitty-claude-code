# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared session-launch action for Gherkin step modules."""

from __future__ import annotations

from dataclasses import dataclass

from api.controls.models.attachment_reference import AttachmentReferenceBody
from sdk.client import BaqylauClient, SessionLaunchRequest
from tests.e2e.testkit import selector_turns
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.references import (
    Sessions,
    SessionSpecs,
    StagedAttachments,
    Turns,
)


@dataclass(frozen=True)
class SessionLaunchReferences:
    """Contain references that a session launch updates."""

    session_specs: SessionSpecs
    sessions: Sessions
    turns: Turns


@dataclass(frozen=True)
class SessionLaunchContext:
    """Contain services for one named session launch."""

    client: BaqylauClient
    workspace: str
    references: SessionLaunchReferences
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class AttachmentLaunchContext:
    """Contain services for one session launch with an attachment."""

    session_launch: SessionLaunchContext
    staged_attachments: StagedAttachments


@dataclass(frozen=True)
class NamedSessionLaunch:
    """Describe one named session launch."""

    session_name: str
    turn_name: str
    prompt: str
    attachments: tuple[AttachmentReferenceBody, ...] = ()


def start_named_session(
    context: SessionLaunchContext,
    request: NamedSessionLaunch,
) -> None:
    """Start named session."""
    spec = context.references.session_specs.get(request.session_name)
    launch = context.client.sessions.launch(
        SessionLaunchRequest(
            spec.harness,
            workspace=spec.workspace or context.workspace,
            prompt=request.prompt,
            model=spec.model,
            effort=spec.effort,
            attachments=request.attachments,
            account_id=spec.account_id,
        ),
    )
    session = context.client.sessions.wait_for_session(
        launch,
        context.wait_policy.session_announcement,
    )
    context.references.sessions.bind(request.session_name, session)
    context.references.turns.bind(
        request.turn_name,
        selector_turns.launched_turn(
            context.client.sessions.watch(session),
            context.wait_policy.feed,
        ),
    )
