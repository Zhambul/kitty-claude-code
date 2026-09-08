# Copyright (c) 2026 Zhambyl Yermagambet
"""Build single-work delegation prompts for E2E journeys."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tests.e2e.testkit import work_names
from tests.e2e.testkit.references import WorkerKind

if TYPE_CHECKING:
    from tests.e2e.testkit.work_models import WorkRequest

CODEX_HARNESS = "codex"
CLAUDE_CODE_HARNESS = "claude_code"


def delegation_prompt(harness: str, request: WorkRequest) -> str:
    """Return the prompt that delegates one work request.

    Returns:
        The prompt that delegates one work request.

    Raises:
        AssertionError: If subagent work is requested for an unsupported harness.

    """
    if request.worker_kind.value == "lead":
        return request.prompt
    prompt = request.prompt
    if request.attachments:
        paths = "\n".join(f"- {attachment.local_path}" for attachment in request.attachments)
        prompt = f"{prompt}\n\nThe files for this work are at these exact paths. Use only these paths:\n{paths}"
    name = work_names.worker_name(request.name)
    if harness == CODEX_HARNESS:
        return codex_prompt(name, prompt)
    if harness == CLAUDE_CODE_HARNESS:
        return claude_prompt(name, prompt, named=request.named)
    message = f"harness {harness!r} has no subagent work adapter"
    raise AssertionError(message)


def request_prompt(harness: str, request: WorkRequest) -> str:
    """Return the prompt for one work request.

    Returns:
        The prompt for one work request.

    """
    if request.worker_kind == WorkerKind.LEAD:
        return request.prompt
    return delegation_prompt(harness, request)


def codex_prompt(name: str, prompt: str) -> str:
    """Return the Codex single-work prompt.

    Returns:
        The Codex single-work prompt.

    """
    encoded_message = json.dumps(prompt).replace("$", r"\u0024")
    instruction = (
        "Use spawn_agent exactly once. "
        f"Set task_name to {name!r}. Decode WORK MESSAGE JSON as JSON and "
        "set message to the decoded string exactly. Do not do the work yourself. "
        "Do not use another tool. After the subagent starts, reply only with the word delegated."
    )
    return f"{instruction}\n\nWORK MESSAGE JSON\n{encoded_message}"


def claude_prompt(name: str, prompt: str, *, named: bool) -> str:
    """Return the Claude single-work prompt.

    Returns:
        The Claude single-work prompt.

    """
    name_instruction = f"Set name to {name!r}. " if named else "Do not set name. "
    instruction = (
        "Use the Agent tool exactly once. "
        f"Use description {name!r}. Give the subagent the exact work text between WORK START and WORK END. "
        f"Do not do the work yourself. {name_instruction}Do not use another tool. "
        "After the Agent tool returns, reply only with the word delegated."
    )
    return f"{instruction}\n\nWORK START\n{prompt}\nWORK END"
