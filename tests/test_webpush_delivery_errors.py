# Copyright (c) 2026 Zhambyl Yermagambet
"""Keep HTTP delivery errors readable when the response body is invalid."""

from http import HTTPStatus, client as http_client
from io import BytesIO
from unittest.mock import Mock
from urllib.error import HTTPError

import pytest

from notify.channels import webpush_delivery


@pytest.mark.parametrize(("body", "gone"), [
    (b'{"reason":"VapidPkHashMismatch"}', True),
    (b'{"reason":"other"}', False),
    (b"invalid json", False),
])
def test_http_error_keeps_status(body: bytes, monkeypatch: pytest.MonkeyPatch, *, gone: bool) -> None:
    """Keep the status and detect a rejected signing key."""
    error = HTTPError(
        "https://push.example.invalid", HTTPStatus.BAD_REQUEST, "bad request", http_client.HTTPMessage(), BytesIO(body),
    )
    monkeypatch.setattr(webpush_delivery, "enabled", lambda: True)
    monkeypatch.setattr(webpush_delivery, "_send_delivery", Mock(side_effect=error))
    result = webpush_delivery.deliver(Mock(), Mock(), None)
    assert (result.ok, result.status, result.gone) == (False, HTTPStatus.BAD_REQUEST, gone)
    assert result.error


@pytest.mark.parametrize("read_error", [OSError("closed"), http_client.IncompleteRead(b"partial")])
def test_unreadable_error_body_keeps_status(read_error: Exception, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the HTTP failure when its body cannot be read."""
    error = HTTPError("https://push.example.invalid", HTTPStatus.GONE, "gone", http_client.HTTPMessage(), None)
    monkeypatch.setattr(error, "read", Mock(side_effect=read_error))
    monkeypatch.setattr(webpush_delivery, "enabled", lambda: True)
    monkeypatch.setattr(webpush_delivery, "_send_delivery", Mock(side_effect=error))
    result = webpush_delivery.deliver(Mock(), Mock(), None)
    assert (result.ok, result.status, result.gone) == (False, HTTPStatus.GONE, True)
    assert result.error == str(error)
