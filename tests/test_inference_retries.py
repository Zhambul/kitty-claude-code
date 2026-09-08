# Copyright (c) 2026 Zhambyl Yermagambet
"""Inference retry and fresh-session tests."""

from __future__ import annotations

import pytest

from inference import contract as inference_contract
from tests.inference_support import InferenceTerminal, factory

CODEX_EXECUTABLE = "codex"
MODEL_PROMPT = "name this"


def test_large_model_sizes_are_deliberately() -> None:
    """Verify large model sizes are deliberately unimplemented."""
    model_factory = factory(InferenceTerminal(()))
    with pytest.raises(NotImplementedError):
        model_factory.big()
    with pytest.raises(NotImplementedError):
        model_factory.mid()


def test_title_that_violates_requested_shape() -> None:
    """Verify a malformed title retries a fresh process."""
    terminal = InferenceTerminal(('{"title":"Too short"}', '{"title":"Fallback title has enough words"}'))
    response = factory(terminal).small().send(inference_contract.ModelPromptRequest(MODEL_PROMPT))
    assert response.text == "Fallback title has enough words"
    assert [launch.command[0] for launch in terminal.opened_tabs] == [CODEX_EXECUTABLE, CODEX_EXECUTABLE]


def test_transient_provider_failures_retry() -> None:
    """Verify transient provider failures retry the preferred provider."""
    terminal = InferenceTerminal((
        "rate limit exceeded",
        "model unavailable",
        '{"title":"Recovered preferred provider title"}',
    ))
    response = factory(terminal).small().send(inference_contract.ModelPromptRequest(MODEL_PROMPT))
    assert response.text == "Recovered preferred provider title"
    assert [launch.command[0] for launch in terminal.opened_tabs] == [CODEX_EXECUTABLE, "claude", CODEX_EXECUTABLE]


def test_each_send_opens_and_closes_a_new_session() -> None:
    """Verify each send opens and closes a new session."""
    terminal = InferenceTerminal(('{"title":"First fresh model title"}', '{"title":"Second fresh model title"}'))
    small = factory(terminal).small()
    small.send(inference_contract.ModelPromptRequest("first"))
    small.send(inference_contract.ModelPromptRequest("second"))
    assert terminal.closed_tabs == ["model-1", "model-2"]
    assert len(terminal.opened_tabs) == len(terminal.closed_tabs)


def test_valid_title_about_rate_limits_is_not() -> None:
    """Verify a valid rate-limit title is not a provider failure."""
    terminal = InferenceTerminal(('{"title":"Handle rate limit fallback"}',))
    response = factory(terminal).small().send(inference_contract.ModelPromptRequest(MODEL_PROMPT))
    assert response.text == "Handle rate limit fallback"
