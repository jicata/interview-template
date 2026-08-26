from datetime import date

from fastapi import APIRouter, HTTPException

from app.features.reorder import handler
from app.features.reorder.schemas import ReorderSuggestion

router = APIRouter()


@router.get(
    '/customers/{customer_id}/reorder-suggestions',
    response_model=list[ReorderSuggestion],
)
def reorder_suggestions(customer_id: int, as_of: date | None = None) -> list[ReorderSuggestion]:
    """List products this customer is due to reorder, most overdue first.

    `as_of` is the reference date the cadence is projected against; it
    defaults to today when omitted. A product due exactly on `as_of` is
    included — `days_overdue == 0` counts as due, not merely approaching.
    """
    reference_date = as_of if as_of is not None else date.today()
    try:
        return handler.get_suggestions(customer_id, reference_date)
    except handler.CustomerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
