# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test architecture harness."""

from __future__ import annotations

from tests import (
    architecture_packages,
    architecture_project_dependencies as project_dependencies,
    architecture_test_adapters,
    architecture_test_files,
    architecture_test_paths,
    architecture_test_providers,
    architecture_test_syntax,
    architecture_test_terminals,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
BIN_DIRECTORY_NAME = "bin"
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
DOMAIN_PACKAGE = "domain"
REPOSITORY_PACKAGE = "repository"
CORE_PACKAGE = "core"
AUDIT_PACKAGE = "audit"
IMPLEMENTATION_DIRECTORY_NAME = "impl"
HARNESS_PACKAGE = "harness"
API_PACKAGE = "api"
DASHBOARD_PACKAGE = "dashboard"
ENGINE_PACKAGE = "engine"
TERMINAL_PACKAGE = "terminal"
HARNESS_ROOT = ROOT / HARNESS_PACKAGE
API_ROOT = ROOT / API_PACKAGE
DASHBOARD_ROOT = ROOT / DASHBOARD_PACKAGE
HARNESS_IMPLEMENTATION_ROOT = HARNESS_ROOT / IMPLEMENTATION_DIRECTORY_NAME
CLAUDE_CODE_PACKAGE = "claude_code"
CLAUDE_CODE_ROOT = HARNESS_IMPLEMENTATION_ROOT / CLAUDE_CODE_PACKAGE
DASHBOARD_CLI_PATH = "dashboard/cli.py"
OUR_PACKAGES = architecture_packages.owned_packages()
API_CONSUMERS = (project_dependencies.Path("dashboard/cli_server.py"),)
API_CONSUMER_PACKAGES = ("sdk",)


def test_terminal_tier_imports_no_concrete() -> None:
    """Verify the terminal tier imports no concrete harness."""
    architecture_test_files.assert_imports(
        TERMINAL_PACKAGE,
        {CORE_PACKAGE, AUDIT_PACKAGE, DOMAIN_PACKAGE, ENGINE_PACKAGE, REPOSITORY_PACKAGE, TERMINAL_PACKAGE},
        allowed_modules=frozenset(("harness.contract", "harness.models")),
    )


def test_shared_code_imports_no_concrete_plugin() -> None:
    """Verify shared code imports no concrete plugin descriptor."""
    importers = []
    for path in ROOT.rglob(PYTHON_FILE_PATTERN):
        if any(part in {".git", ".claude", ".venv", "tests"} for part in path.parts):
            continue
        text = path.read_text(encoding=TEXT_ENCODING)
        if "harness.impl.claude_code.plugin" in text or "harness.impl.codex.plugin" in text:
            importers.append(path.relative_to(ROOT).as_posix())
    assert not importers


def test_no_process_outside_daemon_lives_inside() -> None:
    """Every program the daemon does not own is a file in `client/` (R1).

    They used to live in five packages and sixteen files — a published wrapper
    beside its implementation beside the daemon-side code it POSTs to — which is
    why "is this file a client?" had no mechanical answer and no rule about one
    could be enforced. The rules themselves are in
    tests/test_canonical_clients.py; this is the absence half.

    The `bin/` directories those published paths lived in are gone too: external
    configuration names `client/` directly now. During the migration they were
    symlinks into it, which is how sessions that had already captured the old
    paths kept delivering.
    """
    gone = (
        "harness/impl/claude_code/hooks/entry.py",
        "harness/impl/claude_code/hooks/statusline.py",
        "harness/impl/claude_code/otel/receiver.py",
        "harness/impl/codex/hooks/entry.py",
        "harness/hooks/client.py",
        "core/daemon/client.py",
        "terminal/panes/client.py",
        "terminal/panes/mirror_process.py",
        "terminal/panes/scoreboard_process.py",
    )
    assert not any((ROOT / name).exists() for name in gone)
    for directory in ("harness/impl/claude_code/bin", "harness/impl/codex/bin", "terminal/bin"):
        assert not (ROOT / directory).exists(), f"{directory} is back"


def test_harness_hook_and_pane_entries_do_not() -> None:
    """Verify harness hook and pane entries do not come back to bin."""
    forbidden_entries = {
        "claude-hook.py",
        "claude-codex-hook.py",
        "claude-codex-session.py",
        "claude-split.py",
        "claude-mirror.py",
        "claude-scorebar.py",
        "claude-cmd-pre.py",
        "claude-copy.py",
        "claude-dashboard.py",
        "claude-audit.py",
        "claude-otlp-launch.py",
        "claude-otlp-receiver.py",
        "claude-statusline.py",
    }
    assert not forbidden_entries.intersection(path.name for path in (ROOT / BIN_DIRECTORY_NAME).iterdir())
    assert not (CLAUDE_CODE_ROOT / "split.py").exists()
    assert not architecture_test_paths.claude_bin_entries()


def test_every_route_answers_with_model_api_layer() -> None:
    """Verify each route names a response model from the API layer."""
    assert not architecture_test_adapters.outside_route_models()


def test_no_response_anywhere_is_hand_built() -> None:
    """One encoder, and it is the models'.

    `JSONResponse` takes any object at all and reflects it onto the wire, which
    is how a route came to answer with a shape its own `response_model` did not
    describe — FastAPI validates nothing it did not serialize itself. It is
    banned outright (ruff's TID251 says so too, so the failure lands at lint
    time), and so is the `json` module inside api/: an error body, an SSE frame
    and a route's reply are all a model, serialized by pydantic.

    The dashboard's `json_ready` — a second encoder that walked dataclass trees
    into dicts — is gone with them.
    """
    offenders = [
        offender
        for path in sorted(API_ROOT.rglob(PYTHON_FILE_PATTERN))
        for offender in architecture_test_providers.response_encoder_offenders(path)
    ]
    assert not offenders
    assert not (DASHBOARD_ROOT / "render" / "serialize.py").exists()
    assert not any(

            "JSONResponse" in path.read_text(encoding=TEXT_ENCODING)
            for package in OUR_PACKAGES
            for path in (ROOT / package).rglob(PYTHON_FILE_PATTERN)

    )


def test_nothing_below_api_layer_knows_it_exists() -> None:
    """Verify nothing below the api layer knows it exists.

    The direction is one-way: api/ maps the services' objects onto the wire,
        and no service, projection, harness or renderer has ever heard of a request.

        Enforced because the api DTO layer only means anything while it holds: the
        moment a service imports a response model, the model stops being the api
        layer's own statement about the wire and becomes shared vocabulary again —
        which is exactly the coupling the DTOs were introduced to break.
    """
    reaching = [
        f"{path.relative_to(ROOT)} imports {imported}"
        for package in OUR_PACKAGES
        if package != API_PACKAGE
        for path, imported in architecture_test_terminals.imports_under(package)
        if (imported == API_PACKAGE or imported.startswith("api."))
        and package not in API_CONSUMER_PACKAGES
        and (path.relative_to(ROOT) not in API_CONSUMERS)
    ]
    assert not reaching
    assert any(
        (
            imported == API_PACKAGE or imported.startswith("api.")
                for _path, imported in architecture_test_syntax.imports_under_path(DASHBOARD_ROOT / "cli_server.py")
        ),
    )
