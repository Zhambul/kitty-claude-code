# Copyright (c) 2026 Zhambyl Yermagambet
"""Checks for the E2E work adapter."""

from tests.e2e.testkit import work_delegation, work_names
from tests.e2e.testkit.work import _parallel_delegation_prompt
from tests.e2e.testkit.work_models import WorkRequest


def test_codex_worker_name_uses_v2_name_grammar() -> None:
    """Verify codex worker name uses the v2 name grammar."""
    assert work_names.worker_name("Greeting work 42!") == "e2e_greeting_work_42"


def test_parallel_work_prompt_keeps_native_tools() -> None:
    """Verify parallel work prompt keeps native tools behind the adapter."""
    requests = (
        WorkRequest("alpha work", "Reply alpha."),
        WorkRequest("beta work", "Reply beta."),
    )

    codex = _parallel_delegation_prompt("codex", requests)
    claude = _parallel_delegation_prompt("claude_code", requests)

    assert (
        codex.count("spawn_agent"),
        "multi_agent_v1__" not in codex,
        "Agent tool" in claude,
        "e2e_alpha_work" in codex,
        "WORK NAME: beta work" in claude,
        "Do not set name" in claude,
        work_names.assignment_actor_name("codex", "alpha work"),
        work_names.assignment_actor_name("claude_code", "alpha work"),
    ) == (1, True, True, True, True, True, "e2e alpha work", "e2e_alpha_work")


def test_codex_delegation_protects_explicit_skill() -> None:
    """Verify codex delegation protects an explicit skill mention from the lead."""
    prompt = work_delegation.delegation_prompt(
        "codex",
        WorkRequest("skill work", "$baqylau-e2e-communication"),
    )

    assert "$baqylau-e2e-communication" not in prompt
    assert r'"\u0024baqylau-e2e-communication"' in prompt
    assert "Decode WORK MESSAGE JSON as JSON" in prompt
