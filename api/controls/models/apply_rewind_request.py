# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the apply rewind request module."""

# The apply-rewind gesture.
from api.common.models.fields import RequiredText
from api.controls.models.control_request import ControlRequestBody
from domain.ids import MessageId, RequestId, SessionId
from harness.models.controls import (
    ApplyRewind,
)


class ApplyRewindRequest(ControlRequestBody):
    """Represent apply rewind request."""

    target_message_id: RequiredText
    target_text: RequiredText
    newer_prompt_count: int = 0
    mode: RequiredText

    def request(self, session_id: SessionId) -> ApplyRewind:
        """Return the request.

        Returns:
            Request.

        """
        return ApplyRewind(
            session_id,
            RequestId(self.request_id),
            target_message_id=MessageId(self.target_message_id),
            target_text=self.target_text,
            newer_prompt_count=self.newer_prompt_count,
            mode=self.mode,
        )
