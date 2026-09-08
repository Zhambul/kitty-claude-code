# Copyright (c) 2026 Zhambyl Yermagambet
"""Validate JSON-RPC envelopes from the Codex usage service."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from harness.impl.codex.usage_rate_limit_documents import AccountRateLimitsResponse

FOREIGN_DOCUMENT = ConfigDict(extra="ignore", frozen=True, validate_by_name=True)


class InvalidUsageRequestError(ValueError):
    """Report an invalid Codex usage request."""


class RpcResponseHeader(BaseModel):
    """Read the response identifier before full validation."""

    model_config = FOREIGN_DOCUMENT
    id: int | None = None


class RateLimitsRpcResponse(BaseModel):
    """Represent a successful rate-limit response."""

    model_config = FOREIGN_DOCUMENT
    jsonrpc: Literal["2.0"] = "2.0"
    id: Literal[2]
    result: AccountRateLimitsResponse


class RpcErrorBody(BaseModel):
    """Represent a JSON-RPC error body."""

    model_config = FOREIGN_DOCUMENT
    code: int
    message: str


class RateLimitsRpcError(BaseModel):
    """Represent a failed rate-limit response."""

    model_config = FOREIGN_DOCUMENT
    jsonrpc: Literal["2.0"] = "2.0"
    id: Literal[2]
    error: RpcErrorBody
