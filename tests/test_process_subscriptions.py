# Copyright (c) 2026 Zhambyl Yermagambet
"""Check native process subscriptions without opening process descriptors."""

import select
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from core.process_subscriptions import ProcessSubscriptions

PROCESS_ID = 123
PROCESS_DESCRIPTOR = 42
ADD_AND_REMOVE_CALLS = 2


@pytest.fixture
def linux_process_api(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Replace the Linux descriptor calls.

    Returns:
        The process descriptor probe.

    """
    process_api = Mock()
    process_api.pidfd_open.return_value = PROCESS_DESCRIPTOR
    monkeypatch.setattr("core.process_subscriptions.os", process_api)
    monkeypatch.setattr("core.process_subscriptions.sys", SimpleNamespace(platform="linux"))
    return process_api


@pytest.mark.skipif(not hasattr(select, "kqueue"), reason="Requires macOS kqueue")
def test_kqueue_keeps_existing_subscription() -> None:
    """Do not register an unchanged process twice or close shared resources."""
    selector = Mock()
    queue = Mock()
    subscriptions = ProcessSubscriptions(selector, queue, Mock())
    subscriptions.update({PROCESS_ID})
    subscriptions.update({PROCESS_ID})
    queue.control.assert_called_once()
    subscriptions.close()
    assert queue.control.call_count == ADD_AND_REMOVE_CALLS
    queue.close.assert_not_called()
    selector.close.assert_not_called()


@pytest.mark.skipif(not hasattr(select, "kqueue"), reason="Requires macOS kqueue")
def test_kqueue_reports_exited_process() -> None:
    """Publish a notice if the process exits before registration."""
    queue = Mock()
    queue.control.side_effect = ProcessLookupError
    changed = Mock()
    subscriptions = ProcessSubscriptions(Mock(), queue, changed)
    subscriptions.update({PROCESS_ID})
    changed.assert_called_once_with()
    subscriptions.close()
    assert queue.control.call_count == ADD_AND_REMOVE_CALLS


def test_linux_closes_only_owned_descriptors(linux_process_api: Mock) -> None:
    """Remove process descriptors but leave the shared selector open."""
    selector = Mock()
    subscriptions = ProcessSubscriptions(selector, None, Mock())
    subscriptions.update({PROCESS_ID})
    subscriptions.update({PROCESS_ID})
    linux_process_api.pidfd_open.assert_called_once_with(PROCESS_ID)
    subscriptions.close()
    selector.unregister.assert_called_once_with(PROCESS_DESCRIPTOR)
    linux_process_api.close.assert_called_once_with(PROCESS_DESCRIPTOR)
    selector.close.assert_not_called()


def test_linux_closes_after_exit_notice(linux_process_api: Mock) -> None:
    """Close a descriptor even if the event wait already removed its watch."""
    selector = Mock()
    selector.unregister.side_effect = KeyError
    subscriptions = ProcessSubscriptions(selector, None, Mock())
    subscriptions.update({PROCESS_ID})
    subscriptions.update(set())
    subscriptions.close()
    linux_process_api.close.assert_called_once_with(PROCESS_DESCRIPTOR)
