"""The product catalogue the Order Builder picks from."""
from app import db
from app.features.products import queries
from app.features.products.schemas import ProductResponse


def list_products() -> list[ProductResponse]:
    """Every product. Unpaginated deliberately — the catalogue is a fixed five
    rows seeded from CSV, and a page cursor over five rows is ceremony."""
    conn = db.get_connection()
    return [
        ProductResponse(
            id=row['id'],
            name=row['name'],
            sku=row['sku'],
            unit_price=row['unit_price'],
            pack_size=row['pack_size'],
        )
        for row in queries.list_products(conn)
    ]
