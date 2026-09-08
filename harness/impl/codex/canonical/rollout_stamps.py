# Copyright (c) 2026 Zhambyl Yermagambet
"""Attach rollout timestamps to typed records."""

from __future__ import annotations

import dataclasses

from harness.impl.codex.canonical import record_task_records, record_terminal_records, record_tool_records


def stamp(
    rec: record_terminal_records.RolloutRecord | None, timestamp: str | None,
) -> record_terminal_records.RolloutRecord | None:
    """Return a record with its source timestamp when that record keeps one.

    Returns:
        A record with its source timestamp when that record keeps one.

    """
    if rec is None:
        return rec
    if isinstance(rec, record_task_records.TaskStartedRecord):
        return dataclasses.replace(rec, ts=timestamp)
    if isinstance(rec, record_task_records.TaskCompleteRecord):
        return dataclasses.replace(rec, ts=timestamp)
    return stamp_execution_record(rec, timestamp)


def stamp_execution_record(
    rec: record_terminal_records.RolloutRecord,
    timestamp: str | None,
) -> record_terminal_records.RolloutRecord:
    """Attach a timestamp to records that describe one command or message.

    Returns:
        A copy with the supplied timestamp, or the unchanged record for other types.

    """
    if isinstance(rec, record_tool_records.ExecRecord):
        return dataclasses.replace(rec, ts=timestamp)
    if isinstance(rec, record_tool_records.ExecResultRecord):
        return dataclasses.replace(rec, ts=timestamp)
    if isinstance(rec, record_task_records.MessageRecord):
        return dataclasses.replace(rec, ts=timestamp)
    return rec
