# Copyright (c) 2026 Zhambyl Yermagambet
"""Keep system wrappers separate from user input."""

import pytest

from harness.impl.codex.canonical import vocabulary


@pytest.mark.parametrize("text", [
    '<hook_prompt hook_run_id="stop:18:/workspace/hooks.json">Check the wiki.</hook_prompt>',
    "<hook_prompt hook_run_id='stop:18' source='hook'>Check the wiki.</hook_prompt>",
    '<hook_prompt hook_run_id="a>b">Check the wiki.</hook_prompt>',
    "<permissions instructions>Read only.</permissions instructions>",
    "<environment_context>Workspace</environment_context>",
])
def test_wrapper_is_system_text(text: str) -> None:
    """Recognize system wrappers with and without attributes."""
    assert vocabulary.is_synthetic(text, "user")


@pytest.mark.parametrize("text", [
    "Please explain <hook_prompt> tags.",
    "<task>Read the code.</task>",
    '<task source="parent">Read the code.</task>',
])
def test_user_input_is_not_system_text(text: str) -> None:
    """Keep user prose and subagent input as prompts."""
    assert not vocabulary.is_synthetic(text, "user")


def test_task_body_excludes_attributes() -> None:
    """Remove the complete opening tag from a subagent task."""
    assert vocabulary.strip_input_wrapper('<task source="parent">Read the code.</task>') == "Read the code."


def test_plan_body_excludes_attributes() -> None:
    """Remove the complete opening tag from a plan."""
    assert vocabulary.plan_body('<proposed_plan source="agent">Read the code.</proposed_plan>') == "Read the code."
