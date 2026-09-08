# Copyright (c) 2026 Zhambyl Yermagambet
"""The answer-question decision on the HTTP boundary."""

from enum import StrEnum


class AnswerDecisionBody(StrEnum):
    """Represent answer decision body."""

    ANSWER = "answer"
    DISCUSS = "discuss"
