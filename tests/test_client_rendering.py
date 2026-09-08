# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify terminal client architecture and behavior."""

from __future__ import annotations

import contextlib
import gzip
import json
import re
import subprocess  # noqa: S404 -- Test the local telemetry receiver as a child process.
from unittest.mock import Mock

import pytest

from core import clients
from harness.models.telemetry import (
    TELEMETRY_KIND_HEADER,
)
from tests import (
    client_test_models,
    client_test_render_support,
    client_test_servers,
    test_client_failures,
    test_client_loading,
)

CLAUDE_OTEL = "claude_otel.py"


STANDARD_RENDER_WIDTH = 80


SHELL_FINISH_TIME = 2.5


NARROW_RENDER_WIDTH = 30


SCOREBOARD_ELAPSED_SECONDS = 30.0


OTEL_RECEIVER_TIMEOUT_SECONDS = 30


CURSOR_FIELD = "cursor"


ACTOR_ID_FIELD = "actor_id"


LEAD_ACTOR_ID_TEXT = "lead"


CONTENT_FIELD = "content"


TEXT_FIELD = "text"


STATE_FIELD = "state"


SESSION_FIELD = "session"


SESSION_ID_FIELD = "session_id"


TEST_SESSION_ID_TEXT = "session-one"


LEAD_ACTOR_ID_FIELD = "lead_actor_id"


ACCOUNT_FIELD = "account"


ACTORS_FIELD = "actors"


LIVE_FIELD = "live"


TEXT_ENCODING = "utf-8"


RESIZE_AMOUNT = "9"


MODEL_MODULE_NAME = "_model"


RENDER_MODULE_NAME = "_render"


ITEMS_FIELD = "items"


SHELL_ID_FIELD = "shell_id"


SHELL_COMMAND = "make test"


SHELL_OUTPUT_TYPE = "shell_output"


STREAM_FIELD = "stream"


OUTPUT_STREAM = "output"


MODE_FIELD = "mode"


TASKS_FIELD = "tasks"


SIMPLE_SHELL_ID = "sh"


_INVISIBLE = re.compile(r"\x1b\[[0-9;]*[mHJ]|\x1b\]8;;[^\x1b]*\x1b\\")


def test_pane_folds_command_and_paints_it_at_its() -> None:
    """The fold and the painter, directly.

    Both are the client's now, and both are the kind of thing that is wrong for a
    week before anyone notices by eye: an output chunk that replaces instead of
    appending doubles a command's output, and a wrap that mis-counts a prefix
    silently eats a column.
    """
    model_module = test_client_loading.load_shared(MODEL_MODULE_NAME)
    render = test_client_loading.load_shared(RENDER_MODULE_NAME)

    model = model_module.SessionModel()
    model.apply_snapshot(
        {
            CURSOR_FIELD: 1,
            SESSION_FIELD: {
                SESSION_ID_FIELD: TEST_SESSION_ID_TEXT,
                LEAD_ACTOR_ID_FIELD: LEAD_ACTOR_ID_TEXT,
                ACCOUNT_FIELD: None,
            },
            ACTORS_FIELD: [{ACTOR_ID_FIELD: LEAD_ACTOR_ID_TEXT, "name": "Lead", "background": {}}],
            LIVE_FIELD: True,
        },
    )
    model.apply_page(
        {
            ITEMS_FIELD: [
                client_test_models.lead_pane_entry(
                    "1",
                    "shell_started",
                    {
                        SHELL_ID_FIELD: SIMPLE_SHELL_ID,
                        "command": {TEXT_FIELD: SHELL_COMMAND},
                        "execution": "foreground",
                    },
                ),
                client_test_models.lead_pane_entry(
                    "2",
                    SHELL_OUTPUT_TYPE,
                    {
                        SHELL_ID_FIELD: SIMPLE_SHELL_ID,
                        STREAM_FIELD: OUTPUT_STREAM,
                        MODE_FIELD: "append",
                        CONTENT_FIELD: {TEXT_FIELD: "first\n"},
                    },
                ),
                client_test_models.lead_pane_entry(
                    "3",
                    SHELL_OUTPUT_TYPE,
                    {
                        SHELL_ID_FIELD: SIMPLE_SHELL_ID,
                        STREAM_FIELD: OUTPUT_STREAM,
                        MODE_FIELD: "replace",
                        CONTENT_FIELD: {TEXT_FIELD: "the whole output, all of it, arriving at once\n"},
                    },
                ),
                client_test_models.lead_pane_entry(
                    "4",
                    "shell_finished",
                    {SHELL_ID_FIELD: SIMPLE_SHELL_ID, STATE_FIELD: "succeeded", "exit_code": 0},
                    occurred_at=SHELL_FINISH_TIME,
                ),
            ],
        },
    )
    # One block, not four: a command is its start, its chunks and its finish.
    folded = list(model.feed())
    # Replaced, not appended: the first chunk is gone rather than prefixed.
    assert (len(folded), folded[0].output) == (1, "the whole output, all of it, arriving at once\n")

    narrow = render.mirror(model, NARROW_RENDER_WIDTH)
    # The same model at two widths: the text is the same and the wrapping is not.
    assert (
        "the whole output, all of it, arriving at once" in render.mirror(model, 100)
        and narrow.count("\n") > render.mirror(model, 100).count("\n")
        and max(len(line) for line in _visible_rows(narrow)) <= NARROW_RENDER_WIDTH
    )
    # An overlapping page after a reconnect is applied twice and shows once.
    model.apply_page(
        {
            ITEMS_FIELD: [
                client_test_models.lead_pane_entry(
                    "2",
                    SHELL_OUTPUT_TYPE,
                    {
                        SHELL_ID_FIELD: SIMPLE_SHELL_ID,
                        STREAM_FIELD: OUTPUT_STREAM,
                        MODE_FIELD: "append",
                        CONTENT_FIELD: {TEXT_FIELD: "DOUBLED"},
                    },
                ),
            ],
        },
    )
    assert "DOUBLED" not in render.mirror(model, 100)

    # …and a prompt the harness DISCARDED stays gone across that same replay. Two
    # prompts naming one parent means the older is dead; deleting it without
    # remembering the decision would re-admit it as news on the next reconnect,
    # and it would stay, because the survivor that condemned it is applied once.
    # Asserted on the MODEL rather than on the paint, because the mirror hides
    # the lead's own conversation on purpose (it is a window on the work, not a
    # second copy of the chat you are having) — so a paint would say nothing
    # about whether the entry is held.
    model.apply_page({ITEMS_FIELD: client_test_render_support.discarded_parent_prompts()})
    assert client_test_render_support.pane_message_ids(model) == [RESIZE_AMOUNT]
    model.apply_page({ITEMS_FIELD: [client_test_render_support.pane_prompt("8", "parent-1")]})
    assert client_test_render_support.pane_message_ids(model) == [RESIZE_AMOUNT]


def _visible_rows(painted: str) -> list[str]:
    """Remove terminal escape sequences before checking row widths.

    Returns:
        The output rows without the recognized escape sequences.

    """
    return [_INVISIBLE.sub("", row) for row in painted.split("\n")]


def test_mirror_draws_task_list_as_state_rather() -> None:
    """The task list is AGGREGATE state, so it is a panel and not feed rows.

    It used to be a line per change, from a `task.changed` event — which meant a
    list of three items that moved twice read as six lines of history, none of
    them the current list. Now the pane draws what the list IS, and the only thing
    it keeps from the old form is that a completed item stops being work.
    """
    model_module = test_client_loading.load_shared(MODEL_MODULE_NAME)
    render = test_client_loading.load_shared(RENDER_MODULE_NAME)

    model = model_module.SessionModel()
    model.apply_snapshot(
        {
            CURSOR_FIELD: 1,
            LIVE_FIELD: True,
            ACTORS_FIELD: [],
            SESSION_FIELD: {
                SESSION_ID_FIELD: TEST_SESSION_ID_TEXT,
                LEAD_ACTOR_ID_FIELD: LEAD_ACTOR_ID_TEXT,
                ACCOUNT_FIELD: None,
                TASKS_FIELD: [
                    client_test_render_support.task_record("t1", "Rewrite the pane", "completed"),
                    client_test_render_support.task_record("t2", "Rework the e2e suite", "in_progress"),
                    client_test_render_support.task_record("t3", "Update the skill", "pending"),
                    client_test_render_support.task_record("t4", "Abandoned", "deleted"),
                ],
            },
        },
    )
    painted = "\n".join(_visible_rows(render.mirror(model, 60)))

    assert "tasks 1/3" in painted, "deleted tasks are not tasks, and done ones are a count"
    assert "Rework the e2e suite" in painted and "Update the skill" in painted
    assert "Rewrite the pane" not in painted, "a finished item is not work"
    assert "Abandoned" not in painted

    # A session with no list gets no panel at all — not an empty one.
    empty = model_module.SessionModel()
    empty.apply_snapshot(
        {
            CURSOR_FIELD: 1,
            LIVE_FIELD: True,
            ACTORS_FIELD: [],
            SESSION_FIELD: {
                SESSION_ID_FIELD: TEST_SESSION_ID_TEXT,
                LEAD_ACTOR_ID_FIELD: LEAD_ACTOR_ID_TEXT,
                ACCOUNT_FIELD: None,
                TASKS_FIELD: [],
            },
        },
    )
    assert TASKS_FIELD not in "\n".join(_visible_rows(render.mirror(empty, 60)))


@pytest.fixture
def monotonic_clock(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Set one controlled clock for client model frames and elapsed time.

    Returns:
        The model clock probe.

    """
    clock = Mock(return_value=0)
    for module_name in ("_model_session", "_model_session_state", "_model_session_feed"):
        monkeypatch.setattr(test_client_loading.load_shared(module_name), "time", Mock(monotonic=clock))
    return clock


def test_scoreboard_clock_moves_between_frames(monotonic_clock: Mock) -> None:
    """The clock the daemon used to redraw once a second, now the pane's.

    Frames arrive on CHANGE, and `active_seconds` is measured when the daemon
    builds one — so on a working session that says nothing for a minute, a pane
    that only ever showed the number it was sent would show a clock standing
    still. `active` is what makes carrying it forward honest: the pane adds its
    own elapsed time only while an interval is open, and an idle actor's clock
    stays exactly where the daemon left it.
    """
    model_module = test_client_loading.load_shared(MODEL_MODULE_NAME)
    render = test_client_loading.load_shared(RENDER_MODULE_NAME)

    working, render = client_test_render_support.scoreboard_with(model_module, render, active=True)
    assert "1m40s" in render.scoreboard(working, STANDARD_RENDER_WIDTH)
    monotonic_clock.return_value = SCOREBOARD_ELAPSED_SECONDS
    assert "2m10s" in render.scoreboard(working, STANDARD_RENDER_WIDTH)

    idle, render = client_test_render_support.scoreboard_with(model_module, render, active=False)
    monotonic_clock.return_value += SCOREBOARD_ELAPSED_SECONDS
    assert "1m40s" in render.scoreboard(idle, STANDARD_RENDER_WIDTH)


def _send_otlp_export(
    listen_port: int,
    export: bytes,
    cleanup: contextlib.ExitStack,
) -> tuple[int, bytes]:
    connection = test_client_failures.wait_for_receiver(listen_port)
    cleanup.callback(connection.close)
    connection.request(
        "POST",
        "/v1/metrics",
        gzip.compress(export),
        {"Content-Encoding": "gzip", "Content-Type": "application/json"},
    )
    response = connection.getresponse()
    return response.status, response.read()


def test_otlp_receiver_forwards_export(daemon: client_test_servers._Capture, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify the otlp receiver forwards an export and acknowledges it."""
    monkeypatch.setattr(clients, "PORT_NUMBER", daemon.port)
    listen_port = client_test_servers.free_port()
    export = json.dumps({"resourceMetrics": []}).encode()
    process = subprocess.Popen(  # noqa: S603 -- Run the fixed telemetry client and test arguments without a shell.
        clients.command(CLAUDE_OTEL, listen_port, OTEL_RECEIVER_TIMEOUT_SECONDS),
    )
    with contextlib.ExitStack() as cleanup:
        cleanup.callback(process.wait, timeout=10)
        cleanup.callback(process.terminate)
        # gzip too: Claude Code's exporter compresses, and being the endpoint is
        # what this process is for
        assert _send_otlp_export(listen_port, export, cleanup) == (200, b"{}")

    delivery = daemon.delivery("/telemetry")
    assert delivery.path == "/api/harnesses/claude_code/telemetry"
    assert delivery.headers[TELEMETRY_KIND_HEADER] == "otlp"
    assert delivery.body == export  # decompressed, unparsed
