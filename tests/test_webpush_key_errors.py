# Copyright (c) 2026 Zhambyl Yermagambet
"""Check key recovery without writing real Web Push keys."""

from unittest.mock import Mock

import pytest
from cryptography.exceptions import UnsupportedAlgorithm

from domain.preferences import PushSigningKeypair
from notify.channels import webpush_keys


@pytest.fixture
def key_repository(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Provide a stored key and replace key generation and audit writes.

    Returns:
        The key repository probe.

    """
    repository = Mock()
    repository.keypair.return_value = PushSigningKeypair("private", "stored-public")
    monkeypatch.setattr(webpush_keys, "enabled", lambda: True)
    monkeypatch.setattr(webpush_keys, "create_keypair_material", Mock(return_value=(Mock(), b"public", b"private")))
    monkeypatch.setattr("notify.channels.webpush_keys.audit_record.error", Mock())
    return repository


@pytest.mark.parametrize("error", [
    TypeError("wrong key type"), ValueError("bad PEM"), UnsupportedAlgorithm("unsupported"),
])
def test_invalid_key_is_replaced(error: Exception, monkeypatch: pytest.MonkeyPatch, key_repository: Mock) -> None:
    """Replace a key only after a known key-reading error."""
    monkeypatch.setattr(webpush_keys, "load_private_key", Mock(side_effect=error))
    assert webpush_keys.public_key(key_repository) == "cHVibGlj"
    key_repository.save_keypair.assert_called_once_with(PushSigningKeypair("private", "cHVibGlj"))


def test_unexpected_error_keeps_stored_key(monkeypatch: pytest.MonkeyPatch, key_repository: Mock) -> None:
    """Do not rotate a stored key after an unrelated implementation error."""
    monkeypatch.setattr(webpush_keys, "load_private_key", Mock(side_effect=RuntimeError("unexpected")))
    with pytest.raises(RuntimeError, match="unexpected"):
        webpush_keys.public_key(key_repository)
    key_repository.save_keypair.assert_not_called()
