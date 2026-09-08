# Copyright (c) 2026 Zhambyl Yermagambet
"""Read state from Codex rollout records."""

from harness.impl.codex.canonical.records import (
    PromptRecord,
    RolloutRecord,
    TaskStartedRecord,
)


def _has_queued_turn(records: tuple[RolloutRecord | None, ...], start: int) -> bool:
    return any(
        isinstance(record, (TaskStartedRecord, PromptRecord))
        for record in records[start:]
    )
