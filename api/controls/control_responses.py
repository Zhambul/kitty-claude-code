# Copyright (c) 2026 Zhambyl Yermagambet
"""Map control and launch outcomes to HTTP responses."""

from http import HTTPStatus
from types import MappingProxyType

from fastapi import Response

from api.controls import mapper
from api.controls.models.control_outcome_response import ControlOutcomeResponse
from api.controls.models.launch_response import LaunchResponse
from api.responses import with_body
from harness.models.controls import ControlAcknowledgement, ControlOutcome, MessageDeliveryResult
from harness.models.launch import LaunchStatus

LAUNCH_STATUS = MappingProxyType({LaunchStatus.STARTED: 202, LaunchStatus.REJECTED: 409})
CONTROL_STATUS = MappingProxyType(
    {
        ControlAcknowledgement.ACKNOWLEDGED: 200,
        ControlAcknowledgement.INDETERMINATE: 202,
        ControlAcknowledgement.REJECTED: 409,
    },
)
LAUNCH_RESPONSES = with_body(LaunchResponse, {409: "Rejected — nothing was launched."})
CONTROL_RESPONSES = with_body(
    ControlOutcomeResponse,
    {
        202: "Sent, but the effect is unconfirmed — the browser reconciles from the stream.",
        409: "Rejected — the session cannot take this gesture now.",
    },
)


def respond(outcome: ControlOutcome, response: Response) -> ControlOutcomeResponse:
    """Return the mapped control outcome response.

    Returns:
        The control outcome response.

    """
    if isinstance(outcome, MessageDeliveryResult):
        response.status_code = HTTPStatus.OK
    else:
        response.status_code = CONTROL_STATUS[outcome.status]
    return mapper.control_outcome(outcome)
