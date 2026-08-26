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
    status: str
    lines: list[DraftLineOut]
