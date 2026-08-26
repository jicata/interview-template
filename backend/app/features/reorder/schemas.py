from datetime import date

from pydantic import BaseModel


class ReorderSuggestion(BaseModel):
    product_id: int
    name: str
    sku: str
    pack_size: int
    unit_price: float
    last_order_date: date
    cadence_days: int
    next_due_date: date
    days_overdue: int
    suggested_quantity: int
