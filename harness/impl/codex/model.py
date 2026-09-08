# Copyright (c) 2026 Zhambyl Yermagambet
"""The closed model vocabulary reported by Codex."""

from enum import StrEnum


class CodexModel(StrEnum):
    """Represent codex model."""

    GPT_SIX_ASTRA = "gpt-6-astra"
    GPT_FIVE_SIX_SOL = "gpt-5.6-sol"
    GPT_FIVE_SIX_TERRA = "gpt-5.6-terra"
    GPT_FIVE_SIX_LUNA = "gpt-5.6-luna"
    GPT_FIVE_FIVE = "gpt-5.5"
    GPT_FIVE_FOUR = "gpt-5.4"
    GPT_FIVE_FOUR_MINI = "gpt-5.4-mini"
    GPT_FIVE_THREE_CODEX_SPARK = "gpt-5.3-codex-spark"


CODEX_MODELS = (
    CodexModel.GPT_FIVE_SIX_SOL,
    CodexModel.GPT_FIVE_SIX_TERRA,
    CodexModel.GPT_FIVE_SIX_LUNA,
    CodexModel.GPT_FIVE_FIVE,
    CodexModel.GPT_FIVE_FOUR,
    CodexModel.GPT_FIVE_FOUR_MINI,
    CodexModel.GPT_FIVE_THREE_CODEX_SPARK,
    CodexModel.GPT_SIX_ASTRA,
)


class CodexEffort(StrEnum):
    """Represent codex effort."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"
    MAX = "max"
    ULTRA = "ultra"


class BaseInstructionsSourceType(StrEnum):
    """Represent base instructions source type."""

    MODEL = "model"
