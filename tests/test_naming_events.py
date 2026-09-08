# Copyright (c) 2026 Zhambyl Yermagambet
"""Check naming work after database change notices."""

from dataclasses import dataclass, field
from threading import Event
from unittest.mock import Mock

import pytest

from core.change_signal import ChangeSignal
from domain.naming import NamingJob, NamingJobState
from naming.jobs import NamingJobWorker
from repository.impl.sqlite.naming import SqliteNamingJobRepository
from tests.automatic_naming_session_helper import session
from tests.automatic_naming_values import SESSION_ID
from tests.worker_test_support import running_worker

INITIAL_READS = 3
TOTAL_READS = 4
IDLE_CHECK_SECONDS = 0.7


@dataclass
class _NamingDrain:
    drained: Event = field(default_factory=Event)
    calls: int = 0

    def tick(self, _cancelled: object) -> bool:
        """Finish the initial jobs, then report that no work is ready.

        Returns:
            True while an initial job remains.

        """
        self.calls += 1
        if self.calls < INITIAL_READS:
            return True
        self.drained.set()
        return False


def test_naming_drains_jobs_and_waits(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read every ready job, then stop reading until a change arrives."""
    changes = ChangeSignal()
    worker = NamingJobWorker(Mock(), Mock(), Mock(), Mock(), changes=changes)
    drain = _NamingDrain()
    monkeypatch.setattr(worker, "tick", drain.tick)
    with running_worker(worker.run, worker.stop) as thread:
        assert drain.drained.wait(1)
        drain.drained.clear()
        assert not drain.drained.wait(IDLE_CHECK_SECONDS)
        assert drain.calls == INITIAL_READS
        changes.publish()
        assert (drain.drained.wait(1), drain.calls) == (True, TOTAL_READS)
    assert not thread.is_alive()


def _naming_worker(naming_jobs: SqliteNamingJobRepository, completed: Event) -> NamingJobWorker:
    changes = ChangeSignal()
    naming_jobs.database.changes = changes
    audit = Mock()
    audit.state_file.side_effect = lambda *_args: completed.set()
    namer = Mock()
    namer.initial_name.return_value = "Stored title"
    sessions = Mock()
    sessions.find.return_value = session()
    return NamingJobWorker(naming_jobs, sessions, namer, audit, changes=changes)


def test_committed_naming_job_wakes_worker(naming_jobs: SqliteNamingJobRepository) -> None:
    """Complete a stored job after its commit notice, without a timer."""
    completed = Event()
    worker = _naming_worker(naming_jobs, completed)
    with running_worker(worker.run, worker.stop) as thread:
        job = NamingJob("event-name", SESSION_ID, "Name this session")
        assert naming_jobs.enqueue(job)
        assert completed.wait(1)
        stored = naming_jobs.find(job.key)
        assert stored is not None
        assert (stored.state, stored.title) == (NamingJobState.COMPLETED, "Stored title")
    assert not thread.is_alive()
