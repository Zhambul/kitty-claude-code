# Copyright (c) 2026 Zhambyl Yermagambet
"""Load notification channels without imports from other application paths."""

import subprocess  # noqa: S404 -- Run a fixed import-check script in a fresh Python process.
import sys

IMPORT_CHECK_TIMEOUT_SECONDS = 15


def test_fresh_notifier_can_send_a_second_alert() -> None:
    """Use a fake sender after a fresh import, without a network request."""
    script = """
import sys
from unittest.mock import Mock
from dashboard import config
from domain.actor_state import ActorStatus
from domain.ids import SessionId
from notify import notifier

telegram = sys.modules['notify.channels.telegram']
sender = Mock(return_value=None)
telegram.send_alert = sender
config.NOTIFY_TELEGRAM = True
dependencies = Mock()
dependencies.presence.web_viewing.return_value = False
service = notifier.Notifier(dependencies)
pending = notifier.PendingNotification(
    SessionId('test-session'), ActorStatus.AWAITING_RESPONSE,
    'done', 'test', 'finished', 0, pushed=True,
)
service.pending[pending.session_id] = pending
service.escalate(pending)
sender.assert_called_once_with(pending.payload(), 'escalation')
assert not service.pending
assert 'notify.channels.webpush' in sys.modules
assert 'notify.channels.retraction' in sys.modules
"""
    result = subprocess.run(  # noqa: S603 -- The current interpreter runs fixed test code, without a shell.
        (sys.executable, "-c", script), capture_output=True, text=True, check=False,
        timeout=IMPORT_CHECK_TIMEOUT_SECONDS,
    )
    assert result.returncode == 0, result.stderr
