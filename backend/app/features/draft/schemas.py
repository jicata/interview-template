from typing import Literal

from pydantic import BaseModel, Field


class DraftLineInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class SaveLinesRequest(BaseModel):
    lines: list[DraftLineInput] = Field(min_length=1)


class DraftLineOut(BaseModel):
    product_id: int
    name: str
    sku: str
    quantity: int
    unit_price: float


class DraftOrder(BaseModel):
    id: int
    customer_id: int
    # This endpoint only ever finds or creates a draft, so 'draft' is the
    # only value it can return; `Literal` puts that fact on the wire rather
    # than widening the schema's CHECK(status IN ('completed', 'draft')) to
    # a bare `str`.
    status: Literal['draft']
    lines: list[DraftLineOut]
