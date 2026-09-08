# Copyright (c) 2026 Zhambyl Yermagambet
"""Import safety for the canonical runtime and direct plugin entries."""

from __future__ import annotations

import os
import subprocess  # noqa: S404 -- Check imports in a fresh Python process.
import sys
from pathlib import Path

REPOSITORY_ROOT = str(Path(__file__).resolve().parents[1])
IMPORT_TIMEOUT_SECONDS = 30

# The processes that used to be on this list — the hook entries, the two pane
# processes, the keybinding, the status-line shim — are stdlib-only clients now
# (`client/`), and tests/test_canonical_clients.py both forbids them any import of
# ours and RUNS each one. What is left here is the daemon's own import graph.
CANONICAL_MODULES = (
    "harness.impl",
    "api.server",
    "harness.impl.claude_code.plugin",
    "harness.impl.claude_code.hooks.gateway",
    "harness.impl.claude_code.otel.gateway",
    "harness.impl.claude_code.otel.launch",
    "harness.impl.codex.hooks.gateway",
    "harness.impl.claude_code.hooks.foreground",
    "harness.impl.codex.plugin",
)

IMPORT_PROGRAM = """
import importlib
import sys
import terminal.impl.resolution
module = sys.argv[1]
sys.argv = ['import-safety-test']
def fail(*arguments, **keywords):
    raise AssertionError('terminal resolved at import time')
terminal.impl.resolution.resolve = fail
importlib.import_module(module)
print('OK')
"""


def _environment() -> dict[str, str]:
    return {
        variable_name: variable_content
        for variable_name, variable_content in os.environ.items()
        if not variable_name.startswith(("KITTY_", "CLAUDE_"))
    }


def _run_import(program: str, module: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 -- Only fixed test programs and module names reach this call; no shell is used.
        [sys.executable, "-c", program, module],
        cwd=REPOSITORY_ROOT,
        env=_environment(),
        capture_output=True,
        text=True,
        timeout=IMPORT_TIMEOUT_SECONDS,
        check=False,
    )


def test_canon_modules_have_no_import_time() -> None:
    """Verify canonical modules have no import time terminal or argument work."""
    for module in CANONICAL_MODULES:
        result = _run_import(IMPORT_PROGRAM, module)
        assert result.returncode == 0, f"import of {module} failed:\n{result.stderr}"
        assert "OK" in result.stdout, f"import of {module} did not finish:\n{result.stderr}"


def test_hook_gateways_do_not_load_presentation() -> None:
    """Verify hook gateways do not load presentation or legacy semantic stores.

    The gateways run on the HTTP thread that records a delivery, so what they
        drag in is paid per hook — and a presenter is never part of recording one.

        (The hook PROCESSES this used to check are `client/` files now: they import
        nothing of ours at all, which is checked and MEASURED next door.)
    """
    program = """
import importlib
import sys
importlib.import_module(sys.argv[1])
forbidden = {
    'core.ops', 'core.state', 'core.sessionapi', 'core.mdrender',
    'api.sessiondata.mapper', 'engine.sessiondata.entries', 'pygments', 'wenmode',
}
loaded = sorted(forbidden.intersection(sys.modules))
if loaded:
    raise SystemExit(','.join(loaded))
"""
    for module in (
        "harness.impl.claude_code.hooks.gateway",
        "harness.impl.claude_code.otel.gateway",
        "harness.impl.codex.hooks.gateway",
    ):
        result = _run_import(program, module)
        assert result.returncode == 0, f"{module} loaded: {result.stderr}"


def test_audit_write_path_does_not_import_its() -> None:
    """A writer records audit; it never reads them back.

    The reader is the daemon's own tier — typed queries the dashboard renders — and
    the write API is reached from paths that run before the graph exists, so
    importing the reader from there buys a tier that cannot be used.
    (The daemon itself, `api.server`, legitimately holds both halves.)
    """
    program = """
import importlib
import sys
importlib.import_module(sys.argv[1])
if 'audit.read' in sys.modules:
    raise SystemExit('audit.read loaded')
"""
    writers = tuple(module for module in CANONICAL_MODULES if module != "api.server")
    for module in ("audit.record", *writers):
        result = _run_import(program, module)
        assert result.returncode == 0, f"{module}: {result.stderr}"
