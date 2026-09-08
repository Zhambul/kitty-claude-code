# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Telegram Bot API request and response data."""

import dataclasses

from pydantic import BaseModel, ConfigDict

FOREIGN = ConfigDict(extra="ignore", frozen=True)


class TelegramChat(BaseModel):
    """Describe the chat in a Telegram message."""

    model_config = FOREIGN
    id: int | str


class TelegramMessage(BaseModel):
    """Describe the retraction fields in a Telegram message."""

    model_config = FOREIGN
    message_id: int
    chat: TelegramChat


class TelegramApiResponse(BaseModel):
    """Describe a Telegram Bot API response."""

    model_config = FOREIGN
    ok: bool
    description: str | None = None
    result: TelegramMessage | bool | None = None


@dataclasses.dataclass(frozen=True)
class SendMessageParams:
    """Define a send-message request body."""

    chat_id: str
    text: str


@dataclasses.dataclass(frozen=True)
class DeleteMessageParams:
    """Define a delete-message request body."""

    chat_id: int | str
    message_id: int


@dataclasses.dataclass(frozen=True, slots=True)
class Result:
    """Describe one Telegram Bot API outcome."""

    ok: bool = False
    gone: bool = False
    status: int = 0
    error: str = ""
    message_id: int | None = None
    chat: int | str | None = None


@dataclasses.dataclass(frozen=True)
class TelegramResponse:
    """Hold a decoded API body and its HTTP status."""

    body: TelegramApiResponse
    status: int


type TelegramCallParams = SendMessageParams | DeleteMessageParams
