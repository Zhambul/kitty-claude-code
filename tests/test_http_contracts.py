# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test http contracts."""

from __future__ import annotations

from tests import (
    http_application_dependencies as application_dependencies,
    http_library_dependencies as library_dependencies,
    http_test_server_runtime,
    http_value_dependencies as standard_dependencies,
)

# Keep dependencies and server setup separate from request helpers.
# isort: split

from tests import (
    http_test_application_builders,
    http_test_assets,
    http_test_contracts,
    http_test_control_models,
    http_test_controls,
    http_test_hooks,
    http_test_preferences,
    http_test_requests,
)

SESSION_ID_FIELD = "session_id"
ERROR_FIELD = "error"


def test_input_caller_really_did_get_wrong() -> None:
    """Verify input the caller really did get wrong is still a 400 with its reason.

    The other half of the change above: the sites that meant "bad request" say
        so by type, and keep the 400 and the message the browser already reads.
    """
    server, thread = http_test_hooks.server(http_test_server_runtime.application())
    with standard_dependencies.contextlib.ExitStack() as cleanup:
        cleanup.callback(http_test_requests.stop_server, server, thread)
        status, _, body = http_test_controls.get_response(server, "/sessionData/nosuchsession")
        assert status == library_dependencies.http.client.BAD_REQUEST
        assert "unknown session" in body.json[ERROR_FIELD]
        status, _, body = http_test_controls.get_response(server, "/api/harnesses/mystery/catalog")
        assert status == library_dependencies.http.client.BAD_REQUEST
        assert "mystery" in body.json[ERROR_FIELD]


def test_session_id_that_could_never_be_one() -> None:
    """Verify a session id that could never be one is refused at the boundary.

    A path parameter used to be a bare `str`, so anything at all reached the
        store, the harness registry, and — truncated to 200 characters, which is not
        the same thing as validated — the audit rows a stream writes about itself.
    """
    server, thread = http_test_hooks.server(http_test_server_runtime.application())
    with standard_dependencies.contextlib.ExitStack() as cleanup:
        cleanup.callback(http_test_requests.stop_server, server, thread)
        status, _, body = http_test_controls.get_response(server, "/sessionData/not%20a%20session")
        assert status == library_dependencies.http.client.BAD_REQUEST
        assert SESSION_ID_FIELD in body.json[ERROR_FIELD]
        status, _, _ = http_test_controls.get_response(server, "/api/harnesses/NOT-A-NAME/catalog")
        assert status == library_dependencies.http.client.BAD_REQUEST


def test_every_declared_response_model_describes() -> None:
    """Verify the published schema describes the bytes on the read plane."""
    application = http_test_server_runtime.application()
    with http_test_assets.running_server(application) as server:
        http_test_application_builders.assert_read_plane_was_checked(
            http_test_assets.validated_response_routes(application, server),
        )


def test_published_schema_names_every_status() -> None:
    """Verify the published schema names every status that a caller must handle."""
    paths = http_test_control_models.json_object(
        library_dependencies.build_web_application(http_test_server_runtime.application().instances).openapi()["paths"],
    )
    error_body = {"$ref": "#/components/schemas/ErrorResponse"}
    http_test_controls.assert_standard_schema_errors(paths, error_body)
    http_test_preferences.assert_no_validation_error_response(paths)
    http_test_hooks.assert_gesture_schema(paths, error_body)
    http_test_hooks.assert_launch_schema(paths)


def test_every_plane_carries_the_security_headers() -> None:
    """Verify every HTTP plane has the security headers."""
    with http_test_assets.running_server(http_test_server_runtime.application()) as server:
        http_test_contracts.assert_plane_security(server)
        http_test_contracts.assert_cached_build_headers(server)


def test_installed_app_versions_follow_content(
    tmp_path: library_dependencies.Path, monkeypatch: library_dependencies.pytest.MonkeyPatch,
) -> None:
    """Verify an icon change updates the installed application identity."""
    http_test_application_builders.write_installed_app_assets(tmp_path)
    monkeypatch.setattr(application_dependencies.static_documents, "STATIC_DIR", str(tmp_path))
    monkeypatch.setattr(application_dependencies.static_documents, "manifest_tags", lambda: b"build assets")
    first_policy = standard_dependencies.dataclasses.replace(
        application_dependencies.api_config.settings(), boot_id="boot-one", cache_static="immutable",
    )
    second_policy = standard_dependencies.dataclasses.replace(
        application_dependencies.api_config.settings(), boot_id="boot-two", cache_static="immutable",
    )
    first_document = http_test_application_builders.assert_restart_keeps_asset_versions(first_policy, second_policy)
    http_test_application_builders.assert_icon_change_updates_versions(tmp_path, second_policy, first_document)


def test_every_asset_document_references() -> None:
    """Verify the server delivers each static asset that the index document names."""
    with http_test_assets.running_server(http_test_server_runtime.application()) as server:
        build_references = http_test_assets.served_build_references(
            server, http_test_contracts.index_document(server),
        )
        assert build_references == http_test_server_runtime.expected_build_references()
