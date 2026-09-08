# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the decide plan request module."""

# The plan-decision gesture.
from api.common.models.fields import RequiredText
from api.controls.models.control_request import ControlRequestBody
from domain.ids import AttentionId, RequestId, SessionId
from harness.models.controls import (
    DecidePlan,
)


class DecidePlanRequest(ControlRequestBody):
    """Represent decide plan request."""

    attention_id: RequiredText
    decision: RequiredText
    feedback: str | None = None

    def request(self, session_id: SessionId) -> DecidePlan:
        """Return the request.

        Returns:
            Request.

        """
        return DecidePlan(
            session_id,
            RequestId(self.request_id),
            attention_id=AttentionId(self.attention_id),
            decision=self.decision,
            feedback=self.feedback,
        )
