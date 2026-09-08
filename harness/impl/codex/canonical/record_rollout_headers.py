# Copyright (c) 2026 Zhambyl Yermagambet
"""Own rollout headers models."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, RootModel

from harness.impl.codex.canonical.record_config import OPEN_FOREIGN, ForeignMetadata
from harness.impl.codex.ids_conversation_types import CodexTurnId


class RolloutHeader(BaseModel):
    """Represent rollout header."""

    model_config = OPEN_FOREIGN
    type: str | None = None
    timestamp: str | None = None
    payload: ForeignMetadata | None = None


class RolloutInput(RootModel[Mapping[str, object]]):
    """Compatibility input for callers that already decoded a rollout line."""


class NativePayloadIdentity(BaseModel):
    """Represent native payload identity."""

    model_config = OPEN_FOREIGN
    id: str | int | None = None
    item_id: str | int | None = None
    turn_id: CodexTurnId | None = None


class RolloutObservation(BaseModel):
    """Represent rollout observation."""

    model_config = OPEN_FOREIGN
    type: str | None = None
    timestamp: str | int | float | None = None
    payload: NativePayloadIdentity | None = None


class PayloadTypeHeader(BaseModel):
    """Represent payload type header."""

    model_config = OPEN_FOREIGN
    type: str | None = None


class RolloutDocument[PayloadModel: BaseModel](BaseModel):
    """Represent rollout document."""

    model_config = OPEN_FOREIGN
    type: str
    timestamp: str | None = None
    payload: PayloadModel


class PayloadHeaderDocument(RolloutDocument[PayloadTypeHeader]):
    """Represent payload header document."""
