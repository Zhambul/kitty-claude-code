# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

from dataclasses import dataclass

from sdk import application_models, control_models, state


@dataclass(frozen=True)
class SessionLaunchRequest:
    """Contain one session launch request."""

    harness: str
    workspace: str
    prompt: str | None
    model: str | None
    effort: str | None
    resume_session_id: str | None = None
    attachments: tuple[control_models.attachment_reference.AttachmentReferenceBody, ...] = ()
    account_id: str | None = None


@dataclass(frozen=True)
class LaunchRef:
    """Represent launch ref."""

    harness: str
    workspace: str
    window_id: str
    known_session_ids: frozenset[str]


@dataclass(frozen=True)
class ActionReceipt:
    """Represent action receipt."""

    request_id: str
    status_code: int
    outcome: control_models.control_outcome_response.ControlOutcomeResponse
    cursor_before: int


@dataclass(frozen=True)
class SessionSnapshotRead:
    """Represent session snapshot read."""

    snapshot: state.SessionSnapshot
    page_count: int


@dataclass(frozen=True)
class SessionStreamUpdate:
    """Represent session stream update."""

    cursor: int
    frame: application_models.stream_frame.SessionStreamFrame


@dataclass(frozen=True)
class GlobalStreamUpdate:
    """Represent global stream update."""

    cursor: int
    frame: application_models.stream_frame.GlobalStreamFrame


SessionRef = state.SessionRef
