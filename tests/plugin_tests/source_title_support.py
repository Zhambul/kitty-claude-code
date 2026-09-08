# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for native title source tests."""

from dataclasses import dataclass
from pathlib import Path

import pytest

from domain import event_session, ids, work_state
from harness.impl.codex.canonical import title as codex_title
from harness.impl.codex.canonical.source_readers import (
    CodexTitleRawEventSource,
)
from harness.impl.codex.canonical.translator import CodexCanonicalTranslator
from harness.models import raw_events as raw_event_models
from harness.models.session import (
    Session,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.source_common_support import PRIMARY_LEAD_ACTOR
from tests.plugin_tests.support_events import payloads


@dataclass(frozen=True)
class ObservedCodexTitle:
    """Hold a native title event and its translated title payload."""

    raw_event: raw_event_models.RawEvent
    payload: event_session.SessionTitleChanged


@dataclass(frozen=True)
class CodexTitleFixture:
    """Hold mutable native title data and the source that reads it."""

    titles: list[codex_title.CodexNativeTitle]
    marker: list[int]
    source: CodexTitleRawEventSource
    translator: CodexCanonicalTranslator

    def read(self, previous_position: str | None) -> ObservedCodexTitle:
        """Read and translate the next required title event.

        Returns:
            The raw event and its canonical title-change payload.

        """
        raw_title = self.source.read(previous_position)[0]
        title_event = payloads(
            self.translator.translate(raw_title),
            event_session.SessionTitleChanged,
        )[0]
        return ObservedCodexTitle(raw_title, title_event.payload)


def codex_title_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> CodexTitleFixture:
    """Build a title source with controlled native title and store-marker values.

    Returns:
        The mutable values, source, and translator for the title test.

    """
    source_path = tmp_path / ("rollout-2026-08-23T01-02-03-00000000-0000-0000-0000-000000000001.jsonl")
    source_path.write_text("")
    session = Session(
        ids.SessionId(fixture.SESSION_ONE_ID),
        PRIMARY_LEAD_ACTOR,
        source_path.as_posix(),
        fixture.WORK_PATH,
    )
    titles = [codex_title.CodexNativeTitle(fixture.GENERATED_TITLE_TEXT, work_state.TitleOrigin.AUTOMATIC)]
    marker = [1]
    monkeypatch.setattr(
        "harness.impl.codex.canonical.sources.native_title.titles.read_title",
        lambda _path: titles[0],
    )
    monkeypatch.setattr(
        "harness.impl.codex.canonical.sources.native_title.title_store_marker",
        lambda _path, _configuration_directory: codex_title.CodexTitleStoreMarker(
            "state.sqlite",
            (1, marker[0], 1),
            None,
        ),
    )
    return CodexTitleFixture(
        titles,
        marker,
        CodexTitleRawEventSource(session.source_context),
        CodexCanonicalTranslator(),
    )
