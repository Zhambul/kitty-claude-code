# Copyright (c) 2026 Zhambyl Yermagambet
"""Read the Deepgram key and mint short-lived browser grants."""

import os
import pathlib

import httpx
from pydantic import BaseModel, ConfigDict

DEFAULT_KEY_FILE = "~/.config/deepgram/api-key"
DEEPGRAM_GRANT_URL = "https://api.deepgram.com/v1/auth/grant"
GRANT_TIMEOUT_SECONDS = 5.0


class GrantRequest(BaseModel):
    """Declare the requested Deepgram grant lifetime."""

    ttl_seconds: int | None = None


class GrantResponse(BaseModel):
    """Declare the Deepgram grant response."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    access_token: str
    expires_in: int | None = None


def key_file() -> str:
    """Return the expanded Deepgram key path.

    Returns:
        The key file path.

    """
    return str(
        pathlib.Path(
            os.environ.get("BAQYLAU_DICTATION_KEY_FILE") or DEFAULT_KEY_FILE,
        ).expanduser(),
    )


def available() -> bool:
    """Return true when the key file is readable and not empty.

    Returns:
        True when dictation credentials are available.

    """
    try:
        return bool(read_file(key_file()))
    except (OSError, UnicodeError):
        return False


def read_file(path: str) -> str:
    """Read and trim one UTF-8 text file.

    Returns:
        The trimmed file content.

    """
    return pathlib.Path(path).read_text(encoding="utf-8").strip()


def grant(lifetime_seconds: int | None = None) -> GrantResponse:
    """Mint a short-lived browser token.

    Returns:
        The Deepgram grant response.

    """
    key = read_file(key_file())
    url = os.environ.get("BAQYLAU_DICTATION_GRANT_URL") or DEEPGRAM_GRANT_URL
    body = GrantRequest(ttl_seconds=lifetime_seconds).model_dump_json(exclude_none=True).encode()
    request_headers = {
        "Authorization": f"Token {key}",
        "Content-Type": "application/json",
    }
    response = httpx.post(
        url,
        content=body,
        headers=request_headers,
        timeout=GRANT_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return GrantResponse.model_validate_json(response.content)
