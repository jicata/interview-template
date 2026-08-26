"""Shared in-memory SQLite seeded from CSV at import time."""
import contextlib
import csv
import pathlib
import sqlite3
import threading
from collections.abc import Iterator

_DATA = pathlib.Path(__file__).parent.parent / 'data'

# Serialized mode makes individual sqlite3 calls thread-safe, but the implicit
# transaction belongs to the shared connection — concurrent writers would
# commit/roll back each other's work. All writes must go through transaction().
_write_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    return _conn


@contextlib.contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """Serialize write transactions across request threads.

    Commits on success, rolls back on error. Use for any handler that writes:

        with db.transaction() as conn:
            conn.execute('INSERT ...', params)
    """
    with _write_lock:
        try:
            yield _conn
            _conn.commit()
        except BaseException:
            _conn.rollback()
            raise


def _build_db() -> sqlite3.Connection:
    # check_same_thread=False: FastAPI serves sync endpoints from a thread
    # pool; sharing one connection requires a serialized sqlite3 build.
    assert sqlite3.threadsafety == 3, 'sqlite3 must be built in serialized mode'
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    # SQLite ignores declared REFERENCES unless this pragma is set per
    # connection, and it is a no-op once a transaction is open — it must run
    # here, before the executescript, or it silently enforces nothing.
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            sku TEXT NOT NULL,
            unit_price REAL NOT NULL,
            pack_size INTEGER NOT NULL
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            status TEXT NOT NULL CHECK(status IN ('completed', 'draft')),
            order_date TEXT
        );
        CREATE TABLE order_lines (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL
        );
    ''')
    for table, fname in [
        ('customers', 'customers.csv'),
        ('products', 'products.csv'),
        ('orders', 'orders.csv'),
        ('order_lines', 'order_lines.csv'),
    ]:
        with open(_DATA / fname, newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                cols = list(rows[0].keys())
                placeholders = ', '.join('?' * len(cols))
                col_names = ', '.join(cols)
                c.executemany(
                    f'INSERT INTO {table} ({col_names}) VALUES ({placeholders})',
                    [
                        [r[col] if r[col] != '' else None for col in cols]
                        for r in rows
                    ],
                )
    conn.commit()
    return conn


_conn = _build_db()
