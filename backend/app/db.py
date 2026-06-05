"""Thread-local in-memory SQLite seeded from CSV on first access."""
import csv
import pathlib
import sqlite3
import threading

_DATA = pathlib.Path(__file__).parent.parent / 'data'
_local = threading.local()


def get_connection() -> sqlite3.Connection:
    if not hasattr(_local, 'conn'):
        _local.conn = _build_db()
    return _local.conn


def _build_db() -> sqlite3.Connection:
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
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
