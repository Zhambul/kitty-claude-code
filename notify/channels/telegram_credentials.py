# Copyright (c) 2026 Zhambyl Yermagambet
"""Read Telegram configuration and credentials."""

import os
import pathlib

DEFAULT_CREDENTIAL_DIRECTORY = "~/.config/telegram"
BOT_CREDENTIAL_FILE = "bot-token"
CHAT_NAME = "chat-id"
DEFAULT_API_BASE = "https://api.telegram.org"


def api_base() -> str:
    """Return the configured Telegram API base.

    Returns:
        The Telegram API base.

    """
    return (os.environ.get("BAQYLAU_DASHBOARD_TELEGRAM_API") or DEFAULT_API_BASE).rstrip("/")


def credential_directory() -> str:
    """Return the directory that contains both credential files.

    Returns:
        The credential directory.

    """
    configured_directory = os.environ.get("BAQYLAU_DASHBOARD_TELEGRAM_DIR")
    return str(pathlib.Path(configured_directory or DEFAULT_CREDENTIAL_DIRECTORY).expanduser())


def token() -> str:
    """Return the Telegram bot token.

    Returns:
        The bot token, or an empty string.

    """
    return _credential("BAQYLAU_DASHBOARD_TELEGRAM_TOKEN", BOT_CREDENTIAL_FILE)


def chat_id() -> str:
    """Return the Telegram chat ID.

    Returns:
        The chat ID, or an empty string.

    """
    return _credential("BAQYLAU_DASHBOARD_TELEGRAM_CHAT", CHAT_NAME)


def enabled() -> bool:
    """Return true when both Telegram credentials are available.

    Returns:
        True when the Telegram channel is configured.

    """
    return bool(token() and chat_id())


def _credential(environment_name: str, credential_name: str) -> str:
    environment_value = os.environ.get(environment_name)
    if environment_value:
        return environment_value.strip()
    credential_path = pathlib.Path(credential_directory()) / credential_name
    try:
        return credential_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return ""
