# Copyright (c) 2026 Zhambyl Yermagambet
"""Start real plan work through one harness-neutral test interface."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from http import HTTPStatus
from typing import TYPE_CHECKING

from api.sessiondata.models.entry import MessageBodyResponse
from tests.e2e.testkit.references import PlanRef, SessionSpec, TurnRef
from tests.e2e.testkit.turns import matches_final_answer

if TYPE_CHECKING:
    from api.sessiondata.models.entry import EntryResponse
    from sdk.client import ActionReceipt, BaqylauClient, SessionRef
    from sdk.state import PlanState, SessionSnapshot


@dataclass(frozen=True)
class PlanAnswerExpectation:
    """Describe the final answer after a plan."""

    after_cursor: int
    text: str
    name: str
    timeout: float


def plan_state(snapshot: SessionSnapshot, reference: PlanRef) -> PlanState:
    """Find the unique plan state for a reference.

    Returns:
        The plan with the reference's attention identity.

    Raises:
        AssertionError: If the snapshot does not contain exactly one matching plan.

    """
    found = [plan_state for plan_state in snapshot.plans() if plan_state.attention_id == reference.attention_id]
    if len(found) != 1:
        message = f"plan attention {reference.attention_id!r} has {len(found)} matches"
        raise AssertionError(
            message,
        )
    return found[0]


def _matches_plan_answer(
    entry: EntryResponse,
    actor_id: str,
    after_cursor: int,
    text: str,
) -> bool:
    if entry.cursor <= after_cursor or entry.actor_id != actor_id:
        return False
    if not isinstance(entry.body, MessageBodyResponse):
        return False
    if entry.body.role != "assistant" or entry.body.phase != "end_turn":
        return False
    return matches_final_answer(entry.body.content.text, text)


def _has_exact_plan_answer(
    snapshot: SessionSnapshot,
    reference: PlanRef,
    expectation: PlanAnswerExpectation,
) -> bool | None:
    state = plan_state(snapshot, reference)
    answers = [
        entry
        for entry in snapshot.entries
        if _matches_plan_answer(
            entry,
            state.actor_id,
            expectation.after_cursor,
            expectation.text,
        )
    ]
    if len(answers) > 1:
        message = (
            f"plan {expectation.name!r} has {len(answers)} final answers "
            f"equal to {expectation.text!r}"
        )
        raise AssertionError(message)
    if not answers:
        return None
    # Final text can arrive before the native turn ends. A new /plan command
    # sent in that gap becomes queued text instead of a mode change.
    answer = answers[0]
    if answer.turn_id is None or snapshot.turn_state(answer.turn_id) is None:
        return None
    return True


def wait_for_plan_answer(
    client: BaqylauClient,
    reference: PlanRef,
    expectation: PlanAnswerExpectation,
) -> None:
    """Process wait for plan answer."""
    client.sessions.watch(reference.session).wait(
        (
            f"plan {expectation.name!r} to be followed by final answer "
            f"{expectation.text!r}"
        ),
        partial(
            _has_exact_plan_answer,
            reference=reference,
            expectation=expectation,
        ),
        timeout=expectation.timeout,
    )


def _require_acknowledged(receipt: ActionReceipt, action: str) -> None:
    if receipt.status_code != HTTPStatus.OK or receipt.outcome.status not in {"sent", "queued"}:
        message = f"{action} action {receipt.request_id!r} was not accepted: {receipt.outcome}"
        raise AssertionError(message)


class PlanWorkDriver:
    """Represent plan work driver."""

    def __init__(self, client: BaqylauClient) -> None:
        """Initialize the object."""
        self._client = client

    def start(
        self,
        spec: SessionSpec,
        session: SessionRef,
        prompt: str,
    ) -> TurnRef:
        """Enter plan mode and send the planning prompt.

        Returns:
            A reference to the new turn with its expected prompt count.

        Raises:
            AssertionError: If the harness has no plan adapter or a command is not acknowledged.

        """
        native_prompt = prompt
        if spec.harness == "codex":
            # A canonical turn finish can precede the native composer by a few
            # frames. Verify that the TUI is ready before entering plan mode,
            # then verify it again before submitting the actual plan prompt.
            # Without these checks, both accepted writes can land during the
            # transition and Codex silently drops the second one.
            _require_acknowledged(
                self._client.sessions.send(
                    session,
                    "/plan",
                    replace_terminal_draft=True,
                ),
                "enter Codex plan mode",
            )
        elif spec.harness == "claude_code":
            native_prompt = (
                "Your first action must be an EnterPlanMode tool call. Do not "
                "send assistant text before it. "
                f"{prompt} "
                "Your final action must be exactly one ExitPlanMode tool call "
                "that proposes the plan; do not answer in prose instead."
            )
        else:
            message = f"harness {spec.harness!r} has no plan work adapter"
            raise AssertionError(message)

        before = self._client.sessions.snapshot(session)
        lead = before.lead()
        receipt = self._client.sessions.send(
            session,
            native_prompt,
            replace_terminal_draft=spec.harness == "codex",
        )
        _require_acknowledged(receipt, "start plan work")
        return TurnRef(
            session,
            native_prompt,
            receipt.cursor_before,
            lead.statistics.prompt_count + 1,
            actor_id=lead.actor_id,
        )
