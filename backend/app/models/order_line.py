from dataclasses import dataclass


@dataclass
class OrderLine:
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
