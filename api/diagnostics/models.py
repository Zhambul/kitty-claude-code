# Copyright (c) 2026 Zhambyl Yermagambet
"""Structured application pipeline diagnostics."""

from pydantic import BaseModel


class DiagnosticsCheckpointResponse(BaseModel):
    """Represent diagnostics checkpoint response."""

    raw_event_cursor: int
    audit_error_cursor: int
    canonical_cursor: int
    reaction_cursor: int
    pending_raw_event_count: int


class InterpretationProblemResponse(BaseModel):
    """Represent interpretation problem response."""

    raw_event_cursor: int
    source_type: str
    source_position: str
    decision: str | None
    reason: str | None
    payload: str


class AuditProblemResponse(BaseModel):
    """Represent audit problem response."""

    error_cursor: int
    session_id: str
    component: str
    action: str
    context: str


class DiagnosticsReportResponse(BaseModel):
    """Represent diagnostics report response."""

    raw_event_count: int
    verdict_count: int
    interpretation_problems: tuple[InterpretationProblemResponse, ...]
    audit_problems: tuple[AuditProblemResponse, ...]


class TerminalProcessDiagnosticResponse(BaseModel):
    """Represent terminal process diagnostic response."""

    process_id: int | None
    command: tuple[str, ...]


class TerminalWindowDiagnosticResponse(BaseModel):
    """Represent terminal window diagnostic response."""

    window_id: str
    processes: tuple[TerminalProcessDiagnosticResponse, ...]
    screen: str | None
    screen_error: str | None


class TerminalDiagnosticsResponse(BaseModel):
    """Represent terminal diagnostics response."""

    windows: tuple[TerminalWindowDiagnosticResponse, ...]
