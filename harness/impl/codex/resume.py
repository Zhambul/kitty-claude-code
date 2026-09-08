# Copyright (c) 2026 Zhambyl Yermagambet
"""Find native Codex resume commands in terminal windows."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from domain.ids import SessionId, WindowId
from harness.contract import HarnessResumeLocator
from harness.impl.codex.ids_session import session_id_from_codex
from harness.impl.codex.ids_session_types import CodexSessionId
from harness.models.session import (
    LocatedSession,
)

if TYPE_CHECKING:
    from terminal.models.values import WindowInfo, WindowProcess


class CodexResumeLocator(HarnessResumeLocator):
    """Represent codex resume locator."""

    @override
    def locate(
        self,
        windows: tuple[WindowInfo, ...],
    ) -> tuple[LocatedSession, ...]:
        """Return the locate.

        Returns:
            Locate.

        """
        located: list[LocatedSession] = []
        located_ids: set[SessionId] = set()
        for window in windows:
            for process in window.processes:
                match = _located_session(window, process)
                if match is not None and match.session_id not in located_ids:
                    located.append(match)
                    located_ids.add(match.session_id)
        return tuple(located)


def _located_session(window_info: WindowInfo, window_process: WindowProcess) -> LocatedSession | None:
    native_session_id = _resumed_session(window_process.command)
    if native_session_id is None:
        return None
    return LocatedSession(
        session_id_from_codex(native_session_id),
        WindowId(str(window_info.window_id)),
    )


def _resumed_session(command: tuple[str, ...]) -> CodexSessionId | None:
    try:
        resume_target = _resume_target(command)
    except (ValueError, IndexError):
        return None
    if not resume_target or resume_target.startswith("-"):
        return None
    return CodexSessionId(resume_target)


def _resume_target(command: tuple[str, ...]) -> str:
    resume_index = command.index("resume")
    return command[resume_index + 1].strip()
