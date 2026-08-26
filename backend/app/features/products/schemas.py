from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    unit_price: float = Field(description="The product's current price.")
    pack_size: int = Field(description='Units in one pack. Order in multiples of this.')
