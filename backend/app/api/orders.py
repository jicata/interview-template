"""Transport for the Order Builder.

Thin by design: validate, call, return. The one thing this layer owns that the
handler must not is the translation from domain error to HTTP status — the
handler raises `OrderError`s and never imports `HTTPException`.
"""
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.features.orders import handler
from app.features.orders.errors import (
    CustomerNotFoundError,
    OrderError,
    OrderLineNotFoundError,
    OrderNotDraftError,
    OrderNotFoundError,
    PackSizeViolationError,
    ProductNotFoundError,
)
from app.features.orders.schemas import (
    AddOrderLineRequest,
    CreateOrderRequest,
    OrderResponse,
)

router = APIRouter(tags=['orders'])

# One table instead of a try/except per route. A new domain error that is not
# listed here becomes a 500, which is the right default: an untranslated error is
# a gap in this map, not something to guess a status code for.
_ERROR_STATUS: dict[type[OrderError], int] = {
    OrderNotFoundError: status.HTTP_404_NOT_FOUND,
    ProductNotFoundError: status.HTTP_404_NOT_FOUND,
    CustomerNotFoundError: status.HTTP_404_NOT_FOUND,
    OrderLineNotFoundError: status.HTTP_404_NOT_FOUND,
    OrderNotDraftError: status.HTTP_409_CONFLICT,
    PackSizeViolationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def order_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Render a domain error as `{"detail": "<readable sentence>"}`.

    A plain string rather than FastAPI's list-of-objects 422 body, because this
    message is written to be shown to a sales rep verbatim.
    """
    code = _ERROR_STATUS.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(status_code=code, content={'detail': str(exc)})


@router.post(
    '/orders', response_model=OrderResponse, status_code=status.HTTP_201_CREATED
)
def create_order(payload: CreateOrderRequest) -> OrderResponse:
    """Start a new empty draft order for a customer."""
    return handler.create_order(payload.customer_id)


@router.get('/orders/{order_id}', response_model=OrderResponse)
def get_order(order_id: int) -> OrderResponse:
    """Read an order back with every line priced and the order total."""
    return handler.get_order(order_id)


@router.post(
    '/orders/{order_id}/lines',
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_order_line(order_id: int, payload: AddOrderLineRequest) -> OrderResponse:
    """Add units of a product to a draft order.

    Rejects a quantity that is not a whole number of packs. Returns the whole
    recomputed order, so the running total needs no second request.
    """
    return handler.add_order_line(order_id, payload.product_id, payload.quantity)


@router.delete('/orders/{order_id}/lines/{line_id}', response_model=OrderResponse)
def remove_order_line(order_id: int, line_id: int) -> OrderResponse:
    """Remove a line and return the recomputed order."""
    return handler.remove_order_line(order_id, line_id)
