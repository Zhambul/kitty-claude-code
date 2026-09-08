# Copyright (c) 2026 Zhambyl Yermagambet
# client/_handoff.py — the local channel between a pane and its click handlers.
#
# A click on a link in the mirror does not reach the pane process: the terminal
# launches a NEW program with the URI (kitty's open-actions), and that program
# has no model, no stream and — by decision — no daemon to ask. Content is
# embedded in the entries the pane already holds, so both gestures are the
# frontend's own and the daemon is not involved in either.
#
# So the two processes meet on disk, and the shape is chosen to make races
# impossible rather than to handle them: TWO files, each with exactly ONE writer.
#
#   <dir>/baqylau-pane-<uid>-<session>-<kind>.json    written by the PANE only
#       {"pid": 4321, "targets": {"<id>": "<text>", …}}
#   <dir>/baqylau-view-<uid>-<session>-<kind>.json    written by the HANDLER only
#       {"opened": ["<entry-id>", …]}
#   <dir>/baqylau-pane-<uid>-<session>-<kind>.lock    HELD by the pane, flock'd
#
# The pane publishes what is on screen and its own pid; the handler publishes
# what the reader has expanded and then signals that pid. Neither ever writes the
# other's file, so a half-written file is only ever a file the other side
# re-reads next tick.
#
# The LOCK is what makes the signal safe, and it is not optional. A pid in a file
# is a pid that was true once: a pane that died leaves its file behind, the
# system recycles the number, and a handler that trusted it would fire SIGUSR1 at
# whatever now holds it — someone else's process, for whom that signal means
# something else entirely, or nothing and therefore death. So the pane holds an
# exclusive flock for its whole life, and the handler signals only when it CANNOT
# take that lock. A lock nobody holds is a pane that is gone.
#
# Import-pure. The pane process uses Pydantic for this file boundary.
from __future__ import annotations

import os
import signal
from typing import TYPE_CHECKING

import _handoff_documents
import _handoff_lock
import _handoff_paths
import _handoff_storage

if TYPE_CHECKING:
    from collections.abc import Mapping

# The uid is in the NAME, not in a directory mode: on a shared /tmp two people
# running this must not collide, and a name is checked by the filesystem for
# free. (macOS already gives each user its own TMPDIR; Linux does not.)
# What a handler sends to make the pane re-read the view file and repaint. SIGUSR1
# because the pane already lives on signals — a resize and the clock are the same
# mechanism — and because it is the one channel that reaches a process blocked in
# a socket read without a second thread.
REPAINT_SIGNAL = signal.SIGUSR1
# One copy target is a command's output. Capped so that a runaway build log
# cannot turn every repaint into a multi-megabyte write; a clipboard nobody can
# read past the first screenful loses nothing real.
TARGET_LIMIT = 262_144
PRIVATE_UMASK = 0o77


def hold(session_id: str, kind: str) -> bool:
    """Claim this session-and-kind as the live pane. False if another one has it.

    False is not an error and not a reason to exit: two panes on one session are
    allowed and both paint correctly. It only decides which of them a CLICK wakes,
    and the first one there wins — the same rule the terminal itself applies when
    it decides which window a link was clicked in.

    Returns:
        True when the stated condition is met; otherwise, false.

    """
    path = _handoff_paths.handoff_paths.lock_path(session_id, kind)
    return _handoff_lock.pane_lock.claim(path)


def publish(session_id: str, kind: str, targets: Mapping[str, str]) -> None:
    """Publish publish.

    The pane says what is on screen and where to find it.
    """
    os.umask(PRIVATE_UMASK)
    published_targets = {name: text[:TARGET_LIMIT] for name, text in targets.items()}
    _handoff_storage.write_document(
        _handoff_paths.handoff_paths.pane_path(session_id, kind),
        _handoff_documents.PaneDocument(pid=os.getpid(), targets=published_targets),
    )


def target(session_id: str, kind: str, name: str) -> str | None:
    """Return the target.

    The text behind one copy link, as the pane last published it.

    Returns:
        Target.

    """
    path = _handoff_paths.handoff_paths.pane_path(session_id, kind)
    found = _handoff_storage.read_document(path, _handoff_documents.PaneDocument)
    if found is None:
        return None
    return found.targets.get(name)


def opened(session_id: str, kind: str) -> frozenset[str]:
    """Which entries the reader has expanded.

    Returns:
        Result items.

    """
    path = _handoff_paths.handoff_paths.view_path(session_id, kind)
    found = _handoff_storage.read_document(path, _handoff_documents.ViewDocument)
    return frozenset() if found is None else frozenset(found.opened)


def toggle(session_id: str, kind: str, entry_id: str) -> bool:
    """Flip one entry's expanded state and say what it became.

    Returns:
        True when the stated condition is met; otherwise, false.

    """
    current = set(opened(session_id, kind))
    became = entry_id not in current
    if became:
        current.add(entry_id)
    else:
        current.discard(entry_id)
    os.umask(PRIVATE_UMASK)
    document = _handoff_documents.ViewDocument(opened=tuple(sorted(current)))
    path = _handoff_paths.handoff_paths.view_path(session_id, kind)
    _handoff_storage.write_document(path, document)
    return became


def wake(session_id: str, kind: str) -> bool:
    """Ask the pane to re-read and repaint. False when there is no pane to ask.

    The lock is checked BEFORE the pid is used, and that order is the whole
    safety of this function: a pid nobody vouches for is a pid that may belong to
    a stranger.

    Returns:
        True when the stated condition is met; otherwise, false.

    """
    lock_path = _handoff_paths.handoff_paths.lock_path(session_id, kind)
    if not _handoff_lock.pane_is_running(lock_path):
        return False
    pane_path = _handoff_paths.handoff_paths.pane_path(session_id, kind)
    found = _handoff_storage.read_document(pane_path, _handoff_documents.PaneDocument)
    if found is None:
        return False
    try:
        os.kill(found.pid, REPAINT_SIGNAL)
    except OSError:
        return False  # it exited between the two checks
    return True
