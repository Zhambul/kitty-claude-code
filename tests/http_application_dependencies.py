# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http application dependencies."""

from api import config as _api_config
from api.application import static_delivery as static_delivery, static_documents as static_documents
from api.controls.models.send_text_request import SendTextRequest as SendTextRequest
from api.server import build_server as build_server
from audit.documents import AuditContent as AuditContent
from audit.recorder import AuditRecorder as AuditRecorder
from audit.records import StateFileRecord as StateFileRecord
from audit.telemetry import BrowserTelemetryService as BrowserTelemetryService

api_config = _api_config
