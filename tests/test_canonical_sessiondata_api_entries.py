# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata api entries."""

from __future__ import annotations

import pytest

from api.sessiondata import mapper
from api.sessiondata.models import entry as entry_responses
from domain import (
    attention,
    content as domain_content,
    entries as domain_entries,
    entry_attention,
    entry_conversation,
    entry_lifecycle,
    entry_shells,
)

# Keep entry models separate from shared identity and outcome vocabulary.
# isort: split

from domain import (
    ids as domain_ids,
    messaging,
    outcomes,
)
from tests import canonical_sessiondata_api_entries as api_entries, canonical_sessiondata_api_values as api_values


def test_entry_carries_its_envelope_and_its_typed() -> None:
    """Verify an entry carries its envelope and its typed body."""
    response = mapper.entry(
        api_entries.entry(
            entry_conversation.MessageBody(
                domain_ids.MessageId(api_values.MESSAGE_ID_TEXT),
                messaging.MessageRole.ASSISTANT,
                messaging.MessagePhase.END_TURN,
                domain_content.TextContent("Done."),
            ),
        ),
    )
    assert (response.entry_id, response.type, response.cursor, response.turn_id) == (
        "event-one",
        "message",
        api_values.ENTRY_CURSOR,
        "turn-7",
    )
    assert response.occurred_at == pytest.approx(api_values.ENTRY_TIME)
    assert isinstance(response.body, entry_responses.MessageBodyResponse)
    assert response.body.role == "assistant"
    assert response.body.content.text == "Done."


def test_content_says_how_to_draw_itself() -> None:
    """Verify content says how to draw itself.

    Markdown or not is a fact the harness told us; a client that had to guess
        by role would render a plain-text tool result as markdown.
    """
    markdown = mapper.entry(
        api_entries.entry(
            entry_conversation.MessageBody(
                domain_ids.MessageId(api_values.MESSAGE_ID_TEXT),
                messaging.MessageRole.ASSISTANT,
                messaging.MessagePhase.END_TURN,
                domain_content.TextContent("**bold**", domain_content.MediaType.TEXT_MARKDOWN),
            ),
        ),
    )
    assert isinstance(markdown.body, entry_responses.MessageBodyResponse)
    assert markdown.body.content.media_type == "text/markdown"

    structured = mapper.entry(
        api_entries.entry(
            entry_shells.ShellStartedBody(
                domain_ids.ShellId("sh1"),
                domain_content.StructuredContent('{"b":2,"a":1}'),
                outcomes.ExecutionMode.FOREGROUND,
            ),
        ),
    )
    assert isinstance(structured.body, entry_responses.ShellStartedBodyResponse)
    # A document in a shape we do not define is laid out as the text a person
    # reads — the only thing a client can do with it.
    assert structured.body.command.media_type == "text/plain"
    assert '"a": 1' in structured.body.command.text


def test_question_entry_offers_labels_and_nothing() -> None:
    """Verify a question entry offers labels and nothing else.

    The label IS the value: both harnesses answer with the label they were
        shown, so a second spelling was a mapping every client had to keep.
    """
    response = mapper.entry(
        api_entries.entry(
            entry_attention.QuestionAskedBody(
                domain_ids.AttentionId("att-3"),
                (
                    attention.AttentionPrompt(
                        prompt_id=domain_ids.QuestionId("q1"),
                        title="Permissions",
                        prompt="Allow Bash?",
                        multiple=False,
                        choices=(attention.AttentionChoice("Yes", "go ahead"), attention.AttentionChoice("No", None)),
                    ),
                ),
            ),
        ),
    )
    assert isinstance(response.body, entry_responses.QuestionAskedBodyResponse)
    question = response.body.questions[0]
    assert (question.question_id, question.question) == ("q1", "Allow Bash?")
    assert [choice.label for choice in question.choices] == ["Yes", "No"]
    assert "value" not in response.model_dump_json()


def test_every_entry_kind_has_a_wire_shape() -> None:
    """Verify every entry kind has a wire shape.

    Exhaustiveness, checked rather than trusted: an entry kind the api layer
        never decided how to expose would otherwise reach a client as `{}`.
    """
    unmapped = []
    for name, body_type in domain_entries.BODY_TYPES.items():
        try:
            mapper.entry_body(api_entries.sample_body(body_type))
        except TypeError:
            unmapped.append(name)
    assert unmapped == []


def test_compacted_context_crosses_http_boundary() -> None:
    """Verify compacted context crosses the HTTP boundary."""
    response = mapper.entry_body(
        entry_lifecycle.CompactionFinishedBody(
            api_values.ACTOR_CONTEXT_USED_TOKENS,
            api_values.COMPACTION_RESULT_TOKENS,
            domain_content.TextContent("The retained compacted context"),
        ),
    )

    assert isinstance(response, entry_responses.CompactionFinishedBodyResponse)
    assert response.context is not None
    assert response.context.text == "The retained compacted context"
