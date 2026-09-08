# Copyright (c) 2026 Zhambyl Yermagambet
"""Read copied file paths from the local system clipboard."""

# Read the LOCAL machine's pasteboard for copied FILE
# PATHS. The ONE
# owner of the "what files are on the clipboard" fact.
#
# Why this exists at all. Copying a file in an app that offers it as a PROMISE
# (IntelliJ IDEA's Project-view Copy) puts these flavors on the macOS
# pasteboard:
#
#   public.utf8-plain-text   "__init__.py"                    ← the BARE NAME
#   NSFilenamesPboardType    ["/Users/…/clients/__init__.py"] ← the full path
#   public.file-url          "file:///Users/…/__init__.py"    ← the full path
#
# The browser is shown NONE of the path-bearing ones. Chrome hands the page a
# zero-byte `File` whose `.name` is a BASENAME by design — the web platform
# deliberately never exposes a filesystem path to script, and no clipboard API
# (`clipboardData.getData`, `navigator.clipboard.read`) will surface
# `public.file-url`. The paste event's text flavor is the bare name, which is
# not what the user copied and not what the terminal pastes.
#
# So the page cannot answer this question and the SERVER must: the dashboard
# runs on the same Mac as the pasteboard, so it reads the same flavor the
# terminal reads. That is the whole trick — the browser reports WHICH file (basename +
# zero bytes), the server supplies WHERE it is.
#
# Read-only, no caching (a pasteboard is live state — a stale answer is a wrong
# path), and it degrades to [] on every failure: no pyobjc, no pasteboard, a
# non-macOS host. The caller then falls back to the bare name.
#
# Env knob (read at CALL time — the in-process test server flips it per-test):
# BAQYLAU_DASHBOARD_CLIPBOARD_FILES is a `:`-separated path list that REPLACES the
# real pasteboard read, which is what makes this hermetically testable (and
# testable at all off macOS).
import os
from importlib import import_module
from pathlib import Path
from urllib.parse import unquote, urlparse

from audit import record as audit_record
from audit.documents import ShortErrorAudit

ENV_FILES = "BAQYLAU_DASHBOARD_CLIPBOARD_FILES"
FILES_MAX = 20  # a sane multi-select ceiling; a runaway pasteboard
#                         must not become a runaway message
ERROR_TEXT_LIMIT = 200
NAMES_TYPE = "NSFilenamesPboardType"  # plist array of POSIX paths (multi-file)
URL_TYPE = "public.file-url"  # a single file:// URL (the fallback)
CLIPBOARD_ERRORS = (ImportError, OSError, TypeError, ValueError, AttributeError)


def _from_env() -> list[str] | None:
    """Read an explicit clipboard path list from the environment.

    Returns:
        Result items.

    """
    raw = os.environ.get(ENV_FILES)
    if raw is None:
        return None
    return [path_text for path_text in raw.split(":") if path_text]


def _from_pasteboard() -> list[str]:
    """Read all file paths from the general pasteboard.

    pyobjc is imported HERE, not at module scope — the dashboard imports this
    module on every request path and must not pay (or crash on) an AppKit load
    it may never need. AppKit ships with the system python3 on macOS; anywhere
    else the ImportError is the caller's "no clipboard" answer.

    Returns:
        Result items.

    """
    pasteboard_type = import_module("AppKit").NSPasteboard
    pasteboard = pasteboard_type.generalPasteboard()
    if pasteboard is None:
        return []
    # NSFilenamesPboardType first: it is the only flavor that carries MORE than
    # one file (a multi-select copy), and it is already POSIX paths.
    path_list = pasteboard.propertyListForType_(NAMES_TYPE)
    if path_list:
        return [str(path_entry) for path_entry in path_list]
    file_url = pasteboard.stringForType_(URL_TYPE)
    if file_url:
        parsed_url = urlparse(str(file_url).rstrip("\x00"))
        if parsed_url.scheme == "file" and parsed_url.path:
            return [unquote(parsed_url.path)]
    return []


def files() -> list[str]:
    """Return valid absolute file paths from the local clipboard.

    Return no paths when the clipboard is not available. Limit the result to
    prevent a large pasteboard from creating a large message.

    Returns:
        Valid absolute file paths from the local clipboard.

    """
    try:
        path_texts = _read_path_texts()
    except CLIPBOARD_ERRORS as error:
        audit_record.error(
            "",
            "clipboard (read failed)",
            ShortErrorAudit(
                error=f"{type(error).__name__}: {error}"[:ERROR_TEXT_LIMIT],
            ),
        )
        return []
    return [
        path_text
        for path_text in path_texts
        if path_text and Path(path_text).is_absolute() and Path(path_text).exists()
    ][:FILES_MAX]


def match(names: list[str] | None) -> list[str]:
    """Match clipboard paths to file names that a browser reported.

    This correlation is the whole safety story. The dashboard is reachable from
    a phone over the tunnel, and a phone's clipboard is not this Mac's: without
    the check, any remote paste would be answered with whatever path happens to
    sit on the host's pasteboard — a wrong path silently pasted into a message,
    and a small disclosure of the host's filesystem to a device that never
    copied anything. Requiring the basenames to agree means we only ever
    RESOLVE a file the caller already named; we never volunteer one.

    Returns:
        Result items.

    """
    expected_names = _browser_file_names(names)
    if not expected_names:
        return []
    clipboard_paths = files()
    clipboard_names = sorted(Path(path_text).name for path_text in clipboard_paths)
    if clipboard_names != expected_names:
        return []
    return clipboard_paths


def _read_path_texts() -> list[str]:
    """Read configured paths or the current pasteboard paths.

    Returns:
        Result items.

    """
    configured_paths = _from_env()
    if configured_paths is not None:
        return configured_paths
    return _from_pasteboard()


def _browser_file_names(names: list[str] | None) -> list[str]:
    """Return the valid file names in one browser report.

    Returns:
        Valid file names in one browser report.

    """
    valid_names = [file_name for file_name in names or [] if isinstance(file_name, str) and file_name]
    return sorted(valid_names)
