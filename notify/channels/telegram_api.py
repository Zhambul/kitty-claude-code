# Copyright (c) 2026 Zhambyl Yermagambet
"""Call the Telegram Bot API."""

import dataclasses
from http import HTTPStatus

import httpx
from pydantic import ValidationError

from notify.channels import telegram_credentials, telegram_models

REQUEST_TIMEOUT_SECONDS = 10.0


def send_message(text: str) -> telegram_models.Result:
    """Send a message to the configured chat.

    Returns:
        The Telegram result.

    """
    chat = telegram_credentials.chat_id()
    if not chat:
        return telegram_models.Result(error="no chat")
    response, error = _call(
        "sendMessage",
        telegram_models.SendMessageParams(chat_id=chat, text=text),
    )
    if error is not None or not isinstance(response, telegram_models.TelegramMessage):
        return error or telegram_models.Result(error="empty result")
    return telegram_models.Result(
        ok=True,
        status=HTTPStatus.OK,
        message_id=response.message_id,
        chat=response.chat.id,
    )


def delete_message(
    chat: int | str | None,
    message_id: int | None,
) -> telegram_models.Result:
    """Delete a message that this bot sent.

    Returns:
        The Telegram result.

    """
    if not (chat and message_id):
        return telegram_models.Result(error="no handle")
    _response, error = _call(
        "deleteMessage",
        telegram_models.DeleteMessageParams(chat_id=chat, message_id=message_id),
    )
    if error is not None:
        return error
    return telegram_models.Result(
        ok=True,
        status=HTTPStatus.OK,
        message_id=message_id,
        chat=chat,
    )


def _call(
    method: str,
    call_parameters: telegram_models.TelegramCallParams,
) -> tuple[telegram_models.TelegramMessage | bool | None, telegram_models.Result | None]:
    bot_token = telegram_credentials.token()
    if not bot_token:
        return None, telegram_models.Result(error="no token")
    response = _request_response(method, call_parameters, bot_token)
    if isinstance(response, telegram_models.Result):
        return None, response
    if not response.body.ok:
        return None, _failed_response(response)
    return response.body.result, None


def _request_response(
    method: str,
    call_parameters: telegram_models.TelegramCallParams,
    bot_token: str,
) -> telegram_models.TelegramResponse | telegram_models.Result:
    api_url = f"{telegram_credentials.api_base()}/bot{bot_token}/{method}"
    try:
        response = httpx.post(
            api_url,
            data=dataclasses.asdict(call_parameters),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as error:
        return telegram_models.Result(error=str(error))
    try:
        return telegram_models.TelegramResponse(
            telegram_models.TelegramApiResponse.model_validate_json(response.content or b"{}"),
            response.status_code,
        )
    except (ValueError, ValidationError) as error:
        return telegram_models.Result(status=response.status_code, error=str(error))


def _failed_response(
    response: telegram_models.TelegramResponse,
) -> telegram_models.Result:
    description = response.body.description or ""
    gone = response.status == HTTPStatus.BAD_REQUEST and "not found" in description.lower()
    return telegram_models.Result(
        gone=gone,
        status=response.status,
        error=description,
    )
