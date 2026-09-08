# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the send text request module."""

# The send-text gesture: text and/or attachments into the session.
from pydantic import model_validator

from api.controls.models.attachment_reference import AttachmentReferenceBody, references
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    SendText,
)


class SendTextRequest(ControlRequestBody):
    """Represent send text request."""

    text: str
    attachments: tuple[AttachmentReferenceBody, ...] = ()
    replace_terminal_draft: bool = False

    def request(self, session_id: SessionId) -> SendText:
        """Return the request.

        Returns:
            Request.

        """
        return SendText(
            session_id,
            RequestId(self.request_id),
            text=self.text,
            attachments=references(self.attachments),
            replace_terminal_draft=self.replace_terminal_draft,
        )

    @model_validator(mode="after")
    def _text_or_attachments(self) -> "SendTextRequest":
        if not self.text and not self.attachments:
            message = "text or attachments are required"
            raise ValueError(message)
        return self
