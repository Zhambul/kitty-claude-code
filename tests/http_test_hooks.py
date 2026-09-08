# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http test hooks."""

from __future__ import annotations

from tests import (
    http_contract_dependencies as contract_dependencies,
    http_library_dependencies as library_dependencies,
    http_runtime_dependencies as runtime_dependencies,
    http_value_dependencies as standard_dependencies,
)

# Keep dependencies and server setup separate from request helpers.
# isort: split

from tests import (
    http_test_audit_models,
    http_test_control_models,
    http_test_controls,
    http_test_pane_models,
    http_test_response_helpers,
    http_test_server_runtime,
)

SESSION_ID_TEXT = "session-one"
LOOPBACK_ADDRESS = "127.0.0.1"
SESSION_ID_FIELD = "session_id"
BROWSER_DEVICE_ID = "browser-one"
SAVED_FIELD = "saved"
SUBSCRIPTION_REPLACEMENT_REVISION = 3
DEVICE_ID_FIELD = "device_id"
SESSION_ID = runtime_dependencies.domain_ids.SessionId(SESSION_ID_TEXT)
type JsonValue = bool | float | int | str | list[JsonValue] | dict[str, JsonValue] | None


def assert_gesture_schema(paths: dict[str, JsonValue], error_body: dict[str, str]) -> None:
    """Check send-text response codes and their shared outcome schema."""
    gesture = http_test_server_runtime.response_answers(paths, "/api/sessions/{session_id}/controls/send-text", "post")
    assert {"200", "202", "409"} <= set(gesture)
    outcome = http_test_control_models.json_object(http_test_server_runtime.response_schema(gesture["200"]))["anyOf"]
    assert (
        http_test_control_models.json_object(http_test_server_runtime.response_schema(gesture["202"]))["anyOf"]
        == outcome
    )
    assert (
        http_test_control_models.json_object(http_test_server_runtime.response_schema(gesture["409"]))["anyOf"]
        == outcome
    )
    assert http_test_server_runtime.response_schema(gesture["400"]) == error_body


def assert_launch_schema(paths: dict[str, JsonValue]) -> None:
    """Check that launch responses use accepted and conflict status codes."""
    launch = http_test_server_runtime.response_answers(paths, "/api/sessions", "post")
    assert "200" not in launch
    assert {"202", "409"} <= set(launch)


def server[Override](
    application: contract_dependencies.canonical_runtime.ProviderGraph,
    override: tuple[
        standard_dependencies.collections_abc.Callable[..., Override],
        Override,
    ]
    | None = None,
) -> tuple[
    http_test_pane_models.RunningDaemon,
    standard_dependencies.threading.Thread,
]:
    """Start a test server on an available local port.

    Returns:
        The server control object and its running thread.

    """
    bound_socket = standard_dependencies.socket.create_server((LOOPBACK_ADDRESS, 0))
    return http_test_server_runtime.start_server(
        http_test_controls.web_application(application, override), bound_socket,
    )


def assert_saved_application_route(
    server: http_test_pane_models.RunningDaemon,
    application: contract_dependencies.canonical_runtime.ProviderGraph,
    path: str,
    body: dict[str, JsonValue],
    revision: int,
) -> None:
    """Verify an application route saves its value and changes the revision."""
    response = http_test_controls.post(server, path, body)
    assert (response.status, response.body.json, application.application_update_state.revision()) == (
        library_dependencies.http.client.OK,
        {SAVED_FIELD: True},
        revision,
    )


def assert_push_subscriptions(
    server: http_test_pane_models.RunningDaemon,
    application: contract_dependencies.canonical_runtime.ProviderGraph,
) -> None:
    """Check subscription storage, replacement, and revision updates."""
    response = http_test_controls.post(
        server,
        "/api/application/push-subscriptions",
        http_test_response_helpers.subscription_document("https://push.example/subscription", "public", "secret"),
    )
    subscription_document = response.body.json
    assert (response.status, subscription_document) == (library_dependencies.http.client.OK, {SAVED_FIELD: True})
    subscriptions = application.push_subscriptions.subscriptions()
    assert [
        (
            subscription.endpoint,
            subscription.public_key,
            subscription.authentication_secret,
            subscription.device_id,
            subscription.device_label,
        )
        for subscription in subscriptions
    ] == [("https://push.example/subscription", "public", "secret", BROWSER_DEVICE_ID, "Tablet")]
    response = http_test_controls.post(
        server,
        "/api/application/push-subscriptions",
        http_test_response_helpers.subscription_document(
            "https://push.example/replacement", "new-public", "new-secret",
        ),
    )
    assert response.status == library_dependencies.http.HTTPStatus.OK
    assert [subscription.endpoint for subscription in application.push_subscriptions.subscriptions()] == [
        "https://push.example/replacement",
    ]
    assert application.application_update_state.revision() == SUBSCRIPTION_REPLACEMENT_REVISION


def assert_presence_routes(
    server: http_test_pane_models.RunningDaemon, presence_calls: list[http_test_audit_models.PresenceCall],
) -> None:
    """Check that viewing and away requests produce the expected presence calls."""
    response = http_test_controls.post(
        server, "/api/application/presence", {DEVICE_ID_FIELD: BROWSER_DEVICE_ID, SESSION_ID_FIELD: SESSION_ID_TEXT},
    )
    assert response.status == library_dependencies.http.HTTPStatus.OK
    assert response.body.json == {SAVED_FIELD: True}
    response = http_test_controls.post(
        server,
        "/api/application/presence",
        {DEVICE_ID_FIELD: BROWSER_DEVICE_ID, SESSION_ID_FIELD: SESSION_ID_TEXT, "away": True},
    )
    assert response.status == library_dependencies.http.client.OK
    assert presence_calls == [
        http_test_audit_models.PresenceCall("device", device=BROWSER_DEVICE_ID),
        http_test_audit_models.PresenceCall("viewing", session_id=SESSION_ID),
        http_test_audit_models.PresenceCall("away", BROWSER_DEVICE_ID, SESSION_ID),
    ]


def assert_legacy_application_routes_are_gone(server: http_test_pane_models.RunningDaemon) -> None:
    """Check that removed application routes return not found."""
    for legacy_path in ("/api/ns-prefs", "/api/ns-draft", "/api/dirs/hidden", "/api/limits"):
        status, _, _ = http_test_controls.get(server, legacy_path)
        assert status == library_dependencies.http.client.NOT_FOUND
    for legacy_path in ("/api/ns-prefs", "/api/ns-draft", "/api/dirs/hide", "/api/push/subscribe", "/api/presence"):
        status, _ = http_test_controls.post(server, legacy_path, {})
        assert status == library_dependencies.http.client.NOT_FOUND
