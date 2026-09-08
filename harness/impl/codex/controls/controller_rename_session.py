# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control rename session."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from harness.contract import ControlHandler
from harness.impl.codex.controls import composer, controller_timeouts
from harness.impl.codex.controls.controller_results import (
    error_detail,
    has_live_window,
)
from harness.impl.codex.controls.controller_values import SESSION_NOT_LIVE_REASON
from harness.models import controls as control_models
from harness.services.composer import ComposerRestoreError, with_preserved_draft
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from domain.ids import WindowId
    from harness.impl.codex.canonical import title


class RenameSessionHandler(ControlHandler):
    """Represent rename session handler."""

    def __init__(self, titles: title.CodexThreadTitleRepository) -> None:
        """Initialize the object."""
        self.titles = titles

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a session-rename request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.RenameSession):
            msg = "rename_session handler requires RenameSession"
            raise TypeError(msg)
        if control_context.terminal_window_id is None:
            return self._rename_durable(request, control_context.session.source_reference)
        return self._rename_live(request, control_context)

    def _rename_durable(
        self, request: control_models.RenameSession, source_reference: str,
    ) -> control_models.ControlResult:
        outcome = self.titles.set_title(source_reference, request.name)
        if outcome == "unsupported":
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                "session source is not renameable",
            )
        if outcome == "unavailable":
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.INDETERMINATE,
                "native title store is unavailable",
            )
        return control_models.DurableTitleResult(
            request.request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED,
        )

    def _rename_live(
        self, request: control_models.RenameSession, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        window_id = control_context.terminal_window_id
        if not has_live_window(window_id):
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, SESSION_NOT_LIVE_REASON,
            )
        driver = TerminalDriver(control_context.terminal)
        try:
            return with_preserved_draft(
                composer.CodexComposer(),
                driver,
                window_id,
                lambda: self._submit_rename(
                    request,
                    control_context.session.source_reference,
                    driver,
                    window_id,
                ),
            )
        except ComposerRestoreError as error:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.INDETERMINATE,
                error_detail(error),
            )

    def _submit_rename(
        self,
        request: control_models.RenameSession,
        source_reference: str,
        terminal_driver: TerminalDriver,
        window_id: WindowId,
    ) -> control_models.ControlResult:
        try:
            composer.CodexComposer().submit(terminal_driver, window_id, f"/rename {request.name}")
        except composer.ComposerError as error:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.INDETERMINATE,
                error_detail(error),
            )
        return self._confirm_title(request, source_reference)

    def _confirm_title(
        self, request: control_models.RenameSession, source_reference: str,
    ) -> control_models.ControlResult:
        deadline = time.monotonic() + controller_timeouts.NATIVE_TITLE_CONFIRM_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            observed = self.titles.read_title(source_reference)
            if observed is not None and observed.text == request.name:
                return control_models.ControlResult(
                    request.request_id,
                    control_models.ControlAcknowledgement.ACKNOWLEDGED,
                )
            time.sleep(controller_timeouts.NATIVE_TITLE_CONFIRM_POLL_SECONDS)
        return control_models.ControlResult(
            request.request_id,
            control_models.ControlAcknowledgement.INDETERMINATE,
            "Codex did not confirm the title",
        )
