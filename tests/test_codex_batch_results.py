# Copyright (c) 2026 Zhambyl Yermagambet
"""Do not guess which command owns an output block."""

import pytest

from harness.impl.codex.canonical.item_javascript_calls import js_tool_calls
from harness.impl.codex.canonical.record_actor_records import ToolBatchRecord
from harness.impl.codex.canonical.record_tool_records import ExecRecord, ExecResultRecord
from harness.impl.codex.canonical.translator_batch_results import command_results, ordered_command_results
from harness.impl.codex.ids_session_types import CodexCallId

CALL_ID = CodexCallId("batch")


@pytest.mark.parametrize(
    ("javascript", "expected"),
    [
        ('text(await tools.exec_command({cmd:"one"}));text(await tools.write_stdin({session_id:12}));', True),
        (
            (
                'const a=await tools.exec_command({cmd:"one"});'
                'const b=await tools.exec_command({cmd:"two"});text(b);text(a);'
            ),
            False,
        ),
        ('if(false){text(await tools.exec_command({cmd:"one"}));}', False),
        ('text(await tools.exec_command({cmd:"one"}));text("extra");', False),
        ("text(await tools.web__run({search_query:[]}));", False),
    ],
)
def test_result_order_must_be_explicit(javascript: str, *, expected: bool) -> None:
    """Accept only direct sequential command prints."""
    assert ordered_command_results(javascript, js_tool_calls(javascript)) is expected


@pytest.mark.parametrize(
    "output",
    ['{"output":"one"}', "{}\n{}", '{"output":"one"}\ntruncated', '{"output":null}\n{"output":null}'],
)
def test_incomplete_batch_has_no_assigned_results(output: str) -> None:
    """Reject partial or unrelated output blocks."""
    batch = ToolBatchRecord(
        call_id=CALL_ID,
        ordered_results=True,
        actions=(
            ExecRecord(cmd="one", call_id=CALL_ID),
            ExecRecord(cmd="two", call_id=CodexCallId("two")),
        ),
    )
    assert command_results(batch, ExecResultRecord(call_id=CALL_ID, exit=None, output=output)) == ()
