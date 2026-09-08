# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test http application."""

from __future__ import annotations

from app import provider_notifications, provider_runtime
from tests import (
    http_application_dependencies as application_dependencies,
    http_contract_dependencies as contract_dependencies,
    http_library_dependencies as library_dependencies,
    http_runtime_dependencies as runtime_dependencies,
    http_value_dependencies as standard_dependencies,
)

# Keep dependencies and server setup separate from request helpers.
# isort: split

from tests import (
    http_test_assets,
    http_test_audit_models,
    http_test_controls,
    http_test_hooks,
    http_test_requests,
    http_test_server_runtime,
)

SESSION_ID_TEXT = "session-one"
CODEX_HARNESS_TEXT = "codex"
WORKING_DIRECTORY = "/work"
WORKING_DIRECTORY_FIELD = "working_directory"
SESSION_ID_FIELD = "session_id"
TEXT_FIELD = "text"
BROWSER_DEVICE_ID = "browser-one"
SEQUENCE_FIELD = "sequence"
SAVED_FIELD = "saved"
ERROR_FIELD = "error"
REQUEST_ID_FIELD = "request_id"
FIRST_REQUEST_ID = "request-one"
APPLICATION_PREFERENCE_CHANGE_COUNT = 3
ATTACHMENT_PATH = "/test-data/image.png"
SESSION_ID = runtime_dependencies.domain_ids.SessionId(SESSION_ID_TEXT)


def test_terminal_diagnostics_show_visible_screen() -> None:
    """Verify terminal diagnostics show the visible screen."""
    terminal = contract_dependencies.fake_terminal.FakeTerminal(
        windows=(contract_dependencies.fake_terminal.window("window-one"),),
        screen_text="Choose the text style that looks best",
    )
    with http_test_assets.running_server(
        http_test_server_runtime.application(),
        (provider_runtime.terminal_plugin, terminal.plugin()),
    ) as server:
        response = http_test_controls.get(server, "/api/diagnostics/terminal")
        document = response[2].json
        assert response[0] == library_dependencies.http.client.OK
        assert document["windows"][0]["window_id"] == "window-one"
        assert document["windows"][0]["screen"] == "Choose the text style that looks best"


def test_insights_use_typed_canon_app_data() -> None:
    """Verify insights use typed canonical application data."""
    with http_test_assets.running_server(http_test_server_runtime.application()) as server:
        response = http_test_controls.get(server, "/api/insights")
        insights = response.body.json
        assert (
            response.status,
            insights["total_session_count"],
            insights["all_time"]["session_count"],
            insights["all_time"]["finished_session_count"],
            insights["projects"][0][WORKING_DIRECTORY_FIELD],
            insights["daily_sessions"][0]["session_count"],
            set(insights["hourly_sessions"][0]),
        ) == (
            library_dependencies.http.client.OK,
            1,
            1,
            0,
            WORKING_DIRECTORY,
            1,
            {"day_of_week", "hour", "session_count"},
        )
        response = http_test_controls.get(server, "/api/stats")
        assert response.status == library_dependencies.http.client.NOT_FOUND
        response = http_test_controls.get(server, "/sessionData/directories")
        expected_response = library_dependencies.http.client.OK, [WORKING_DIRECTORY]
        assert (response.status, response.body.json) == expected_response


def test_resumable_sessions_come_from_canon() -> None:
    """Verify resumable sessions come from canonical session summaries."""
    server, thread = http_test_hooks.server(http_test_server_runtime.application())
    with standard_dependencies.contextlib.ExitStack() as cleanup:
        cleanup.callback(http_test_requests.stop_server, server, thread)
        status, _, body = http_test_controls.get(
            server, "/api/resumable-sessions?working_directory=%2Fwork&search=session-one",
        )
        assert status == library_dependencies.http.HTTPStatus.OK
        assert body.json == [
            {
                SESSION_ID_FIELD: SESSION_ID_TEXT,
                "title": None,
                "last_activity_at": 10.0,
                "active": False,
                "harness": CODEX_HARNESS_TEXT,
                "model": None,
                "effort": None,
                "account": None,
            },
        ]
        status, _, body = http_test_controls.get(server, "/api/resumable-sessions?working_directory=%2Fother")
        assert status == library_dependencies.http.HTTPStatus.OK
        assert not body.json
        status, _, _ = http_test_controls.get(server, "/api/resumable?cwd=%2Fwork")
        assert status == library_dependencies.http.client.NOT_FOUND


def test_session_app_routes_publish_complete() -> None:
    """Verify session application routes publish complete composer state."""
    session_application = http_test_server_runtime.application()
    with http_test_assets.running_server(session_application) as server:
        status, body = http_test_controls.post(
            server,
            "/api/sessions/session-one/application/composer-draft",
            {TEXT_FIELD: "half written", "origin": BROWSER_DEVICE_ID, SEQUENCE_FIELD: 20},
        )
        assert (status, body.json) == (library_dependencies.http.client.OK, {SAVED_FIELD: True})
        status, body = http_test_controls.post(
            server,
            "/api/sessions/session-one/application/composer-draft",
            {TEXT_FIELD: "older", "origin": "browser-two", SEQUENCE_FIELD: 10},
        )
        assert (status, body.json) == (library_dependencies.http.client.OK, {SAVED_FIELD: False})
        status, _, body = http_test_controls.get(server, "/api/sessions/session-one/application")
        state = body.json
        assert (status, state["composer"], state["dialog"]) == (
            library_dependencies.http.client.OK,
            {"draft": {TEXT_FIELD: "half written", "origin": BROWSER_DEVICE_ID, SEQUENCE_FIELD: 20.0}, "queue": None},
            {"draft": None},
        )
        status, body = http_test_controls.post(
            server, "/api/sessions/session-one/application/tasks-hidden", {"hidden": True},
        )
        assert (status, body.json) == (
            library_dependencies.http.client.CONFLICT,
            {ERROR_FIELD: "every task must be completed before hiding the task card"},
        )


def test_global_app_routes_replace_field_specific() -> None:
    """Verify global application routes replace field specific preferences routes."""
    presence_calls: list[http_test_audit_models.PresenceCall] = []
    application = http_test_server_runtime.application()
    with http_test_assets.running_server(
        application,
        (
            provider_notifications.presence,
            http_test_server_runtime.RecordingPresence(presence_calls),
        ),
    ) as server:
        http_test_assets.assert_application_preferences(server, application)
        http_test_hooks.assert_push_subscriptions(server, application)
        http_test_hooks.assert_presence_routes(server, presence_calls)
        assert application.application_update_state.revision() == APPLICATION_PREFERENCE_CHANGE_COUNT
        http_test_hooks.assert_legacy_application_routes_are_gone(server)


def test_control_request_uses_complete_names() -> None:
    """Verify control request uses complete names and structured attachments."""
    request = application_dependencies.SendTextRequest.model_validate({
        REQUEST_ID_FIELD: FIRST_REQUEST_ID,
        TEXT_FIELD: "inspect",
        "attachments": [{"local_path": ATTACHMENT_PATH, "display_name": "image.png", "media_type": "image/png"}],
    }).request(SESSION_ID)
    assert request.session_id == SESSION_ID
    assert request.attachments[0].local_path == ATTACHMENT_PATH
    assert request.attachments[0].display_name == "image.png"
    attachment_only = application_dependencies.SendTextRequest.model_validate({
        REQUEST_ID_FIELD: "request-two",
        TEXT_FIELD: "",
        "attachments": [{"local_path": ATTACHMENT_PATH, "display_name": "image.png"}],
    }).request(SESSION_ID)
    assert not attachment_only.text


def test_invalid_canon_post_is_client_error_not() -> None:
    """Verify invalid canonical post is a client error not an old route."""
    server, thread = http_test_hooks.server(http_test_server_runtime.application())
    with standard_dependencies.contextlib.ExitStack() as cleanup:
        cleanup.callback(http_test_requests.stop_server, server, thread)
        response = http_test_controls.post(
            server, "/api/sessions/session-one/controls/send-text", {REQUEST_ID_FIELD: FIRST_REQUEST_ID},
        )
        assert response.status == library_dependencies.http.HTTPStatus.BAD_REQUEST
        assert TEXT_FIELD in response.body.json[ERROR_FIELD]
