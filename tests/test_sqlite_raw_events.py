# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test sqlite raw events."""

from __future__ import annotations

from tests import (
    sqlite_domain_dependencies as domain_dependencies,
    sqlite_repository_dependencies as repository_dependencies,
    sqlite_test_dependencies as test_dependencies,
    sqlite_test_events,
    sqlite_test_fixtures,
    sqlite_test_migrations,
    sqlite_value_dependencies as standard_dependencies,
)

SESSION = domain_dependencies.domain_ids.SessionId("session-one")
FIRST_TRANSLATION_TIME = 1001.0
FIRST_RAW_EVENT_ID = "raw-one"
FIRST_SOURCE_POSITION = "1"
SECOND_SOURCE_POSITION = "2"
THIRD_SOURCE_POSITION = "3"
FIRST_CANONICAL_EVENT_ID = "event-one"
PAYLOAD_FIELD = "payload"


def test_backlog_is_evidence_without_verdict(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify the backlog is evidence without a verdict in arrival order."""
    raw_events = test_dependencies.SqliteRawEventRepository(main)
    canonical = repository_dependencies.SqliteCanonicalEventRepository(main)
    raw_events.record([sqlite_test_fixtures.a_raw_event()])
    unverdicted = raw_events.unverdicted(10)
    assert [event.raw_event_id for event in unverdicted] == [
        domain_dependencies.domain_ids.RawEventId(FIRST_RAW_EVENT_ID),
    ]
    canonical.record_translation(
        sqlite_test_fixtures.a_raw_event(),
        FIRST_SOURCE_POSITION,
        repository_dependencies.raw_event_models.TranslationResult(
            (), domain_dependencies.domain_records.RecordedTranslationDecision.IGNORED_UNKNOWN,
        ),
        1000.0,
    )
    assert not raw_events.unverdicted(10)


def test_raw_evidence_is_compressed_in_storage(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify raw evidence is compressed in storage and restored exactly."""
    raw_events = test_dependencies.SqliteRawEventRepository(main)
    payload_parts = (b'{"text":"', b"repeat " * 1000, b'"}')
    raw = standard_dependencies.replace(sqlite_test_fixtures.a_raw_event(), payload=b"".join(payload_parts))
    raw_events.record([raw])
    with main.read() as connection:
        stored = connection.execute(
            "SELECT payload, payload_codec FROM raw_events WHERE raw_event_id=?", (str(raw.raw_event_id),),
        ).fetchone()
    assert stored["payload_codec"] == "zlib"
    assert len(stored[PAYLOAD_FIELD]) < len(raw.payload)
    assert raw_events.find(raw.raw_event_id) == raw
    raw_events.record([raw])


def test_one_translation_writes_verdict_facts(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify one translation writes verdict facts and provenance together."""
    raw_events = test_dependencies.SqliteRawEventRepository(main)
    canonical = repository_dependencies.SqliteCanonicalEventRepository(main)
    raw_events.record([sqlite_test_fixtures.a_raw_event()])
    outcome = canonical.record_translation(
        sqlite_test_fixtures.a_raw_event(),
        FIRST_SOURCE_POSITION,
        repository_dependencies.raw_event_models.TranslationResult(
            (sqlite_test_fixtures.a_started_event(),),
            domain_dependencies.domain_records.RecordedTranslationDecision.TRANSLATED,
        ),
        1000.0,
    )
    assert [event.event_id for event in outcome.accepted] == [
        domain_dependencies.domain_ids.CanonicalEventId(FIRST_CANONICAL_EVENT_ID),
    ]
    stored = canonical.find(domain_dependencies.domain_ids.CanonicalEventId(FIRST_CANONICAL_EVENT_ID))
    assert stored
    assert stored.raw_event_ids == (domain_dependencies.domain_ids.RawEventId(FIRST_RAW_EVENT_ID),)


def test_re_observed_fact_adds_provenance(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify a re observed fact adds provenance and is not re accepted."""
    canonical = repository_dependencies.SqliteCanonicalEventRepository(main)
    second = sqlite_test_fixtures.a_raw_event("raw-two", SECOND_SOURCE_POSITION)
    test_dependencies.SqliteRawEventRepository(main).record([sqlite_test_fixtures.a_raw_event(), second])
    canonical.record_translation(
        sqlite_test_fixtures.a_raw_event(),
        FIRST_SOURCE_POSITION,
        repository_dependencies.raw_event_models.TranslationResult(
            (sqlite_test_fixtures.a_started_event(),),
            domain_dependencies.domain_records.RecordedTranslationDecision.TRANSLATED,
        ),
        1000.0,
    )
    translation = repository_dependencies.raw_event_models.TranslationResult(
        (sqlite_test_fixtures.a_started_event(),),
        domain_dependencies.domain_records.RecordedTranslationDecision.TRANSLATED,
    )
    outcome = canonical.record_translation(second, FIRST_SOURCE_POSITION, translation, FIRST_TRANSLATION_TIME)
    assert not outcome.accepted
    assert [event.event_id for event in outcome.deduplicated] == [
        domain_dependencies.domain_ids.CanonicalEventId(FIRST_CANONICAL_EVENT_ID),
    ]
    stored = canonical.find(domain_dependencies.domain_ids.CanonicalEventId(FIRST_CANONICAL_EVENT_ID))
    assert stored is not None
    assert set(stored.raw_event_ids) == sqlite_test_migrations.raw_event_ids(FIRST_RAW_EVENT_ID, "raw-two")


def test_reaction_loops_page_walks_every_session(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify the reaction page walks all sessions in observation order."""
    other = domain_dependencies.domain_ids.SessionId("session-two")
    for index, session_id in enumerate((SESSION, other, SESSION)):
        sqlite_test_events.record_paged_event(main, index, session_id)
    sqlite_test_migrations.assert_canonical_pages(repository_dependencies.SqliteCanonicalEventRepository(main), other)


def test_raw_event_audit_joins_observation_to_its(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify raw event audit joins an observation to its interpretation and facts."""
    raw_events = test_dependencies.SqliteRawEventRepository(main)
    canonical = repository_dependencies.SqliteCanonicalEventRepository(main)
    audits = repository_dependencies.SqliteRawEventAuditRepository(main)
    raw_events.record([sqlite_test_fixtures.a_raw_event()])
    canonical.record_translation(
        sqlite_test_fixtures.a_raw_event(),
        THIRD_SOURCE_POSITION,
        repository_dependencies.raw_event_models.TranslationResult(
            (sqlite_test_fixtures.a_started_event(),),
            domain_dependencies.domain_records.RecordedTranslationDecision.TRANSLATED,
        ),
        1000.0,
    )
    one = audits.audit(domain_dependencies.domain_ids.RawEventId(FIRST_RAW_EVENT_ID))
    assert one is not None
    assert one.interpretation is not None
    assert (
        one.interpretation.decision,
        one.interpretation.translator_version,
        [recorded_event.event.event_id for recorded_event in one.interpretation.events],
        audits.audits_for_session(SESSION),
    ) == (
        domain_dependencies.domain_records.RecordedTranslationDecision.TRANSLATED,
        THIRD_SOURCE_POSITION,
        [domain_dependencies.domain_ids.CanonicalEventId(FIRST_CANONICAL_EVENT_ID)],
        (one,),
    )


def test_uninterpreted_raw_event_audit_has_no(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify uninterpreted raw event audit has no interpretation."""
    raw_events = test_dependencies.SqliteRawEventRepository(main)
    audits = repository_dependencies.SqliteRawEventAuditRepository(main)
    raw_events.record([sqlite_test_fixtures.a_raw_event()])
    one = audits.audit(domain_dependencies.domain_ids.RawEventId(FIRST_RAW_EVENT_ID))
    assert one is not None
    assert one.interpretation is None
