# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the browser session test driver."""

from tests.e2e.testkit import (
    browser_assertions as _browser_assertions,
    browser_capabilities as _browser_capabilities,
    browser_driver as _browser_driver,
    browser_session_forms as _browser_session_forms,
)

BrowserSessionStart = _browser_assertions.BrowserSessionStart
BrowserSessionResume = _browser_assertions.BrowserSessionResume
BrowserPlanAction = _browser_capabilities.BrowserPlanAction
default_model_usage_window = _browser_session_forms.default_model_usage_window
BrowserSessionDriver = _browser_driver.BrowserSessionDriver
