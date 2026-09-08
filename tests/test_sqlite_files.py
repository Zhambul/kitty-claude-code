# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test sqlite files."""

from __future__ import annotations

from tests import (
    sqlite_domain_dependencies as domain_dependencies,
    sqlite_repository_dependencies as repository_dependencies,
    sqlite_test_dependencies as test_dependencies,
    sqlite_test_shells,
    sqlite_value_dependencies as standard_dependencies,
)

SESSION = domain_dependencies.domain_ids.SessionId("session-one")
NEWER_PREFERENCE_TIME = 2.0
PROJECT_DIRECTORY = "/project"
REMEMBERED_PANE_WIDTH_PERCENT = 40
UPLOAD_EXPIRY_CHECK_TIME = 50.0


def test_push_subscriptions_upsert_by_endpoint(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify push subscriptions upsert by endpoint."""
    subscriptions = repository_dependencies.sqlite_preferences.SqlitePushSubscriptionRepository(main)
    subscriptions.upsert(
        domain_dependencies.preference_models.PushSubscription(
            "https://push/1", "p", "a", domain_dependencies.domain_ids.DeviceId("device"), None, 1.0,
        ),
    )
    subscriptions.upsert(
        domain_dependencies.preference_models.PushSubscription(
            "https://push/1",
            "p2",
            "a2",
            domain_dependencies.domain_ids.DeviceId("device"),
            "phone",
            NEWER_PREFERENCE_TIME,
        ),
    )
    assert len(subscriptions.subscriptions()) == 1
    assert subscriptions.subscriptions()[0].device_label == "phone"
    subscriptions.remove("https://push/1")
    assert not subscriptions.subscriptions()


def test_the_push_signing_keypair_is_a_singleton(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify the push signing keypair is a singleton."""
    keys = repository_dependencies.sqlite_preferences.SqlitePushSigningKeyRepository(main)
    assert keys.keypair() is None
    keys.save_keypair(domain_dependencies.preference_models.PushSigningKeypair("pem", "pub"))
    keys.save_keypair(domain_dependencies.preference_models.PushSigningKeypair("pem2", "pub2"))
    assert keys.keypair() == domain_dependencies.preference_models.PushSigningKeypair("pem2", "pub2")


def test_a_pane_width_is_absent_until_remembered(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify a pane width is absent until remembered."""
    widths = test_dependencies.SqlitePaneWidthRepository(main)
    assert widths.width_percent(PROJECT_DIRECTORY) is None
    widths.remember_width(PROJECT_DIRECTORY, REMEMBERED_PANE_WIDTH_PERCENT)
    assert widths.width_percent(PROJECT_DIRECTORY) == REMEMBERED_PANE_WIDTH_PERCENT


def test_expired_uploads_come_back_so_caller(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify expired uploads come back so the caller can unlink."""
    uploads = test_dependencies.SqliteUploadRepository(main)
    uploads.record(
        domain_dependencies.upload_models.StoredUpload(
            domain_dependencies.domain_ids.UploadId("u1"), SESSION, "a.png", "image/png", 3, "/test-data/a.png", 1.0,
        ),
    )
    uploads.record(
        domain_dependencies.upload_models.StoredUpload(
            domain_dependencies.domain_ids.UploadId("u2"), None, "b.png", "image/png", 3, "/test-data/b.png", 100.0,
        ),
    )
    removed = uploads.remove_expired(UPLOAD_EXPIRY_CHECK_TIME)
    assert [upload.stored_path for upload in removed] == ["/test-data/a.png"]
    assert not uploads.remove_expired(UPLOAD_EXPIRY_CHECK_TIME)


def test_nothing_in_layer_needs_real_clock_to_be(main: repository_dependencies.SqliteDatabase) -> None:
    """Verify nothing in the layer needs a real clock to be exercised.

    Every timestamp above is supplied by the caller, which is why these
        tests assert on exact values rather than on ranges.
    """
    uploads = test_dependencies.SqliteUploadRepository(main)
    uploads.record(sqlite_test_shells.an_upload())
    removed = uploads.remove_expired(standard_dependencies.time.time())
    assert removed[0].created_at == standard_dependencies.pytest.approx(0)
