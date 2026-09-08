# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http test assets."""

from __future__ import annotations

from tests import (
    http_contract_dependencies as contract_dependencies,
    http_library_dependencies as library_dependencies,
    http_value_dependencies as standard_dependencies,
)

# Keep dependencies and server setup separate from request helpers.
# isort: split

from tests import (
    http_test_application_builders,
    http_test_audit_models,
    http_test_contracts,
    http_test_controls,
    http_test_hooks,
    http_test_pane_models,
    http_test_requests,
    http_test_response_helpers,
)

SESSION_ID_TEXT = "session-one"
CODEX_HARNESS_TEXT = "codex"
HTTP_GET_METHOD = "GET"
WORKING_DIRECTORY_FIELD = "working_directory"
SESSION_ID_FIELD = "session_id"
TEXT_FIELD = "text"
BROWSER_DEVICE_ID = "browser-one"
SEQUENCE_FIELD = "sequence"
ERROR_FIELD = "error"
PROJECT_DIRECTORY = "/project"
MINIMUM_STATIC_REFERENCES = 4
DEVICE_ID_FIELD = "device_id"


@standard_dependencies.contextlib.contextmanager
def running_server[Override](
    application: contract_dependencies.canonical_runtime.ProviderGraph,
    override: tuple[
        standard_dependencies.collections_abc.Callable[..., Override],
        Override,
    ]
    | None = None,
) -> standard_dependencies.collections_abc.Iterator[http_test_pane_models.RunningDaemon]:
    """Run a test server for the duration of a context.

    Yields:
        The running server, which is stopped when the context exits.

    """
    server, thread = http_test_hooks.server(application, override)
    with standard_dependencies.contextlib.ExitStack() as cleanup:
        cleanup.callback(http_test_requests.stop_server, server, thread)
        yield server


def assert_application_preferences(
    server: http_test_pane_models.RunningDaemon,
    application: contract_dependencies.canonical_runtime.ProviderGraph,
) -> None:
    """Check saved session preferences, drafts, and hidden directories."""
    http_test_hooks.assert_saved_application_route(
        server,
        application,
        "/api/application/new-session-preferences",
        {WORKING_DIRECTORY_FIELD: PROJECT_DIRECTORY, "harness": CODEX_HARNESS_TEXT, "model": "gpt-5", "effort": "high"},
        1,
    )
    http_test_hooks.assert_saved_application_route(
        server,
        application,
        "/api/application/new-session-drafts",
        {WORKING_DIRECTORY_FIELD: PROJECT_DIRECTORY, TEXT_FIELD: "unfinished", SEQUENCE_FIELD: 25},
        2,
    )
    response = http_test_controls.post(
        server, "/api/application/hidden-directories", {WORKING_DIRECTORY_FIELD: "/parked"},
    )
    hidden = response.body.json["hidden"]
    assert (response.status, application.application_update_state.revision()) == (
        library_dependencies.http.client.OK,
        3,
    )
    assert "/parked" in hidden
    stored = application.new_sessions.preferences()
    assert stored is not None
    assert (stored.working_directory, stored.harness, stored.model, stored.effort) == (
        PROJECT_DIRECTORY,
        CODEX_HARNESS_TEXT,
        "gpt-5",
        "high",
    )
    drafts = application.new_sessions.drafts()
    assert (
        (drafts[0].working_directory, drafts[0].text),
        "/parked" in {entry.working_directory for entry in application.hidden_directories.hidden()},
    ) == ((PROJECT_DIRECTORY, "unfinished"), True)


def send_browser_telemetry(server: http_test_pane_models.RunningDaemon) -> None:
    """Send and verify the supported browser telemetry requests."""
    http_test_contracts.assert_recorded_telemetry(
        server,
        "/api/sessions/session-one/application/optimistic-actions",
        {"action": "composer", "phase": "reconciled", "character_count": 12, "elapsed_milliseconds": 40},
    )
    http_test_contracts.assert_recorded_telemetry(
        server,
        "/api/sessions/session-one/application/client-failures",
        {"gesture": "send", "failure_kind": "transport", ERROR_FIELD: "connection closed"},
    )
    http_test_contracts.assert_recorded_telemetry(
        server,
        "/api/application/browser-events",
        {
            "client_id": "client-one",
            DEVICE_ID_FIELD: BROWSER_DEVICE_ID,
            "connection": {"online": True, "stream_count": 2},
            "events": [
                {
                    SESSION_ID_FIELD: SESSION_ID_TEXT,
                    "name": "send.started",
                    "timestamp": 50,
                    "details": {"character_count": 12},
                },
            ],
        },
    )


def validated_response_routes(
    application: contract_dependencies.canonical_runtime.ProviderGraph,
    server: http_test_pane_models.RunningDaemon,
) -> list[str]:
    """Validate modeled GET responses whose path parameters are known.

    Returns:
        The route templates whose responses were checked.

    """
    checked: list[str] = []
    for route in http_test_application_builders.api_routes(
        library_dependencies.build_web_application(application.instances),
    ):
        if route.methods is None or HTTP_GET_METHOD not in route.methods or route.response_model is None:
            continue
        path = http_test_response_helpers.fixture_route_path(route)
        if path is not None:
            http_test_contracts.validate_route_response(server, route, path)
            checked.append(route.path)
    return checked


def served_build_references(server: http_test_pane_models.RunningDaemon, document: bytes) -> set[str]:
    """Check each static reference in an index document.

    Returns:
        The build-relative paths found in the document.

    """
    references = standard_dependencies.re.findall(
        rb"(?:src|href)=\"(/static/[^\"]+)\"",
        document,
    )
    assert len(references) >= MINIMUM_STATIC_REFERENCES
    build_references: set[str] = set()
    for reference_bytes in references:
        reference = http_test_audit_models.AssetReference.from_bytes(reference_bytes)
        if reference.build_path is not None:
            build_references.add(reference.build_path)
            assert "?v=" not in reference.path, reference.path
        http_test_contracts.assert_served_asset(server, reference)
    return build_references
