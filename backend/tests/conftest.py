"""Shared test fixtures.

The app's single module-level connection has no per-test rollback — a test
that writes leaves those rows visible to every later test in the process.
`customers` and `products` are never mutated by any handler; `orders` and
`order_lines` are the only tables any write touches, so snapshotting and
restoring just those two, once per test, isolates every write test in the
suite without weakening `db.py`.
"""
import pytest

from app.db import get_connection, transaction


@pytest.fixture(autouse=True)
def _restore_orders_and_lines():
    conn = get_connection()
    orders_before = [dict(row) for row in conn.execute('SELECT * FROM orders').fetchall()]
    lines_before = [dict(row) for row in conn.execute('SELECT * FROM order_lines').fetchall()]

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
