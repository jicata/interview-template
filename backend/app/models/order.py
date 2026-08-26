from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class OrderStatus(StrEnum):
    """The closed set of order statuses.

    Names the same two values as the `CHECK(status IN ('completed', 'draft'))`
    constraint in `app/db.py`. Nothing else can be written.
    """

    COMPLETED = 'completed'
    DRAFT = 'draft'


@dataclass
class Order:
    id: int
    customer_id: int
    status: OrderStatus
    order_date: Optional[str]
