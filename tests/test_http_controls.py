# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test http controls."""

from __future__ import annotations

from unittest.mock import Mock

from app import provider_browser_telemetry, provider_terminal
from tests import (
    http_application_dependencies as application_dependencies,
    http_contract_dependencies as contract_dependencies,
    http_library_dependencies as library_dependencies,
    http_runtime_dependencies as runtime_dependencies,
    http_test_server_runtime,
    http_value_dependencies as standard_dependencies,
)

# Keep dependencies and server setup separate from request helpers.
# isort: split

from tests import (
    http_test_assets,
    http_test_audit_models,
    http_test_contracts,
    http_test_control_models,
    http_test_controls,
    http_test_preferences,
    http_test_requests,
    http_test_response_helpers,
)

SESSION_ID_TEXT = "session-one"
WORKING_DIRECTORY = "/work"
WORKING_DIRECTORY_FIELD = "working_directory"
SESSION_ID_FIELD = "session_id"
FIRST_REQUEST_ID = "request-one"
SESSION_ID = runtime_dependencies.domain_ids.SessionId(SESSION_ID_TEXT)
type MethodAuditRow = tuple[str, contract_dependencies.control_services.ControlAudit]


def test_browser_telemetry_uses_named_app() -> None:
    """Verify browser telemetry uses named application resources."""
    audit = http_test_audit_models.BrowserAudit()
    application = http_test_server_runtime.application()
    override = (
        provider_browser_telemetry.browser_telemetry,
        application_dependencies.BrowserTelemetryService(audit),
    )
    with http_test_assets.running_server(application, override) as server:
        http_test_assets.send_browser_telemetry(server)
        assert [record[2] for record in audit.records] == [
            "browser-optimistic-action",
            "browser-client-failure",
            "browser-event",
        ]
        recorded_content = standard_dependencies.json.loads(audit.records[0][3])
        assert recorded_content[SESSION_ID_FIELD] == SESSION_ID_TEXT
        http_test_contracts.assert_legacy_telemetry_routes_are_gone(server)


def test_unconfirmed_control_is_audited_with_its(monkeypatch: library_dependencies.pytest.MonkeyPatch) -> None:
    """Verify an unconfirmed control is audited with its reason."""
    rows, raised = http_test_requests.audited_control(
        monkeypatch,
        runtime_dependencies.control_models.ControlResult(
            runtime_dependencies.domain_ids.RequestId(FIRST_REQUEST_ID),
            runtime_dependencies.control_models.ControlAcknowledgement.INDETERMINATE,
            "row: no 'all models'",
        ),
    )
    assert raised is None
    assert len(rows) == 1
    log, action, content = rows[0]
    assert (log, action) == (str(SESSION_ID), "control")
    assert (content.control, content.status, content.reason) == (
        "select_model",
        "indeterminate",
        "row: no 'all models'",
    )
    assert isinstance(content.ms, int)


def test_an_acknowledged_control_is_audited_too(monkeypatch: library_dependencies.pytest.MonkeyPatch) -> None:
    """Verify an acknowledged control is audited too."""
    rows, _ = http_test_requests.audited_control(
        monkeypatch,
        runtime_dependencies.control_models.ControlResult(
            runtime_dependencies.domain_ids.RequestId(FIRST_REQUEST_ID),
            runtime_dependencies.control_models.ControlAcknowledgement.ACKNOWLEDGED,
        ),
    )
    assert rows[0][2].status == "acknowledged"
    assert not rows[0][2].reason


def test_raised_control_is_audited_before_it(monkeypatch: library_dependencies.pytest.MonkeyPatch) -> None:
    """Verify a raised control is audited before it propagates."""
    rows, raised = http_test_requests.audited_control(monkeypatch, RuntimeError("driver exploded"))
    assert isinstance(raised, RuntimeError)
    assert rows[0][2].status == "raised"


def test_broken_audit_never_takes_down_gesture(monkeypatch: library_dependencies.pytest.MonkeyPatch) -> None:
    """Verify a broken audit never takes down the gesture."""
    service = contract_dependencies.control_services.HarnessControlService(Mock())
    service.audit = http_test_audit_models.BrokenControlAudit()
    service.sessions = http_test_audit_models.MissingSessions()
    monkeypatch.setattr(
        service,
        "_execute",
        lambda request: runtime_dependencies.control_models.ControlResult(
            request.request_id, runtime_dependencies.control_models.ControlAcknowledgement.ACKNOWLEDGED,
        ),
    )
    outcome = service.select_model(
        runtime_dependencies.control_models.SelectModel(
            SESSION_ID, runtime_dependencies.domain_ids.RequestId(FIRST_REQUEST_ID), model="x",
        ),
    )
    assert outcome.status == "acknowledged"


def test_every_control_method_writes_exactly_one(monkeypatch: library_dependencies.pytest.MonkeyPatch) -> None:
    """Verify every control method writes exactly one audit row through one core."""
    rows: list[MethodAuditRow] = []
    service = http_test_requests.acknowledged_control_service(monkeypatch, rows)
    http_test_response_helpers.assert_control_invocations(rows, http_test_preferences.control_invocations(service))


def test_pane_command_route_carries_keypress_env() -> None:
    """Verify pane command route carries the keypress environment."""
    pane_commands = http_test_control_models.PaneCommands()
    with http_test_assets.running_server(
        http_test_server_runtime.application(),
        (provider_terminal.pane_commands, pane_commands),
    ) as server:
        response = http_test_controls.post(
            server,
            "/api/terminal/panes/set-percent",
            {"window_id": "77", WORKING_DIRECTORY_FIELD: WORKING_DIRECTORY, "percent": 40},
        )
        response_document = response.body.json
        assert (response.status, response_document, pane_commands.calls) == (
            library_dependencies.http.client.OK,
            {"handled": True, "succeeded": True, "reason": None},
            [("setpct", "77", WORKING_DIRECTORY, None, 40)],
        )
        pane_commands.outcome = contract_dependencies.PaneCommandOutcome(
            handled=True, succeeded=False, reason="no pane",
        )
        response = http_test_controls.post(
            server, "/api/terminal/panes/toggle", {WORKING_DIRECTORY_FIELD: WORKING_DIRECTORY},
        )
        response_document = response.body.json
        assert (response.status, response_document["reason"]) == (
            library_dependencies.http.client.CONFLICT,
            "no pane",
        )
        pane_commands.outcome = contract_dependencies.PaneCommandOutcome(handled=False, succeeded=True)
        response = http_test_controls.post(
            server, "/api/terminal/panes/toggle", {WORKING_DIRECTORY_FIELD: WORKING_DIRECTORY},
        )
        response_document = response.body.json
        assert (response.status, response_document["handled"]) == (library_dependencies.http.client.OK, False)
        status, _ = http_test_controls.post(server, "/api/terminal/panes/toggle", {})
        assert status == library_dependencies.http.HTTPStatus.BAD_REQUEST
