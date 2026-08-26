"""SQL for the reorder-suggestions feature. Reads only — never `transaction()`."""
from app.db import get_connection


def customer_exists(customer_id: int) -> bool:
    conn = get_connection()
    row = conn.execute('SELECT 1 FROM customers WHERE id = ?', (customer_id,)).fetchone()
    return row is not None


def completed_order_lines(customer_id: int) -> list[dict]:
    """Completed-order lines for a customer, one row per order line.

    Filters on `status = 'completed'` and `order_date IS NOT NULL` — a draft
    order (order 19) must never reach the cadence calculation. `unit_price`
    is the product's *current* price, joined from `products`, because this
    is a suggestion for a future order, not a record of a past one.
    """
    conn = get_connection()
    rows = conn.execute(
        '''
        SELECT
            p.id AS product_id,
            p.name AS name,
            p.sku AS sku,
            p.pack_size AS pack_size,
            p.unit_price AS unit_price,
            o.order_date AS order_date
        FROM orders o
        JOIN order_lines ol ON ol.order_id = o.id
        JOIN products p ON p.id = ol.product_id
        WHERE o.customer_id = ?
          AND o.status = 'completed'
          AND o.order_date IS NOT NULL
        ''',
        (customer_id,),
    ).fetchall()
    return [dict(row) for row in rows]
