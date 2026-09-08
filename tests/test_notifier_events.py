# Copyright (c) 2026 Zhambyl Yermagambet
"""Check notification reads after changes and known deadlines."""

from dataclasses import dataclass, field
from threading import Event
from time import monotonic
from unittest.mock import Mock

import pytest

from core.change_signal import ChangeSignal
from domain.actor_state import ActorStatus
from domain.ids import SessionId
from notify.notifier import Notifier, PendingNotification
from tests.worker_test_support import running_worker

EXPECTED_READS = 2
IDLE_CHECK_SECONDS = 1.1
TEST_DEADLINE_SECONDS = 0.03
SCAN_METHOD = "scan"


@dataclass
class _ChangeScan:
    changes: ChangeSignal
    scanned: Event = field(default_factory=Event)
    calls: int = 0

    def __call__(self) -> None:
        """Publish a change during the first scan and record the next scan."""
        self.calls += 1
        if self.calls == 1:
            self.changes.publish()
        else:
            self.scanned.set()


@dataclass
class _DeadlineScan:
    notifier: Notifier
    scanned: Event = field(default_factory=Event)
    calls: int = 0

    def __call__(self) -> None:
        """Set a deadline during the first scan and record the next scan."""
        self.calls += 1
        if self.calls == 1:
            session_id = SessionId("deadline")
            self.notifier.pending[session_id] = PendingNotification(
                session_id, ActorStatus.AWAITING_RESPONSE, "done", "test", "finished",
                monotonic() + TEST_DEADLINE_SECONDS,
            )
        else:
            self.notifier.pending.clear()
            self.scanned.set()


def test_notification_worker_waits_for_changes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not scan each second, and release an idle worker at shutdown."""
    changes = ChangeSignal()
    notifier = Notifier(Mock(changes=changes))
    scanned = Event()
    scan = Mock(side_effect=scanned.set)
    monkeypatch.setattr(notifier, SCAN_METHOD, scan)
    with running_worker(notifier.run, notifier.stop) as worker:
        assert scanned.wait(1)
        scanned.clear()
        assert not scanned.wait(IDLE_CHECK_SECONDS)
        scan.assert_called_once()
        changes.publish()
        assert scanned.wait(1)
        assert scan.call_count == EXPECTED_READS
    assert not worker.is_alive()


def test_notification_change_during_read_is_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read again when a change arrives during a scan."""
    changes = ChangeSignal()
    notifier = Notifier(Mock(changes=changes))
    scan = _ChangeScan(changes)
    monkeypatch.setattr(notifier, SCAN_METHOD, scan)
    with running_worker(notifier.run, notifier.stop) as worker:
        assert scan.scanned.wait(1)
        assert scan.calls == EXPECTED_READS
    assert not worker.is_alive()


def test_notification_deadline_wakes_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deliver due work even when no new session data arrives."""
    notifier = Notifier(Mock(changes=ChangeSignal()))
    scan = _DeadlineScan(notifier)
    monkeypatch.setattr(notifier, SCAN_METHOD, scan)
    with running_worker(notifier.run, notifier.stop) as worker:
        assert scan.scanned.wait(1)
        assert scan.calls == EXPECTED_READS
    assert not worker.is_alive()


def test_thread_subscription_removed_on_close() -> None:
    """Do not wake a worker after it leaves the subscription."""
    changes = ChangeSignal()
    with changes.subscribe_thread() as changed:
        changes.publish()
        assert changed.is_set()
        changed.clear()
    changes.publish()
    assert not changed.is_set()


def test_notification_worker_retries_failed_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    """Record a failed scan and retry before the worker stops."""
    dependencies = Mock(changes=ChangeSignal())
    notifier = Notifier(dependencies)
    scan = Mock(side_effect=(RuntimeError("delivery failed"), None))
    monkeypatch.setattr(notifier, SCAN_METHOD, scan)
    monkeypatch.setattr("notify.notifier.NOTIFICATION_RETRY_SECONDS", 0)
    stop = Mock()
    stop.is_set.side_effect = (False, False, False, True)

    notifier.run(stop)

    assert scan.call_count == EXPECTED_READS
    dependencies.audit_recorder.error.assert_called_once_with("", "dashboard notifier")
