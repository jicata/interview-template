"""Data access for the orders feature.

Lives with the feature that owns it rather than in a generic repository; promote
to a shared module only when a second feature needs the same query
(`arch-layered` rule 4). Every function takes its connection explicitly so
nothing here depends on ambient module state.
"""
import sqlite3

from app.models.order import OrderStatus


def find_order(conn: sqlite3.Connection, order_id: int) -> sqlite3.Row | None:
    return conn.execute(
        'SELECT id, customer_id, status, order_date FROM orders WHERE id = ?',
        (order_id,),
    ).fetchone()


def find_product(conn: sqlite3.Connection, product_id: int) -> sqlite3.Row | None:
    return conn.execute(
        'SELECT id, name, sku, unit_price, pack_size FROM products WHERE id = ?',
        (product_id,),
    ).fetchone()


def list_order_lines(conn: sqlite3.Connection, order_id: int) -> list[sqlite3.Row]:
    """The order's lines, oldest first.

    Joins `products` for the display name only. `unit_price` is read from
    `order_lines` — it is the price charged at the time, and the product's current
    price is a different number that happens to match in the seed data.
    """
    return conn.execute(
        '''
        SELECT ol.id, ol.product_id, p.name AS product_name, ol.quantity,
               ol.unit_price
          FROM order_lines ol
          JOIN products p ON p.id = ol.product_id
         WHERE ol.order_id = ?
         ORDER BY ol.id
        ''',
        (order_id,),
    ).fetchall()


def find_order_line(
    conn: sqlite3.Connection, order_id: int, line_id: int
) -> sqlite3.Row | None:
    return conn.execute(
        'SELECT id, quantity FROM order_lines WHERE id = ? AND order_id = ?',
        (line_id, order_id),
    ).fetchone()


def find_order_line_for_product(
    conn: sqlite3.Connection, order_id: int, product_id: int
) -> sqlite3.Row | None:
    return conn.execute(
        'SELECT id, quantity FROM order_lines WHERE order_id = ? AND product_id = ?',
        (order_id, product_id),
    ).fetchone()


def insert_order(conn: sqlite3.Connection, customer_id: int) -> int:
    """Create a draft. A draft has no `order_date` until it is placed."""
    cursor = conn.execute(
        'INSERT INTO orders (customer_id, status, order_date) VALUES (?, ?, NULL)',
        (customer_id, OrderStatus.DRAFT.value),
    )
    return int(cursor.lastrowid)


def insert_order_line(
    conn: sqlite3.Connection,
    order_id: int,
    product_id: int,
    quantity: int,
    unit_price: float,
) -> int:
    cursor = conn.execute(
        '''
        INSERT INTO order_lines (order_id, product_id, quantity, unit_price)
        VALUES (?, ?, ?, ?)
        ''',
        (order_id, product_id, quantity, unit_price),
    )
    return int(cursor.lastrowid)


def update_order_line_quantity(
    conn: sqlite3.Connection, line_id: int, quantity: int
) -> None:
    conn.execute(
        'UPDATE order_lines SET quantity = ? WHERE id = ?', (quantity, line_id)
    )


def delete_order_line(conn: sqlite3.Connection, line_id: int) -> None:
    conn.execute('DELETE FROM order_lines WHERE id = ?', (line_id,))


def customer_exists(conn: sqlite3.Connection, customer_id: int) -> bool:
    row = conn.execute(
        'SELECT 1 FROM customers WHERE id = ?', (customer_id,)
    ).fetchone()
    return row is not None
