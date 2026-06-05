from dataclasses import dataclass
from typing import Optional


@dataclass
class Order:
    id: int
    customer_id: int
    status: str
    order_date: Optional[str]
