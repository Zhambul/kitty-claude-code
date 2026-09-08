# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the session data module."""

# One session's aggregate, as both frontends receive it.
#
# Everything actor-specific sits on the actor, because that is where the
# harnesses report it: a session with a lead and three subagents has four
# models, four statuses and four scoreboards, and one of each on the session
# would have to pick a winner.

from pydantic import BaseModel

from api.common.models.values.account_reference import AccountReferenceResponse
from api.common.models.values.repository_status import RepositoryStatusResponse
from api.sessiondata.models.actor import ActorResponse
from domain.lifecycle import LifecycleState
from domain.work_state import GoalState, TaskState


class GoalResponse(BaseModel):
    """Represent goal response."""

    objective: str | None
    state: GoalState
    reason: str | None
    completed: bool


class TaskResponse(BaseModel):
    """Represent task response."""

    task_id: str
    subject: str
    description: str | None
    state: TaskState
    owner_actor_id: str | None


class SessionResponse(BaseModel):
    """The session's own FACTS — everything about it that a stored event said.

    Nothing read-time is in here, and that is what lets an SSE frame carry this
    same shape: a frame is what the read model committed, and a client that
    applied one would otherwise clobber the world's state (see
    `SessionDataResponse.live`) with an absent field.
    """

    session_id: str
    harness: str
    title: str | None
    state: LifecycleState
    working_directory: str
    started_at: float | None
    finished_at: float | None
    account: AccountReferenceResponse | None
    lead_actor_id: str
    goal: GoalResponse | None
    tasks: tuple[TaskResponse, ...]
    continued_from: str | None = None


class SessionDataResponse(BaseModel):
    """The snapshot a client starts from.

    `cursor` is the session's high-water mark across its entries AND its
    aggregate revisions, read in the same transaction as the rows — so the
    entries page taken `at` it and the stream opened from it describe one
    instant. The aggregate's own revision would not do: it routinely lags the
    newest entry, and starting there re-sends what the client already has.
    """

    cursor: int
    session: SessionResponse
    actors: tuple[ActorResponse, ...]
    # The two READ-TIME truths, beside the facts rather than inside them:
    # whether a terminal window is attached right now, and what git says about
    # the working directory right now. Neither is event-sourced, neither is
    # stored, and neither can ride a stream frame — so they belong to the
    # ANSWER, not to the session.
    live: bool
    project_directory: str
    repository: RepositoryStatusResponse | None


class SessionDataListResponse(BaseModel):
    """Represent session data list response.

    The list view: every visible session, and the cursor to open the global
        stream from.

        `cursor` is the read model's high-water mark AT THE SAME READ as `sessions`
        — so a stream opened from it carries only what committed after this list,
        and never the backlog a stream opened from 0 would replay as if every
        session had just been born.
    """

    cursor: int
    sessions: tuple[SessionDataResponse, ...]
