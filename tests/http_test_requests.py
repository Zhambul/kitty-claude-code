# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http test requests."""

from __future__ import annotations

from unittest.mock import Mock

from tests import (
    http_contract_dependencies as contract_dependencies,
    http_library_dependencies as library_dependencies,
    http_runtime_dependencies as runtime_dependencies,
    http_test_audit_models,
    http_test_control_models,
    http_test_pane_models,
    http_test_response_helpers,
    http_value_dependencies as standard_dependencies,
)

SESSION_ID_TEXT = "session-one"
LOOPBACK_ADDRESS = "127.0.0.1"
FIRST_REQUEST_ID = "request-one"
SESSION_ID = runtime_dependencies.domain_ids.SessionId(SESSION_ID_TEXT)
SOCKET_RESPONSE_READ_BYTES = 4096
type ControlAuditRow = tuple[str, str, contract_dependencies.control_services.ControlAudit]
type AuditedControlResult = tuple[list[ControlAuditRow], Exception | None]
type MethodAuditRow = tuple[str, contract_dependencies.control_services.ControlAudit]


def stop_server(server: http_test_pane_models.RunningDaemon, thread: standard_dependencies.threading.Thread) -> None:
    """Stop a test server and wait for its thread."""
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


class HttpResponse(library_dependencies.typing.NamedTuple):
    """Represent one response with its status and decoded body."""

    status: int
    body: http_test_response_helpers.JsonBody


class HttpGetResponse(library_dependencies.typing.NamedTuple):
    """Represent one GET response with its content type."""

    status: int
    content_type: str | None
    body: http_test_response_helpers.JsonBody


class HttpHeadersResponse(library_dependencies.typing.NamedTuple):
    """Represent one response whose headers are under test."""

    status: int
    headers: library_dependencies.http.client.HTTPMessage
    body: http_test_response_helpers.JsonBody


def post_without_a_declared_length(server: http_test_pane_models.RunningDaemon, path: str, body: bytes) -> int:
    """Send a chunked POST directly through a socket.

    Returns:
        The HTTP response status code.

    """
    head = (
        f"POST {path} HTTP/1.1\r\nHost: 127.0.0.1\r\n"
        "Content-Type: application/json\r\nX-Baqylau: 1\r\nTransfer-Encoding: chunked\r\n\r\n"
    ).encode()
    with standard_dependencies.socket.create_connection((LOOPBACK_ADDRESS, server.server_port), timeout=2) as raw:
        raw.sendall(head + b"%x\r\n%s\r\n0\r\n\r\n" % (len(body), body))
        return int(raw.recv(SOCKET_RESPONSE_READ_BYTES).split(b" ")[1])


def audited_control(
    monkeypatch: library_dependencies.pytest.MonkeyPatch,
    outcome: runtime_dependencies.control_models.ControlResult | Exception,
) -> AuditedControlResult:
    """Run a model selection with a fixed outcome and record its audit.

    Returns:
        The audit rows and any exception raised by the control call.

    """
    rows: list[ControlAuditRow] = []
    service = contract_dependencies.control_services.HarnessControlService(Mock())
    service.audit = http_test_audit_models.ControlAuditRecorder(rows)
    request = runtime_dependencies.control_models.SelectModel(
        SESSION_ID,
        runtime_dependencies.domain_ids.RequestId(FIRST_REQUEST_ID),
        model="gpt-5.6-sol",
    )
    monkeypatch.setattr(
        service,
        "_execute",
        lambda request: http_test_control_models.execute_control_outcome(outcome, request),
    )
    raised = None
    try:
        service.select_model(request)
    except Exception as error:  # noqa: BLE001 — the raised-path assertion
        raised = error
    return (rows, raised)


def acknowledged_control_service(
    monkeypatch: library_dependencies.pytest.MonkeyPatch,
    rows: list[MethodAuditRow],
) -> contract_dependencies.control_services.HarnessControlService:
    """Build a control service with fixed successful execution for audit tests.

    Returns:
        The service with test-only repositories, effects, and audit recording.

    """
    service = contract_dependencies.control_services.HarnessControlService(Mock())
    service.audit = http_test_audit_models.MethodAuditRecorder(rows)
    service.interrupts = http_test_control_models.NullInterruptRegistry()
    service.control_effects = http_test_control_models.NullControlEffects()
    service.sessions = http_test_audit_models.MissingSessions()
    monkeypatch.setattr(service, "_pending_attention_entry", lambda _request: None)
    monkeypatch.setattr(
        service,
        "_execute",
        lambda request: runtime_dependencies.control_models.ControlResult(
            request.request_id,
            runtime_dependencies.control_models.ControlAcknowledgement.ACKNOWLEDGED,
        ),
    )
    return service
