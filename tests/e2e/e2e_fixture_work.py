# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture work."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from tests.e2e import (
    e2e_fixture_dependencies as fixture_dependencies,
    e2e_fixture_journeys,
    e2e_fixture_reporting,
    e2e_fixture_usage,
)

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator

FILE_RENAME_SOURCE = "baqylau-e2e-rename-source.txt"
FILE_RENAME_TARGET = "baqylau-e2e-rename-target.txt"
MISSING_FILE_FIXTURE = "baqylau-e2e-missing-file-963.txt"
REWIND_FILE_FIXTURE = "baqylau-e2e-rewind.txt"
TEXT_ENCODING = "utf-8"
SESSION_SCOPE: Literal["session"] = "session"
CLAUDE_CONFIG_DIRECTORY_VARIABLE = "CLAUDE_CONFIG_DIR"
CLAUDE_MANAGED_SETTINGS_VARIABLE = "CLAUDE_CODE_MANAGED_SETTINGS_PATH"


@fixture_dependencies.application.pytest.fixture
def file_rename_paths(workspace: str) -> Iterator[tuple[str, str]]:
    """Reserve and clean up the source and target paths for a rename.

    Yields:
        The source and target file paths.

    """
    paths = (
        str(fixture_dependencies.application.Path(workspace) / FILE_RENAME_SOURCE),
        str(fixture_dependencies.application.Path(workspace) / FILE_RENAME_TARGET),
    )
    for path in paths:
        with fixture_dependencies.standard.contextlib.suppress(FileNotFoundError):
            fixture_dependencies.standard.os.unlink(path)
    try:
        yield paths
    finally:
        for path in paths:
            with fixture_dependencies.standard.contextlib.suppress(FileNotFoundError):
                fixture_dependencies.standard.os.unlink(path)


@fixture_dependencies.application.pytest.fixture
def missing_file_path(workspace: str) -> Iterator[str]:
    """Reserve a path that has no file at test startup.

    Yields:
        The missing file path, which is removed after the test.

    """
    path = str(fixture_dependencies.application.Path(workspace) / MISSING_FILE_FIXTURE)
    with fixture_dependencies.standard.contextlib.suppress(FileNotFoundError):
        fixture_dependencies.application.Path(path).unlink()
    try:
        yield path
    finally:
        with fixture_dependencies.standard.contextlib.suppress(FileNotFoundError):
            fixture_dependencies.application.Path(path).unlink()


@fixture_dependencies.application.pytest.fixture
def rewind_file_path(workspace: str) -> Iterator[str]:
    """Write the baseline file used by rewind tests.

    Yields:
        The baseline file path, which is removed after the test.

    """
    path = str(fixture_dependencies.application.Path(workspace) / REWIND_FILE_FIXTURE)
    with fixture_dependencies.standard.contextlib.suppress(FileNotFoundError):
        fixture_dependencies.application.Path(path).unlink()
    fixture_dependencies.application.Path(path).write_text("rewind-baseline-194\n", encoding=TEXT_ENCODING)
    try:
        yield path
    finally:
        with fixture_dependencies.standard.contextlib.suppress(FileNotFoundError):
            fixture_dependencies.application.Path(path).unlink()


def failure_report(
    test_item: fixture_dependencies.application.pytest.Item,
) -> Generator[
    None,
    fixture_dependencies.application.pytest.TestReport,
    fixture_dependencies.application.pytest.TestReport,
]:
    """Add application diagnostics to a failed E2E report.

    Returns:
        The report with a diagnostic section when an application is available.

    Yields:
        Control to pytest while the test report is built.

    """
    report = yield
    if report.when not in {"call", "teardown"} or not report.failed:
        return report
    if not isinstance(test_item, fixture_dependencies.application.pytest.Function):
        return report
    application = test_item.funcargs.get("application_process")
    if not isinstance(application, fixture_dependencies.drivers.process_testkit.ApplicationProcess):
        return report
    try:
        diagnostics = e2e_fixture_journeys.failure_diagnostic_text(application, test_item)
    except Exception as error:  # noqa: BLE001 — the raised-path assertion
        diagnostics = f"failure diagnostics raised {type(error).__name__}: {error}"
    report.sections.append(("Baqylau E2E diagnostics", diagnostics))
    return report  # noqa: B901 -- Pluggy wrappers return the hook result.


@fixture_dependencies.application.pytest.fixture(scope=SESSION_SCOPE)
def isolated_codex_home(
    tmp_path_factory: fixture_dependencies.application.pytest.TempPathFactory,
    workspace: str,
) -> fixture_dependencies.application.Path:
    """Create a test profile with the current Codex credentials and hooks.

    Returns:
        The isolated Codex profile directory.

    Raises:
        AssertionError: If the source profile has no trusted hooks.

    """
    source = fixture_dependencies.application.Path(
        fixture_dependencies.standard.os.environ.get(
            "CODEX_HOME",
            fixture_dependencies.application.Path.home() / ".codex",
        ),
    )
    destination = tmp_path_factory.mktemp("baqylau-e2e-codex-home")
    fixture_dependencies.standard.shutil.copy2(source / "auth.json", destination / "auth.json")
    fixture_dependencies.standard.shutil.copy2(source / "hooks.json", destination / "hooks.json")
    hook_state_lines = e2e_fixture_journeys.codex_hook_state_lines(source, destination)
    if len(hook_state_lines) == 1:
        message = "Codex E2E hooks have no trusted source entries"
        raise AssertionError(message)
    (destination / "config.toml").write_text(
        e2e_fixture_journeys.isolated_codex_config(workspace, hook_state_lines),
        encoding=TEXT_ENCODING,
    )
    return destination


@fixture_dependencies.application.pytest.fixture(scope=SESSION_SCOPE)
def isolated_claude_home(
    tmp_path_factory: fixture_dependencies.application.pytest.TempPathFactory,
) -> Iterator[fixture_dependencies.application.Path]:
    """Create one writable Claude profile per xdist worker.

    Yields:
        The isolated Claude profile directory.

    """
    source = fixture_dependencies.application.Path(
        fixture_dependencies.standard.os.environ.get(
            CLAUDE_CONFIG_DIRECTORY_VARIABLE,
            fixture_dependencies.application.Path.home() / ".claude",
        ),
    )
    destination = tmp_path_factory.mktemp("baqylau-e2e-claude-home")
    e2e_fixture_reporting.copy_claude_credentials(source, destination)
    e2e_fixture_usage.copy_optional_claude_settings(source, destination)
    e2e_fixture_journeys.copy_isolated_claude_settings(source, destination)
    managed_settings = destination / "managed-settings.json"
    managed_settings.write_text("{}", encoding=TEXT_ENCODING)
    previous = fixture_dependencies.standard.os.environ.get(CLAUDE_CONFIG_DIRECTORY_VARIABLE)
    previous_managed_settings = fixture_dependencies.standard.os.environ.get(CLAUDE_MANAGED_SETTINGS_VARIABLE)
    fixture_dependencies.standard.os.environ[CLAUDE_CONFIG_DIRECTORY_VARIABLE] = str(destination)
    fixture_dependencies.standard.os.environ[CLAUDE_MANAGED_SETTINGS_VARIABLE] = str(managed_settings)
    try:
        yield destination
    finally:
        if previous is None:
            fixture_dependencies.standard.os.environ.pop(CLAUDE_CONFIG_DIRECTORY_VARIABLE, None)
        else:
            fixture_dependencies.standard.os.environ[CLAUDE_CONFIG_DIRECTORY_VARIABLE] = previous
        if previous_managed_settings is None:
            fixture_dependencies.standard.os.environ.pop(CLAUDE_MANAGED_SETTINGS_VARIABLE, None)
        else:
            fixture_dependencies.standard.os.environ[CLAUDE_MANAGED_SETTINGS_VARIABLE] = previous_managed_settings


@fixture_dependencies.application.pytest.fixture
def versioned_session_config_context(
    session_config_context: fixture_dependencies.testkit.session_contexts.SessionConfigContext,
    versioned_workspace: str,
) -> fixture_dependencies.testkit.session_contexts.WorkspaceSessionConfigContext:
    """Return session configuration services for a versioned workspace.

    Returns:
        Session configuration services for a versioned workspace.

    """
    return fixture_dependencies.testkit.session_contexts.WorkspaceSessionConfigContext(
        session_config_context,
        versioned_workspace,
    )
