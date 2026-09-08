# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the launch session request module."""

# Launch (or resume) a harness session from the new-session form.
from pathlib import Path

from pydantic import BaseModel

from api.common.models.fields import RequiredText
from api.controls.models.attachment_reference import AttachmentReferenceBody, references
from domain.ids import AccountId, SessionId
from harness.models.launch import (
    LaunchRequest,
)


class LaunchSessionRequest(BaseModel):
    """Represent launch session request."""

    harness: RequiredText
    working_directory: RequiredText
    initial_text: str | None = None
    model_id: str | None = None
    effort: str | None = None
    account_id: str | None = None
    resume_session_id: str | None = None
    attachments: tuple[AttachmentReferenceBody, ...] = ()

    def request(self) -> LaunchRequest:
        """Return the request.

        Returns:
            Request.

        """
        return LaunchRequest(
            working_directory=str(Path(self.working_directory).expanduser().resolve()),
            initial_text=self.initial_text,
            model=self.model_id,
            effort=self.effort,
            account_id=AccountId(self.account_id) if self.account_id else None,
            resume_session_id=(SessionId(self.resume_session_id) if self.resume_session_id else None),
            attachments=references(self.attachments),
        )
