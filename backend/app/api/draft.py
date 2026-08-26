from fastapi import APIRouter, HTTPException

from app.features.draft import handler
from app.features.draft.schemas import DraftOrder, SaveLinesRequest

router = APIRouter()


@router.post(
    '/customers/{customer_id}/draft/lines',
    response_model=DraftOrder,
)
def save_draft_lines(customer_id: int, payload: SaveLinesRequest) -> DraftOrder:
    """Merge a batch of product/quantity lines onto a customer's draft order.

    Finds the customer's draft order or creates one, then writes every line
    in a single transaction — either the whole batch lands or none of it
    does. A product already on the draft has its quantity increased rather
    than gaining a second row; duplicate product ids within the batch are
    summed before writing.
    """
    try:
        return handler.save_lines(customer_id, payload.lines)
    except handler.CustomerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except handler.InvalidProductError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
