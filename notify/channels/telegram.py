# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the Telegram notification channel."""

from notify.channels import (
    telegram_alert,
    telegram_api,
    telegram_credentials,
    telegram_models,
)

TelegramChat = telegram_models.TelegramChat
TelegramMessage = telegram_models.TelegramMessage
TelegramApiResponse = telegram_models.TelegramApiResponse
SendMessageParams = telegram_models.SendMessageParams
DeleteMessageParams = telegram_models.DeleteMessageParams
TelegramCallParams = telegram_models.TelegramCallParams
Result = telegram_models.Result
TelegramHandle = telegram_alert.TelegramHandle

token = telegram_credentials.token
chat_id = telegram_credentials.chat_id
enabled = telegram_credentials.enabled
send_message = telegram_api.send_message
delete_message = telegram_api.delete_message
send_alert = telegram_alert.send_alert
retract_alert = telegram_alert.retract_alert
