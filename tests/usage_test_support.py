# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide usage service test fixtures."""

from threading import Event

from harness.models.usage import UsageRow

READS_BEFORE_STOP = 2


class RecordingUsageSource:
    """Return configured usage rows and count reads."""

    def __init__(self, rows: tuple[UsageRow, ...] = ()) -> None:
        """Initialize the source."""
        self.rows = rows
        self.calls = 0

    def read(self) -> tuple[UsageRow, ...]:
        """Read the configured usage rows.

        Returns:
            The configured rows.

        """
        self.calls += 1
        return self.rows


class UsageRetryStop(Event):
    """Stop a usage loop after its successful retry."""

    def __init__(self, source: RecordingUsageSource) -> None:
        """Initialize the stop signal."""
        super().__init__()
        self.source = source
        self.delays: list[float | None] = []
        self.stopped = False

    def is_set(self) -> bool:
        """Check if the loop must stop.

        Returns:
            True when the retry read is complete.

        """
        return self.stopped

    def wait(self, timeout: float | None = None) -> bool:
        """Record one delay and update the stop state.

        Returns:
            True when the retry read is complete.

        """
        self.delays.append(timeout)
        self.stopped = self.source.calls >= READS_BEFORE_STOP
        return self.stopped


class FirstReadFailureUsageSource(RecordingUsageSource):
    """Fail the first usage read and then return configured rows."""

    def read(self) -> tuple[UsageRow, ...]:
        """Read rows after one transient failure.

        Returns:
            The configured rows after the first call.

        Raises:
            RuntimeError: On the first call.

        """
        self.calls += 1
        if self.calls == 1:
            message = "transient probe failure"
            raise RuntimeError(message)
        return self.rows
