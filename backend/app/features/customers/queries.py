"""SQL for the customers feature. Reads only — never `transaction()`."""
from app.db import get_connection


def all_customers() -> list[dict]:
    conn = get_connection()
    rows = conn.execute('SELECT id, name, email FROM customers ORDER BY name').fetchall()
    return [dict(row) for row in rows]
