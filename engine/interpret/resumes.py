# Copyright (c) 2026 Zhambyl Yermagambet
"""Discover native session resumes from terminal process data."""

from engine.interpret.dependencies import InterpreterDependencies
from harness.contract import HarnessPlugin, SessionResumeRecorder, TerminalWindows


def discover_resumes(
    interpreter_dependencies: InterpreterDependencies,
    terminal_windows: TerminalWindows,
) -> None:
    """Record all newly discovered native resumes."""
    terminal = interpreter_dependencies.runtime.terminal
    resume_recorder = interpreter_dependencies.runtime.resume_recorder
    if terminal is None or resume_recorder is None:
        return
    for plugin in interpreter_dependencies.services.harnesses.plugins():
        _discover_plugin_resumes(
            interpreter_dependencies,
            plugin,
            terminal_windows,
            resume_recorder,
        )


def _discover_plugin_resumes(
    interpreter_dependencies: InterpreterDependencies,
    harness_plugin: HarnessPlugin,
    terminal_windows: TerminalWindows,
    session_resume_recorder: SessionResumeRecorder,
) -> None:
    locator = harness_plugin.resume_locator
    if locator is None:
        return
    for located_session in locator.locate(terminal_windows):
        session = interpreter_dependencies.repositories.sessions.find(located_session.session_id)
        if session is None or session.terminal_window_id == located_session.window_id:
            continue
        session_resume_recorder.resumed(
            harness_plugin.harness_info.name,
            located_session.session_id,
            located_session.window_id,
        )
