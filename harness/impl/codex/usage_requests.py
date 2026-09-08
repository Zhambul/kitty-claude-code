# Copyright (c) 2026 Zhambyl Yermagambet
"""Build JSON-RPC requests for the Codex usage service."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from harness.impl.codex.usage_rpc import InvalidUsageRequestError


class OwnedDocument(BaseModel):
    """Apply strict validation to a document that this project owns."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_by_name=True)


class RpcRequest(OwnedDocument):
    """Provide the common JSON-RPC request fields."""

    jsonrpc: Literal["2.0"] = "2.0"


class ClientInfo(OwnedDocument):
    """Identify the JSON-RPC client."""

    name: str
    version: str


class InitializeParams(OwnedDocument):
    """Provide the Codex initialization fields."""

    client_info: Annotated[ClientInfo, Field(alias="clientInfo")]


class EmptyParams(OwnedDocument):
    """Represent an empty JSON-RPC parameter document."""


class InitializeRequest(RpcRequest):
    """Build the Codex initialization request."""

    id: Literal[1] = 1
    method: Literal["initialize"] = "initialize"
    initialization_details: InitializeParams = Field(serialization_alias="params")

    def request_json(self) -> str:
        """Return the JSON-RPC request.

        Returns:
            The JSON-RPC request.

        Raises:
            InvalidUsageRequestError: If the client name is empty.

        """
        if not self.initialization_details.client_info.name:
            message = "Codex usage client name must not be empty"
            raise InvalidUsageRequestError(message)
        return self.model_dump_json(by_alias=True)


class RateLimitsRequest(RpcRequest):
    """Build the Codex rate-limit request."""

    id: Literal[2] = 2
    method: Literal["account/rateLimits/read"] = "account/rateLimits/read"
    request_options: EmptyParams = Field(serialization_alias="params")

    def request_json(self) -> str:
        """Return the JSON-RPC request.

        Returns:
            The JSON-RPC request.

        """
        return self.model_dump_json(by_alias=True)
