# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared fakes and builders for inference tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from inference import default as inference_default, options as inference_options
from terminal.models import tab_results, tabs, values, viewport
from tests.fake_terminal import FakeTerminal, window

if TYPE_CHECKING:
    from audit.documents import AuditContent
    from audit.recorder import AuditRecorder
    from harness.models.usage import UsageRow


class Usage:
    """Represent test usage rows."""

    def __init__(self, rows: tuple[UsageRow, ...] = ()) -> None:
        """Store fixed usage rows."""
        self.rows = rows

    def usage_rows(self) -> tuple[UsageRow, ...]:
        """Read the fixed usage rows.

        Returns:
            The configured rows without collecting provider data.

        """
        return self.rows


class Audit:
    """Record test audit errors."""

    def __init__(self) -> None:
        """Create an empty audit error record."""
        self.errors: list[tuple[str, str, AuditContent]] = []

    def error(self, session_or_log: str = "", func: str = "", context: AuditContent = None) -> None:
        """Record an audit error and its context."""
        self.errors.append((session_or_log, func, context))


class InferenceTerminal(FakeTerminal):
    """Represent an inference terminal with scripted output."""

    def __init__(self, outputs: tuple[str, ...], *, stays_open: bool = False) -> None:
        """Store scripted outputs and the requested window visibility."""
        super().__init__()
        self.outputs = list(outputs)
        self.stays_open = stays_open
        self.output_by_window: dict[str, str] = {}
        self.next_id = 0

    def open_tab(self, request: tabs.TabOpenRequest) -> tab_results.TabOpenResponse:
        """Record a tab request and assign the next scripted output.

        Returns:
            A successful response with a new test window identifier.

        """
        self.opened_tabs.append(request)
        self.next_id += 1
        window_id = f"model-{self.next_id}"
        self.output_by_window[window_id] = self.outputs.pop(0)
        return tab_results.TabOpenResponse(succeeded=True, window_id=values.WindowId(window_id))

    def windows(self) -> tuple[values.WindowInfo, ...]:
        """Read the visible test window.

        Returns:
            The latest open window if configured to stay open, or no windows.

        """
        if not self.stays_open or not self.output_by_window:
            return ()
        window_id = next(reversed(self.output_by_window))
        return (window(window_id),)

    def read_screen(
        self,
        request: viewport.ScreenReadRequest,
    ) -> viewport.ScreenReadResponse:
        """Read scripted output for the requested window.

        Returns:
            A successful response with that window's text.

        """
        text = self.output_by_window[str(request.window_id)]
        return viewport.ScreenReadResponse(succeeded=True, text=text)

    def close_tab(self, request: tabs.TabCloseRequest) -> tab_results.TabCloseResponse:
        """Record a close request and remove its scripted output.

        Returns:
            A successful close response.

        """
        self.closed_tabs.append(request.window_id)
        self.output_by_window.pop(str(request.window_id), None)
        return tab_results.TabCloseResponse(succeeded=True)


def factory(
    terminal: InferenceTerminal,
    usage: Usage | None = None,
    audit: Audit | None = None,
    *,
    timeout: float = 1,
) -> inference_default.DefaultModelFactory:
    """Return a default model factory for tests.

    Returns:
        A default model factory for tests.

    """
    return inference_default.DefaultModelFactory(
        terminal.plugin(),
        usage or Usage(),
        cast("AuditRecorder", audit or Audit()),
        inference_options.DefaultModelOptions(
            timeout_seconds=timeout,
            executable_available=lambda _executable_name: True,
        ),
    )
