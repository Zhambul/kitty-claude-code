# Copyright (c) 2026 Zhambyl Yermagambet
"""Own event documents models."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from harness.impl.codex.canonical.record_event_messages import (
    AgentMessagePayload,
    AgentReasoningPayload,
    TurnAbortedPayload,
    UserMessagePayload,
    WebSearchEndPayload,
)
from harness.impl.codex.canonical.record_goal_payloads import EmptyPayload, ThreadGoalUpdatedPayload
from harness.impl.codex.canonical.record_item_registry import ItemCompletedPayload
from harness.impl.codex.canonical.record_rollout_headers import RolloutDocument
from harness.impl.codex.canonical.record_task_payloads import (
    TaskCompletePayload,
    TaskStartedPayload,
    ThreadSettingsAppliedPayload,
)
from harness.impl.codex.canonical.record_usage_payloads import TokenCountPayload

EventPayload = Annotated[
    TokenCountPayload
    | ThreadGoalUpdatedPayload
    | EmptyPayload
    | TaskStartedPayload
    | TaskCompletePayload
    | ThreadSettingsAppliedPayload
    | ItemCompletedPayload
    | TurnAbortedPayload
    | UserMessagePayload
    | AgentReasoningPayload
    | AgentMessagePayload
    | WebSearchEndPayload,
    Field(discriminator="type"),
]


class EventDocument(RolloutDocument[EventPayload]):
    """Represent event document."""

    type: Literal["event_msg"] = "event_msg"
