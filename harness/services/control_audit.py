# Copyright (c) 2026 Zhambyl Yermagambet
"""Record one control request outcome."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from harness.services.control_types import ControlAudit

if TYPE_CHECKING:
    from audit.recorder import AuditRecorder
    from harness.models import controls as control_models


def audit_control(
    audit_recorder: AuditRecorder,
    request: control_models.ControlRequest,
    outcome: control_models.ControlOutcome | None,
    elapsed: float,
) -> None:
    """Record a control outcome without blocking the control request."""
    status = "raised" if outcome is None else outcome.status
    reason = "" if outcome is None else getattr(outcome, "reason", "")
    with contextlib.suppress(Exception):
        audit_recorder.state_file(
            str(request.session_id),
            "",
            "control",
            ControlAudit(
                control=getattr(request, "control_name", ""),
                request_id=request.request_id,
                status=status,
                reason=reason or "",
                ms=round(elapsed * 1000),
            ),
        )
