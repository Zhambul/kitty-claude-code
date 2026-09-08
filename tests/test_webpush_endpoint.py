# Copyright (c) 2026 Zhambyl Yermagambet
"""Check the Web Push endpoint before network delivery."""

from http import HTTPStatus
from unittest.mock import MagicMock, Mock

import pytest

from notify.channels import webpush_delivery


@pytest.mark.parametrize("endpoint", [
    "http://push.invalid", "file:///tmp/push", "ftp://push.invalid", "data:text/plain,x",
])
def test_push_rejects_non_https(endpoint: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject other URL schemes without opening a network connection."""
    network = Mock()
    monkeypatch.setattr(webpush_delivery, "enabled", lambda: True)
    monkeypatch.setattr("notify.channels.webpush_delivery.urllib_request.urlopen", network)
    result = webpush_delivery.deliver(
        {"endpoint": endpoint, "device": "test", "label": None, "keys": {"p256dh": "", "auth": ""}},
        Mock(),
        None,
    )
    assert not result.ok
    assert result.error == "push endpoint must use https"
    network.assert_not_called()


def test_push_accepts_https(monkeypatch: pytest.MonkeyPatch) -> None:
    """Send the encrypted body to an HTTPS endpoint."""
    response = MagicMock()
    response.__enter__.return_value.status = HTTPStatus.ACCEPTED
    network = Mock(return_value=response)
    monkeypatch.setattr(webpush_delivery, "enabled", lambda: True)
    monkeypatch.setattr("notify.channels.webpush_delivery.urllib_request.urlopen", network)
    monkeypatch.setattr(
        "notify.channels.webpush_delivery_crypto.content_and_authorization",
        Mock(return_value=(b"encrypted", "test-auth")),
    )
    result = webpush_delivery.deliver(
        {"endpoint": "https://push.invalid", "device": "test", "label": None, "keys": {"p256dh": "", "auth": ""}},
        Mock(),
        None,
    )
    assert result.ok
    assert result.status == HTTPStatus.ACCEPTED
    network.assert_called_once()
    request = network.call_args.args[0]
    assert request.full_url == "https://push.invalid"
    assert request.data == b"encrypted"
