# Copyright (c) 2026 Zhambyl Yermagambet
"""Decode Claude Code control response lines."""

from pydantic import ValidationError

from harness.impl.claude_code.usage import live_models, probe_documents


def decode_control_line(line: str) -> live_models.ProbeResult | None:
    """Decode a matching usage response line.

    Returns:
        A probe result, or None for an unrelated line.

    """
    try:
        identity = probe_documents.ControlResponseIdentity.model_validate_json(line)
    except ValidationError:
        return None
    valid_response = (
        identity.type == "control_response"
        and identity.response is not None
        and identity.response.request_id == probe_documents.REQUEST_ID
    )
    if not valid_response:
        return None
    return _validated_control_line(line)


def _validated_control_line(line: str) -> live_models.ProbeResult:
    try:
        message = probe_documents.ControlResponseLine.model_validate_json(line)
    except ValidationError as error:
        location = _error_location(error)
        return live_models.ProbeResult(
            None,
            live_models.ProbeFailure(
                message=f"Claude usage response is incompatible at {location}",
                recoverable=False,
            ),
        )
    document = message.response.response
    if document is None:
        return live_models.ProbeResult(
            None,
            live_models.ProbeFailure(
                message="Claude returned no usage data",
                recoverable=True,
            ),
        )
    return live_models.ProbeResult(document, None)


def _error_location(error: ValidationError) -> str:
    location = error.errors()[0]["loc"]
    return ".".join(str(part) for part in location)
