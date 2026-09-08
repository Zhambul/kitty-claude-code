# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared identities for terminal plugin tests."""

from domain.ids import SessionId, WindowId
from tests.plugin_tests import vocabulary as fixture

PRIMARY_SESSION = SessionId(fixture.SESSION_ONE_ID)
PRIMARY_WINDOW = WindowId(fixture.WINDOW_ONE_ID)
PANE_WINDOW = WindowId(fixture.SEVENTY_SEVEN_TEXT)
