# Copyright (c) 2026 Zhambyl Yermagambet
"""Map interpretation records to SQL values."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.records import InterpretationEventRecord, InterpretationRecord
    from repository.model.sql import SqlValues


def interpretation_record_values(interpretation_record: InterpretationRecord) -> SqlValues:
    """Return SQL values for an interpretation record.

    Returns:
        SQL values for an interpretation record.

    """
    return (
        str(interpretation_record.raw_event_id),
        interpretation_record.translator_version,
        interpretation_record.decision,
        interpretation_record.reason,
        interpretation_record.completed_at,
    )


def interpretation_event_values(interpretation_event_record: InterpretationEventRecord) -> SqlValues:
    """Return SQL values for an interpretation-event record.

    Returns:
        SQL values for an interpretation-event record.

    """
    return (
        str(interpretation_event_record.event_id),
        str(interpretation_event_record.raw_event_id),
        interpretation_event_record.event_order,
        interpretation_event_record.storage_result,
    )
