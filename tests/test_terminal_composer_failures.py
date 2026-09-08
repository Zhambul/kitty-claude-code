# Copyright (c) 2026 Zhambyl Yermagambet
"""Check error reporting when a terminal draft cannot be restored."""

from unittest.mock import Mock

import pytest

from domain.ids import WindowId
from harness.services.composer import ComposerRestoreError, with_preserved_draft

SAVED_DRAFT = "saved draft"


@pytest.mark.parametrize(
    "restore_error", [ValueError("invalid draft"), OSError("terminal closed"), RuntimeError("failed")],
)
def test_restore_failure_keeps_action_error(restore_error: Exception) -> None:
    """Keep the first failure as the cause and include the restore failure."""
    composer = Mock()
    composer.read.return_value.typed_text = SAVED_DRAFT
    composer.insert.side_effect = restore_error
    action_error = KeyError("action failed")
    with pytest.raises(ComposerRestoreError, match="action failed and the draft was not restored") as raised:
        with_preserved_draft(composer, Mock(), WindowId("test-window"), Mock(side_effect=action_error))
    assert raised.value.__cause__ is action_error
    assert str(restore_error) in str(raised.value)
    assert composer.insert.call_args.args[-1] == SAVED_DRAFT


def test_action_failure_restores_draft() -> None:
    """Restore the saved draft and raise the same action error."""
    composer = Mock()
    composer.read.return_value.typed_text = SAVED_DRAFT
    action_error = KeyError("action failed")
    with pytest.raises(KeyError, match="action failed") as raised:
        with_preserved_draft(composer, Mock(), WindowId("test-window"), Mock(side_effect=action_error))
    assert raised.value is action_error
    assert composer.insert.call_args.args[-1] == SAVED_DRAFT
