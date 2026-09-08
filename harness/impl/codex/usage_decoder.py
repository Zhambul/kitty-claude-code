# Copyright (c) 2026 Zhambyl Yermagambet
"""Decode Codex rate limit RPC responses."""

from __future__ import annotations

from pydantic import ValidationError

from harness.impl.codex import usage_rpc
from harness.impl.codex.usage_models import ProbeFailure, ProbeResult


def decode_response(line: str, response_id: int) -> ProbeResult | None:
    """Return the matching decoded response, or nothing for another response.

    Returns:
        The matching decoded response, or nothing for another response.

    """
    try:
        header = usage_rpc.RpcResponseHeader.model_validate_json(line)
    except ValidationError:
        return None
    if header.id != response_id:
        return None
    try:
        response = usage_rpc.RateLimitsRpcResponse.model_validate_json(line)
    except ValidationError as success_error:
        return _decode_error(line, success_error)
    return ProbeResult(response.result, None)


def _decode_error(line: str, success_error: ValidationError) -> ProbeResult:
    try:
        error = usage_rpc.RateLimitsRpcError.model_validate_json(line).error
    except ValidationError:
        location = _error_location(success_error)
        return ProbeResult(
            None,
            ProbeFailure(
                message=f"Codex usage response is incompatible at {location}",
                recoverable=False,
            ),
        )
    return ProbeResult(None, ProbeFailure(error.message, not _is_permanent_error(error.message)))


def _is_permanent_error(message: str) -> bool:
    markers = ("auth", "forbidden", "login", "revoked", "token expired", "token reused", "unauthorized")
    return any(marker in message.lower() for marker in markers)


def _error_location(error: ValidationError) -> str:
    location = error.errors()[0]["loc"]
    return ".".join(str(part) for part in location)
