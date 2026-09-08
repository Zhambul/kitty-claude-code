# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the rename session request module."""

# The rename gesture.
from api.common.models.fields import RequiredText
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    RenameSession,
)


class RenameSessionRequest(ControlRequestBody):
    """Represent rename session request."""

    name: RequiredText

    def request(self, session_id: SessionId) -> RenameSession:
        """Return the request.

        Returns:
            Request.

        """
        return RenameSession(session_id, RequestId(self.request_id), name=self.name)
