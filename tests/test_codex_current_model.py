# Copyright (c) 2026 Zhambyl Yermagambet
"""Check the model name present in current Codex records."""

from harness.impl.codex.canonical.record_turn_payloads import TurnContextPayload
from harness.impl.codex.model import CODEX_MODELS, CodexModel


def test_current_codex_model_is_accepted() -> None:
    """Accept the model in both direct and collaboration settings."""
    payload = TurnContextPayload.model_validate({
        "model": "gpt-6-astra",
        "collaboration_mode": {
            "mode": "default",
            "settings": {"model": "gpt-6-astra", "reasoning_effort": "xhigh"},
        },
    })
    assert payload.model == CodexModel.GPT_SIX_ASTRA
    assert payload.collaboration_mode is not None
    assert payload.collaboration_mode.settings is not None
    assert payload.collaboration_mode.settings.model == CodexModel.GPT_SIX_ASTRA
    assert payload.model in CODEX_MODELS
