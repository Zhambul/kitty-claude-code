# Copyright (c) 2026 Zhambyl Yermagambet
"""Closed roles and phases for session participants and messages."""

from enum import StrEnum


class ActorRole(StrEnum):
    """Identify an actor's relationship to the lead actor."""

    LEAD = "lead"
    CHILD = "child"
    TEAMMATE = "teammate"
    SIDECAR = "sidecar"


class MessageRole(StrEnum):
    """Identify who sent a canonical message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    PEER = "peer"
    PARENT = "parent"


class MessagePhase(StrEnum):
    """Identify a message's position in an agent turn."""

    PROMPT = "prompt"
    INTERMEDIATE = "intermediate"
    END_TURN = "end_turn"
    SYNTHETIC = "synthetic"
    RECAP = "recap"
