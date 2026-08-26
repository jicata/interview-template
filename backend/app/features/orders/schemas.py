"""The wire contract for the orders feature.

These models are the wire truth: the frontend re-declares them by hand as
TypeScript interfaces, and `scripts/gen_postman.py` generates the Postman
collection from the schema they produce. Field names match the database's
`snake_case` deliberately — there is no codegen to translate, so a rename here is
a translation surface with no owner.
"""
from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class CreateOrderRequest(BaseModel):
    customer_id: int = Field(gt=0, description='The customer the order is for.')


class AddOrderLineRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(
        gt=0,
        description=(
            'Units to add. Must be a whole number of packs — a multiple of the '
            "product's pack_size. Adding a product already on the order adds to "
            'that line rather than creating a second one.'
        ),
    )


class OrderLineResponse(BaseModel):
    """One priced order line. Every money field is already rounded to the cent."""

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float = Field(description='The price charged for this line.')
    discount_rate: float = Field(description='0.1 when the volume discount applies, else 0.')
    discount_amount: float
    line_total: float


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus
    order_date: str | None
    lines: list[OrderLineResponse]
    order_total: float = Field(description='The sum of the line totals.')
