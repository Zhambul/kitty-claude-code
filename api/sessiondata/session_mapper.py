# Copyright (c) 2026 Zhambyl Yermagambet
"""Map session aggregate facts to API session responses."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from api.common.mapper import states, usage, values
from api.sessiondata.models import actor as actor_models, session_data as session_models

if TYPE_CHECKING:
    from api.sessiondata.models.session_data import SessionDataResponse
    from core.git_status import RepositoryStatus
    from domain import actor_state, session_state


def session_data(
    session_data: session_state.SessionData,
    *,
    live: bool,
    repository_status: RepositoryStatus | None,
    project_directory: str | None = None,
    now: float | None = None,
) -> SessionDataResponse:
    """Return the API response for one session aggregate.

    Returns:
        The API response for one session aggregate.

    """
    return session_models.SessionDataResponse(
        cursor=session_data.cursor,
        session=session(session_data.session),
        actors=tuple(actor(row, now=now) for row in session_data.actors),
        live=live,
        project_directory=(project_directory or session_data.session.working_directory),
        repository=states.maybe_repository_status(repository_status),
    )


def session(session_facts: session_state.SessionFacts) -> session_models.SessionResponse:
    """Return the API response for session facts.

    Returns:
        The API response for session facts.

    """
    return session_models.SessionResponse(
        session_id=str(session_facts.session_id),
        harness=session_facts.harness,
        title=session_facts.title,
        state=session_facts.state,
        working_directory=session_facts.working_directory,
        started_at=session_facts.started_at,
        finished_at=session_facts.finished_at,
        account=values.maybe_account_reference(session_facts.account),
        lead_actor_id=str(session_facts.lead_actor_id),
        continued_from=(None if session_facts.continued_from is None else str(session_facts.continued_from)),
        goal=(
            None
            if session_facts.goal is None
            else session_models.GoalResponse(
                objective=session_facts.goal.objective,
                state=session_facts.goal.state,
                reason=session_facts.goal.reason,
                completed=session_facts.goal.state == "completed",
            )
        ),
        tasks=tuple(
            session_models.TaskResponse(
                task_id=str(task.task_id),
                subject=task.subject,
                description=task.description,
                state=task.state,
                owner_actor_id=None if task.owner_actor_id is None else str(task.owner_actor_id),
            )
            for task in session_facts.tasks
        ),
    )


def actor(actor_facts: actor_state.ActorFacts, *, now: float | None = None) -> actor_models.ActorResponse:
    """Return the API response for actor facts.

    Returns:
        The API response for actor facts.

    """
    statistics = actor_facts.statistics
    current_time = time.time() if now is None else now
    open_interval = (
        0 if statistics.active_since_internal is None else max(0, current_time - statistics.active_since_internal)
    )
    return actor_models.ActorResponse(
        session_id=str(actor_facts.session_id),
        actor_id=str(actor_facts.actor_id),
        parent_actor_id=None if actor_facts.parent_actor_id is None else str(actor_facts.parent_actor_id),
        role=actor_facts.role,
        name=actor_facts.name,
        description=actor_facts.description,
        state=actor_facts.state,
        started_at=actor_facts.started_at,
        finished_at=actor_facts.finished_at,
        model=None if actor_facts.model is None else (actor_facts.model.display_name or actor_facts.model.name),
        effort=actor_facts.effort,
        status=actor_facts.status,
        usage=actor_models.ActorUsageResponse(
            tokens=usage.token_usage(actor_facts.usage.tokens),
            cost_in_usd=None if actor_facts.usage.cost_in_usd is None else str(actor_facts.usage.cost_in_usd),
        ),
        context=actor_models.ActorContextResponse(
            used_tokens=actor_facts.context.used_tokens,
            window_tokens=actor_facts.context.window_tokens,
            compacting=actor_facts.context.compacting,
        ),
        background=actor_models.ActorBackgroundResponse(
            running_shell_ids=tuple(str(shell_id) for shell_id in actor_facts.background.running_shell_ids),
            monitor_count=actor_facts.background.monitor_count,
            background_job_count=actor_facts.background.background_job_count,
        ),
        statistics=actor_models.ActorStatisticsResponse(
            prompt_count=statistics.prompt_count,
            shell_command_count=statistics.shell_command_count,
            failed_shell_command_count=statistics.failed_shell_command_count,
            file_count=statistics.file_count,
            lines_added=statistics.lines_added,
            lines_removed=statistics.lines_removed,
            actor_message_count=statistics.actor_message_count,
            tool_counts=tuple(
                actor_models.ToolCountResponse(tool=tool_count.tool, count=tool_count.count)
                for tool_count in statistics.tool_counts
            ),
            active_seconds=statistics.active_seconds + open_interval,
            active=statistics.active_since_internal is not None,
        ),
    )
