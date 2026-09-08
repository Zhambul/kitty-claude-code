# Copyright (c) 2026 Zhambyl Yermagambet
"""The composition root: where the concrete parts are chosen and wired.

    provider_*.py    application nodes grouped by one purpose
    injection.py     the injection kernel: singleton scope, and resolving one
    services/        services that compose concerns the engine keeps apart
    raw_events_audit_cli.py  the read-only raw-event audit CLI

The only package that knows which harnesses and which terminal are installed.
"""
