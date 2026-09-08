# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the test audit failures module."""

from audit.documents import AuditContent
from audit.failures import CoalescingFailureRecorder, FailureContext
from audit.recorder import AuditRecorder
from domain.ids import SessionId


class RecordingAudit(AuditRecorder):
    """Represent recording audit."""

    def __init__(self) -> None:
        """Initialize the object."""
        self.errors: list[tuple[str, str, AuditContent]] = []

    def error(self, session_or_log: str = "", func: str = "", context: AuditContent = None) -> None:
        """Process error."""
        self.errors.append((session_or_log, func, context))


def _raise_value_error(message: str) -> None:
    raise ValueError(message)


def _zero_time() -> float:
    return 0


def _record_source_failure(
    failures: CoalescingFailureRecorder,
    message: str,
) -> None:
    try:
        _raise_value_error(message)
    except ValueError:
        failures.record(
            "source read",
            FailureContext(session_id=SessionId("session-one")),
        )


def test_repeated_loop_failure_is_counted() -> None:
    """Verify repeated loop failure is counted instead of written each cycle."""
    now: list[float] = [0]
    audit = RecordingAudit()
    failures = CoalescingFailureRecorder(
        audit,
        "interpreter",
        clock=lambda: now[0],
        repeat_report_seconds=60.0,
    )
    failure_message = "foreign record changed"
    expected_report_count = 2

    _record_source_failure(failures, failure_message)
    _record_source_failure(failures, failure_message)
    _record_source_failure(failures, failure_message)
    assert len(audit.errors) == 1

    now[0] = 60.0
    _record_source_failure(failures, failure_message)

    assert len(audit.errors) == expected_report_count
    assert audit.errors[-1][2] == FailureContext(
        session_id=SessionId("session-one"),
        suppressed_repeats=expected_report_count,
    )


def test_changed_failure_shape_is_recorded() -> None:
    """Verify changed failure shape is recorded without a delay."""
    audit = RecordingAudit()
    failures = CoalescingFailureRecorder(audit, "interpreter", clock=_zero_time)
    expected_report_count = 2

    for message in ("first drift", "second drift"):
        try:
            _raise_value_error(message)
        except ValueError:
            failures.record(
                "source read",
                FailureContext(session_id=SessionId("session-one")),
            )

    assert len(audit.errors) == expected_report_count
