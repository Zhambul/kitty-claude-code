# Copyright (c) 2026 Zhambyl Yermagambet
"""Item response content."""

from __future__ import annotations

from harness.impl.codex.canonical import (
    item_patterns,
    record_interaction_records,
    record_response_documents,
    record_response_parts,
    record_task_records,
    record_terminal_records,
    record_tool_records,
)
from harness.impl.codex.canonical.item_plan_exec import _exec_output_body
from harness.impl.codex.canonical.vocabulary import (
    empty_record,
    is_synthetic,
    loaded_skill_name,
    plan_body,
    strip_input_wrapper,
)
from harness.impl.codex.ids_session_types import CodexCallId


def _interrupted_output(text: str) -> bool:
    return text.strip().casefold().startswith("aborted by user after ")


def content_text(content: str | list[record_response_parts.ContentPart | str] | None) -> str:
    """Return the content text.

    A response_item content list -> its text. The items are usually
        {"type": "input_text"|"output_text", "text": …}; older versions (and the
        custom-tool outputs) sometimes hand a bare string instead, either for the
        whole field (caught above) or for one entry inside an otherwise-typed
        list (caught below).

    Returns:
        Content text.

    """
    if isinstance(content, str):
        return content.strip()
    parts: list[str] = []
    for part in content or ():
        if isinstance(part, str):
            parts.append(part)
        elif part.text is not None:
            parts.append(part.text)
    return "\n".join(parts).strip()


def _rsp_web_search_call(
    web_search_call_payload: record_response_parts.WebSearchCallPayload,
) -> record_tool_records.SearchRecord | None:
    action = web_search_call_payload.action
    query = "" if action is None else action.query
    return record_tool_records.SearchRecord(query=query) if query else None


def _rsp_function_call_output(
    function_call_output_payload: record_response_parts.FunctionCallOutputPayload,
) -> record_tool_records.ExecResultRecord:
    output = (
        function_call_output_payload.output
        if isinstance(function_call_output_payload.output, str)
        else content_text(function_call_output_payload.output)
    )
    exit_match = item_patterns.EXECUTION_EXIT_PATTERN.search(output[: item_patterns.EXECUTION_EXIT_SCAN_BYTES])
    return record_tool_records.ExecResultRecord(
        exit=exit_match.group(1) if exit_match else None,
        output=_exec_output_body(output),
        call_id=CodexCallId(function_call_output_payload.call_id or ""),
        interrupted=_interrupted_output(output),
    )


def _message_turn(message_payload: record_response_documents.MessagePayload) -> str:
    metadata = message_payload.internal_chat_message_metadata_passthrough
    if metadata is None:
        return ""
    return metadata.turn_id or ""


def _rsp_skill(
    message_payload: record_response_documents.MessagePayload,
    message_text: str,
    role: str,
) -> record_task_records.SkillRecord | None:
    skill_name = loaded_skill_name(message_text) if role == "user" else ""
    if not skill_name:
        return None
    return record_task_records.SkillRecord(
        name=skill_name,
        output=message_text,
        turn=_message_turn(message_payload),
    )


def _rsp_message(message_payload: record_response_documents.MessagePayload) -> record_terminal_records.RolloutRecord:
    # The response_item register (module header): the conversation as the
    # model API records it — assistant/user/developer, and the ONLY place a
    # post-abort or queued prompt appears. Deliberately NOT kind "message"/
    # "prompt": those are the event_msg register the mirror paints, and one
    # turn shows up in both.
    message_text = content_text(message_payload.content)
    if not message_text:
        return empty_record()
    role = (message_payload.role or "").strip()
    skill_record = _rsp_skill(message_payload, message_text, role)
    if skill_record is not None:
        return skill_record
    # A plan wrapper is the response-register copy of the structured Plan item.
    # The item-completed register has the stable plan ID and owns the canonical
    # plan. Mark this copy as covered so one native plan makes one card.
    if role == "assistant":
        plan = plan_body(message_text)
        if plan:
            return record_terminal_records.CoveredItemRecord()
    # role-aware synthetic on the RAW text (the `<tag>` is the signal), THEN unwrap
    # an INPUT wrapper so a kept `<task>` prompt reads as its inner text.
    synthetic = is_synthetic(message_text, role)
    # …carrying the assistant PHASE too (see events.PHASE_FINAL): this register is
    # the twin of the event_msg one, and the web's conversation read takes
    # whichever arrives first — so the fact that a reply is the turn's FINAL
    # ANSWER has to survive both spellings or it survives neither.
    return record_interaction_records.ChatRecord(
        role=role,
        text=strip_input_wrapper(message_text),
        synthetic=synthetic,
        phase=(message_payload.phase or "").strip(),
        turn=_message_turn(message_payload),
    )
