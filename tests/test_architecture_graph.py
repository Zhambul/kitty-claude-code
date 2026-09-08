# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test architecture graph."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_canonical,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
IMPLEMENTATION_DIRECTORY_NAME = "impl"
HARNESS_PACKAGE = "harness"
MODELS_DIRECTORY_NAME = "models"
API_PACKAGE = "api"
APP_PACKAGE = "app"
DASHBOARD_PACKAGE = "dashboard"
ENGINE_PACKAGE = "engine"
HARNESS_ROOT = ROOT / HARNESS_PACKAGE
DASHBOARD_ROOT = ROOT / DASHBOARD_PACKAGE
CLAUDE_CODE_PACKAGE = "claude_code"
SERVICES_DIRECTORY_NAME = "services"
CODEX_PACKAGE = "codex"
FRONTEND_DIRECTORY_NAME = "frontend"
SOURCE_DIRECTORY_NAME = "src"


def test_canon_consumers_cannot_observe() -> None:
    """Verify canonical consumers cannot observe or checkpoint native sources."""
    consumers = [
        DASHBOARD_ROOT / SERVICES_DIRECTORY_NAME,
        ROOT / ENGINE_PACKAGE / "sessiondata",
        *sorted((ROOT / API_PACKAGE).rglob(PYTHON_FILE_PATTERN)),
    ]
    forbidden_fragments = (".drain(", ".sources(", "CheckpointStore", "ObservationRunner", "SourceCheckpoint")
    consumer_source_violations = [
        violation
        for consumer in consumers
        for violation in architecture_test_canonical.consumer_source_violations(consumer, forbidden_fragments)
    ]
    assert not consumer_source_violations


def test_canon_sse_has_no_broker_or_app_event() -> None:
    """Verify canonical SSE has no broker or application event registry."""
    source = (ROOT / API_PACKAGE / "sessiondata" / "streams.py").read_text(encoding=TEXT_ENCODING)
    assert "DashboardEventStream" not in source
    assert "subscribe" not in source
    assert "queue.Queue" not in source
    assert not (DASHBOARD_ROOT / "events.py").exists()
    assert not (ROOT / API_PACKAGE / "broker.py").exists()


def test_global_app_updates_use_event_stream() -> None:
    """Verify global application updates use the event stream instead of a timer."""
    state = (
        DASHBOARD_ROOT / FRONTEND_DIRECTORY_NAME / SOURCE_DIRECTORY_NAME / APP_PACKAGE / "app-state.svelte.ts"
    ).read_text(encoding=TEXT_ENCODING)
    stream = (
        DASHBOARD_ROOT / FRONTEND_DIRECTORY_NAME / SOURCE_DIRECTORY_NAME / API_PACKAGE / "global-stream.ts"
    ).read_text(encoding=TEXT_ENCODING)
    assert "APPLICATION_REFRESH_MS" not in state
    assert "applicationRefreshTimer" not in state
    assert "addEventListener('application'" in stream


def test_resume_and_sse_have_one_authoritative() -> None:
    """Verify resume and SSE have one authoritative path."""
    launch_files = (
        HARNESS_ROOT / MODELS_DIRECTORY_NAME / "launch.py",
        ROOT / API_PACKAGE / "controls" / "routes.py",
        ROOT
        / DASHBOARD_PACKAGE
        / FRONTEND_DIRECTORY_NAME
        / SOURCE_DIRECTORY_NAME
        / "sessions"
        / "components"
        / "Composer.svelte",
        ROOT
        / DASHBOARD_PACKAGE
        / FRONTEND_DIRECTORY_NAME
        / SOURCE_DIRECTORY_NAME
        / "new-session"
        / "NewSessionModal.svelte",
        ROOT
        / DASHBOARD_PACKAGE
        / FRONTEND_DIRECTORY_NAME
        / SOURCE_DIRECTORY_NAME
        / APP_PACKAGE
        / "app-state.svelte.ts",
        HARNESS_ROOT / IMPLEMENTATION_DIRECTORY_NAME / CLAUDE_CODE_PACKAGE / "launcher.py",
        HARNESS_ROOT / IMPLEMENTATION_DIRECTORY_NAME / CODEX_PACKAGE / "launcher.py",
    )
    assert not any("continue_latest" in path.read_text(encoding=TEXT_ENCODING) for path in launch_files)
    session_browser = (
        DASHBOARD_ROOT / FRONTEND_DIRECTORY_NAME / SOURCE_DIRECTORY_NAME / API_PACKAGE / "session-stream.ts"
    ).read_text(encoding=TEXT_ENCODING)
    assert "stream.onerror" not in session_browser
    assert "SES_RECONNECT" not in session_browser


def test_harness_packages_are_only_inert_package() -> None:
    """A harness package's `__init__.py` never runs anything.

    Discovery imports `<harness>/plugin.py` directly, so an `__init__` that did
    work would make merely NAMING a harness (a test, an audit CLI) pay for it —
    and would run before the descriptor the registry validates. `harness/impl/
    __init__.py` is exempt: it IS the discovery door, the twin of
    `terminal/impl/__init__.py`.
    """
    for package_path in (
        HARNESS_ROOT / IMPLEMENTATION_DIRECTORY_NAME / CLAUDE_CODE_PACKAGE / "__init__.py",
        HARNESS_ROOT / IMPLEMENTATION_DIRECTORY_NAME / CODEX_PACKAGE / "__init__.py",
    ):
        tree = standard_dependencies.ast.parse(package_path.read_text(encoding=TEXT_ENCODING))
        executable_nodes = [
            node
            for node in tree.body
            if not (
                isinstance(node, standard_dependencies.ast.Expr)
                and isinstance(node.value, standard_dependencies.ast.Constant)
                and isinstance(node.value.value, str)
            )
        ]
        assert not executable_nodes


def test_legacy_dashboard_semantic_readers() -> None:
    """Verify legacy dashboard semantic readers and handlers are deleted."""
    for directory in ("read", "control"):
        assert not list((DASHBOARD_ROOT / directory).glob(PYTHON_FILE_PATTERN))
    removed_paths = (
        DASHBOARD_ROOT / "http",
        ROOT / DASHBOARD_PACKAGE / "server.py",
        HARNESS_ROOT / IMPLEMENTATION_DIRECTORY_NAME / "host.py",
        ROOT / HARNESS_PACKAGE / IMPLEMENTATION_DIRECTORY_NAME / CLAUDE_CODE_PACKAGE / "hostctl.py",
        ROOT / HARNESS_PACKAGE / IMPLEMENTATION_DIRECTORY_NAME / CODEX_PACKAGE / "hostctl.py",
    )
    assert all(not path.exists() for path in removed_paths)
    assert not list((ROOT / DASHBOARD_PACKAGE / "ext").rglob(PYTHON_FILE_PATTERN))
    assert not list((ROOT / DASHBOARD_PACKAGE / "opshtml").glob(PYTHON_FILE_PATTERN))


def test_descriptor_discovery_does_not_load() -> None:
    """Verify descriptor discovery does not load legacy semantic stores."""
    program = (
        "\nimport sys\nfrom harness.impl.discovery import "
        "installed\ninstalled()\nforbidden = {'core.ops', 'core.state', "
        "'core.sessionapi', 'harness.impl.host'}\nloaded = "
        "sorted(forbidden.intersection(sys.modules))\nif loaded:\n    raise "
        "SystemExit(','.join(loaded))\n"
    )
    result = standard_dependencies.subprocess.run(
        [project_dependencies.sys.executable, "-c", program],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
