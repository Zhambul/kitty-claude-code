# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http test controls."""

from __future__ import annotations

from tests import (
    http_contract_dependencies as contract_dependencies,
    http_library_dependencies as library_dependencies,
    http_test_pane_models,
    http_test_preferences,
    http_test_requests,
    http_test_response_helpers,
    http_test_server_runtime,
    http_value_dependencies as standard_dependencies,
)

LOOPBACK_ADDRESS = "127.0.0.1"
HTTP_GET_METHOD = "GET"
SESSION_ID_FIELD = "session_id"
HOOK_SESSION_ID = "hook-session"
CLAUDE_HARNESS_TEXT = "claude_code"
type JsonValue = bool | float | int | str | list[JsonValue] | dict[str, JsonValue] | None


def web_application[Override](
    application: contract_dependencies.canonical_runtime.ProviderGraph,
    override: tuple[standard_dependencies.collections_abc.Callable[..., Override], Override] | None,
) -> library_dependencies.fastapi.FastAPI:
    """Build the HTTP application with an optional provider override.

    Returns:
        The configured test application.

    """
    web_application = library_dependencies.build_web_application(application.instances)
    if override is not None:
        provider, override_dependency = override
        web_application.dependency_overrides[provider] = http_test_server_runtime.fixed(override_dependency)
    return web_application


def get(server: http_test_pane_models.RunningDaemon, path: str) -> http_test_requests.HttpGetResponse:
    """Read one complete GET response from the test server.

    Returns:
        The response status, content type, and body.

    """
    connection = library_dependencies.http.client.HTTPConnection(LOOPBACK_ADDRESS, server.server_port, timeout=2)
    connection.request(HTTP_GET_METHOD, path)
    response = connection.getresponse()
    body = http_test_response_helpers.JsonBody(response.read())
    connection.close()
    return http_test_requests.HttpGetResponse(response.status, response.getheader("Content-Type"), body)


def get_response(
    server: http_test_pane_models.RunningDaemon,
    path: str,
    *,
    read_body: bool = True,
) -> http_test_requests.HttpHeadersResponse:
    """Send one GET and read its response headers and optional body.

    `read_body=False` is for the event streams, whose body never ends: the
    headers are already out by then, which is the whole point of a stream.

    Returns:
        The status, headers, and body, with an empty body when reading is disabled.

    """
    with standard_dependencies.contextlib.closing(
        library_dependencies.http.client.HTTPConnection(LOOPBACK_ADDRESS, server.server_port, timeout=2),
    ) as connection:
        connection.request(HTTP_GET_METHOD, path)
        response = connection.getresponse()
        body = (
            http_test_response_helpers.JsonBody(response.read()) if read_body else http_test_response_helpers.JsonBody()
        )
        return http_test_requests.HttpHeadersResponse(response.status, response.headers, body)


def post(
    server: http_test_pane_models.RunningDaemon,
    path: str,
    body: dict[str, JsonValue],
) -> http_test_requests.HttpResponse:
    """Send a JSON document to the test server.

    Returns:
        The response status and complete body.

    """
    connection = library_dependencies.http.client.HTTPConnection(LOOPBACK_ADDRESS, server.server_port, timeout=2)
    encoded = standard_dependencies.json.dumps(body).encode()
    connection.request("POST", path, body=encoded, headers={"Content-Type": "application/json"})
    response = connection.getresponse()
    response_body = http_test_response_helpers.JsonBody(response.read())
    connection.close()
    return http_test_requests.HttpResponse(response.status, response_body)


def assert_successful_hook(server: http_test_pane_models.RunningDaemon, payload: bytes) -> None:
    """Check that a Claude hook returns a successful command update."""
    status, body = http_test_preferences.post_hook(
        server,
        CLAUDE_HARNESS_TEXT,
        payload,
        {"X-Baqylau-Terminal-Window": "1114", "X-Baqylau-Harness-Process": "4242"},
    )
    assert status == library_dependencies.http.client.OK
    assert b"updatedInput" in body


def post_distinct_hook_events(
    server: http_test_pane_models.RunningDaemon,
    tmp_path: library_dependencies.Path,
) -> tuple[bytes, bytes]:
    """Post a duplicate hook followed by a hook with a different tool name.

    Returns:
        The original and changed hook payloads.

    """
    document = {
        SESSION_ID_FIELD: HOOK_SESSION_ID,
        "transcript_path": str(tmp_path / "hook-session.jsonl"),
        "hook_event_name": "PostToolUse",
        "hook_event_id": "post-one",
        "tool_name": "Read",
    }
    first = standard_dependencies.json.dumps(document).encode()
    assert (
        http_test_preferences.post_hook(server, CLAUDE_HARNESS_TEXT, first)[0] == library_dependencies.http.client.OK
    )
    assert (
        http_test_preferences.post_hook(server, CLAUDE_HARNESS_TEXT, first)[0] == library_dependencies.http.client.OK
    )
    changed = standard_dependencies.json.dumps({**document, "tool_name": "Write"}).encode()
    assert (
        http_test_preferences.post_hook(server, CLAUDE_HARNESS_TEXT, changed)[0] == library_dependencies.http.client.OK
    )
    return (first, changed)


def assert_standard_schema_errors(paths: dict[str, JsonValue], error_body: dict[str, str]) -> None:
    """Check standard error response schemas for the selected routes."""
    for route_path, method in (
        ("/sessionData", "get"),
        ("/sessionData/{session_id}/entries", "get"),
        ("/api/sessions/{session_id}/controls/background", "post"),
    ):
        responses = http_test_server_runtime.response_answers(paths, route_path, method)
        assert {"400", "500"} <= set(responses), (route_path, method)
        assert http_test_server_runtime.response_schema(responses["400"]) == error_body
