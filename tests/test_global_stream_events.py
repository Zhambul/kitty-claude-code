# Copyright (c) 2026 Zhambyl Yermagambet
"""Check global stream wakeups and idle reads."""

import asyncio
from unittest.mock import Mock

import pytest

from api import sse
from api.sessiondata.stream_global_frames import global_frame_loop
from core.change_signal import ChangeSignal
from dashboard.services.application_updates import ApplicationUpdateState
from repository.contract.session_data import AggregateDelta, SessionDataRepository
from tests.canonical_sessiondata_api_stream_models import ApplicationSnapshots

IDLE_CHECK_SECONDS = 0.7
TEST_HEARTBEAT_SECONDS = 0.02


async def _check_writer_notices() -> None:
    signal = ChangeSignal()
    with signal.subscribe() as first, signal.subscribe() as second:
        await asyncio.to_thread(signal.publish)
        await asyncio.wait_for(
            asyncio.gather(first.wait(), second.wait()), 1,
        )
        first.clear()
        await asyncio.to_thread(signal.publish)
        await asyncio.wait_for(first.wait(), 1)
    signal.publish()


async def _check_idle_reads() -> None:
    repository = Mock(spec=SessionDataRepository)
    repository.changed_after.return_value = AggregateDelta((), (), 0)
    application = ApplicationSnapshots()
    updates = ApplicationUpdateState()
    stream = global_frame_loop(repository, 0, application, updates)
    assert "event: application" in await anext(stream)
    pending = asyncio.create_task(anext(stream))
    await asyncio.sleep(IDLE_CHECK_SECONDS)
    repository.changed_after.assert_called_once_with(0)
    assert not pending.done()
    application.enabled = False
    updates.publish()
    assert "event: application" in await asyncio.wait_for(pending, 1)
    await stream.aclose()


async def _check_idle_heartbeat() -> None:
    repository = Mock(spec=SessionDataRepository)
    repository.changed_after.return_value = AggregateDelta((), (), 0)
    stream = global_frame_loop(repository, 0, ApplicationSnapshots(), ApplicationUpdateState())
    await anext(stream)
    assert await asyncio.wait_for(anext(stream), 1) == sse.BEAT
    assert await asyncio.wait_for(anext(stream), 1) == sse.BEAT
    repository.changed_after.assert_called_once_with(0)
    await stream.aclose()


def test_writer_thread_wakes_each_reader() -> None:
    """Notify every reader, including a notice received during a read."""
    asyncio.run(_check_writer_notices())


def test_global_stream_waits_without_reads() -> None:
    """Read once at connection, then read only after a change notice."""
    asyncio.run(_check_idle_reads())


def test_idle_heartbeat_avoids_database_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the connection alive without a database poll."""
    monkeypatch.setattr(sse, "STREAM_HEARTBEAT_SECONDS", TEST_HEARTBEAT_SECONDS)
    asyncio.run(_check_idle_heartbeat())
