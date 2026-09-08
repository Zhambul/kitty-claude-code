# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from _model import (
    SessionModel,
    StatisticsRecord,
    TokenRecord,
)
from _render_styles import _STATISTIC_FIELDS


@dataclass(frozen=True)
class SessionStatistics:
    prompt_count: int
    shell_command_count: int
    failed_shell_command_count: int
    file_count: int
    lines_added: int
    lines_removed: int
    actor_message_count: int
    active_seconds: float
    tool_counts: Mapping[str, int]


def session_statistics(model: SessionModel) -> SessionStatistics:
    totals, tools = _statistic_totals(model)
    return SessionStatistics(
        **totals,
        active_seconds=_active_seconds(model),
        tool_counts=tools,
    )


def _statistic_totals(
    model: SessionModel,
) -> tuple[dict[str, int], dict[str, int]]:
    totals = dict.fromkeys(_STATISTIC_FIELDS, 0)
    tools: dict[str, int] = {}
    for actor in model.actors.values():
        _add_statistics(totals, tools, actor.statistics)
    return totals, tools


def _add_statistics(
    totals: dict[str, int],
    tools: dict[str, int],
    statistics: StatisticsRecord,
) -> None:
    for name in _STATISTIC_FIELDS:
        totals[name] += int(getattr(statistics, name))
    for row in statistics.tool_counts:
        tools[row.tool] = tools.get(row.tool, 0) + row.count


def _active_seconds(model: SessionModel) -> float:
    # The clock is the LEAD's, not a sum: two actors working at once are one
    # stretch of a person's time, and adding them would report more time than
    # the session has existed. It CARRIES FORWARD while the interval is open —
    # the daemon measured `active_seconds` when it built the frame, and frames
    # arrive on change, so a working session would otherwise show a clock that
    # sits still for minutes on a surface somebody is watching.
    lead = model.lead()
    lead_statistics = None if lead is None else lead.statistics
    if lead_statistics is None:
        return 0
    active_increment = model.elapsed_since_frame() if lead_statistics.active else 0
    return lead_statistics.active_seconds + active_increment


def session_usage(model: SessionModel) -> tuple[TokenRecord, float | None]:
    tokens = TokenRecord()
    cost: float | None = None
    for actor in model.actors.values():
        usage = actor.usage
        for name in TokenRecord.model_fields:
            _add_token_field(tokens, usage.tokens, name)
        if usage.cost_in_usd is not None:
            cost = (cost or 0) + float(usage.cost_in_usd)
    return tokens, cost


def _add_token_field(total_tokens: TokenRecord, actor_tokens: TokenRecord, name: str) -> None:
    total = getattr(total_tokens, name) + getattr(actor_tokens, name)
    setattr(total_tokens, name, total)
