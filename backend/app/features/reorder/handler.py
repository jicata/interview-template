from datetime import date

from app.features.reorder import queries
from app.features.reorder.cadence import suggest
from app.features.reorder.schemas import ReorderSuggestion


class CustomerNotFoundError(Exception):
    """Raised when the requested customer id does not exist."""


def get_suggestions(customer_id: int, as_of: date) -> list[ReorderSuggestion]:
    if not queries.customer_exists(customer_id):
        raise CustomerNotFoundError(f'customer {customer_id} not found')

    rows = queries.completed_order_lines(customer_id)
    suggestions = suggest(rows, as_of)
    return [
        ReorderSuggestion(
            product_id=s.product_id,
            name=s.name,
            sku=s.sku,
            pack_size=s.pack_size,
            unit_price=s.unit_price,
            last_order_date=s.last_order_date,
            cadence_days=s.cadence_days,
            next_due_date=s.next_due_date,
            days_overdue=s.days_overdue,
            suggested_quantity=s.suggested_quantity,
        )
        for s in suggestions
    ]
