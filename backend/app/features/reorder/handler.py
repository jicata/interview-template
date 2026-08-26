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
    return [ReorderSuggestion.model_validate(s, from_attributes=True) for s in suggestions]
