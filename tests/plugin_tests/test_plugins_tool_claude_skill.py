# Copyright (c) 2026 Zhambyl Yermagambet
"""Claude skill and web tool tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.event_resource import (
    SkillFinished,
    SkillStarted,
    WebFetched,
    WorktreeChanged,
)
from harness.impl.claude_code.canonical.translator import ClaudeCanonicalTranslator
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.support_events import payloads
from tests.plugin_tests.support_values import JsonValue, structured_of, text_of
from tests.plugin_tests.tool_translation_support import translate_claude_hook

type CodexTranslationDecisionCase = tuple[dict[str, JsonValue], str]


if TYPE_CHECKING:
    from harness.models.raw_events import (
        TranslationResult,
    )


def test_claude_skill_and_web_and_worktree_tools() -> None:
    """Verify claude skill and web and worktree tools have their own facts.

    Four tool families that used to be one generic operation, each now saying
        what it actually is. A skill has a life (it runs, it answers); a fetch and a
        worktree move do not — they are one fact at result time.
    """
    translator = ClaudeCanonicalTranslator()

    skill_start = translate_claude_hook(
        translator,
        {
            fixture.HOOK_EVENT_NAME_FIELD: fixture.PRE_TOOL_USE_HOOK,
            fixture.TOOL_USE_ID_FIELD: fixture.SKILL_ONE,
            fixture.TOOL_NAME_FIELD: fixture.SKILL_TOOL,
            fixture.TOOL_INPUT_FIELD: {fixture.SKILL_ARGUMENT: fixture.AUDIT_DEBUG},
        },
        "skill-start",
    )
    skill_finish = translate_claude_hook(
        translator,
        {
            fixture.HOOK_EVENT_NAME_FIELD: fixture.POST_TOOL_USE_HOOK,
            fixture.TOOL_USE_ID_FIELD: fixture.SKILL_ONE,
            fixture.TOOL_NAME_FIELD: fixture.SKILL_TOOL,
            fixture.TOOL_INPUT_FIELD: {fixture.SKILL_ARGUMENT: fixture.AUDIT_DEBUG},
            fixture.TOOL_RESPONSE_FIELD: "the skill's report",
        },
        "skill-finish",
    )
    fetched = translate_claude_hook(
        translator,
        {
            fixture.HOOK_EVENT_NAME_FIELD: fixture.POST_TOOL_USE_HOOK,
            fixture.TOOL_USE_ID_FIELD: "fetch-one",
            fixture.TOOL_NAME_FIELD: "WebFetch",
            fixture.TOOL_INPUT_FIELD: {fixture.URL_FIELD: "https://example.dev/docs"},
            fixture.TOOL_RESPONSE_FIELD: {
                "bytes": 8,
                fixture.CODE: 200,
                "codeText": "OK",
                fixture.RESULT: "the page",
                fixture.DURATION_MS_FIELD: 10,
                fixture.URL_FIELD: "https://example.dev/docs",
            },
        },
        "fetch",
    )
    entered = translate_claude_hook(
        translator,
        {
            fixture.HOOK_EVENT_NAME_FIELD: fixture.POST_TOOL_USE_HOOK,
            fixture.TOOL_USE_ID_FIELD: "worktree-one",
            fixture.TOOL_NAME_FIELD: "EnterWorktree",
            fixture.TOOL_INPUT_FIELD: {"branch": "wip"},
            fixture.TOOL_RESPONSE_FIELD: "entered",
        },
        "worktree",
    )

    _assert_claude_skill(skill_start, skill_finish)
    _assert_claude_fetch(fetched)
    _assert_claude_worktree(entered)


def _assert_claude_skill(
    skill_start: TranslationResult,
    skill_finish: TranslationResult,
) -> None:
    """Verify the Claude skill lifecycle."""
    started = payloads(skill_start, SkillStarted)[0].payload
    assert (started.skill_id, started.name) == (fixture.SKILL_ONE, fixture.AUDIT_DEBUG)
    # Claude collapses a Skill call's input to the bare name, so there is nothing
    # left to show as arguments.
    assert started.arguments is None
    assert text_of(payloads(skill_finish, SkillFinished)[0].payload.result) == "the skill's report"


def _assert_claude_fetch(fetched: TranslationResult) -> None:
    """Verify the Claude web fetch fact."""
    payload = payloads(fetched, WebFetched)[0].payload
    assert payload.url == "https://example.dev/docs"
    assert text_of(payload.result) == "the page"


def _assert_claude_worktree(entered: TranslationResult) -> None:
    """Verify the Claude worktree fact."""
    payload = payloads(entered, WorktreeChanged)[0].payload
    # No harness exposes a worktree path, so the call's own arguments ride along
    # rather than a parsed field that would always be empty.
    assert payload.action == "entered"
    assert structured_of(payload.arguments).field("branch") == "wip"
