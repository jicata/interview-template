"""Shared test fixtures.

The app's single module-level connection has no per-test rollback — a test
that writes leaves those rows visible to every later test in the process.
`orders` and `order_lines` are the only tables any handler writes to, so
restoring just those two, once per test, isolates every write test in the
suite without weakening `db.py`.

The pristine snapshot is taken once, at session scope, from whatever state
the process is in before the first test runs — not re-captured per test.
Capturing per test would make the fixture self-perpetuating rather than
self-correcting: a write landing outside a test body (import time,
collection, a future session-scoped fixture) would be baked in as the new
"seed" and then faithfully restored forever after, silently masking exactly
the leakage this fixture exists to prevent.
"""
import pytest

from app.db import get_connection, transaction


@pytest.fixture(scope='session')
def _pristine_orders_and_lines():
    conn = get_connection()
    orders = [dict(row) for row in conn.execute('SELECT * FROM orders').fetchall()]
    lines = [dict(row) for row in conn.execute('SELECT * FROM order_lines').fetchall()]
    return orders, lines


@pytest.fixture(autouse=True)
def _restore_orders_and_lines(_pristine_orders_and_lines):
    orders_before, lines_before = _pristine_orders_and_lines

    yield

    with transaction() as tx:
        tx.execute('DELETE FROM order_lines')
        tx.execute('DELETE FROM orders')
        for row in orders_before:
            tx.execute(
                'INSERT INTO orders (id, customer_id, status, order_date) VALUES (?, ?, ?, ?)',
                (row['id'], row['customer_id'], row['status'], row['order_date']),
            )
        for row in lines_before:
            tx.execute(
                'INSERT INTO order_lines (id, order_id, product_id, quantity, unit_price) '
                'VALUES (?, ?, ?, ?, ?)',
                (row['id'], row['order_id'], row['product_id'], row['quantity'], row['unit_price']),
            )
