# Copyright (c) 2026 Zhambyl Yermagambet
"""Define control audit data and control-service ports."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from audit import documents as audit_documents
from domain.ids import RequestId, SessionId

if TYPE_CHECKING:
    from collections.abc import Callable

    from harness import contract as harness_contract
    from harness.models import controls as control_models, session as session_models


class ControlAudit(audit_documents.AuditDocument):
    """Represent control audit."""

    control: str
    request_id: RequestId
    status: str
    reason: str
    ms: int


class AutomaticSessionNaming(Protocol):
    """Represent automatic session naming."""

    def requested_name(
        self,
        session: session_models.Session,
        request_id: RequestId,
        _apply_title: Callable[[str], control_models.ControlResult],
    ) -> control_models.ControlResult:
        """Return the requested name."""
        ...


class SessionRenaming(Protocol):
    """Represent session renaming."""

    def rename(
        self,
        _harness_controller: harness_contract.HarnessController,
        rename_session: control_models.RenameSession,
        control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Rename."""
        ...


class SessionFinder(Protocol):
    """Find the session used by a control."""

    def find(self, session_id: SessionId) -> session_models.Session | None:
        """Return the session if it exists."""
        ...
