# Engine input events

The engine has one worker. It has no periodic input check.

The work queue combines repeated notices for three stages:

- Sources: a file changes, a process exits, or a session input changes.
- Raw events: a transaction commits new raw events.
- Canonical events: a transaction commits translated events.

The worker reads all available source batches, translates pending raw events,
and applies pending canonical events. A notice received during this work stays
in the queue. The worker waits when the queue is empty.

Database notices are sent after commit. A rollback sends no notice. At startup,
the worker runs all three stages to read work stored before the restart.

When the worker applies stored history, it keeps every history entry but sends
one final display update. This includes history that needs more than one read
batch. The terminal colour uses the final actor state. Old turn changes do not
flash through the mirror and terminal colour during import.

## Native input watches

Watchdog watches directories for new files, moves, and writes. Harness profiles
remain watched when no session is active, so an external resume can be found.
Each source declares the files that can stay open between writes.

On macOS, direct `kqueue` file watches detect appended data in these open files.
Directory notifications alone can miss such writes. On Linux, Watchdog uses
`inotify`. Process exit uses `kqueue` on macOS and process descriptors on Linux.
The native waits block until an event or the stop signal arrives.

File watches are set before the source read. New watches also send a notice to
close the gap between discovery and registration. Replaced files get a new watch.
Finished sessions release their source watches.

## Known deadlines

Interrupt confirmation and output expiry need a future action even if no new
input arrives. The queue waits until the next known deadline. Each interrupt
has its own deadline. Failed worker stages get a delayed retry. None of these
actions creates an idle input poll.

The global browser stream also waits for change notices. Database commits and
application-state updates wake its readers. A heartbeat keeps an idle connection
open without a database read. Each reader subscribes before its first read and
releases the subscription on disconnect.

Session data streams also wait for commit notices. Terminal panes request only
session data. They do not request browser application state or check terminal
input. Keep-alive frames do not read the database.

Usage remains separate from the engine. A browser session stream
still checks native terminal input once per second. This check remains because
native typing does not produce a harness event.

The notification worker uses the same change signal as the streams. It reads
state at startup and after a notice. Pending alerts set delivery deadlines.
Failed sends or retractions can set a retry deadline. With no pending work, the
worker waits without a timed scan. Shutdown releases that wait.

The naming worker also waits for database change notices. It drains all stored
jobs before it waits. Failed database reads get a retry deadline. There is no
periodic naming-job scan.

Account usage still has a timed refresh because it can change on a remote
service without a local session event.

## Checks

`tests/test_engine_events.py` checks idle waits, commit and rollback notices,
independent deadlines, complete batch reads, partial lines, file replacement,
open-file writes, process exit, and shutdown. `tests/test_notifier_events.py`
checks idle notification waits, changes during reads, and delivery deadlines.
Run `make e2e` for the full live
harness and browser gate.
