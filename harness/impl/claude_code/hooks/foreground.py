# Copyright (c) 2026 Zhambyl Yermagambet
"""Claude Code command output as recordable output-location directives."""

from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pydantic

from domain import event_shell, work_state
from harness.impl.claude_code import ids as claude_ids, shell
from harness.impl.claude_code.canonical import records

if TYPE_CHECKING:
    from domain.ids import SessionId, ShellId

CHUNK_SOURCE_TYPE = "foreground_output"
PRIVATE_DIRECTORY_MODE = 0o700
PRIVATE_FILE_MODE = 0o600

# Claude Code writes a background command's output to
# /tmp/claude-<uid>/<cwd-slug>/<session-id>/tasks/<taskId>.output. The slug rule
# is Claude's own, so the file is FOUND by its unique (session, task) pair
# rather than derived — a miss simply means nothing to watch.
BACKGROUND_OUTPUT_ROOT = tempfile.gettempdir()


@dataclass(frozen=True)
class PreparedForegroundCommand:
    """Represent prepared foreground command."""

    reply: bytes
    locations: tuple[event_shell.ShellOutputLocated, ...]

    @classmethod
    def fallback(
        cls,
        shell_arguments: records.ShellArguments,
        command: str,
        session_id: SessionId,
        shell_id: ShellId,
    ) -> PreparedForegroundCommand:
        """Prepare a command that copies output to a session-specific file.

        Returns:
            The hook reply and the directive to follow the output until the shell finishes.

        """
        source_path = cls._source_path(session_id, shell_id)
        Path(source_path).parent.mkdir(
            mode=PRIVATE_DIRECTORY_MODE,
            exist_ok=True,
            parents=True,
        )
        descriptor = os.open(
            source_path,
            os.O_WRONLY | os.O_CREAT | os.O_APPEND,
            PRIVATE_FILE_MODE,
        )
        os.close(descriptor)
        location = event_shell.ShellOutputLocated(
            shell_id=claude_ids.shell_id_from_claude_code(
                claude_ids.ClaudeCodeShellId(shell_id),
            ),
            source_path=source_path,
            chunk_source_type=CHUNK_SOURCE_TYPE,
            delete_source=True,
            initial_size=0,
            initial_modified_at=0,
            wait_for_source_change=False,
            until=work_state.ShellFollowUntil.SHELL_FINISHED,
        )
        return cls(
            HookReply.encode_command(
                shell_arguments,
                shell.copy_output_to(command, source_path),
            ),
            (location,),
        )

    @classmethod
    def _source_path(cls, session_id: SessionId, shell_id: ShellId) -> str:
        configured_directory = os.environ.get("CLAUDE_CONFIG_DIR")
        configuration_directory = Path(configured_directory) if configured_directory else Path("~/.claude").expanduser()
        session_identity = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
        shell_identity = hashlib.sha256(shell_id.encode("utf-8")).hexdigest()
        return str(
            configuration_directory / "baqylau" / "foreground" / session_identity / f"{shell_identity}.out",
        )


class HookSpecificOutput(pydantic.BaseModel):
    """Represent hook specific output."""

    model_config = pydantic.ConfigDict(frozen=True, populate_by_name=True)
    hook_event_name: str = pydantic.Field(alias="hookEventName")
    permission_decision: str = pydantic.Field(alias="permissionDecision")
    updated_input: records.ShellArguments = pydantic.Field(alias="updatedInput")


class HookReply(pydantic.BaseModel):
    """Represent hook reply."""

    model_config = pydantic.ConfigDict(frozen=True, populate_by_name=True)
    hook_specific_output: HookSpecificOutput = pydantic.Field(alias="hookSpecificOutput")

    @classmethod
    def encode_command(
        cls,
        shell_arguments: records.ShellArguments,
        command: str,
    ) -> bytes:
        """Encode a hook reply with an allowed replacement command.

        Returns:
            The JSON reply followed by a newline, encoded as bytes.

        """
        reply = cls(
            hookSpecificOutput=HookSpecificOutput(
                hookEventName="PreToolUse",
                permissionDecision="allow",
                updatedInput=records.ShellArguments(
                    command=command,
                    description=shell_arguments.description,
                    run_in_background=shell_arguments.run_in_background,
                    timeout=shell_arguments.timeout,
                ),
            ),
        )
        return f"{reply.model_dump_json(by_alias=True, exclude_none=True)}\n".encode()


class _ForegroundCommand:
    def __init__(self, hook_payload: records.HookPayload) -> None:
        self.hook_payload = hook_payload
        self.shell_arguments = hook_payload.shell_input()
        self.command = self.shell_arguments.command if isinstance(self.shell_arguments.command, str) else ""
        response = hook_payload.tool_response
        self.background_task_id = response.background_task_id if isinstance(response, records.ToolResponse) else None

    def background_output(self) -> event_shell.ShellOutputLocated | None:
        if not self.shell_arguments.run_in_background:
            return None
        native_session_id, call_id = self._native_ids(None)
        if not native_session_id or not call_id or not self.background_task_id:
            return None
        pattern = f"claude-*/*/{native_session_id}/tasks/{self.background_task_id}.output"
        matches = sorted(Path(BACKGROUND_OUTPUT_ROOT).glob(pattern))
        if not matches:
            return None
        return event_shell.ShellOutputLocated(
            shell_id=claude_ids.shell_id_from_claude_code_call(call_id),
            source_path=str(matches[0].resolve()),
            chunk_source_type=CHUNK_SOURCE_TYPE,
            delete_source=False,
            initial_size=0,
            initial_modified_at=0,
            wait_for_source_change=False,
            until=work_state.ShellFollowUntil.SESSION_FINISHED,
        )

    def redirected_locations(
        self,
        shell_follow_until: work_state.ShellFollowUntil,
    ) -> tuple[event_shell.ShellOutputLocated, ...]:
        if not self.command.strip():
            return ()
        _native_session_id, call_id = self._native_ids(
            "Claude Code shell tool has no session or command id",
        )
        shell_id = claude_ids.shell_id_from_claude_code_call(call_id)
        working_directory = self.hook_payload.cwd
        targets = shell.redirected_outputs(
            self.command,
            str(working_directory) if working_directory else None,
        )
        return tuple(self._redirected_location(target, shell_id, shell_follow_until) for target in targets)

    def prepare(self) -> PreparedForegroundCommand | None:
        if not self.command.strip() or self.shell_arguments.run_in_background:
            return None
        native_session_id, call_id = self._native_ids(
            "Claude Code foreground command has no session or command id",
        )
        shell_id = claude_ids.shell_id_from_claude_code_call(call_id)
        locations = self.redirected_locations(work_state.ShellFollowUntil.SHELL_FINISHED)
        if locations:
            return PreparedForegroundCommand(
                HookReply.encode_command(self.shell_arguments, self.command),
                locations,
            )
        return PreparedForegroundCommand.fallback(
            self.shell_arguments,
            self.command,
            claude_ids.session_id_from_claude_code(native_session_id),
            shell_id,
        )

    def _native_ids(
        self,
        error_message: str | None,
    ) -> tuple[claude_ids.ClaudeCodeSessionId, claude_ids.ClaudeCodeCallId]:
        native_session_id = claude_ids.ClaudeCodeSessionId(
            self.hook_payload.session_id or "",
        )
        call_id = claude_ids.ClaudeCodeCallId(self.hook_payload.tool_use_id or "")
        if error_message is not None and (not native_session_id or not call_id):
            raise ValueError(error_message)
        return native_session_id, call_id

    def _redirected_location(
        self,
        target: shell.RedirectedOutput,
        shell_id: ShellId,
        shell_follow_until: work_state.ShellFollowUntil,
    ) -> event_shell.ShellOutputLocated:
        try:
            source_status = Path(target.path).stat()
        except FileNotFoundError:
            initial_state = (0, 0)
        else:
            initial_state = (source_status.st_size, source_status.st_mtime_ns)
        return event_shell.ShellOutputLocated(
            shell_id=claude_ids.shell_id_from_claude_code(
                claude_ids.ClaudeCodeShellId(shell_id),
            ),
            source_path=target.path,
            chunk_source_type=CHUNK_SOURCE_TYPE,
            delete_source=False,
            initial_size=initial_state[0],
            initial_modified_at=initial_state[1],
            wait_for_source_change=target.append is False,
            until=shell_follow_until,
        )


def background_output(
    hook_payload: records.HookPayload,
) -> event_shell.ShellOutputLocated | None:
    """Return the background output.

    The output location of a background command's native output file.

        Background commands are not rewritten (Claude Code redirects their output
        itself), so the location becomes known at the PostToolUse that reports the
        task id. The native file is Claude Code's — never deleted by us — and the
        following ends with the session (or the lifetime cap), never with the
        command, whose launch reports "finished" while output keeps flowing.

    Returns:
        Background output.

    """
    return _ForegroundCommand(hook_payload).background_output()


def redirected_locations(
    hook_payload: records.HookPayload,
    shell_follow_until: work_state.ShellFollowUntil,
) -> tuple[event_shell.ShellOutputLocated, ...]:
    """Return every concrete file that receives this tool's output.

    Command validation raises ValueError if the session or command ID is absent.

    Returns:
        Every concrete file that receives this tool's output.

    """
    return _ForegroundCommand(hook_payload).redirected_locations(
        shell_follow_until,
    )


def prepare(
    hook_payload: records.HookPayload,
) -> PreparedForegroundCommand | None:
    """Rewrite one Bash command so its output lands in a readable file.

    The returned location is NOT applied here — the gateway records it as an
    output-location directive and the interpreter does the following. The
    gateway's only file act is creating the tee target, which the rewritten
    command itself requires.

    Command validation raises ValueError if the session or command ID is absent.

    Returns:
        The prepared foreground command.

    """
    return _ForegroundCommand(hook_payload).prepare()
