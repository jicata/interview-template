"""Test isolation for a database that has none of its own.

`app/db.py` builds one module-level connection at import time, and `TestClient`
imports the same `app.db` the app does. So a test that writes leaves its rows
visible to every later test in the process, and test order silently becomes
load-bearing.

The fix belongs here, in the suite, and never in `db.py` — weakening the app's
connection handling to suit the tests is how the shared-connection bug (b0a7929)
became possible in the first place.
"""
import sqlite3
from collections.abc import Iterator, Sequence

import pytest

from app import db

# Only these two are ever written. Ordered parent-first so restoring inserts
# `orders` before the `order_lines` that reference them; deletion walks the
# reverse. Table names cannot be bound as parameters, so these are module
# constants and never reach here from a request.
_MUTABLE_TABLES = ('orders', 'order_lines')


@pytest.fixture(autouse=True)
def restore_seeded_rows() -> Iterator[None]:
    conn = db.get_connection()
    snapshot = {
        table: conn.execute(f'SELECT * FROM {table}').fetchall()
        for table in _MUTABLE_TABLES
    }

    yield

    with db.transaction() as write:
        for table in reversed(_MUTABLE_TABLES):
            write.execute(f'DELETE FROM {table}')
        for table in _MUTABLE_TABLES:
            _reinsert(write, table, snapshot[table])


def _reinsert(
    conn: sqlite3.Connection, table: str, rows: Sequence[sqlite3.Row]
) -> None:
    if not rows:
        return
    columns = rows[0].keys()
    placeholders = ', '.join('?' * len(columns))
    conn.executemany(
        f'INSERT INTO {table} ({", ".join(columns)}) VALUES ({placeholders})',
        [tuple(row) for row in rows],
    )
