"""SQL for the draft feature.

Every function here takes the connection explicitly and is called from
inside `handler.save_lines`'s single `db.transaction()` block — never open
a second transaction in this module. `unit_price` on `order_lines` is
written from `products.unit_price` at insert time and is never re-derived
by joining `products` on read; the read-back query joins `products` for
`name` and `sku` only.
"""
import sqlite3


def customer_exists(conn: sqlite3.Connection, customer_id: int) -> bool:
    row = conn.execute('SELECT 1 FROM customers WHERE id = ?', (customer_id,)).fetchone()
    return row is not None


def existing_product_ids(conn: sqlite3.Connection, product_ids: list[int]) -> set[int]:
    placeholders = ', '.join('?' * len(product_ids))
    rows = conn.execute(
        f'SELECT id FROM products WHERE id IN ({placeholders})', product_ids
    ).fetchall()
    return {row['id'] for row in rows}


def find_draft_order_id(conn: sqlite3.Connection, customer_id: int) -> int | None:
    row = conn.execute(
        "SELECT id FROM orders WHERE customer_id = ? AND status = 'draft'",
        (customer_id,),
    ).fetchone()
    return row['id'] if row else None


def create_draft_order(conn: sqlite3.Connection, customer_id: int) -> int:
    cursor = conn.execute(
        "INSERT INTO orders (customer_id, status, order_date) VALUES (?, 'draft', NULL)",
        (customer_id,),
    )
    return cursor.lastrowid


def find_line(conn: sqlite3.Connection, order_id: int, product_id: int) -> dict | None:
    row = conn.execute(
        'SELECT id, quantity FROM order_lines WHERE order_id = ? AND product_id = ?',
        (order_id, product_id),
    ).fetchone()
    return dict(row) if row else None


def increment_line_quantity(conn: sqlite3.Connection, line_id: int, additional_quantity: int) -> None:
    conn.execute(
        'UPDATE order_lines SET quantity = quantity + ? WHERE id = ?',
        (additional_quantity, line_id),
    )


def insert_line(
    conn: sqlite3.Connection, order_id: int, product_id: int, quantity: int, unit_price: float
) -> None:
    conn.execute(
        'INSERT INTO order_lines (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)',
        (order_id, product_id, quantity, unit_price),
    )


def product_unit_price(conn: sqlite3.Connection, product_id: int) -> float:
    row = conn.execute('SELECT unit_price FROM products WHERE id = ?', (product_id,)).fetchone()
    return row['unit_price']


def read_draft_order(conn: sqlite3.Connection, order_id: int) -> dict:
    order = conn.execute(
        'SELECT id, customer_id, status FROM orders WHERE id = ?', (order_id,)
    ).fetchone()
    lines = conn.execute(
        '''
        SELECT
            ol.product_id AS product_id,
            p.name AS name,
            p.sku AS sku,
            ol.quantity AS quantity,
            ol.unit_price AS unit_price
        FROM order_lines ol
        JOIN products p ON p.id = ol.product_id
        WHERE ol.order_id = ?
        ''',
        (order_id,),
    ).fetchall()
    return {
        'id': order['id'],
        'customer_id': order['customer_id'],
        'status': order['status'],
        'lines': [dict(row) for row in lines],
    }
