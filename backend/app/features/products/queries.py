"""Data access for the products feature."""
import sqlite3


def list_products(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        'SELECT id, name, sku, unit_price, pack_size FROM products ORDER BY name'
    ).fetchall()
