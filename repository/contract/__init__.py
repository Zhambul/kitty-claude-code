# Copyright (c) 2026 Zhambyl Yermagambet
"""The Protocols — the only thing a caller outside this package imports.

Every method takes and returns MODEL objects: never a row, never a dict, never
a `sqlite3.Row`. Every method is ONE whole transaction — none returns a
connection, a cursor, or a context manager, so no caller above this line
manages a transaction or holds a handle.
"""
