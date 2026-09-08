# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the read plan choices request module."""

# The read-plan-choices gesture.
from api.common.models.fields import RequiredText
from api.controls.models.control_request import ControlRequestBody
from domain.ids import AttentionId, RequestId, SessionId
from harness.models.controls import (
    ReadPlanChoices,
)


class ReadPlanChoicesRequest(ControlRequestBody):
    """Represent read plan choices request."""

    attention_id: RequiredText

    def request(self, session_id: SessionId) -> ReadPlanChoices:
        """Return the request.

        Returns:
            Request.

        """
        return ReadPlanChoices(
            session_id,
            RequestId(self.request_id),
            attention_id=AttentionId(self.attention_id),
        )
