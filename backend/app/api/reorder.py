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
    reference_date = as_of if as_of is not None else date.today()
    try:
        return handler.get_suggestions(customer_id, reference_date)
    except handler.CustomerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
