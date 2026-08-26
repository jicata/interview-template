from app.db import transaction
from app.features.draft import queries
from app.features.draft.schemas import DraftLineInput, DraftLineOut, DraftOrder


class CustomerNotFoundError(Exception):
    """Raised when the requested customer id does not exist."""


class InvalidProductError(Exception):
    """Raised when a batch references a product id that does not exist."""

    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f'product {product_id} not found')


def save_lines(customer_id: int, lines: list[DraftLineInput]) -> DraftOrder:
    """Merge a batch of lines onto a customer's draft order, atomically.

    Sums duplicate product ids within the incoming batch before touching
    the database, then — inside one `db.transaction()` — validates the
    customer and every product id, finds or creates the draft, and upserts
    each line: increments an existing row's quantity or inserts a new one
    with the price frozen at write time. Any failure rolls back everything,
    including a draft created moments earlier in the same call, so a bad
    product id never leaves a phantom empty draft behind.
    """
    merged = _sum_by_product(lines)

    with transaction() as conn:
        if not queries.customer_exists(conn, customer_id):
            raise CustomerNotFoundError(f'customer {customer_id} not found')

        existing_product_ids = queries.existing_product_ids(conn, list(merged.keys()))
        for product_id in merged:
            if product_id not in existing_product_ids:
                raise InvalidProductError(product_id)

        order_id = queries.find_draft_order_id(conn, customer_id)
        if order_id is None:
            order_id = queries.create_draft_order(conn, customer_id)

        for product_id, quantity in merged.items():
            existing_line = queries.find_line(conn, order_id, product_id)
            if existing_line is not None:
                queries.increment_line_quantity(conn, existing_line['id'], quantity)
            else:
                unit_price = queries.product_unit_price(conn, product_id)
                queries.insert_line(conn, order_id, product_id, quantity, unit_price)

        row = queries.read_draft_order(conn, order_id)

    return DraftOrder(
        id=row['id'],
        customer_id=row['customer_id'],
        status=row['status'],
        lines=[DraftLineOut.model_validate(line) for line in row['lines']],
    )


def _sum_by_product(lines: list[DraftLineInput]) -> dict[int, int]:
    """Same input yields the same result whether it arrives as one request
    or several — request packaging is not something the caller should be
    punished for."""
    merged: dict[int, int] = {}
    for line in lines:
        merged[line.product_id] = merged.get(line.product_id, 0) + line.quantity
    return merged
